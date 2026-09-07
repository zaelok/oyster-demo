"""Build the auto tier of the review corpus from merged bug-fix PRs in public repositories.

The reviewed tier (`oyster/corpus/cases/`) is 17 cases a person signed off on. This tool
grows a second, machine-labelled tier next to it: it searches a fixed list of public
repositories for merged pull requests whose titles read like fixes, filters them by size and
author, reverses each one with `tools.pr_to_case.build`, and keeps only the drafts that pass
mechanical gates (validator, source files only, small, no leaked fix vocabulary, one to three
change blocks). Nothing is judged by a model and nothing is judged by a person, which is why
the tier is labelled `auto` and why every case carries the PR title as its description:
the label says what the fix did, not what the defect is.

    python -m tools.build_corpus --out oyster/corpus/cases-auto --target 183
    python -m tools.build_corpus --orgs apple cuda --target 20      # a subset
    python -m tools.build_corpus --offline                           # cache only, no gh calls

Everything fetched from GitHub is cached under --cache (default .corpus-cache/, gitignored),
so a rerun is offline and deterministic once the cache is warm. The output directory gets the
cases, a generated SOURCES.md, candidates.jsonl with every PR considered and the reason it
was accepted or not, and BUILD-REPORT.md with the funnel.

What the gates cannot check: whether the reversed hunk is a defect a reviewer could find from
the diff alone, whether the category guess is right, and whether the seeded range is the best
anchor for an absence bug. Those are the questions the reviewed tier answers by hand and the
reason the two tiers are evaluated separately.
"""

import argparse
import json
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass, field
from pathlib import Path

from oyster.corpus import load_case_dict, load_cases, parse_diff
from tools.pr_to_case import _gh, build, clean_title, leak_hits

# ------------------------------------------------------------------ repositories

