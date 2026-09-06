"""Frozen contracts. Every module imports from here. Nothing here changes without a
coordinated re-dispatch of dependent tasks."""

from dataclasses import dataclass, field
from typing import Literal, Protocol

Category = Literal["logic", "security", "style"]
CATEGORIES: tuple[Category, ...] = ("logic", "security", "style")


@dataclass(frozen=True)
class Cost:
    dollars: float
    latency_s: float

    def __add__(self, other: "Cost") -> "Cost":
        return Cost(self.dollars + other.dollars, self.latency_s + other.latency_s)

    @staticmethod
    def zero() -> "Cost":
        return Cost(0.0, 0.0)


@dataclass(frozen=True)
class ModelBinding:
    alias: str  # "cheap-model" | "strong-model"
    model_id: str
    rate_in: float  # dollars per 1M input tokens
    rate_out: float  # dollars per 1M output tokens
    cache_discount: float  # 0.0-1.0, fraction of rate_in waived on cached prefix tokens


@dataclass(frozen=True)
class Node:
    id: str  # unique within a Path
    role: str  # "cheap-scanner" | "deep-reviewer" | "critic"
    model_alias: str
    prompt_key: str  # key into oyster.prompts.templates.TEMPLATES


@dataclass(frozen=True)
class Edge:
    src: str
    dst: str
    carries: Literal["findings"] = "findings"


@dataclass(frozen=True)
class Path:
    id: str
    description: str
    nodes: tuple[Node, ...]  # topologically ordered
    edges: tuple[Edge, ...]


@dataclass(frozen=True)
class Finding:
    file: str
    line_start: int
    line_end: int
    category: Category
    description: str
    confidence: float


@dataclass(frozen=True)
class SeededBug:
    id: str
    file: str
    line_start: int
    line_end: int
    category: Category
    description: str


@dataclass(frozen=True)
class CorpusCase:
    id: str
    diff: str
    seeded: tuple[SeededBug, ...]


@dataclass(frozen=True)
class Completion:
    text: str
    input_tokens: int
    cached_input_tokens: int
    output_tokens: int
    latency_s: float
    model_id: str


@dataclass(frozen=True)
class NodeResult:
    node_id: str
    role: str
    findings: tuple[Finding, ...]
    completion: Completion
    cost: Cost
    parse_failed: bool = False


@dataclass(frozen=True)
class PathResult:
    path_id: str
    case_id: str
    node_results: tuple[NodeResult, ...]
    findings: tuple[Finding, ...]
    cost: Cost
    halted_reason: str | None = None


@dataclass(frozen=True)
class MatchReport:
    case_id: str
    path_id: str
    caught_strict: tuple[str, ...]
    caught_loose: tuple[str, ...]
    missed: tuple[str, ...]
    false_positives: int


@dataclass(frozen=True)
class QualityEstimate:
    """v2 addition (2026-09-06): a catch rate with the evidence behind it. ci is a Wilson
    95% interval on n seeded bugs of that category."""

    rate: float
    n: int
    ci_low: float
    ci_high: float


@dataclass(frozen=True)
class CostProfile:
    """v2 addition (2026-09-06): cost as a distribution over n calibration cases, nearest-rank
    percentiles. Latency tolerance is an SLO, so the selector checks it at p95."""

    dollars_p50: float
    dollars_p95: float
    latency_p50: float
    latency_p95: float
    n: int


@dataclass(frozen=True)
class Priors:
    """Calibrated quality priors. key is (role, model_alias, category).

    v2 addition (2026-09-06): `quality` and `cost` carry the same keys as `catch_rate` and
    `mean_cost` with sample sizes, intervals and percentiles. Both default to empty so every
    v1 call site keeps working; the spec froze this file for the first build and these fields
    are additive."""

    catch_rate: dict[tuple[str, str, str], float]
    mean_cost: dict[tuple[str, str], Cost]  # (role, model_alias)
    corpus_size: int
    quality: dict[tuple[str, str, str], QualityEstimate] = field(default_factory=dict)
    cost: dict[tuple[str, str], CostProfile] = field(default_factory=dict)


@dataclass(frozen=True)
class Selection:
    path_id: str | None
    predicted_quality: float
    predicted_cost: Cost
    rejected: tuple[tuple[str, str], ...]  # (path_id, reason)
    no_feasible_reason: str | None = None
    cheapest_infeasible: tuple[str, Cost] | None = None


class ModelProvider(Protocol):
    def complete(
        self,
        model_id: str,
        system: str,
        user: str,
        cached_prefix: str | None = None,
    ) -> Completion: ...


class Hook(Protocol):
    def before_node(self, node: Node, spent: Cost, budget: Cost) -> str | None:
        """Return a halt reason string to stop the run, or None to continue."""
