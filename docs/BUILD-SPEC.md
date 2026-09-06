# OYSTER Build Specification

Written for unattended execution by background agents. Every task below is self-contained:
inputs, exact signatures, acceptance tests, and a hard stop condition. An agent that needs to
ask a question has hit a spec bug, so it stops and reports rather than guessing.

Companion document: [`ARCHITECTURE.md`](ARCHITECTURE.md) for what and why. This document is how.

**Stack.** Python 3.12, `uv`, `pytest`, `ruff`, `pydantic` and `pydantic-settings`, `anthropic`.
No web framework, no ORM, no async in the MVP.

---

## 0. Rules for every agent

Prepend this to every task dispatch.

1. **Write only the files in your assignment.** Touching anything else fails the task,
   including formatting fixes, import reordering, or improvements elsewhere.
2. **Import from `oyster.types` and `oyster.config` only.** Never import another module's
   internals. If your module seems to need another module, that is a spec bug, so stop and
   report.
3. **`oyster/types.py` is frozen.** Read it, never edit it.
4. **Never invent methodology.** If a behavior is not specified, stop and report rather than
   choosing. Specifically: never invent matching rules, scoring formulas, prompt wording, or
   pricing numbers.
5. **Never create corpus cases.** Corpus content is human authored, see §9.
6. **Never make network calls in tests.** Every test runs offline.
7. **Stop when your acceptance criteria pass.** Do not refactor, optimize, add features, or
   improve unrelated code.
8. Run `ruff check . && ruff format --check . && pytest -q` before reporting done.

---

## 1. Repository scaffold

Task 0, done first, by the orchestrator or a single agent. Everything else depends on it.

```
oyster-engine/
├── pyproject.toml
├── Makefile
├── README.md
├── .env.example
├── .github/workflows/ci.yml
├── oyster/
│   ├── __init__.py
│   ├── types.py            # §2, frozen
│   ├── config.py           # §3
│   ├── graph/__init__.py
│   ├── graph/catalog.py
│   ├── prompts/__init__.py
│   ├── prompts/templates.py
│   ├── cost/__init__.py
│   ├── providers/__init__.py
│   ├── providers/anthropic_provider.py
│   ├── providers/mock_provider.py
│   ├── corpus/__init__.py
│   ├── corpus/cases/          # human authored, agents never write here
│   ├── matching/__init__.py
│   ├── executor/__init__.py
│   ├── selector/__init__.py
│   ├── evaluation/__init__.py
│   └── cli.py
└── tests/
    ├── conftest.py
    ├── fixtures/
    └── test_*.py
```

`pyproject.toml`:

```toml
[project]
name = "oyster-engine"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "pydantic>=2.9",
    "pydantic-settings>=2.5",
    "anthropic>=0.40",
    "rich>=13.0",
]

[dependency-groups]
dev = ["pytest>=8.0", "ruff>=0.6"]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

`Makefile`:

```make
install:      ; uv sync
test:         ; uv run pytest -q
lint:         ; uv run ruff check . && uv run ruff format --check .
calibrate:    ; uv run python -m oyster.cli calibrate --provider $(PROVIDER)
eval:         ; uv run python -m oyster.cli eval --provider $(PROVIDER)
eval-mock:    ; $(MAKE) eval PROVIDER=mock
```

`PROVIDER` defaults to `mock`. Real API runs require `PROVIDER=anthropic` explicitly, so no
agent can spend money by accident.

CI runs `install`, `lint`, `test`, `eval-mock`. It never has an API key.

**Acceptance:** `make install && make lint && make test` succeeds with zero tests collected
failing, and every module directory exists with an `__init__.py`.

---

## 2. `oyster/types.py`, frozen contracts

Copy exactly. This file is the interface every other task compiles against.

```python
"""Frozen contracts. Every module imports from here. Nothing here changes without a
coordinated re-dispatch of dependent tasks."""

from dataclasses import dataclass
from typing import Literal, Protocol

Category = Literal["logic", "security", "style"]
CATEGORIES: tuple[Category, ...] = ("logic", "security", "style")


@dataclass(frozen=True)
class Cost:
    dollars: float
    latency_s: float

    def __add__(self, other: "Cost") -> "Cost":
        return Cost(self.dollars + other.dollars, self.latency_s + other.latency_s)

    @staticmethod
    def zero() -> "Cost":
        return Cost(0.0, 0.0)


