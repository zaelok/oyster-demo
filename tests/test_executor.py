import json

from oyster.executor import REPAIR_SUFFIX, BudgetHook, parse_findings, run_path
from oyster.graph.catalog import PATH_A, PATH_B, PATH_C
from oyster.prompts import render_messages
from oyster.providers import MockProvider, fixture_key
from oyster.types import Cost, Finding, Priors
from tests.conftest import EMPTY, ScriptedProvider, finding_json


def test_path_a_end_to_end_produces_one_node_result(corpus_case, bindings, tmp_path):
    result = run_path(PATH_A, corpus_case, MockProvider(tmp_path), bindings)
    assert result.path_id == "A" and result.case_id == corpus_case.id
    assert len(result.node_results) == 1
    assert result.node_results[0].node_id == "a1"
    assert result.node_results[0].role == "cheap-scanner"
    assert result.findings == ()
    assert result.cost.dollars > 0 and result.cost.latency_s == 0.05
    assert result.halted_reason is None
    assert result.node_results[0].parse_failed is False


def test_path_b_passes_upstream_findings_into_second_prompt(corpus_case, bindings):
    provider = ScriptedProvider([finding_json("pricing.py", 7, 7), EMPTY])
    result = run_path(PATH_B, corpus_case, provider, bindings)

    first, second = provider.calls
    assert first["model_id"] == "mock-cheap" and second["model_id"] == "mock-strong"
    assert "EARLIER FINDINGS" not in first["user"]
    assert "EARLIER FINDINGS" in second["user"]
    assert '"file": "pricing.py"' in second["user"]
    assert '"line_start": 7' in second["user"]
    assert second["cached_prefix"] == corpus_case.diff
    assert corpus_case.diff not in second["user"]
    assert len(result.node_results) == 2


def test_hook_halts_before_second_node_and_partial_result_is_data(corpus_case, bindings):
    class HaltOnSecond:
        def before_node(self, node, spent, budget):
            return None if node.id == "b1" else "stop: test hook"

    provider = ScriptedProvider([finding_json("pricing.py", 7, 7)])
    result = run_path(PATH_B, corpus_case, provider, bindings, hooks=[HaltOnSecond()])
    assert result.halted_reason == "stop: test hook"
    assert len(result.node_results) == 1
    assert len(provider.calls) == 1
    assert result.findings == result.node_results[0].findings
    assert result.cost == result.node_results[0].cost


def test_malformed_fixture_triggers_one_retry_then_parse_failed(corpus_case, bindings, tmp_path):
    system, user, cached = render_messages("cheap_scanner", corpus_case.diff)
    for prompt in (user, user + REPAIR_SUFFIX):
        key = fixture_key("mock-cheap", system, prompt, cached)
        (tmp_path / f"{key}.json").write_text(
            json.dumps(
                {
                    "text": "Sure! Here are the findings: none.",
                    "input_tokens": 500,
                    "cached_input_tokens": 400,
                    "output_tokens": 30,
                    "latency_s": 0.2,
                    "model_id": "mock-cheap",
                }
            )
        )
    provider = MockProvider(tmp_path)
    result = run_path(PATH_A, corpus_case, provider, bindings)

    node = result.node_results[0]
    assert node.parse_failed is True
    assert node.findings == ()
    assert provider.misses == [], "both the original and the repair prompt hit fixtures"
    assert node.cost.dollars > 0
    assert node.cost.latency_s == 0.4, "cost of both calls is kept"


def test_retry_prompt_is_original_plus_repair_suffix(corpus_case, bindings):
    provider = ScriptedProvider(["not json", EMPTY])
    result = run_path(PATH_A, corpus_case, provider, bindings)
    assert len(provider.calls) == 2
    assert provider.calls[1]["user"] == provider.calls[0]["user"] + REPAIR_SUFFIX
    assert result.node_results[0].parse_failed is False
    assert result.node_results[0].cost.latency_s == 1.0


def test_finding_on_file_absent_from_diff_is_discarded(corpus_case, bindings):
    provider = ScriptedProvider([finding_json("ghost.py", 1, 1)])
    result = run_path(PATH_A, corpus_case, provider, bindings)
    assert result.findings == ()
    assert result.node_results[0].parse_failed is False


