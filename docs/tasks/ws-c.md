# Workstream C · Data and evaluation — task list

Owner: Andrea · Reviewer: Mattia · How to use this file: `docs/tasks/README.md`

Specification: `docs/evaluation_protocol.md` (every definition, count and
threshold) and `docs/interfaces.md` (contracts and file formats, section 5).
Read both before the first task. The evaluation calls `pipeline.mask`,
`pipeline.protect_send_restore` and `backends.complete`, nothing below them.

## Step 1 · Skeleton · M1 · Fri 13 Nov

- [ ] **C1 · Fixtures, profile schema, annotation guide v0** — `data/fixtures/`, `data/profiles/`, `docs/annotation_guide.md`
  - Blocked by: B0.
  - Do: loaders and validation tests for the text and profile file formats
    of `docs/interfaces.md`, section 5; 5
    synthetic Italian emails as fixtures (3 bank, 2 HR or health
    administration, one with special-category data); the guide with classes,
    types, edge cases and worked examples.
  - Done when: the loader returns `Span`s that all satisfy `span.matches(text)`;
    every fixture has at least one direct identifier.
  - **Human:** rewrite the guide's edge cases in your own words; confirm the
    emails read like real correspondence and contain nothing real.

## Step 2 · Second detector and pilot · M2 · Sun 15 Nov

- [ ] **C2 · Profile generator** — `data/profiles/`, `eval/profiles.py`
  - Blocked by: C1.
  - Do: profiles and candidate lists exactly as in
    `docs/evaluation_protocol.md`, section 1.
  - Done when: tests assert the sharing rule, list sizes, presence of the true
    author and determinism for the seed.

- [ ] **C3 · Text generator with inline tags** — `eval/textgen.py`, `data/pool/`
  - Blocked by: C2, B11; model `generator` pinned (not the D3 or attacker model).
  - Do: prompt that writes an Italian email from one profile and one scenario
    with spans marked `[[TYPE|text]]`; a parser that strips the tags and
    computes offsets; the scenarios, counts and text requirements of
    `docs/evaluation_protocol.md`, section 2.
  - Done when: parser tests cover nested-looking brackets, unknown types and
    adjacent tags; 10 pilot texts are in `data/pool/`.
  - **Human:** review the 10 pilot texts.

- [ ] **C4 · The two attacks** — `eval/attacks.py`
  - Blocked by: C2, B11, B5; model `attacker` pinned.
  - Do: both attacks exactly as in `docs/evaluation_protocol.md`, section 7,
    through `backends.complete`.
  - Done when: scoring is tested with a fake provider; the call count and
    estimated cost are printed before any real batch.
  - **Human:** read and approve both prompts.

- [ ] **C5 · Pilot report**
  - Blocked by: C3, C4.
  - Do: both attacks on the 10 pilot texts for REF-none, D1+R1 and REF-oracle;
    a one-page note in `results/` with the numbers.
  - **Human:** go or no-go with the team: the attacks must be neither at
    ceiling nor at floor. Record the decision in `docs/decisions.md`.

- [ ] **C9 · Statistics** — `eval/stats.py`
  - Blocked by: B0.
  - Do: the procedures of `docs/evaluation_protocol.md`, section 12.
  - Done when: tests compare against hand-computed or textbook values.

## Step 3 · Full system · M3 · Thu 19 Nov

- [ ] **C6 · Full dataset and split** — `data/pool/`, `make split`
  - Blocked by: C5 go.
  - Do: the 66 texts of `docs/evaluation_protocol.md` section 2 in
    `data/pool/`; the agreement script of section 3; `make split` as in
    section 4, refusing texts without `reviewed_by`.
  - **Human:** each member reviews 22 texts; 13 are annotated twice; Andrea
    runs `make split`. After that no agent opens `data/test/`.

- [ ] **C7 · Utility tasks** — `eval/utility.py`
  - Blocked by: B4, C1.
  - Do: T3 and T1 exactly as in `docs/evaluation_protocol.md`, section 8.
  - Done when: scoring tests cover equal values in different formats and
    missing fields.
  - **Human:** read and approve the T3 and T1 prompts.

- [ ] **C8 · Judge and its validation** — `eval/judge.py`
  - Blocked by: C7; model `judge` pinned.
  - Do: the judge, the rating sheet for two humans and the acceptance
    computation exactly as in `docs/evaluation_protocol.md`, section 9.
  - **Human:** read and approve the judge prompt. Giuseppe and Mattia rate the 40 items; Andrea records whether
    the judge is accepted (kappa ≥ 0.6 or ≥ 85% within one point).

- [ ] **C10 · Report and evaluation commands** — `eval/report.py`, `make eval-dev`, `make eval-test`
  - Blocked by: C4, C7, C8, C9, A5, A7, A9.
  - Do: the full evaluation over the configurations of
    `docs/evaluation_protocol.md` section 5; metrics files, chart and
    scorecard as in sections 10 to 13; `make eval-test`
    refusing to run a second time and writing the access log.
  - Done when: `make eval-dev` produces chart and scorecard on dev.

## Step 4 · Results · M4–M5 · Sat 21 – Mon 23 Nov

- [ ] **C11 · Final results and error taxonomy**
  - Blocked by: M4 freeze.
  - **Human:** the three members launch `make eval-test` together, once.
  - Do: chart, scorecard and error taxonomy from the metrics files; every
    statement limited to what the intervals support; `docs/cards.md` with one
    entry per model and dataset (source, revision, licence, how we use it).
  - **Human:** check every headline number against `results/metrics/`.

## Step 5 · Presentation · M6 · Wed 25 Nov

- [ ] **C12 · Slides for evaluation and results**
  - Blocked by: C11.
  - Do: draft content for Andrea's part (evaluation design, the chart, what
    did not work, limits and conclusions) and the backup slides (annotation
    agreement, judge validation, per-type detection, attack design, cost),
    every number taken from `results/metrics/`.
  - **Human:** write the final slides and rehearse twice with the team.
