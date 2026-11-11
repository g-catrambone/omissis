# Workstream B · Pseudonymisation core — task list

Owner: Giuseppe · Reviewer: Andrea · How to use this file: `docs/tasks/README.md`

Specification: `docs/interfaces.md`. This list says in which order to build
the pieces and how to tell when each is finished.

## Step 0 · Foundation · M0 · Wed 11 Nov

- [x] **B0 · Foundation** — scaffold, `contracts.py`, `config.py`, `vault.py`, boundary stubs
  - Blocked by: nothing. Every other task of every workstream waits for this one.
  - Do: `pyproject.toml` (Python 3.11, `uv`, dependencies `pyyaml`, dev group
    `pytest` and `ruff`), `uv.lock`, `.python-version`, `.env.example`,
    `Makefile` with the targets of `CLAUDE.md` section 6 (targets not built
    yet print which task builds them and exit non-zero), CI workflow running
    `make lint` and `make test` on pushes to `main` and on pull requests,
    `README.md` (what the project is, status, quick start, AI-assistance
    statement), `configs/example.yaml`, `configs/models.yaml` with every role
    set to `TO_BE_PINNED`. Then `contracts.py`, `config.py`, `vault.py` and
    the `backends` request types, `cache_key` and provider registry, fully
    implemented as in `docs/interfaces.md` sections 1, 2 and 4; and the
    boundary functions of section 3 as stubs with the exact signatures, a
    docstring restating the specified behaviour, and
    `raise NotImplementedError` naming the task that builds them.
  - Done when: `make setup`, `make test` and `make lint` pass from a clean
    clone; tests cover every validation rule of section 1, the placeholder
    round trip and its rejections, config loading with invalid values and
    unknown keys, the unpinned-model refusal, the vault never showing
    originals in `repr` or logs, `cache_key` changing with each of its inputs,
    and the parameter names of every boundary function; no test asserts
    `NotImplementedError`, so the tests stay valid when stubs are filled in.
  - Note: this task creates `src/omissis/detect/__init__.py` with the `detect`
    stub, although the folder belongs to workstream A, so that the boundary
    exists from the start. This is the one agreed exception to the path rule;
    workstream A owns the file from the moment B0 is merged.
  - **Human:** read `contracts.py` and the stubs with the whole team before
    merging; Mattia and Andrea confirm they can build on them.

## Step 1 · Skeleton · M1 · Fri 13 Nov

- [ ] **B1 · R1 placeholders** — `replace/placeholders.py`, `replace/__init__.py`
  - Blocked by: B0.
  - Do: `replace()` for `Strategy.R1`, using `make_placeholder`; substitution
    from the end of the text to the start; one counter per type; the same
    entity always gets the same surrogate; a passed-in vault is reused.
  - Done when: tests cover adjacent mentions, several mentions of one entity,
    two entities of one type, reuse of a vault across two texts, and a source
    text that already contains square brackets.

- [ ] **B2 · Restore, exact and normalised** — `restore.py`
  - Blocked by: B1.
  - Do: steps 1 and 2 of the `restore()` docstring and the outcomes RESTORED,
    DROPPED, HALLUCINATED_TOKEN, ALTERED_UNRESOLVED.
  - Done when: tests cover an untouched placeholder, changed case, missing
    brackets, spaces for underscores, a placeholder not in the vault, a
    surrogate the reply does not use; no placeholder remains in the output
    without an event reporting it.

- [ ] **B3 · Backends: cache, replay, echo** — `backends/`, `configs/`
  - Blocked by: B0.
  - Do: JSONL cache keyed by `cache_key`; `complete()` as specified; the
    built-in `echo` provider; `configs/models.echo.yaml` and
    `configs/skeleton.yaml` as in `docs/interfaces.md`.
  - Done when: tests with a fake provider show a miss calling the provider
    once and a second identical call served from the cache; replay raises
    `CacheMissError` and the provider is not called; an unpinned role is
    refused; `echo` returns the prompt; no test needs the network.

