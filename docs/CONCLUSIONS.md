# Conclusions after four runs

What the measurements support, what they do not, and what would change them. Written
2026-09-07 after the fourth run; every number below traces to a `results/<run>/results.json`
and a retained fixture holding the model's verbatim reply.

Measured so far: one model pair (Claude Haiku 4.5 as cheap-model, Claude Sonnet 5 as
strong-model), three executor configurations, two corpus tiers, four runs, about 1,270 CLI
calls and six chat messages. Not measured: any other model pair, any replicate of a run, the
style category.

## The runs

| run | harness and settings | tokens | corpus | A single cheap pass | B cascade | C reviewer → critic → reviewer | selector chose | measured best |
|---|---|---|---|---|---|---|---|---|
| 1 | claude.ai chat: Haiku thinking off, Sonnet medium | estimated (`chars // 4`) | reviewed, 17 cases / 21 bugs | 15 · $0.012 | 16 · $0.045 | 14 · $0.098 | C | B |
| 2 | Claude Code CLI defaults: Haiku adaptive thinking, Sonnet default | API-reported | reviewed | 13 · $0.513 | 18 · $0.641 | 18 · $0.325 | C | B = C |
| 3 | CLI: Haiku thinking off (`OYSTER_CHEAP_EFFORT=none`), Sonnet default | API-reported | reviewed | 18 · $0.025 | 18 · $0.141 | 20 · $0.302 | C | C |
| 4 | as run 3 | API-reported | auto, 183 cases / 314 bugs from 89 repositories | 192 · $0.313 | 184 · $2.630 | 177 · $5.496 | C | A |

Cells are strict catches · dollars at API list rates. Runs 1 to 3 score the same 21 bugs.
Sources: [`results/conversation-haiku45-sonnet5/`](../results/conversation-haiku45-sonnet5/),
[`results/cli/summary.md`](../results/cli/summary.md),
[`results/cli-auto/summary.md`](../results/cli-auto/summary.md).

Strict catch rates on run 4 with Wilson 95% intervals: A 0.61 (0.56 to 0.66), B 0.59 (0.53
to 0.64), C 0.56 (0.51 to 0.62). False positives 16, 25, 21. No halts, no parse failures.

## Calibrated priors, each skill alone

| skill | executor | run 1 (n = 17 logic / 4 security) | run 3 (same n) | run 4 (n = 282 / 32) |
|---|---|---|---|---|
| cheap-scanner, logic | Haiku 4.5 | 0.82 (0.59 to 0.94) | 1.00 (0.82 to 1.00) | 0.66 (0.61 to 0.72) |
| cheap-scanner, security | Haiku 4.5 | 0.25 (0.05 to 0.70) | 0.25 | 0.16 (0.07 to 0.32) |
| deep-reviewer, logic | Sonnet 5 | 0.71 (0.47 to 0.87) | 1.00 (0.82 to 1.00) | 0.60 (0.54 to 0.66) |
| deep-reviewer, security | Sonnet 5 | 0.50 (0.15 to 0.85) | 0.50 | 0.19 (0.09 to 0.35) |
| critic, logic (alone, with nothing to judge) | Sonnet 5 | 0.94 (0.73 to 0.99) | 0.71 | 0.33 (0.28 to 0.39) |
| critic, security | Sonnet 5 | 0.50 | 0.50 | 0.12 (0.05 to 0.28) |

The reviewed tier's intervals span half the unit interval; the auto tier's are five to six
points wide. That difference is the reason the auto tier exists.

## What the runs support

1. **Spending more did not catch more.** On the 314-bug tier the cheap single pass caught the
   most: 192 against 184 and 177, at an eighth of the cascade's cost and a seventeenth of the
   critic loop's ($0.0016, $0.0143 and $0.0311 per bug caught), with overlapping intervals on
   the rates and none on the costs. On the 21-bug tier it trailed once, in run 2, by five bugs
   (13 against 18), in the setting where it was made to think; with thinking off (run 3) it
   caught 18 and C's 20 was inside the noise that run 4 then resolved.

2. **"Security" is a category disagreement, not a detection hole.** On run 4 the 32 bugs
   whose PR text carried security vocabulary were found at the loose level 29, 29 and 25
   times by A, B and C, the same rate as the other 282, and labelled security 5, 6 and 6
   times: the models call them logic. On the reviewed tier the four security bugs went 1 to 3
   of 4 loose across runs, too few to say anything. An earlier draft of this document called
   this a hole every path shared; it is a disagreement between a keyword label and a model
   about what "security" means, and adjudicating it is a person's job, which is what the
   reviewed tier is for and why the sparse matrix keeps facets and executors apart.

3. **An executor is a model plus its settings plus its harness.** At the CLI's default, Haiku
   4.5 spent a median 4,900 output tokens per call thinking, took 46 seconds, cost twenty
   times the same model with thinking off ($0.51 against $0.025 for the same 17 calls), and
   caught fewer bugs (13 against 18). A registry entry
   that names only the model is not an executor, and a results table whose header does not
   name the settings is not comparable to anything.

