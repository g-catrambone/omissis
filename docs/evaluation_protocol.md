# Evaluation protocol

Exact definitions for the data and for every number the project reports.
`src/omissis/eval/` implements this document. Values here are decisions:
changing one needs an entry in `docs/decisions.md`. File formats are in
`docs/interfaces.md`, section 5.

Sections: 1 profiles · 2 texts · 3 annotation and review · 4 split ·
5 configurations · 6 detection · 7 attacks · 8 utility · 9 judge ·
10 restoration · 11 cost · 12 statistics · 13 reporting · 14 LLM budget.

## 1. Profiles

- 30 synthetic people, ids `p01`–`p30`, in 6 cohorts of 5 (`c1`–`c6`), fixed seed.
- Fields: see `docs/interfaces.md`. All values invented. Names, cities and
  employers come from lists kept in `data/profiles/` and disjoint from the R2
  fake lists.
- Cohort rule: all 5 members share at least two of {`role`, `city`,
  `employer`, `bank`}; which two varies by cohort. Within a cohort no two
  members share all four.
- Value pools, so that attribute inference has a closed answer space:
  6 cities, 8 roles, 6 employers, 4 banks, age from 24 to 67.
- 10 of the 30 profiles have a `special` fact (8 `SALUTE`, 2 `SINDACATO`).
- Candidate lists per text for N = 10 and N = 25: the true author, the other
  4 cohort members, the rest drawn at random without replacement, shuffled;
  fixed by seed.

## 2. Texts

66 Italian texts, each written from one profile and one scenario by the
`generator` model, then reviewed by a human (section 3).

| Domain | Scenario (`scenario` = `intent`) | Texts | Allowed `requested_action` |
|---|---|---|---|
| bank | `mortgage_suspension` | 6 | `suspend_payment`, `reschedule_payment` |
| bank | `card_dispute` | 6 | `refund`, `open_investigation` |
| bank | `iban_change` | 6 | `update_details`, `send_information` |
| bank | `loan_early_repayment` | 6 | `send_information`, `close_account` |
| bank | `account_closure` | 6 | `close_account`, `release_funds` |
| bank | `fee_complaint` | 5 | `refund`, `schedule_meeting` |
| bank | `inheritance_unblock` | 5 | `release_funds`, `send_information` |
| hr | `sick_leave` | 5 | `register_absence`, `approve_request` |
| hr | `remote_work_request` | 5 | `approve_request`, `schedule_meeting` |
| hr | `harassment_complaint` | 4 | `open_investigation`, `schedule_meeting` |
| hr | `medical_reimbursement` | 4 | `refund`, `send_information` |
| hr | `transfer_request` | 4 | `approve_request`, `schedule_meeting` |
| hr | `union_leave` | 4 | `approve_request`, `register_absence` |

Totals: 40 bank, 26 hr. `has_special` is true in exactly 20 texts: all
`sick_leave`, `medical_reimbursement` and `union_leave` texts (13) plus 7
chosen by seed among `mortgage_suspension` and `remote_work_request`; the
author of a `has_special` text is a profile with a matching `special` fact
(`SINDACATO` for `union_leave`, `SALUTE` for the others). `has_special` is
true exactly when the text carries at least one gold special-category span.

Requirements for every text:

- 120 to 250 words (whitespace-separated tokens of `text`), first person,
  addressed to the bank or to the HR office.
- At least one direct identifier and at least four quasi-identifier spans.
- At least one amount or one date, so the extraction task is not empty.
- Exactly one requested action: one of the two allowed for the scenario, not
  both.
- Clues to the author must be spread over several quasi-identifiers; no
  sentence states a unique fact that identifies the author on its own.
- Nothing copied from real correspondence or public datasets.

The generator marks sensitive spans inline as `[[TYPE|text]]`; a parser strips
the tags and computes offsets. It also returns the gold fields
(`requested_action` as planned, `amounts`, `dates`, `deadline`), which the
reviewer confirms. The `generator` model is neither the `d3`
model nor the `attacker` model.

