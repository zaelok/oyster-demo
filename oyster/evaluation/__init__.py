"""Calibration, evaluation and the results table.

Calibration runs each single node config in isolation over the corpus and measures
P(catch | category) and mean cost per config. Those are the priors the selector ranks with:
measured on this corpus, not learned on someone else's (architecture §1.4).

Evaluation runs each full path over every case. render_results turns the retained
PathResults and MatchReports into results.md; every number in the table is traceable to
one of them, and results_to_json retains them all.
"""

import json
import statistics
from collections import Counter, defaultdict
from collections.abc import Sequence
from dataclasses import asdict
from datetime import UTC, datetime

from oyster.cost import path_cost
from oyster.executor import run_path
from oyster.graph.catalog import CATALOG
from oyster.matching import match
from oyster.types import (
    CorpusCase,
    Cost,
    Hook,
    MatchReport,
    ModelBinding,
    ModelProvider,
    Node,
    Path,
    PathResult,
    Priors,
)

__all__ = [
    "LIMITATIONS",
    "calibrate",
    "calibration_paths",
    "evaluate",
    "priors_from_json",
    "priors_to_json",
    "render_results",
    "results_to_json",
]

# Verbatim from the OYSTER architecture document (demo-design-doc.md), §3 "What the numbers
# do and don't show" and §4 "Non-Goals (this slice)". Static text, never edited by code.
LIMITATIONS = """\
**What the numbers do and don't show**: catch-rates are corpus-specific; N is small; seeded \
bugs are cleaner than wild bugs. The table supports the *claim* (§0) — that selection over \
measured paths is possible and auditable — not a general benchmark of any model's review \
ability.

### Non-Goals (this slice)

- **Unbounded runtime cycles** (convergence-criterion stopping). A cyclic graph requires a \
termination argument — cost budget as a **variant function**, monotonically decreasing per \
traversal. The DAG slice guarantees finite execution structurally; the variant-function \
treatment for true cycles is designed (vision doc) and is v2.
- **Runtime re-planning** (switching paths mid-run on intermediate results) and **dynamic node \
creation** — not on the MVP critical path; both need evaluation machinery of their own.
- **Learned quality priors** (§1.4 note) and **semantic result caching** — future work, one \
sentence each in the README.
- **Any hosted service.** The deliverable is a reproducible repo, not a deployment.
"""


def calibration_paths(paths: Sequence[Path] = CATALOG) -> tuple[Path, ...]:
    """One single-node Path per distinct (role, model_alias, prompt_key) in the given paths,
    in first-seen order."""
    seen: dict[tuple[str, str, str], Path] = {}
    for path in paths:
        for node in path.nodes:
            key = (node.role, node.model_alias, node.prompt_key)
            if key not in seen:
                seen[key] = Path(
                    id=f"cal:{node.role}:{node.model_alias}",
                    description=f"calibration of {node.role} on {node.model_alias}",
                    nodes=(Node("n1", node.role, node.model_alias, node.prompt_key),),
                    edges=(),
                )
    return tuple(seen.values())


def calibrate(
    cases: Sequence[CorpusCase],
    provider: ModelProvider,
    bindings: dict[str, ModelBinding],
    paths: Sequence[Path] = CATALOG,
) -> Priors:
    """catch_rate[(role, alias, category)] = strict catches of that category / seeded bugs of
    that category, over every case, each node config run alone. Categories with no seeded
    bugs get no entry rather than a fabricated zero. mean_cost is the mean Cost per config."""
    strict: Counter[tuple[str, str, str]] = Counter()
    seeded: Counter[tuple[str, str, str]] = Counter()
    costs: dict[tuple[str, str], list[Cost]] = defaultdict(list)

    for single in calibration_paths(paths):
        node = single.nodes[0]
        config = (node.role, node.model_alias)
        for case in cases:
            result = run_path(single, case, provider, bindings)
            report = match(result.findings, case.seeded, case.id, single.id)
            costs[config].append(result.cost)
            category_of = {bug.id: bug.category for bug in case.seeded}
            for bug in case.seeded:
                seeded[(*config, bug.category)] += 1
            for bug_id in report.caught_strict:
                strict[(*config, category_of[bug_id])] += 1

    catch_rate = {key: strict[key] / count for key, count in seeded.items() if count > 0}
    mean_cost = {
        config: Cost(
            statistics.fmean(cost.dollars for cost in samples),
            statistics.fmean(cost.latency_s for cost in samples),
        )
        for config, samples in costs.items()
        if samples
    }
    return Priors(catch_rate=catch_rate, mean_cost=mean_cost, corpus_size=len(cases))


def evaluate(
    paths: Sequence[Path],
    cases: Sequence[CorpusCase],
    provider: ModelProvider,
    bindings: dict[str, ModelBinding],
    hooks: Sequence[Hook] = (),
) -> tuple[tuple[PathResult, ...], tuple[MatchReport, ...]]:
    """One PathResult and one MatchReport per (path, case), paths outer, cases inner."""
    results: list[PathResult] = []
    reports: list[MatchReport] = []
    for path in paths:
        for case in cases:
            result = run_path(path, case, provider, bindings, hooks)
            results.append(result)
            reports.append(match(result.findings, case.seeded, case.id, path.id))
    return tuple(results), tuple(reports)


def _dollars(value: float) -> str:
    return f"${value:.4f}"


def _per_bug(total_dollars: float, strict_caught: int) -> str:
    """total_dollars / strict_caught, rendered as n/a when nothing was caught strictly. Never
    infinity, never a zero produced by division."""
    if strict_caught == 0:
        return "n/a"
    return _dollars(total_dollars / strict_caught)


