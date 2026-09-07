# Related work

What exists next to each part of the skill-forest vision, and what the vision adds. This is a
snapshot from a set of web searches on 2026-09-06, not a systematic review; papers are cited by
arXiv id where they have one, and everything else by URL in the source list at the end. The
short version: every component has neighbors, several of them strong; nobody found here
combines priors calibrated on the owner's own corpus, selection over multi-step flows under the
owner's objective including human cost, provenance to the raw reply, and one registry that
holds models, tools and people as executors.

## 1. Model routing and cascades (single-step selection)

The oldest and busiest lane. FrugalGPT introduced the cascade (query cheap models first,
escalate on low confidence) and reported large cost reductions; AutoMix estimates reliability by
self-verification before escalating; RouteLLM learns a router from human preference data;
RouterBench standardized evaluation with 36,497 queries answered by 11 models with quality and
cost recorded per answer, and TwinRouterBench (2026) extends that to agentic settings. Newer
work adds calibrated uncertainty for cascade decisions (UCCI, 2605.18796), conformal cascading
with distillation (RouteNLP, 2604.23577), cluster-then-escalate serving (2606.27457), and a 2026
survey that formalizes the shared objective as choosing a model under a cost budget
(2603.04445). Commercially, gateways such as Not Diamond, Martian, OpenRouter, LiteLLM, Portkey
and TrueFoundry do routing and cost tracking across vendors.

What differs: these decide one model for one query, and their priors are learned on the
vendor's or a benchmark's data. OYSTER's unit of selection is a multi-node flow (a cascade is
Path B, an escalate-on-low-confidence rule is a flow pattern), its priors are calibrated on the
owner's corpus, and its objective belongs to the owner and can include the cost of a miss.

## 2. Optimizing compound AI systems

Archon (2409.15254) searches over inference-time architectures (ensembling, sampling, fusion,
ranking, critiquing, verification) under a compute budget with Bayesian optimization, and
reports state-of-the-art results with fewer calls and tokens. SCOPE (2606.00774) does
cost-efficient model selection for compound systems under quality constraints, the closest
academic sibling to OYSTER's selection objective. ProgRouter (2608.25992) routes online, step by
step, against progress, time budgets and operating cost; difficulty-aware orchestration
(2509.11079) pairs each operator with a model from a candidate set; confidence-aware routing
(2601.04861) assigns model capacity per turn from a multi-scale pool; a 2026 deployment study
covers scalable inference architectures for compound systems (2604.25724).

What differs: these optimize configurations against public benchmarks; the candidates are
found by search and are hard to audit. OYSTER enumerates candidate flows as data, calibrates
each end to end, records why one was chosen, and marks the seam where an Archon-style search
would attach. ProgRouter's online re-planning is the runtime re-planning the architecture
document lists as a non-goal for this slice.

## 3. Metric-driven program optimizers

DSPy's optimizers (BootstrapFewShot, MIPROv2, COPRO, GEPA) tune the prompts and few-shot
examples inside a declarative LM program against a metric; GEPA (2507.19457, ICLR 2026) uses
natural-language reflection instead of policy gradients and reports beating GRPO with far fewer
rollouts; TextGrad backpropagates textual feedback through workflows and Trace (2406.16218)
generalizes that over execution traces.

What differs and how they combine: they change the skill (its prompt); OYSTER freezes the
prompt and chooses among flows and executors. A DSPy- or GEPA-optimized skill is simply a
binding whose profile OYSTER measures. One caution the combination creates: optimizing a prompt
on the calibration corpus inflates that corpus's priors, so the calibration set must be held
out from the optimizer.

## 4. Bandits and exploration

Routing as online learning: MetaLLM frames model choice as a multi-armed bandit; MixLLM uses
contextual bandits with a knapsack cost constraint; GreenServ (2026) runs LinUCB over sixteen
open models; cost-aware multi-objective bandits for budgeted configuration evaluation
(2608.04333); online multi-LLM selection under context drift (AAAI); CUPID (2606.00846) as
online matchmaking; a 2025 survey of bandits meeting LLMs (2505.13355).

