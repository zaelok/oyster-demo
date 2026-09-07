"""Draft an OYSTER corpus case from a bug-fix pull request by reversing the fix.

A fix PR removes a defect; the corpus needs a diff that introduces one. Reversing the fix
makes the fixed code the "before" side and the buggy code the "after" side, and the lines
the fix replaced become the seeded bug on the new-file side, with ground truth that came
from a real defect. The human still chooses the PR and signs off on every draft: category,
line range, description and trimming. This tool only does the mechanical part.

    python -m tools.pr_to_case --pr https://github.com/OWNER/REPO/pull/N --id case-02 --out drafts
    python -m tools.pr_to_case --view pr.json --diff pr.diff --id case-02 --out drafts

`--view` is the JSON from `gh pr view --json title,body,labels,files`; `--diff` is the output
of `gh pr diff`. Test files, mocks, docs and generated code are dropped because a reversed
diff that deletes a regression test gives the answer away. Files the fix created are dropped
too: reversed, they are whole-file deletions and cannot host a seeded bug.

Two modes. `reverse` (default) shows the fixed code being replaced by the buggy code, so the
reviewer sees both sides; the fix's own comments are stripped from the removed lines because
they tend to narrate the answer. `additive` presents the buggy hunks as newly added code with
no removed lines at all, which hides the fix entirely but cannot seed "absence" bugs.

Each draft is written next to a review sheet that shows every candidate bug in context, the
category guess and why, the leak check, and the validator verdict. Nothing goes into
oyster/corpus/cases/ until a human moves it there.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

from oyster.corpus import load_case_dict
from oyster.types import CATEGORIES

MODES = ("reverse", "additive")

# Matched case-insensitively: Swift and Java projects capitalise Tests/ and FooTests.swift.
TEST_PATTERNS = (
    r"_test\.go$",
    r"(^|/)test_[^/]*\.py$",
    r"_test\.py$",
    r"tests?\.(swift|java|kt|scala|cs)$",
    r"_tests?\.rs$",
    r"\.(test|spec)\.[jt]sx?$",
    r"(^|/)tests?/",
    r"(^|/)testing/",
    r"(^|/)testdata/",
    r"(^|/)mocks?/",
    r"mockery",
    r"\.snap$",
    r"\.golden$",
)
NOISE_PATTERNS = (
    r"(^|/)scripts/manual/",
    r"\.md$",
    r"(^|/)CHANGELOG",
    r"(^|/)docs?/",
    r"\.pb\.go$",
    r"\.gen\.go$",
    r"_generated\.",
    r"\.lock$",
    r"(^|/)go\.sum$",
)

SECURITY_WORDS = (
    "security",
    "cve",
    "inject",
    "xss",
    "csrf",
    "authz",
    "authoriz",
    "authent",
    "permission",
    "secret",
    "credential",
    "sanitiz",
    "escap",
    "unsafe",
    "deserializ",
    "leak",
    "exposure",
)
# In a payments codebase "authorization" and "client secret" are Stripe vocabulary, not
# access control, so those hits are discounted when the text is about payments.
PAYMENT_WORDS = ("payment", "stripe", "card", "checkout", "wallet")
PAYMENT_FALSE_POSITIVES = ("authoriz", "authent", "secret")
STYLE_WORDS = (
    "lint",
    "unused",
    "rename",
    "naming",
    "typo",
    "dead code",
    "format",
    "cleanup",
    "clean up",
    "docstring",
    "cosmetic",
)
BEHAVIOR_WORDS = ("crash", "error", "incorrect", "wrong", "fail", "500", "panic", "skip")

_HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)$")
_TICKET_RE = re.compile(r"\b[A-Z][A-Z0-9]{1,9}-\d+\b")
_LEAK_RE = re.compile(
    r"\b(fix(?:es|ed)?|bug|regression|hotfix|workaround|todo|fixme|hack"
    r"|vulnerab\w*|risk|security|unsafe|cve|exploit|ssrf)\b",
    re.IGNORECASE,
)
_PR_URL_RE = re.compile(r"github\.com/([^/]+)/([^/]+)/pull/(\d+)")
# A '#' line is a comment unless it is a preprocessor directive, a Rust/Swift attribute or a
# shebang: those are code and must survive the removed-comment stripper.
_COMMENT_RE = re.compile(
    r"^\s*(//|#(?![\[!]|(?:include|define|undef|pragma|if|ifdef|ifndef|elif|else|endif"
    r"|error|import)\b)|/\*|\*|--|<!--)"
)
_TRIVIAL_LINE_RE = re.compile(
    r"^\s*($|//|#|/\*|\*|--|<!--|import\b|from\s+\S+\s+import\b|package\b|use\b"
    r"|\"[^\"]*\"\s*$|'[^']*'\s*$|[{}()\[\];,]+\s*$|\}?\s*else\s*\{?\s*$)"
)


@dataclass
class Hunk:
    old_start: int
    old_count: int
    new_start: int
    new_count: int
    heading: str
    lines: list[str] = field(default_factory=list)

    def header(self) -> str:
        return (
            f"@@ -{self.old_start},{self.old_count} +{self.new_start},{self.new_count} @@"
            f"{self.heading}"
        )


@dataclass
class FileDiff:
    old_path: str | None
    new_path: str | None
    hunks: list[Hunk] = field(default_factory=list)

    @property
    def path(self) -> str:
        return self.new_path or self.old_path or ""


@dataclass
class Candidate:
    file: str
    line_start: int
    line_end: int
    kind: str  # "added", "deletion-only" or "unanchored"
    added: list[str]
    removed: list[str]

    @property
    def shown(self) -> list[str]:
        return self.added if self.added else self.removed


@dataclass
class Report:
    case_id: str
    title: str
    source: dict
    mode: str
    category: str
    reasons: list[str]
    kept: list[FileDiff]
    dropped: list[tuple[str, str]]
    seeded: list[Candidate]
    skipped_trivial: list[Candidate]
    dropped_absence: list[Candidate]
    stripped_comments: int
    diff_text: str
    max_lines: int
    verdict: str


# ------------------------------------------------------------------ parsing


def _path_of(raw: str) -> str | None:
    raw = raw.split("\t", 1)[0].strip()
    if raw == "/dev/null":
        return None
    if raw.startswith(("a/", "b/")):
        raw = raw[2:]
    return raw


def parse_git_diff(text: str) -> list[FileDiff]:
    """Parse `git diff` / `gh pr diff` output. Hunk bodies are delimited by their line
    counts, so a removed line that happens to start with '---' cannot be mistaken for a
    file header."""
    files: list[FileDiff] = []
    current: FileDiff | None = None
    hunk: Hunk | None = None
    remaining_old = remaining_new = 0

    for line in text.splitlines():
        if hunk is not None and (remaining_old > 0 or remaining_new > 0):
            tag = line[:1]
            if tag == "\\":
                hunk.lines.append(line)
                continue
            if line == "":
                line, tag = " ", " "  # some tools strip the space on blank context lines
            if tag == " ":
                remaining_old -= 1
                remaining_new -= 1
            elif tag == "-":
                remaining_old -= 1
            elif tag == "+":
                remaining_new -= 1
            else:
                raise ValueError(f"malformed hunk body line: {line!r}")
            hunk.lines.append(line)
            continue

        if hunk is not None and line.startswith("\\"):
            hunk.lines.append(line)
            continue
        hunk = None

        if line.startswith("diff --git "):
            current = FileDiff(None, None)
            files.append(current)
            continue
        if line.startswith("--- "):
            if current is None or current.old_path is not None or current.new_path is not None:
                current = FileDiff(None, None)
                files.append(current)
            current.old_path = _path_of(line[4:])
            continue
        if line.startswith("+++ ") and current is not None:
            current.new_path = _path_of(line[4:])
            continue
        match = _HUNK_RE.match(line)
        if match and current is not None:
            hunk = Hunk(
                int(match[1]),
                int(match[2]) if match[2] is not None else 1,
                int(match[3]),
                int(match[4]) if match[4] is not None else 1,
                match[5],
            )
            current.hunks.append(hunk)
            remaining_old, remaining_new = hunk.old_count, hunk.new_count
        # index / mode / similarity / binary lines are ignored

    return [file for file in files if file.hunks]


# ---------------------------------------------------------------- reversing


def _reverse_lines(lines: Sequence[str]) -> list[str]:
    """Swap +/- and reorder each change block so removed lines precede added lines."""
    result: list[str] = []
    minus: list[str] = []
    plus: list[str] = []
    last = result

    def flush() -> None:
        result.extend(minus)
        result.extend(plus)
        minus.clear()
        plus.clear()

    for line in lines:
        tag = line[:1]
        if tag == "\\":
            last.append(line)
        elif tag == " ":
            flush()
            result.append(line)
            last = result
        elif tag == "+":
            minus.append("-" + line[1:])
            last = minus
        elif tag == "-":
            plus.append("+" + line[1:])
            last = plus
    flush()
    return result


def reverse(file: FileDiff) -> FileDiff:
    out = FileDiff(old_path=file.new_path, new_path=file.old_path)
    for hunk in file.hunks:
        reversed_hunk = Hunk(
            hunk.new_start, hunk.new_count, hunk.old_start, hunk.old_count, hunk.heading
        )
        reversed_hunk.lines = _reverse_lines(hunk.lines)
        out.hunks.append(reversed_hunk)
    return out


def strip_removed_comments(file: FileDiff) -> int:
    """Drop removed lines that are comments. In a reversed fix those are the fix's own
    explanation of the defect, which is the most common way the answer leaks. The old-side
    count is adjusted so the hunk stays valid. Returns the number of lines dropped."""
    dropped = 0
    for hunk in file.hunks:
        kept: list[str] = []
        skip_marker = False
        for line in hunk.lines:
            if skip_marker and line.startswith("\\"):
                skip_marker = False
                continue
            skip_marker = False
            if line.startswith("-") and _COMMENT_RE.match(line[1:]):
                dropped += 1
                hunk.old_count -= 1
                skip_marker = True
                continue
            kept.append(line)
        hunk.lines = kept
    return dropped


def additive(file: FileDiff) -> FileDiff:
    """Present the new side of every hunk as freshly added code: no removed lines, the file
    appears to be created. Line numbers on the new side are unchanged."""
    out = FileDiff(old_path=None, new_path=file.new_path)
    for hunk in file.hunks:
        lines = ["+" + line[1:] for line in hunk.lines if line[:1] in (" ", "+")]
        out.hunks.append(Hunk(0, 0, hunk.new_start, hunk.new_count, hunk.heading, lines))
    return out


def render_diff(files: Sequence[FileDiff]) -> str:
    out: list[str] = []
    for file in files:
        out.append(f"--- {'a/' + file.old_path if file.old_path else '/dev/null'}")
        out.append(f"+++ {'b/' + file.new_path if file.new_path else '/dev/null'}")
        for hunk in file.hunks:
            out.append(hunk.header())
            out.extend(hunk.lines)
    return "\n".join(out) + "\n"


# --------------------------------------------------------------- candidates


def candidates(file: FileDiff) -> list[Candidate]:
    """One candidate per change block of a reversed file diff. Blocks with added lines seed
    those lines. Blocks that only remove lines (the fix had only added code, so the bug is an
    absence) are anchored at the following context line and flagged for the human."""
    found: list[Candidate] = []
    for hunk in file.hunks:
        new_line = hunk.new_start
        minus: list[str] = []
        plus: list[str] = []
        first_plus: int | None = None

        def flush(anchor: int, hunk: Hunk = hunk) -> None:
            nonlocal minus, plus, first_plus
            if plus and first_plus is not None:
                found.append(
                    Candidate(
                        file.path, first_plus, first_plus + len(plus) - 1, "added", plus, minus
                    )
                )
            elif minus:
                kind = "deletion-only" if hunk.new_count > 0 else "unanchored"
                found.append(Candidate(file.path, anchor, anchor, kind, [], minus))
            minus, plus, first_plus = [], [], None

        for line in hunk.lines:
            tag = line[:1]
            if tag == "\\":
                continue
            if tag == " ":
                flush(anchor=new_line)
                new_line += 1
            elif tag == "-":
                minus.append(line[1:])
            elif tag == "+":
                if first_plus is None:
                    first_plus = new_line
                plus.append(line[1:])
                new_line += 1
        flush(anchor=max(hunk.new_start, new_line - 1))
    return found


def is_trivial(candidate: Candidate) -> bool:
    """Imports, comments, blank lines and bare braces cannot carry a seeded bug."""
    return all(_TRIVIAL_LINE_RE.match(line) for line in candidate.shown)


# ------------------------------------------------------------ heuristics


def is_test_path(path: str) -> bool:
    return any(re.search(pattern, path, re.IGNORECASE) for pattern in TEST_PATTERNS)


def is_noise_path(path: str) -> bool:
    return any(re.search(pattern, path) for pattern in NOISE_PATTERNS)


def guess_category(title: str, body: str, labels: Sequence[str]) -> tuple[str, list[str]]:
    text = " ".join([title, body[:3000], " ".join(labels)]).lower()
    security_hits = [word for word in SECURITY_WORDS if word in text]
    if any(word in text for word in PAYMENT_WORDS):
        security_hits = [word for word in security_hits if word not in PAYMENT_FALSE_POSITIVES]
    if security_hits:
        return "security", security_hits
    style_hits = [word for word in STYLE_WORDS if word in text]
    behavior_hits = [word for word in BEHAVIOR_WORDS if word in text]
    if style_hits and not behavior_hits:
        return "style", style_hits
    return "logic", behavior_hits or ["default"]


def clean_title(title: str) -> str:
    text = re.sub(r"^\s*(\[[^\]]*\]\s*)+", "", title)
    text = re.sub(r"^\s*[A-Z][A-Z0-9]+-\d+\s*[:\-]\s*", "", text)
    text = re.sub(r"^\s*(bug|fix|feature|chore|hotfix)\s*[:\-]\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^\s*fix(?:es|ed)?\s+", "", text, flags=re.IGNORECASE)
    return text.strip().rstrip(".")


def leak_hits(diff_text: str) -> list[tuple[int, str]]:
    hits: list[tuple[int, str]] = []
    for number, line in enumerate(diff_text.splitlines(), start=1):
        if line.startswith(("---", "+++", "@@")):
            continue
        if _LEAK_RE.search(line) or _TICKET_RE.search(line):
            hits.append((number, line.strip()[:120]))
    return hits


# ----------------------------------------------------------------- inputs


def _gh(*args: str) -> str:
    """Run the gh CLI and return stdout. gh always emits UTF-8; decoding with the platform
    locale (cp1252 on Windows) makes subprocess's reader thread die on the first curly quote
    or emoji in a PR body and hand back stdout=None, so the encoding is pinned."""
    gh = shutil.which("gh") or r"C:\Program Files\GitHub CLI\gh.exe"
    completed = subprocess.run(
        [gh, *args],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    return completed.stdout


def fetch_pr(url: str) -> tuple[dict, str]:
    view = _gh("pr", "view", url, "--json", "title,body,labels,files")
    diff = _gh("pr", "diff", url)
    return json.loads(view), diff


def select_files(
    files: Sequence[FileDiff],
    *,
    keep_tests: bool,
    keep_new_files: bool,
    only: Sequence[str],
) -> tuple[list[FileDiff], list[tuple[str, str]]]:
    kept: list[FileDiff] = []
    dropped: list[tuple[str, str]] = []
    for file in files:
        path = file.path
        if only and not any(fragment in path for fragment in only):
            dropped.append((path, "not in --files"))
        elif file.old_path is None and not keep_new_files:
            dropped.append((path, "created by the fix; reversed it is a whole-file deletion"))
        elif file.new_path is None:
            dropped.append((path, "deleted by the fix; reversed it re-adds a whole file"))
        elif not keep_tests and is_test_path(path):
            dropped.append((path, "test or mock; would leak the answer"))
        elif is_noise_path(path):
            dropped.append((path, "docs, generated or manual script"))
        else:
            kept.append(file)
    return kept, dropped


# ----------------------------------------------------------------- output


def build_draft(
    case_id: str,
    files: Sequence[FileDiff],
    seeded_candidates: Sequence[Candidate],
    category: str,
    title: str,
    source: dict,
) -> dict:
    description_base = clean_title(title) or title
    seeded = []
    for index, candidate in enumerate(seeded_candidates, start=1):
        seeded.append(
            {
                "id": f"{case_id}-b{index}",
                "file": candidate.file,
                "line_start": candidate.line_start,
                "line_end": candidate.line_end,
                "category": category,
                "description": (
                    f"{description_base}; defect reintroduced by reversing the fix at "
                    f"{candidate.file}:{candidate.line_start}-{candidate.line_end}. "
                    "REVIEW: rewrite as what is wrong, not what was fixed."
                ),
            }
        )
    return {"id": case_id, "source": source, "diff": render_diff(files), "seeded": seeded}


def _candidate_block(candidate: Candidate) -> list[str]:
    lines = ["```diff"]
    lines += [f"-{text}" for text in candidate.removed]
    lines += [f"+{text}" for text in candidate.added]
    lines.append("```")
    return lines


def review_sheet(report: Report) -> str:
    lines = [
        f"# Draft {report.case_id}",
        "",
        f"PR: {report.title}",
        f"Source: {json.dumps(report.source)}",
        f"Mode: {report.mode}",
        f"Category guess: **{report.category}** ({', '.join(report.reasons)}); confirm or override",
        f"Validator: {report.verdict}",
        "",
        "## Files",
        "",
    ]
    for file in report.kept:
        lines.append(f"- kept `{file.path}` ({len(file.hunks)} hunks)")
    for path, reason in report.dropped:
        lines.append(f"- dropped `{path}`: {reason}")
    size = report.diff_text.count("\n")
    lines += [
        "",
        f"Size: {size} diff lines"
        + (f" (over {report.max_lines}, consider --files)" if size > report.max_lines else ""),
        f"Stripped removed comment lines: {report.stripped_comments}",
    ]

    hits = leak_hits(report.diff_text)
    lines += ["", f"## Leak check: {len(hits)} hit(s)", ""]
    for number, text in hits:
        lines.append(f"- diff line {number}: `{text}`")
    if not hits:
        lines.append("- none")

    lines += ["", f"## Seeded candidates: {len(report.seeded)}", ""]
    for index, candidate in enumerate(report.seeded, start=1):
        lines.append(
            f"### {report.case_id}-b{index}: `{candidate.file}` lines "
            f"{candidate.line_start}-{candidate.line_end} ({candidate.kind})"
        )
        if candidate.kind == "deletion-only":
            lines.append(
                "The fix only added code, so the bug is an absence. Anchored at the next "
                "context line; confirm or move it."
            )
        if candidate.kind == "unanchored":
            lines.append(
                "The reversed hunk has no new-side lines; the validator will reject this "
                "range. Move the bug to a neighbouring hunk or drop it."
            )
        lines += ["", *_candidate_block(candidate), ""]

    if report.skipped_trivial:
        lines += [
            (
                f"## Skipped trivial candidates: {len(report.skipped_trivial)} "
                "(imports, comments, braces; --keep-trivial to include)"
            ),
            "",
        ]
        for candidate in report.skipped_trivial:
            lines.append(
                f"- `{candidate.file}` lines {candidate.line_start}-{candidate.line_end} "
                f"({candidate.kind}): `{(candidate.shown or [''])[0].strip()[:80]}`"
            )
        lines.append("")

    if report.dropped_absence:
        lines += [
            f"## Dropped in additive mode: {len(report.dropped_absence)} absence bug(s)",
            "",
            (
                "Additive diffs have no removed lines, so a bug that is missing code has "
                "nothing to point at. Use reverse mode for these."
            ),
            "",
        ]
        for candidate in report.dropped_absence:
            lines.append(f"- `{candidate.file}` line {candidate.line_start}")
            lines += _candidate_block(candidate)
        lines.append("")
    return "\n".join(lines) + "\n"


def build(
    view: dict,
    diff_text: str,
    *,
    case_id: str,
    source: dict,
    mode: str = "reverse",
    keep_tests: bool = False,
    keep_new_files: bool = False,
    keep_removed_comments: bool = False,
    keep_trivial: bool = False,
    only: Sequence[str] = (),
    category: str | None = None,
    max_lines: int = 200,
) -> tuple[dict, Report]:
    """The mechanical part without touching the filesystem: the draft case as a JSON-ready
    dict plus the report behind the review sheet. `run` writes both; batch tools gate on the
    report first and decide what to write."""
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}, got {mode!r}")
    title = str(view.get("title", ""))
    body = str(view.get("body", "") or "")
    labels = [str(label.get("name", "")) for label in view.get("labels", []) or []]

    parsed = parse_git_diff(diff_text)
    kept, dropped = select_files(
        parsed, keep_tests=keep_tests, keep_new_files=keep_new_files, only=only
    )
    reversed_files = [reverse(file) for file in kept]
    stripped = 0
    if not keep_removed_comments:
        stripped = sum(strip_removed_comments(file) for file in reversed_files)

    found = [candidate for file in reversed_files for candidate in candidates(file)]
    skipped_trivial = [] if keep_trivial else [c for c in found if is_trivial(c)]
    seeded = [c for c in found if c not in skipped_trivial]
    dropped_absence: list[Candidate] = []
    if mode == "additive":
        dropped_absence = [c for c in seeded if c.kind != "added"]
        seeded = [c for c in seeded if c.kind == "added"]
    output_files = (
        [additive(file) for file in reversed_files] if mode == "additive" else reversed_files
    )

    guessed, reasons = guess_category(title, body, labels)
    if category is not None:
        guessed, reasons = category, ["--category override"]

    draft = build_draft(case_id, output_files, seeded, guessed, title, source)
    try:
        load_case_dict(draft, case_id)
        verdict = "OK"
    except ValueError as exc:
        verdict = f"REJECTED: {exc}"

    report = Report(
        case_id=case_id,
        title=title,
        source=source,
        mode=mode,
        category=guessed,
        reasons=reasons,
        kept=reversed_files,
        dropped=dropped,
        seeded=seeded,
        skipped_trivial=skipped_trivial,
        dropped_absence=dropped_absence,
        stripped_comments=stripped,
        diff_text=draft["diff"],
        max_lines=max_lines,
        verdict=verdict,
    )
    return draft, report


def run(
    view: dict,
    diff_text: str,
    *,
    case_id: str,
    out_dir: Path,
    source: dict,
    mode: str = "reverse",
    keep_tests: bool = False,
    keep_new_files: bool = False,
    keep_removed_comments: bool = False,
    keep_trivial: bool = False,
    only: Sequence[str] = (),
    category: str | None = None,
    max_lines: int = 200,
) -> tuple[Path, Path, str]:
    """`build`, then write the draft JSON and its review sheet under out_dir."""
    draft, report = build(
        view,
        diff_text,
        case_id=case_id,
        source=source,
        mode=mode,
        keep_tests=keep_tests,
        keep_new_files=keep_new_files,
        keep_removed_comments=keep_removed_comments,
        keep_trivial=keep_trivial,
        only=only,
        category=category,
        max_lines=max_lines,
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"{case_id}.json"
    json_path.write_text(json.dumps(draft, indent=2) + "\n", encoding="utf-8")
    review_path = out_dir / f"{case_id}.review.md"
    review_path.write_text(review_sheet(report), encoding="utf-8")
    return json_path, review_path, report.verdict


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pr_to_case", description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--pr", help="pull request URL (uses the gh CLI)")
    source.add_argument("--view", help="saved `gh pr view --json title,body,labels,files`")
    parser.add_argument("--diff", help="saved `gh pr diff` output (required with --view)")
    parser.add_argument("--id", required=True, help="case id, also the output filename stem")
    parser.add_argument("--out", default="drafts", help="output directory for drafts")
    parser.add_argument("--mode", choices=MODES, default="reverse")
    parser.add_argument("--keep-tests", action="store_true")
    parser.add_argument("--keep-new-files", action="store_true")
    parser.add_argument("--keep-removed-comments", action="store_true")
    parser.add_argument("--keep-trivial", action="store_true")
    parser.add_argument("--files", nargs="*", default=(), help="keep only paths containing these")
    parser.add_argument("--category", choices=CATEGORIES, default=None)
    parser.add_argument("--max-lines", type=int, default=200)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.pr:
        view, diff_text = fetch_pr(args.pr)
        match = _PR_URL_RE.search(args.pr)
        source = {"pr": args.pr}
        if match:
            source.update({"repo": f"{match[1]}/{match[2]}", "number": int(match[3])})
    else:
        if not args.diff:
            print("--diff is required with --view", file=sys.stderr)
            return 2
        view = json.loads(Path(args.view).read_text(encoding="utf-8"))
        diff_text = Path(args.diff).read_text(encoding="utf-8")
        source = {"view": Path(args.view).name, "diff": Path(args.diff).name}

    json_path, review_path, verdict = run(
        view,
        diff_text,
        case_id=args.id,
        out_dir=Path(args.out),
        source=source,
        mode=args.mode,
        keep_tests=args.keep_tests,
        keep_new_files=args.keep_new_files,
        keep_removed_comments=args.keep_removed_comments,
        keep_trivial=args.keep_trivial,
        only=args.files,
        category=args.category,
        max_lines=args.max_lines,
    )
    print(f"{args.id}: {verdict}; wrote {json_path} and {review_path}")
    return 0 if verdict == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
