"""Command line entry point.

    python -m oyster.cli calibrate --provider {mock,anthropic} [--corpus DIR ...]
    python -m oyster.cli eval      --provider {mock,anthropic} [--corpus DIR ...] [--out results.md]
    python -m oyster.cli select    --budget 1.00 --latency 120 [--priors priors.json]

The mock provider is the default and spends nothing. The anthropic provider requires
OYSTER_ANTHROPIC_API_KEY, prints a cost estimate and asks for confirmation unless --yes is
passed. Paid completions are recorded as mock fixtures by default so the run can be replayed
offline afterwards.
"""

import argparse
import json
import os
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path as FsPath

from rich.console import Console
from rich.table import Table

from oyster.config import BINDINGS, settings
from oyster.conversation import collect_pending, ingest, write_pack
from oyster.corpus import load_corpora
from oyster.cost import estimate_tokens
from oyster.evaluation import (
    calibrate,
    calibration_paths,
    evaluate,
    priors_from_json,
    priors_to_json,
    render_results,
    results_to_json,
)
from oyster.executor import BudgetHook
from oyster.graph import validate_path
from oyster.graph.catalog import CATALOG
from oyster.prompts import render
from oyster.providers import (
    AnthropicProvider,
    ClaudeCodeProvider,
    MockProvider,
    RecordingProvider,
)
from oyster.selector import select
from oyster.types import CorpusCase, Cost, ModelProvider, Path, Priors

DEFAULT_FIXTURES = "fixtures/mock"
# Pre-run estimate only. Billing always uses the token counts the API reports.
ASSUMED_OUTPUT_TOKENS_PER_CALL = 1000

console = Console()


def _corpus_dirs(args: argparse.Namespace) -> list[FsPath]:
    """--corpus may be repeated to evaluate several tiers as one corpus; the default is the
    reviewed tier alone, so the committed table replays unchanged."""
    return [FsPath(directory) for directory in (args.corpus or [settings.corpus_dir])]


