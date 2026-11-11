# Workstream A · Detection and app — task list

Owner: Mattia · Reviewer: Giuseppe · How to use this file: `docs/tasks/README.md`

Specification: `docs/interfaces.md` (contracts, `detect`, `register_provider`)
and `docs/evaluation_protocol.md`, sections 6 and 11. Read them before the
first task. The boundary is
`omissis.detect.detect(text, detector, config) -> list[Span]`.

## Step 1 · Skeleton · M1 · Fri 13 Nov

- [ ] **A1 · D0 rules** — `detect/rules.py`
  - Blocked by: B0.
  - Do: regular expressions plus validation for IBAN (mod-97), codice fiscale
    (check character), partita IVA (check digit), Italian phone numbers, email,
    amounts in euro. One function per type returning `Span`s with source `D0`.
  - Done when: curated lists of at least 10 valid and 10 invalid examples per
    checksum type sit in `tests/detect/`; valid ones are all found, invalid
    ones all rejected; all examples are synthetic (IBANs built on bank code
    `00000`); spans satisfy `span.matches(text)` on a multi-entity text.
  - **Human:** check two validators by hand against the official algorithm;
    confirm that bank code `00000` is not assigned to any real bank.

- [ ] **A2 · Span merging and the `detect` entry point** — `detect/merge.py`, `detect/__init__.py`
  - Blocked by: B0.
  - Do: `merge(spans, source_priority)` implementing the overlap rule: longer
    span wins, then higher confidence, then earlier in `source_priority`.
    Output sorted by `start`, non-overlapping. Then `detect()` for
    `DetectorId.D0` (rules, then `merge`), raising `NotImplementedError` with
    a clear message for detectors not built yet.
  - Done when: tests cover nested, partially overlapping, identical and
    adjacent spans, and a tie decided by each of the three criteria;
    `detect(text, D0, config)` returns the D0 spans and never raises on empty
    or odd input.

## Step 2 · Second detector and pilot · M2 · Sun 15 Nov

- [ ] **A3 · D1 Presidio** — `detect/presidio.py`
  - Blocked by: A2.
  - **Human:** approve the new dependencies (Presidio, spaCy, one Italian
    spaCy model) and their pinned versions before they are added.
  - Do: Presidio analyser with the Italian pipeline and Italian recognisers,
    mapped to our `SpanType`s, available through `detect()` as `DetectorId.D1`.
  - Done when: a test shows an Italian person name, city and codice fiscale
    detected in an Italian sentence; unmapped Presidio labels are listed in the
    module docstring.

- [ ] **A4 · D2 ready-made classifier** — `detect/classifier.py`
  - Blocked by: A3; model `d2` pinned in `configs/models.yaml`.
  - **Human:** read the model card, confirm the licence allows our use, and
    approve the label-mapping table.
  - Do: token classification with sliding windows and overlap for long texts,
    spans merged back to character offsets, labels mapped to `SpanType`.
    The model is used as is: no fine-tuning, weights never in the repository.
  - Done when: a text longer than one window yields correct offsets across the
    window border; labels with no counterpart are documented, not invented;
    the test that needs the model is marked so CI can skip it.

- [ ] **A5 · Detection metrics** — `eval/detection.py`
  - Blocked by: C1 (fixtures with gold spans).
  - Do: the detection metrics exactly as defined in
    `docs/evaluation_protocol.md`, section 6, written to
    `results/metrics/detection.json`.
  - Done when: hand-computed toy cases in `tests/` give the expected numbers,
    including a text with zero gold spans and a detector with zero predictions.

## Step 3 · Full system · M3 · Thu 19 Nov

- [ ] **A6 · D3 local LLM** — `detect/llm.py`, `detect/local_runtime.py`
  - Blocked by: B3 (backends); model `d3` pinned; reference machine decided.
  - **Human:** approve the runtime dependency; read the prompt; read 20 raw
    outputs before trusting the detector.
  - Do: register the local runtime with `backends.register_provider`; prompt
    asking for JSON items `{text, type, reason}` for quasi-identifiers and
    special categories; schema validation; offsets by string search (every
    occurrence; drop and count items whose text is absent); one retry on
    invalid JSON, then log and return no spans.
  - Done when: tests with a fake provider cover valid JSON, invalid JSON twice,
    hallucinated text, repeated text; no test needs the real model.

- [ ] **A7 · D4 hybrid** — `detect/hybrid.py`
  - Blocked by: A4, A6.
  - Do: D0 ∪ D2 for direct identifiers, D3 for quasi-identifiers and special
    categories, combined with `merge`. No new detection logic.
  - Done when: a test with fake detectors shows the routing by class.

- [ ] **A8 · Gradio app** — `app.py`, `make demo`
  - Blocked by: B4 (pipeline). Tests go in `tests/app/`.
  - **Human:** approve the Gradio dependency; try to break the app.
  - Do: input box with ready-made examples; masked text exactly as sent with
    highlighted placeholders; restored reply; disclosure panel (surrogate,
    class, detector, D3 reason, restoration problems); selectors for detector,
    strategy and backend. The app calls `pipeline.protect_send_restore` only.
  - Done when: `make demo` starts in replay mode with no network and no GPU and
    shows a full run from the cache; a cache miss shows a readable message.

- [ ] **A9 · Latency** — `eval/detection.py`
  - Blocked by: A7.
  - Do: p50 and p95 latency per detector on the dev texts, written to
    `results/metrics/`.
  - Done when: one command produces the table; the machine is named in it.

## Step 4 · Results · M4–M5 · Sat 21 – Mon 23 Nov

- [ ] **A10 · Detection results and examples**
  - Blocked by: M4 freeze and `make eval-test` run by the humans.
  - Do: detection columns of the scorecard; categorised examples of missed
    identifiers from the **dev** split for the error taxonomy.
  - **Human:** choose the examples for the slides.

## Step 5 · Presentation · M6 · Wed 25 Nov

- [ ] **A11 · Slides for detection and the demo**
  - Blocked by: A10.
  - Do: draft content for Mattia's part (the five detectors and what each
    finds), every number taken from `results/metrics/`; a demo script of at
    most 90 seconds that works in replay mode.
  - **Human:** write the final slides, run the demo offline, rehearse twice
    with the team.
