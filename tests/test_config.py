import importlib

import oyster.config as config_module
from oyster.config import BINDINGS, Settings


def test_import_without_env_yields_two_bindings():
    assert set(BINDINGS) == {"cheap-model", "strong-model"}
    assert BINDINGS["cheap-model"].alias == "cheap-model"
    assert BINDINGS["strong-model"].model_id == config_module.settings.strong_model_id


def test_env_var_overrides_budget(monkeypatch):
    monkeypatch.setenv("OYSTER_BUDGET_DOLLARS", "5")
    assert Settings(_env_file=None).budget_dollars == 5.0
    reloaded = importlib.reload(config_module)
    try:
        assert reloaded.settings.budget_dollars == 5.0
    finally:
        monkeypatch.delenv("OYSTER_BUDGET_DOLLARS")
        importlib.reload(config_module)


def test_defaults_are_the_spec_placeholders():
    settings = Settings(_env_file=None)
    assert settings.budget_dollars == 1.0
    assert settings.latency_tolerance_s == 120.0
    assert settings.cache_discount == 0.9
    assert settings.corpus_dir == "oyster/corpus/cases"
