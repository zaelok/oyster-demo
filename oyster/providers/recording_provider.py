"""Wraps any provider and writes each completion as a mock fixture, keyed exactly as
MockProvider looks them up, so a paid run can be replayed offline forever after."""

import json
from pathlib import Path

from oyster.providers.mock_provider import fixture_key
from oyster.types import Completion, ModelProvider


class RecordingProvider:
    def __init__(self, inner: ModelProvider, fixtures_dir: Path):
        self.inner = inner
        self.fixtures_dir = Path(fixtures_dir)
        self.recorded: list[str] = []

    def complete(
        self,
        model_id: str,
        system: str,
        user: str,
        cached_prefix: str | None = None,
    ) -> Completion:
        completion = self.inner.complete(model_id, system, user, cached_prefix)
        key = fixture_key(model_id, system, user, cached_prefix)
        self.fixtures_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "text": completion.text,
            "input_tokens": completion.input_tokens,
            "cached_input_tokens": completion.cached_input_tokens,
            "output_tokens": completion.output_tokens,
            "latency_s": completion.latency_s,
            "model_id": completion.model_id,
        }
        (self.fixtures_dir / f"{key}.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        self.recorded.append(key)
        return completion
