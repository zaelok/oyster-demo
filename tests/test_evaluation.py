from datetime import UTC, datetime

from oyster.evaluation import (
    LIMITATIONS,
    calibrate,
    calibration_paths,
    evaluate,
    priors_from_json,
    priors_to_json,
    render_results,
    results_to_json,
)
from oyster.graph.catalog import CATALOG
from oyster.providers import MockProvider
from oyster.types import Cost, Priors
from tests.conftest import EMPTY, ScriptedProvider, finding_json


def test_end_to_end_mock_renders_one_row_per_path(corpus_case, bindings, tmp_path):
    results, reports = evaluate(CATALOG, [corpus_case], MockProvider(tmp_path), bindings)
    assert len(results) == 3 and len(reports) == 3
    text = render_results(results, reports, bindings, corpus_size=1, provider_name="mock")

    rows = [line for line in text.splitlines() if line.startswith("| ") and line[2] in "ABC"]
    assert len(rows) == 3
    for row in rows:
        assert "| n/a |" in row, "no fixtures means nothing caught, so $/bug is n/a"
        assert "| 0 | 0 | 2 |" in row, "strict, loose and seeded are separate columns"
    assert "Models: cheap-model=mock-cheap @ $1.00/$5.00 per 1M" in text
    assert "        strong-model=mock-strong @ $3.00/$15.00 per 1M" in text
    assert "Provider: mock" in text
    assert "Corpus: 1 cases, 2 seeded bugs" in text
    assert "## Per-case detail" in text
    assert "### Path C" in text
    assert "## Limitations" in text
    assert LIMITATIONS.strip() in text


def test_render_reports_strict_and_loose_separately_and_halts(corpus_case, bindings):
    provider = ScriptedProvider([finding_json("pricing.py", 7, 7, "style")])
    results, reports = evaluate([CATALOG[0]], [corpus_case], provider, bindings)
    text = render_results(
        results,
        reports,
        bindings,
        1,
        generated_at=datetime(2026, 9, 6, 12, 0, tzinfo=UTC),
        corpus_commit="abc123",
    )
    assert "Generated: 2026-09-06T12:00:00Z" in text
    assert "corpus commit abc123" in text
    row = next(line for line in text.splitlines() if line.startswith("| A |"))
    assert "| 0 | 1 | 2 | n/a |" in row


def test_render_shows_dollars_per_bug_and_halted_count(corpus_case, bindings):
    class HaltAlways:
        def before_node(self, node, spent, budget):
            return "budget: test"

    caught = ScriptedProvider([finding_json("pricing.py", 7, 7)])
    results, reports = evaluate([CATALOG[0]], [corpus_case], caught, bindings)
    halted_results, halted_reports = evaluate(
        [CATALOG[1]], [corpus_case], caught, bindings, hooks=[HaltAlways()]
    )
    text = render_results(
        results + halted_results, reports + halted_reports, bindings, corpus_size=1
    )
    row_a = next(line for line in text.splitlines() if line.startswith("| A |"))
    row_b = next(line for line in text.splitlines() if line.startswith("| B |"))
    assert "| 1 | 1 | 2 | $" in row_a
    assert row_a.rstrip().endswith("| 0 |")
    assert "| n/a |" in row_b and row_b.rstrip().endswith("| 1 |")
    assert "budget: test" in text


def test_render_with_empty_corpus_is_still_complete(bindings):
    text = render_results((), (), bindings, corpus_size=0)
    assert "Corpus: 0 cases, 0 seeded bugs" in text
    assert "## Limitations" in text


def test_calibration_paths_are_one_per_distinct_node_config():
    singles = calibration_paths(CATALOG)
    assert [p.id for p in singles] == [
        "cal:cheap-scanner:cheap-model",
        "cal:deep-reviewer:strong-model",
        "cal:critic:strong-model",
    ]
    assert all(len(p.nodes) == 1 and p.edges == () for p in singles)


def test_calibrate_measures_catch_rates_and_mean_cost(corpus_case, bindings):
    # Every config sees the same script: catches the logic bug, misses the security bug.
    provider = ScriptedProvider([finding_json("pricing.py", 7, 7)])
    priors = calibrate([corpus_case], provider, bindings)
    assert priors.corpus_size == 1
    for role, alias in (
        ("cheap-scanner", "cheap-model"),
        ("deep-reviewer", "strong-model"),
        ("critic", "strong-model"),
    ):
        assert priors.catch_rate[(role, alias, "logic")] == 1.0
        assert priors.catch_rate[(role, alias, "security")] == 0.0
        assert (role, alias, "style") not in priors.catch_rate, "no style bugs seeded"
        assert priors.mean_cost[(role, alias)].latency_s == 0.5
    assert priors.mean_cost[("deep-reviewer", "strong-model")].dollars > (
        priors.mean_cost[("cheap-scanner", "cheap-model")].dollars
    )


