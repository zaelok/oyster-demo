import json

from oyster.corpus import load_case_file, parse_diff
from tools.pr_to_case import (
    candidates,
    clean_title,
    guess_category,
    is_trivial,
    leak_hits,
    main,
    parse_git_diff,
    render_diff,
    reverse,
    run,
    select_files,
    strip_removed_comments,
)

FIX_DIFF = """\
diff --git a/pkg/pager.go b/pkg/pager.go
index 1111111..2222222 100644
--- a/pkg/pager.go
+++ b/pkg/pager.go
@@ -10,5 +10,8 @@ func next(cursor int) string {
 \tbase := "SELECT id FROM t"
-\twhere := " WHERE id > :cursor"
+\twhere := " WHERE id >= :cursor"
 \tq := base + where
+\tif cursor < 0 {
+\t\treturn ""
+\t}
 \treturn q
 }
\\ No newline at end of file
diff --git a/pkg/pager_test.go b/pkg/pager_test.go
index 3333333..4444444 100644
--- a/pkg/pager_test.go
+++ b/pkg/pager_test.go
@@ -1,2 +1,3 @@
 package pkg
+// regression test for the fix
 func TestNext() {}
diff --git a/pkg/new_helper.go b/pkg/new_helper.go
new file mode 100644
--- /dev/null
+++ b/pkg/new_helper.go
@@ -0,0 +1,2 @@
+package pkg
+func helper() {}
"""

COMMENT_FIX_DIFF = """\
--- a/svc/cast.go
+++ b/svc/cast.go
@@ -5,3 +5,6 @@ func nullText() string {
 \tif opt {
-\t\treturn "NULL::text AS d"
+\t\t// sqlx rewrites :: to : so the ANSI cast form is required here.
+\t\t// Keep CAST(NULL AS text).
+\t\treturn "CAST(NULL AS text) AS d"
+\t\t// trailing note
 \t}
"""

TRIVIAL_FIX_DIFF = """\
--- a/pkg/x.go
+++ b/pkg/x.go
@@ -1,6 +1,7 @@
 package pkg

 import (
+\t"fmt"
 \t"os"
 )

@@ -20,3 +21,3 @@ func run() {
 \tstart()
-\tfmt.Println("ok")
+\tfmt.Println("started")
 }
"""

VIEW = {
    "title": "[APSS-2382] BUG: Fix pagination skipping the cursor row",
    "body": "ListStoreUpdates skipped the token row because the SQL used > instead of >=.",
    "labels": [],
    "files": [],
}


def _write_inputs(tmp_path, diff_text=FIX_DIFF):
    view_path = tmp_path / "pr.json"
    diff_path = tmp_path / "pr.diff"
    view_path.write_text(json.dumps(VIEW), encoding="utf-8")
    diff_path.write_text(diff_text, encoding="utf-8")
    return view_path, diff_path


def test_parse_reads_files_hunks_and_no_newline_marker():
    files = parse_git_diff(FIX_DIFF)
    assert [file.path for file in files] == [
        "pkg/pager.go",
        "pkg/pager_test.go",
        "pkg/new_helper.go",
    ]
    pager = files[0]
    assert (pager.old_path, pager.new_path) == ("pkg/pager.go", "pkg/pager.go")
    hunk = pager.hunks[0]
    assert (hunk.old_start, hunk.old_count, hunk.new_start, hunk.new_count) == (10, 5, 10, 8)
    assert hunk.lines[-1] == "\\ No newline at end of file"
    assert files[2].old_path is None


def test_select_files_drops_tests_and_new_files():
    kept, dropped = select_files(
        parse_git_diff(FIX_DIFF), keep_tests=False, keep_new_files=False, only=()
    )
    assert [file.path for file in kept] == ["pkg/pager.go"]
    assert {path for path, _ in dropped} == {"pkg/pager_test.go", "pkg/new_helper.go"}
    kept_all, _ = select_files(
        parse_git_diff(FIX_DIFF), keep_tests=True, keep_new_files=True, only=()
    )
    assert len(kept_all) == 3


