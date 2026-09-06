"""Runs one Path against one CorpusCase and returns a PathResult.

Execution contract (spec §10):
- nodes run in path order; before each one every hook is consulted and the first non-None
  reason halts the run. A halted run is data, not an error: the partial PathResult carries
  the node results collected so far and the reason.
- the diff is passed to the provider as cached_prefix and never duplicated into the user
  body (see oyster.prompts.render_messages).
- upstream findings are the union over upstream nodes, deduplicated by
  (file, line_start, line_end, category), ordered by file then line_start.
- a response that is not JSON is retried once with a repair suffix; a second failure records
  an empty NodeResult with parse_failed=True. The cost of every call, failed or not, is kept.
- findings on files absent from the diff are discarded and counted in the debug log.
- PathResult.findings is the LAST node's findings, not the union: a cascade's later stage
  supersedes the earlier one, and the critic path depends on that.
"""

import json
import logging
import re
from collections.abc import Sequence
from dataclasses import replace
from typing import Any

from oyster.cost import path_cost, price
from oyster.graph import upstream_of
from oyster.scenario import Scenario
from oyster.types import (
    CATEGORIES,
    Cost,
    Finding,
    Hook,
    ModelBinding,
    ModelProvider,
    Node,
    NodeResult,
    Path,
    PathResult,
    Priors,
)

__all__ = [
    "REPAIR_SUFFIX",
    "UNBOUNDED",
    "BudgetHook",
    "diff_files",
    "keep_known",
    "parse_findings",
    "run_path",
    "stats",
]

log = logging.getLogger("oyster.executor")

REPAIR_SUFFIX = "\n\nYour previous response was not valid JSON. Respond with JSON only."
UNBOUNDED = Cost(float("inf"), float("inf"))

# Module-level counters behind the debug log: how often models hallucinated paths or emitted
# individual findings that did not fit the output contract.
stats = {"discarded_unknown_file": 0, "dropped_malformed_item": 0}

_FENCE = re.compile(r"^\s*```(?:json)?\s*(.*?)\s*```\s*$", re.DOTALL)


def diff_files(diff: str) -> frozenset[str]:
    """Target paths on the new-file side of a unified diff, 'a/' or 'b/' prefix stripped."""
    files: set[str] = set()
    previous = ""
    for line in diff.splitlines():
        if line.startswith("+++ ") and previous.startswith("--- "):
            target = line[4:].split("\t", 1)[0].strip()
            if target.startswith(("a/", "b/")):
                target = target[2:]
            if target != "/dev/null":
                files.add(target)
        previous = line
    return frozenset(files)


def _normalize_file(file: str) -> str:
    file = file.strip()
    return file[2:] if file.startswith(("a/", "b/")) else file


def parse_findings(text: str) -> tuple[Finding, ...] | None:
    """Parse a node response. None means the response was not a JSON object with a
    'findings' list (the retry condition). Individual items that do not fit the contract are
    dropped and counted; they do not fail the whole response."""
    try:
        data = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        fenced = _FENCE.match(text or "")
        if not fenced:
            return None
        try:
            data = json.loads(fenced.group(1))
        except json.JSONDecodeError:
            return None
    if not isinstance(data, dict) or not isinstance(data.get("findings"), list):
        return None

    findings: list[Finding] = []
    for item in data["findings"]:
        finding = _finding_from(item)
        if finding is None:
            stats["dropped_malformed_item"] += 1
            log.debug("dropped malformed finding item: %r", item)
            continue
        findings.append(finding)
    return tuple(findings)


def _finding_from(item: object) -> Finding | None:
    if not isinstance(item, dict):
        return None
    try:
        file = str(item["file"])
        line_start = int(item["line_start"])
        line_end = int(item["line_end"])
        category = str(item["category"])
        description = str(item.get("description", ""))
        confidence = float(item.get("confidence", 0.0))
    except (KeyError, TypeError, ValueError):
        return None
    if category not in CATEGORIES or line_start < 1 or line_end < line_start:
        return None
    return Finding(file, line_start, line_end, category, description, confidence)  # type: ignore[arg-type]


def keep_known(findings: Sequence[Finding], diff: str) -> tuple[Finding, ...]:
    """Drop findings on files the diff does not touch, normalizing 'a/' and 'b/' prefixes."""
    known = diff_files(diff)
    kept: list[Finding] = []
    for finding in findings:
        normalized = _normalize_file(finding.file)
        if normalized in known:
            kept.append(replace(finding, file=normalized))
        else:
            stats["discarded_unknown_file"] += 1
            log.debug("discarded finding on file absent from diff: %r", finding.file)
    return tuple(kept)


