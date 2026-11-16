# Block 2 · Core completion — task list

Owner: Giuseppe · Reviewed at the gate by: Andrea · Mon 16 – Wed 18 Nov
How to use this file: `docs/tasks/README.md`. Specification: `docs/interfaces.md`.
Start from `docs/handoff/block-1.md`.

Block 1 left a pipeline that works with the D0 rules. This block completes the
core so that the evaluation can be built on it without any further detector:
the three references that come from human annotation, the real cloud model,
the proper entity resolver, the second replacement strategy, and the app.

- [ ] **2.1 · Clean-up after the reorganisation**
  - Do: replace every reference to the old task ids (A*, B*, C*) and to
    "workstream" or "step" with the task numbers of these lists (or with
    "block 1" where no task succeeds the old one), in the
    `NotImplementedError` messages, comments and module docstrings of block
    2's modules under `src/omissis/` and of `tests/core/`, in the `Makefile`
    messages (text only: an agreed exception to the rule on other blocks'
    targets), in the comments of `configs/*.yaml` except `configs/models.yaml`,
    in `.env.example`, and in the Status section of `README.md` (this and the
    docstring of `contracts.py` are agreed exceptions too). The ids in
    `src/omissis/detect/` and `tests/detect/` are left to task 4.0, those in
    `src/omissis/eval/datasets.py`, `tests/data/` and
    `docs/annotation_guide.md` to task 3.1. No behaviour changes. Old to new:
    B1 to B4 become "block 1"; B5 is 2.2, B6 2.3, B7 2.5, B8 2.6 (the
    threshold is re-checked on dev in 4.5), B9 5.2, B11 2.4; A8 is 2.7; C6 is
    3.5 and C10 3.10; "Step 0" is "Block 0".
  - Also: the three tests that match an old id in a message
    (`test_pipeline.py`, `test_replace.py`, `test_restore.py`) change in the
    same pull request; the test of the unpinned models in
    `tests/core/test_config.py` reads a temporary file instead of
    `configs/models.yaml`, so that a pin cannot turn CI red;
    `configs/skeleton.yaml` gets `cache_dir: results/scratch/skeleton`.
  - Done when: `grep` finds no old task id in those files; `make test` passes.
    Merge this before any model is pinned.

- [ ] **2.2 · References and named configurations** — `config.py`, `pipeline.py`, `cli.py`, `configs/eval.yaml`
  - Do, all as specified in `docs/interfaces.md` sections 3 and 4: the
    configuration key `detector` accepting `GOLD` and `NONE`; the `gold_spans`
    argument of `mask` and of `protect_send_restore`, with the rules that tie
    it to `config.detector`; `load_eval_configs`; `configs/eval.yaml` with the
    three references; in the command line, gold spans taken from the JSON
    record when the detector is `GOLD`, and the new command `omissis mask`.
  - The signature of `protect_send_restore` changes by specification: update
    `tests/core/test_boundaries.py` to the new signature. This is a change of
    the contract agreed in `docs/decisions.md`, not a test weakened to pass.
  - Also: `omissis mask` masks every record with a fresh vault, and a test
    asserts that the masked text it writes equals
    `protect_send_restore(...).masked_text` for the same record and
    configuration; `NotImplementedError` and `UnicodeDecodeError` exit with
    status 2 like the other errors, and a YAML syntax error becomes a
    `ConfigError`; a D3 `reason` that quotes a masked value is rewritten with
    the surrogate, or dropped, before it enters the disclosure; a test covers
    the vault being erased when the provider raises. The choices the
    specification leaves open (`NONE` with `gold_spans`, `GOLD` with an empty
    list, unknown `--names`, a plain-text input with `GOLD`) are listed in the
    hand-back with the lines proposed for `docs/interfaces.md`.
  - Done when: an integration test with a fake provider runs a fixture end to
    end with detector `GOLD`; with `mask_quasi: true` no gold span text appears
    in the prompt handed to the provider, and with `mask_quasi: false` the
    quasi-identifier texts appear and no other gold span text does (both
    asserted); detector `NONE` sends the text unchanged; `GOLD` without
    `gold_spans`, and a detector with `gold_spans`, raise `ValueError`; two
    configurations that differ only in detector have different run ids;
    `omissis mask` writes the masked-batch files for the three references on
    the fixtures (under `results/scratch/`: the fixtures belong to no split).

- [ ] **2.3 · Entity resolver** — `resolve.py`
  - **Human:** provide or approve the first-name list and its source.
  - Do: replace the interim resolver with `resolve()` as specified, rules only.
  - Also: two entities that the resolver keeps apart never receive the same
    placeholder, even when their canonical values are equal (today `replace`
    matches on type and canonical value only).
  - Done when: tests cover "Marco Ferri" / "Ferri" / "il Sig. Ferri" merged;
    two people with one surname and different first names kept apart; gender
    from titles, then from the name list, else `UNKNOWN`; non-person types
    merged on normalised equality; placeholders carry `_M` or `_F` when the
    gender is known.