def _corpus_commit(corpus_dirs: Sequence[FsPath]) -> str:
    try:
        completed = subprocess.run(
            ["git", "log", "-1", "--format=%H", "--", *[str(d) for d in corpus_dirs]],
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return completed.stdout.strip() or "uncommitted"


def _estimate_dollars(cases: Sequence[CorpusCase], paths: Sequence[Path]) -> float:
    total = 0.0
    for case in cases:
        for path in paths:
            for node in path.nodes:
                binding = BINDINGS[node.model_alias]
                tokens_in = estimate_tokens(render(node.prompt_key, case.diff))
                total += (
                    tokens_in * binding.rate_in + ASSUMED_OUTPUT_TOKENS_PER_CALL * binding.rate_out
                ) / 1e6
    return total


def _make_provider(
    args: argparse.Namespace, cases: Sequence[CorpusCase], paths: Sequence[Path]
) -> ModelProvider:
    if args.provider == "mock":
        return MockProvider(FsPath(args.fixtures))

    if args.provider == "claude-code":
        calls = sum(len(path.nodes) for path in paths) * len(cases)
        console.print(
            f"About to make up to {calls} calls through the Claude Code CLI on your "
            "subscription (no API billing; counts against subscription usage limits). "
            "Dollar figures in the table are API list prices for the tokens used."
        )
        if not args.yes:
            answer = input("Proceed? [y/N] ")
            if answer.strip().lower() not in {"y", "yes"}:
                console.print("Aborted.")
                sys.exit(1)
        provider: ModelProvider = ClaudeCodeProvider(
            oauth_token=settings.claude_code_oauth_token or None
        )
        if args.record:
            provider = RecordingProvider(provider, FsPath(args.record))
            console.print(f"Recording completions as mock fixtures under {args.record}")
        return provider

    if not settings.anthropic_api_key and not os.environ.get("ANTHROPIC_API_KEY"):
        console.print(
            "[red]Neither OYSTER_ANTHROPIC_API_KEY nor ANTHROPIC_API_KEY is set; refusing to "
            "run the anthropic provider."
        )
        sys.exit(2)

    estimate = _estimate_dollars(cases, paths)
    calls = sum(len(path.nodes) for path in paths) * len(cases)
    console.print(
        f"About to make up to {calls} paid API calls (plus JSON-repair retries). "
        f"Rough estimate: ${estimate:.2f}, assuming {ASSUMED_OUTPUT_TOKENS_PER_CALL} output "
        "tokens per call and no cache hits. Rates in oyster/config.py are placeholders: "
        "verify them against published pricing first."
    )
    if not args.yes:
        answer = input("Proceed? [y/N] ")
        if answer.strip().lower() not in {"y", "yes"}:
            console.print("Aborted.")
            sys.exit(1)

    provider: ModelProvider = AnthropicProvider(settings.anthropic_api_key)
    if args.record:
        provider = RecordingProvider(provider, FsPath(args.record))
        console.print(f"Recording completions as mock fixtures under {args.record}")
    return provider


def _load_corpus(corpus_dirs: Sequence[FsPath]) -> tuple[CorpusCase, ...]:
    cases = load_corpora(corpus_dirs)
    if not cases:
        console.print(
            f"[yellow]No cases in {', '.join(map(str, corpus_dirs))}. The corpus is human "
            "authored; see "
            "oyster/corpus/cases/README.md. Continuing with an empty corpus."
        )
    return cases


def _report_recording(provider: ModelProvider) -> None:
    if isinstance(provider, RecordingProvider):
        console.print(
            f"{len(provider.recorded)} call(s) made and recorded, "
            f"{len(provider.replayed)} replayed from existing fixtures under "
            f"{provider.fixtures_dir}"
        )


def _load_priors(path: str | None) -> Priors | None:
    if not path:
        return None
    file = FsPath(path)
    if not file.is_file():
        console.print(f"[red]priors file {path} not found; run calibrate first.")
        sys.exit(2)
    return priors_from_json(file.read_text(encoding="utf-8"))


def cmd_calibrate(args: argparse.Namespace) -> int:
    cases = _load_corpus(_corpus_dirs(args))
    provider = _make_provider(args, cases, calibration_paths(CATALOG))
    priors = calibrate(cases, provider, BINDINGS, CATALOG, workers=args.workers)
    _report_recording(provider)
    FsPath(args.priors_out).write_text(priors_to_json(priors), encoding="utf-8")

    table = Table(title=f"Calibrated priors over {priors.corpus_size} cases")
    table.add_column("role")
    table.add_column("model")
    table.add_column("category")
    table.add_column("catch rate", justify="right")
    table.add_column("n", justify="right")
    table.add_column("95% CI", justify="right")
    for (role, alias, category), rate in sorted(priors.catch_rate.items()):
        estimate = priors.quality.get((role, alias, category))
        n = str(estimate.n) if estimate else "-"
        ci = f"{estimate.ci_low:.2f}-{estimate.ci_high:.2f}" if estimate else "-"
        table.add_row(role, alias, category, f"{rate:.2f}", n, ci)
    console.print(table)
    console.print(f"Wrote {args.priors_out}")
    return 0


def cmd_eval(args: argparse.Namespace) -> int:
    cases = _load_corpus(_corpus_dirs(args))
    for path in CATALOG:
        validate_path(path, set(BINDINGS))
    provider = _make_provider(args, cases, CATALOG)

    hooks: list[BudgetHook] = []
    if args.budget is not None:
        priors = _load_priors(args.priors)
        hooks.append(BudgetHook(Cost(args.budget, args.latency), priors))

    results, reports = evaluate(CATALOG, cases, provider, BINDINGS, hooks, workers=args.workers)
    _report_recording(provider)
    markdown = render_results(
        results,
        reports,
        BINDINGS,
        corpus_size=len(cases),
        provider_name=args.label or args.provider,
        corpus_commit=_corpus_commit(_corpus_dirs(args)),
    )
    FsPath(args.out).write_text(markdown, encoding="utf-8")
    FsPath(args.json_out).write_text(results_to_json(results, reports), encoding="utf-8")

    table = Table(title=f"OYSTER eval over {len(cases)} cases ({args.provider})")
    for column in ("path", "$ total", "strict", "loose", "seeded", "$/bug", "halted"):
        table.add_column(column, justify="right" if column != "path" else "left")
    for path in CATALOG:
        path_results = [result for result in results if result.path_id == path.id]
        path_reports = [report for report in reports if report.path_id == path.id]
        dollars = sum(result.cost.dollars for result in path_results)
        strict = sum(len(report.caught_strict) for report in path_reports)
        loose = sum(len(report.caught_loose) for report in path_reports)
        seeded = sum(len(report.caught_loose) + len(report.missed) for report in path_reports)
        halted = sum(1 for result in path_results if result.halted_reason)
        per_bug = "n/a" if strict == 0 else f"${dollars / strict:.4f}"
        table.add_row(
            path.id, f"${dollars:.4f}", str(strict), str(loose), str(seeded), per_bug, str(halted)
        )
    console.print(table)
    console.print(f"Wrote {args.out} and {args.json_out}")
    return 0


def cmd_pack(args: argparse.Namespace) -> int:
    cases = _load_corpus(_corpus_dirs(args))
    fixtures = FsPath(args.fixtures)
    pending = collect_pending(cases, fixtures, BINDINGS, CATALOG)
    if not pending:
        console.print(
            f"[green]Nothing pending: every request is answered under {fixtures}. "
            f"Run: python -m oyster.cli eval --provider mock --fixtures {fixtures} "
            f'--label "conversation: <model> (estimated tokens)"'
        )
        return 0
    pack_root = FsPath(args.out)
    rounds = sorted(
        (p for p in pack_root.glob("round-*") if p.is_dir()),
        key=lambda p: int(p.name.split("-", 1)[1]) if p.name[6:].isdigit() else 0,
    )
    if rounds and (rounds[-1] / "manifest.json").is_file():
        latest = json.loads((rounds[-1] / "manifest.json").read_text(encoding="utf-8"))
        if {entry["key"] for entry in latest} == {request.key for request in pending}:
            console.print(
                f"[yellow]Nothing new since {rounds[-1]}: the same {len(pending)} request(s) "
                "are still unanswered. Paste its messages and run ingest before packing again."
            )
            return 0
    round_number = len(rounds) + 1
    out_dir = pack_root / f"round-{round_number}"
    pack_path, manifest_path = write_pack(pending, out_dir, batch_size=args.batch_size)
    by_model: dict[str, int] = {}
    for request in pending:
        by_model[request.model_id] = by_model.get(request.model_id, 0) + 1
    console.print(
        f"Round {round_number}: {len(pending)} pending request(s) "
        + ", ".join(f"{count} on {model}" for model, count in by_model.items())
    )
    console.print(f"Wrote {pack_path} and {manifest_path}")
    console.print(
        "Paste each message into a chat on the model it names, save the replies to a file, "
        f"then: python -m oyster.cli ingest --pack {out_dir} --responses <file> "
        f"--fixtures {fixtures} --model-label <label>"
    )
    return 0


def cmd_ingest(args: argparse.Namespace) -> int:
    manifest = FsPath(args.pack) / "manifest.json"
    responses_text = FsPath(args.responses).read_text(encoding="utf-8")
    report = ingest(
        manifest,
        responses_text,
        FsPath(args.fixtures),
        model_label=args.model_label,
        latency_s=args.latency_s,
    )
    console.print(f"Wrote {len(report.written)} fixture(s) under {args.fixtures}")
    if report.missing:
        console.print(f"[yellow]No reply found for: {', '.join(report.missing)}")
    if report.unparseable:
        console.print(
            f"[red]Reply is not a JSON findings object for: {', '.join(report.unparseable)}"
        )
    console.print(
        "Next: python -m oyster.cli pack (emits the next round, or says nothing is pending)"
    )
    return 0 if not report.unparseable else 1


def cmd_select(args: argparse.Namespace) -> int:
    priors = _load_priors(args.priors)
    if priors is None:
        console.print("[red]--priors is required for select.")
        return 2
    case = CorpusCase(id="<none>", diff="", seeded=())
    if args.corpus and args.case:
        case = next(c for c in load_corpora(_corpus_dirs(args)) if c.id == args.case)

    selection = select(CATALOG, case, priors, BINDINGS, args.budget, args.latency)
    if selection.path_id is None:
        console.print(f"[yellow]No feasible path: {selection.no_feasible_reason}")
        if selection.cheapest_infeasible:
            path_id, cost = selection.cheapest_infeasible
            console.print(
                f"Cheapest infeasible: {path_id} at ${cost.dollars:.4f}, {cost.latency_s:.2f}s"
            )
    else:
        console.print(
            f"[green]Selected path {selection.path_id}[/green]: predicted quality "
            f"{selection.predicted_quality:.2f}, predicted cost "
            f"${selection.predicted_cost.dollars:.4f} / {selection.predicted_cost.latency_s:.2f}s"
        )
    for path_id, reason in selection.rejected:
        console.print(f"  rejected {path_id}: {reason}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="oyster", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    def add_provider_args(p: argparse.ArgumentParser) -> None:
        p.add_argument("--provider", choices=["mock", "anthropic", "claude-code"], default="mock")
        p.add_argument(
            "--corpus",
            action="append",
            default=None,
            help=f"case directory; repeatable (default {settings.corpus_dir})",
        )
        p.add_argument("--fixtures", default=DEFAULT_FIXTURES, help="mock fixture dir")
        p.add_argument(
            "--record",
            default=DEFAULT_FIXTURES,
            help="record anthropic completions as mock fixtures here (use --no-record to skip)",
        )
        p.add_argument("--no-record", dest="record", action="store_const", const=None)
        p.add_argument("--yes", action="store_true", help="skip the paid-run confirmation")
        p.add_argument(
            "--workers",
            type=int,
            default=1,
            help="cases run concurrently per path (I/O bound providers only; default 1)",
        )

    cal = sub.add_parser("calibrate", help="measure per-node priors and write priors.json")
    add_provider_args(cal)
    cal.add_argument("--priors-out", default=settings.priors_path)
    cal.set_defaults(func=cmd_calibrate)

    ev = sub.add_parser("eval", help="run every path over the corpus and write results.md")
    add_provider_args(ev)
    ev.add_argument("--out", default=settings.results_path)
    ev.add_argument("--json-out", default="results.json")
    ev.add_argument("--label", default=None, help="provider label in results.md header")
    ev.add_argument("--budget", type=float, default=None, help="enable BudgetHook at $ budget")
    ev.add_argument("--latency", type=float, default=settings.latency_tolerance_s)
    ev.add_argument("--priors", default=None, help="priors.json for BudgetHook predictions")
    ev.set_defaults(func=cmd_eval)

    pack = sub.add_parser(
        "pack", help="conversation mode: write the next round of prompts to paste into a chat"
    )
    pack.add_argument("--corpus", action="append", default=None, help="repeatable")
    pack.add_argument("--fixtures", default="fixtures/conversation")
    pack.add_argument("--out", default="packs")
    pack.add_argument("--batch-size", type=int, default=20, help="requests per chat message")
    pack.set_defaults(func=cmd_pack)

    ing = sub.add_parser("ingest", help="conversation mode: store chat replies as fixtures")
    ing.add_argument("--pack", required=True, help="the round directory holding manifest.json")
    ing.add_argument("--responses", required=True, help="file with the pasted replies")
    ing.add_argument("--fixtures", default="fixtures/conversation")
    ing.add_argument("--model-label", required=True, help='e.g. "chat:claude-sonnet-5"')
    ing.add_argument("--latency-s", type=float, default=0.0, help="not measured in chat; 0")
    ing.set_defaults(func=cmd_ingest)

    sel = sub.add_parser("select", help="pick a path under a budget from calibrated priors")
    sel.add_argument("--budget", type=float, default=settings.budget_dollars)
    sel.add_argument("--latency", type=float, default=settings.latency_tolerance_s)
    sel.add_argument("--priors", default=settings.priors_path)
    sel.add_argument("--corpus", action="append", default=None, help="repeatable")
    sel.add_argument("--case", default=None)
    sel.set_defaults(func=cmd_select)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
