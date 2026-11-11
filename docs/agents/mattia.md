# Personal instructions — Mattia's agent

You work for **Mattia**, owner of **workstream A · Detection and app**. Read the
shared `CLAUDE.md` first; it prevails. Mattia reviews Andrea's workstream C and
is reviewed by Giuseppe.

Talk to Mattia in Italian unless he prefers otherwise; write code, comments,
commit messages and docs in English. Explain what you built in plain terms: he
must be able to defend every detector in the Q&A.

## Your paths

`src/omissis/detect/` (`rules.py`, `presidio.py`, `classifier.py`, `llm.py`,
`hybrid.py`, `merge.py`), `src/omissis/app.py`, `src/omissis/eval/detection.py`.

Your log: `docs/log/ws-a.md` (you are its only writer). Read the other two
logs at the start of each session.

## Tasks by milestone

| Milestone | You produce (code + tests) | Mattia verifies or decides |
|---|---|---|
| M1 · 13 Nov | **D0** rules: IBAN (mod-97), codice fiscale (check character), partita IVA (check digit), Italian phone formats, email, € amounts; curated valid/invalid test sets. **D1** Presidio with an Italian spaCy pipeline and the Italian recognisers. `merge.py` implementing the overlap rule | Checks two validators by hand against the official algorithm; reads the D1 output on the 5 example emails |
| M2 · 15 Nov | **D2** ready-made classifier: sliding windows with overlap, span merge, label mapping to our taxonomy. `eval/detection.py`: entity-level precision, recall, F1 (exact and overlap), per class and type, and the text-level leak rate | Approves the label-mapping table; confirms the classifier's licence terms are respected |
| M3 · 19 Nov | **D3** local LLM detector; **D4** hybrid (D0 ∪ D2 for direct identifiers, D3 for quasi-identifiers and special categories). Gradio app. Latency per detector (p50, p95) | Reads the D3 prompt and 20 raw D3 outputs; tries to break the app with odd inputs |
| M5 · 23 Nov | Detection section of the scorecard; categorised examples of missed identifiers | Chooses the examples for the slides |

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
  the item and count it as a hallucinated span. Invalid JSON: one retry, then log
  the failure and return an empty list. The pipeline must never crash.
- **D3 determinism:** temperature 0, fixed seed, one pinned weights file. Official
  D3 runs for the evaluation are executed once on the reference machine agreed at
  M0 and stored in the cache; everyone else replays them.
- **D4** is composition only: no new detection logic, just routing by class and
  `merge.py`.
- **App:** input box with ready-made examples; masked text exactly as sent, with
  highlighted placeholders; restored reply; disclosure panel (what was hidden,
  class, detector, D3 reason, restoration failures); selectors for detector,
  strategy and backend; replay mode that runs with no network and no GPU. The app
  calls `pipeline.py` and contains no pipeline logic of its own.
- **Leak rate** is the primary safety metric: share of texts with at least one
  direct identifier missed. Recall matters more than precision; report both.

## Shared duties of your human (support them, do not do them in their place)

- **Text review:** 22 of the 66 synthetic texts. The human checks realism, corrects
  the inline tags and confirms the gold fields. You may prepare a checklist or
  highlight suspicious tags; you may not mark a text as reviewed.
- **Double annotation:** part of the 13 texts annotated independently by two
  humans. Never show your human the other annotator's labels before they finish.
- **Slides and rehearsal:** you may draft slide text and figures from results in
  `results/`; every number on a slide must come from a file produced by
  `make reproduce`.

## How to hand work back

End every task with: files changed; commands run and their real output; open
doubts; the three reviewer questions; a proposed commit message; confirmation
that you appended the entry to `docs/log/ws-a.md`; a proposed line for
`docs/ai_use.md`. Then wait. Do not stage, commit or push (shared rule 1).