Pilot: 10 texts from 2 cohorts, generated first, used for the go/no-go on the
attacks and kept in the final set if they pass review; having steered a design
decision, they go to dev in the split (section 4). The pilot compares
`REF-none`, `REF-oracle-direct` and `REF-oracle` (section 5): it needs no
detector, and it shows whether masking quasi-identifiers changes what the
attacker can do.

Pilot rule, on linkage top-1 at N = 10 over the 10 texts: **go** when the
attacker identifies the author of at least 6 texts under `REF-oracle-direct`
(direct identifiers masked, quasi-identifiers visible) and of at least 3 fewer
under `REF-oracle`. `REF-none` is reported, not a condition: with the name in
clear it only shows that the attacker can read the candidate list. On
**no-go** the humans change profiles or scenarios (more distinctive
quasi-identifiers when the first number is low, clues kept inside the
annotated spans when the second does not drop) and the pilot is repeated on
new texts before the dataset is written, the texts of the failed pilot being
discarded; after two failed pilots the attacks are kept as designed and their
result is reported as it is.

## 3. Annotation and human review

- **Fixtures.** The 5 fixture emails are annotated by this same
  policy, before the annotation guide exists; the guide must not contradict
  them. The text requirements of section 2 do not bind them.
- **Policy.** Tag every direct identifier, quasi-identifier and
  special-category span with its type. Do not decide whether a
  quasi-identifier "should" be masked: that is `mask_quasi`. A span is the
  shortest stretch that carries the information (the name without the title,
  the amount with its currency, the date without the weekday).
- **Review.** Since 21 Nov every text is reviewed by Giuseppe's AI agent (a
  subagent on Claude Opus 5.5 that reads the tagged text), and Giuseppe approves
  the review on the agent's written report (`docs/decisions.md`); before, one
  member was to review all 66. Checklist: reads like real
  correspondence; nothing real; every span tagged with the right type and
  boundaries; gold fields correct; text requirements of section 2 met.
  `reviewed_by` carries Giuseppe's initials: they record his approval of the
  report, not a reading of each text by him. A text without
  `reviewed_by` cannot enter the split.
- **How the review is done.** The reviewer edits the files in `data/pool/`;
  `data/pool/REVIEWERS.md` lists the texts. The review is done on tagged text,
  not on the JSON: `python -m omissis.eval.textgen export` writes a pool text
  with its spans as `[[TYPE|text]]` tags and `import` reads the corrected
  copy, recomputing the offsets.
- **Blind annotation.** 13 texts, chosen by seed among those that are not
  pilot texts and stratified by domain, are first annotated from the raw text
  with no tags visible: `python -m omissis.eval.review export` writes
  `data/annotation/<text_id>.txt` (plain text) and the annotator saves
  `data/annotation/<text_id>.<initials>.txt` with `[[TYPE|text]]` tags added.
  Since 21 Nov the annotator is a subagent of Giuseppe's AI agent (Claude Opus
  5.5) that sees the raw text and the annotation guide only and shares no
  context with the reviewer; its files carry the label `AI` in place of the
  initials, and Giuseppe approves them on the agent's report.
  This is done, and `python -m omissis.eval.review agreement` is run, before
  any of the 13 is reviewed: the command refuses a text that has
  `reviewed_by`. Report span-level F1 between the annotator and the tags of
  the generator (exact and overlap matching, section 6) and Cohen's kappa on
  class over spans paired by character overlap whatever their class (the
  overlap match of section 6 requires the same class and would make kappa 1 by
  construction). Agreement is computed on the pool, before the split.
- **Limit to declare.** No human annotated or reviewed the texts one by one. The
  agreement is between two models, an AI annotator and the generator: it does
  not measure how far a person would agree with either. The gold is reviewed by
  an LLM, and D3 and D4 are LLM detectors too (another model): the detection
  numbers may favour them. Nothing measures how far a person would annotate the
  same way.
