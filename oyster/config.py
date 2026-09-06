"""Settings and model bindings. Rates are placeholders: a human verifies them against
published pricing before any real API run, and results.md records what was used."""

from pydantic_settings import BaseSettings, SettingsConfigDict

from oyster.types import ModelBinding


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="OYSTER_", extra="ignore")

    anthropic_api_key: str = ""
    cheap_model_id: str = "claude-haiku-4-5-20251001"
    strong_model_id: str = "claude-sonnet-4-5"
    cheap_rate_in: float = 1.00  # dollars per 1M tokens, VERIFY before real runs
    cheap_rate_out: float = 5.00
    strong_rate_in: float = 3.00
    strong_rate_out: float = 15.00
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
