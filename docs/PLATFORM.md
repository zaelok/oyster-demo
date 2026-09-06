# Platform: the registry, the profile, and the run manifest

How the skill forest becomes a system. This document fixes the shapes; the engine in this
repository is the first optimizer that reads them. Everything here is data first: the registry
is a directory of versioned files, the profiles are generated from runs, and git is the
database until that stops being enough.

## 0. Layers

| layer | responsibility | today |
|---|---|---|
| registry | skills, executors, corpora, roles, flow patterns, as versioned files | `registry/` (first entries) |
| calibration | run corpora through bindings, write profiles with provenance | `oyster.cli calibrate` |
| optimizer (OYSTER) | given a role's objective, a task's facets, the candidate flows and the profiles, select a flow and its bindings, execute with hooks, return provenance, deposit observations | `oyster.selector`, `oyster.executor` |
| observation store | raw completions (fixtures), per-run results, edge payloads for research, production observations, labels | `fixtures/`, `results/` |
| policy | fixed human nodes, autonomy level, budgets, latency SLOs, kill switch | role files, `BudgetHook` |

## 1. Principles that shape every schema

1. **Level is derived.** A skill executed by one binding is level 1. A skill whose flow
   references other skills has level `max(children) + 1`. Nobody types a level.
2. **Skills are executor-agnostic.** A skill is a contract, a scorer and a corpus. Which
   models, tools or people can perform it is discovered by calibration and recorded in
   profiles, never declared on the skill.
3. **Profiles are distributions with provenance.** Quality carries the sample size and a
   confidence interval; cost and latency carry p50 and p95; every profile names the corpus
   commit, the executor specification and the run manifest it came from, and expires when any
   of them changes.
4. **Composites are measured end to end.** A flow's profile is never the product of its
   leaves. The independence formula is a labeled prior for flows that have not been run.
5. **Flows are data; the optimizer selects.** Candidate flows are instances of patterns
   (single, cascade, critic loop, ensemble, route then dispatch, escalate on low confidence).
   Generating candidates by search is a later step and stays enumerable and auditable.
6. **Reproducibility has three layers.** The pipeline replays bit-exactly from fixtures; an
   observation is one sample from a distribution and profiles are built from `k` replicates;
   a decision is a pure function of the objective, the profile snapshot and the candidates,
   and records the snapshot hash it used.
7. **Objectives and policy belong to the owner; priors belong to measurement; intermediate
   products belong to research.** Stored separately, the platform stays generic.

## 2. The run manifest

Two runs with equal manifests are replicates; the spread between them is the binding's own
variance. A manifest is hashed and attached to every profile cell and every decision.

```yaml
manifest:
  corpus: {id: code-review, commit: cba004d1}
  prompts_sha256: 9c0e...            # bytes of every template used
  scorer: {id: overlap-and-category, version: 1}
  executor:
    model: claude-sonnet-5
    settings: {effort: medium, thinking: default}
    harness: claude.ai-chat            # api | claude-code-cli | claude.ai-chat | human
  cache: cold                          # cold | warm | n/a
  replicates: 1
  measured_at: 2026-09-06T18:46:37Z
```

## 3. Registry schemas

### 3.1 Skill

```yaml
id: code-review/find-defects
level: derived
contract:
  input: unified-diff
  output: finding[]                    # file, line range, category, description, confidence
scorer: {id: overlap-and-category, version: 1, oracle_tier: structural}
task_descriptor:                       # facets, the rows of the sparse matrix
  declared: [language, change_type, diff_lines, repository]
  derived: [risk_class]                # produced by a triage skill, itself measured
categories: [logic, security, style]   # the first, degenerate facet
corpus: {id: code-review, path: oyster/corpus/cases}
replicates: 1                          # minimum k before a profile counts
flows: [A, B, C]                       # candidate composites, see registry/flows
```

Oracle tiers, from strongest to weakest: `deterministic` (tests pass, builds succeed),
`structural` (location overlap), `human-label`, `judged` (a model calibrated against human
labels). The platform discounts confidence by tier.

### 3.2 Executor

```yaml
id: claude-sonnet-5@api
kind: model                            # model | tool | human
model: claude-sonnet-5
settings: {effort: default, thinking: default}
harness: api
rates: {input_per_1m: 2.00, output_per_1m: 10.00, cache_discount: 0.90}
cost_dimensions: [dollars, latency_s]
```

A person is an executor of kind `human` with `cost_dimensions: [minutes]` and a rate per
minute or per task. The conversation-mode loop (`pack`, `ingest`) is the harness for human
executors.

