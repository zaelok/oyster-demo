import pytest

from oyster.cost import estimate_tokens, path_cost, price
from oyster.types import Completion, Cost, ModelBinding

BINDING = ModelBinding("strong-model", "m", 3.0, 15.0, 0.9)


def test_price_matches_spec_formula_exactly():
    completion = Completion("x", 1000, 800, 200, 1.25, "m")
    cost = price(completion, BINDING)
    # Same operand order as the implementation and the spec docstring, so the float is exact.
    expected = (200 * 3.0 + 800 * 3.0 * (1 - 0.9) + 200 * 15.0) / 1e6
    assert cost.dollars == expected
    # The spec's acceptance text writes the discount factor as 0.1; that differs from
    # (1 - 0.9) by one ulp, so it is checked with a tolerance rather than exactly.
    assert cost.dollars == pytest.approx((200 * 3 + 800 * 3 * 0.1 + 200 * 15) / 1e6)
    assert cost.latency_s == 1.25


def test_uncached_tokens_pay_full_rate():
    completion = Completion("x", 1000, 0, 0, 0.0, "m")
    assert price(completion, BINDING).dollars == pytest.approx(0.003)


def test_zero_is_additive_identity():
    cost = Cost(1.5, 2.5)
    assert cost + Cost.zero() == cost
    assert Cost.zero() + cost == cost


def test_path_cost_empty_is_zero():
    assert path_cost([]) == Cost.zero()


def test_path_cost_sums_dollars_and_latency():
    assert path_cost([Cost(1.0, 2.0), Cost(0.5, 3.0)]) == Cost(1.5, 5.0)


def test_estimate_tokens_is_chars_div_4():
    assert estimate_tokens("") == 0
    assert estimate_tokens("abcd") == 1
    assert estimate_tokens("a" * 403) == 100
