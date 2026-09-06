# OYSTER as a skill forest

The general model underneath the engine, and code review as one instance of it.

## 0. Why generalize

Catching bugs is one skill. The engine that measured it does not know what a diff is: a graph
of measurable capabilities, priors calibrated on the owner's own ground truth, a selection
objective under the owner's constraints, and provenance for every number. The architecture
document said this was scenario-generic ([`ARCHITECTURE.md`](ARCHITECTURE.md) §0). The first
run gave the strongest reason to take that seriously: the only place the engine was wrong was
the one assumption it made without measuring (node independence), and it was wrong in a way the
table exposed.

A skill forest is the same discipline applied to every capability an engineering organization,
or a person, relies on. Each skill is measured on its own ground truth with its own scorer.
Skills compose into functions, functions into roles, roles into what an organization or a
career actually is. At every level the same question is asked the same way: given this task,
this budget and these success metrics, which subgraph, executed by whom, and how do we know.

## 1. The general model

Nine nouns. The third column is where each lives today; the fourth says whether it is engine
(generic) or scenario (specific to code review).

| noun | meaning | today | kind |
|---|---|---|---|
| **Task** | one unit of work: an input artifact plus ground truth | `CorpusCase(id, diff, seeded)` | scenario |
| **Expected** | a golden label the scorer matches against | `SeededBug` | scenario |
| **Output** | the structured claim a skill produces | `Finding` | scenario |
| **Scorer** | rule mapping (outputs, expected) to a report with recall-side counts (caught, missed) and precision-side counts (false positives), at a strict and a loose level | `matching.match()`, `MatchReport` | scenario rule, engine report shape |
| **Skill** | a role with a contract: the procedure (prompt or program) and the output schema | `Node.role`, `prompts.templates`, `OUTPUT_CONTRACT` | scenario wording, engine shape |
| **Executor** | whatever performs a skill: a model, a tool, a person | `ModelBinding`, `providers/` | engine (people not yet first-class) |
| **Binding** | skill × executor | `Node(role, model_alias, prompt_key)` | engine |
| **Composite** | a DAG of bindings whose edges carry outputs; a function is a composite whose terminal output has the function's contract | `Path`, `Edge`, `executor.run_path` | engine |
| **Cost** | a vector, today (dollars, latency), extensible with human minutes, CI minutes, blast radius | `Cost`, `cost.price`, `path_cost` | engine |
| **Prior** | calibrated quality per (skill, executor, category) and mean cost per binding | `Priors`, `evaluation.calibrate` | engine |
| **Objective** | constraints and an argmax over candidates, with an explicit answer when nothing is feasible | `selector.select`, `Selection` | engine |
| **Provenance** | every result retains each binding's raw completion and cost | `PathResult`, `NodeResult`, fixtures | engine |

Twelve rows because three of the nouns split into a rule and a shape. The engine modules
(`graph`, `cost`, `executor`, `selector`, `evaluation`, `providers`, `conversation`) never
touch a diff. Everything review-specific sits in four places: the three scenario types, the
matcher, the prompt templates, and the corpus loader with its diff parser plus
`tools/pr_to_case.py`. That is the seam a scenario plugin cuts along (§4).

## 2. The forest

**Trees and levels.** A tree per domain: software delivery, incident response, data quality,
whatever the owner runs. Levels: skill → function → role → organization or career. Leaves are
skills with a corpus and a scorer. Internal nodes are composites. The three review paths are
three composites of three skills inside one function, "review a change".

**Priors roll up by measurement, not by formula.** The first run predicted the composites from
their leaves under an independence assumption and got the ranking backwards (predicted
C > B > A, measured B > A > C). Two reasons, both structural: a critic re-judges the reviewer's
findings rather than detecting independently, and a composite's transfer rule (last node wins)
can lose an upstream catch. So every composite that has been run gets its own calibration row,
and its parent's prior is measured on the parent's corpus. The independence formula remains
only as the prior for a composite that has never been run, labeled as such.

**People are executors.** A human is a binding with a measured prior and a cost: dollars per
task, or a cost `h` per miss that reaches them. That turns "what do we delegate to AI" into the
same argmax the engine already runs: minimize AI dollars + human dollars + `h` × expected misses,
subject to latency, budget and policy constraints. On the first run's numbers the break-even
between the cheap pass and the cascade is `h` above three cents per missed bug, which is why
the AI-dollar column stops mattering the moment a person is in the loop. The engine can say
that only because the cost vector and the objective are the owner's.

**Policy is a constraint, not a prompt.** Some nodes must be executed by a person (the merge
decision, the production promotion). In the forest that is a fixed binding on a node, a
constraint the selector cannot trade away, rather than an instruction the model is asked to
obey.

**Selection is hierarchical.** Choose a function's composite, then the bindings within it, at
each level over the candidates that level exposes. The `SEAM` comment in `selector.select` is
where a search over the forest attaches; enumeration over a catalog is the degenerate case with
one level and three candidates.

**Provenance composes.** A function's result is the tree of its skills' results, each with its
raw completion, so a wrong answer at the top can be traced to the leaf that produced it.

**A career is a profile.** A person's priors across skills, and the weights they put on the
objective, are what "your success metrics" means at the individual level. An organization's
forest is the same matrix over people, tools and agents. The engine does not decide the weights;
it makes them explicit and shows what each weighting selects.

## 3. Instances

### 3.1 Code review (implemented)

