# Code walkthrough: thirty minutes through OYSTER

A reading order for someone who wants to understand what the numbers in `results/` mean and
how they were produced. Each stop names the file, what to look at, and the rule that governs
the numbers. The rules are the point: the table is only as honest as the rules that made it,
so they are specified in [`BUILD-SPEC.md`](BUILD-SPEC.md) rather than left to taste.

## Stop 1. The claim (`README.md`, 3 min)

Three review strategies are paths through one graph. The same code prices, runs, scores and
ranks every path. The claim under test: an orchestrator that measures its own priors can pick,
under an explicit budget, a strategy whose bugs-caught-per-dollar beats any fixed one, and can
show its work. The deliverable is the table, plus the honest account of where the prediction
was wrong.

## Stop 2. The table (`results/conversation-haiku45-sonnet5/results.md`, 5 min)

Read the header first: which models, which rates, which provider, which corpus commit. A table
without those lines is not reproducible. Then the three rows. Then the per-case tables: every
strict catch, loose catch, miss and false positive is listed per case, so any cell in the
summary can be traced to a case id, and from the case id to a `PathResult` in `results.json`,
and from there to the fixture holding the model's verbatim reply.

Strict and loose are separate columns. Strict means the finding overlapped the seeded range
and named the same category; loose ignores category. When they are equal, every overlapping
finding also got the category right.

## Stop 3. One case (`oyster/corpus/cases/case-servicetalk-3554.json`, 3 min)

A case is a unified diff plus seeded bugs. This one is one hunk: the fix changed
`getShort(index) & 0xfff` to `& 0xffff`; reversed, the diff shows the correct line being
replaced by the buggy one, and the seeded bug points at the new-file line with the buggy mask,
category `logic`, with a description that states what is wrong. The `source` field is the pull
request it came from. Line numbers are new-file side, and the validator (`oyster/corpus`)
refuses a bug whose range is not inside a hunk on that side.

Notice what the model sees: the removed line is the fix. That is why these cases are easier
than wild bugs, and why the README says so.

## Stop 4. Matching (`oyster/matching/__init__.py`, 5 min)

Every number in the table passes through `match()`. The rules, in order:

1. A finding **overlaps** a bug when both name the same file and their inclusive line ranges
   share at least one line.
2. **Strict** catch: overlap and equal category. **Loose** catch: overlap, category ignored.
   Every strict catch is also a loose catch.
3. Each finding goes to **at most one** bug: the largest overlap, ties to the lowest bug id.
   Deterministic by construction.
4. Each bug is caught by **at most one** finding. A second finding on an already-caught bug is
   ignored: not a catch, not a false positive.
5. A finding overlapping no bug is a **false positive**; only the count is reported.
6. `missed` is every bug id not caught loosely.

Worked example from the tests: a finding spanning lines 1-10 against bug b1 at 1-2 and b2 at
5-10 is assigned to b2 (overlap 6 beats 2), so b1 is missed. Findings are processed in the
order the model returned them, so which finding claims a bug is fixed given the reply.

## Stop 5. Executor (`oyster/executor/__init__.py`, 7 min)

`run_path()` executes one path over one case. What governs the numbers:

- **Hooks run before every node.** The first non-None reason halts the run and returns a
  partial `PathResult` with the reason set. A halted run is data, not an error.
- **The diff is passed once, as `cached_prefix`.** `render_messages()` in `oyster/prompts`
  renders the template with the diff slot left empty and hands the diff separately, so the
  provider can cache it and the model sees it exactly once.
- **Upstream findings** are the union over incoming edges, deduplicated by
  `(file, line_start, line_end, category)`, ordered by file then line. They fill the template's
  `EARLIER FINDINGS` or `FINDINGS UNDER REVIEW` block. With no upstream findings, the block is
  empty, which is why a downstream prompt can coincide with a first-round one.
- **Parsing.** A reply that is not a JSON object with a `findings` list is retried once with
  the repair suffix; a second failure records `parse_failed=True` and empty findings. The cost
  of both calls is kept. Findings on files absent from the diff are discarded and counted, so
  a hallucinated path cannot become a false positive.
- **Last node wins.** `PathResult.findings` is the last node's findings, not the union. A
  cascade's later stage is meant to supersede the earlier one, and the critic path depends on
  it: if findings accumulated, a critic could never drop a false positive.

The last rule explains the first run's biggest surprise. In three cases the first reviewer
caught the bug, the critic kept it, and the final reviewer re-described it at a line range
that no longer overlapped the seeded one. Upstream catch, downstream miss, by the rule.

