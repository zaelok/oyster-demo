"""Real API calls. Token counts come from the API response, never from an estimate.

Retry policy: 429 and 5xx are retried, three attempts in total, exponential backoff with
jitter (1s, 2s, then 4s if a further attempt were ever added). Any other error raises
immediately. Latency is perf_counter around the successful call.
"""

import random
import time
from collections.abc import Callable
from typing import Any

import anthropic

from oyster.types import Completion

MAX_ATTEMPTS = 3
BACKOFF_S = (1.0, 2.0, 4.0)
JITTER_S = 0.5
MAX_OUTPUT_TOKENS = 4096


class AnthropicProvider:
    def __init__(
        self,
        api_key: str,
        *,
        client: Any | None = None,
        sleep: Callable[[float], None] = time.sleep,
        rng: random.Random | None = None,
    ):
        self._client = client if client is not None else anthropic.Anthropic(api_key=api_key)
        self._sleep = sleep
        self._rng = rng if rng is not None else random.Random()

    def complete(
        self,
        model_id: str,
        system: str,
        user: str,
        cached_prefix: str | None = None,
    ) -> Completion:
        system_blocks: list[dict[str, Any]] = []
        if cached_prefix:
            system_blocks.append(
                {"type": "text", "text": cached_prefix, "cache_control": {"type": "ephemeral"}}
            )
        if system:
            system_blocks.append({"type": "text", "text": system})

        request: dict[str, Any] = {
            "model": model_id,
            "max_tokens": MAX_OUTPUT_TOKENS,
            "messages": [{"role": "user", "content": user}],
        }
        if system_blocks:
            request["system"] = system_blocks

        response, latency_s = self._call_with_retry(request)
        usage = getattr(response, "usage", None)
        base_input = _usage_int(usage, "input_tokens")
        cache_read = _usage_int(usage, "cache_read_input_tokens")
        cache_write = _usage_int(usage, "cache_creation_input_tokens")
        return Completion(
            text=_text_of(response),
            # The API reports uncached, cache-read and cache-write tokens separately; the
            # pricing formula wants total input with the cached share broken out.
            input_tokens=base_input + cache_read + cache_write,
            cached_input_tokens=cache_read,
            output_tokens=_usage_int(usage, "output_tokens"),
            latency_s=latency_s,
            model_id=str(getattr(response, "model", None) or model_id),
        )

    def _call_with_retry(self, request: dict[str, Any]) -> tuple[Any, float]:
        for attempt in range(MAX_ATTEMPTS):
            start = time.perf_counter()
            try:
                response = self._client.messages.create(**request)
            except anthropic.APIStatusError as exc:
                retryable = exc.status_code == 429 or exc.status_code >= 500
                if retryable and attempt < MAX_ATTEMPTS - 1:
                    self._sleep(BACKOFF_S[attempt] + self._rng.uniform(0.0, JITTER_S))
                    continue
                raise
            return response, time.perf_counter() - start
        raise RuntimeError("unreachable: retry loop exhausted without raising")


def _usage_int(usage: Any, field: str) -> int:
    """Read a usage field; 0 when the API omits it. Never an estimate."""
    value = getattr(usage, field, None) if usage is not None else None
    return int(value) if value is not None else 0


def _text_of(response: Any) -> str:
    blocks = getattr(response, "content", None) or []
    return "".join(
        str(getattr(block, "text", "")) for block in blocks if getattr(block, "type", "") == "text"
    )