def test_reverse_swaps_sides_and_orders_removed_before_added():
    pager = parse_git_diff(FIX_DIFF)[0]
    reversed_file = reverse(pager)
    hunk = reversed_file.hunks[0]
    assert hunk.header() == "@@ -10,8 +10,5 @@ func next(cursor int) string {"
    assert hunk.lines == [
        ' \tbase := "SELECT id FROM t"',
        '-\twhere := " WHERE id >= :cursor"',
        '+\twhere := " WHERE id > :cursor"',
        " \tq := base + where",
        "-\tif cursor < 0 {",
        '-\t\treturn ""',
        "-\t}",
        " \treturn q",
        " }",
        "\\ No newline at end of file",
    ]


def test_candidates_seed_added_lines_and_flag_deletion_only():
    pager = reverse(parse_git_diff(FIX_DIFF)[0])
    found = candidates(pager)
    assert [(c.line_start, c.line_end, c.kind) for c in found] == [
        (11, 11, "added"),
        (13, 13, "deletion-only"),
    ]
    assert found[0].added == ['\twhere := " WHERE id > :cursor"']
    assert found[0].removed == ['\twhere := " WHERE id >= :cursor"']
    assert found[1].removed == ["\tif cursor < 0 {", '\t\treturn ""', "\t}"]


def test_rendered_reversed_diff_is_accepted_by_the_corpus_parser():
    pager = reverse(parse_git_diff(FIX_DIFF)[0])
    text = render_diff([pager])
    assert text.startswith("--- a/pkg/pager.go\n+++ b/pkg/pager.go\n@@ -10,8 +10,5 @@")
    assert parse_diff(text) == {"pkg/pager.go": [(10, 14)]}


def test_strip_removed_comments_drops_the_fix_narration():
    cast = reverse(parse_git_diff(COMMENT_FIX_DIFF)[0])
    assert strip_removed_comments(cast) == 3
    hunk = cast.hunks[0]
    assert hunk.header() == "@@ -5,3 +5,3 @@ func nullText() string {"
    assert not any(line.startswith("-\t\t//") for line in hunk.lines)
    assert [(c.line_start, c.line_end, c.kind) for c in candidates(cast)] == [(6, 6, "added")]
    assert parse_diff(render_diff([cast])) == {"svc/cast.go": [(5, 7)]}


def test_trivial_candidates_are_skipped_unless_kept(tmp_path):
    json_path, review_path, verdict = run(
        VIEW, TRIVIAL_FIX_DIFF, case_id="case-80", out_dir=tmp_path, source={}
    )
    assert verdict == "OK"
    case = load_case_file(json_path)
    assert [(bug.line_start, bug.line_end) for bug in case.seeded] == [(21, 21)]
    review = review_path.read_text(encoding="utf-8")
    assert "Skipped trivial candidates: 1" in review

    json_path, _, _ = run(
        VIEW, TRIVIAL_FIX_DIFF, case_id="case-81", out_dir=tmp_path, source={}, keep_trivial=True
    )
    assert len(load_case_file(json_path).seeded) == 2


def test_is_trivial_recognises_imports_comments_and_braces():
    from tools.pr_to_case import Candidate

    assert is_trivial(Candidate("f", 1, 1, "added", ['\t"fmt"', "}", "// note", ""], []))
    assert not is_trivial(Candidate("f", 1, 1, "added", ["x := 1"], []))
    assert is_trivial(Candidate("f", 1, 1, "deletion-only", [], ["import os"]))


def test_additive_mode_hides_the_fixed_code(tmp_path):
    json_path, review_path, verdict = run(
        VIEW, FIX_DIFF, case_id="case-82", out_dir=tmp_path, source={}, mode="additive"
    )
    assert verdict == "OK"
    case = load_case_file(json_path)
    body = case.diff.splitlines()
    assert body[:3] == [
        "--- /dev/null",
        "+++ b/pkg/pager.go",
        "@@ -0,0 +10,5 @@ func next(cursor int) string {",
    ]
    assert all(not line.startswith("-") for line in body[1:])
    assert parse_diff(case.diff) == {"pkg/pager.go": [(10, 14)]}
    assert [(bug.line_start, bug.line_end) for bug in case.seeded] == [(11, 11)]
    review = review_path.read_text(encoding="utf-8")
    assert "Mode: additive" in review
    assert "Dropped in additive mode: 1 absence bug(s)" in review