@dataclass(frozen=True)
class ModelBinding:
    alias: str  # "cheap-model" | "strong-model"
    model_id: str
    rate_in: float  # dollars per 1M input tokens
    rate_out: float  # dollars per 1M output tokens
    cache_discount: float  # 0.0-1.0, fraction of rate_in waived on cached prefix tokens


@dataclass(frozen=True)
class Node:
    id: str  # unique within a Path
    role: str  # "cheap-scanner" | "deep-reviewer" | "critic"
    model_alias: str
    prompt_key: str  # key into oyster.prompts.templates.TEMPLATES


@dataclass(frozen=True)
class Edge:
    src: str
    dst: str
    carries: Literal["findings"] = "findings"


@dataclass(frozen=True)
class Path:
    id: str
    description: str
    nodes: tuple[Node, ...]  # topologically ordered
    edges: tuple[Edge, ...]


@dataclass(frozen=True)
class Finding:
    file: str
    line_start: int
    line_end: int
    category: Category
    description: str
    confidence: float


@dataclass(frozen=True)
class SeededBug:
    id: str
    file: str
    line_start: int
    line_end: int
    category: Category
    description: str


@dataclass(frozen=True)
class CorpusCase:
    id: str
    diff: str
    seeded: tuple[SeededBug, ...]


@dataclass(frozen=True)
class Completion:
    text: str
    input_tokens: int
    cached_input_tokens: int
    output_tokens: int
    latency_s: float
    model_id: str


@dataclass(frozen=True)
class NodeResult:
    node_id: str
    role: str
    findings: tuple[Finding, ...]
    completion: Completion
    cost: Cost
    parse_failed: bool = False


@dataclass(frozen=True)
class PathResult:
    path_id: str
    case_id: str
    node_results: tuple[NodeResult, ...]
    findings: tuple[Finding, ...]
    cost: Cost
    halted_reason: str | None = None


@dataclass(frozen=True)
class MatchReport:
    case_id: str
    path_id: str
    caught_strict: tuple[str, ...]
    caught_loose: tuple[str, ...]
    missed: tuple[str, ...]
    false_positives: int


@dataclass(frozen=True)
class Priors:
    """Calibrated quality priors. key is (role, model_alias, category)."""

    catch_rate: dict[tuple[str, str, str], float]
    mean_cost: dict[tuple[str, str], Cost]  # (role, model_alias)
    corpus_size: int


@dataclass(frozen=True)
class Selection:
    path_id: str | None
    predicted_quality: float
    predicted_cost: Cost
    rejected: tuple[tuple[str, str], ...]  # (path_id, reason)
    no_feasible_reason: str | None = None
    cheapest_infeasible: tuple[str, Cost] | None = None


class ModelProvider(Protocol):
    def complete(
        self,
        model_id: str,
        system: str,
        user: str,
        cached_prefix: str | None = None,
    ) -> Completion: ...


class Hook(Protocol):
    def before_node(self, node: Node, spent: Cost, budget: Cost) -> str | None:
        """Return a halt reason string to stop the run, or None to continue."""
```

---

## 3. `oyster/config.py`

```python
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
```

**Rates are placeholders.** The agent must not look them up or invent them. A human verifies
against published pricing before any real API run, and `results.md` records what was used.

**Acceptance:** importing `oyster.config` with no `.env` present succeeds and yields two
bindings. Setting `OYSTER_BUDGET_DOLLARS=5` in the environment changes `settings.budget_dollars`.

---

## 4. `oyster/prompts/templates.py`

Prompt wording is load-bearing because it determines every number in the results table.
It is specified here, not left to an agent.

```python
OUTPUT_CONTRACT = """
Respond with JSON only, no prose, no markdown fence:
{"findings": [{"file": str, "line_start": int, "line_end": int,
               "category": "logic"|"security"|"style",
               "description": str, "confidence": float}]}
Use line numbers from the diff's new-file side. If you find nothing, return
{"findings": []}. Never invent a file path that does not appear in the diff.
"""

CHEAP_SCANNER = (
    """You are a fast first-pass code reviewer. Scan the diff and flag anything
that looks suspicious. Favor recall over precision: it is better to flag a hunk that turns out
fine than to miss a real defect. Do not explain at length, one sentence per finding.

Categories: logic (wrong behavior, off-by-one, null handling, race), security (injection,
authz, secrets, unsafe deserialization), style (naming, dead code, formatting).

DIFF:
{diff}
"""
    + OUTPUT_CONTRACT
)

