"""ModelProvider implementations. The mock replays fixtures offline; the anthropic provider
spends money and is only ever selected explicitly."""

from oyster.providers.anthropic_provider import AnthropicProvider
from oyster.providers.claude_code_provider import ClaudeCodeProvider
from oyster.providers.mock_provider import MockProvider, fixture_key
from oyster.providers.recording_provider import RecordingProvider

__all__ = [
    "AnthropicProvider",
    "ClaudeCodeProvider",
    "MockProvider",
    "RecordingProvider",
    "fixture_key",
]