# Names are the ones GitHub search accepts today: search does not follow renames (HTTP 422),
# so moved repositories (rapidsai/* to NVIDIA/*, NeMo to NVIDIA-NeMo/*) are listed at their
# new addresses.
REPOS: dict[str, tuple[str, ...]] = {
    "apple": (
        "apple/swift-nio",
        "apple/swift-collections",
        "apple/swift-protobuf",
        "apple/swift-argument-parser",
        "apple/swift-crypto",
        "apple/swift-certificates",
        "apple/swift-nio-ssl",
        "apple/swift-nio-http2",
        "apple/swift-nio-extras",
        "apple/swift-async-algorithms",
        "apple/swift-openapi-generator",
        "apple/swift-log",
        "apple/swift-metrics",
        "apple/swift-configuration",
        "apple/swift-http-types",
        "apple/pkl",
        "apple/pkl-go",
        "apple/foundationdb",
        "apple/coremltools",
        "apple/servicetalk",
        "apple/axlearn",
        "apple/container",
        "apple/containerization",
        "swiftlang/swift",
        "swiftlang/swift-syntax",
        "swiftlang/swift-package-manager",
        "swiftlang/sourcekit-lsp",
        "swiftlang/swift-format",
        "swiftlang/swift-build",
        "swiftlang/swift-foundation",
        "swiftlang/swift-testing",
        "swiftlang/swift-driver",
        "swiftlang/swift-corelibs-foundation",
    ),
    "openai": (
        "openai/codex",
        "openai/openai-python",
        "openai/openai-node",
        "openai/openai-agents-python",
        "openai/openai-agents-js",
        "openai/tiktoken",
        "openai/whisper",
        "openai/evals",
        "openai/openai-go",
        "openai/openai-java",
        "openai/openai-dotnet",
        "openai/openai-ruby",
        "openai/gpt-oss",
        "openai/harmony",
        "openai/simple-evals",
        "openai/openai-realtime-agents",
    ),
    "allenai": (
        "allenai/OLMo-core",
        "allenai/open-instruct",
        "allenai/olmocr",
        "allenai/dolma",
        "allenai/olmes",
        "allenai/OLMo",
        "allenai/beaker-py",
        "allenai/beaker-gantry",
        "allenai/reward-bench",
        "allenai/olmo-cookbook",
        "allenai/OLMoE",
        "allenai/molmo",
        "allenai/wildguard",
        "allenai/asta-bench",
        "allenai/ai2-scholarqa-lib",
        "allenai/papermage",
        "allenai/rslearn",
        "allenai/ir_datasets",
        "allenai/SciRIFF",
        "allenai/tango",
    ),
    "anthropics": (
        "anthropics/anthropic-sdk-python",
        "anthropics/anthropic-sdk-typescript",
        "anthropics/anthropic-sdk-go",
        "anthropics/anthropic-sdk-java",
        "anthropics/anthropic-sdk-ruby",
        "anthropics/anthropic-sdk-csharp",
        "anthropics/anthropic-sdk-php",
        "anthropics/claude-agent-sdk-python",
        "anthropics/claude-agent-sdk-typescript",
        "anthropics/claude-code",
        "anthropics/claude-code-action",
        "anthropics/claude-code-base-action",
        "anthropics/claude-code-security-review",
        "anthropics/claude-cookbooks",
        "anthropics/claude-quickstarts",
        "anthropics/courses",
        "anthropics/skills",
    ),
    "mcp": (
        "modelcontextprotocol/python-sdk",
        "modelcontextprotocol/typescript-sdk",
        "modelcontextprotocol/go-sdk",
        "modelcontextprotocol/java-sdk",
        "modelcontextprotocol/rust-sdk",
        "modelcontextprotocol/csharp-sdk",
        "modelcontextprotocol/kotlin-sdk",
        "modelcontextprotocol/inspector",
        "modelcontextprotocol/servers",
        "modelcontextprotocol/registry",
        "modelcontextprotocol/mcpb",
    ),
    "cuda": (
        "NVIDIA/cutlass",
        "NVIDIA/cccl",
        "NVIDIA/cuda-python",
        "NVIDIA/TensorRT-LLM",
        "NVIDIA/TensorRT",
        "NVIDIA/Megatron-LM",
        "NVIDIA/TransformerEngine",
        "NVIDIA/warp",
        "NVIDIA/cuda-quantum",
        "NVIDIA/DALI",
        "NVIDIA/nvidia-container-toolkit",
        "NVIDIA/cudf-spark",
        "NVIDIA/cuopt",
        "NVIDIA-NeMo/Speech",
        "NVIDIA-NeMo/RL",
        "NVIDIA/apex",
        "NVIDIA/nvmath-python",
        "NVIDIA/cuda-samples",
        "NVIDIA/nccl",
        "NVIDIA/gpu-operator",
        "NVIDIA/k8s-device-plugin",
        "NVIDIA/Model-Optimizer",
        "NVIDIA/cudnn-frontend",
        "NVIDIA/MatX",
        "NVIDIA/nvbench",
        "NVIDIA/cudf",
        "NVIDIA/cuml",
        "rapidsai/rmm",
        "NVIDIA/raft",
        "NVIDIA/cuvs",
        "rapidsai/cugraph",
        "rapidsai/kvikio",
        "rapidsai/ucxx",
        "cupy/cupy",
        "triton-lang/triton",
        "flashinfer-ai/flashinfer",
        "Dao-AILab/flash-attention",
    ),
    "litellm": ("BerriAI/litellm",),
    "vllm": (
        "vllm-project/vllm",
        "vllm-project/vllm-ascend",
        "vllm-project/llm-compressor",
        "vllm-project/production-stack",
        "vllm-project/aibrix",
        "vllm-project/guidellm",
        "vllm-project/semantic-router",
        "vllm-project/tpu-inference",
        "vllm-project/vllm-omni",
        "vllm-project/vllm-gaudi",
        "vllm-project/flash-attention",
    ),
}

# New cases per org and per repository; the target is filled round-robin so no single
# high-volume repository (litellm, vllm, codex) becomes the corpus.
ORG_CAPS = {
    "apple": 40,
    "openai": 30,
    "allenai": 20,
    "anthropics": 15,
    "mcp": 10,
    "cuda": 40,
    "litellm": 10,
    "vllm": 20,
}
PER_REPO_CAP = 8
REPO_CAP_OVERRIDES = {"BerriAI/litellm": 10, "vllm-project/vllm": 10, "openai/codex": 10}

# ------------------------------------------------------------------ filters

SINCE = "2025-09-01"
SEARCH_TERMS = "(fix OR fixes OR fixed OR bugfix OR bug OR crash OR regression OR incorrect)"

