# Status — Tue 17 Nov 2026, end of session

Written by Mattia's agent. A snapshot for the three members: what exists, what is
open, and a schedule that fits the nine days left. It does not replace the task lists
in `docs/tasks/`: no box is ticked there, because nothing below is committed yet.

## 1. Situation

**Nothing is committed.** Two days of work sit in the working tree of the branch
`fix/plan-corrections` on Mattia's machine: about 35 changed files and 45 new ones.
It is the only copy. `make test`: 919 passed, 1 skipped. `make lint`: clean.

| Block | Code | What is missing |
|---|---|---|
| 1 · Skeleton | done, note in `docs/handoff/block-1.md` | the human checks of task 1.2; gate G1 was taken as ticked by Mattia |
| 2 · Core | done (2.1–2.8), note in `docs/handoff/block-2.md` | approvals (lists, prompts); gate G2 |
| 3 · Data and evaluation | done (3.1–3.11), note in `docs/handoff/block-3.md` | the review of the 66 texts, the split, every official number |
| 4 · Detectors | D0–D4 built (4.0–4.4) | 4.4b, 4.5, 4.6: all need the dev split |
| 5 · Closing | not started | everything |

**Data.** The 66 texts are generated in `data/pool/` and unreviewed. The check tool
flags 4 of them. `data/pool/REVIEWERS.md` assigns 22 texts to each member and names
the 13 texts of the double annotation.

**Models** (`configs/models.yaml`, GroqCloud free tier): `cloud`, `attacker`, `judge`
on `openai/gpt-oss-120b`; `generator` on `qwen/qwen3.8-27b`; `d3` on
`openai/gpt-oss-20b`; `d2` is `iiiorg/piiranha-v1-detect-personal-information`.
D3 is a hosted model, not a local one. Three API keys are used in turn.

**Changes to the design made in this session**

- D4 takes direct identifiers from D0, D1 and D2 (Presidio added), and D3 also
  returns `UTENTE` (recorded in `docs/decisions.md`, 17 Nov).
- D3 runs at low reasoning effort with a token limit: at the default the hosted
  model loops and never answers.
- R2 keeps the R1 placeholder for roles, facilities, nationalities and special
  categories.
- `detect/local_runtime.py` was never written: D3 goes through the `groq` provider.

## 2. Results so far (indicative: 10 unreviewed pilot texts)

Pilot rule met: the attacker identifies 10 of 10 authors under `REF-oracle-direct`
and 6 under `REF-oracle` (N = 10). `results/pilot/pilot.md`.

One end-to-end run with the real models, in `results/scratch/smoke-before-d1/`
(gitignored), **before** D4 was improved:

| Configuration | Authors identified, N = 25 | Utility | T3 / T1 | Fully restored |
|---|---|---|---|---|
| `REF-none` | 10 of 10 | 0.92 | 0.84 / 1.00 | 10 of 10 |
| `REF-oracle-direct` | 9 | 0.74 | 0.84 / 0.65 | 10 |
| `REF-oracle` | 5 | 0.63 | 0.80 / 0.46 | 8 |
| `D1+R1` | 10 | 0.67 | 0.84 / 0.49 | 10 |
| `D4+R1` (old D4) | 8 | 0.65 | 0.80 / 0.49 | 6 |

D4 detection on the same texts, before and after the two changes:

| | Old D4 | With Presidio | With Presidio and `UTENTE` |
|---|---|---|---|
| Person names found | 19 of 26 | 26 of 26 | 26 of 26 |
| Employee numbers found | 0 of 10 | 0 of 10 | 9 of 10 |
| Texts with an uncovered direct identifier | 9 of 10 | 8 of 10 | 1 of 10 |

**Not known yet:** the attacker and utility numbers of the improved `D4+R1`. That
run stopped on the rate limit with about 65 calls to go. To finish it:

```
uv run --env-file .env python results/scratch/smoke.py
```

What the numbers suggest, with all the caution ten texts deserve: masking costs
utility almost only on the reply draft (the judge, not yet validated, scores every
masked configuration around 0.5); even perfect masking leaves the attacker at 5 of
10; more placeholders mean more placeholders invented by the model.

## 3. The token budget

One text under one configuration is 6 calls (2 cloud, 3 attacker, 1 judge), about
6,800 visible tokens, probably 1.5 to 2 times that with the models' hidden reasoning.

| Run | Calls | Tokens (rough, with reasoning) | On the free tier, three keys |
|---|---|---|---|
| Dev, 20 texts × 7 configurations | ~820 | 1.5–2 million | about 3 days |
| Held out, 46 × 7 | ~1,900 | 3.5–4.5 million | about a week |

