"""Settings and model bindings. The defaults are the model ids and list rates every committed
run used, so a bare clone replays the committed fixtures (fixture keys include the model id);
a human verifies the rates against published pricing before any new paid run, and results.md
records what was used."""

from pydantic_settings import BaseSettings, SettingsConfigDict

from oyster.types import ModelBinding


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="OYSTER_", extra="ignore")

    anthropic_api_key: str = ""
    # `claude setup-token` output; lets --provider claude-code run from any shell or
    # session without the variable being exported there. Never committed (.env is ignored).
    claude_code_oauth_token: str = ""
    # Thinking effort per model for --provider claude-code: "" leaves the CLI's default
    # (adaptive thinking, which on review prompts runs to thousands of tokens), "none"
    # disables thinking (MAX_THINKING_TOKENS=0), low|medium|high|xhigh|max map to --effort.
    # The API provider ignores these; the results header records them.
    cheap_effort: str = ""
    strong_effort: str = ""
    cheap_model_id: str = "claude-haiku-4-5"
    strong_model_id: str = "claude-sonnet-5"
    cheap_rate_in: float = 1.00  # dollars per 1M tokens, Anthropic list rates as of 2026-09
    cheap_rate_out: float = 5.00
    strong_rate_in: float = 2.00
    strong_rate_out: float = 10.00
    cache_discount: float = 0.90
    budget_dollars: float = 1.00
    latency_tolerance_s: float = 120.0
    corpus_dir: str = "oyster/corpus/cases"
    results_path: str = "results.md"
    priors_path: str = "priors.json"


settings = Settings()

BINDINGS: dict[str, ModelBinding] = {
    "cheap-model": ModelBinding(
        "cheap-model",
        settings.cheap_model_id,
        settings.cheap_rate_in,
        settings.cheap_rate_out,
        settings.cache_discount,
    ),
    "strong-model": ModelBinding(
        "strong-model",
        settings.strong_model_id,
        settings.strong_rate_in,
        settings.strong_rate_out,
        settings.cache_discount,
    ),
}