TITLE_INCLUDE = re.compile(
    r"\b(fix(?!ture)\w*|bug\w*|hotfix|crash\w*|incorrect\w*|wrong\w*|regression|leak\w*|race|deadlock"
    r"|overflow|underflow|off-by-one|null|nil|none|panic\w*|exception|hang\w*|broken|missing"
    r"|invalid|corrupt\w*|mismatch\w*|use-after-free|double[- ]free|infinite loop|segfault"
    r"|unhandled|uninitiali[sz]ed|stale|inconsistent)\b",
    re.IGNORECASE,
)
TITLE_EXCLUDE = re.compile(
    r"\b(bump\w*|typos?|docs?|documentation|readme|changelog|chore|revert\w*|releases?"
    r"|versions?|lint\w*|format\w*|rename\w*|deprecat\w*|flaky|spelling|licen[cs]e"
    r"|dependabot|pre-commit|mypy|pyright|ruff|clippy|type hints?|typing|annotations?"
    r"|refactor\w*|clean ?up|ci|cd|workflows?|benchmarks?|examples?|tests?|testing|comments?"
    r"|logging|warnings?|translation|i18n|nightly|pipeline|build|compile|compilation|docker"
    r"|dockerfile|package|packaging|dependency|dependencies|requirements|upgrade|update"
    r"|coverage|readability|style|prettier|eslint|black|isort|notebook|tutorial|sample|link)\b",
    re.IGNORECASE,
)

SOURCE_EXTENSIONS = {
    ".py": "python",
    ".swift": "swift",
    ".go": "go",
    ".rs": "rust",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".java": "java",
    ".kt": "kotlin",
    ".scala": "scala",
    ".cs": "csharp",
    ".rb": "ruby",
    ".php": "php",
    ".c": "c",
    ".h": "c",
    ".cc": "cpp",
    ".cpp": "cpp",
    ".cxx": "cpp",
    ".hpp": "cpp",
    ".hh": "cpp",
    ".cuh": "cuda",
    ".cu": "cuda",
    ".m": "objc",
    ".mm": "objc",
    ".pkl": "pkl",
}

STRONG_SECURITY = (
    "security",
    "cve-",
    "vulnerab",
    "inject",
    "xss",
    "csrf",
    "ssrf",
    "traversal",
    "sanitiz",
    "authoriz",
    "authenticat",
    "privilege",
    "exploit",
    "credential",
    "secret",
    "redact",
    "api key",
    "api_key",
    "apikey",
    "password",
    "sensitive",
    "plaintext",
    "unsafe deserial",
)
# "leak" alone is usually memory; it counts as security only next to something worth leaking.
LEAK_CONTEXT = ("key", "secret", "credential", "password", "sensitive", "pii", "token")

MAX_CHANGED_FILES = 4
MAX_CHANGES = 150
MAX_KEPT_FILES = 3
MAX_HUNKS = 6
MAX_DIFF_LINES = 120
MAX_SEEDED = 3

_PR_NUMBER_RE = re.compile(r"/pull/(\d+)$")


# ------------------------------------------------------------------ records


@dataclass
class Entry:
    """One pull request through the funnel."""

    org: str
    repo: str
    number: int
    title: str
    merged_at: str = ""
    author: str = ""
    outcome: str = "pending"
    reason: str = ""
    case_id: str = ""
    language: str = ""
    category: str = ""
    seeded: int = 0
    kinds: list[str] = field(default_factory=list)

    @property
    def url(self) -> str:
        return f"https://github.com/{self.repo}/pull/{self.number}"

    def key(self) -> str:
        return f"{self.repo}#{self.number}"


# ------------------------------------------------------------------ GitHub access