def test_category_and_title_heuristics():
    assert guess_category("Fix SQL injection in search", "", [])[0] == "security"
    assert guess_category("chore: remove unused import", "", [])[0] == "style"
    assert guess_category("Fix pagination skipping rows", "returns wrong page", [])[0] == "logic"
    payments = "authorizeStripePayment rejected a saved card; clientSecret in response"
    assert guess_category("bug: support saved-card authorization", payments, [])[0] == "logic"
    assert (
        clean_title("[APSS-2382] BUG: Fix pagination skipping rows") == "pagination skipping rows"
    )
    assert clean_title("APSS-1: fixes the thing.") == "the thing"


def test_fetch_pr_pins_utf8_decoding(monkeypatch):
    import subprocess

    from tools import pr_to_case

    calls: list[dict] = []

    def fake_run(args, **kwargs):
        calls.append(kwargs)
        stdout = '{"title": "curly “quotes”"}' if args[1] == "pr" and args[2] == "view" else "diff"
        return subprocess.CompletedProcess(args, 0, stdout=stdout, stderr="")

    monkeypatch.setattr(pr_to_case.subprocess, "run", fake_run)
    view, diff = pr_to_case.fetch_pr("https://github.com/o/r/pull/1")
    assert view["title"] == "curly “quotes”"
    assert diff == "diff"
    assert all(call["encoding"] == "utf-8" for call in calls)
    assert all("text" not in call for call in calls)


def test_leak_check_flags_fix_words_tickets_and_security_vocabulary():
    text = "--- a/x\n+++ b/x\n@@ -1 +1 @@\n+// APSS-12 workaround for the bug\n+ok := 1\n"
    assert leak_hits(text) == [(4, "+// APSS-12 workaround for the bug")]
    docstring = "--- a/x\n+++ b/x\n@@ -1 +1 @@\n-    (SSRF risk: loopback, redirects)\n+    ok\n"
    assert leak_hits(docstring) == [(4, "-    (SSRF risk: loopback, redirects)")]


def test_test_paths_match_case_insensitively():
    from tools.pr_to_case import is_test_path

    assert is_test_path("Tests/NIOHTTP1Tests/HTTPResponseEncoderTest.swift")
    assert is_test_path("src/test/java/FooTest.java")
    assert is_test_path("core/src/FooTests.kt")
    assert is_test_path("web/button.spec.tsx")
    assert is_test_path("rust/src/verifier_tests.rs")
    assert not is_test_path("Sources/NIOHTTP1/HTTPEncoder.swift")
    assert not is_test_path("pkg/contest.go")


def test_main_writes_valid_draft_and_review(tmp_path):
    view_path, diff_path = _write_inputs(tmp_path)
    out = tmp_path / "drafts"

    code = main(
        ["--view", str(view_path), "--diff", str(diff_path), "--id", "case-77", "--out", str(out)]
    )
    assert code == 0

    case = load_case_file(out / "case-77.json")
    assert case.id == "case-77"
    assert [(bug.line_start, bug.line_end, bug.category) for bug in case.seeded] == [
        (11, 11, "logic"),
        (13, 13, "logic"),
    ]
    assert "pkg/pager_test.go" not in case.diff
    raw = json.loads((out / "case-77.json").read_text(encoding="utf-8"))
    assert raw["source"] == {"view": "pr.json", "diff": "pr.diff"}

    review = (out / "case-77.review.md").read_text(encoding="utf-8")
    assert "Validator: OK" in review
    assert "Mode: reverse" in review
    assert "Category guess: **logic**" in review
    assert "deletion-only" in review
    assert "dropped `pkg/pager_test.go`" in review
    assert "Leak check: 0 hit(s)" in review
    assert "Stripped removed comment lines: 0" in review


def test_category_override_and_file_filter(tmp_path):
    view_path, diff_path = _write_inputs(tmp_path)
    main(
        [
            "--view",
            str(view_path),
            "--diff",
            str(diff_path),
            "--id",
            "case-78",
            "--out",
            str(tmp_path),
            "--category",
            "style",
            "--files",
            "pager.go",
        ]
    )
    case = load_case_file(tmp_path / "case-78.json")
    assert {bug.category for bug in case.seeded} == {"style"}