DEEP_REVIEWER = (
    """You are a thorough code reviewer. Analyze the diff for real defects.
Favor precision over recall: report a finding only when you can state what breaks and under
what condition.

Categories: logic, security, style, as defined by the impact on behavior rather than surface
appearance.

DIFF:
{diff}
{upstream_block}
"""
    + OUTPUT_CONTRACT
)

UPSTREAM_BLOCK = """
An earlier pass flagged these locations. Treat them as hints, not conclusions. Confirm, refute
or extend them, and report defects they missed.

EARLIER FINDINGS:
{upstream_findings}
"""

CRITIC = (
    """You are reviewing another reviewer's output, not the code directly. For each
finding below, decide whether it is a real defect or a false positive. Then state what the
reviewer likely missed.

Return findings you believe are real, plus any additional defects you identify. Drop findings
you judge to be false positives.

DIFF:
{diff}

FINDINGS UNDER REVIEW:
{upstream_findings}
"""
    + OUTPUT_CONTRACT
)

TEMPLATES: dict[str, str] = {
    "cheap_scanner": CHEAP_SCANNER,
    "deep_reviewer": DEEP_REVIEWER,
    "critic": CRITIC,
}
```

Rendering rules, normative:

- `{diff}` is always substituted with the case diff and always passed as `cached_prefix` to the
  provider, never duplicated into the user message body.
- `{upstream_block}` is the empty string when a node has no incoming edge, otherwise
  `UPSTREAM_BLOCK` with findings rendered as one JSON object per line.
- Prompt text is never modified at runtime.

**Acceptance:** rendering `deep_reviewer` with no upstream produces a prompt containing no
"EARLIER FINDINGS" text. With upstream, it contains each finding's file and line range.

---

## 5. `oyster/graph/`

```python
def validate_path(path: Path, known_aliases: set[str]) -> None:
    """Raise ValueError with a specific message on the first violation."""


def upstream_of(path: Path, node_id: str) -> tuple[str, ...]:
    """Node ids with an edge into node_id, in path order."""
```

Validation rules, all must be enforced, each with its own test:

1. node ids unique within the path
2. every edge endpoint refers to an existing node id
3. no cycles
4. `path.nodes` is a valid topological order, so every edge's src precedes its dst
5. every `node.model_alias` is in `known_aliases`
6. every `node.prompt_key` is in `TEMPLATES`
7. roles may repeat across nodes, ids may not

`catalog.py` defines exactly three paths:

```python
PATH_A  # id="A", one node: cheap-scanner on cheap-model, prompt cheap_scanner
PATH_B  # id="B", cheap-scanner(cheap) -> deep-reviewer(strong), one edge
PATH_C  # id="C", deep-reviewer(strong) -> critic(strong) -> deep-reviewer(strong)
# three nodes, ids "c1","c2","c3", two edges, role repeats at c1 and c3
CATALOG: tuple[Path, ...] = (PATH_A, PATH_B, PATH_C)
```

**Acceptance:** seven tests, one per rule, each asserting the specific error. Plus a test that
every path in `CATALOG` passes `validate_path`. Plus a test that Path C validates despite the
repeated role.

---

## 6. `oyster/cost/`

```python
def price(completion: Completion, binding: ModelBinding) -> Cost:
    """dollars = (input - cached) * rate_in / 1e6
           + cached * rate_in * (1 - cache_discount) / 1e6
           + output * rate_out / 1e6
    latency = completion.latency_s"""


def path_cost(node_costs: Sequence[Cost]) -> Cost:
    """Sequential execution: dollars sum, latency sums.
    NOTE: latency is a sum because this slice executes nodes serially. If parallel branches
    are added, latency becomes a max over branches and only this function changes."""


def estimate_tokens(text: str) -> int:
    """Single shared estimator, chars // 4. Used for prediction only, never for billing.
    Actual counts always come from Completion."""
```

**Acceptance:** a completion with 1000 input, 800 cached, 200 output at rate_in 3.0,
rate_out 15.0, discount 0.9 prices to `(200 * 3 + 800 * 3 * 0.1 + 200 * 15) / 1e6`. Assert the
exact float. Plus: `Cost.zero()` is the additive identity, `path_cost([])` is zero.

---

## 7. `oyster/providers/`

### mock_provider

```python
class MockProvider:
    def __init__(self, fixtures_dir: Path): ...
    def complete(self, model_id, system, user, cached_prefix=None) -> Completion: ...
