"""Bug fixing as a scenario: the genericity test for the engine.

Task: a repository at a buggy commit, the failing tests, the reference fix. Output: a patch.
Scorer: deterministic when a test runner is available (strict = every test passes, loose =
the target tests pass); structural otherwise (strict = the patch touches exactly the files the
reference fix touched, loose = it touches at least one of them; false positives = files touched
that the reference did not). The review corpus is the fixing corpus for free: each reversed
PR's original fix is the reference patch and its tests are the oracle.

Nothing in the engine changes. Flows, executor, selector, calibration and rendering are the
same code that produced the review table; this module supplies the five scenario pieces.
"""

import json
import re
import subprocess
from collections.abc import Callable, Hashable, Sequence
from dataclasses import dataclass
from pathlib import Path as FsPath

from oyster.executor import diff_files
from oyster.types import Edge, MatchReport, Node, Path

OUTPUT_CONTRACT = """
Respond with a unified diff only, inside a ```diff fence, that applies to the repository at
the stated commit. Touch only the files the fix needs. Do not include prose outside the fence.
"""

PATCHER = (
    """You are fixing a defect. The repository, commit, failing tests and what is wrong are
given in the context. Produce the smallest patch that makes the failing tests pass without
breaking other tests.
{upstream_block}
"""
    + OUTPUT_CONTRACT
)

UPSTREAM_BLOCK = """
An earlier attempt produced this patch. Keep what is right, fix what is not, or replace it.

EARLIER PATCH:
{upstream_patch}
"""

TEMPLATES: dict[str, str] = {"patcher": PATCHER}

PATH_F1 = Path(
    id="F1",
    description="single patch attempt: patcher(strong-model)",
    nodes=(Node("f1", "patcher", "strong-model", "patcher"),),
    edges=(),
)
PATH_F2 = Path(
    id="F2",
    description="cascade: patcher(cheap-model) -> patcher(strong-model) with the first patch as a hint",
    nodes=(
        Node("f1", "patcher", "cheap-model", "patcher"),
        Node("f2", "patcher", "strong-model", "patcher"),
    ),
    edges=(Edge("f1", "f2"),),
)
CATALOG_FIX: tuple[Path, ...] = (PATH_F1, PATH_F2)

_FENCE = re.compile(r"```(?:diff|patch)?\s*\n(.*?)```", re.DOTALL)


@dataclass(frozen=True)
class FixTask:
    id: str
    repo: str
    base_commit: str
    failing_tests: tuple[str, ...]
    reference_patch: str
    description: str
    test_command: str = ""

    @property
    def context(self) -> str:
        tests = "\n".join(f"- {test}" for test in self.failing_tests) or "- (none listed)"
        return (
            f"REPOSITORY: {self.repo}\nCOMMIT: {self.base_commit}\n"
            f"FAILING TESTS:\n{tests}\nWHAT IS WRONG:\n{self.description}\n"
        )


@dataclass(frozen=True)
class Patch:
    text: str
    files: tuple[str, ...]


@dataclass(frozen=True)
class RunOutcome:
    target_passed: bool
    all_passed: bool
    detail: str = ""


TestRunner = Callable[[FixTask, Patch], RunOutcome]


def parse_patch(text: str) -> tuple[Patch, ...] | None:
    body = None
    fenced = _FENCE.search(text or "")
    if fenced:
        body = fenced.group(1)
    else:
        stripped = (text or "").strip()
        if stripped.startswith(("--- ", "diff --git ")):
            body = stripped
    if body is None:
        return None
    body = body.strip("\n") + "\n"
    files = tuple(sorted(diff_files(body)))
    if not files:
        return None
    return (Patch(body, files),)


