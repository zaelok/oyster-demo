from oyster.matching import match, overlap
from oyster.types import Finding, MatchReport, SeededBug


def bug(bug_id: str, start: int, end: int, category: str = "logic", file: str = "a.py"):
    return SeededBug(bug_id, file, start, end, category, "seeded")  # type: ignore[arg-type]


def finding(start: int, end: int, category: str = "logic", file: str = "a.py"):
    return Finding(file, start, end, category, "found", 0.8)  # type: ignore[arg-type]


def report(strict=(), loose=(), missed=(), fps=0):
    return MatchReport("case", "P", tuple(strict), tuple(loose), tuple(missed), fps)


def test_exact_range_same_category_is_strict_and_loose():
    assert match([finding(10, 12)], [bug("b1", 10, 12)], "case", "P") == report(["b1"], ["b1"])


def test_exact_range_wrong_category_is_loose_only():
    assert match([finding(10, 12, "style")], [bug("b1", 10, 12)], "case", "P") == report([], ["b1"])


def test_adjacent_ranges_do_not_overlap():
    assert match([finding(13, 15)], [bug("b1", 10, 12)], "case", "P") == report(
        [], [], ["b1"], fps=1
    )


def test_single_line_overlap_at_boundary_counts():
    assert match([finding(12, 20)], [bug("b1", 10, 12)], "case", "P") == report(["b1"], ["b1"])


def test_finding_spanning_two_bugs_goes_to_larger_overlap_only():
    bugs = [bug("b1", 1, 2), bug("b2", 5, 10)]
    assert match([finding(1, 10)], bugs, "case", "P") == report(["b2"], ["b2"], ["b1"])


def test_two_findings_on_one_bug_is_one_catch_extra_ignored():
    bugs = [bug("b1", 10, 12)]
    result = match([finding(10, 12), finding(11, 11)], bugs, "case", "P")
    assert result == report(["b1"], ["b1"], [], fps=0)


def test_tie_in_overlap_size_goes_to_lower_bug_id():
    bugs = [bug("b2", 5, 6), bug("b1", 1, 2)]
    assert match([finding(2, 5)], bugs, "case", "P") == report(["b1"], ["b1"], ["b2"])


def test_different_file_same_lines_is_no_overlap():
    result = match([finding(10, 12, file="other.py")], [bug("b1", 10, 12)], "case", "P")
    assert result == report([], [], ["b1"], fps=1)


def test_empty_findings_means_all_missed_and_zero_false_positives():
    bugs = [bug("b2", 5, 6), bug("b1", 1, 2)]
    assert match([], bugs, "case", "P") == report([], [], ["b1", "b2"], fps=0)


def test_overlap_helper():
    assert overlap(finding(1, 5), bug("b", 5, 9)) == 1
    assert overlap(finding(1, 5), bug("b", 6, 9)) == 0
    assert overlap(finding(3, 4), bug("b", 1, 10)) == 2
    assert overlap(finding(3, 4, file="z.py"), bug("b", 1, 10)) == 0


def test_report_carries_ids_and_is_sorted():
    result = match([finding(1, 1)], [bug("b1", 1, 1)], "case-9", "C")
    assert result.case_id == "case-9" and result.path_id == "C"
    bugs = [bug("b3", 30, 30), bug("b1", 10, 10), bug("b2", 20, 20)]
    result = match([finding(30, 30), finding(10, 10)], bugs, "case", "P")
    assert result.caught_strict == ("b1", "b3")
    assert result.missed == ("b2",)