4. **The independence prior over-predicts multi-node flows, by construction.** Under
   1 − ∏(1 − r) a path with more nodes can never predict lower quality than its prefix, and
   the predicted costs ($0.02 to $0.04 per case) never approach the $1 budget, so the longest
   feasible path wins whenever the budget is slack. The selector chose C in all four runs (in
   run 2 by elimination: A and B failed the 120 s latency tolerance on Haiku's p95 of 188 s;
   unconstrained, C still ranked first at 0.57 against 0.47 and 0.32); C was best in one. The
   printed predicted quality also averages over three categories including style, which has
   no calibrated rate and contributes zero, so it is not on the scale of the measured rate.
   Two mechanisms, both visible in the retained
   results: a critic re-judges the findings it is handed rather than detecting independently
   (alone it catches 0.33 of logic bugs on the auto tier, the lowest of the three skills), and
   the last-node-wins transfer rule lets a later reviewer drop an upstream catch. Both mean
   the nodes are not independent detectors, which is the one assumption the selector makes
   without measuring. The remedy is already specified (SKILL-FOREST §2): a flow that has been
   run gets its own measured prior and the formula is used only for flows never run.

5. **Label quality can be measured.** 43 of A's 235 loose catches on run 4 (18 percent) sat
   on the seeded lines with a different category from the keyword rule's; 24 of the 43 are the
   security cases of point 2. Some of that disagreement is the model's, so 18 percent is an
   upper bound on the auto tier's category noise, not a point estimate. Two more facets of the
   labels show through: bugs the
   fix corrected by adding code (the seeded range is the neighbouring lines) were caught 50 to
   52 percent against 60 to 66 for bugs on replaced lines; and bugs from PRs merged in
   August and September 2026 were caught 57 percent against 68 for earlier ones, intervals
   overlapping. Training-data contamination cannot be the reading for path A: Haiku 4.5's
   published cutoff precedes every PR in the corpus. A shift in the repository mix over time
   is the remaining candidate, and this data cannot test it.

6. **With a person in the loop the dollar column stops deciding, but not always the same
   way.** On the reviewed tier a human cost `h` above about three cents per missed bug flips
   the choice from A to B (run 1). On the auto tier no `h` flips it, because the cascade
   costs more and catches fewer. The lever on that tier is the security hole, not the path.

## What the runs do not show

- **A no-model baseline scores like a model.** Flagging every non-trivial added block as a
  logic bug scores 180 of 314 strict (202 loose, 0 false positives) on the auto tier and 17
  of 21 on the reviewed tier, at $0, because a reversed fix makes every changed block a seeded
  bug and the corpus has no decoy hunks. The tables compare paths on the same task; they do
  not measure recall against an absolute bar, and precision is only the false-positive count.
  Decoy hunks are the fix.
- **Two auto-tier cases carry inline test names** (codex-5016, codex-4944: Rust `#[test]`
  functions survived the test-file filter, which is path-based), and the comment stripper
  removed `#`-prefixed code lines (attributes, preprocessor directives) from removed sides.
  The tool is fixed for future builds; the committed cases are unchanged so the numbers stay
  reproducible, and both are listed in the tier's README.
- **Variance across settings is large and no configuration has been replicated.** The same
  21 bugs gave A 15, 13 and 18 strict catches across three runs under three settings (chat
  with estimated tokens, CLI thinking on, CLI thinking off). Each run is one replicate; the
  platform design asks for k of them under a run manifest, and until they exist a one- or
  two-bug difference between paths on the reviewed tier is noise by construction.
- **One model family and one prompt set.** Whether a materially stronger deep reviewer (Opus
  5 or Fable 5.1 behind a Haiku scanner) rescues the cascade is the obvious next question and
  the cascade's best case; it has not been run.
- **Reversed fixes are easier than wild bugs.** The reviewer sees correct code being replaced.
  The auto tier's labels are unreviewed; the reviewed tier's 21 bugs are too few to bound
  anything tightly. The two tiers are reported separately for that reason and never merged.
- **The CLI's scaffolding is inside the token counts.** Input tokens through the CLI are about
  double the bare prompt; the API route would be cheaper in absolute terms, with the same
  ordering.
- **Style was never measured**: no seeded style bugs in either tier.

## What would change the conclusions

- A strong-model that is clearly stronger than the scanner on this corpus, which would give
  the cascade its case; Sonnet 5 alone (0.60 logic) was not better than Haiku 4.5 alone (0.66).
- A security-specialised executor, which would test whether the hole is a property of the
  executors or of the task.
- Three replicates per configuration, which would turn the reviewed tier's differences into
  intervals instead of anecdotes.
- Measured flow priors in the selector, which would test whether the selector's mistake is
  the formula or the inputs.

## Next runs, in cost order

Dollar figures are API list rates for the subscription route, which bills nothing; a run
through the API would cost roughly two thirds of the figure because the bare prompt is
shorter. Each is one `tools/run_matrix.py` command.

| run | calls | list-rate equivalent | what it answers |
|---|---|---|---|
| Sonnet 5 + Opus 5 on the reviewed tier, thinking off | ~100 | ~$2.5 | Opus's default token behaviour before spending more |
| Sonnet 5 + Opus 5 on the auto tier | ~1,100 | ~$25 | the cascade's case with a stronger reviewer |
| Haiku 4.5 + Fable 5.1 on the auto tier | ~1,100 | ~$48 | same, with the strongest available reviewer |
| Haiku default thinking on the auto tier | ~180 | ~$5 | whether thinking hurts the scanner at n = 314 as it did at n = 21 |
| three replicates of run 4 | ~2,200 | ~$22 | run-to-run variance |
