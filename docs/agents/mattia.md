# Personal instructions — Mattia's agent

You work for **Mattia**. Read the shared `CLAUDE.md` first; it prevails.

Write code, comments, commit messages and docs in English.

The relay of blocks is over (`docs/decisions.md`, 18 Nov). What is left is in
`docs/TODO.md` and is written on the branch `final-steps`: read *How to work on
the branch* at the top of that file before anything else.

**When told to start or continue**, check that you are on `final-steps` and up to
date, then take the step Mattia names or, when none is named, the first open step of
sections B and C that nobody has claimed and whose results exist. Mattia claims the
step before you write anything. Do one step per hand-back. Never do a line marked
**Human**, and never take a step of sections 1 to 3: they are Giuseppe's.

## Component notes and known traps

These notes were written for the blocks. Where they disagree with
`docs/decisions.md`, the decisions prevail.

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

## How to hand work back

End every task with: files changed; commands run and their real output; open
doubts; a proposed commit message; a proposed line for `docs/ai_use.md`. Then wait.
Do not stage, commit or push unless your human asks (shared rule 1).
