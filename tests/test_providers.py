import json
import random
from types import SimpleNamespace

import anthropic
import pytest

from oyster.providers import AnthropicProvider, MockProvider, RecordingProvider, fixture_key

# ---------------------------------------------------------------- mock provider


def test_mock_is_deterministic(tmp_path):
    provider = MockProvider(tmp_path)
    first = provider.complete("m", "sys", "user", "diff")
    second = provider.complete("m", "sys", "user", "diff")
    assert first == second


def test_same_inputs_give_same_key_and_different_inputs_do_not():
    assert fixture_key("m", "s", "u", "d") == fixture_key("m", "s", "u", "d")
    assert fixture_key("m", "s", "u", "d") != fixture_key("m", "s", "u", "d2")
    assert fixture_key("m", "s", "u", None) == fixture_key("m", "s", "u", "")
    assert len(fixture_key("m", "s", "u", "d")) == 16


def test_missing_fixture_returns_empty_findings_not_error(tmp_path, capsys):
    provider = MockProvider(tmp_path)
    completion = provider.complete("mock-cheap", "", "prompt", "diff text")
    assert json.loads(completion.text) == {"findings": []}
    assert completion.latency_s == 0.05
    assert completion.input_tokens > 0
    assert completion.model_id == "mock-cheap"
    assert provider.misses == [fixture_key("mock-cheap", "", "prompt", "diff text")]
    assert "no fixture" in capsys.readouterr().err


def test_fixture_hit_is_replayed(tmp_path):
    key = fixture_key("mock-cheap", "", "prompt", "diff")
    (tmp_path / f"{key}.json").write_text(
        json.dumps(
            {
                "text": '{"findings": []}',
                "input_tokens": 1200,
                "cached_input_tokens": 1000,
                "output_tokens": 150,
                "latency_s": 0.8,
                "model_id": "mock-cheap",
            }
        )
    )
    completion = MockProvider(tmp_path).complete("mock-cheap", "", "prompt", "diff")
    assert completion.input_tokens == 1200
    assert completion.cached_input_tokens == 1000
    assert completion.latency_s == 0.8


def test_recording_provider_writes_replayable_fixture(tmp_path):
    class Inner:
        def complete(self, model_id, system, user, cached_prefix=None):
            from oyster.types import Completion

            return Completion('{"findings": []}', 10, 5, 2, 0.3, model_id)

    recorder = RecordingProvider(Inner(), tmp_path)
    original = recorder.complete("m", "s", "u", "d")
    replayed = MockProvider(tmp_path).complete("m", "s", "u", "d")
    assert replayed == original
    assert recorder.recorded == [fixture_key("m", "s", "u", "d")]


# ------------------------------------------------------------ anthropic provider


def _response(text='{"findings": []}', **usage):
    return SimpleNamespace(
        content=[SimpleNamespace(type="text", text=text)],
        usage=SimpleNamespace(**usage),
        model="claude-x",
    )


def _status_error(status: int):
    # The SDK exception only reads status_code, headers and request off the response, so a
    # response-shaped stub keeps the test independent of the SDK's HTTP client.
    response = SimpleNamespace(status_code=status, headers={}, request=None)
    return anthropic.APIStatusError(f"status {status}", response=response, body=None)


class StubClient:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.requests = []
        self.messages = SimpleNamespace(create=self.create)

    def create(self, **request):
        self.requests.append(request)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def _provider(client, sleeps):
    return AnthropicProvider("key", client=client, sleep=sleeps.append, rng=random.Random(0))


def test_cached_tokens_come_from_usage_not_computed():
    client = StubClient(
        [
            _response(
                input_tokens=100,
                output_tokens=20,
                cache_read_input_tokens=900,
                cache_creation_input_tokens=0,
            )
        ]
    )
    completion = _provider(client, []).complete("claude-x", "sys", "user", "d" * 40000)
    assert completion.cached_input_tokens == 900
    assert completion.input_tokens == 1000
    assert completion.output_tokens == 20
    assert completion.model_id == "claude-x"
    assert completion.latency_s >= 0.0


def test_omitted_usage_field_records_zero_not_an_estimate():
    client = StubClient([_response(input_tokens=50, output_tokens=5)])
    completion = _provider(client, []).complete("claude-x", "", "user", "prefix")
    assert completion.cached_input_tokens == 0
    assert completion.input_tokens == 50


def test_cached_prefix_goes_in_system_block_with_cache_control():
    client = StubClient([_response(input_tokens=1, output_tokens=1)])
    _provider(client, []).complete("claude-x", "instructions", "user body", "THE DIFF")
    request = client.requests[0]
    assert request["model"] == "claude-x"
    assert request["messages"] == [{"role": "user", "content": "user body"}]
    assert request["system"][0] == {
        "type": "text",
        "text": "THE DIFF",
        "cache_control": {"type": "ephemeral"},
    }
    assert request["system"][1] == {"type": "text", "text": "instructions"}


def test_retries_on_429_with_backoff_then_succeeds():
    client = StubClient(
        [_status_error(429), _status_error(503), _response(input_tokens=1, output_tokens=1)]
    )
    sleeps: list[float] = []
    completion = _provider(client, sleeps).complete("claude-x", "", "u", None)
    assert completion.text == '{"findings": []}'
    assert len(client.requests) == 3
    assert len(sleeps) == 2
    assert 1.0 <= sleeps[0] <= 1.5
    assert 2.0 <= sleeps[1] <= 2.5


def test_gives_up_after_three_attempts():
    client = StubClient([_status_error(429), _status_error(429), _status_error(429)])
    sleeps: list[float] = []
    with pytest.raises(anthropic.APIStatusError):
        _provider(client, sleeps).complete("claude-x", "", "u", None)
    assert len(client.requests) == 3
    assert len(sleeps) == 2


def test_does_not_retry_on_400():
    client = StubClient([_status_error(400)])
    sleeps: list[float] = []
    with pytest.raises(anthropic.APIStatusError):
        _provider(client, sleeps).complete("claude-x", "", "u", None)
    assert len(client.requests) == 1
    assert sleeps == []
