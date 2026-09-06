import pytest

from oyster.corpus import load_case_file, load_cases, parse_diff, validate_case, validate_corpus
from oyster.types import CorpusCase, SeededBug
from tests.conftest import CORPUS_DIR, INVALID_DIR


def test_valid_fixture_corpus_loads():
    cases = load_cases(CORPUS_DIR)
    assert [case.id for case in cases] == ["case-01"]
    case = cases[0]
    assert {bug.file for bug in case.seeded} == {"pricing.py", "auth.py"}
    assert {bug.category for bug in case.seeded} == {"logic", "security"}


def test_parse_diff_new_side_ranges(corpus_case):
    hunks = parse_diff(corpus_case.diff)
    assert hunks == {"pricing.py": [(1, 14)], "auth.py": [(20, 26)]}


def test_parse_diff_handles_dev_null_and_default_counts():
    diff = "--- /dev/null\n+++ b/new.py\n@@ -0,0 +1 @@\n+x = 1\n--- a/gone.py\n+++ /dev/null\n@@ -1 +0,0 @@\n-y\n"
    assert parse_diff(diff) == {"new.py": [(1, 1)]}


@pytest.mark.parametrize(
    ("filename", "field"),
    [
        ("case-bad-id.json", "'id' does not match filename stem"),
        ("case-empty-diff.json", "'diff' is empty"),
        ("case-bad-file.json", "field 'file' 'billing.py'"),
        ("case-bad-range.json", "'line_start'/'line_end' (9, 7)"),
        ("case-outside-hunk.json", "(40-41) fall outside"),
        ("case-bad-category.json", "field 'category' 'perf'"),
        ("case-dup-bug.json", "seeded field 'id' 'case-01-b1' is duplicated"),
    ],
)
def test_each_invalid_fixture_triggers_exactly_its_rule(filename, field):
    with pytest.raises(ValueError, match=r"case '.*?':") as excinfo:
        load_case_file(INVALID_DIR / filename)
    assert field in str(excinfo.value)


def test_invalid_fixture_dir_has_exactly_seven_cases():
    assert len(list(INVALID_DIR.glob("*.json"))) == 7


def test_diff_without_hunk_is_rejected():
    case = CorpusCase("c", "--- a/x.py\n+++ b/x.py\njust text\n", ())
    with pytest.raises(ValueError, match="at least one hunk"):
        validate_case(case)


def test_duplicate_ids_across_corpus_are_rejected(corpus_case):
    with pytest.raises(ValueError, match="duplicated across the corpus"):
        validate_corpus((corpus_case, corpus_case))


def test_missing_field_names_case_and_field(tmp_path):
    (tmp_path / "case-x.json").write_text('{"id": "case-x", "seeded": []}')
    with pytest.raises(ValueError, match="case 'case-x': case field 'diff' is missing"):
        load_case_file(tmp_path / "case-x.json")


def test_wrong_type_names_case_and_field(tmp_path):
    (tmp_path / "case-y.json").write_text(
        '{"id": "case-y", "diff": "--- a/x\\n+++ b/x\\n@@ -1 +1 @@\\n+a\\n", '
        '"seeded": [{"id": "b", "file": "x", "line_start": "1", "line_end": 1, '
        '"category": "logic", "description": ""}]}'
    )
    with pytest.raises(ValueError, match="seeded\\[0\\] field 'line_start' must be int"):
        load_case_file(tmp_path / "case-y.json")


def test_zero_line_is_rejected():
    case = CorpusCase(
        "c",
        "--- a/x.py\n+++ b/x.py\n@@ -1 +1 @@\n+a\n",
        (SeededBug("b", "x.py", 0, 1, "logic", ""),),
    )
    with pytest.raises(ValueError, match="must be positive"):
        validate_case(case)


def test_templates_and_readme_are_not_loaded_as_cases():
    from pathlib import Path

    real_corpus = Path("oyster/corpus/cases")
    assert (real_corpus / "_example.json.template").exists()
    assert (real_corpus / "README.md").exists()
    assert load_cases(real_corpus) == () or all(
        case.id.startswith("case-") for case in load_cases(real_corpus)
    )
