"""Subscription-backed provider: shells out to the Claude Code CLI in print mode.

No API key and no API billing. The CLI authenticates with the user's Claude subscription:
either the stored login (`claude auth login`, read from the keychain) or a `claude setup-token`
token in CLAUDE_CODE_OAUTH_TOKEN. `--bare` mode, which skips hooks, plugins and keychain
reads, is used only when the token variable is present, because bare mode never reads the
stored login. ANTHROPIC_API_KEY is removed from the CLI's environment on purpose: with it set
the CLI would bill the API, and the API route is `--provider anthropic`. Its JSON result
carries the token usage the API actually reported, so the pricing formula prices the run at
API list rates: the table shows what the run would have cost through the API, not what was
charged, which for a subscription is nothing beyond quota.

Read the numbers with these differences from a raw API call in mind:
- the CLI wraps the prompt in its own scaffolding, so input token counts include it;
- the cached diff plus any system text go through --system-prompt-file; --tools "" removes
  every tool and --max-turns 1 forbids an agentic loop, so one call is one completion;
- latency is the CLI's duration_api_ms (time spent in the model), not process spawn time;
- models that think by default (Sonnet 5, Opus 5, Fable 5.1) report thinking tokens inside
  output_tokens, exactly as the API bills them.
"""

import json
import os
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from oyster.types import Completion

DEFAULT_CLI_CANDIDATES = (
    "claude",
    r"C:\Users\{user}\AppData\Roaming\Claude\claude-code\2.1.260\claude.exe",
)
# Environment the desktop app sets on its child sessions; a nested CLI must not inherit it.
# The one CLAUDE_CODE_* variable that must survive is the subscription token from
# `claude setup-token`, or the CLI would report "Not logged in" inside the run.
STRIPPED_ENV_PREFIXES = ("CLAUDECODE", "CLAUDE_CODE_", "CLAUDE_PID", "CLAUDE_EFFORT")
KEPT_ENV = ("CLAUDE_CODE_OAUTH_TOKEN",)
# API credentials would make the CLI bill the API instead of the subscription.
STRIPPED_ENV_EXACT = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN")
TOKEN_ENV = "CLAUDE_CODE_OAUTH_TOKEN"
LOGIN_HINT = (
    " (the CLI is not authenticated: run `claude auth login` once, or `claude setup-token` "
    "and export CLAUDE_CODE_OAUTH_TOKEN in the shell that runs OYSTER)"
)
MAX_ATTEMPTS = 3
BACKOFF_S = (5.0, 15.0, 45.0)
TRANSIENT_MARKERS = ("rate limit", "overloaded", "529", "usage limit", "try again")


def find_cli() -> str:
    for candidate in DEFAULT_CLI_CANDIDATES:
        candidate = candidate.format(user=os.environ.get("USERNAME", ""))
        if os.path.isfile(candidate):
            return candidate
        if os.sep not in candidate and _which(candidate):
            return candidate
    raise FileNotFoundError("claude CLI not found; pass cli= or put `claude` on PATH")


def _which(name: str) -> str | None:
    import shutil

    return shutil.which(name)


def _clean_env(oauth_token: str | None = None) -> dict[str, str]:
    env = {
        key: value
        for key, value in os.environ.items()
        if key in KEPT_ENV
        or (not key.startswith(STRIPPED_ENV_PREFIXES) and key not in STRIPPED_ENV_EXACT)
    }
    if oauth_token:
        env[TOKEN_ENV] = oauth_token
    return env