def _upstream_outputs(
    path: Path, node_id: str, done: dict[str, NodeResult], scenario: Scenario
) -> tuple[Any, ...]:
    seen: set[Any] = set()
    merged: list[Any] = []
    for upstream_id in upstream_of(path, node_id):
        result = done.get(upstream_id)
        if result is None:
            continue
        for output in result.findings:
            key = scenario.dedup_key(output)
            if key not in seen:
                seen.add(key)
                merged.append(output)
    merged.sort(key=scenario.sort_key)
    return tuple(merged)


def _last_findings(results: Sequence[NodeResult]) -> tuple[Any, ...]:
    return results[-1].findings if results else ()


def run_path(
    path: Path,
    case: Any,
    provider: ModelProvider,
    bindings: dict[str, ModelBinding],
    hooks: Sequence[Hook] = (),
    budget: Cost = UNBOUNDED,
    scenario: Scenario | None = None,
) -> PathResult:
    """Execute path over case. `budget` is the run-level budget handed to hooks; it defaults to
    unbounded because the spec signature carries none, and BudgetHook brings its own.
    `scenario` supplies rendering, parsing, filtering and output identity; it defaults to code
    review so every v1 call site is unchanged."""
    if scenario is None:
        from oyster.scenarios.code_review import CODE_REVIEW

        scenario = CODE_REVIEW
    results: list[NodeResult] = []
    done: dict[str, NodeResult] = {}
    spent = Cost.zero()

    for node in path.nodes:
        for hook in hooks:
            reason = hook.before_node(node, spent, budget)
            if reason is not None:
                return PathResult(
                    path_id=path.id,
                    case_id=case.id,
                    node_results=tuple(results),
                    findings=_last_findings(results),
                    cost=path_cost([result.cost for result in results]),
                    halted_reason=reason,
                )

        binding = bindings[node.model_alias]
        upstream = _upstream_outputs(path, node.id, done, scenario)
        system, user, cached_prefix = scenario.render_messages(node.prompt_key, case, upstream)

        completion = provider.complete(binding.model_id, system, user, cached_prefix)
        cost = price(completion, binding)
        parsed = scenario.parse_output(completion.text)
        parse_failed = False
        if parsed is None:
            completion = provider.complete(
                binding.model_id, system, user + REPAIR_SUFFIX, cached_prefix
            )
            cost = cost + price(completion, binding)
            parsed = scenario.parse_output(completion.text)
            if parsed is None:
                parse_failed = True
                parsed = ()

        result = NodeResult(
            node_id=node.id,
            role=node.role,
            findings=scenario.keep(parsed, case),
            completion=completion,
            cost=cost,
            parse_failed=parse_failed,
        )
        results.append(result)
        done[node.id] = result
        spent = spent + cost

    return PathResult(
        path_id=path.id,
        case_id=case.id,
        node_results=tuple(results),
        findings=_last_findings(results),
        cost=path_cost([result.cost for result in results]),
        halted_reason=None,
    )


class BudgetHook:
    """Halts before a node when spend so far plus the node's predicted cost would exceed the
    budget. Predicted cost is priors.mean_cost[(role, model_alias)], zero without priors. The
    effective budget is the stricter of this hook's own and the run-level one it is handed."""

    def __init__(self, budget: Cost, priors: Priors | None = None):
        self.budget = budget
        self.priors = priors

    def before_node(self, node: Node, spent: Cost, budget: Cost) -> str | None:
        predicted = Cost.zero()
        if self.priors is not None:
            predicted = self.priors.mean_cost.get((node.role, node.model_alias), Cost.zero())
        limit = Cost(
            min(self.budget.dollars, budget.dollars), min(self.budget.latency_s, budget.latency_s)
        )
        projected = spent + predicted
        if projected.dollars > limit.dollars:
            return (
                f"budget: ${spent.dollars:.4f} spent + ${predicted.dollars:.4f} predicted for "
                f"node {node.id} exceeds ${limit.dollars:.4f}"
            )
        if projected.latency_s > limit.latency_s:
            return (
                f"latency: {spent.latency_s:.2f}s spent + {predicted.latency_s:.2f}s predicted "
                f"for node {node.id} exceeds {limit.latency_s:.2f}s"
            )
        return None