```

Deterministic. Key on `sha256(model_id + system + user + (cached_prefix or ""))[:16]`. Look up
`fixtures_dir/<key>.json`. On miss, return a **valid empty response**,
`{"findings": []}`, with token counts derived from `estimate_tokens` and `latency_s = 0.05`,
and log the missing key to stderr so fixtures can be recorded later.

Fixture file format:

```json
{"text": "{\"findings\": [...]}", "input_tokens": 1200, "cached_input_tokens": 1000,
 "output_tokens": 150, "latency_s": 0.8, "model_id": "mock-cheap"}
```

Missing fixtures must never crash. A CI run with zero fixtures produces a complete results
table where every path catches nothing, which is a valid and honest result.

### anthropic_provider

```python
class AnthropicProvider:
    def __init__(self, api_key: str): ...
    def complete(self, model_id, system, user, cached_prefix=None) -> Completion: ...
```

- `cached_prefix` goes in the system block with `cache_control: {"type": "ephemeral"}`.
- Token counts come from `response.usage`, including `cache_read_input_tokens`. **Never
  estimate.** If the API omits a field, record 0 and set no fallback estimate.
- `latency_s` is measured with `time.perf_counter` around the call.
- Retry on 429 and 5xx: three attempts, exponential backoff 1s, 2s, 4s, with jitter. Other
  errors raise immediately.

**Acceptance:** mock tests assert determinism, that the same inputs give the same key, and that
a missing fixture returns an empty-findings completion rather than raising. Anthropic provider
tests use a stub HTTP layer and assert that cached tokens are read from usage rather than
computed, and that the retry policy fires on 429 and not on 400.

---

## 8. `oyster/matching/`

Normative rules. An agent that changes these has failed the task.

```python
def match(findings: Sequence[Finding], seeded: Sequence[SeededBug],
          case_id: str, path_id: str) -> MatchReport
```

1. A finding **overlaps** a bug when both are in the same file and the line ranges intersect by
   at least one line, treating both endpoints as inclusive.
2. **Strict catch**: overlap and `finding.category == bug.category`.
3. **Loose catch**: overlap, category ignored. Every strict catch is also a loose catch.
4. Each finding is assigned to **at most one** bug. When a finding overlaps several bugs,
   assign it to the bug with the largest overlap in lines. Ties break by lowest `bug.id`
   lexicographically. This makes the result deterministic.
5. Each bug may be caught by **at most one** finding. Extra findings on an already-caught bug
   are neither catches nor false positives, they are ignored.
6. **False positive**: a finding overlapping no bug at all. Report the count only.
7. `missed` is every bug id not in `caught_loose`.

**Acceptance:** at minimum these cases, each asserting exact `MatchReport` contents.

| Case | Expectation |
|---|---|
| exact range, same category | strict and loose |
| exact range, wrong category | loose only |
| adjacent ranges, no overlap | missed, and one false positive |
| single-line overlap at boundary | counts as overlap |
| finding spanning two bugs | assigned to larger overlap only |
| two findings on one bug | one catch, the extra ignored |
| tie in overlap size | lower bug id wins |
| different file, same lines | no overlap |
| empty findings | all missed, zero false positives |

---

## 9. `oyster/corpus/`

The agent implements the loader. **The agent does not write cases.**

```python
def load_cases(corpus_dir: Path) -> tuple[CorpusCase, ...]
def validate_case(case: CorpusCase) -> None
```

Case file, one JSON per case in `corpus/cases/`:

```json
{
  "id": "case-01",
  "diff": "--- a/pricing.py\n+++ b/pricing.py\n@@ -10,7 +10,7 @@\n...",
  "seeded": [
    {"id": "case-01-b1", "file": "pricing.py", "line_start": 42, "line_end": 44,
     "category": "logic", "description": "off-by-one in the discount tier boundary"}
  ]
}
```

Validation, each failure raising with the case id and the offending field:

1. `id` unique across the corpus, and matches the filename stem
2. `diff` non-empty and parses as a unified diff with at least one hunk
3. every `seeded[].file` appears as a target path in the diff
4. every `seeded[].line_start <= line_end`, both positive
5. every seeded line range falls inside a hunk of the new-file side
6. `category` is in `CATEGORIES`
7. seeded bug ids unique within the case

The agent creates `corpus/cases/README.md` explaining the format and stating that cases are
human authored, plus `corpus/cases/_example.json.template`. It creates no real cases.

**Acceptance:** loader tests use fixtures under `tests/fixtures/corpus/`, containing one valid
case and seven invalid ones, each triggering exactly one validation error.

---

## 10. `oyster/executor/`

```python
def run_path(path: Path, case: CorpusCase, provider: ModelProvider,
             bindings: dict[str, ModelBinding], hooks: Sequence[Hook] = ()) -> PathResult

