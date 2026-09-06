"""Finding-to-seeded-bug matcher. These rules determine every number in the results table, so
they are normative (spec §8) and not a matter of implementation taste.

1. A finding overlaps a bug when both name the same file and their inclusive line ranges
   share at least one line.
2. Strict catch: overlap and equal category. Loose catch: overlap, category ignored.
3. Each finding is assigned to at most one bug: the largest overlap, ties to the lowest bug
   id. Each bug is caught by at most one finding; later findings on a caught bug are ignored,
   neither catches nor false positives. Findings are processed in the order given.
4. A finding overlapping no bug is a false positive. Only the count is reported.
"""

from collections.abc import Sequence

from oyster.types import Finding, MatchReport, SeededBug

__all__ = ["match", "overlap"]


def overlap(finding: Finding, bug: SeededBug) -> int:
    """Number of shared lines, 0 when the files differ or the ranges do not intersect."""
    if finding.file != bug.file:
        return 0
    low = max(finding.line_start, bug.line_start)
    high = min(finding.line_end, bug.line_end)
    return max(0, high - low + 1)


def match(
    findings: Sequence[Finding],
    seeded: Sequence[SeededBug],
    case_id: str,
    path_id: str,
) -> MatchReport:
    strict: set[str] = set()
    loose: set[str] = set()
    false_positives = 0

    for finding in findings:
        best: SeededBug | None = None
        best_overlap = 0
        for bug in seeded:
            shared = overlap(finding, bug)
            if shared == 0:
                continue
            if shared > best_overlap:
                best, best_overlap = bug, shared
            elif shared == best_overlap and best is not None and bug.id < best.id:
                best = bug
        if best is None:
            false_positives += 1
            continue
        if best.id in loose:
            continue
        loose.add(best.id)
        if finding.category == best.category:
            strict.add(best.id)

    missed = tuple(sorted(bug.id for bug in seeded if bug.id not in loose))
    return MatchReport(
        case_id=case_id,
        path_id=path_id,
        caught_strict=tuple(sorted(strict)),
        caught_loose=tuple(sorted(loose)),
        missed=missed,
        false_positives=false_positives,
    )
