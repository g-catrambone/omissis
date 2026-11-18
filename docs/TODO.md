# What is left

One list, in order. A line marked **Human** is never done by an agent. Tick a line
when its *Done when* is true; decisions go in `docs/decisions.md`. Specifications:
`docs/interfaces.md` and `docs/evaluation_protocol.md`. History of the code:
`docs/handoff/`.

## How to work on the branch `final-steps`

Everything below is written on one branch, `final-steps`. Giuseppe reviews each
step and merges the branch into `main`.

1. **Start from the branch.** `git switch final-steps && git pull`. Nobody pushes
   to `main`.
2. **Claim a step before working on it.** Write your name after *Claimed by* in
   the step, commit that line alone (`B2: claimed by <name>`) and push it. A
   claimed step is nobody else's. Sections 1 to 3 are Giuseppe's.
3. **Small commits, one step each.** Every commit message starts with the id of
   its step (`B1: …`), so that a step can be read on its own. Pull before you push.
4. **Touch only the files the step names.** If a step needs a change anywhere else
   (`src/`, a specification, the files of another step), describe the change in the
   hand-back and stop: Giuseppe decides.
5. **Before every push** `make test` and `make lint` pass on your machine. CI runs
   them again on every push to the branch.
6. **Never**, whatever the step says:
   - open `data/test/` or any copy of the test texts (`CLAUDE.md`, rule 2);
   - run `make split`, `make eval-dev`, `make eval-test`, or any command with
     `--backend cloud`: they spend the API allowance that the evaluation needs,
     and Giuseppe launches them;
   - edit `configs/models.yaml`, `results/cache/`, a prompt, the fake lists in
     `src/omissis/replace/data/`, or anything that changes what the evaluation
     measures (`CLAUDE.md`, rule 6).
7. **Hand back** as `CLAUDE.md`, section 4, says. An agent commits and pushes only
   when its human asks (rule 1).

Needed on the machine that runs the evaluation, not for the steps of section B:
`uv sync --locked --group detect` (Presidio, spaCy, `transformers`), the D2
weights, Ollama running with `gpt-oss:20b` for D3 (`brew services start ollama`),
`GROQ_API_KEY` in `.env`.

## 1. Data (Giuseppe; protocol, section 3)

- [ ] **Human — blind annotation of 13 texts, before any review.** It measures how
  far a human agrees with the tags the generator wrote.

  ```
  uv run python -m omissis.eval.review export       # 13 plain texts in data/annotation/
  # add [[TYPE|text]] tags by the annotation guide, with no other file open;
  # save each as data/annotation/<text_id>.<initials>.txt
  uv run python -m omissis.eval.review agreement    # results/dev/metrics/agreement.json
  ```

  The last command refuses a text that already has `reviewed_by`.
- [ ] **Human — review of the 66 texts** (`data/pool/REVIEWERS.md`). The gold tags
  are what every number is measured against. For each text: it reads like real
  correspondence; nothing real; every sensitive span is tagged, with the right type
  and the shortest boundaries; the deadline (`SCADENZA`) and the gold fields are
  right; the requirements of the protocol, section 2, are met.

  ```
  uv run python -m omissis.eval.textgen export data/pool results/scratch/pool-txt
  # edit results/scratch/pool-txt/<text_id>.txt
  uv run python -m omissis.eval.textgen import results/scratch/pool-txt/<text_id>.txt data/pool
  uv run python -m omissis.eval.textgen check data/pool
  ```

  Then add `"reviewed_by": "<initials>"` to the JSON by hand. A disagreement with
  the blind annotation that shows an unclear rule gets one line in
  `docs/annotation_guide.md`.
- [ ] **Human — pilot: go or no-go**, recorded in `docs/decisions.md`. The numbers
  are in `results/pilot/pilot.md` and meet the rule, but on texts that were not
  reviewed: if the review changes one of the ten pilot texts, run
  `uv run --env-file .env python -m omissis.eval.pilot` again first.
- [ ] **Human — `make split`**, once: 20 dev, 46 test. From here rule 2 of
  `CLAUDE.md` covers every copy of the test texts; delete
  `results/scratch/pool-txt/`.