- **Adjudication.** The review settles the disagreements: the reviewed tags
  are the gold. A disagreement that shows an unclear rule gets one line in
  `docs/annotation_guide.md`.

## 4. Split

- 20 dev, 46 test, fixed seed: the pilot texts go to dev, and the others are
  split, stratified by `domain` × `has_special`, so that dev reaches 20.
- A human runs `make split`: it writes `data/dev/`, `data/test/`,
  `data/split.json` with checksums, and empties `data/pool/`.
- Dev is for every design choice: prompts, thresholds, debugging, judge
  validation, slide examples. Test is evaluated once, after the freeze, by
  `make eval-test`, which refuses a second run. Test results are described as
  "evaluated once", never as "unseen data".
- A run of `make eval-test` counts once it has written
  `results/test/metrics/contrasts.json`, the last file it writes. A launch
  that stops before that (a network error, a spending cap) is repeated and
  resumes from the cache: the calls already made are not made again. With
  the judge rejected, the command is also launched again before the sheets
  of section 9 are filled, as section 7 says for the attacker's replies cut
  at the token limit: the run still counts once. Every
  launch adds a line to `data/test_access.log`. The command is launched on the
  reference machine, and it stops on a missing model, library or cache entry
  instead of scoring a text as if nothing had been found. A scoring defect
  found after a completed run is fixed on a `fix/…` branch; the numbers are
  recomputed by a new launch with `backend: replay`, which makes no LLM call,
  after a human has removed `results/test/metrics/`; the defect and both sets
  of numbers go in `docs/decisions.md`.

## 5. Configurations

| Name | Detector | Strategy | `mask_quasi` | Role |
|---|---|---|---|---|
| `REF-none` | — | — | — | unmasked text: utility ceiling, privacy floor |
| `REF-oracle-direct` | gold spans | R1 | false | perfect detection of direct identifiers and special categories; quasi-identifiers left visible |
| `REF-oracle` | gold spans | R1 | true | perfect detection of everything |
| `D1+R1` | D1 | R1 | true | the standard tool |
| `D2+R1` | D2 | R1 | true | a dedicated classifier |
| `D4+R1` | D4 | R1 | true | our proposal |
| `D4+R2` | D4 | R2 | true | same detection, realistic fakes |

Detection alone is also measured for D0 and D3. Chance is analytic: 1/N for
linkage top-1 and 3/N for top-3, the majority class of the evaluated split for
each attribute.

Primary contrasts, declared before seeing test data:

1. `D4+R1` vs `D1+R1` on linkage top-1 at N = 25.
2. `D4+R1` vs `REF-none` on the utility score.
3. `D4+R2` vs `D4+R1` on the full-restoration rate.

Every other comparison is descriptive.

Every configuration with a detector masks whatever its detector finds,
quasi-identifiers included, so contrast 1 compares what the two detectors
find. The effect of masking quasi-identifiers as such is read from
`REF-oracle-direct` against `REF-oracle`.

## 6. Detection metrics

- Unit: the span. **Exact** match: same `start`, `end` and `type`.
  **Overlap** match: at least one shared character and the same class. Each
  gold span matches at most one predicted span and vice versa (greedy by
  longest overlap).
- Precision, recall, F1 under both matchings, micro-averaged, per class and
  per type, for each detector D0–D4. Under overlap matching the per-type
  figures count a gold span under its own type (recall) and a predicted span
  under its own type (precision).
- **Leak rate** (primary safety metric): share of texts in which at least one
  gold direct-identifier span is not fully covered by the predicted spans,
  whatever their type. Reported for D0, D1, D2 and D4: D3 does not look for
  direct identifiers.
- Recall is the primary detection metric; precision is always reported next
  to it.

## 7. Attacks

Both use the `attacker` model through `backends.complete`, temperature 0,
fixed prompts. Prompts never contain gold labels or configuration names.
Input is the masked text from `results/<split>/masked/<config_name>/`.

