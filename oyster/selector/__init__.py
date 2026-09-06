"""Budgeted path selection over the catalog (architecture §2).

Prediction is one algorithm over data: the same formula prices and scores every path from
calibrated priors, so adding a strategy is adding a Path, not adding selection code.

INDEPENDENCE ASSUMPTION. Predicted quality treats the nodes of a path as independent
detectors: for each category, P(caught) = 1 - prod over nodes of (1 - catch_rate). That is
false in reality. A deep reviewer that receives a scanner's findings is correlated with the
scanner, and the critic path re-runs the same role twice on the same diff. Knowing where the
model is wrong is part of the deliverable: the evaluation table measures whole paths and
shows how far the independent prediction is from the truth.
"""

from collections.abc import Sequence

from oyster.cost import path_cost
from oyster.types import CATEGORIES, CorpusCase, Cost, ModelBinding, Path, Priors, Selection

__all__ = ["has_priors", "predict", "select"]


def has_priors(path: Path, priors: Priors) -> bool:
    """Every node has a mean cost and at least one calibrated catch rate."""
    for node in path.nodes:
        if (node.role, node.model_alias) not in priors.mean_cost:
            return False
        if not any(
            (node.role, node.model_alias, category) in priors.catch_rate for category in CATEGORIES
        ):
            return False
    return True


def predict(
    path: Path,
    case: CorpusCase,
    priors: Priors,
    bindings: dict[str, ModelBinding],
) -> tuple[float, Cost]:
    """(predicted_quality, predicted_cost) for path under priors.

    Cost is the sum over nodes of priors.mean_cost[(role, model_alias)], zero for an absent
    key (select() rejects such paths rather than ranking them). Quality is the mean over
    categories of 1 - prod over nodes of (1 - catch_rate[role, alias, category]); a missing
    catch rate counts as 0.0 for that node and category. See the module docstring for the
    independence assumption. `case` and `bindings` are accepted for the future where predicted
    tokens scale with the diff; in this slice priors are per node config only.
    """
    del case, bindings
    node_costs = []
    for node in path.nodes:
        key = (node.role, node.model_alias)
        mean = priors.mean_cost.get(key, Cost.zero())
        profile = priors.cost.get(key)
        # v2: latency is an SLO, so predict it at p95 when the profile has one; dollars stay
        # at the mean, which is what a budget over many tasks actually pays.
        latency = profile.latency_p95 if profile is not None else mean.latency_s
        node_costs.append(Cost(mean.dollars, latency))
    cost = path_cost(node_costs)

    per_category: list[float] = []
    for category in CATEGORIES:
        miss = 1.0
        for node in path.nodes:
            miss *= 1.0 - priors.catch_rate.get((node.role, node.model_alias, category), 0.0)
        per_category.append(1.0 - miss)
    quality = sum(per_category) / len(per_category)
    return quality, cost


def select(
    paths: Sequence[Path],
    case: CorpusCase,
    priors: Priors,
    bindings: dict[str, ModelBinding],
    budget_dollars: float,
    latency_tolerance_s: float,
) -> Selection:
    """Reject in order: no priors, latency over tolerance, dollars over budget. Among survivors
    return the max predicted quality, ties to lower predicted dollars, then path id. With no
    survivors, say so: name the constraint that eliminated the last candidates and surface the
    cheapest priced-but-infeasible option so the caller can raise the budget or relax the
    tolerance. The engine never silently degrades."""
    # SEAM: enumeration is exhaustive over `paths`. A Steiner-style heuristic that generates
    # candidate subgraphs from the full node graph instead of the shipped catalog would attach
    # here, feeding the same predict()/reject/argmax loop below.
    rejected: list[tuple[str, str]] = []
    priced_rejected: list[tuple[str, Cost]] = []
    survivors: list[tuple[Path, float, Cost]] = []

    for path in paths:
        quality, cost = predict(path, case, priors, bindings)
        if not has_priors(path, priors):
            rejected.append((path.id, "no priors"))
            continue
        if cost.latency_s > latency_tolerance_s:
            rejected.append((path.id, "latency"))
            priced_rejected.append((path.id, cost))
            continue
        if cost.dollars > budget_dollars:
            rejected.append((path.id, "budget"))
            priced_rejected.append((path.id, cost))
            continue
        survivors.append((path, quality, cost))

    if survivors:
        best_path, best_quality, best_cost = min(
            survivors, key=lambda entry: (-entry[1], entry[2].dollars, entry[0].id)
        )
        return Selection(
            path_id=best_path.id,
            predicted_quality=best_quality,
            predicted_cost=best_cost,
            rejected=tuple(rejected),
        )

    reasons = {reason for _, reason in rejected}
    if "budget" in reasons:
        constraint = "budget"
        detail = f"every priced candidate exceeds the budget of ${budget_dollars:.2f}"
    elif "latency" in reasons:
        constraint = "latency"
        detail = (
            f"every priced candidate exceeds the latency tolerance of {latency_tolerance_s:.0f}s"
        )
    else:
        constraint = "no priors"
        detail = "no candidate has calibrated priors; run calibrate first"
    cheapest = min(priced_rejected, key=lambda entry: (entry[1].dollars, entry[0]), default=None)
    return Selection(
        path_id=None,
        predicted_quality=0.0,
        predicted_cost=Cost.zero(),
        rejected=tuple(rejected),
        no_feasible_reason=f"{constraint}: {detail}",
        cheapest_infeasible=cheapest,
    )