class GitHub:
    """gh-backed fetches with a file cache. Search is throttled to stay under GitHub's 30
    requests per minute; the other endpoints share the 5000 per hour core budget."""

    def __init__(self, cache: Path, offline: bool = False, refresh_search: bool = False):
        self.cache = cache
        self.offline = offline
        self.refresh_search = refresh_search
        self._last_search = 0.0
        for sub in ("search", "meta", "diff"):
            (cache / sub).mkdir(parents=True, exist_ok=True)

    def _run(self, *args: str) -> str:
        if self.offline:
            raise RuntimeError("offline: " + " ".join(args))
        delay = 65.0
        for attempt in range(4):
            try:
                return _gh(*args)
            except subprocess.CalledProcessError as exc:
                stderr = (exc.stderr or "").lower()
                throttled = "rate limit" in stderr or "403" in stderr or "429" in stderr
                if not throttled or attempt == 3:
                    raise
                print(f"  rate limited; sleeping {delay:.0f}s", file=sys.stderr)
                time.sleep(delay)
        raise RuntimeError("unreachable")

    def search(self, repo: str, since: str) -> list[dict]:
        path = self.cache / "search" / (repo.replace("/", "__") + ".json")
        if path.exists() and not self.refresh_search:
            return json.loads(path.read_text(encoding="utf-8"))
        gap = 2.2 - (time.monotonic() - self._last_search)
        if gap > 0:
            time.sleep(gap)
        query = f"repo:{repo} is:pr is:merged merged:>={since} {SEARCH_TERMS} in:title"
        out = self._run(
            "api",
            "-X",
            "GET",
            "search/issues",
            "-f",
            f"q={query}",
            "-F",
            "per_page=100",
            "-f",
            "sort=created",
            "-f",
            "order=desc",
            "-f",
            "advanced_search=true",
        )
        self._last_search = time.monotonic()
        items = json.loads(out).get("items", [])
        slim = [
            {
                "number": item["number"],
                "title": item.get("title", ""),
                "user": (item.get("user") or {}).get("login", ""),
                "user_type": (item.get("user") or {}).get("type", ""),
                "labels": [label.get("name", "") for label in item.get("labels", [])],
            }
            for item in items
        ]
        path.write_text(json.dumps(slim, indent=1), encoding="utf-8")
        return slim

    def meta(self, repo: str, number: int) -> dict:
        path = self.cache / "meta" / f"{repo.replace('/', '__')}__{number}.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        out = self._run("api", f"repos/{repo}/pulls/{number}")
        raw = json.loads(out)
        slim = {
            "title": raw.get("title", ""),
            "body": raw.get("body") or "",
            "labels": [label.get("name", "") for label in raw.get("labels", [])],
            "additions": raw.get("additions", 0),
            "deletions": raw.get("deletions", 0),
            "changed_files": raw.get("changed_files", 0),
            "merged_at": raw.get("merged_at") or "",
            "user": (raw.get("user") or {}).get("login", ""),
            "user_type": (raw.get("user") or {}).get("type", ""),
            "merge_commit_sha": raw.get("merge_commit_sha") or "",
        }
        path.write_text(json.dumps(slim, indent=1), encoding="utf-8")
        return slim

    def diff(self, repo: str, number: int) -> str:
        path = self.cache / "diff" / f"{repo.replace('/', '__')}__{number}.diff"
        if path.exists():
            return path.read_text(encoding="utf-8")
        text = self._run("pr", "diff", f"https://github.com/{repo}/pull/{number}")
        path.write_text(text, encoding="utf-8")
        return text


# ------------------------------------------------------------------ pure helpers


def title_verdict(title: str) -> str | None:
    """None when the title reads like a bug fix, else the rejection reason."""
    if TITLE_EXCLUDE.search(title):
        return "title:excluded-word"
    if not TITLE_INCLUDE.search(title):
        return "title:not-fix-like"
    return None


def size_verdict(meta: dict) -> str | None:
    if not meta.get("merged_at"):
        return "meta:not-merged"
    if meta.get("user_type") == "Bot" or str(meta.get("user", "")).endswith("[bot]"):
        return "meta:bot-author"
    if int(meta.get("changed_files", 0)) > MAX_CHANGED_FILES:
        return "meta:too-many-files"
    if int(meta.get("additions", 0)) + int(meta.get("deletions", 0)) > MAX_CHANGES:
        return "meta:too-large"
    if "revert" in str(meta.get("title", "")).lower():
        return "meta:revert"
    return None


def auto_category(title: str, body: str, labels: Sequence[str]) -> tuple[str, list[str]]:
    """Stricter than pr_to_case.guess_category: only strong security vocabulary flips the
    label, and nothing is called style, because a merged fix PR changed behaviour by
    construction and the word "cleanup" in its title is not evidence otherwise."""
    text = " ".join([title, body[:2000], " ".join(labels)]).lower()
    hits = [word for word in STRONG_SECURITY if word in text]
    if "leak" in text and any(word in text for word in LEAK_CONTEXT):
        hits.append("leak+" + next(word for word in LEAK_CONTEXT if word in text))
    if hits:
        return "security", hits
    return "logic", ["default"]


