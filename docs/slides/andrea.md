# Slides — Andrea (draft, no numbers)

Part: evaluation design, the chart, what did not work, limits; backup slides on
annotation agreement, judge validation, attack design, cost. A draft for the
human who writes the slides. Where a number will go, the file it comes from is
named; no number is written here.

## 1. Evaluation design

- On screen: three boxes. Data (synthetic profiles and emails) → configurations
  (three references, four with detectors) → measures (privacy, utility,
  restoration).
- Say: every person is invented. The profiles come in cohorts that share job,
  town or employer, so that the attacker has look-alike candidates to confuse.
- Say: the split is fixed once, and the test texts were never opened while the
  system was built; the whole protocol was frozen before the held-out run.
- Say: the three references bound the space: nothing masked, direct identifiers
  masked from the gold annotation, everything masked from the gold annotation.

## 2. How we measure privacy and utility

- On screen: two halves.
  - Privacy: an attacker LLM sees the masked text and a list of candidate
    profiles and ranks who wrote it (linkage, top-1 and top-3); a second attack
    guesses attributes from the text alone, from closed lists.
  - Utility: the cloud model answers through the whole pipeline; we score a
    structured extraction against gold (T3) and a draft reply judged against the
    unmasked reply (T1).
- Say: privacy score = 1 − linkage top-1 with 25 candidates; chance is marked on
  the chart.
- Say: three contrasts were declared before any result, with a Holm correction.

## 3. The chart

- On screen: `results/test/figures/privacy_utility.png`: x privacy, y utility,
  one point per configuration with 95% intervals, chance line.
- Numbers here: the points from `results/test/metrics/linkage.json` (top-1,
  N = 25) and `results/test/metrics/utility.json`; contrasts from
  `results/test/metrics/contrasts.json`.
- Say: read the chart from `REF-none` (top left: useful, exposed) towards
  `REF-oracle` (right: masked from gold). Where do the detector configurations
  sit between the two?
- Say: if the judge was rejected, the y axis is T3 for every configuration, and
  that is a finding too.

## 4. What did not work

- On screen: three or four error examples from `results/dev/error_examples.md`
  and the taxonomy in `results/dev/error_taxonomy.md`.
- Numbers here: D3 failures and leak rate from `results/dev/metrics/detection.json`;
  counts of `wrong_mapping` and of R2 fakes left in the text, given by the human
  inspection (protocol, section 10).
- Say: derived values (a postcode computed for a fake town, a sum of masked
  amounts) cannot be restored; the model sometimes swaps whose data is whose.
- Say: R2's full-restoration rate is an upper bound, because a fake the model
  rewrites is not recognised.

## 5. Limits

- On screen: a list, one line each.
  - Synthetic data, written by one model: more regular than real mail.
  - One reviewer of the gold and one rater of the judge.
  - The judge is the same model as the cloud model.
  - Texts by the same author are not independent: intervals are optimistic.
  - One attacker model; no external data, no linking across texts.
  - Pseudonymisation, not anonymisation: we measure re-identification risk.

## Backup A. Annotation agreement

- Numbers here: span F1 (exact and overlap) and Cohen's kappa on class, from
  `results/dev/metrics/agreement.json`.
- Say: it is agreement between one human and the generator's tags, before review,
  not between two humans.

## Backup B. Judge validation

- Numbers here: quadratic-weighted kappa and share within one point, per
  criterion and overall, from `results/dev/metrics/judge_validation.json`.
- Say: the rule (kappa or within-one-point) was fixed before the sheets were
  compared; the items come from gold-span masking, under R1 and R2.

## Backup C. Attack design

- On screen: one linkage prompt with its candidate list (synthetic), and the
  closed lists of the attribute attack.
- Numbers here: per-attribute accuracy against `REF-none` and the majority
  baseline, from `results/test/metrics/attributes.json`.
- Say: the attacker must always choose; `health` is readable from the topic
  in the health scenarios under every configuration; R2 is not measured as a
  decoy, because its fakes match no candidate.

## Backup D. Cost

- Numbers here: latency p50 and p95 per detector from
  `results/dev/metrics/latency.json`; LLM calls and estimated tokens per
  configuration from `results/<split>/metrics/cost.json`.
- Say: everything ran on a free tier; the daily allowance, not money, set the
  pace.