- [ ] **B4 · Pipeline and CLI** — `pipeline.py`, `cli.py`
  - Blocked by: B1, B2, B3, A2 (D0 behind `detect`), C1 (fixtures).
  - Do: `mask()` and `protect_send_restore()` as in their docstrings; an
    interim resolver that makes one entity per distinct span text (replaced in
    B6); `omissis run` and `omissis batch`.
  - Done when: an integration test with a fake provider runs a fixture email
    end to end; the original values do not appear in the prompt handed to the
    provider (asserted); `omissis run --config configs/skeleton.yaml` works on
    each of the 5 fixture emails of C1 and, run a second time with
    `backend: replay`, gives the same result from the cache.
  - **Human:** read what is sent for the 5 emails and confirm nothing leaks.

## Step 2 · Second detector and pilot · M2 · Sun 15 Nov

- [ ] **B11 · Cloud provider** — `backends/`
  - Blocked by: B3; model `cloud` pinned in `configs/models.yaml`; API key in `.env`.
  - **Human:** approve the provider SDK dependency; create the key with a
    spending cap and pass it privately.
  - Do: one provider for the chosen cloud API, registered with
    `register_provider`, reading the key from the environment; it serves every
    role that uses that API (cloud, attacker, judge, generator).
  - Done when: a test with the SDK call mocked shows the request built from
    `LLMRequest` and the text returned; a missing key gives a clear error;
    one real call, launched by the human, lands in the cache.

- [ ] **B5 · REF-oracle and batch runs** — `pipeline.py`, `cli.py`
  - Blocked by: B4, C1.
  - Do: `mask(..., gold_spans=...)`; batch masking of a folder for a list of
    configurations, written where workstream C's attacks expect it.
  - Done when: masking with gold spans leaves no gold span text in the output
    (asserted on fixtures); the batch output format is agreed with C in the
    pull request.

## Step 3 · Full system · M3 · Thu 19 Nov

- [ ] **B6 · Entity resolver** — `resolve.py`
  - Blocked by: B4.
  - Do: `resolve()` as in its docstring, rules only.
  - Done when: tests cover "Marco Ferri" / "Ferri" / "il Sig. Ferri" merged;
    two people with one surname and different first names kept apart; gender
    from titles, then from the name list, else UNKNOWN; non-person types
    merged on normalised equality.
  - **Human:** provide or approve the first-name list and its source.

- [ ] **B7 · R2 realistic fakes** — `replace/fakes.py`
  - Blocked by: B6; C2 (profile pool, so the fake lists can be disjoint).
  - **Human:** approve the fake-value lists (names, cities, employers) and
    their sources before they are added.
  - Do: `replace()` for `Strategy.R2`: same-gender names, checksum-valid IBANs
    on bank code `00000`, amounts of the same order of magnitude, cities of
    similar size; deterministic for the seed; never a value already in the text.
  - Done when: a test asserts the fake lists and the profile pool do not
    intersect; same seed gives the same fakes; fake IBANs pass A1's validator.

- [ ] **B8 · Fuzzy restore and R2 restore** — `restore.py`
  - Blocked by: B7.
  - Do: step 3 of `restore()`; whole-token matching for R2 surrogates and
    their variants; RESTORED_FUZZY events; the count of restored fakes per reply.
  - Done when: tests cover a near-miss above and below the threshold and a
    fake value that is a substring of another word (not restored).
  - **Human:** read 20 restored replies; set `fuzzy_threshold` on dev and
    record it in `docs/decisions.md`.

## Step 4 · Results · M4–M5 · Sat 21 – Mon 23 Nov

- [ ] **B9 · Reproducibility and README** — `Makefile`, `README.md`
  - Blocked by: C10.
  - Do: `make reproduce` regenerates every figure and table from the cache
    with no network; README with quick start, architecture, results chart,
    limitations (threat model, pseudonymisation is not anonymisation, derived
    values, synthetic data only) and licence; `LICENSE` files.
  - **Human:** confirm the licences (default: MIT for code, CC BY 4.0 for the
    synthetic data).
  - Done when: the command runs with the network disabled.
  - **Human:** clean-clone check on a second machine; tag the freeze.

## Step 5 · Presentation · M6 · Wed 25 Nov

- [ ] **B10 · Slides for the core** — outside the repository or in `docs/slides/`
  - Blocked by: C11.
  - Do: draft content for Giuseppe's part (problem, existing tools, architecture
    and the design choices of the core), every number taken from
    `results/metrics/`.
  - **Human:** write the final slides and rehearse twice with the team.