### 3.3 Flow (a composite, instantiated from a pattern)

```yaml
id: B
skill: code-review/find-defects
pattern: cascade
nodes:
  - {id: b1, skill: code-review/cheap-scan,   executor: claude-haiku-4-5@api}
  - {id: b2, skill: code-review/deep-review,  executor: claude-sonnet-5@api}
edges: [{from: b1, to: b2, carries: finding[]}]
transfer: last-node-wins                # how the terminal output is formed
```

### 3.4 Profile (generated, never hand-edited)

One row per (skill or flow) × executor × facet cell. Empty cells are absent; readers back off
along the facet hierarchy and report the level they landed on.

```yaml
key: {skill: code-review/find-defects, flow: A, facet: {category: logic}}
quality: {rate: 0.82, n: 17, ci95: [0.59, 0.94]}
cost:    {dollars: {p50: 0.0007, p95: 0.0011}, latency_s: {p50: null, p95: null}}
manifest_sha256: 4f3a...
source: results/conversation-haiku45-sonnet5/priors.json
```

### 3.5 Corpus

```yaml
id: code-review
path: oyster/corpus/cases
commit: cba004d1
source_tier: reversed-fixes            # reversed-fixes | bug-introducing-commits | planted | production
date_cutoff: 2025-09-01                # cases merged after this date, contamination control
facet_tags: [language, repository, category]
license_note: excerpts keep their original licenses, see SOURCES.md
size: {cases: 17, expected: 21}
```

### 3.6 Role

```yaml
id: change-reviewer
skill_sets: [code-quality]
objective:
  weights: {logic: 1.0, security: 3.0, style: 0.2}
  h_per_miss: 50                       # what a miss costs the owner, in dollars
  false_positive_cost: 5
  budget_per_task: 0.05
  latency_p95_s: 120
  exploration_budget: 0.05             # share of spend reserved for filling empty cells
policy:
  human_nodes: [merge-decision]
  autonomy: advisory
```

The optimizer minimizes `AI dollars + human dollars + h_per_miss × expected misses +
false_positive_cost × expected false positives` subject to the budget, the latency SLO and
the fixed nodes. With `h_per_miss = 0` it reduces to the current engine.

## 4. The sparse matrix

Rows are facet combinations from the skill's `task_descriptor`; columns are executors and
flows; cells are profile entries. Three operations:

- **lookup with backoff**: `(Go, security, large-diff)` → `(*, security, *)` → `(*, *, *)`,
  returning the estimate and the level it came from;
- **fill**: calibration weighted by the role's actual traffic distribution over facets, plus
  the exploration budget for cells the traffic hits but no profile covers;
- **render**: the matrix is the capability map, a heatmap of facets by executors with cell
  opacity for `n`.

Intermediate outputs (what an edge carried) are exported as a separate dataset keyed by the
manifest, for research on edge value: quality and cost downstream with and without the
upstream payload. They do not enter the matrix.

## 5. Feedback loop

Two channels, never merged: measurements on golden corpora (quality, cost, latency) and
observations from production (cost and latency always; quality only when a label arrives:
a human review outcome, a revert, an incident traced back to a change). Labels are batched
into corpus updates and profiles are recalibrated offline on a cadence the domain sets: daily
for build triage, per release for review, per term for a person. Survivorship is stated:
misses surface later than catches, so production labels over-represent them.

## 6. Changes since the build spec

The spec ([`BUILD-SPEC.md`](BUILD-SPEC.md)) froze `oyster/types.py` for the first build.
These additions are additive; every v1 call site still works.

| change | where | why |
|---|---|---|
| `QualityEstimate(rate, n, ci_low, ci_high)` and `CostProfile(p50/p95 dollars and latency, n)` alongside `Priors.catch_rate` and `Priors.mean_cost` | `types.py`, `evaluation.calibrate`, `priors.json` | principle 3 |
| latency tolerance checked at the sum of node p95 latencies when a profile exists, mean otherwise | `selector.predict` | SLOs are p95 statements |
| scenario plugin: the review-specific pieces behind one protocol, the engine generic over the output type | `oyster/scenario.py`, `oyster/scenarios/` | principle 2 and the genericity test |

## 7. What is in `registry/` today

The review skill as the first registered entry: skill, executors, corpus, flows and role, all
pointing at code and results that exist. The profile is the generated `priors.json` of the
first run. Everything else in this document is the shape the next entries must fit.