class BudgetHook:
    def __init__(self, budget: Cost, priors: Priors | None = None): ...
    def before_node(self, node, spent, budget) -> str | None: ...
```

Execution contract:

1. Nodes execute in `path.nodes` order.
2. Before each node, call every hook in order. The first non-None return halts the run.
   Return a `PathResult` with the node results collected so far and `halted_reason` set.
   **A halted run is data, not an error.**
3. Build the user prompt from `TEMPLATES[node.prompt_key]`. `{diff}` is substituted for
   rendering but the same diff text is passed as `cached_prefix`.
4. `upstream_findings` is the union of findings from all upstream nodes per `upstream_of`,
   deduplicated by `(file, line_start, line_end, category)`, ordered by file then line_start.
5. Parse the response as JSON. On failure, retry once with the same prompt plus
   `"\n\nYour previous response was not valid JSON. Respond with JSON only."`. On second
   failure, record a `NodeResult` with empty findings and `parse_failed=True`.
   **The cost of a failed call is still recorded.** Never drop it.
6. Discard any finding whose `file` does not appear in the diff, and count discards in a
   module-level debug log. Models hallucinate paths and those must not become false positives.
7. Final `PathResult.findings` is the findings of the **last** node in path order, not the
   union. A cascade's later stage is meant to supersede the earlier one, and the critic path
   depends on this.
8. `cost` is `path_cost` over all node costs including failed ones.

**Acceptance:** all tests against `MockProvider`.

- path A end to end produces one `NodeResult`
- path B passes upstream findings into the second prompt, asserted by inspecting the rendered
  prompt captured by a recording provider
- a hook returning a reason halts before the second node, and the partial result has one node
  result and the reason set
- a fixture returning malformed JSON triggers one retry then `parse_failed=True` with cost
  still nonzero
- a finding on a file absent from the diff is discarded
- `PathResult.findings` equals the last node's findings, not the union

---

## 11. `oyster/selector/`

```python
def predict(path: Path, case: CorpusCase, priors: Priors,
            bindings: dict[str, ModelBinding]) -> tuple[float, Cost]

def select(paths: Sequence[Path], case: CorpusCase, priors: Priors,
           bindings: dict[str, ModelBinding],
           budget_dollars: float, latency_tolerance_s: float) -> Selection
```

Prediction, normative:

- predicted cost per node is `priors.mean_cost[(role, model_alias)]`, summed via `path_cost`.
  When a key is absent, use zero and record the path id in `Selection.rejected` with reason
  `"no priors"`, so an uncalibrated path is never silently ranked.
- predicted quality is the probability that a bug of average category mix is caught by at least
  one node in the path:
  `quality = mean over categories of (1 - product over nodes of (1 - catch_rate[role, alias, cat]))`
  This assumes node independence. **State that assumption in a docstring**, because it is
  false in reality and knowing where the model is wrong is part of the deliverable.

Selection order, normative:

1. reject paths with no priors
2. reject paths whose predicted `latency_s > latency_tolerance_s`, reason `"latency"`
3. reject paths whose predicted `dollars > budget_dollars`, reason `"budget"`
4. among survivors return the max predicted quality, ties broken by lower predicted dollars,
   then by path id
5. when no survivors remain, return `Selection` with `path_id=None`,
   `no_feasible_reason` naming which constraint eliminated the last candidate, and
   `cheapest_infeasible` carrying the lowest-dollar rejected path and its predicted cost

Enumeration is over the given `paths` only. **Do not implement heuristic search.** Leave one
comment marking where a Steiner heuristic would attach.

**Acceptance:** a path over budget is rejected with reason `"budget"`; a path over tolerance is
rejected with `"latency"` even when it is cheapest; an empty feasible set returns
`path_id=None` with `cheapest_infeasible` populated; a tie in quality resolves to lower cost;
a path with missing priors is rejected rather than scored as zero.

---

## 12. `oyster/evaluation/`

```python
def calibrate(cases, provider, bindings) -> Priors
def evaluate(paths, cases, provider, bindings) -> tuple[tuple[PathResult, ...],
                                                        tuple[MatchReport, ...]]