def test_calibrate_on_empty_corpus_yields_empty_priors(bindings):
    priors = calibrate([], ScriptedProvider([EMPTY]), bindings)
    assert priors == Priors(catch_rate={}, mean_cost={}, corpus_size=0)


def test_priors_json_round_trip():
    priors = Priors(
        catch_rate={("cheap-scanner", "cheap-model", "logic"): 0.25},
        mean_cost={("cheap-scanner", "cheap-model"): Cost(0.01, 1.5)},
        corpus_size=4,
    )
    assert priors_from_json(priors_to_json(priors)) == priors


def test_results_json_retains_every_path_result(corpus_case, bindings, tmp_path):
    results, reports = evaluate(CATALOG, [corpus_case], MockProvider(tmp_path), bindings)
    import json

    payload = json.loads(results_to_json(results, reports))
    assert [r["path_id"] for r in payload["results"]] == ["A", "B", "C"]
    assert payload["results"][2]["node_results"][2]["node_id"] == "c3"
    assert payload["reports"][0]["missed"] == ["case-01-b1", "case-01-b2"]


def test_wilson_interval_and_percentile_helpers():
    from oyster.evaluation import percentile, wilson_interval

    low, high = wilson_interval(14, 17)
    assert 0.58 < low < 0.60 and 0.93 < high < 0.95
    assert wilson_interval(0, 0) == (0.0, 1.0)
    assert wilson_interval(1, 1)[0] > 0.2 and wilson_interval(1, 1)[1] > 0.999
    assert wilson_interval(0, 1)[0] == 0.0 and wilson_interval(0, 1)[1] < 0.8
    values = [float(v) for v in range(1, 18)]
    assert percentile(values, 0.50) == 9.0
    assert percentile(values, 0.95) == 17.0
    assert percentile([], 0.5) == 0.0


def test_calibrate_records_evidence_and_percentiles(corpus_case, bindings):
    provider = ScriptedProvider([finding_json("pricing.py", 7, 7)])
    priors = calibrate([corpus_case], provider, bindings)
    logic = priors.quality[("cheap-scanner", "cheap-model", "logic")]
    assert (logic.rate, logic.n) == (1.0, 1)
    assert logic.ci_low > 0.2 and logic.ci_high > 0.999
    security = priors.quality[("cheap-scanner", "cheap-model", "security")]
    assert (security.rate, security.n, security.ci_low) == (0.0, 1, 0.0)
    profile = priors.cost[("cheap-scanner", "cheap-model")]
    assert profile.n == 1
    assert profile.latency_p50 == profile.latency_p95 == 0.5
    assert profile.dollars_p95 == priors.mean_cost[("cheap-scanner", "cheap-model")].dollars


def test_priors_json_round_trip_keeps_evidence():
    from oyster.types import CostProfile, QualityEstimate

    priors = Priors(
        catch_rate={("cheap-scanner", "cheap-model", "logic"): 0.25},
        mean_cost={("cheap-scanner", "cheap-model"): Cost(0.01, 1.5)},
        corpus_size=4,
        quality={("cheap-scanner", "cheap-model", "logic"): QualityEstimate(0.25, 4, 0.05, 0.7)},
        cost={("cheap-scanner", "cheap-model"): CostProfile(0.01, 0.02, 1.0, 3.0, 4)},
    )
    text = priors_to_json(priors)
    assert '"ci_low": 0.05' in text and '"latency_p95": 3.0' in text
    assert priors_from_json(text) == priors
    # A v1 file without evidence still loads, with empty evidence maps.
    legacy = priors_from_json(
        '{"corpus_size": 1, "catch_rate": [{"role": "r", "model_alias": "m", '
        '"category": "logic", "rate": 0.5}], "mean_cost": [{"role": "r", '
        '"model_alias": "m", "dollars": 0.1, "latency_s": 2.0}]}'
    )
    assert legacy.quality == {} and legacy.cost == {}
    assert legacy.catch_rate[("r", "m", "logic")] == 0.5