The free tier gives 200,000 tokens a day per key on `gpt-oss-120b`, which carries
three roles. **The held-out run does not fit before the presentation on the free
tier.** Ways out: a pay-as-you-go plan (prices not checked); the judge moved to
`qwen/qwen3.8-27b`, before any official result exists; fewer configurations, by a
decision of the team.

## 4. To do

**Now (humans)**

- [ ] Commit and push the working tree, so the work has a second copy.
- [ ] Decide how the evaluation is paid for (section 3).
- [ ] Record the pilot go or no-go in `docs/decisions.md` with its numbers.

**Dataset (humans)** — commands in `docs/handoff/block-3.md`

- [ ] Double annotation of the 13 texts, from plain text, before any review.
- [ ] Review of the 66 texts, 22 each, as tagged text; `reviewed_by` added by hand.
- [ ] Agreement script, adjudication, `make split`.

**After the split (agent, then humans)**

- [ ] `make eval-dev` on the three references.
- [ ] 4.4b: the known D0 limits checked on dev.
- [ ] 4.5: the four detector configurations added to `configs/eval.yaml`; full dev
      run and timing pass; `results/dev/error_examples.md`.
- [ ] Judge validation: two raters, 40 dev items each, blind.
- [ ] 20 restored replies read; `fuzzy_threshold` confirmed.
- [ ] 4.6: hand-over note of block 4; tag `freeze`.

**Block 5 and presentation**

- [ ] `make eval-test`, once, the three members together.
- [ ] Results, error taxonomy, `docs/cards.md`, README, licence, `make reproduce`
      from a clean clone; tag `v1.0`.
- [ ] Slides, demo recorded in the cache, two timed rehearsals.

**Documents that no longer match the code**

- [ ] `CLAUDE.md`, `docs/interfaces.md`, `docs/evaluation_protocol.md`,
      `docs/tasks/block-4.md`, `docs/agents/mattia.md`: D3 is described as a local
      model, D4 as D0 and D2 plus D3, and `local_runtime.py` is named.
- [ ] `docs/interfaces.md`: the choices of task 2.2 and the restore rules of 2.6.
- [ ] `docs/decisions.md`: the agent working across blocks; the pinned models and
      the free tier; D3 hosted; R2 keeping placeholders for four kinds of type;
      judge and cloud on one model.
- [ ] `docs/ai_use.md`: one line per task of this session.

**Approvals still open**

- [ ] Prompts: generator, the two attacks, T3, judge, D3.
- [ ] Lists: first names (`resolve.py`), fake values (`replace/data/`), profile pools
      (`data/profiles/pools.json`), the D2 label mapping.
- [ ] Human checks of task 1.2: two D0 validators by hand, bank code `00000`, the
      partita IVA and phone values of the tests.
- [ ] Whether three free accounts used in turn are allowed by Groq's terms.

**Known weak points**

- D1 finds no synthetic codice fiscale (place code `X`); in D4 the D0 rules cover it.
- The judge is the same model as `cloud`, and is not validated.
- Fake phone numbers under R2 are random digits and could be real numbers.

## 5. Schedule proposed for the nine days left

The calendar in `CLAUDE.md` assumed the split on Sun 22 and the detectors joined on
Mon 23. The code is ahead of it and the data are behind. A schedule that fits:

| When | What | Who |
|---|---|---|
| Tue 17 | Commit and push. Decide the payment of the evaluation. Start the double annotation | all |
| Wed 18 – Thu 19 | Review of the 66 texts; agreement; adjudication; `make split` by Thu evening. Workshop Thu 19 | all |
| Fri 20 | `make eval-dev` with the seven configurations; 4.4b; timing pass | agent, Mattia |
| Sat 21 | Judge validation sheets; 20 restored replies read; fuzzy threshold | Giuseppe, Mattia |
| Sun 22 | Fixes from dev; hand-over note of block 4; tag `freeze` | Mattia |
| Mon 23 | `make eval-test`, once | all |
| Tue 24 | Results, cards, README, `make reproduce`; tag `v1.0` | Giuseppe |
| Tue 24 – Wed 25 | Slides, demo recorded, two rehearsals | all |
| Thu 26 | Presentation | all |

Fri 20 and Mon 23 are one day each only with a paid plan. On the free tier the dev
run alone takes Fri 20 to Sun 22 and the held-out run cannot finish by Thu 26.
The team has to change the calendar in `CLAUDE.md`; this table is a proposal.
