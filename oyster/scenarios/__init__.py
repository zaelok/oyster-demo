"""Scenario plugins. Each module owns its task and output types, prompts, parser, filter and
scorer, and exposes one `Scenario` instance. The engine imports nothing scenario-specific
except the default (code review) in the executor and evaluation entry points."""
