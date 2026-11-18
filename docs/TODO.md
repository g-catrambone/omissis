# What is left

One list, in order. It replaces the task lists of the blocks. A line marked
**Human** is never done by an agent. Tick a line when it is done; decisions go in
`docs/decisions.md`. Specifications: `docs/interfaces.md` and
`docs/evaluation_protocol.md`. History of the code: `docs/handoff/`.

Needed on the machine that runs the evaluation: `uv sync --locked --group detect`
(Presidio, spaCy, `transformers`), the D2 weights, Ollama running with
`gpt-oss:20b` for D3 (`brew services start ollama`), `GROQ_API_KEY` in `.env`.

## 1. Data (protocol, section 3)

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

## 2. Evaluation on dev

- [ ] **Human — approve the prompts** before the first judged result: attacks
  (`attacks.LINKAGE_PROMPT`, `ATTRIBUTES_PROMPT`), T3 (`utility.T3_TASK`), judge
  (`judge.PROMPT`). They are frozen once a result exists.
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
  identifiers. The agent writes the counts, the D3 failures and the categorised
  examples in `results/dev/error_examples.md`.

## 3. Evaluation on the held-out split

- [ ] **Human — `make eval-test`**, once, after `make eval-dev` has reproduced the
  committed dev results on the same machine. A launch that stops half-way is
  resumed as the protocol says in section 4. If the judge was rejected, fill the
  sheet of the fallback before any result is reported.

## 4. Closing

- [ ] Results: chart and scorecard from the metrics files, error taxonomy
  (`results/dev/error_taxonomy.md`), `docs/cards.md` with one entry per model and
  dataset (source, revision, licence, how we use it; lines proposed in
  `docs/handoff/`; D2 is CC BY-NC-ND 4.0). **Human:** check every headline number
  against `results/<split>/metrics/`.
- [ ] `make reproduce` (today a stub): it calls
  `python -m omissis.eval.report --split <split>` for every split, with no network,
  no model, no detector and without reading `data/test/`.
- [ ] `README.md`: quick start, architecture, results chart, limitations (threat
  model, pseudonymisation is not anonymisation, derived values, synthetic data
  only, one reviewer and one rater), licence. **Human:** confirm the licences
  (default: MIT for code, CC BY 4.0 for the synthetic data); clean-clone check on a
  second machine; tag `v1.0`.

## 5. Presentation (Thu 26 Nov at the earliest)

- [ ] **Human — record the demo**: run the fixtures of the demo once through
  `omissis run --backend cloud` on a configuration whose `cache_dir` is
  `results/cache`, with the task text the app sends, and commit the cache; run the
  demo offline before each rehearsal.
- [ ] Drafts in `docs/slides/<name>.md`; every number comes from
  `results/<split>/metrics/`. **Human:** the final slides; two timed rehearsals.

## Known and not fixed

Declared limits are in `docs/handoff/block-2.md` (section 4) and
`docs/handoff/block-3.md` (section 5). Added on 18 Nov:

- An R2 amount that the reply writes without its decimals ("701 euro" for
  "701,00 euro") stays in the reply; its entry is `dropped`.
- Two replies of D3 that are not valid JSON give no spans for that text: with D4
  the direct identifiers are still masked, the quasi-identifiers are not.
- Under R2 two people told apart only by a title ("Sig. Ferri", "Sig.ra Ferri")
  share one fake surname and one vault entry.
- The R2 reply of the fixture `fx-bank-03` in `results/cache/cloud.jsonl` was made
  when a date of birth had a fake: it is no longer read.
