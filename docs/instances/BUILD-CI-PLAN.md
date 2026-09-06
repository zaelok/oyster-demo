# Implementation plan: the build and CI instance

How to take [`BUILD-CI.md`](BUILD-CI.md) from a design to a table, in the order that produces
a defensible number soonest. Each phase ends with a definition of done that is a measurement,
not a feature list. Phases 0 and 1 need no access to any organization's systems; they run on
public Bazel repositories and the subscription routes this repository already has.

## Phase 0. First table on public data (two to three days)

**Goal.** A `results/build-ci-*/results.md` with one row per triage flow, strict and loose
columns, false passes and false fails as separate columns, produced by the unchanged engine
through a `build_ci` scenario plugin.

**Corpus.** 40 to 60 failed CI runs from public Bazel monorepos with a disposition the history
already contains. Candidates: `bazelbuild/bazel`, `bazelbuild/rules_go`, `envoyproxy/envoy`,
`grpc/grpc` (all Bazel, all with years of GitHub Actions or Buildkite history). Labeling is a
query over the history, not a person:

| disposition in history | label |
|---|---|
| same commit rerun passed with no change | environmental flake |
| next commit on the branch touched the failing target and passed | real failure |
| failure text names a fetch, network, quota, or runner error | infrastructure |
| failing target depends on a bumped external dependency | dependency drift |
| failure disappears after a cache purge or a `--nocache` rerun | cache problem |
| step exceeded its time limit | timeout |

Store each case as a task file: build id, repository, commit, target, the failing step, a
bounded log excerpt (the last N lines plus the first error block), the change metadata
(files, size, type) and the label. A `tools/ci_to_case.py` in the shape of
`tools/pr_to_case.py` does the fetching and the excerpting; the human confirms labels.

**Skill and scorer.** One leaf, `build-ci/triage`: log excerpt and change metadata in, a class
plus a confidence out. Scorer: strict is the exact class, loose is real-or-not (real failure
versus everything else). False pass is a real failure classed as anything else; false fail is
a non-real classed as real. Both are reported per flow.

**Flows.** A: one cheap classifier. B: cheap classifier, escalate to a strong log-reader when
the class is real or the confidence is below a threshold. C: strong log-reader alone. The
selector's job is to find the threshold at which B beats both.

**Executors.** Haiku 4.5 and Sonnet 5 through the subscription routes; a deterministic
baseline (regex over known error signatures) as a tool executor, because a model has to beat
the grep it replaces.

**Definition of done.** The table exists, with confidence intervals, and the false-pass rate
per flow is a number with an interval, not an adjective.

## Phase 1. Root cause and test selection (one week)

**Root-cause location.** Leaf `build-ci/locate`: the failing target, step and log span that is
the cause. Scorer: span overlap with the lines the fixing commit's author cited or the code
they changed, structural like the review matcher. Corpus: the real-failure subset of phase 0
joined to the fixing commit.

**Test selection.** Leaf `build-ci/select-tests`: change in, set of targets and tests out.
Scorer: recall against the tests a retrospective full run shows failing; cost as the size of
the selected set in targets or minutes. Baseline: `bazel query rdeps` of the changed files, the
deterministic tool every proposal must beat on recall at equal cost. Corpus: commits from the
same repositories with a full CI run available, which is most of them on the main branch.

**Definition of done.** For each leaf, a calibrated profile per facet (build system, platform,
change type) with N and intervals, and a first two-level composite measured end to end:
triage, then locate, with the composite's profile compared against the product of its leaves
so the independence error is stated for this domain as it was for review.

## Phase 2. Pipeline analysis (one week, needs pipeline definitions)

**Critical path.** Leaf `build-ci/critical-path`: a pipeline definition (GitHub Actions, Cloud
Build, Buildkite) and step timings in; the serialized edges that could run in parallel and a
predicted saving out. Scorer: predicted versus measured duration after the change is applied,
on a replay of the pipeline with the edge removed. Corpus: public pipeline definitions with
timing history.

**Cache-key correctness.** Leaf `build-ci/cache-keys`: configuration and change in, keys that
may collide across branches out. Scorer: replay under both branch states. The warm-cache
cross-branch poisoning case from the review corpus's era is the first seeded case.

**Definition of done.** A proposal is accepted only when the simulated saving matches the
measured one within the interval; the false-positive column here is "proposals that would
have broken the pipeline".

## Phase 3. Organization integration (two to four weeks, needs access)

- **Event stream.** Build and pipeline events, log excerpts and dispositions joined by build
  id into the corpus format, daily.
- **Daily recalibration.** `calibrate` on the new rows per facet; profiles carry their date;
  the false-pass rate is a first-class metric with an alert.
- **Policy layer.** Fixed human nodes as configuration: marking a real failure as passed,
  editing shared pipeline definitions and production promotion are never selectable. A kill
  switch that reverts every flow to the deterministic baseline.
- **Surfaces.** Verdicts as annotations on the build, a proposal as a draft change with the
  evidence attached, never a mutation. Integration through the existing paved road (the CI
  system's annotation API, a bot account with scoped permissions), not a new one.
- **Reporting.** The role's objective is the delivery metrics: engineer waiting minutes per
  failure, false passes that shipped, time to correct verdict, reruns per engineer per week.
  The results page gains those columns; DORA and SPACE names appear where they map.

**Definition of done.** Two consecutive weeks of the false-pass rate under the agreed ceiling
with the interval inside it, verdict trust measured (do engineers act on annotations or rerun
anyway), and an audit trail that answers "why did the system say flake" for any build.

## Risks and how the plan meets them

| risk | mitigation |
|---|---|
| labels from history are wrong (a rerun passed by coincidence) | replicate policy: a flake label needs two consistent dispositions; the label source is a facet, results are sliced by it |
| log excerpts leak the answer (an infra error string) | the deterministic baseline sees the same excerpt; the question is what the model adds over grep |
| false-pass cost is set by hand | derive it from measured incident cost per shipped defect where the organization has the number; otherwise state the assumption in the results header |
| the model learns the repository, not the skill | hold out repositories: calibrate on some, test on others, report both |
| engineers ignore or over-trust verdicts | trust is measured (SPACE), and confidence gating is calibrated, not fixed |

## What this reuses

Everything: the executor, selector, calibration, rendering, fixtures, conversation mode and
the CLI provider. The new code is a scenario plugin (`oyster/scenarios/build_ci.py`), a
corpus tool (`tools/ci_to_case.py`), a registry entry, and two objective weights. If the
plugin needs an engine change, the change is the finding.
