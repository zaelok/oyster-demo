"""Shared test helpers. Every test runs offline."""

import json
from pathlib import Path

import pytest

from oyster.corpus import load_case_file
from oyster.types import Completion, CorpusCase, ModelBinding

FIXTURES = Path(__file__).parent / "fixtures"
CORPUS_DIR = FIXTURES / "corpus"
INVALID_DIR = FIXTURES / "corpus_invalid"

EMPTY = '{"findings": []}'


@pytest.fixture
def bindings() -> dict[str, ModelBinding]:
    return {
        "cheap-model": ModelBinding("cheap-model", "mock-cheap", 1.0, 5.0, 0.9),
        "strong-model": ModelBinding("strong-model", "mock-strong", 3.0, 15.0, 0.9),
    }


@pytest.fixture
def corpus_case() -> CorpusCase:
    return load_case_file(CORPUS_DIR / "case-01.json")


class ScriptedProvider:
    """Records every call and answers from a scripted list of texts; the last text repeats.
    Fixed token counts so costs are predictable."""

    def __init__(self, texts: list[str] | None = None):
        self.texts = list(texts or [EMPTY])
        self.calls: list[dict[str, str | None]] = []

    def complete(
        self,
        model_id: str,
        system: str,
        user: str,
        cached_prefix: str | None = None,
    ) -> Completion:
        index = len(self.calls)
        self.calls.append(
            {"model_id": model_id, "system": system, "user": user, "cached_prefix": cached_prefix}
        )
        text = self.texts[min(index, len(self.texts) - 1)]
        return Completion(
            text=text,
            input_tokens=1000,
            cached_input_tokens=800,
            output_tokens=100,
            latency_s=0.5,
            model_id=model_id,
        )


def finding_json(file: str, start: int, end: int, category: str = "logic") -> str:
    finding = {
        "file": file,
        "line_start": start,
        "line_end": end,
        "category": category,
        "description": "d",
        "confidence": 0.9,
    }
    return json.dumps({"findings": [finding]})
