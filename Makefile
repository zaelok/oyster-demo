# PROVIDER defaults to mock so nothing here can spend money by accident.
# Real API runs require PROVIDER=anthropic explicitly.
PROVIDER ?= mock

install:      ; uv sync
test:         ; uv run pytest -q
lint:         ; uv run ruff check . && uv run ruff format --check .
calibrate:    ; uv run python -m oyster.cli calibrate --provider $(PROVIDER)
eval:         ; uv run python -m oyster.cli eval --provider $(PROVIDER)
eval-mock:    ; $(MAKE) eval PROVIDER=mock

.PHONY: install test lint calibrate eval eval-mock