def language_of(paths: Iterable[str]) -> str | None:
    """The language facet, or None when any kept file is not source code."""
    languages: list[str] = []
    for path in paths:
        suffix = Path(path).suffix.lower()
        if suffix not in SOURCE_EXTENSIONS:
            return None
        languages.append(SOURCE_EXTENSIONS[suffix])
    if not languages:
        return None
    return Counter(languages).most_common(1)[0][0]


def case_id_for(repo: str, number: int, taken: set[str]) -> str:
    name = repo.split("/", 1)[1].lower().replace("-", "").replace("_", "").replace(".", "")
    candidate = f"case-{name}-{number}"
    if candidate in taken:
        org = repo.split("/", 1)[0].lower().replace("-", "")
        candidate = f"case-{org}-{name}-{number}"
    return candidate


def widen_absence(seeded: list[dict], kinds: Sequence[str], diff: str) -> None:
    """An absence bug is anchored at one context line by pr_to_case; a reviewer pointing at
    the missing check may land a line either side, so the seeded range is widened by one
    line in each direction, clipped to its hunk. Mutates the seeded dicts in place."""
    ranges = parse_diff(diff)
    for bug, kind in zip(seeded, kinds, strict=True):
        if kind != "deletion-only":
            continue
        anchor = bug["line_start"]
        for start, end in ranges.get(bug["file"], []):
            if start <= anchor <= end:
                bug["line_start"] = max(start, anchor - 1)
                bug["line_end"] = min(end, anchor + 1)
                break


def gate(draft: dict, kinds: Sequence[str], verdict: str) -> str | None:
    """Mechanical acceptance for the auto tier. Returns the rejection reason or None."""
    if verdict != "OK":
        return "case:validator"
    files = list(parse_diff(draft["diff"]))
    if not files:
        return "case:no-source-files"
    if len(files) > MAX_KEPT_FILES:
        return "case:too-many-files"
    if language_of(files) is None:
        return "case:non-source-file"
    diff = draft["diff"]
    if sum(1 for line in diff.splitlines() if line.startswith("@@")) > MAX_HUNKS:
        return "case:too-many-hunks"
    if diff.count("\n") > MAX_DIFF_LINES:
        return "case:too-long"
    if not draft["seeded"]:
        return "case:no-seeded"
    if len(draft["seeded"]) > MAX_SEEDED:
        return "case:too-many-seeded"
    if any(kind == "unanchored" for kind in kinds):
        return "case:unanchored"
    return None


def existing_sources(existing_dirs: Sequence[Path]) -> tuple[set[str], set[str]]:
    """PR urls and case ids already in other tiers, so they are neither repeated nor
    shadowed."""
    urls: set[str] = set()
    ids: set[str] = set()
    for directory in existing_dirs:
        for path in sorted(Path(directory).glob("case-*.json")):
            raw = json.loads(path.read_text(encoding="utf-8"))
            ids.add(str(raw.get("id", path.stem)))
            url = str((raw.get("source") or {}).get("pr", ""))
            if url:
                urls.add(url.rstrip("/"))
    return urls, ids


# ------------------------------------------------------------------ the funnel


def discover(gh: GitHub, orgs: Sequence[str], since: str, log: list[str]) -> list[Entry]:
    entries: list[Entry] = []
    for org in orgs:
        for repo in REPOS[org]:
            try:
                hits = gh.search(repo, since)
            except (subprocess.CalledProcessError, RuntimeError) as exc:
                log.append(f"search failed for {repo}: {str(exc).splitlines()[-1][:120]}")
                continue
            for hit in hits:
                entry = Entry(org, repo, int(hit["number"]), str(hit["title"]), author=hit["user"])
                if hit.get("user_type") == "Bot" or entry.author.endswith("[bot]"):
                    entry.outcome, entry.reason = "rejected", "meta:bot-author"
                else:
                    reason = title_verdict(entry.title)
                    if reason:
                        entry.outcome, entry.reason = "rejected", reason
                entries.append(entry)
            print(f"  {repo}: {len(hits)} hits", file=sys.stderr)
    return entries