**Linkage.** Input: masked text plus the candidate list rendered as numbered
profiles (all fields except `id` and `cohort`; of `special` the fact, not
its category). Output: JSON with the three
most likely candidates in order. Metrics: top-1 and top-3 accuracy, for
N = 10 and N = 25. The prompt asks for a ranking in every case; unparseable
output counts as a miss and is counted separately for each configuration.
A reply that the model cuts at the token limit is unparseable and is not
written to the cache: it is asked again at the next launch, so the count, and
with it the top-1 of a configuration, can differ between two launches by
those texts. A cut reply is always a miss, so it makes a configuration look
more private than it is. For this reason the command is launched again, at
most three more times, for as long as a reply of the attacker (linkage or
attributes) is not parsed; a new launch makes only the calls that are not in
the cache, and the results of a split are those of its last launch. On the
test the three launches come before the one that completes the run, which
asks once more the replies still cut. The rule reads the number of replies
not parsed (`python -m omissis.eval.report --split <split> --not-parsed`)
and no outcome; a complete reply that is not valid JSON is in the cache and
is never asked again, so the count may stay above zero. The pilot is not
launched again: it stays the record of the go of 21 Nov. The scorecard shows
the count that is left.
**Privacy score** of a configuration = 1 − top-1 accuracy at N = 25.
**Limit to declare, and its control.** Seven bank texts are about a loan or a
mortgage that the profile of their author does not hold (`docs/decisions.md`,
21 Nov): the plan gives a scenario to an author without reading the products
of the profile. The candidate list shows the products, so on these texts it
points away from the author under every configuration, and the privacy score
of a masked configuration is too high by what they add. The monthly
instalment of a profile is never the one a text states. The linkage rows are
computed a second time without the seven texts: a control, reported beside
the rows on all texts, with no test and no contrast.

**Attribute inference.** Input: masked text only. Output: JSON with one value
per attribute, chosen from a closed list given in the prompt: the attacker
must always choose, there is no `"unknown"` option.

| Attribute | Answer space | Correct when |
|---|---|---|
| `city` | the 6 pool cities | equals the profile's `city` |
| `role` | the 8 pool roles | equals `role` |
| `employer` | the 6 pool employers | equals `employer` |
| `age_bracket` | `<30`, `30-44`, `45-59`, `60+` | contains `age` |
| `gender` | `M`, `F` | equals `gender` |
| `health` | `none`, `present` | `present` iff the text has a gold `SALUTE` span |

An answer outside the list is wrong and is counted with the unparseable ones.
Metric: accuracy per attribute, against `REF-none` and the majority-class
baseline. Gender is included because R1 placeholders reveal it on purpose.
Two limits are declared. `health` is read from the text, and in the health
scenarios the topic reveals it under every configuration. R2 fakes come from
lists disjoint from the profile pool, so a fake city or employer matches no
candidate and no value of the closed lists: R2 is not measured as a decoy.

## 8. Utility

Each task runs through `protect_send_restore` for every configuration,
`REF-none` included. Outputs are scored after restoration.

**T3 · extraction.** The model returns JSON with `intent`,
`requested_action` (closed vocabularies of section 2, listed in the prompt),
`amounts`, `dates`, `deadline`. Normalisation before comparison: amounts to
euro floats rounded to 2 decimals; dates and deadline to ISO `YYYY-MM-DD`;
`amounts` and `dates` compared as sets. A field is correct when equal to
gold after normalisation. **T3 score** of a text = share of the 5 fields
correct. Unparseable JSON scores 0. The prompt asks for amounts and dates
copied as they are written in the email: the scorer normalises them, not the
model, and it accepts every format that the annotation guide allows in the
texts.

**T1 · reply draft.** Instruction: "Scrivi una bozza di risposta a questa
email." Scored by the judge (section 9). **T1 score** of a text = mean of the
three criteria, mapped to [0, 1] as (score − 1) / 4.

