"""Corpus loader and validator.

Cases are human authored ground truth (see cases/README.md). This module never writes them;
it only refuses to load ones that are malformed, naming the case id and the offending field.
"""

import json
import re
from pathlib import Path

from oyster.types import CATEGORIES, CorpusCase, SeededBug

__all__ = ["load_case_file", "load_cases", "parse_diff", "validate_case", "validate_corpus"]

_HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def _strip_prefix(path: str) -> str:
    path = path.strip()
    if path.startswith(("a/", "b/")):
        return path[2:]
    return path


def parse_diff(diff: str) -> dict[str, list[tuple[int, int]]]:
    """Map each target path (new-file side, 'a/' or 'b/' prefix stripped) to the inclusive
    new-side line ranges of its hunks. A hunk that adds no lines contributes no range."""
    files: dict[str, list[tuple[int, int]]] = {}
    current: str | None = None
    previous = ""
    for line in diff.splitlines():
        if line.startswith("+++ ") and previous.startswith("--- "):
            target = _strip_prefix(line[4:].split("\t", 1)[0])
            current = None if target == "/dev/null" else target
            if current is not None:
                files.setdefault(current, [])
        else:
            hunk = _HUNK.match(line)
            if hunk and current is not None:
                start = int(hunk.group(3))
                count = int(hunk.group(4)) if hunk.group(4) is not None else 1
                if count > 0:
                    files[current].append((start, start + count - 1))
        previous = line
    return files


def _hunk_count(diff: str) -> int:
    return sum(1 for line in diff.splitlines() if _HUNK.match(line))


def validate_case(case: CorpusCase) -> None:
    """Rules 2 to 7 of spec §9. Rule 1 (id matches filename, unique across the corpus) lives in
    load_case_file and validate_corpus because it needs the filename and the other cases."""
    if not case.diff.strip():
        raise ValueError(f"case {case.id!r}: field 'diff' is empty")
    hunks = parse_diff(case.diff)
    if not hunks or _hunk_count(case.diff) == 0:
        raise ValueError(
            f"case {case.id!r}: field 'diff' is not a unified diff with at least one hunk"
        )

    for bug in case.seeded:
        if bug.file not in hunks:
            raise ValueError(
                f"case {case.id!r}: seeded {bug.id!r} field 'file' {bug.file!r} "
                "is not a target path in the diff"
            )

    for bug in case.seeded:
        if bug.line_start < 1 or bug.line_end < 1 or bug.line_start > bug.line_end:
            raise ValueError(
                f"case {case.id!r}: seeded {bug.id!r} fields 'line_start'/'line_end' "
                f"({bug.line_start}, {bug.line_end}) must be positive with start <= end"
            )

    for bug in case.seeded:
        inside = any(
            start <= bug.line_start and bug.line_end <= end for start, end in hunks[bug.file]
        )
        if not inside:
            raise ValueError(
                f"case {case.id!r}: seeded {bug.id!r} fields 'line_start'/'line_end' "
                f"({bug.line_start}-{bug.line_end}) fall outside every new-file hunk "
                f"of {bug.file!r}"
            )

    for bug in case.seeded:
        if bug.category not in CATEGORIES:
            raise ValueError(
                f"case {case.id!r}: seeded {bug.id!r} field 'category' {bug.category!r} "
                f"is not one of {CATEGORIES}"
            )

    seen: set[str] = set()
    for bug in case.seeded:
        if bug.id in seen:
            raise ValueError(f"case {case.id!r}: seeded field 'id' {bug.id!r} is duplicated")
        seen.add(bug.id)


def validate_corpus(cases: tuple[CorpusCase, ...]) -> None:
    """Rule 1, second half: ids unique across the corpus."""
    seen: set[str] = set()
    for case in cases:
        if case.id in seen:
            raise ValueError(f"case {case.id!r}: field 'id' is duplicated across the corpus")
        seen.add(case.id)


def _require(raw: dict, field: str, kind: type, case_id: str, where: str) -> object:
    if field not in raw:
        raise ValueError(f"case {case_id!r}: {where} field {field!r} is missing")
    value = raw[field]
    if not isinstance(value, kind) or isinstance(value, bool):
        # Every malformed field is a ValueError naming case and field (spec §9), so callers
        # catch one type.
        raise ValueError(  # noqa: TRY004
            f"case {case_id!r}: {where} field {field!r} must be {kind.__name__}, "
            f"got {type(value).__name__}"
        )
    return value


def _from_raw(raw: object, source: Path) -> CorpusCase:
    if not isinstance(raw, dict):
        raise ValueError(f"case {source.stem!r}: file must contain a JSON object")  # noqa: TRY004
    case_id = str(raw.get("id", source.stem))
    _require(raw, "id", str, case_id, "case")
    diff = _require(raw, "diff", str, case_id, "case")
    seeded_raw = _require(raw, "seeded", list, case_id, "case")
    seeded: list[SeededBug] = []
    for index, item in enumerate(seeded_raw):  # type: ignore[union-attr]
        where = f"seeded[{index}]"
        if not isinstance(item, dict):
            raise ValueError(f"case {case_id!r}: {where} must be an object")  # noqa: TRY004
        seeded.append(
            SeededBug(
                id=str(_require(item, "id", str, case_id, where)),
                file=str(_require(item, "file", str, case_id, where)),
                line_start=int(_require(item, "line_start", int, case_id, where)),  # type: ignore[call-overload]
                line_end=int(_require(item, "line_end", int, case_id, where)),  # type: ignore[call-overload]
                category=str(_require(item, "category", str, case_id, where)),  # type: ignore[arg-type]
                description=str(_require(item, "description", str, case_id, where)),
            )
        )
    return CorpusCase(id=case_id, diff=str(diff), seeded=tuple(seeded))


def load_case_file(path: Path) -> CorpusCase:
    """Parse and validate one case file. Rule 1 first half: id matches the filename stem."""
    path = Path(path)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"case {path.stem!r}: file is not valid JSON ({exc})") from exc
    case = _from_raw(raw, path)
    if case.id != path.stem:
        raise ValueError(f"case {case.id!r}: field 'id' does not match filename stem {path.stem!r}")
    validate_case(case)
    return case


def load_cases(corpus_dir: Path) -> tuple[CorpusCase, ...]:
    """Load every *.json case in corpus_dir, validated, sorted by id. Templates and READMEs are
    ignored because they do not end in .json."""
    corpus_dir = Path(corpus_dir)
    cases = tuple(load_case_file(path) for path in sorted(corpus_dir.glob("*.json")))
    validate_corpus(cases)
    return tuple(sorted(cases, key=lambda case: case.id))
