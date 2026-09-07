"""tools/build_corpus.py: the pure parts of the funnel, offline."""

import json

from oyster.corpus import load_case_dict
from tools import build_corpus as bc
from tools.build_corpus import Entry

REVERSED_DIFF = """\
--- a/pkg/pager.go
+++ b/pkg/pager.go
@@ -10,8 +10,5 @@ func next(cursor int) string {
 \tbase := "SELECT id FROM t"
-\twhere := " WHERE id >= :cursor"
+\twhere := " WHERE id > :cursor"
 \tq := base + where
-\tif cursor < 0 {
-\t\treturn ""
-\t}
 \treturn q
 }
"""


def _draft(diff: str = REVERSED_DIFF, seeded: list[dict] | None = None) -> dict:
    if seeded is None:
        seeded = [
            {
                "id": "case-x-1-b1",
                "file": "pkg/pager.go",
                "line_start": 11,
                "line_end": 11,
                "category": "logic",
                "description": "d",
            }
        ]
    return {"id": "case-x-1", "diff": diff, "seeded": seeded, "source": {"pr": "u"}}


def test_title_filter_keeps_fixes_and_drops_chores_and_fixtures():
    assert bc.title_verdict("[Bugfix] Fall back to T1 when ARC cannot reclaim") is None
    assert bc.title_verdict("fix: only subscribe when server advertises capability") is None
    assert bc.title_verdict("Fix Integration Tests thresholds") == "title:excluded-word"
    assert bc.title_verdict("Bump version to 1.2.3") == "title:excluded-word"
    assert bc.title_verdict("Add fused MoE tuned config") == "title:not-fix-like"
    assert bc.title_verdict("Exercise the conformance fixtures") == "title:not-fix-like"
    assert bc.title_verdict('Revert "fix the thing"') == "title:excluded-word"


def test_size_filter_reasons():
    base = {
        "merged_at": "2026-01-01T00:00:00Z",
        "user_type": "User",
        "user": "someone",
        "changed_files": 2,
        "additions": 10,
        "deletions": 5,
        "title": "fix x",
    }
    assert bc.size_verdict(base) is None
    assert bc.size_verdict(dict(base, merged_at="")) == "meta:not-merged"
    assert bc.size_verdict(dict(base, user_type="Bot")) == "meta:bot-author"
    assert bc.size_verdict(dict(base, user="stainless-app[bot]")) == "meta:bot-author"
    assert bc.size_verdict(dict(base, changed_files=9)) == "meta:too-many-files"
    assert bc.size_verdict(dict(base, additions=500)) == "meta:too-large"
    assert bc.size_verdict(dict(base, title="Revert fix x")) == "meta:revert"


def test_auto_category_needs_strong_security_words_and_never_says_style():
    assert bc.auto_category("fix memory leak in decoder", "", []) == ("logic", ["default"])
    assert bc.auto_category("cleanup unused imports", "", []) == ("logic", ["default"])
    category, hits = bc.auto_category("fix path traversal in file server", "", [])
    assert category == "security" and hits == ["traversal"]
    category, hits = bc.auto_category("harden parser", "Fixes CVE-2026-1234", ["security"])
    assert category == "security" and "security" in hits
    category, hits = bc.auto_category("redact provider keys from tracebacks", "", [])
    assert category == "security" and hits == ["redact"]
    assert bc.auto_category("fix leak of file handles", "", [])[0] == "logic"
    category, hits = bc.auto_category("fix api key leak in debug log", "", [])
    assert category == "security" and "leak+key" in hits


def test_language_facet_and_source_file_rule():
    assert bc.language_of(["a/b.py", "c.py", "d.cu"]) == "python"
    assert bc.language_of(["kernel.cu", "kernel.cuh"]) == "cuda"
    assert bc.language_of(["Sources/Foo.swift"]) == "swift"
    assert bc.language_of(["config.yaml", "a.py"]) is None
    assert bc.language_of([]) is None


def test_case_ids_compact_repo_names_and_avoid_collisions():
    taken: set[str] = set()
    assert bc.case_id_for("apple/swift-collections", 661, taken) == "case-swiftcollections-661"
    taken.add("case-flashattention-9")
    assert bc.case_id_for("Dao-AILab/flash-attention", 9, taken) == "case-daoailab-flashattention-9"


def test_widen_absence_grows_deletion_only_ranges_within_the_hunk():
    seeded = [
        {"id": "b1", "file": "pkg/pager.go", "line_start": 10, "line_end": 10},
        {"id": "b2", "file": "pkg/pager.go", "line_start": 13, "line_end": 13},
        {"id": "b3", "file": "pkg/pager.go", "line_start": 11, "line_end": 11},
    ]
    bc.widen_absence(seeded, ["deletion-only", "deletion-only", "added"], REVERSED_DIFF)
    assert (seeded[0]["line_start"], seeded[0]["line_end"]) == (10, 11)  # clipped at hunk start
    assert (seeded[1]["line_start"], seeded[1]["line_end"]) == (12, 14)  # clipped at hunk end
    assert (seeded[2]["line_start"], seeded[2]["line_end"]) == (11, 11)  # untouched