`REF-none` is the reference of the judge, so its T1 score is 1 by definition
and it is not judged. Its T3 score is measured like any other. The T1 half of
the utility gap to `REF-none` is therefore non-negative by construction:
contrast 2 is reported as the size of the gap with its interval, next to its
T3 component, and never as a loss that the test alone proves.

**Utility score** of a text = mean of its T3 and T1 scores; of a
configuration = mean over texts. Always reported with its two components.

## 9. Judge

- `judge` model through `backends.complete`, temperature 0. The judge is not
  the `cloud` model; if the team pins one model for both, that is declared as
  a limit.
- Input: the original email, the `REF-none` reply as reference, and the reply
  under evaluation after restoration. The configuration is never shown.
- Rubric, each 1–5: **correctness** (addresses the request, no invented
  facts, right person, amounts and dates), **completeness** (covers what the
  reference covers), **Italian quality** (grammar, gender agreement, no
  leftover placeholders or broken tokens). Output: JSON with three integers
  and a one-sentence justification. An unparseable reply scores 1 on each
  criterion and is counted for each configuration.
- **Validation.** Since 21 Nov a subagent of Giuseppe's AI agent (Claude Opus
  5.5) rates 40 dev items blind, and Giuseppe approves its sheet before the
  judge is compared with it; before, one member was to rate them. The items:
  the 20 dev
  texts masked from gold spans (`mask_quasi` true) with R1 and with R2
  (`REF-oracle`, and `REF-oracle` with `strategy` overridden to `R2`: this
  second configuration has no name, is not in `configs/eval.yaml` and is not
  reported: the runner never makes its replies, so `judge sheets --backend
  cloud` makes them, 20 calls to the `cloud` model, when the sheets are
  written), order shuffled, strategy hidden. No detector is needed. The
  rater sees exactly what the judge sees and fills
  `results/dev/judge_validation/sheet_AI.csv` without opening
  `key.json` or the scores of the judge. The outcome (accepted or rejected,
  with the numbers) goes in `docs/decisions.md`.
- **Limit to declare.** The judge is validated on replies produced from
  gold-span masking, not on replies from the detector configurations, and
  against the ratings of a model, not of a person (decided on 21 Nov): no
  human rated the replies.
  Consensus = the scores of the rater; with more than one sheet, the
  mean of the raters per criterion. The judge is
  accepted if quadratic-weighted kappa between judge and rounded consensus is
  at least 0.6, **or** at least 85% of judge scores are within one point of
  the rounded consensus. Report both, plus the score distribution. Both are computed over
  the 120 item-criterion scores together (per criterion is reported too); a
  consensus ending in .5 is rounded up. The judge prompt is frozen before the
  sheets are compared and is validated once. With consensus concentrated on 4
  and 5 the validation shows the absence of gross disagreement, not fine
  discrimination: declared.
- **Fallback.** If rejected, Giuseppe scores T1 on the 46 test
  replies of `D4+R1` (the agent may not read the test texts: `CLAUDE.md`,
  rule 2), blind, with the `REF-none` reply as reference, exactly
  as the judge would (46 items, consensus as above). Contrast 2
  uses these human scores for `D4+R1`. The other configurations report T3
  alone; the chart uses T3 on the y axis for every configuration; the judge's
  failure is reported as a finding. The runner reads the outcome of the
  validation from `results/dev/metrics/judge_validation.json`. In that case
  `make eval-test` writes the sheets to `results/test/judge_fallback/` and
  stops there, before `contrasts.json`; when the sheets are filled, the same
  day and before any result is reported, the command is launched again and
  completes the same run: a resumed launch, not a second run.

## 10. Restoration

Computed on the T1 replies of each configuration.

- Share of restore events in each `RestoreOutcome`.
- **Full-restoration rate**: share of replies with `fully_restored` true.
- For R2: number of restored fakes per reply.
- For R2 the full-restoration rate is an upper bound: a fake value that the
  model reformats or abbreviates is neither restored nor flagged, except an
  amount, which is read as a number next to its currency. The manual
  inspection below also counts the replies where a fake value is left in the
  text.
