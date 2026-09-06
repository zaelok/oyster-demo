"""Cost arithmetic. One pricing formula and one token estimator, used everywhere, so estimated
and billed numbers can never diverge silently."""

from collections.abc import Sequence

from oyster.types import Completion, Cost, ModelBinding

__all__ = ["estimate_tokens", "path_cost", "price"]


def price(completion: Completion, binding: ModelBinding) -> Cost:
    """dollars = (input - cached) * rate_in / 1e6
              + cached * rate_in * (1 - cache_discount) / 1e6
              + output * rate_out / 1e6
    latency = completion.latency_s
    """
    uncached = completion.input_tokens - completion.cached_input_tokens
    dollars = (
        uncached * binding.rate_in
        + completion.cached_input_tokens * binding.rate_in * (1 - binding.cache_discount)
        + completion.output_tokens * binding.rate_out
    ) / 1e6
    return Cost(dollars, completion.latency_s)


def path_cost(node_costs: Sequence[Cost]) -> Cost:
    """Sequential execution: dollars sum, latency sums.

    NOTE: latency is a sum because this slice executes nodes serially. If parallel branches
    are added, latency becomes a max over branches and only this function changes.
    """
    total = Cost.zero()
    for cost in node_costs:
        total = total + cost
    return total


def estimate_tokens(text: str) -> int:
    """Single shared estimator, chars // 4. Used for prediction only, never for billing.
    Actual counts always come from Completion."""
    return len(text) // 4