def load_fix_tasks(directory: FsPath) -> tuple[FixTask, ...]:
    tasks = []
    for path in sorted(FsPath(directory).glob("*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        task = FixTask(
            id=str(raw["id"]),
            repo=str(raw["repo"]),
            base_commit=str(raw["base_commit"]),
            failing_tests=tuple(str(t) for t in raw.get("failing_tests", [])),
            reference_patch=str(raw["reference_patch"]),
            description=str(raw.get("description", "")),
            test_command=str(raw.get("test_command", "")),
        )
        if task.id != path.stem:
            raise ValueError(f"task {task.id!r}: field 'id' does not match filename stem")
        if not diff_files(task.reference_patch):
            raise ValueError(f"task {task.id!r}: field 'reference_patch' names no files")
        tasks.append(task)
    return tuple(sorted(tasks, key=lambda task: task.id))


class SubprocessRunner:
    """Applies the patch in a checkout and runs the task's test command. Strict means the
    command exits 0; the target tests are assumed covered by the same command. Provided for
    real use; tests use a fake."""

    def __init__(self, checkout_for: Callable[[FixTask], FsPath]):
        self.checkout_for = checkout_for

    def __call__(self, task: FixTask, patch: Patch) -> RunOutcome:
        workdir = self.checkout_for(task)
        apply = subprocess.run(
            ["git", "apply", "--check", "-"],
            input=patch.text,
            cwd=workdir,
            capture_output=True,
            encoding="utf-8",
            check=False,
        )
        if apply.returncode != 0:
            return RunOutcome(False, False, f"patch does not apply: {apply.stderr.strip()[:200]}")
        subprocess.run(
            ["git", "apply", "-"],
            input=patch.text,
            cwd=workdir,
            capture_output=True,
            encoding="utf-8",
            check=True,
        )
        try:
            run = subprocess.run(
                task.test_command,
                shell=True,
                cwd=workdir,
                capture_output=True,
                encoding="utf-8",
                check=False,
            )
        finally:
            subprocess.run(["git", "checkout", "--", "."], cwd=workdir, check=False)
        passed = run.returncode == 0
        return RunOutcome(passed, passed, run.stdout[-500:])


class BugFixingScenario:
    name = "bug-fixing"

    def __init__(self, runner: TestRunner | None = None):
        self.runner = runner

    def load_tasks(self, directory: FsPath) -> tuple[FixTask, ...]:
        return load_fix_tasks(directory)

    def prompt_keys(self) -> frozenset[str]:
        return frozenset(TEMPLATES)

    def catalog(self) -> tuple[Path, ...]:
        return CATALOG_FIX

    def render_messages(
        self, prompt_key: str, task: FixTask, upstream: Sequence[Patch]
    ) -> tuple[str, str, str]:
        block = ""
        if upstream:
            block = UPSTREAM_BLOCK.replace("{upstream_patch}", upstream[-1].text)
        user = TEMPLATES[prompt_key].replace("{upstream_block}", block)
        return "", user, task.context

    def parse_output(self, text: str) -> tuple[Patch, ...] | None:
        return parse_patch(text)

    def keep(self, outputs: Sequence[Patch], task: FixTask) -> tuple[Patch, ...]:
        del task
        return tuple(patch for patch in outputs if patch.files)

    def dedup_key(self, output: Patch) -> Hashable:
        return output.text

    def sort_key(self, output: Patch) -> str:
        return output.files[0] if output.files else ""

    def expected(self, task: FixTask) -> tuple[tuple[str, str], ...]:
        return ((task.id, "fix"),)

    def score(self, outputs: Sequence[Patch], task: FixTask, path_id: str) -> MatchReport:
        if not outputs:
            return MatchReport(task.id, path_id, (), (), (task.id,), 0)
        patch = outputs[-1]
        reference_files = set(diff_files(task.reference_patch))
        touched = set(patch.files)
        false_positives = len(touched - reference_files)
        if self.runner is not None:
            outcome = self.runner(task, patch)
            strict, loose = outcome.all_passed, outcome.target_passed
        else:
            loose = bool(touched & reference_files)
            strict = touched == reference_files
        caught_strict = (task.id,) if strict else ()
        caught_loose = (task.id,) if loose or strict else ()
        missed = () if caught_loose else (task.id,)
        return MatchReport(task.id, path_id, caught_strict, caught_loose, missed, false_positives)


BUG_FIXING = BugFixingScenario()
