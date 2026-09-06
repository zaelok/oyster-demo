"""The scenario plugin: everything the engine must not know about a task.

The engine (graph, cost, executor, selector, evaluation, providers, conversation) runs any
skill whose task, expected label, output and scorer are supplied through this protocol. Code
review is the first scenario (`oyster.scenarios.code_review`); bug fixing is the second and
the test that the abstraction holds (`oyster.scenarios.bug_fixing`).

Tasks and outputs are opaque to the engine, so they are typed `Any` here. Each scenario owns
its own frozen dataclasses for them; `oyster/types.py` stays frozen.
"""

from collections.abc import Hashable, Sequence
from pathlib import Path as FsPath
from typing import Any, Protocol

from oyster.types import MatchReport, Path


class Scenario(Protocol):
    name: str

    def load_tasks(self, directory: FsPath) -> tuple[Any, ...]:
        """Validated tasks from a directory, sorted by id."""
        ...

    def prompt_keys(self) -> frozenset[str]:
        """The prompt keys nodes of this scenario may name; validate_path checks them."""
        ...

    def catalog(self) -> tuple[Path, ...]:
        """Candidate flows for this scenario."""
        ...

    def render_messages(
        self, prompt_key: str, task: Any, upstream: Sequence[Any]
    ) -> tuple[str, str, str]:
        """(system, user, cached_prefix) for one node call."""
        ...

    def parse_output(self, text: str) -> tuple[Any, ...] | None:
        """Outputs from a reply; None means unparseable (the executor retries once)."""
        ...

    def keep(self, outputs: Sequence[Any], task: Any) -> tuple[Any, ...]:
        """Drop outputs that cannot be valid for this task (a hallucinated file path)."""
        ...

    def dedup_key(self, output: Any) -> Hashable:
        """Identity of an output when upstream outputs are merged."""
        ...

    def sort_key(self, output: Any) -> Any:
        """Order of merged upstream outputs in a downstream prompt."""
        ...

    def expected(self, task: Any) -> tuple[tuple[str, str], ...]:
        """(expected id, category) for every label the scorer can catch; calibration counts
        catch rates per category from these."""
        ...

    def score(self, outputs: Sequence[Any], task: Any, path_id: str) -> MatchReport:
        """Outputs against the task's expected labels, strict and loose, with false positives."""
        ...