| noun | instance |
|---|---|
| task | a unified diff |
| expected | seeded bug: file, inclusive line range, category, description |
| output | finding: file, line range, category, description, confidence |
| scorer | overlap on file and lines; strict adds category; one finding per bug, largest overlap, ties by id; false positives counted |
| skills | cheap-scanner (recall-biased), deep-reviewer (precision-biased), critic (judges another reviewer's output) |
| executors | Haiku 4.5, Sonnet 5 through the API, the Claude Code CLI, or a chat window |
| composites | A single pass, B cascade, C bounded iteration |
| categories | logic, security, style |
| cost | tokens at list rates; latency |
| corpus | 17 reversed bug-fix PRs from public repositories, 21 seeded bugs |
| result | A 15/21 at $0.0008 per bug, B 16/21 at $0.0028, C 14/21 at $0.0070; selector picked C |

### 3.2 Bug fixing (next instance, ground truth already in hand)

| noun | instance |
|---|---|
| task | repository state at the buggy commit plus the failing test, optionally plus the finding that located the bug (the review function's output becomes this function's input, which is what an edge between functions means) |
| expected | the tests that must pass; the original fix as a reference patch |
| output | a patch |
| scorer | deterministic: run the suite. Strict = every test passes including tests unseen by the executor; loose = the target test passes. False positive = a patch that touches files the reference did not need to touch, or breaks a passing test |
| skills | patcher, test-writer, patch-reviewer (the review skill reused at the next level) |
| executors | models and agents; the Claude Code CLI provider already runs them; a person |
| cost | tokens plus CI minutes per attempt |
| corpus | the same 17 PRs: the fix is the reference patch and the PR's tests are the oracle, so the review corpus is the fixing corpus for free |

### 3.3 Incident root cause

| noun | instance |
|---|---|
| task | an alert plus a window of logs, traces and recent changes |
| expected | the root cause from the post-mortem: component, offending change, category |
| output | a root-cause claim: component, suspected change, category, confidence |
| scorer | strict = component and change match; loose = component only; false positive = a confident wrong claim |
| skills | triage (which subsystem), evidence-reader, hypothesis-critic |
| executors | models; the on-call engineer as a fixed binding for the mitigation decision |
| cost | tokens, latency, and time-to-mitigation, which dominates |

### 3.4 Deployment

| noun | instance |
|---|---|
| task | a release candidate with its checks |
| expected | post-deploy health: no rollback, no error-budget burn |
| output | go, no-go, or a staged plan with a canary and a rollback trigger |
| scorer | outcome after the fact: rollback happened or not, incident opened or not |
| skills | risk-assessor, canary-planner |
| executors | the promotion node is a person by policy: a fixed binding, not a selectable one |
| cost | blast radius enters the vector; the objective is asymmetric because a wrong go costs more than a wrong no-go |

### 3.5 Two instances written out in full

[`instances/BUILD-CI.md`](instances/BUILD-CI.md) takes the model into a build and release
platform, where ground truth is free and the objective has two error costs.
[`instances/LIFE-PLANNING.md`](instances/LIFE-PLANNING.md) takes it to a person planning a
path from school into work, where the executor owns the objective, the counterfactual is never
observed, and wellbeing models supply the dimensions of the weight vector.

### 3.6 Skills with judged outputs

Design-document review, pull-request descriptions, runbook quality: no deterministic oracle.
The scorer is a rubric applied by a judge, and the judge is itself a skill in the forest with
its own corpus, calibrated by its agreement with human labels. Measurement-first all the way
down: a judge with an unmeasured agreement rate is an assumption, and the forest has one rule
about assumptions.

## 4. What changes in the code

A minimal generalization, in order of leverage:

1. **A scenario plugin.** Done: `oyster/scenario.py` is the protocol (`load_tasks`,
   `render_messages`, `parse_output`, `keep`, `dedup_key`, `sort_key`, `expected`, `score`,
   `prompt_keys`, `catalog`), `oyster/scenarios/code_review.py` gathers the review pieces
   behind it without moving them, and `oyster/scenarios/bug_fixing.py` is the second instance.
   The executor and evaluation take a scenario and default to code review, so every v1 call is
   unchanged and the committed table replays identically. The genericity test
   (`tests/test_bug_fixing_scenario.py`) runs a patch-producing flow, a cascade that hands the
   first patch to the second node, and calibration, through the same engine with no engine
   change. The structural scorer (files touched versus the reference fix) stands in until a
   test runner is wired to real checkouts; `SubprocessRunner` is the shape of that.
2. **The human executor is already prototyped.** Conversation mode's pack and ingest loop is a
   queue of tasks handed to a person and their answers taken back as completions. Naming it a
   provider with a cost per task makes people first-class bindings.
3. **Per-composite calibration** rows and a predictor that uses a measured composite prior when
   one exists and the independence formula, labeled, only when none does.
4. **The objective takes weights**: `h` per miss, a cost per false positive, extra cost
   dimensions, so `select` minimizes what the owner actually pays.
5. **Composites that reference composites**, so the catalog becomes a forest and selection
   becomes hierarchical at the seam already marked.

The second instance (§3.2) is the test of genericity: if bug fixing runs on the same engine
with only a scenario plugin added, the abstraction is real. If it needs engine changes, the
abstraction was wrong and the changes say where.

## 5. What must not change

The rules that made the first table honest hold at every leaf and every level: priors are
measured, strict and loose never merge, a halted run is data, a failed call is billed, the
transfer rule between nodes is explicit, and every number traces to a retained raw result. A
forest is only worth growing if each tree keeps those rules; a skill that cannot be measured
against ground truth of its own is not a leaf yet.