def round_robin(entries: Sequence[Entry], orgs: Sequence[str]) -> list[Entry]:
    """Newest first within a repository (by PR number, so no metadata is needed yet),
    repositories cycled within an org, orgs cycled."""
    by_repo: dict[str, list[Entry]] = defaultdict(list)
    for entry in entries:
        by_repo[entry.repo].append(entry)
    for queue in by_repo.values():
        queue.sort(key=lambda entry: entry.number, reverse=True)
    org_queues: dict[str, list[list[Entry]]] = {
        org: [by_repo[repo] for repo in REPOS[org] if by_repo.get(repo)] for org in orgs
    }
    ordered: list[Entry] = []
    active = [org for org in orgs if org_queues[org]]
    while active:
        for org in list(active):
            queues = org_queues[org]
            if not queues:
                active.remove(org)
                continue
            queue = queues.pop(0)
            ordered.append(queue.pop(0))
            if queue:
                queues.append(queue)
    return ordered


def convert(
    gh: GitHub,
    entry: Entry,
    meta: dict,
    case_id: str,
    log: list[str],
) -> tuple[dict | None, list[str]]:
    try:
        diff_text = gh.diff(entry.repo, entry.number)
    except (subprocess.CalledProcessError, RuntimeError) as exc:
        entry.outcome, entry.reason = "rejected", "case:diff-fetch-error"
        log.append(f"diff failed for {entry.key()}: {str(exc).splitlines()[-1][:120]}")
        return None, []
    view = {
        "title": meta["title"],
        "body": meta["body"],
        "labels": [{"name": name} for name in meta["labels"]],
    }
    source = {"pr": entry.url, "repo": entry.repo, "number": entry.number}
    draft, report = build(view, diff_text, case_id=case_id, source=source, max_lines=MAX_DIFF_LINES)
    kinds = [candidate.kind for candidate in report.seeded]
    category, reasons = auto_category(meta["title"], meta["body"], meta["labels"])
    title = clean_title(meta["title"]) or meta["title"]
    for bug in draft["seeded"]:
        bug["category"] = category
        bug["description"] = (
            f"{title} [auto label from the fix PR title: says what the fix did, "
            "not what the defect is]"
        )
    widen_absence(draft["seeded"], kinds, draft["diff"])
    try:
        load_case_dict(draft, case_id)
        verdict = "OK"
    except ValueError as exc:
        verdict = f"REJECTED: {exc}"
    reason = gate(draft, kinds, verdict)
    if reason is None and leak_hits(draft["diff"]):
        reason = "case:leak"
    if reason is not None:
        entry.outcome, entry.reason = "rejected", reason
        return None, kinds
    files = list(parse_diff(draft["diff"]))
    draft["meta"] = {
        "tier": "auto",
        "org": entry.org,
        "repo": entry.repo,
        "number": entry.number,
        "merged_at": meta["merged_at"],
        "merge_commit": meta["merge_commit_sha"],
        "title": meta["title"],
        "language": language_of(files),
        "category_reasons": reasons,
        "seeded_kinds": kinds,
        "generator": "tools/build_corpus.py",
    }
    entry.language = draft["meta"]["language"]
    entry.category = category
    entry.seeded = len(draft["seeded"])
    entry.kinds = kinds
    return draft, kinds


