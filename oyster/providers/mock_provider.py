"""Deterministic provider for CI and tests.

Every request is keyed by a hash of its inputs and answered from a recorded fixture when one
exists. A missing fixture is not an error: it yields a valid empty response, so a run with
zero fixtures still produces a complete, honest table in which every path catches nothing.
"""

import hashlib
import json
import sys
from pathlib import Path

from oyster.cost import estimate_tokens
from oyster.types import Completion

MISS_LATENCY_S = 0.05
EMPTY_RESPONSE = '{"findings": []}'


def fixture_key(model_id: str, system: str, user: str, cached_prefix: str | None) -> str:
    """sha256(model_id + system + user + (cached_prefix or ""))[:16]."""
    payload = model_id + system + user + (cached_prefix or "")
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


class MockProvider:
    def __init__(self, fixtures_dir: Path):
        self.fixtures_dir = Path(fixtures_dir)
        self.misses: list[str] = []

    def complete(
        self,
        model_id: str,
        system: str,
        user: str,
        cached_prefix: str | None = None,
    ) -> Completion:
        key = fixture_key(model_id, system, user, cached_prefix)
        fixture = self.fixtures_dir / f"{key}.json"
        if fixture.is_file():
            data = json.loads(fixture.read_text(encoding="utf-8"))
            return Completion(
                text=str(data["text"]),
                input_tokens=int(data["input_tokens"]),
                cached_input_tokens=int(data["cached_input_tokens"]),
                output_tokens=int(data["output_tokens"]),
                latency_s=float(data["latency_s"]),
                model_id=str(data["model_id"]),
            )

        self.misses.append(key)
        print(
            f"mock_provider: no fixture {fixture} for model {model_id}; returning empty findings",
            file=sys.stderr,
        )
        prefix = cached_prefix or ""
        return Completion(
            text=EMPTY_RESPONSE,
            input_tokens=estimate_tokens(prefix + system + user),
            cached_input_tokens=estimate_tokens(prefix),
            output_tokens=estimate_tokens(EMPTY_RESPONSE),
            latency_s=MISS_LATENCY_S,
            model_id=model_id,
        )
