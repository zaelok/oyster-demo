# Instance: cloud build and CI triage

The skill-forest model ([`../SKILL-FOREST.md`](../SKILL-FOREST.md)) applied to a build and
release platform: a Bazel-style monorepo, remote execution and caching, a CI pipeline that
thousands of engineers wait on. Not implemented; this is the design of the second instance and
the argument for why it is a better fit for the method than code review was.

## 0. Why this domain fits better than code review

Code review needed seeded bugs because a diff has no oracle. A build system is full of them:
a target builds or it does not, a test passes or it does not, a cache key hit or it did not, a
critical path took the minutes it took. Ground truth is free, labels arrive in hours rather than
weeks, and the cost that matters, engineer waiting time, is directly measurable. Every rule
that made the review table honest applies unchanged; the oracle tier goes up.

## 1. The mapping

| noun | instance |
|---|---|
| task | a build or pipeline event: a failed build with its logs and the change that triggered it, a change awaiting test selection, a pipeline definition awaiting analysis |
| expected | the disposition the system later took or the outcome that later happened: rerun passed (flake), fix commit passed (real failure), full-run results (which tests actually failed), measured duration after a change |
| output | a verdict or a plan: failure class plus root-cause location, a test set, a pipeline change with a predicted saving, a release go or no-go |
| scorer | deterministic where the oracle allows: verdict versus disposition, selected tests versus tests that actually failed, predicted versus measured duration |
| skills | see §2 |
| executors | models at several tiers, deterministic tools (build-graph queries, log parsers, cache inspectors), and engineers as fixed bindings on decisions |
| composites | classify then escalate; locate then propose; analyze then simulate |
| cost | tokens, CI minutes, and engineer waiting time, which dominates |
| priors | per skill × executor × facet, measured on the historical corpus |
| objective | asymmetric; see §5 |
| provenance | every verdict carries the log lines it rests on and the node that produced it |

## 2. Skills (leaves)

| skill | contract | scorer | oracle tier |
|---|---|---|---|
| failure triage | failure record → class in {real failure, environmental flake, dependency drift, cache problem, timeout, infrastructure} plus confidence | class versus later disposition (rerun passed, fix commit, infra ticket) | deterministic after the fact |
| root-cause location | failure record → the target, step and log span that is the cause rather than an echo | span overlaps the span the fixing engineer cited or edited | structural match, like review |
| affected-target and test selection | change → set of targets and tests to run | recall against the tests a full run shows failing; cost as the size of the selected set | deterministic (retrospective full runs) |
| cache-key correctness | build configuration and change → keys that may collide or miss across branches | verified by replaying the cache under the two branch states | deterministic |
| critical-path analysis | pipeline definition and timings → the serialized edges that could run in parallel, with a predicted saving | predicted versus measured duration after the change is applied | deterministic with delay |
| release readiness | release candidate and its checks → go, no-go, or staged plan | outcome: rollback or incident within the window | deterministic with delay, asymmetric |

Each leaf has a corpus, a scorer and a replicate policy before it is registered. Composites
are measured end to end and never scored by multiplying leaf priors.

## 3. Flows (candidates for the selector)

- **Triage cascade**: cheap classifier on every failure; escalate only "real failure" and
  "unknown" to the log-reading root-cause skill on a strong model; propose a fix; an engineer
  decides. The review cascade with the escalation condition changed from risk class to failure
  class.
- **Confidence-gated annotation**: a flake verdict above a calibrated confidence threshold
  annotates the build and triggers a rerun; below it, the build stays failed and a person
  looks. The threshold is chosen from the measured false-pass rate, not by hand.
- **Select then verify**: test selection on the cheap tier, with a periodic full run on a sample
  of changes to keep the recall estimate honest.
- **Analyze then simulate**: critical-path proposals are checked against a replay of the
  pipeline before anyone edits a `waitFor` edge.

## 4. Facets

Rows of the sparse matrix, from cheap to expensive to obtain:

- declared: build system (Bazel, Gradle, Xcode), platform (iOS, macOS, Linux), remote execution
  on or off, repository and target count, toolchain version, change type (source, build file,
  dependency bump, config), change size;
- derived by a triage skill: failure class, subsystem, whether the failing target is on the
  critical path.

Empty cells back off along the facet hierarchy and say which level the estimate came from.
Calibration fills the cells the real traffic hits, weighted by frequency.

## 5. The objective is asymmetric

Two error costs, not one:

- `h_false_pass`: a real failure annotated as a flake and allowed through. Ships a defect,
  costs an incident or a rollback. Large.
- `h_false_fail`: a flake left as a failure. Costs an engineer a rerun and some minutes. Small.

The objective a CI-triage role minimizes is

```
tokens + CI minutes + engineer waiting minutes + h_false_pass × false passes + h_false_fail × false fails
```

subject to a latency tolerance per event (a verdict that arrives after the engineer has already
rerun the build is worth nothing). The selector will choose the cheap classifier alone only
where its measured false-pass rate on that facet is low enough; elsewhere it escalates. That is
the review lesson (security bugs need the strong tier) with the stakes made explicit.

## 6. Policy: fixed human nodes

- The agent may rerun, annotate, propose, open a ticket, draft a fix.
- Marking a real failure as passed, changing a shared pipeline definition, and promoting to
  production are fixed human bindings. The selector cannot trade them away.
- Every AI-initiated action is attributable, replayable and has a kill switch. The automation
  must fail safer than the manual process it replaces.

## 7. Corpus and feedback loop

The corpus is the build history with its dispositions: failures joined to reruns, fix commits,
reverts and infrastructure tickets by build id. Labeling is a query, not a person. Because
labels arrive within hours, the feedback loop can run daily: new dispositions become new
corpus rows, profiles are recalibrated per facet, and the false-pass rate is tracked as a
first-class metric with its own alert.

Two biases to correct for: a verdict that triggers a rerun changes what is observed next
(the rerun result is conditioned on the verdict), and failures nobody investigated have no
disposition and must not be treated as flakes by default.

## 8. What the role reports

At role level the objective is the delivery metrics the team is accountable for:

| DORA / SPACE signal | what the instance measures |
|---|---|
| lead time for changes | engineer waiting minutes per failure, before and after |
| change failure rate | false passes that shipped |
| time to restore | time from failure to correct verdict |
| deployment frequency | pipeline duration on the critical path |
| satisfaction (SPACE) | reruns per engineer per week, and whether verdicts are trusted or ignored |

A results table for this instance has the same shape as the review table: one row per flow,
strict and loose columns (exact class versus real-or-not), false passes and false fails as
separate columns, engineer minutes instead of dollars as the headline cost.

## 9. What the engine needs

Nothing, if the abstraction holds: a scenario plugin with `load_tasks` (build records),
`validate`, `render` (a failure record and its logs into the skill's prompt or tool call),
`parse_output` (verdict schema) and `score` (disposition match). Two additions the review
instance did not need and that belong in the engine: a second cost dimension (engineer
minutes) and an objective with two error weights. Both are data, not selection code.