def _p50(values: Sequence[float]) -> str:
    if not values:
        return "n/a"
    return f"{statistics.median(values):.2f}s"


def render_results(
    results: Sequence[PathResult],
    reports: Sequence[MatchReport],
    bindings: dict[str, ModelBinding],
    corpus_size: int,
    *,
    provider_name: str = "mock",
    corpus_commit: str = "unknown",
    generated_at: datetime | None = None,
    descriptions: dict[str, str] | None = None,
) -> str:
    """results.md. Every path gets a row, including bad performers. Strict and loose are
    separate columns, never merged."""
    stamp = (generated_at or datetime.now(UTC)).strftime("%Y-%m-%dT%H:%M:%SZ")
    descriptions = descriptions or {path.id: path.description for path in CATALOG}
    reports_by_path: dict[str, list[MatchReport]] = defaultdict(list)
    results_by_path: dict[str, list[PathResult]] = defaultdict(list)
    path_order: list[str] = []
    for result in results:
        if result.path_id not in results_by_path:
            path_order.append(result.path_id)
        results_by_path[result.path_id].append(result)
    for report in reports:
        reports_by_path[report.path_id].append(report)

    seeded_total = 0
    if path_order:
        first = reports_by_path[path_order[0]]
        seeded_total = sum(len(report.caught_loose) + len(report.missed) for report in first)

    lines = [
        "# OYSTER results",
        "",
        f"Generated: {stamp}",
        f"Corpus: {corpus_size} cases, {seeded_total} seeded bugs, corpus commit {corpus_commit}",
    ]
    for index, alias in enumerate(bindings):
        binding = bindings[alias]
        prefix = "Models: " if index == 0 else "        "
        lines.append(
            f"{prefix}{alias}={binding.model_id} "
            f"@ ${binding.rate_in:.2f}/${binding.rate_out:.2f} per 1M"
        )
    lines += [
        f"Provider: {provider_name}",
        "",
        (
            "| path | description | $ total | strict caught | loose caught | seeded | "
            "$/bug (strict) | p50 latency | halted |"
        ),
        (
            "|------|-------------|---------|---------------|--------------|--------|"
            "----------------|-------------|--------|"
        ),
    ]

    for path_id in path_order:
        path_results = results_by_path[path_id]
        path_reports = reports_by_path[path_id]
        total = path_cost([result.cost for result in path_results])
        strict_caught = sum(len(report.caught_strict) for report in path_reports)
        loose_caught = sum(len(report.caught_loose) for report in path_reports)
        seeded = sum(len(report.caught_loose) + len(report.missed) for report in path_reports)
        halted = sum(1 for result in path_results if result.halted_reason is not None)
        lines.append(
            f"| {path_id} | {descriptions.get(path_id, '')} | {_dollars(total.dollars)} | "
            f"{strict_caught} | {loose_caught} | {seeded} | "
            f"{_per_bug(total.dollars, strict_caught)} | "
            f"{_p50([result.cost.latency_s for result in path_results])} | {halted} |"
        )

    lines += ["", "## Per-case detail", ""]
    for path_id in path_order:
        lines += [
            f"### Path {path_id}",
            "",
            (
                "| case | $ | latency | caught (strict) | caught (loose) | missed | "
                "false positives | halted |"
            ),
            (
                "|------|---|---------|-----------------|----------------|--------|"
                "-----------------|--------|"
            ),
        ]
        reports_by_case = {report.case_id: report for report in reports_by_path[path_id]}
        for result in results_by_path[path_id]:
            report = reports_by_case.get(result.case_id)
            strict_ids = ", ".join(report.caught_strict) if report else ""
            loose_ids = ", ".join(report.caught_loose) if report else ""
            missed_ids = ", ".join(report.missed) if report else ""
            false_positives = report.false_positives if report else 0
            lines.append(
                f"| {result.case_id} | {_dollars(result.cost.dollars)} | "
                f"{result.cost.latency_s:.2f}s | {strict_ids or '-'} | {loose_ids or '-'} | "
                f"{missed_ids or '-'} | {false_positives} | {result.halted_reason or '-'} |"
            )
        lines.append("")

    lines += ["## Limitations", "", LIMITATIONS]
    return "\n".join(lines)


def results_to_json(results: Sequence[PathResult], reports: Sequence[MatchReport]) -> str:
    """Every retained PathResult and MatchReport, so each number in results.md is traceable."""
    payload = {
        "results": [asdict(result) for result in results],
        "reports": [asdict(report) for report in reports],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def priors_to_json(priors: Priors) -> str:
    payload = {
        "corpus_size": priors.corpus_size,
        "catch_rate": [
            {"role": role, "model_alias": alias, "category": category, "rate": rate}
            for (role, alias, category), rate in sorted(priors.catch_rate.items())
        ],
        "mean_cost": [
            {
                "role": role,
                "model_alias": alias,
                "dollars": cost.dollars,
                "latency_s": cost.latency_s,
            }
            for (role, alias), cost in sorted(priors.mean_cost.items())
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def priors_from_json(text: str) -> Priors:
    data = json.loads(text)
    catch_rate = {
        (str(entry["role"]), str(entry["model_alias"]), str(entry["category"])): float(
            entry["rate"]
        )
        for entry in data.get("catch_rate", [])
    }
    mean_cost = {
        (str(entry["role"]), str(entry["model_alias"])): Cost(
            float(entry["dollars"]), float(entry["latency_s"])
        )
        for entry in data.get("mean_cost", [])
    }
    return Priors(catch_rate=catch_rate, mean_cost=mean_cost, corpus_size=int(data["corpus_size"]))
