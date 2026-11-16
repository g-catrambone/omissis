# Personal instructions — Mattia's agent

You work for **Mattia**, owner of **block 1 · Skeleton** (already written, to be
merged) and of **block 4 · Detectors**. Read the shared `CLAUDE.md` first; it
prevails. At the gates Giuseppe and Andrea review block 1 and Giuseppe reviews
block 4; Mattia reviews Andrea's block 3 and, with Andrea, block 5.

Write code, comments, commit messages and docs in English.

**When told to start or continue, work from `docs/tasks/block-1.md`** until gate
G1 is ticked, then from `docs/tasks/block-4.md`, as described in
`docs/tasks/README.md`. Block 4 runs beside blocks 2 and 3: it does not wait
for their gates, except its task 4.5, which needs gate G3. After gate G4 it is
not your turn: change nothing, except a `fix/…` branch for a defect in block
4's code that Mattia explicitly asks for. After gate G5, task P.3 is yours.

## Your paths

Block 4: `src/omissis/detect/` (`rules.py` and `merge.py` from block 1, then
`presidio.py`, `classifier.py`, `llm.py`, `local_runtime.py`, `hybrid.py`);
`tests/detect/`; in `configs/eval.yaml` only the two edits allowed by
`docs/interfaces.md` section 4 (append the four configurations; change
`base.fuzzy_threshold` after Mattia's decision); the files task 4.5 writes in
`results/`; `docs/handoff/block-1.md` and `block-4.md`. After G5:
`docs/slides/mattia.md`.

The rest of what block 1 wrote passes to others at gate G1: the core modules
(`pipeline.py`, `resolve.py`, `replace/`, `restore.py`, `backends/`, `cli.py`)
to Giuseppe's block 2, `eval/datasets.py` and the annotation guide to Andrea's
block 3. From then on you do not change them: Giuseppe and Andrea are editing
them in the same days. If a detector needs something from them, describe it
and stop.

## What the blocks deliver

| Block | You produce (code + tests) | Mattia verifies or decides |
|---|---|---|
| 1 · Skeleton · merged Mon 16 Nov | Already written. Now: answers on the code for the reviewers, the hand-over note | Opens the pull request; checks two validators by hand and the bank code `00000`; merges; tags `block-1` |
| 4 · Detectors · Tue 17 – Sun 22 Nov, then Mon 23 morning | D1 Presidio; D2 ready-made classifier; D3 local LLM; D4 hybrid; on Monday 23 the four configurations in `configs/eval.yaml` and the full evaluation on dev; hand-over note | Approves dependencies and the label mapping; confirms the classifier's licence; pins `d2` and `d3` with the team; reads the D3 prompt and 20 raw outputs; confirms the fuzzy threshold on dev; tags `freeze` |

Develop each detector against the five fixtures (`data/fixtures/`, gold spans
loaded with `omissis.eval.datasets.load_texts`). The dev texts exist from the
day `make split` has run (task 3.5): from then you may run `detect` on them;
until then do not wait for them. Before every task Mattia runs
`git switch main && git pull`, because blocks 2 and 3 are merging too; you
share with them only `pyproject.toml` and `uv.lock`.

## Reviewing blocks 3 and 5

When Mattia asks you to help review: at G3, `docs/handoff/block-3.md` and the
code of block 3 against `docs/evaluation_protocol.md`; at G5, the detection and
latency columns of `results/<split>/scorecard.md` against `results/<split>/metrics/`, and
`make reproduce`. Run the tests and give concrete findings with file and line.
You advise; Mattia reviews.

## Component notes and known traps

- **D0 must be exact.** Unit tests require 100% detection and 0% false acceptance
  on the curated sets. All test identifiers are synthetic: build valid IBANs on a
  documented non-existent bank code, never copy a real one.
- **D1:** Presidio needs the Italian language and recognisers configured
  explicitly; verify in a test that an Italian codice fiscale is detected, do not
  assume the default English setup covers it.
- **D2:** read the model card before writing the mapping. The model is used as
  is: no fine-tuning, no redistribution of weights (its licence forbids
  derivatives). Pin it by name and revision in `configs/models.yaml`. It may have
  no label for organisations, amounts or generic dates: map what exists and
  document the gaps, do not invent labels.
- **D3 returns text, not offsets.** Ask for JSON items `{text, type, reason}`,
  validate against a schema, then locate each `text` in the source. If the text
  occurs several times, mark every occurrence. If it does not occur at all, drop
  the item and count it as a hallucinated span. Invalid JSON: one retry with a
  different prompt (the cache answers an identical one), then log the failure
  and return an empty list. A missing model or cache entry is not a failure of
  this kind: `CacheMissError` and `ConfigError` propagate.
- **D3 goes through `backends.complete`.** Register the local runtime as a
  provider with `backends.register_provider`; do not call it directly, so D3
  outputs are cached and replayable like every other LLM call.
- **D3 determinism:** temperature 0, fixed seed, one pinned weights file. Official
  D3 runs for the evaluation are executed once on the reference machine recorded in
  `docs/decisions.md` before task 4.3, and stored in the cache; everyone else replays them.
- **D4** is composition only: no new detection logic, just routing by class and
  `merge.py`.

## Shared duties of your human (support them, do not do them in their place)

- **Text review (during block 3):** 22 of the 66 synthetic texts, on a branch
  `b3/review-<initials>`. The human checks realism, corrects the inline tags
  and confirms the gold fields. You may prepare a checklist or highlight
  suspicious tags; you may not mark a text as reviewed.
- **Double annotation (during block 3):** part of the 13 texts annotated
  independently by two humans. Never show your human the other annotator's
  labels before they finish.
- **Judge validation (during block 3):** rates 40 dev items blind and sends
  the sheet privately to Andrea. Do not show the judge's scores, the other
  rater's sheet or the replacement strategy before the ratings are finished.
- **Final evaluation (block 5):** the three members launch `make eval-test`
  together, once.
- **Slides and rehearsal:** task P.3 of `docs/tasks/block-5.md`. You draft
  content in your member's file under `docs/slides/`; every number must come
  from a file in `results/<split>/metrics/`.

## How to hand work back

End every task with: files changed; commands run and their real output; open
doubts; the three reviewer questions; a proposed commit message; a proposed line
for `docs/ai_use.md`. Then wait. Do not stage, commit or push (shared rule 1).
