"""The genericity test: bug fixing runs on the unchanged engine with a scenario plugin."""

import json

from oyster.evaluation import calibrate, evaluate
from oyster.executor import run_path
from oyster.graph import validate_path
from oyster.scenarios.bug_fixing import (
    CATALOG_FIX,
    PATH_F1,
    PATH_F2,
    BugFixingScenario,
    FixTask,
    Patch,
    RunOutcome,
    load_fix_tasks,
    parse_patch,
)
from tests.conftest import ScriptedProvider

REFERENCE = "--- a/pkg/pager.go\n+++ b/pkg/pager.go\n@@ -1 +1 @@\n-x := 1\n+x := 2\n"
GOOD_PATCH = "```diff\n--- a/pkg/pager.go\n+++ b/pkg/pager.go\n@@ -1 +1 @@\n-x := 1\n+x := 3\n```"
WIDE_PATCH = (
    "```diff\n--- a/pkg/pager.go\n+++ b/pkg/pager.go\n@@ -1 +1 @@\n-x := 1\n+x := 3\n"
    "--- a/pkg/other.go\n+++ b/pkg/other.go\n@@ -1 +1 @@\n-y := 1\n+y := 2\n```"
)
WRONG_PATCH = "--- a/pkg/other.go\n+++ b/pkg/other.go\n@@ -1 +1 @@\n-y := 1\n+y := 2\n"

TASK = FixTask(
    id="fix-01",
    repo="example/pager",
    base_commit="abc123",
    failing_tests=("TestNextSkipsCursorRow",),
    reference_patch=REFERENCE,
    description="the cursor row is skipped",
    test_command="go test ./...",
)


def test_parse_patch_from_fence_and_raw():
    (patch,) = parse_patch(GOOD_PATCH)
    assert patch.files == ("pkg/pager.go",)
    assert patch.text.startswith("--- a/pkg/pager.go")
    (raw,) = parse_patch(WRONG_PATCH)
    assert raw.files == ("pkg/other.go",)
    assert parse_patch("I could not produce a patch.") is None
    assert parse_patch("```diff\nnot a diff\n```") is None


def test_structural_scoring_without_a_runner():
    scenario = BugFixingScenario()
    good = scenario.score(parse_patch(GOOD_PATCH), TASK, "F1")
    assert (good.caught_strict, good.caught_loose, good.missed, good.false_positives) == (
        ("fix-01",),
        ("fix-01",),
        (),
        0,
    )
    wide = scenario.score(parse_patch(WIDE_PATCH), TASK, "F1")
    assert (wide.caught_strict, wide.caught_loose, wide.false_positives) == ((), ("fix-01",), 1)
    wrong = scenario.score(parse_patch(WRONG_PATCH), TASK, "F1")
    assert (wrong.caught_loose, wrong.missed, wrong.false_positives) == ((), ("fix-01",), 1)
    assert scenario.score((), TASK, "F1").missed == ("fix-01",)


def test_runner_outcome_drives_strict_and_loose():
    calls = []

    def runner(task: FixTask, patch: Patch) -> RunOutcome:
        calls.append((task.id, patch.files))
        return RunOutcome(target_passed=True, all_passed=False, detail="one regression")

    report = BugFixingScenario(runner=runner).score(parse_patch(GOOD_PATCH), TASK, "F1")
    assert report.caught_loose == ("fix-01",) and report.caught_strict == ()
    assert calls == [("fix-01", ("pkg/pager.go",))]


def test_bug_fixing_runs_on_the_unchanged_engine(bindings):
    scenario = BugFixingScenario(runner=lambda task, patch: RunOutcome(True, True))
    provider = ScriptedProvider([GOOD_PATCH])
    for path in CATALOG_FIX:
        validate_path(path, set(bindings), scenario.prompt_keys())

    result = run_path(PATH_F1, TASK, provider, bindings, scenario=scenario)
    assert result.path_id == "F1" and len(result.node_results) == 1
    assert result.findings[0].files == ("pkg/pager.go",)
    assert provider.calls[0]["cached_prefix"] == TASK.context
    assert "unified diff only" in provider.calls[0]["user"]

    results, reports = evaluate(
        CATALOG_FIX, [TASK], ScriptedProvider([GOOD_PATCH]), bindings, scenario=scenario
    )
    assert [r.path_id for r in results] == ["F1", "F2"]
    assert all(report.caught_strict == ("fix-01",) for report in reports)
    assert all(result.cost.dollars > 0 for result in results)


def test_cascade_passes_the_first_patch_as_a_hint(bindings):
    scenario = BugFixingScenario()
    provider = ScriptedProvider([WRONG_PATCH, GOOD_PATCH])
    result = run_path(PATH_F2, TASK, provider, bindings, scenario=scenario)
    assert "EARLIER PATCH" not in provider.calls[0]["user"]
    assert "EARLIER PATCH" in provider.calls[1]["user"]
    assert "pkg/other.go" in provider.calls[1]["user"]
    assert result.findings[0].files == ("pkg/pager.go",), "last node wins"


def test_calibrate_works_for_the_second_scenario(bindings):
    scenario = BugFixingScenario()
    priors = calibrate([TASK], ScriptedProvider([GOOD_PATCH]), bindings, CATALOG_FIX, scenario)
    assert priors.corpus_size == 1
    assert ("patcher", "strong-model") in priors.mean_cost
    assert ("patcher", "cheap-model") in priors.mean_cost


def test_load_fix_tasks_validates(tmp_path):
    (tmp_path / "fix-01.json").write_text(
        json.dumps(
            {
                "id": "fix-01",
                "repo": "example/pager",
                "base_commit": "abc123",
                "failing_tests": ["TestNext"],
                "reference_patch": REFERENCE,
                "description": "skips the row",
            }
        ),
        encoding="utf-8",
    )
    (tasks,) = load_fix_tasks(tmp_path)
    assert tasks.id == "fix-01" and tasks.failing_tests == ("TestNext",)
    (tmp_path / "fix-02.json").write_text(
        json.dumps({"id": "fix-02", "repo": "r", "base_commit": "c", "reference_patch": "nope"}),
        encoding="utf-8",
    )
    try:
        load_fix_tasks(tmp_path)
    except ValueError as exc:
        assert "reference_patch" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("expected a validation error")