- `wrong_mapping` is assigned by comparing the restored reply with gold:
  a gold value appears where a different entity's value belongs. Counted on
  dev by manual inspection of up to 20 replies per strategy, reported as a
  count with examples, not as a rate. The sentence is applied as it is
  written, and each occurrence is reported with its cause: the model gave the
  value to the wrong party, or the substitute held a wrong value. The
  inspection is made by Giuseppe's AI agent (two subagents on Claude Opus 5.5
  that share no context, one per strategy; every finding carries a quotation
  that is checked in the text), and Giuseppe approves the counts on the
  agent's written report (`docs/decisions.md`, 22 Nov).
- Values the model derives from masked values (computed amounts, shifted
  dates) cannot be restored: collected as examples for the error taxonomy.

## 11. Cost

Added latency per text for each detector, p50 and p95, measured on the dev
texts on the reference machine named in `docs/decisions.md`, by a timing pass
that runs each detector once per text with an empty cache, so that no LLM call
is answered from the cache. Number of LLM
calls and estimated spend per configuration.

## 12. Statistics

- All comparisons are paired on the same texts.
- 95% confidence intervals by paired bootstrap over texts, 10,000 resamples,
  percentile method, seed from the run configuration.
- McNemar's exact test, two-sided, for paired binary outcomes (linkage top-1,
  full restoration); for the utility score the paired bootstrap on the
  difference, with two-sided p = 2 × min(share of resampled differences ≤ 0,
  share ≥ 0).
- Holm correction across the three primary contrasts; alpha 0.05. A primary
  contrast is stated as a finding only when its Holm-adjusted p is below 0.05;
  the intervals describe its size. Where a contrast cannot be computed the
  correction runs over the ones that exist: dev has no T1 since the judge was
  rejected, so its two contrasts are corrected for two (contrast 1 on dev: Holm
  p 0.031; for three it would be 0.047). The test has all three.
- A bootstrap p of 0 means below 1 in 10,000, the resolution of the resamples;
  the scorecard prints it as 0.000. The scorecard writes "(no variation)" for
  the interval of an estimate with no variation, and the README adds the number
  of texts.
- With 46 texts intervals are wide. A difference that does not pass is stated
  as "not distinguishable with this sample". Negative results get the same
  space. An interval of zero width (0 or 46 of 46) is reported as "no
  variation observed, n = 46".
- Texts by the same author are not independent (66 texts from 30 profiles),
  so tests and intervals over texts overstate precision: declared as a limit.

## 13. Reporting

- **Chart**: x = privacy score, y = utility score, one point per
  configuration of section 5 with 95% intervals on both axes, chance marked.
- **Scorecard**: one row per configuration; columns: linkage top-1 and top-3
  at N = 10 and 25, the linkage replies not parsed at each N, attribute
  accuracy, T3, T1, utility, full-restoration rate. The utility cell is empty
  where T1 is not reported: T3 alone is not the utility score of section 8.
  Below it, the control of section 7: linkage top-1 at N = 25 without
  the seven loan texts, beside the value on all texts. A second table has
  one row per detector D0 to D4: recall by class, leak rate, latency.
- **Error taxonomy**: categorised dev examples of missed identifiers, failed
  restorations, derived values and successful attacks.
- Every number on a slide comes from a file in `results/<split>/metrics/`
  produced by `make reproduce`. Wording: "pseudonymised", "re-identification risk";
  never "anonymous".

## 14. LLM budget

Test-split calls with this protocol: utility 46 × 7 × 2 = 644; judge
46 × 6 = 276; linkage 46 × 7 × 2 = 644; attributes 46 × 7 = 322; about 1,900
in total, plus dev runs. Team budget: about 10 euro. Before any real batch
the code prints the number of calls and the estimated cost and waits for a
human's confirmation.
