# Personal instructions — Andrea's agent

You work for **Andrea**, owner of **block 3 · Data and evaluation**. Read the
shared `CLAUDE.md` first; it prevails. At the gates Andrea reviews block 1
(with Giuseppe), block 2 and, with Mattia, block 5; Mattia reviews block 3.

Write code, comments, commit messages and docs in English.
This block decides whether the project's numbers can be trusted: when a
shortcut would weaken the evaluation, say so before taking it.

**When told to start or continue, work from `docs/tasks/block-3.md`** as described
in `docs/tasks/README.md`. Before gate G2 is ticked and after gate G3 is ticked
it is not your turn: change nothing, except a `fix/…` branch for a defect in
block 3's code that Andrea explicitly asks for. Three tasks may start as soon
as G1 is ticked, while block 2 is running, when Andrea names one: 3.8, the
code and tests of 3.9 (after task 4.0), and the guide half of 3.1
(`docs/tasks/README.md`). After gate G5, task P.2 is yours.

## Your paths

`data/` except `fixtures/` (and never `data/test/` after the split);
`src/omissis/eval/` (`datasets.py`, written in block 1, is yours from gate G1);
`docs/annotation_guide.md`; `tests/eval/`, `tests/data/`; the `split` and
`eval-*` targets of the `Makefile`; the files your tasks write in `results/`;
`docs/handoff/block-3.md`. After G5: `docs/slides/andrea.md`. You read
`configs/eval.yaml` and never edit it.

## What the block delivers

| Block | You produce | Andrea verifies or decides |
|---|---|---|
| 3 · Data and evaluation · Thu 19 – Sun 22 Nov | Revised annotation guide; 30 profiles in 6 look-alike cohorts and the candidate lists; text generator and 66 texts; the two attacks and the pilot; utility tasks; judge and its validation sheets; statistics; detection metrics and latency; evaluation runner, chart and scorecard for the three reference configurations; hand-over note | Rewrites the guide's edge cases; approves every prompt; calls the pilot go/no-go with the team; coordinates the review of the texts and the double annotation; runs `make split`; records the judge's outcome; tags `block-3` |

The privacy and utility evaluation of this block runs **without any detector**:
the three reference configurations come from gold spans and are already listed
in `configs/eval.yaml` (block 2). The detection metrics run on dev for D0
only; D1 to D4 are measured in task 4.5 on the reference machine, through the
same code. Block 4 then appends the four
configurations with detectors; the runner and the report must accept them
without code changes.

## Reviewing blocks 1, 2 and 5

When Andrea asks you to help review: at G1, `eval/datasets.py`, the fixtures and
the guide of block 1; at G2, `docs/handoff/block-2.md` and the code of block 2
against `docs/interfaces.md`; at G5, every headline number of the README and of
`results/<split>/scorecard.md` against `results/<split>/metrics/`, and `make reproduce`. Run
the tests and give concrete findings with file and line. You advise; Andrea
reviews.

## Component notes and known traps

- **Profiles:** name, gender, age, city, employer, role, bank, branch city,
  financial facts, optional special-category fact. Cohort members share at least
  two quasi-identifiers, so no single clue identifies the author. All values
  invented; names and cities come from lists disjoint from the R2 fake lists.
- **Text generation:** the generator model writes an Italian email from one
  profile and one scenario, marking sensitive spans inline as `[[TYPE|text]]`. A
  script strips the tags and computes character offsets. About 60% bank
  correspondence, 40% HR and health administration; about 30% with
  special-category data; every text has at least one direct identifier.
  **The generator must not be the D3 model or the attacker model**, otherwise
  detection and attack results are inflated. In the hand-over
  note, propose the `docs/cards.md` lines for the generator, the attacker and
  the judge: block 5 writes that file.
- **Annotation policy:** tag *all* direct identifiers, quasi-identifiers and
  special-category spans by type. Do not decide in the annotation whether a
  quasi-identifier "should" be masked; that is a configuration switch.
- **Split:** before the split all texts live in `data/pool/`. A human runs
  `make split`, which writes `data/dev/` and `data/test/`, records checksums and
  empties the pool. From that moment you never open `data/test/`. Results on test
  are described as "evaluated once", never as "unseen data".
- **Linkage attack:** input = masked text + candidate list of N profiles
  (N = 10 and 25; true author + cohort look-alikes + random others, fixed by
  seed); output = ranked guess; metrics = top-1 and top-3. Headline privacy
  score = 1 − top-1 at N = 25. Always shown against `REF-none` and chance (1/N).
- **Attribute inference:** masked text only; guesses for city, profession,
  employer, age bracket, gender, presence of a health condition, each from a
  closed answer list, with no "unknown" option;
  accuracy against `REF-none` and the majority baseline. Gender is included
  because the placeholders deliberately reveal it.
- **The attacker prompt never contains gold labels or the configuration name.**
- **Utility:** T3 extraction (intent, amounts, dates, requested action, deadline)
  scored exactly per field after restoration; T1 reply draft scored by the judge
  (1–5 on correctness, completeness, Italian grammar) against the `REF-none`
  reply, blind to the configuration.
- **Judge validation (pre-declared):** two humans (Giuseppe and Mattia) rate 40 dev
  items blind: the 20 dev texts masked from gold spans with R1 and with R2. The
  judge is accepted if weighted κ ≥ 0.6 **or** agreement within ±1 point ≥ 85%;
  report both plus the score distribution. If rejected, humans score T1 on test
  only for contrast (2), as the fallback of the protocol says in section 9, and
  the failure is reported as a finding.
- **Statistics:** all comparisons paired on the same texts; 95% intervals by
  paired bootstrap (10,000 resamples, fixed seed); McNemar for paired binary
  outcomes; Holm correction across the three primary contrasts. With 46 test
  texts intervals are wide: state conclusions only where the decision rule of
  the protocol, section 12, supports them, and report negative results with
  the same prominence.
- **Cost guard:** before any batch of LLM calls, print the number of calls and
  the estimated cost and wait for Andrea's go-ahead. Team budget: about €10.



## Shared duties of your human (support them, do not do them in their place)

- **Text review (during block 3):** 22 of the 66 synthetic texts, on a branch
  `b3/review-<initials>`. The human checks realism, corrects the inline tags
  and confirms the gold fields. You may prepare a checklist or highlight
  suspicious tags; you may not mark a text as reviewed.
- **Double annotation (during block 3):** part of the 13 texts annotated
  independently by two humans. Never show your human the other annotator's
  labels before they finish.
- **Final evaluation (block 5):** the three members launch `make eval-test`
  together, once.
- **Slides and rehearsal:** task P.2 of `docs/tasks/block-5.md`. You draft
  content in your member's file under `docs/slides/`; every number must come
  from a file in `results/<split>/metrics/`.

## How to hand work back

End every task with: files changed; commands run and their real output; open
doubts; the three reviewer questions; a proposed commit message; a proposed line
for `docs/ai_use.md`. Then wait. Do not stage, commit or push (shared rule 1).
