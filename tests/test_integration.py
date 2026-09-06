"""Cross-module rules from the build spec: every package has an __init__, no module imports
another module's internals, and the CLI runs end to end offline."""

import ast
import subprocess
import sys
from pathlib import Path

from tests.conftest import CORPUS_DIR

ROOT = Path(__file__).resolve().parent.parent
PACKAGE = ROOT / "oyster"

# Allowed intra-package imports per module, mirroring the task graph in spec §14. A module may
# import from oyster.types and oyster.config freely; anything else must be listed here.
ALLOWED: dict[str, set[str]] = {
    "oyster": set(),
    "oyster.types": set(),
    "oyster.config": set(),
    "oyster.prompts": {"oyster.prompts.templates"},
    "oyster.prompts.templates": set(),
    "oyster.graph": {"oyster.prompts.templates"},
    "oyster.graph.catalog": set(),
    "oyster.cost": set(),
    "oyster.providers": {
        "oyster.providers.mock_provider",
        "oyster.providers.anthropic_provider",
        "oyster.providers.recording_provider",
    },
    "oyster.providers.mock_provider": {"oyster.cost"},
    "oyster.providers.anthropic_provider": set(),
    "oyster.providers.recording_provider": {"oyster.providers.mock_provider"},
    "oyster.corpus": set(),
    "oyster.matching": set(),
    "oyster.executor": {"oyster.cost", "oyster.graph", "oyster.prompts"},
    "oyster.selector": {"oyster.cost"},
    "oyster.evaluation": {
        "oyster.cost",
        "oyster.executor",
        "oyster.graph.catalog",
        "oyster.matching",
    },
}
ALWAYS = {"oyster.types", "oyster.config"}


def _module_name(path: Path) -> str:
    relative = path.relative_to(ROOT).with_suffix("")
    parts = list(relative.parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _imports(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name, None
        elif isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                yield node.module, alias.name


def test_every_module_directory_has_an_init():
    for directory in [PACKAGE, *[p for p in PACKAGE.rglob("*") if p.is_dir()]]:
        if directory.name in {"cases", "__pycache__"}:
            continue
        assert (directory / "__init__.py").exists(), f"{directory} lacks __init__.py"


def test_no_module_imports_another_modules_internals():
    violations = []
    for path in sorted(PACKAGE.rglob("*.py")):
        module = _module_name(path)
        if module == "oyster.cli":
            continue  # the CLI wires every public API together by design
        allowed = ALLOWED[module] | ALWAYS
        for target, name in _imports(path):
            if not target.startswith("oyster"):
                continue
            if target not in allowed:
                violations.append(f"{module} imports {target}")
            if name is not None and name.startswith("_"):
                violations.append(f"{module} imports private name {target}.{name}")
    assert violations == []


def test_cli_only_imports_public_names():
    for target, name in _imports(PACKAGE / "cli.py"):
        if target.startswith("oyster") and name:
            assert not name.startswith("_"), f"cli imports private {target}.{name}"


def test_cli_eval_mock_runs_offline_end_to_end(tmp_path):
    out = tmp_path / "results.md"
    json_out = tmp_path / "results.json"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "oyster.cli",
            "eval",
            "--provider",
            "mock",
            "--corpus",
            str(CORPUS_DIR),
            "--fixtures",
            str(tmp_path / "fixtures"),
            "--out",
            str(out),
            "--json-out",
            str(json_out),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    text = out.read_text(encoding="utf-8")
    assert text.count("| n/a |") == 3
    assert json_out.exists()
    assert "Wrote" in completed.stdout


def test_cli_select_reports_no_priors_without_calibration(tmp_path):
    priors = tmp_path / "priors.json"
    priors.write_text('{"corpus_size": 0, "catch_rate": [], "mean_cost": []}')
    completed = subprocess.run(
        [sys.executable, "-m", "oyster.cli", "select", "--priors", str(priors)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert "No feasible path: no priors" in completed.stdout


def test_anthropic_provider_refuses_without_key(tmp_path):
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "oyster.cli",
            "eval",
            "--provider",
            "anthropic",
            "--corpus",
            str(CORPUS_DIR),
            "--yes",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={**__import__("os").environ, "OYSTER_ANTHROPIC_API_KEY": ""},
    )
    assert completed.returncode == 2
    assert "OYSTER_ANTHROPIC_API_KEY" in completed.stdout