Relation: the platform document's exploration budget is a bandit, and the per-cell sample size
and interval in a profile are exactly the state a bandit needs. OYSTER's first slice has no
exploration; this lane is where it comes from.

## 5. Evaluation and observability platforms

Braintrust (scorers, experiment diffs), LangSmith (tracing and evals for LangChain and
LangGraph), Langfuse (self-hostable, online evaluation of live traffic by a sampled judge),
Inspect AI, promptfoo (declarative comparisons and release gates), Arize and others; 2026
comparisons note that most teams rate their evaluation setup inadequate. OpenTelemetry's GenAI
semantic conventions standardize model, token-usage and finish-reason attributes on spans,
with agent, tool-call and multi-agent conventions in progress; as of 2026 they are still
experimental and explicitly do not cover output quality evaluation.

Relation: these hold traces and scores; OYSTER's fixture, keyed by a hash of the exact prompt,
is what makes a run replay bit for bit, and its profile (rate, n, interval, p50, p95, manifest)
is a thing these platforms could emit. `Completion`'s fields map onto the OTel attributes
(`gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`), which is the adoption path.

## 6. Code review agents and their benchmarks

Martian published an independent benchmark of 17 review tools over 300,000 real pull requests
in February 2026; CodeAnt and Entelligence publish precision, recall and F1 comparisons;
DeepSource reports the highest F1 on the OpenSSF CVE benchmark. False positives are the
industry's first complaint: Greptile shows the highest catch rate and the highest false-positive
rate; Cursor's BugBot runs eight parallel passes with randomized diff order on every pull
request.

Relation: the same spirit, measured on someone else's corpus. OYSTER measures on the owner's
diffs, reports strict, loose and false positives as separate columns per flow with cost, and
prices each flow; BugBot's eight randomized passes is an ensemble pattern OYSTER could price as
a flow.

**Closest prior claims to the four-run result** (checked 2026-09-07; no post or paper with the
same setup and the same set of conclusions was found):

- *Bigger Isn't Always Better: A Comparative Evaluation of LLMs for Automated Code Review*
  (arXiv 2606.15689) finds Haiku beating Sonnet on recall in review (0.293 against 0.248, F1
  0.365 against 0.343) at 3.2 times lower cost. Same direction as OYSTER's scanner-alone
  against reviewer-alone priors (0.66 against 0.60 on logic bugs); a single-model comparison,
  no flows, no selector.
- *More Rounds, More Noise: Why Multi-Turn Review Fails to Improve Cross-Context Verification*
  (arXiv 2603.16244): single-pass review reached F1 0.376 on 150 injected errors while
  multi-turn variants fell to 0.303, because reviewers fabricate findings once real errors are
  exhausted. Same direction as OYSTER's critic loop; different mechanism named (noise from
  re-review rather than last-node-wins drift), and no cost column.
- Qodo's 400-PR Haiku 4.5 against Sonnet 4 benchmark (judge-scored quality, thinking with a
  4,096-token budget) found thinking improved both models. OYSTER measured the opposite for
  recall on seeded bugs under the CLI's adaptive thinking (13 against 18 of 21), which spent
  a median 4,900 tokens per call; the two are not the same executor, which is the point of
  the finding.
- Greptile's benchmark builds its corpus the way OYSTER's does, by tracing a merged fix back
  to the change that introduced the bug and reintroducing it as a fresh PR; Qodo injects bugs
  into merged PRs instead. Neither publishes a two-tier corpus with measured label noise.
- *A Theoretical Framework for the Security of Multi-stage LLM Output Filtering Pipelines*
  (Springer 2026) shows independence-based estimates are systematically wrong under natural
  dependence between stages, which is the selector's failure stated in general.

