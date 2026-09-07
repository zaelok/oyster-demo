"""Run calibrate, eval and select for several model configurations and summarize them.

Each configuration binds cheap-model and strong-model to concrete model ids and the
published per-1M-token rates, runs `oyster.cli calibrate` then `eval` in a subprocess with
the OYSTER_* environment overrides (config.py reads them at import), and writes everything
under results/<config>/. A combined results/summary.md compares the configurations.

    python -m tools.run_matrix                 # all configs, paid, asks nothing (uses --yes)
    python -m tools.run_matrix --only haiku45-sonnet5
    python -m tools.run_matrix --provider mock  # offline dry run of the plumbing

Rates below are Anthropic first-party API prices as cached in the claude-api reference on
2026-06-24. Cache discount stays at the spec default 0.9 (cache reads at 10% of input);
Claude Fable 5.1 reads cache cheaper than that, so its cached tokens are slightly overpriced
here, which is the conservative direction.
"""

import argparse
import json
import os
import statistics
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ModelSpec:
    model_id: str
    rate_in: float
    rate_out: float


HAIKU_45 = ModelSpec("claude-haiku-4-5", 1.00, 5.00)
SONNET_5 = ModelSpec("claude-sonnet-5", 2.00, 10.00)
OPUS_5 = ModelSpec("claude-opus-5", 5.00, 25.00)
FABLE_51 = ModelSpec("claude-fable-5-1", 10.00, 50.00)

CONFIGS: dict[str, tuple[ModelSpec, ModelSpec]] = {
    "haiku45-sonnet5": (HAIKU_45, SONNET_5),
    "sonnet5-opus5": (SONNET_5, OPUS_5),
    "haiku45-fable51": (HAIKU_45, FABLE_51),
}


def config_key(name: str, cheap_effort: str, strong_effort: str) -> str:
    """Output directory and fixture directory name: the model pair plus any non-default
    effort, so two runs of the same pair under different thinking settings never share a
    fixture or a results file."""
    suffix = ""
    if cheap_effort:
        suffix += f"-cheap{cheap_effort}"
    if strong_effort:
        suffix += f"-strong{strong_effort}"
    return name + suffix


def base_name(key: str) -> str:
    """The model-pair name behind a config key, effort suffixes stripped."""
    for marker in ("-cheap", "-strong"):
        if marker in key:
            key = key.split(marker, 1)[0]
    return key


def env_for(
    cheap: ModelSpec, strong: ModelSpec, cheap_effort: str = "", strong_effort: str = ""
) -> dict[str, str]:
    env = dict(os.environ)
    env.update(
        {
            "OYSTER_CHEAP_EFFORT": cheap_effort,
            "OYSTER_STRONG_EFFORT": strong_effort,
            "OYSTER_CHEAP_MODEL_ID": cheap.model_id,
            "OYSTER_CHEAP_RATE_IN": str(cheap.rate_in),
            "OYSTER_CHEAP_RATE_OUT": str(cheap.rate_out),
            "OYSTER_STRONG_MODEL_ID": strong.model_id,
            "OYSTER_STRONG_RATE_IN": str(strong.rate_in),
            "OYSTER_STRONG_RATE_OUT": str(strong.rate_out),
            # The child's stdout/stderr go to run.log; keep them UTF-8 on Windows, where a
            # redirected Python stream otherwise uses the ANSI code page.
            "PYTHONUTF8": "1",
            "PYTHONIOENCODING": "utf-8",
        }
    )
    return env


def run_config(
    name: str,
    provider: str,
    out_root: Path,
    corpus: Sequence[str],
    budget: float,
    latency: float,
    workers: int = 1,
    cheap_effort: str = "",
    strong_effort: str = "",
) -> int:
    cheap, strong = CONFIGS[name]
    key = config_key(name, cheap_effort, strong_effort)
    out = out_root / key
    out.mkdir(parents=True, exist_ok=True)
    env = env_for(cheap, strong, cheap_effort, strong_effort)
    # Fixtures per provider and configuration: a rerun of the same command replays what was
    # already answered and only makes the missing calls, so an interrupted run resumes.
    common = [
        "--provider",
        provider,
        "--yes",
        "--record",
        f"fixtures/{provider}/{key}",
        "--workers",
        str(workers),
    ]
    for directory in corpus:
        common += ["--corpus", directory]
    steps = [
        ["calibrate", *common, "--priors-out", str(out / "priors.json")],
        [
            "eval",
            *common,
            "--out",
            str(out / "results.md"),
            "--json-out",
            str(out / "results.json"),
        ],
        [
            "select",
            "--priors",
            str(out / "priors.json"),
            "--budget",
            str(budget),
            "--latency",
            str(latency),
        ],
    ]
    log = out / "run.log"
    with log.open("w", encoding="utf-8") as handle:
        for step in steps:
            command = [sys.executable, "-m", "oyster.cli", *step]
            handle.write(f"$ {' '.join(command)}\n")
            handle.flush()
            completed = subprocess.run(
                command,
                env=env,
                stdout=handle,
                stderr=subprocess.STDOUT,
                encoding="utf-8",
                check=False,
            )
            handle.write(f"[exit {completed.returncode}]\n\n")
            if completed.returncode != 0:
                print(f"{name}: {step[0]} failed with exit {completed.returncode}, see {log}")
                return completed.returncode
    print(f"{name}: done, see {out}")
    return 0


