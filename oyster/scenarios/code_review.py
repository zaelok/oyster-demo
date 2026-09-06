"""Code review as a scenario: the pieces the first build wrote directly, gathered behind the
protocol without moving them. Task = CorpusCase, expected = SeededBug, output = Finding."""

from collections.abc import Hashable, Sequence
from pathlib import Path as FsPath

from oyster.corpus import load_cases
from oyster.executor import keep_known, parse_findings
from oyster.graph.catalog import CATALOG
from oyster.matching import match
from oyster.prompts import render_messages
from oyster.prompts.templates import TEMPLATES
from oyster.types import CorpusCase, Finding, MatchReport, Path


class CodeReviewScenario:
    name = "code-review"

    def load_tasks(self, directory: FsPath) -> tuple[CorpusCase, ...]:
        return load_cases(directory)

    def prompt_keys(self) -> frozenset[str]:
        return frozenset(TEMPLATES)

    def catalog(self) -> tuple[Path, ...]:
        return CATALOG

    def render_messages(
        self, prompt_key: str, task: CorpusCase, upstream: Sequence[Finding]
    ) -> tuple[str, str, str]:
        return render_messages(prompt_key, task.diff, upstream)

    def parse_output(self, text: str) -> tuple[Finding, ...] | None:
        return parse_findings(text)

    def keep(self, outputs: Sequence[Finding], task: CorpusCase) -> tuple[Finding, ...]:
        return keep_known(outputs, task.diff)

    def dedup_key(self, output: Finding) -> Hashable:
        return (output.file, output.line_start, output.line_end, output.category)

    def sort_key(self, output: Finding) -> tuple[str, int]:
        return (output.file, output.line_start)

    def expected(self, task: CorpusCase) -> tuple[tuple[str, str], ...]:
        return tuple((bug.id, bug.category) for bug in task.seeded)

    def score(self, outputs: Sequence[Finding], task: CorpusCase, path_id: str) -> MatchReport:
        return match(outputs, task.seeded, task.id, path_id)


CODE_REVIEW = CodeReviewScenario()
