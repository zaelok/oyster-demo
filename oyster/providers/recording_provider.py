"""Wraps any provider and writes each completion as a mock fixture, keyed exactly as
MockProvider looks them up, so a paid run can be replayed offline forever after.

A request whose fixture already exists is answered from the fixture and never sent again.
That makes every recorded run resumable: an interrupted run re-issued with the same command
replays what it already paid for and only makes the calls that are missing. It also means
identical requests across calibrate and eval (a single-node calibration path and the same
node at the head of a flow render byte-identical prompts) are paid for once."""

import json
import threading
from pathlib import Path

from oyster.providers.mock_provider import MockProvider, fixture_key
from oyster.types import Completion, ModelProvider


class RecordingProvider:
    def __init__(self, inner: ModelProvider, fixtures_dir: Path, replay: bool = True):
        self.inner = inner
        self.fixtures_dir = Path(fixtures_dir)
        self.replay = replay
        self.recorded: list[str] = []
        self.replayed: list[str] = []
        self._lock = threading.Lock()

    def complete(
        self,
        model_id: str,
        system: str,
        user: str,
        cached_prefix: str | None = None,
    ) -> Completion:
        key = fixture_key(model_id, system, user, cached_prefix)
        if self.replay and (self.fixtures_dir / f"{key}.json").is_file():
            with self._lock:
                self.replayed.append(key)
            return MockProvider(self.fixtures_dir).complete(model_id, system, user, cached_prefix)
        completion = self.inner.complete(model_id, system, user, cached_prefix)
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
        with self._lock:
            self.recorded.append(key)
        return completion
