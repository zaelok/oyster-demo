# Instance: long-term life planning, high school to early career

The skill-forest model ([`../SKILL-FOREST.md`](../SKILL-FOREST.md)) applied to a person
planning a path from secondary school into their first years of work. Not implemented. This
instance is the hardest test of the model because three things that are convenient in
engineering are absent here: the executor and the owner of the objective are the same person,
the counterfactual path is never observed, and feedback arrives in years.

## 0. The rule that comes first

The platform does not decide what a good life is. It makes the person's weights explicit,
shows what each weighting selects, with the evidence and its width, and records why. It never
outputs "you will become X"; it outputs "under your objective, this path has better evidence,
and here is how wide the interval is and where the estimate came from". That is the same
sentence OYSTER says about review paths; here it is the ethical floor, not a feature.

Corollaries: weights are elicited from the person and versioned, never inferred and imposed;
priors from other people are labeled as population data; basic needs are constraints, not
tradeable weights; for minors, the fixed human nodes include a guardian or counselor.

## 1. The mapping

| noun | instance |
|---|---|
| task | a decision point: course selection, subject choice, application list, gap year, internship, first job, first job change |
| expected | outcomes measured later: milestones (completion, admission, offer, retention) and the person's own wellbeing, measured with validated instruments (§3) |
| output | a ranked set of paths with evidence, cost, interval and provenance, never a single verdict |
| scorer | two layers: predictive validity over cohorts (did paths recommended to people like this lead to the outcomes they weighted), and the individual's measured outcomes after the fact |
| skills | competencies with levels derived from composition (§2) |
| executors | the person, plus their resources: school, mentors, tools, programs |
| composites | path patterns: explore then commit, cheap self-assessment then expensive assessment, mentor critique loop, parallel options with a decision date |
| cost | time, money, energy, opportunity cost; latency is a hard deadline (application seasons) |
| priors | cohort matrix with backoff, overridden progressively by the person's own measurements |
| objective | weights over wellbeing dimensions plus constraints (§3) |
| provenance | why this path ranked where it did: which cohort cells, which of the person's own results, which weights, at what date |

## 2. Skills and levels

Level is derived from composition, as everywhere in the forest:

- level 1, atomic competencies with a direct assessment: solve a class of algebra problems,
  write a working function, write a paragraph that argues a claim, hold a conversation in a
  second language;
- level 2, composed: complete a small project end to end, run an experiment and report it,
  learn a tool from its documentation;
- level 3, role-shaped: deliver a feature inside a team, teach a unit, run a small event,
  hold a part-time job for a term.

Each leaf declares a scorer and its oracle tier: standardized tests are close to deterministic;
project work is judged against a rubric by a reviewer who is themselves calibrated (agreement
with other reviewers is measured); milestones such as admission and offers are the slowest
and most real labels. A competency without any assessment is not a leaf yet.

Flows are path patterns instantiated over skills: a cascade is "self-assess cheaply, then pay
for an evaluation only where the self-assessment is uncertain"; a critique loop is "mentor
review, revise, review again, bounded"; exploration is "take the elective, do the two-week
internship" as a deliberately bounded cost that fills an empty cell of the person's own matrix.

## 3. The objective: wellbeing models as the dimension schema

The weights in the objective are over dimensions of a life, not over bug categories. Rather
than invent dimensions, use published wellbeing models as the schema and their validated
instruments as the measurement, chosen and named explicitly so the person knows which lens is
in use:

| model | dimensions | how it is used here |
|---|---|---|
| PERMA (Seligman) | positive emotion, engagement, relationships, meaning, accomplishment | default schema for the weight vector; measured with the PERMA-Profiler questionnaire |
| Self-Determination Theory (Deci and Ryan) | autonomy, competence, relatedness | basic psychological needs; used as constraints with floors, not as tradeable weights |
| Ryff's psychological well-being | autonomy, environmental mastery, personal growth, positive relations, purpose in life, self-acceptance | alternative schema; useful for the growth and purpose dimensions PERMA folds together |
| Cantril ladder, SWLS | overall life evaluation | a single-number check that the weighted dimensions add up to something the person recognizes |
| Gallup and OECD wellbeing frameworks | career, social, financial, physical, community; income, housing, health, education, work-life balance, safety | adds the material dimensions the psychological models leave implicit |