def render_results(results, reports, bindings, corpus_size: int) -> str
```

Calibration runs each **single node config** in isolation, not whole paths: for each distinct
`(role, model_alias, prompt_key)` in the catalog, run it alone over every case, match against
golden labels, and compute `catch_rate` per category as
`strict catches of that category / seeded bugs of that category`. `mean_cost` is the mean
`Cost` per node config over cases. Write `priors.json`.

Evaluation runs each full path over every case and produces one `PathResult` and one
`MatchReport` per (path, case).

`results.md` structure:

```markdown
# OYSTER results

Generated: <UTC ISO8601>
Corpus: <N> cases, <M> seeded bugs, corpus commit <sha>
Models: cheap-model=<id> @ $<rate_in>/$<rate_out> per 1M
        strong-model=<id> @ $<rate_in>/$<rate_out> per 1M
Provider: <mock|anthropic>

| path | description | $ total | strict caught | loose caught | seeded | $/bug (strict) | p50 latency | halted |
|------|-------------|---------|---------------|--------------|--------|----------------|-------------|--------|

## Per-case detail
<one table per path: case id, cost, caught ids, missed ids, false positives>

## Limitations
<static text from architecture §4, verbatim>
```

Rules:

- every path gets a row including bad performers
- strict and loose reported in **separate columns**, never merged
- `$/bug` is `total_dollars / strict_caught`, rendered as `n/a` when strict caught is zero,
  never as infinity or zero
- when `PathResult.halted_reason` is set for any case, the halted column shows the count

**Acceptance:** end to end against `MockProvider` with the fixture corpus, `render_results`
output contains one row per path, a `n/a` in the `$/bug` column when a path caught nothing, and
a Models line naming both model ids.

---

## 13. `oyster/cli.py`

```
python -m oyster.cli calibrate --provider {mock,anthropic} [--corpus DIR]
python -m oyster.cli eval      --provider {mock,anthropic} [--corpus DIR] [--out results.md]
python -m oyster.cli select    --budget 1.00 --latency 120 [--priors priors.json]
```

`--provider anthropic` requires `OYSTER_ANTHROPIC_API_KEY` and prints a cost estimate with a
confirmation prompt before running, unless `--yes` is passed. Default provider is `mock`.

---

## 14. Task graph for dispatch

Tasks in the same wave have disjoint file ownership and may run in parallel.

| Wave | Task | Owns | Depends on |
|---|---|---|---|
| 0 | scaffold, types, config | `pyproject`, `Makefile`, CI, `types.py`, `config.py` | none |
| 1 | T1 prompts | `oyster/prompts/` | wave 0 |
| 1 | T2 graph | `oyster/graph/`, `tests/test_graph.py` | wave 0, plus TEMPLATES keys from §4 |
| 1 | T3 cost | `oyster/cost/`, `tests/test_cost.py` | wave 0 |
| 1 | T4 providers | `oyster/providers/`, `tests/test_providers.py` | wave 0 |
| 1 | T5 corpus | `oyster/corpus/`, `tests/test_corpus.py`, `tests/fixtures/corpus/` | wave 0 |
| 1 | T6 matching | `oyster/matching/`, `tests/test_matching.py` | wave 0 |
| 2 | T7 executor | `oyster/executor/`, `tests/test_executor.py` | T1 T2 T3 T4 |
| 2 | T8 selector | `oyster/selector/`, `tests/test_selector.py` | T2 T3 T6 |
| 3 | T9 evaluation | `oyster/evaluation/`, `tests/test_evaluation.py` | T5 T6 T7 T8 |
| 3 | T10 cli, README | `oyster/cli.py`, `README.md` | T9 |
| 4 | human | `corpus/cases/*.json`, real API run | T10 |

T2 depends on §4 only for the template key names, which are fixed in this document, so T1 and
T2 still run in parallel.

**Wave 4 is not delegated.** A human seeds the corpus and authorizes the paid run.

---

## 15. Definition of done

- `make lint && make test && make eval-mock` green from a clean clone
- `results.md` generated with every path represented
- No module imports another module's internals, verified by a test that walks imports
- README states the claim, the method, the three paths, and the limitations verbatim from
  architecture §4
- Every number in `results.md` traceable to a retained `PathResult`

## 16. Stop and report, do not guess

An agent stops and reports when:

- a frozen type appears to be wrong or insufficient
- a specified rule is ambiguous or self-contradictory
- a task would require writing corpus cases
- a task would require a network call or spending money
- an acceptance criterion cannot be satisfied without changing a rule in this document
