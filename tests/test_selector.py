import pytest

from oyster.graph.catalog import CATALOG, PATH_A, PATH_B, PATH_C
from oyster.selector import has_priors, predict, select
from oyster.types import CorpusCase, Cost, Priors

CASE = CorpusCase("case", "", ())


def priors(cheap=None, strong=None, critic=None, rates=None):
    cheap = Cost(0.01, 2.0) if cheap is None else cheap
    strong = Cost(0.10, 10.0) if strong is None else strong
    critic = Cost(0.10, 10.0) if critic is None else critic
    rates = rates or {}
    catch_rate = {}
    for role, alias in (
        ("cheap-scanner", "cheap-model"),
        ("deep-reviewer", "strong-model"),
        ("critic", "strong-model"),
    ):
        for category in ("logic", "security", "style"):
            catch_rate[(role, alias, category)] = rates.get((role, category), 0.5)
    return Priors(
        catch_rate=catch_rate,
        mean_cost={
            ("cheap-scanner", "cheap-model"): cheap,
            ("deep-reviewer", "strong-model"): strong,
            ("critic", "strong-model"): critic,
        },
        corpus_size=3,
    )


def test_predict_cost_sums_node_priors_and_quality_uses_independence(bindings):
    quality, cost = predict(PATH_B, CASE, priors(), bindings)
    assert cost == Cost(0.11, 12.0)
    assert quality == pytest.approx(1 - 0.5 * 0.5)
    quality_a, _ = predict(PATH_A, CASE, priors(), bindings)
    assert quality_a == pytest.approx(0.5)


def test_path_over_budget_is_rejected_with_reason_budget(bindings):
    selection = select(
        CATALOG, CASE, priors(), bindings, budget_dollars=0.05, latency_tolerance_s=100
    )
    assert selection.path_id == "A"
    assert ("B", "budget") in selection.rejected
    assert ("C", "budget") in selection.rejected


def test_path_over_tolerance_is_rejected_with_latency_even_when_cheapest(bindings):
    slow_cheap = priors(cheap=Cost(0.001, 500.0))
    selection = select(
        CATALOG, CASE, slow_cheap, bindings, budget_dollars=10, latency_tolerance_s=100
    )
    assert ("A", "latency") in selection.rejected
    assert ("B", "latency") in selection.rejected
    assert selection.path_id == "C"


def test_empty_feasible_set_returns_none_with_cheapest_infeasible(bindings):
    selection = select(
        CATALOG, CASE, priors(), bindings, budget_dollars=0.001, latency_tolerance_s=100
    )
    assert selection.path_id is None
    assert selection.no_feasible_reason is not None
    assert selection.no_feasible_reason.startswith("budget")
    assert selection.cheapest_infeasible == ("A", Cost(0.01, 2.0))
    assert len(selection.rejected) == 3


def test_latency_named_when_it_eliminated_everything(bindings):
    selection = select(CATALOG, CASE, priors(), bindings, budget_dollars=10, latency_tolerance_s=1)
    assert selection.path_id is None
    assert selection.no_feasible_reason.startswith("latency")
    assert selection.cheapest_infeasible[0] == "A"


def test_tie_in_quality_resolves_to_lower_cost(bindings):
    # Make the deep reviewer and critic worthless so B and C match A on quality.
    rates = {("deep-reviewer", c): 0.0 for c in ("logic", "security", "style")}
    rates.update({("critic", c): 0.0 for c in ("logic", "security", "style")})
    selection = select(CATALOG, CASE, priors(rates=rates), bindings, 10, 1000)
    assert selection.path_id == "A"
    assert selection.predicted_cost == Cost(0.01, 2.0)


def test_tie_in_quality_and_cost_resolves_to_path_id(bindings):
    # Deep reviewer and critic cost nothing and catch nothing, so B ties A on both axes.
    rates = {("deep-reviewer", c): 0.0 for c in ("logic", "security", "style")}
    rates.update({("critic", c): 0.0 for c in ("logic", "security", "style")})
    tied = priors(cheap=Cost(0.1, 1.0), strong=Cost(0.0, 0.0), critic=Cost(0.0, 0.0), rates=rates)
    selection = select([PATH_B, PATH_A], CASE, tied, bindings, 10, 1000)
    assert selection.path_id == "A"


def test_missing_priors_are_rejected_not_scored_as_zero(bindings):
    partial = priors()
    partial.mean_cost.pop(("critic", "strong-model"))
    selection = select(CATALOG, CASE, partial, bindings, 10, 1000)
    assert ("C", "no priors") in selection.rejected
    assert selection.path_id == "B"
    assert not has_priors(PATH_C, partial)
    assert has_priors(PATH_B, partial)


def test_all_missing_priors_reports_no_priors_and_no_cheapest(bindings):
    empty = Priors(catch_rate={}, mean_cost={}, corpus_size=0)
    selection = select(CATALOG, CASE, empty, bindings, 10, 1000)
    assert selection.path_id is None
    assert selection.no_feasible_reason.startswith("no priors")
    assert selection.cheapest_infeasible is None
    assert selection.rejected == (("A", "no priors"), ("B", "no priors"), ("C", "no priors"))


def test_best_quality_wins_when_affordable(bindings):
    selection = select(CATALOG, CASE, priors(), bindings, 10, 1000)
    assert selection.path_id == "C"
    assert selection.predicted_quality == pytest.approx(1 - 0.5**3)
    assert selection.rejected == ()