The schema is a choice the person makes and can change; the platform records which schema
and which version of the weights every recommendation used.

**Elicitation and correction.** Stated weights are unreliable on their own, so the weight
vector is built and corrected in three ways:

1. *Stated*: the person rates each dimension's importance on the chosen schema.
2. *Revealed*: the person chooses between concrete paths that trade dimensions against each
   other (more income and less autonomy, closer to family and slower growth). The implied
   weights are computed and shown next to the stated ones. Where they disagree, the platform
   shows the disagreement; the person decides which to keep.
3. *Calibrated over time*: after decisions, the same instruments measure the outcome. If the
   weight vector keeps predicting satisfaction poorly, that is shown, and the person is invited
   to revise. Weights are never changed without the person's consent.

**Constraints, not weights.** Health, safety, financial runway, and the SDT basic needs have
floors. A path that trades below a floor is infeasible, and the engine says so with the reason
and the closest feasible alternative, exactly as `select()` reports `no_feasible_reason` and
`cheapest_infeasible`. The selector never optimizes one dimension without showing the others.

## 4. Priors: cohorts, backoff, and the person's own data

The counterfactual is never observed: one person walks one path. So population priors come
from cohorts, and the sparse matrix has person facets as rows (starting competencies, interests,
available time, financial constraints, region, school type, target field) and paths as columns.
Cells hold outcome distributions with N, intervals and the source, and back off along the facet
hierarchy when empty, saying which level the estimate came from.

Sources for cohort priors are longitudinal studies and graduate outcome surveys where access
and licensing allow (in the United States, for instance, NLSY97, HSLS:09 and Add Health; the
OECD's PISA and PIAAC internationally), plus the platform's own consented, anonymized outcomes
once it has them. Every cell shows that it is population data until the person's own
measurements override it.

Two biases the model must state: survivorship (people who left a path are underrepresented in
its outcomes) and selection (people who chose a path differ from those who did not, so the
cohort outcome is not the causal effect of the path). The platform presents cells as evidence
about people like you, not as predictions about you.

## 5. Feedback loop

- Cadence: instruments at each term or year, milestones as they happen. Consolidation is
  offline and periodic, as in the architecture document, never a live update that changes a
  recommendation under the person's feet.
- Lag: years for the slowest labels. Profiles carry their measurement date, and the person
  sees how old the evidence is.
- Drift: interests and weights change; re-elicitation is scheduled, and old recommendations
  keep the weights they were made with so they can be understood later.
- Consent and minimization: outcomes join the cohort matrix only with consent and only in
  aggregate; a person can withdraw their data, and the cells that depended on it are recomputed.

## 6. Policy: fixed human nodes

- The person decides. The platform recommends, ranks, explains and records.
- For minors, a guardian or counselor is a fixed binding on irreversible decisions
  (applications, withdrawals, financial commitments).
- No dimension is optimized in isolation; no recommendation is shown without its interval and
  its provenance; no cohort cell is shown without its N.

## 7. What the engine needs

The same scenario plugin as every instance: tasks (decision points), a scorer (predictive
validity plus the person's measured outcomes), rendering of a decision point into a skill's
input, and parsing of the output. Three engine changes this instance forces that the others
merely benefit from: a multi-dimensional objective with floors, a person-owned executor whose
prior is a matrix of their own measurements, and provenance that includes the weight-vector
version. All three are data and constraint handling; the selection loop is unchanged.

## 8. What would falsify the instance

The claim is that recommendations made under a person's explicit weights, from labeled cohort
evidence, lead to outcomes the person themselves rates higher than the alternative. That is
testable: measured wellbeing and milestones after recommended versus non-recommended choices,
across people, over years. If the weighted objective does not predict the person's own later
evaluation better than a simple income proxy does, the schema is wrong, and the instrument
data will say so.
