# Block 4 · Detectors — task list

Owner: Mattia · Reviewed at the gate by: Giuseppe
Tue 17 – Sun 22 Nov, beside blocks 2 and 3; last task Mon 23 Nov morning
How to use this file: `docs/tasks/README.md`. Specification: `docs/interfaces.md`
(contracts, `detect`, `register_provider`).

This block adds four detectors behind
`omissis.detect.detect(text, detector, config) -> list[Span]`, next to the D0
rules of block 1. It touches `src/omissis/detect/` and `tests/detect/` only, so
it runs beside blocks 2 and 3 without waiting for them: develop each detector
against the five fixtures, whose gold spans are loaded with
`omissis.eval.datasets.load_texts`. Only the last task needs the dataset and
the evaluation of block 3; from the day `make split` has run (task 3.5) the
dev texts exist and `detect` may be run on them (task 4.4b). Before every task
Mattia runs `git switch main && git pull` and creates the branch.

- [ ] **4.0 · Dispatch table** — `detect/__init__.py` (small and first: the app of task 2.7 and the detection metrics of task 3.9 wait for it)
  - Do: an explicit dispatch table from `DetectorId` to detector, from which
    `supported_detectors()` is derived (`docs/interfaces.md`, section 3). An
    id with no entry raises `NotImplementedError` and never falls through to
    D0; `CacheMissError` and `ConfigError` are re-raised before the generic
    `except`, and a detector whose library or weights are missing on the
    machine raises `ConfigError`. Replace the old task ids in
    `src/omissis/detect/` and `tests/detect/` (task 2.1 leaves them to this
    block: A1 and A2 become "block 1"; A3, A4, A6 and A7 become 4.1 to 4.4;
    "B0" becomes "block 0" and "workstream A" becomes "block 4").
  - Done when: tests show that an id taken out of the table raises
    `NotImplementedError` instead of returning D0 spans, and that the two
    errors propagate. The test that expects D1 to D4 "not built yet" is
    rewritten against the table and loses each detector as it is built.

- [ ] **4.1 · D1 Presidio** — `detect/presidio.py`
  - **Human:** approve the new dependencies (Presidio, spaCy, one Italian
    spaCy model) and their pinned versions before they are added. They go in
    the dependency group `detect` of `pyproject.toml`, as every detector
    library does (`docs/tasks/README.md`, "Working beside another block").
  - Do: Presidio analyser with the Italian pipeline and Italian recognisers,
    mapped to our `SpanType`s, available through `detect()` as D1.
  - Done when: a test shows an Italian person name, city and codice fiscale
    detected in an Italian sentence; unmapped Presidio labels are listed in the
    module docstring; the tests that need Presidio or the spaCy model start
    with `pytest.importorskip`, so they are skipped where the group is not
    installed.

- [ ] **4.2 · D2 ready-made classifier** — `detect/classifier.py`
  - Blocked by: model `d2` pinned in `configs/models.yaml`.
  - **Human:** read the model card, confirm the licence allows our use, and
    approve the label-mapping table; approve the new dependencies
    (`transformers`, `torch`) and their pinned versions before they are added.
  - Do: token classification with sliding windows and overlap for long texts,
    spans merged back to character offsets, labels mapped to `SpanType`. The
    model is used as is: no fine-tuning, weights never in the repository.
  - Done when: a text longer than one window yields correct offsets across the
    window border; labels with no counterpart are documented, not invented;
    the test that needs the model is skipped with `pytest.importorskip` where
    the group is missing and with `pytest.skip` where the weights are not on
    disk: no test downloads a model.

- [ ] **4.3 · D3 local LLM** — `detect/llm.py`, `detect/local_runtime.py` (cut this and 4.4 if the block is late)
  - Blocked by: model `d3` pinned and reference machine recorded in
    `docs/decisions.md`.
  - **Human:** approve the runtime dependency; read the prompt; read 20 raw
    outputs before trusting the detector.
  - Do: register the local runtime with `backends.register_provider`; call it
    through `backends.complete` with role `d3`; prompt asking for JSON items
    `{text, type, reason}` for quasi-identifiers and special categories; schema
    validation; offsets by string search (every occurrence; drop and count
    items whose text is absent); one retry on invalid JSON, with a different
    prompt (the cache answers an identical one with the same invalid reply),
    then log, count the failure and return no spans.
  - Done when: tests with a fake provider cover valid JSON, invalid JSON twice,
    hallucinated text, repeated text; no test needs the real model.

- [ ] **4.4 · D4 hybrid** — `detect/hybrid.py`
  - Do: D0 ∪ D2 for direct identifiers, D3 for quasi-identifiers and special
    categories, combined with `merge`. No new detection logic.
  - Done when: a test with fake detectors shows the routing by class; a test
    with a fake D3 that raises `RuntimeError` shows that the D0 ∪ D2 spans are
    still returned, and one with a fake D3 that raises `ConfigError` or
    `CacheMissError` shows that D4 raises it too.

- [ ] **4.4b · D0 limits on dev** — `detect/rules.py`
  - Blocked by: `make split` has run (task 3.5), so the dev texts exist.
  - Do: check on the dev texts the D0 limits found in the review of block 1 (a
    phone read in a date followed by a time or in a time range, the second of
    two phone numbers in a row, decimals after a point, IBANs written with
    hyphens); fix the ones that occur, with tests; list the others as known
    limits in the hand-over note.

- [ ] **4.5 · Full evaluation on dev** — `configs/eval.yaml`, `results/` · Mon 23 Nov morning
  - Blocked by: gate G3.
  - Do: append `D1+R1`, `D2+R1`, `D4+R1`, `D4+R2` to `configs/eval.yaml`
    exactly as written in `docs/interfaces.md` section 4; print the call count
    and estimated cost; after the human's go-ahead run `make eval-dev` on the
    reference machine, then the timing command of task 3.9: together they
    measure all five detectors and their latency and fill the detection table
    of the scorecard; collect categorised examples of missed identifiers from
    dev in
    `results/dev/error_examples.md` for the error taxonomy.
  - **Human:** read 20 restored replies on dev and confirm or change
    `base.fuzzy_threshold` in `configs/eval.yaml`, recording it in
    `docs/decisions.md`. A change means running `make eval-dev` again; the LLM
    calls come from the cache, so it costs nothing. On the same replies (up to
    20 per strategy) count `wrong_mapping` and the R2 fake values left in the
    text, as the protocol asks in section 10; the agent writes those counts
    and the number of D3 failures at the top of
    `results/dev/error_examples.md`.
  - **Human:** choose the examples of missed identifiers for the slides.

- [ ] **4.6 · Hand-over note** — `docs/handoff/block-4.md`
  - Do: the note described in `docs/tasks/README.md`: what each detector finds
    and misses on dev, the dev chart, open issues, the LLM spend so far; the
    `docs/cards.md` lines proposed for the D2 and D3 models and for the spaCy
    model of D1.
  - **Human:** set the tag `freeze`; Giuseppe reads the note and the code, and
    G4 is ticked.