class ClaudeCodeProvider:
    def __init__(
        self,
        cli: str | None = None,
        *,
        cwd: Path | None = None,
        runner: Callable[..., subprocess.CompletedProcess] = subprocess.run,
        sleep: Callable[[float], None] = time.sleep,
        extra_args: tuple[str, ...] = (),
        oauth_token: str | None = None,
    ):
        self.cli = cli or find_cli()
        # A token from settings (.env) or the environment; either way the CLI gets it in
        # CLAUDE_CODE_OAUTH_TOKEN and runs in --bare mode. Without one, the stored login is
        # read, which --bare would skip.
        self.oauth_token = oauth_token or None
        self.cwd = Path(cwd) if cwd else Path(tempfile.mkdtemp(prefix="oyster-claude-code-"))
        self._runner = runner
        self._sleep = sleep
        self.extra_args = extra_args

    def complete(
        self,
        model_id: str,
        system: str,
        user: str,
        cached_prefix: str | None = None,
    ) -> Completion:
        system_prompt = cached_prefix or ""
        if system:
            system_prompt = f"{system_prompt}\n\n{system}" if system_prompt else system

        with tempfile.NamedTemporaryFile(
            "w", suffix=".txt", prefix="oyster-system-", delete=False, encoding="utf-8"
        ) as handle:
            handle.write(system_prompt)
            system_file = handle.name
        try:
            data, wall_s = self._call_with_retry(model_id, user, system_file)
        finally:
            Path(system_file).unlink(missing_ok=True)

        usage: dict[str, Any] = data.get("usage") or {}
        cache_read = int(usage.get("cache_read_input_tokens") or 0)
        cache_write = int(usage.get("cache_creation_input_tokens") or 0)
        base_input = int(usage.get("input_tokens") or 0)
        duration_ms = data.get("duration_api_ms") or 0
        latency_s = duration_ms / 1000.0 if duration_ms else wall_s
        stop_reason = data.get("stop_reason")
        if stop_reason not in (None, "end_turn", "stop_sequence"):
            print(f"claude_code_provider: {model_id} stop_reason={stop_reason}", file=sys.stderr)
        return Completion(
            text=str(data.get("result") or ""),
            input_tokens=base_input + cache_read + cache_write,
            cached_input_tokens=cache_read,
            output_tokens=int(usage.get("output_tokens") or 0),
            latency_s=latency_s,
            model_id=_model_used(data, model_id),
        )

    def _token(self) -> str | None:
        return self.oauth_token or os.environ.get(TOKEN_ENV) or None

    def _call_with_retry(
        self, model_id: str, user: str, system_file: str
    ) -> tuple[dict[str, Any], float]:
        args = [
            self.cli,
            "-p",
            "--model",
            model_id,
            "--output-format",
            "json",
            "--system-prompt-file",
            system_file,
            "--tools",
            "",
            "--max-turns",
            "1",
            "--no-session-persistence",
            *(("--bare",) if self._token() else ()),
            *self.extra_args,
        ]
        last_error = ""
        for attempt in range(MAX_ATTEMPTS):
            start = time.perf_counter()
            completed = self._runner(
                args,
                input=user,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                cwd=str(self.cwd),
                env=_clean_env(self._token()),
            )
            wall_s = time.perf_counter() - start
            data = _parse_result(completed.stdout)
            if data is None:
                last_error = (
                    f"exit {completed.returncode}, no JSON result; "
                    f"stderr: {completed.stderr.strip()[:300]}"
                )
            elif data.get("is_error"):
                last_error = str(data.get("result") or data)
            else:
                return data, wall_s
            transient = any(marker in last_error.lower() for marker in TRANSIENT_MARKERS)
            if transient and attempt < MAX_ATTEMPTS - 1:
                self._sleep(BACKOFF_S[attempt])
                continue
            break
        if "not logged in" in last_error.lower():
            last_error += LOGIN_HINT
        raise RuntimeError(f"claude-code call failed for {model_id}: {last_error}")


def _parse_result(stdout: str) -> dict[str, Any] | None:
    """The result is one JSON object; tolerate leading noise by scanning for the last line
    that parses as an object with type == result."""
    text = (stdout or "").strip()
    if not text:
        return None
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass
    for line in reversed(text.splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(data, dict) and data.get("type") == "result":
                return data
    return None


def _model_used(data: dict[str, Any], requested: str) -> str:
    model_usage = data.get("modelUsage")
    if isinstance(model_usage, dict) and len(model_usage) == 1:
        return str(next(iter(model_usage)))
    return requested