## 2. Evaluation on dev (Giuseppe)

- [ ] **Human — read the prompts** before the first `make eval-dev`: attacks
  (`attacks.LINKAGE_PROMPT`, `ATTRIBUTES_PROMPT`), T3 (`utility.T3_TASK`), judge
  (`judge.PROMPT`). The pilot already used the attack prompts: a change makes its
  calls again, and after `make eval-dev` a change means running it again.
- [ ] **Human — models.** `cloud`, `attacker` and `judge` are one hosted model
  (`configs/models.yaml`): one daily allowance of the free tier, and a judge that
  is the judged model, which the protocol asks to declare. Re-pin before the first
  `make eval-dev` or not at all: a pin changes every run id.
- [ ] **`make eval-dev`**: the seven configurations, about 700 calls. It prints the
  number of calls and waits for `y`; a run stopped by the daily limit resumes from
  the cache. Then `uv run python -m omissis.eval.detection time --split dev` for
  the latency table. Commit `results/cache/` and `results/dev/`.
- [ ] **Human — judge validation** (protocol, section 9): rate 40 items blind.

  ```
  uv run python -m omissis.eval.judge sheets --split dev --raters <initials>
  # fill results/dev/judge_validation/sheet_<initials>.csv; do not open key.json
  uv run --env-file .env python -m omissis.eval.judge accept --split dev
  ```

  Record the outcome in `docs/decisions.md`.
- [ ] **Human — read up to 20 restored replies per strategy** (`D4+R1`, `D4+R2`):
  confirm or change `base.fuzzy_threshold`; count `wrong_mapping` and the R2 fakes
  left in the text (protocol, section 10); choose the examples of missed
  identifiers for the slides.

## 3. Evaluation on the held-out split (Giuseppe)

- [ ] **Human — `make eval-test`**, once, after `make eval-dev` has reproduced the
  committed dev results on the same machine. A launch that stops half-way is
  resumed as the protocol says in section 4. If the judge was rejected, fill the
  sheet of the fallback before any result is reported.

## B. Open to everyone: can start now

These steps need no result of the evaluation and touch different files.

- [ ] **B1 · `make reproduce`** — *Claimed by:* —
  - Files: the `reproduce` target of `Makefile` (no other target);
    `src/omissis/eval/report.py` and `tests/eval/test_report.py` only for the
    point below.
  - Do: the target runs `uv run --locked python -m omissis.eval.report --split
    <split>` for each of `pilot`, `dev` and `test` that has a folder
    `results/<split>/metrics/`, and skips the others with one line that says so.
    It uses no network, no model, no detector, and reads no text. On the pilot
    the report has no scorecard rows and today writes a `scorecard.md` with a
    title alone: make it write no scorecard when there is no row, with a test.
  - Done when: with the network off, `make reproduce` exits 0 and `git status`
    shows nothing new or changed under `results/` (today this can be shown on
    `pilot`; `dev` and `test` do not exist yet).
- [ ] **B2 · Model and data cards** — *Claimed by:* —
  - Files: `docs/cards.md` (new).
  - Do: one entry for every role of `configs/models.yaml` (read it, never edit
    it), one for what D1 runs on (Presidio and the spaCy model
    `it_core_news_lg`), one for the dataset of 66 synthetic emails. Each entry:
    what it is, where it comes from (link), the revision we pin, its licence,
    how we use it, its limits for us. Start from the lines proposed in
    `docs/handoff/block-2.md` (section 6) and `docs/handoff/block-3.md`
    (section 7). Read every licence at its source, today, and give the link
    where you read it: a licence you could not read there is written "not
    verified", never from memory. The numbers of the dataset that the split
    fixes (how many texts per split) stay marked "after the split".
  - Done when: every role of `configs/models.yaml` has an entry whose model id
    and revision are the ones in that file; every licence has its link or says
    "not verified". **Human:** Giuseppe confirms the licences.