What is not found elsewhere is the combination: the owner's corpus, priced flows with an
explicit transfer rule, a selector whose independence prior is measured against the flows it
ranked, the security facet as the shared hole across flows and runs, and the executor recorded
as model plus settings plus harness because the harness alone moved cost forty times.

## 7. Bug corpora and ground truth

SWE-bench (2,294 instances from 12 Python repositories) and SWE-bench Verified, whose instances
are rebuilt at the base commit and checked with the developer patch under the same test suite;
Defects4J (800+ Java bugs with tests that expose them); BugsInPy; SZZ for bug-introducing
commits, with recent work on its label noise (2605.27880); a 2025 survey of defect datasets
(2504.17977).

Relation: OYSTER's reversed-fix corpus is a lightweight cousin of these; SWE-bench Verified's
oracle (tests pass under the developer patch) is exactly the bug-fixing scenario's strict tier;
SZZ is how the corpus moves from reversed fixes to bug-introducing commits, the realism upgrade
the README names.

## 8. CI failure triage and root cause

Google's Auto-Diagnose (2604.12108) diagnoses integration-test failures with an LLM and
surfaces the relevant log lines inside Critique; an LLM-driven CI failure diagnosis and repair
pipeline from GitHub Actions logs; an AI-assisted flaky-test triage pipeline that decomposes
root-cause analysis into temporality, necessity and sufficiency sub-tasks and reports an F1 of
0.81 zero-shot against a 0.58 baseline; NeuroFlake (2605.11482) for neuro-symbolic flakiness
classification; Meta's Engineering Agent for failing unit tests.

Relation: each is one skill of the build/CI instance. The instance composes them under an
asymmetric objective (a false pass costs more than a false fail) with fixed human nodes; their
reported F1s are candidate cells in its matrix.

## 9. Agent skill registries

By early 2026 more than 280,000 agent skills were public across registries (ClawHub, Skills.sh,
SkillsDirectory, LobeHub); research covers ecosystem-scale organization and benchmarking
(2603.02176), same-capability ambiguity (SkillResolve-Bench, 2606.10388), skill-centered
assessment (SkillAudit, 2606.22613), evaluation at scale (2606.17819), SkillsBench with 87 task
packages, supply-chain security of SKILL.md (2603.00195, 2605.11418, SkillProbe 2603.21019),
and agent-economy market designs (Agent Exchange, 2507.03904). One of these papers states that
dynamic capability assessment is a foundational requirement for agent marketplaces.

What differs: registries declare capabilities; the skill forest registers a skill only with a
contract, a scorer and a corpus, measures each executor against it, and derives levels from
composition. SkillsBench and SkillAudit are the measurement direction the registries lack.

## 10. Human skills taxonomies and assessment

O*NET (1,000+ occupations), ESCO (multilingual EU classification), Lightcast's open taxonomy
(32,000+ skills, refreshed every two weeks), and proprietary graphs from Eightfold, Workday,
Beamery and Gloat; platforms infer proficiency from profiles and work signals.

What differs: taxonomies and inferred proficiency without an owner objective, a cost model or
composition into flows. The skill forest puts people and models in one matrix with the same
profile shape, and lets the owner's weights decide who does what.

## 11. Delegation between people and agents

Intelligent AI Delegation (2602.11865) frames delegation as transfer of authority,
responsibility and accountability with negotiated specifications and verification; a CHI 2026
paper on how repeated delegation erodes human agency; earlier work on optimizing delegation
between human and AI agents (2309.14718) and field experiments on human-agent teamwork
(2503.18238).

Relation: OYSTER's objective with a cost per miss and fixed human nodes is a minimal,
measurable delegation rule; those frameworks' accountability transfer is where the platform's
policy layer would grow.

## 12. Judges

Large 2026 evaluations of LLM-as-judge reliability report inconsistency across prompts and
runs, systematic biases, weak domain calibration and no meta-evaluation standard
(2606.13685, 2606.19544); a RAND study found no judge uniformly reliable and frontier models
above 50% error on hard bias benchmarks; practice samples 100 to 300 traces with two or three
annotators and requires judge-to-human agreement around Cohen's kappa 0.6 or better.

