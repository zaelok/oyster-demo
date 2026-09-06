import json
import subprocess
from pathlib import Path

import pytest

from oyster.providers.claude_code_provider import ClaudeCodeProvider, _parse_result


def _result(text='{"findings": []}', **overrides):
    payload = {
        "type": "result",
        "subtype": "success",
        "is_error": False,
        "result": text,
        "stop_reason": "end_turn",
        "duration_ms": 4200,
        "duration_api_ms": 3100,
        "usage": {
            "input_tokens": 120,
            "cache_creation_input_tokens": 900,
            "cache_read_input_tokens": 0,
            "output_tokens": 45,
        },
        "modelUsage": {"claude-haiku-4-5": {"inputTokens": 1020, "outputTokens": 45}},
    }
    payload.update(overrides)
    return json.dumps(payload)


class FakeRunner:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = []

    def __call__(self, args, **kwargs):
        # Capture the system prompt file before the provider deletes it.
        system_file = args[args.index("--system-prompt-file") + 1]
        self.calls.append(
            {
                "args": args,
                "input": kwargs.get("input"),
                "env": kwargs.get("env"),
                "cwd": kwargs.get("cwd"),
                "system": Path(system_file).read_text(encoding="utf-8"),
            }
        )
        stdout = self.outcomes.pop(0)
        return subprocess.CompletedProcess(args, 0, stdout=stdout, stderr="")


def _provider(runner, tmp_path, sleeps=None):
    sleeps = [] if sleeps is None else sleeps
    return ClaudeCodeProvider("claude", cwd=tmp_path, runner=runner, sleep=sleeps.append)


def test_maps_cli_json_to_completion(tmp_path, monkeypatch):
    monkeypatch.setenv("CLAUDECODE", "1")
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "abc")
    monkeypatch.setenv("KEEP_ME", "yes")
    runner = FakeRunner([_result()])
    completion = _provider(runner, tmp_path).complete(
        "claude-haiku-4-5", "instructions", "user body", "THE DIFF"
    )

    assert completion.text == '{"findings": []}'
    assert completion.input_tokens == 1020
    assert completion.cached_input_tokens == 0
    assert completion.output_tokens == 45
    assert completion.latency_s == pytest.approx(3.1)
    assert completion.model_id == "claude-haiku-4-5"

    call = runner.calls[0]
    assert call["input"] == "user body"
    assert call["system"] == "THE DIFF\n\ninstructions"
    assert call["cwd"] == str(tmp_path)
    for flag in ("-p", "--output-format", "--tools", "--max-turns", "--bare"):
        assert flag in call["args"]
    assert call["args"][call["args"].index("--model") + 1] == "claude-haiku-4-5"
    assert "CLAUDECODE" not in call["env"]
    assert "CLAUDE_CODE_SESSION_ID" not in call["env"]
    assert call["env"]["KEEP_ME"] == "yes"


def test_cache_read_tokens_come_from_usage(tmp_path):
    usage = {
        "input_tokens": 50,
        "cache_creation_input_tokens": 0,
        "cache_read_input_tokens": 900,
        "output_tokens": 10,
    }
    runner = FakeRunner([_result(usage=usage, duration_api_ms=0, modelUsage={})])
    completion = _provider(runner, tmp_path).complete("claude-sonnet-5", "", "u", "diff")
    assert completion.cached_input_tokens == 900
    assert completion.input_tokens == 950
    assert completion.model_id == "claude-sonnet-5"
    assert completion.latency_s > 0


def test_system_prompt_file_is_removed_after_the_call(tmp_path):
    runner = FakeRunner([_result()])
    _provider(runner, tmp_path).complete("claude-haiku-4-5", "", "u", "diff")
    system_file = runner.calls[0]["args"][runner.calls[0]["args"].index("--system-prompt-file") + 1]
    assert not Path(system_file).exists()


def test_transient_error_is_retried_then_succeeds(tmp_path):
    rate_limited = _result("Rate limit reached, try again later", is_error=True)
    runner = FakeRunner([rate_limited, _result()])
    sleeps: list[float] = []
    completion = _provider(runner, tmp_path, sleeps).complete("claude-haiku-4-5", "", "u", "d")
    assert completion.text == '{"findings": []}'
    assert len(runner.calls) == 2
    assert sleeps == [5.0]


def test_hard_error_raises_without_retry(tmp_path):
    runner = FakeRunner([_result("Not logged in · Please run /login", is_error=True)])
    sleeps: list[float] = []
    with pytest.raises(RuntimeError, match="Not logged in"):
        _provider(runner, tmp_path, sleeps).complete("claude-haiku-4-5", "", "u", "d")
    assert len(runner.calls) == 1
    assert sleeps == []


def test_parse_result_tolerates_leading_noise():
    noisy = 'warning: something\n{"type": "result", "result": "ok", "is_error": false}\n'
    assert _parse_result(noisy)["result"] == "ok"
    assert _parse_result("") is None
    assert _parse_result("not json at all") is None