def _per_path(results_json: Path) -> dict[str, dict]:
    data = json.loads(results_json.read_text(encoding="utf-8"))
    by_path: dict[str, dict] = {}
    reports = {(r["path_id"], r["case_id"]): r for r in data["reports"]}
    for result in data["results"]:
        row = by_path.setdefault(
            result["path_id"],
            {
                "dollars": 0.0,
                "latencies": [],
                "strict": 0,
                "loose": 0,
                "seeded": 0,
                "fps": 0,
                "halted": 0,
                "parse_failed": 0,
            },
        )
        row["dollars"] += result["cost"]["dollars"]
        row["latencies"].append(result["cost"]["latency_s"])
        row["halted"] += 1 if result.get("halted_reason") else 0
        row["parse_failed"] += sum(1 for n in result["node_results"] if n["parse_failed"])
        report = reports[(result["path_id"], result["case_id"])]
        row["strict"] += len(report["caught_strict"])
        row["loose"] += len(report["caught_loose"])
        row["seeded"] += len(report["caught_loose"]) + len(report["missed"])
        row["fps"] += report["false_positives"]
    return by_path


def summarize(out_root: Path, names: Sequence[str]) -> str:
    lines = [
        "# OYSTER results across model configurations",
        "",
        (
            "| config | cheap-model | strong-model | path | $ total | strict | loose | seeded | "
            "$/bug (strict) | false pos | p50 latency | parse fails |"
        ),
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for name in names:
        results_json = out_root / name / "results.json"
        if not results_json.exists():
            lines.append(f"| {name} | | | (no results) | | | | | | | | |")
            continue
        cheap, strong = CONFIGS[base_name(name)]
        for path_id, row in _per_path(results_json).items():
            per_bug = "n/a" if row["strict"] == 0 else f"${row['dollars'] / row['strict']:.4f}"
            p50 = f"{statistics.median(row['latencies']):.1f}s" if row["latencies"] else "n/a"
            lines.append(
                f"| {name} | {cheap.model_id} | {strong.model_id} | {path_id} | "
                f"${row['dollars']:.4f} | {row['strict']} | {row['loose']} | {row['seeded']} | "
                f"{per_bug} | {row['fps']} | {p50} | {row['parse_failed']} |"
            )
    lines += ["", "## Selection under the default budget", ""]
    for name in names:
        log = out_root / name / "run.log"
        if not log.exists():
            continue
        text = log.read_text(encoding="utf-8", errors="replace")
        marker = "oyster.cli select"
        if marker in text:
            tail = text[text.rfind(marker) :].splitlines()[1:]
            picked = [line for line in tail if line and not line.startswith("[exit")]
            lines.append(f"- **{name}**: " + " ".join(line.strip() for line in picked[:5]))
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="run_matrix", description=__doc__)
    parser.add_argument(
        "--provider", choices=["mock", "anthropic", "claude-code"], default="claude-code"
    )
    parser.add_argument("--only", nargs="*", default=list(CONFIGS), help="config names")
    parser.add_argument("--out", default="results")
    parser.add_argument(
        "--corpus",
        action="append",
        default=None,
        help="case directory; repeatable (default oyster/corpus/cases)",
    )
    parser.add_argument("--budget", type=float, default=1.00)
    parser.add_argument("--latency", type=float, default=120.0)
    parser.add_argument("--summary-only", action="store_true")
    parser.add_argument("--workers", type=int, default=1, help="concurrent cases per path")
    parser.add_argument(
        "--cheap-effort",
        default="",
        help="claude-code only: none | low | medium | high | xhigh | max (default: CLI default)",
    )
    parser.add_argument("--strong-effort", default="", help="claude-code only: as above")
    args = parser.parse_args(argv)

    out_root = Path(args.out)
    corpus = args.corpus or ["oyster/corpus/cases"]
    unknown = [name for name in args.only if name not in CONFIGS]
    if unknown:
        print(f"unknown config(s): {unknown}; choose from {list(CONFIGS)}", file=sys.stderr)
        return 2
    status = 0
    if not args.summary_only:
        for name in args.only:
            status |= run_config(
                name,
                args.provider,
                out_root,
                corpus,
                args.budget,
                args.latency,
                args.workers,
                args.cheap_effort,
                args.strong_effort,
            )
    keys = [config_key(name, args.cheap_effort, args.strong_effort) for name in args.only]
    if args.summary_only:
        # Summarize every configuration that has results under out_root, whatever effort
        # settings produced them, so one summary compares them side by side.
        keys = [
            p.name
            for p in sorted(out_root.iterdir())
            if (p / "results.json").exists() and base_name(p.name) in CONFIGS
        ]
    summary = summarize(out_root, keys)
    out_root.mkdir(parents=True, exist_ok=True)
    (out_root / "summary.md").write_text(summary, encoding="utf-8")
    print(summary)
    return status


if __name__ == "__main__":
    sys.exit(main())