def test_b_prefixed_path_is_normalized_to_diff_target(corpus_case, bindings):
    provider = ScriptedProvider([finding_json("b/pricing.py", 7, 7)])
    result = run_path(PATH_A, corpus_case, provider, bindings)
    assert result.findings == (Finding("pricing.py", 7, 7, "logic", "d", 0.9),)


def test_path_result_findings_is_last_node_not_union(corpus_case, bindings):
    first = finding_json("pricing.py", 7, 7)
    last = finding_json("auth.py", 23, 24, "security")
    provider = ScriptedProvider([first, last])
    result = run_path(PATH_B, corpus_case, provider, bindings)
    assert result.findings == (Finding("auth.py", 23, 24, "security", "d", 0.9),)
    assert result.node_results[0].findings == (Finding("pricing.py", 7, 7, "logic", "d", 0.9),)


def test_upstream_findings_are_deduplicated_and_ordered(corpus_case, bindings):
    duplicate = (
        '{"findings": ['
        '{"file": "pricing.py", "line_start": 7, "line_end": 7, "category": "logic", '
        '"description": "x", "confidence": 0.5},'
        '{"file": "pricing.py", "line_start": 7, "line_end": 7, "category": "logic", '
        '"description": "y", "confidence": 0.6},'
        '{"file": "auth.py", "line_start": 23, "line_end": 24, "category": "security", '
        '"description": "z", "confidence": 0.7}]}'
    )
    provider = ScriptedProvider([duplicate, EMPTY])
    run_path(PATH_B, corpus_case, provider, bindings)
    body = provider.calls[1]["user"]
    assert body.count('"file": "pricing.py"') == 1
    assert body.index('"file": "auth.py"') < body.index('"file": "pricing.py"')


def test_path_c_runs_three_nodes_and_critic_sees_findings_under_review(corpus_case, bindings):
    provider = ScriptedProvider([finding_json("pricing.py", 7, 7), EMPTY, EMPTY])
    result = run_path(PATH_C, corpus_case, provider, bindings)
    assert [r.node_id for r in result.node_results] == ["c1", "c2", "c3"]
    assert "FINDINGS UNDER REVIEW" in provider.calls[1]["user"]
    assert '"file": "pricing.py"' in provider.calls[1]["user"]
    assert "EARLIER FINDINGS" not in provider.calls[2]["user"], "c2 returned nothing"
    assert result.cost.latency_s == 1.5


def test_parse_findings_tolerates_fence_and_drops_malformed_items():
    fenced = '```json\n{"findings": [{"file": "a", "line_start": 1, "line_end": 2, "category": "style", "description": "", "confidence": 1}, {"nope": 1}]}\n```'
    parsed = parse_findings(fenced)
    assert parsed == (Finding("a", 1, 2, "style", "", 1.0),)
    assert parse_findings("[]") is None
    assert parse_findings('{"findings": "x"}') is None
    assert parse_findings("") is None


def test_budget_hook_halts_when_projected_spend_exceeds_budget(corpus_case, bindings):
    priors = Priors(
        catch_rate={},
        mean_cost={
            ("cheap-scanner", "cheap-model"): Cost(0.1, 1.0),
            ("deep-reviewer", "strong-model"): Cost(2.0, 5.0),
        },
        corpus_size=1,
    )
    hook = BudgetHook(Cost(1.0, 100.0), priors)
    provider = ScriptedProvider([EMPTY])
    result = run_path(PATH_B, corpus_case, provider, bindings, hooks=[hook])
    assert result.halted_reason is not None and result.halted_reason.startswith("budget:")
    assert len(result.node_results) == 1


def test_budget_hook_latency_and_run_level_budget():
    hook = BudgetHook(Cost(10.0, 10.0))
    node = PATH_A.nodes[0]
    assert hook.before_node(node, Cost(0.0, 0.0), Cost(10.0, 10.0)) is None
    assert hook.before_node(node, Cost(0.0, 11.0), Cost(10.0, 10.0)).startswith("latency:")
    assert hook.before_node(node, Cost(0.5, 0.0), Cost(0.25, 10.0)).startswith("budget:")