Relation: the skill forest's oracle tiers put judged outputs last for a reason, and treat the
judge as a skill with its own corpus and agreement rate.

## 13. Wellbeing and career guidance

A 2025 meta-review of 35 papers finds strong evidence for mental-wellbeing effects of career
guidance; positive-education work frames interventions through Self-Determination Theory and
PERMA; longitudinal PERMA measurements in secondary schools; a quasi-experimental study of
career planning education on career adaptability; a study of a mobile career-counseling app on
decision-making self-efficacy.

Relation: the life-planning instance's instruments and its falsification test (do
recommendations under the person's own weights predict the person's later evaluation better
than an income proxy) sit on this evidence base rather than on the platform's own claims.

## 14. Summary

| component | nearest neighbors | what the vision adds |
|---|---|---|
| selection | RouteLLM, FrugalGPT, SCOPE, Archon, ProgRouter | flows not single calls; owner's corpus and objective; auditable candidates |
| priors | RouterBench, Martian's review benchmark, SWE-bench | measured on the owner's data with n and intervals; composites measured end to end |
| skills | DSPy, GEPA, agent skill registries | executor-agnostic contract + scorer + corpus; derived levels |
| executors | gateways, skills marketplaces, O*NET/Lightcast | models, tools and people in one matrix |
| exploration | bandit routers | an explicit exploration budget over profile cells |
| provenance | Braintrust, Langfuse, OTel GenAI | bit-exact replay from prompt-keyed fixtures |
| objective | delegation frameworks | cost per miss, false-positive cost, fixed human nodes |
| ground truth | Defects4J, SWE-bench Verified, SZZ, Auto-Diagnose | oracle tiers per scorer; corpus source tiers and date cutoffs |

Read first, in this order, to place the work: the routing survey (2603.04445), SCOPE
(2606.00774), Archon (2409.15254), Martian's review benchmark, SWE-bench Verified, and Google's
Auto-Diagnose (2604.12108).

## Sources