def test_gate_reasons_in_order():
    ok = _draft()
    assert bc.gate(ok, ["added"], "OK") is None
    assert bc.gate(ok, ["added"], "REJECTED: x") == "case:validator"
    assert bc.gate(_draft(seeded=[]), [], "OK") == "case:no-seeded"
    assert bc.gate(ok, ["added"] * 1, "OK") is None
    four = _draft(seeded=[dict(ok["seeded"][0], id=f"b{i}") for i in range(4)])
    assert bc.gate(four, ["added"] * 4, "OK") == "case:too-many-seeded"
    assert bc.gate(ok, ["unanchored"], "OK") == "case:unanchored"
    yaml_diff = REVERSED_DIFF.replace("pkg/pager.go", "deploy/values.yaml")
    assert bc.gate(_draft(diff=yaml_diff), ["added"], "OK") == "case:non-source-file"
    long_diff = REVERSED_DIFF + "".join(f" \tpad{i}\n" for i in range(bc.MAX_DIFF_LINES))
    assert bc.gate(_draft(diff=long_diff), ["added"], "OK") == "case:too-long"


def test_round_robin_cycles_orgs_then_repos_newest_first():
    entries = [
        Entry("mcp", "modelcontextprotocol/go-sdk", 1, "t"),
        Entry("mcp", "modelcontextprotocol/go-sdk", 5, "t"),
        Entry("mcp", "modelcontextprotocol/inspector", 3, "t"),
        Entry("litellm", "BerriAI/litellm", 9, "t"),
        Entry("litellm", "BerriAI/litellm", 8, "t"),
    ]
    ordered = bc.round_robin(entries, ["litellm", "mcp"])
    assert [(e.repo.split("/")[1], e.number) for e in ordered] == [
        ("litellm", 9),
        ("go-sdk", 5),
        ("litellm", 8),
        ("inspector", 3),
        ("go-sdk", 1),
    ]


def test_existing_sources_reads_urls_and_ids(tmp_path):
    raw = _draft()
    (tmp_path / "case-x-1.json").write_text(json.dumps(raw), encoding="utf-8")
    urls, ids = bc.existing_sources([tmp_path])
    assert urls == {"u"} and ids == {"case-x-1"}


def test_offline_github_never_calls_gh(tmp_path):
    gh = bc.GitHub(tmp_path, offline=True)
    try:
        gh.meta("o/r", 1)
    except RuntimeError as exc:
        assert "offline" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("offline GitHub must not fetch")


def test_reports_are_written_from_entries(tmp_path):
    accepted = Entry(
        "mcp",
        "modelcontextprotocol/go-sdk",
        5,
        "fix x",
        merged_at="2026-08-01T00:00:00Z",
        outcome="accepted",
        case_id="case-gosdk-5",
        language="go",
        category="logic",
        seeded=2,
        kinds=["added", "deletion-only"],
    )
    rejected = Entry(
        "mcp",
        "modelcontextprotocol/go-sdk",
        4,
        "bump",
        outcome="rejected",
        reason="title:excluded-word",
    )
    bc.write_sources(tmp_path, [accepted], "2025-09-01")
    bc.write_candidates(tmp_path, [accepted, rejected])
    bc.write_report(
        tmp_path, [accepted, rejected], [accepted], ["search failed for x"], "2025-09-01"
    )
    sources = (tmp_path / "SOURCES.md").read_text(encoding="utf-8")
    assert "| case-gosdk-5 | https://github.com/modelcontextprotocol/go-sdk/pull/5 |" in sources
    assert "1 cases, 2 seeded bugs." in sources
    rows = [json.loads(line) for line in (tmp_path / "candidates.jsonl").read_text().splitlines()]
    assert {row["outcome"] for row in rows} == {"accepted", "rejected"}
    report = (tmp_path / "BUILD-REPORT.md").read_text(encoding="utf-8")
    assert "| title:excluded-word | 1 |" in report and "search failed for x" in report


def test_widened_draft_still_validates():
    draft = _draft(
        seeded=[
            {
                "id": "case-x-1-b1",
                "file": "pkg/pager.go",
                "line_start": 13,
                "line_end": 13,
                "category": "logic",
                "description": "d",
            }
        ]
    )
    bc.widen_absence(draft["seeded"], ["deletion-only"], draft["diff"])
    assert load_case_dict(draft, "case-x-1").seeded[0].line_end == 14
