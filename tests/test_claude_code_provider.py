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
    for flag in ("-p", "--output-format", "--tools", "--max-turns"):
        assert flag in call["args"]
    assert "--bare" not in call["args"]  # no token in the environment: stored login must be read
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


def test_clean_env_keeps_the_oauth_token_and_drops_the_desktop_app_variables(monkeypatch):
    from oyster.providers.claude_code_provider import _clean_env

    monkeypatch.setenv("CLAUDE_CODE_OAUTH_TOKEN", "sk-ant-oat01-x")
    monkeypatch.setenv("CLAUDE_CODE_ENTRYPOINT", "desktop")
    monkeypatch.setenv("CLAUDECODE", "1")
    env = _clean_env()
    assert env["CLAUDE_CODE_OAUTH_TOKEN"] == "sk-ant-oat01-x"
    assert "CLAUDE_CODE_ENTRYPOINT" not in env
    assert "CLAUDECODE" not in env


def test_never_bare_and_api_keys_never_reach_the_cli(tmp_path, monkeypatch):
    """Bare mode authenticates with an API key only, so it would silently defeat the
    subscription route; the API key itself is removed for the same reason."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-api03-x")
    monkeypatch.setenv("ANTHROPIC_BASE_URL", "http://127.0.0.1:1/proxy")
    monkeypatch.delenv("CLAUDE_CODE_OAUTH_TOKEN", raising=False)
    runner = FakeRunner([_result(), _result()])
    provider = _provider(runner, tmp_path)
    provider.complete("claude-haiku-4-5", "", "user", "diff")
    assert "--bare" not in runner.calls[0]["args"]
    assert "ANTHROPIC_API_KEY" not in runner.calls[0]["env"]
    assert "ANTHROPIC_BASE_URL" not in runner.calls[0]["env"]
    monkeypatch.setenv("CLAUDE_CODE_OAUTH_TOKEN", "sk-ant-oat01-x")
    provider.complete("claude-haiku-4-5", "", "user", "diff")
    assert "--bare" not in runner.calls[1]["args"]
    assert runner.calls[1]["env"]["CLAUDE_CODE_OAUTH_TOKEN"] == "sk-ant-oat01-x"


def test_not_logged_in_error_carries_the_login_hint(tmp_path):
    runner = FakeRunner(
        [json.dumps({"type": "result", "is_error": True, "result": "Not logged in"})]
    )
    with pytest.raises(RuntimeError, match="claude auth login"):
        _provider(runner, tmp_path).complete("claude-haiku-4-5", "", "user", "diff")


def test_token_from_settings_reaches_the_cli_and_enables_bare_mode(tmp_path, monkeypatch):
    monkeypatch.delenv("CLAUDE_CODE_OAUTH_TOKEN", raising=False)
    runner = FakeRunner([_result()])
    provider = ClaudeCodeProvider(
        "claude", cwd=tmp_path, runner=runner, sleep=lambda s: None, oauth_token="sk-ant-oat01-t"
    )
    provider.complete("claude-haiku-4-5", "", "user", "diff")
    assert runner.calls[0]["env"]["CLAUDE_CODE_OAUTH_TOKEN"] == "sk-ant-oat01-t"
    assert "--bare" not in runner.calls[0]["args"]


def test_effort_none_disables_thinking_and_levels_go_to_the_flag(tmp_path, monkeypatch):
    monkeypatch.delenv("MAX_THINKING_TOKENS", raising=False)
    runner = FakeRunner([_result(), _result(), _result()])
    provider = ClaudeCodeProvider(
        "claude",
        cwd=tmp_path,
        runner=runner,
        sleep=lambda s: None,
        effort={"claude-haiku-4-5": "none", "claude-sonnet-5": "medium", "claude-opus-5": ""},
    )
    provider.complete("claude-haiku-4-5", "", "u", "d")
    provider.complete("claude-sonnet-5", "", "u", "d")
    provider.complete("claude-opus-5", "", "u", "d")
    haiku, sonnet, opus = runner.calls
    assert haiku["env"]["MAX_THINKING_TOKENS"] == "0" and "--effort" not in haiku["args"]
    assert sonnet["args"][sonnet["args"].index("--effort") + 1] == "medium"
    assert "MAX_THINKING_TOKENS" not in sonnet["env"]
    assert "--effort" not in opus["args"] and "MAX_THINKING_TOKENS" not in opus["env"]
    with pytest.raises(ValueError, match="effort for"):
        ClaudeCodeProvider("claude", cwd=tmp_path, runner=runner, effort={"m": "turbo"})