def fill(
    gh: GitHub,
    ordered: Sequence[Entry],
    *,
    target: int,
    out_dir: Path,
    taken_ids: set[str],
    log: list[str],
) -> list[Entry]:
    """Walk the round-robin order until the target is met. Metadata and diffs are fetched
    only for entries actually reached, so the GitHub budget scales with the target, not with
    the number of hits."""
    accepted: list[Entry] = []
    per_org: Counter[str] = Counter()
    per_repo: Counter[str] = Counter()
    for entry in ordered:
        if len(accepted) >= target:
            entry.outcome, entry.reason = "skipped", "cap:target"
            continue
        if per_org[entry.org] >= ORG_CAPS[entry.org]:
            entry.outcome, entry.reason = "skipped", "cap:org"
            continue
        if per_repo[entry.repo] >= REPO_CAP_OVERRIDES.get(entry.repo, PER_REPO_CAP):
            entry.outcome, entry.reason = "skipped", "cap:repo"
            continue
        try:
            meta = gh.meta(entry.repo, entry.number)
        except (subprocess.CalledProcessError, RuntimeError) as exc:
            entry.outcome, entry.reason = "rejected", "meta:fetch-error"
            log.append(f"meta failed for {entry.key()}: {str(exc).splitlines()[-1][:120]}")
            continue
        entry.merged_at = meta.get("merged_at", "")
        entry.author = meta.get("user", entry.author)
        reason = size_verdict(meta)
        if reason:
            entry.outcome, entry.reason = "rejected", reason
            continue
        case_id = case_id_for(entry.repo, entry.number, taken_ids)
        draft, _ = convert(gh, entry, meta, case_id, log)
        if draft is None:
            continue
        taken_ids.add(case_id)
        entry.outcome, entry.reason, entry.case_id = "accepted", "", case_id
        (out_dir / f"{case_id}.json").write_text(
            json.dumps(draft, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
        accepted.append(entry)
        per_org[entry.org] += 1
        per_repo[entry.repo] += 1
        print(
            f"  accepted {len(accepted)}/{target}: {case_id} ({entry.language}, "
            f"{entry.category}, {entry.seeded} seeded)",
            file=sys.stderr,
        )
    return accepted


# ------------------------------------------------------------------ outputs


def write_sources(out_dir: Path, accepted: Sequence[Entry], since: str) -> None:
    lines = [
        "# Corpus sources: auto tier",
        "",
        (
            "Every case is a merged bug-fix PR from a public repository, reversed by "
            "`tools/build_corpus.py` so the fixed code is the before side and the buggy code "
            f"the after side. All PRs merged on or after {since}. **Nobody reviewed these "
            "labels.** The seeded range is where the fix changed code; the description is the "
            "PR title; the category is a keyword guess. See README.md in this directory for "
            "what that means."
        ),
        "",
        "| case | source PR | merged | language | category | seeded | kinds |",
        "|---|---|---|---|---|---|---|",
    ]
    for entry in sorted(accepted, key=lambda entry: entry.case_id):
        lines.append(
            f"| {entry.case_id} | {entry.url} | {entry.merged_at[:10]} | {entry.language} | "
            f"{entry.category} | {entry.seeded} | {', '.join(entry.kinds)} |"
        )
    total_bugs = sum(entry.seeded for entry in accepted)
    lines += [
        "",
        f"{len(accepted)} cases, {total_bugs} seeded bugs.",
        "",
        "## Licensing of the excerpts",
        "",
        (
            "Each case embeds a short excerpt (the reversed hunks of one merged pull request) "
            "from the repository linked in its row. Those excerpts remain under their original "
            "licenses and their copyright stays with their authors; `THIRD-PARTY-NOTICES.md` "
            "at the repository root names each source repository's license and reproduces the "
            "license texts, and the link in the row is the attribution to the change. The "
            "repository's own license covers the engine, the tooling and the labels, not the "
            "excerpts."
        ),
    ]
    (out_dir / "SOURCES.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def write_candidates(out_dir: Path, entries: Sequence[Entry]) -> None:
    """Every PR considered, one line each. Accepted rows carry every field; the thousands
    of rejected and skipped rows keep only what explains the decision, so the file stays
    small enough to commit."""
    with (out_dir / "candidates.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for entry in sorted(entries, key=lambda entry: (entry.org, entry.repo, -entry.number)):
            if entry.outcome == "accepted":
                row = asdict(entry)
                row["url"] = entry.url
            else:
                # No author login on rows that were not accepted: the funnel needs the
                # decision, not a list of people.
                row = {
                    "repo": entry.repo,
                    "number": entry.number,
                    "title": entry.title[:80],
                    "outcome": entry.outcome,
                    "reason": entry.reason,
                }
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_report(
    out_dir: Path,
    entries: Sequence[Entry],
    accepted: Sequence[Entry],
    log: Sequence[str],
    since: str,
) -> None:
    reasons = Counter(entry.reason for entry in entries if entry.outcome != "accepted")
    stages = Counter(entry.outcome for entry in entries)
    by_org: dict[str, Counter[str]] = defaultdict(Counter)
    for entry in entries:
        by_org[entry.org][entry.outcome] += 1
    by_repo = Counter(entry.repo for entry in accepted)
    languages = Counter(entry.language for entry in accepted)
    categories = Counter(entry.category for entry in accepted)
    kinds = Counter(kind for entry in accepted for kind in entry.kinds)

    lines = [
        "# Build report: auto tier",
        "",
        (
            f"Generated by `tools/build_corpus.py`. Search window: merged on or after {since}, "
            "newest 100 fix-like merged PRs per repository, sorted by creation date."
        ),
        "",
        "## Funnel",
        "",
        "| stage | count |",
        "|---|---|",
        f"| search hits | {len(entries)} |",
        f"| accepted | {stages['accepted']} |",
        f"| rejected | {stages['rejected']} |",
        f"| skipped (a cap was reached before conversion) | {stages['skipped']} |",
        f"| never reached (pending) | {stages['pending']} |",
        "",
        "## Rejection reasons",
        "",
        "| reason | count |",
        "|---|---|",
    ]
    lines += [f"| {reason} | {count} |" for reason, count in reasons.most_common()]
    lines += [
        "",
        "## By organisation",
        "",
        "| org | hits | accepted | rejected | skipped |",
        "|---|---|---|---|---|",
    ]
    for org, counter in by_org.items():
        lines.append(
            f"| {org} | {sum(counter.values())} | {counter['accepted']} | "
            f"{counter['rejected']} | {counter['skipped']} |"
        )
    lines += ["", "## Accepted by repository", "", "| repository | cases |", "|---|---|"]
    lines += [f"| {repo} | {count} |" for repo, count in by_repo.most_common()]
    lines += ["", "## Accepted by language", "", "| language | cases |", "|---|---|"]
    lines += [f"| {language} | {count} |" for language, count in languages.most_common()]
    lines += [
        "",
        "## Accepted by category (keyword guess)",
        "",
        "| category | cases |",
        "|---|---|",
    ]
    lines += [f"| {category} | {count} |" for category, count in categories.most_common()]
    lines += ["", "## Seeded bug kinds", "", "| kind | bugs |", "|---|---|"]
    lines += [f"| {kind} | {count} |" for kind, count in kinds.most_common()]
    lines += [
        "",
        (
            "`added`: the fix replaced these lines, so the reversed diff adds the buggy lines "
            "and the seeded range is exactly them. `deletion-only`: the fix only added code, so "
            "the bug is an absence; the seeded range is the neighbouring context line widened "
            "by one line each side."
        ),
    ]
    if log:
        lines += ["", "## Fetch problems", ""]
        lines += [f"- {line}" for line in log]
    (out_dir / "BUILD-REPORT.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8", newline="\n"
    )


# ------------------------------------------------------------------ main


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="build_corpus", description=__doc__)
    parser.add_argument("--out", default="oyster/corpus/cases-auto")
    parser.add_argument("--cache", default=".corpus-cache")
    parser.add_argument("--target", type=int, default=183, help="new cases to accept")
    parser.add_argument("--since", default=SINCE, help="merged on or after (YYYY-MM-DD)")
    parser.add_argument("--orgs", nargs="*", default=list(REPOS), choices=list(REPOS))
    parser.add_argument(
        "--existing",
        nargs="*",
        default=["oyster/corpus/cases"],
        help="case directories whose PRs and ids must not be repeated",
    )
    parser.add_argument("--offline", action="store_true", help="use the cache only")
    parser.add_argument("--refresh-search", action="store_true", help="ignore cached searches")
    parser.add_argument("--clean", action="store_true", help="delete existing case files in --out")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    if args.clean:
        for path in out_dir.glob("case-*.json"):
            path.unlink()
    gh = GitHub(Path(args.cache), offline=args.offline, refresh_search=args.refresh_search)
    log: list[str] = []

    known_urls, taken_ids = existing_sources([Path(p) for p in args.existing])
    print(
        f"discovering across {sum(len(REPOS[o]) for o in args.orgs)} repositories", file=sys.stderr
    )
    entries = discover(gh, args.orgs, args.since, log)
    for entry in entries:
        if entry.outcome == "pending" and entry.url in known_urls:
            entry.outcome, entry.reason = "rejected", "already-in-reviewed-tier"
    ordered = round_robin([e for e in entries if e.outcome == "pending"], args.orgs)
    print(f"{len(entries)} hits, {len(ordered)} pass the title filter; converting", file=sys.stderr)
    accepted = fill(gh, ordered, target=args.target, out_dir=out_dir, taken_ids=taken_ids, log=log)

    write_sources(out_dir, accepted, args.since)
    write_candidates(out_dir, entries)
    write_report(out_dir, entries, accepted, log, args.since)
    cases = load_cases(out_dir)
    print(
        f"{len(accepted)} accepted, {len(cases)} cases load, "
        f"{sum(len(c.seeded) for c in cases)} seeded bugs; report in {out_dir / 'BUILD-REPORT.md'}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