## Stop 6. Selector (`oyster/selector/__init__.py`, 5 min)

`predict()` prices a path as the sum over nodes of the calibrated mean cost, and scores it as

```
quality = mean over categories of  1 - prod over nodes of (1 - catch_rate[role, model, category])
```

which is the probability that a bug of average category mix is caught by at least one node,
**if the nodes were independent detectors**. The module docstring says the assumption is false
and that knowing where it is false is part of the deliverable.

`select()` rejects in order: no priors, predicted latency over tolerance, predicted dollars
over budget; then returns the highest predicted quality, ties to lower dollars, then path id.
With no survivors it names the constraint and the cheapest infeasible option instead of
degrading silently. A comment marks where a heuristic search would attach; enumeration is over
the catalog only.

With the first run's priors (logic / security, no style bugs in the corpus):

| path | predicted quality | measured strict |
|---|---|---|
| A | (0.82 + 0.25 + 0) / 3 = 0.36 | 15 / 21 = 0.71 |
| B | (0.95 + 0.63 + 0) / 3 = 0.52 | 16 / 21 = 0.76 |
| C | (0.99 + 0.88 + 0) / 3 = 0.62 | 14 / 21 = 0.67 |

Predicted order C > B > A. Measured order B > A > C. The selector picked C under a one-dollar
budget and was wrong. Two mechanisms: the nodes are not independent (the critic and the second
reviewer re-judge the reviewer's findings instead of adding new detections), and last-node-wins
turns location drift into misses. The fix is a v2 item: calibrate priors per whole path, or
model the correlation, and the README says which.

## Stop 7. Calibration and rendering (`oyster/evaluation/__init__.py`, 3 min)

`calibrate()` runs each distinct `(role, model, prompt)` **alone** over every case and records
`strict catches / seeded bugs` per category, plus the mean cost per node config. Those are the
priors the selector uses: measured on this corpus, valid for this corpus. `evaluate()` runs the
full paths. `render_results()` writes the table with the rules in the header comments: every
path gets a row, strict and loose never merge, `$/bug` is `n/a` rather than infinity when
nothing was caught.

## Stop 8. Cost (`oyster/cost/__init__.py`, 2 min)

```
dollars = (input - cached) * rate_in / 1e6 + cached * rate_in * (1 - cache_discount) / 1e6 + output * rate_out / 1e6
```

Latency sums along a path because this slice runs nodes serially; the comment in `path_cost`
says what changes if branches run in parallel. `estimate_tokens` is `chars // 4` and is used
only where a provider cannot report counts; the results header says when that happened.

## Stop 9. Providers (`oyster/providers/`, 3 min)

- `mock_provider`: keyed by `sha256(model_id + system + user + cached_prefix)[:16]`; a miss
  returns a valid empty reply and logs the key, so CI with zero fixtures still produces a
  complete, honest table.
- `recording_provider`: wraps any provider and writes fixtures with that key.
- `anthropic_provider`: diff in a `cache_control` system block, usage from the response, never
  estimated; retries 429 and 5xx only.
- `claude_code_provider`: the same request through the Claude Code CLI on a subscription, token
  usage from the CLI's JSON result.
- `oyster/conversation`: the fixture-filling loop that lets any chat window stand in for a
  provider, with estimated token counts and rounds that converge because later prompts depend
  on earlier findings.

## Stop 10. Where the corpus came from (`tools/pr_to_case.py`, 2 min)

Merged bug-fix pull requests from public repositories, reversed so the fixed code is the
before side and the buggy code the after side. Tests, mocks and docs are dropped because a
deleted regression test gives the answer away; the fix's own comments are stripped from the
removed lines; a leak check flags words like "fix" and "SSRF". A human confirmed every
category, range and description; `oyster/corpus/cases/SOURCES.md` links each case to its PR.

## Questions this design invites

- Why reverse fixes instead of planting bugs by hand? Real defects with real ground truth,
  at the price of an easier diff and possible training-data contamination. Both are disclosed.
- Why last-node-wins rather than union? Because a critic must be able to drop findings. The
  cost of that choice is now measured; a fourth path with union semantics would be one more
  entry in the catalog, no selection code.
- Why is the selector's model wrong, and does it matter? Independence overestimates multi-node
  paths. It matters exactly as much as the gap between predicted and measured, which the table
  shows; the next step is per-path calibration.
- What would change the conclusion? A human baseline on the same diffs, a larger corpus with
  bugs from bug-introducing commits, and a run with API-reported tokens.