- [ ] **B3 · README, without the results** — *Claimed by:* —
  - Files: `README.md`.
  - Do: what Omissis is and is not; quick start (`make setup`, `make test`,
    `make lint`, `.env` from `.env.example`, the `detect` group, Ollama for D3);
    how to run one text (`omissis run`) and the demo (`make demo`); the
    architecture, one line per stage of the pipeline; the evaluation in one
    paragraph (the seven configurations, the three contrasts), pointing to the
    protocol; `make reproduce`; limitations (threat model, pseudonymisation is
    not anonymisation, derived values, synthetic data only, one reviewer and one
    rater, and the list *Known and not fixed* below). The section *Results* says
    that no result is reported yet. Keep the section on AI assistance.
  - Done when: every command written in the README runs as written on a clean
    clone, and the file holds no number of the evaluation and no claim of
    anonymity (`CLAUDE.md`, rule 7).
- [ ] **B4 · Slide drafts, without numbers** — one file per member,
  `docs/slides/<name>.md`; nothing to claim.
  - Do: the outline of your part and what you say on each slide. Giuseppe:
    problem, existing tools, architecture and design choices, the demo (at most
    90 seconds), conclusions. Andrea: evaluation design, the chart, what did not
    work, limits; backup slides on annotation agreement, judge validation,
    attack design, cost. Mattia: the five detectors and what each finds and
    misses; backup slide with detection per type. Where a number will go, write
    which file of `results/<split>/metrics/` it comes from.
  - Done when: the draft covers its part and holds no number. The drafts are a
    support: the humans write the slides.

## C. Open to everyone: waits for results

- [ ] **C1 · Error examples** — after `make eval-dev` — *Claimed by:* —
  - Files: `results/dev/error_examples.md` (new).
  - Do: from `results/dev/detected/` and the `per_text` lists of
    `results/dev/metrics/`, the identifiers each detector missed, grouped by kind
    of error, each with `text_id`, detector, type and the span; at the top the
    number of D3 failures and the counts Giuseppe gives for `wrong_mapping` and
    the R2 fakes left in the text. No model is called.
  - Done when: every example can be found again in the files it names.
- [ ] **C2 · Results and error taxonomy** — after `make eval-test` — *Claimed by:* —
  - Files: `results/dev/error_taxonomy.md` (new); `docs/cards.md` (the fields left
    for after the split).
  - Do: the taxonomy from `results/dev/error_examples.md`; every statement
    limited to what the decision rule of the protocol, section 12, supports.
  - **Human:** Giuseppe checks every headline number against
    `results/<split>/metrics/`.
- [ ] **C3 · README results, licence, release** (Giuseppe) — after `make eval-test`
  - Files: `README.md` (section *Results*, with the chart), `LICENSE` (new).
  - **Human:** confirm the licences (default: MIT for code, CC BY 4.0 for the
    synthetic data); clean-clone check on a second machine with `make reproduce`;
    tag `v1.0`.
- [ ] **C4 · Presentation** (Thu 26 Nov at the earliest)
  - The numbers go into the slide drafts, each from `results/<split>/metrics/`.
  - **Human — record the demo** (Giuseppe): run the fixtures of the demo once
    through `omissis run --backend cloud` on a configuration whose `cache_dir` is
    `results/cache`, with the task text the app sends, and commit the cache; run
    the demo offline before each rehearsal.
  - **Human:** the final slides; two timed rehearsals, all three.

## Known and not fixed

Declared limits are in `docs/handoff/block-2.md` (section 4) and
`docs/handoff/block-3.md` (section 5). Added on 18 Nov:

- An R2 amount that the reply writes without its decimals ("701 euro" for
  "701,00 euro") stays in the reply; its entry is `dropped`.
- Two replies of D3 that are not valid JSON give no spans for that text: with D4
  the direct identifiers are still masked, the quasi-identifiers are not.
- An empty reply of the local model is an error and is never cached: D3 stops the
  run, and at temperature 0 the same text may stop it again at the next launch.
- Under R2 two people told apart only by a title ("Sig. Ferri", "Sig.ra Ferri")
  share one fake surname and one vault entry.
- The R2 reply of the fixture `fx-bank-03` in `results/cache/cloud.jsonl` was made
  when a date of birth had a fake: it is no longer read.