Routing and cascades: [survey 2603.04445](https://arxiv.org/pdf/2603.04445),
[UCCI 2605.18796](https://arxiv.org/html/2605.18796), [RouteNLP 2604.23577](https://arxiv.org/pdf/2604.23577),
[TwinRouterBench 2605.18859](https://arxiv.org/html/2605.18859), [Cluster, Route, Escalate 2606.27457](https://arxiv.org/pdf/2606.27457),
[MixLLM](https://www.researchgate.net/publication/390484427_MixLLM_Dynamic_Routing_in_Mixed_Large_Language_Models),
[FrugalGPT overview](https://www.emergentmind.com/topics/frugalgpt), [NeuralTrust on routing](https://neuraltrust.ai/blog/llm-model-routing),
[TrueFoundry on routing](https://www.truefoundry.com/blog/llm-routing-cost-quality-aware-model-selection),
[MintMCP on agent cost](https://www.mintmcp.com/blog/llm-cost-optimization-agent-teams).

Compound systems: [Archon 2409.15254](https://arxiv.org/abs/2409.15254), [SCOPE 2606.00774](https://arxiv.org/pdf/2606.00774),
[ProgRouter 2608.25992](https://arxiv.org/abs/2608.25992), [difficulty-aware orchestration 2509.11079](https://arxiv.org/pdf/2509.11079),
[confidence-aware routing 2601.04861](https://arxiv.org/pdf/2601.04861), [cross-attention routing 2509.09782](https://arxiv.org/pdf/2509.09782),
[multi-agent routing as set-valued prediction 2606.28925](https://arxiv.org/pdf/2606.28925),
[scalable inference architectures 2604.25724](https://arxiv.org/html/2604.25724).

Program optimizers: [DSPy optimizers explained](https://futureagi.com/blog/dspy-optimizers-explained/),
[GEPA 2507.19457](https://arxiv.org/pdf/2507.19457), [GEPA repository](https://github.com/gepa-ai/gepa),
[DSPy GEPA docs](https://dspy.ai/api/optimizers/GEPA/overview/), [Trace 2406.16218](https://arxiv.org/pdf/2406.16218),
[Decagon on GEPA in production](https://decagon.ai/blog/optimizing-gepa-for-production).

Bandits: [cost-aware multi-objective bandits 2608.04333](https://arxiv.org/html/2608.04333),
[online multi-LLM selection via contextual bandits (AAAI)](https://ojs.aaai.org/index.php/AAAI/article/download/39672/43633),
[bandits meet LLMs survey 2505.13355](https://arxiv.org/pdf/2505.13355), [near-optimal online routing 2506.17254](https://arxiv.org/pdf/2506.17254),
[CUPID 2606.00846](https://arxiv.org/pdf/2606.00846), [latency-quality tool routing 2605.14241](https://arxiv.org/pdf/2605.14241).

Evaluation and observability: [Braintrust on LangSmith alternatives](https://www.braintrust.dev/articles/langsmith-alternatives-2026),
[13 evaluation tools compared](https://majesticlabs.dev/blog/202608/13-llm-evaluation-tools-compared-aug-2026),
[Inference.net comparison](https://inference.net/content/llm-evaluation-tools-comparison/),
[Braintrust vs Inspect vs Langfuse](https://www.callmissed.com/en/blog/agent-evaluation-frameworks-compared-braintrust-vs-inspect-vs-langfuse-vs-diy-20),
[MarkTechPost platform comparison](https://www.marktechpost.com/2026/08/09/top-llm-observability-and-evaluation-platforms-in-2026-langfuse-langsmith-braintrust-arize-and-more-compared/),
[OpenTelemetry GenAI observability](https://opentelemetry.io/blog/2026/genai-observability/),
[Uptrace on OTel for AI](https://uptrace.dev/blog/opentelemetry-ai-systems), [Greptime on OTel GenAI conventions](https://greptime.com/blogs/2026-05-09-opentelemetry-genai-semantic-conventions),
[Fiddler on OTel scope](https://www.fiddler.ai/blog/opentelemetry-ai-observability-guide).

Code review benchmarks: [CodeAnt benchmark](https://www.codeant.ai/blogs/ai-code-review-benchmark-results-from-200-000-real-pull-requests),
[CodeAnt tool ranking](https://codeant.ai/blogs/best-ai-code-review-tools), [DeepSource comparison](https://deepsource.com/resources/ai-code-review-tools),
[Entelligence benchmark](https://entelligence.ai/code-review-benchmark-2026), [DEV Community roundup](https://dev.to/heraldofsolace/the-best-ai-code-review-tools-of-2026-2mb3),
[Kunal Ganglani comparison](https://www.kunalganglani.com/blog/ai-code-review-tools-2026-compared).

Bug corpora: [Dissecting the SWE-bench leaderboards 2506.17208](https://arxiv.org/html/2506.17208v2),
[SWE-bench Verified overview](https://www.emergentmind.com/topics/swe-bench-verified-issues),
[SZZ label noise 2605.27880](https://arxiv.org/pdf/2605.27880), [defect datasets survey 2504.17977](https://arxiv.org/pdf/2504.17977).

CI triage: [Auto-Diagnose at Google 2604.12108](https://arxiv.org/html/2604.12108v1),
[LLM-driven CI failure diagnosis and repair](https://www.researchgate.net/publication/401215124_LLM-Driven_CI_Failure_Diagnosis_and_Automated_Repair_From_GitHub_Actions_Logs_to_Patch_Recommendation),
[AI-assisted flaky triage pipeline](https://www.researchgate.net/publication/396192261_AI-Assisted_Triage_of_Flaky_Test_Failures_from_System_Logs_A_Practical_Pipeline_for_CI_at_Scale),
[NeuroFlake 2605.11482](https://arxiv.org/pdf/2605.11482), [Ranger on CI/CD root cause](https://www.ranger.net/post/ai-root-cause-analysis-cicd-failures).

Skill registries: [ecosystem-scale skills 2603.02176](https://arxiv.org/pdf/2603.02176), [SkillAudit 2606.22613](https://arxiv.org/pdf/2606.22613),
[evaluating agentic skills at scale 2606.17819](https://arxiv.org/html/2606.17819), [SkillResolve-Bench 2606.10388](https://arxiv.org/pdf/2606.10388),
[Skill-RM 2606.03980](https://arxiv.org/pdf/2606.03980), [supply-chain security for skills 2603.00195](https://arxiv.org/pdf/2603.00195),
[SKILL.md attacks 2605.11418](https://arxiv.org/pdf/2605.11418), [SkillProbe 2603.21019](https://arxiv.org/pdf/2603.21019),
[Agent Exchange 2507.03904](https://arxiv.org/pdf/2507.03904), [SkillsBench](https://www.skillsbench.ai/).

Human skills: [O*NET, ESCO and the skills-based hiring stack](https://aieh.com/skills-taxonomy-frameworks/),
[Lightcast taxonomies](https://lightcast.io/our-data/taxonomies), [Lightcast Open Skills](https://learnworkecosystemlibrary.com/initiatives/lightcast-skills-taxonomy/),
[Knowlee on skills assessment platforms](https://www.knowlee.ai/blog/ai-skills-assessment-platform),
[O*NET features from the NLx corpus 2510.01470](https://arxiv.org/pdf/2510.01470).

Delegation: [Intelligent AI Delegation 2602.11865](https://arxiv.org/abs/2602.11865),
[The Cost of Convenience (CHI 2026)](https://dl.acm.org/doi/10.1145/3772363.3798760),
[optimizing delegation 2309.14718](https://arxiv.org/pdf/2309.14718), [field experiments 2503.18238](https://arxiv.org/pdf/2503.18238).

Judges: [The Coin Flip Judge 2606.13685](https://arxiv.org/pdf/2606.13685), [Reliability without Validity 2606.19544](https://arxiv.org/html/2606.19544v1),
[Label Your Data guide](https://labelyourdata.com/articles/llm-as-a-judge), [Adaline on judge bias](https://www.adaline.ai/blog/llm-as-a-judge-reliability-bias).

Wellbeing and guidance: [positive higher education strategies (Frontiers 2025)](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2025.1561267/full),
[career planning education quasi-experiment](https://pmc.ncbi.nlm.nih.gov/articles/PMC12754903/),
[CDI wellbeing research](https://www.thecdi.net/resources/research-directory/challenge-wellbeing),
[longitudinal PERMA in Singapore schools](https://internationaljournalofwellbeing.org/index.php/ijow/article/download/5319/1305/19113),
[mobile career counseling app study](https://link.springer.com/article/10.1007/s44202-025-00468-8).
Closest prior claims: [Bigger Isn't Always Better 2606.15689](https://arxiv.org/abs/2606.15689),
[More Rounds, More Noise 2603.16244](https://arxiv.org/abs/2603.16244),
[Qodo thinking-vs-thinking on 400 PRs](https://www.qodo.ai/blog/thinking-vs-thinking-benchmarking-claude-haiku-4-5-and-sonnet-4-5-on-400-real-prs/),
[Greptile benchmark method](https://www.greptile.com/benchmarks),
[Qodo benchmark method](https://www.qodo.ai/blog/how-we-built-a-real-world-benchmark-for-ai-code-review/),
[multi-stage filtering pipelines, independence](https://link.springer.com/chapter/10.1007/978-3-032-32578-5_5),
[Cross-Model LLM Code Review 2607.21656](https://arxiv.org/html/2607.21656v1).