- [ ] **2.4 · Cloud provider** — `backends/`, `.env.example`
  - **Human:** with the team, pin in `configs/models.yaml` the models for
    `cloud`, `generator`, `attacker` and `judge`, all on the API of one
    provider (if the team wants a second provider, name it now: it is built in
    this task too). Approve the SDK dependency; create the key with a spending
    cap and pass it privately.
  - Do: one provider for the chosen API, registered with `register_provider`,
    reading the key from the environment variable named in `.env.example`; it
    serves every role pinned to that API.
  - Also (what concerns `backends/__init__.py` and `pipeline.py` here does not
    wait for the pin): `LLMRequest` always carries `temperature: 0` (the caller's params
    are merged over it) and integral floats are normalised before hashing;
    `max_tokens` is set in the request that `pipeline.py` builds, so that it
    is part of the cache key, and the provider raises on an empty reply or on
    one cut at the token limit instead of caching it; the cache writer adds a
    newline first when the file does not end with one; decide and document how
    the key reaches the process (`uv run --env-file .env` needs no new
    dependency); the provider is registered when `omissis.backends` is
    imported, under the `provider` name the human writes in
    `configs/models.yaml`, with the SDK imported inside the function.
  - Done when: a test with the SDK call mocked shows the request built from
    `LLMRequest` and the text returned; a missing key gives a clear error; one
    real call, launched by the human, lands in the cache.

- [ ] **2.5 · R2 realistic fakes** — `replace/fakes.py`, `replace/data/`
  - **Human:** approve the fake-value lists (names, cities, employers) and
    their sources.
  - Do: `replace()` for `Strategy.R2`: same-gender names, checksum-valid IBANs
    on bank code `00000`, amounts of the same order of magnitude, cities of
    similar size; deterministic for the seed; never a value already in the
    text. The lists live in `replace/data/`; block 3 builds its profile pool
    to be disjoint from them.
  - Done when: same seed gives the same fakes; a fake is never equal to a
    value in the source text; fake IBANs pass the D0 validator.

- [ ] **2.6 · Fuzzy restore and R2 restore** — `restore.py`
  - Do: step 3 of `restore`; whole-token matching for R2 surrogates and their
    variants; `restored_fuzzy` events; the count of restored fakes per reply.
  - Also: one outcome per vault entry (an entry with an `altered_unresolved`
    event gets no `dropped` event); placeholders escaped with backslashes or
    written with a hyphen or a non-breaking hyphen are recognised; after
    substitution the output is scanned with `PLACEHOLDER_RE` and every
    placeholder-shaped token still in it has an event, whatever its label; the
    count of restored fakes per reply is the number of `restored` and
    `restored_fuzzy` events of an R2 run; two run configurations,
    `configs/gold-r1.yaml` and `configs/gold-r2.yaml`, for the ten calls of
    the human. Propose the matching lines for the
    `restore` paragraph of `docs/interfaces.md` and the entry for
    `docs/decisions.md`.
  - Done when: tests cover a near-miss above and below the threshold and a
    fake value that is a substring of another word (not restored).
  - **Human:** send the 5 fixtures once to the real cloud model with R1 and
    once with R2, on gold spans (ten calls, negligible cost) and read the ten
    restored replies: with `echo` the reply is the prompt and restoration is
    trivial. Keep `fuzzy_threshold` at its default; it is re-checked on dev in
    task 4.5.

- [ ] **2.7 · Gradio app** — `app.py`, `make demo` (first thing to cut if the block is late; not a condition of G2: it may be finished beside block 3)
  - **Human:** approve the Gradio dependency; record one fixture with D0 and R1
    in `results/cache/` through `omissis run --backend cloud`, with the
    configuration and the task text the app uses (task P.1 adds the other
    combinations); try to break the app.
  - Do: input box with the fixtures as ready-made examples; masked text
    exactly as sent with highlighted placeholders; restored reply; disclosure
    panel (surrogate, class, detector, reason, restoration problems);
    selectors for detector, strategy and backend, listing the detectors of
    `omissis.detect.supported_detectors()`. Texts go through
    `pipeline.protect_send_restore` only. Tests go in `tests/app/`.
  - Blocked by: task 4.0 merged (`supported_detectors` exists).
  - Also: the test of "a detector not built yet" fakes `supported_detectors`
    and `detect`, and never relies on a real detector being absent; in replay
    mode the app reads `results/cache/`; with backend `cloud` it reads and
    writes a folder under `results/scratch/`, never `results/cache/`.
  - Done when: `make demo` starts in replay mode with no network and no GPU and
    shows a full run from the cache; a cache miss and a detector not built yet
    both show a readable message.

- [ ] **2.8 · Hand-over note** — `docs/handoff/block-2.md`
  - Do: the note described in `docs/tasks/README.md`, with one worked call for
    `mask` with gold spans (with and without `mask_quasi`),
    `protect_send_restore` with gold spans, `complete` on each pinned role,
    `load_eval_configs` and `omissis mask`; and the `docs/cards.md` lines
    proposed for the pinned models.
  - **Human:** set the tag `block-2`; Andrea reads the note and the code, and
    G2 is ticked.
