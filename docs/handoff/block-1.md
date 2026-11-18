# Hand-over note — block 1 · Skeleton

> History: this note describes the code as its block left it. Later changes are
> in `docs/decisions.md`, what is left is in `docs/TODO.md`.

Owner: Mattia · Written with his agent · 16 Nov 2026
For: Giuseppe (block 2), Andrea (block 3), and block 4.

Block 1 is one thin path through the whole tool: D0 rules → interim resolver →
R1 placeholders → cached call to a model → restore. Every stage exists and is
tested, but only in its simplest form. No real model is involved: the
`echo` provider returns the prompt unchanged. `make test` runs 468 tests.

## 1. What exists

| Module | Content | Passes to |
|---|---|---|
| `src/omissis/detect/rules.py` | D0: `find_iban`, `find_cf`, `find_piva`, `find_telefono`, `find_email`, `find_importo`, `find_all`; the validators `iban_is_valid`, `cf_is_valid`, `piva_is_valid` | block 4 |
| `src/omissis/detect/merge.py` | `merge(spans, source_priority)`: longer span, then confidence, then source priority, then input order | block 4 |
| `src/omissis/detect/__init__.py` | `detect` for D0; D1 to D4 raise `NotImplementedError` | block 4 |
| `src/omissis/resolve.py` | interim resolver: one entity per distinct (type, span text), gender unknown | block 2 |
| `src/omissis/replace/` | `replace` and R1 (`placeholders.py`); R2 raises `NotImplementedError` | block 2 |
| `src/omissis/restore.py` | exact and normalised restoration of R1 placeholders; four outcome classes | block 2 |
| `src/omissis/backends/__init__.py` | `LLMRequest`, `LLMResponse`, `cache_key`, `register_provider`, `complete`, the `echo` provider | block 2 |
| `src/omissis/pipeline.py` | `mask`, `protect_send_restore`, `KEEP_PLACEHOLDERS_INSTRUCTION` | block 2 |
| `src/omissis/cli.py` | the `omissis` command: `run`, `batch` | block 2 |
| `src/omissis/eval/datasets.py` | `load_text`, `load_texts`, `load_profiles`, `TextRecord`, `Gold`, `Profile`, `DataError`, `SCENARIOS` | block 3 |
| `data/fixtures/` | five emails with gold spans and gold fields, `profiles.json` with their five profiles | nobody (frozen at G1) |
| `configs/skeleton.yaml`, `configs/models.echo.yaml` | the D0 + R1 + echo run | block 2 |
| `docs/annotation_guide.md` | guide v0 | block 3 |

## 2. How to call it

All examples use the skeleton configuration with the cache moved to the
gitignored scratch folder, as every run that no task asks for must do:

```python
from omissis.config import load_config
cfg = load_config("configs/skeleton.yaml", {"cache_dir": "results/scratch/try"})
text = "Il mio IBAN è IT89Y0000025613651127989360, scrivetemi a lidia.caprioli@example.com."
```

**`detect`** — spans sorted by start, never overlapping.

```python
from omissis.contracts import DetectorId
from omissis.detect import detect
detect(text, DetectorId.D0, cfg)
# [Span(start=14, end=41, text='IT89Y0000025613651127989360', type=IBAN, confidence=1.0, source='D0', reason=None),
#  Span(start=56, end=82, text='lidia.caprioli@example.com', type=EMAIL, confidence=1.0, source='D0', reason=None)]
```

**`mask`** — detect, resolve, replace; no LLM call. Returns the result and the
vault. `result.spans` holds every detected span, `result.entities` only the
masked ones (with `mask_quasi: false` the quasi-identifiers stay visible).

```python
from omissis.pipeline import mask
result, vault = mask(text, cfg)
result.masked_text      # 'Il mio IBAN è [IBAN_1], scrivetemi a [EMAIL_1].'
result.disclosure       # (DisclosureItem(surrogate='[IBAN_1]', type=IBAN, source='D0', reason=None), ...)
len(vault)              # 2; repr(vault) is 'Vault(2 entries)', never the values
```

**`protect_send_restore`** — mask, send to role `cloud`, restore. The vault is
created inside and erased before returning.

```python
from omissis.pipeline import protect_send_restore
r = protect_send_restore(text, "Scrivi una bozza di risposta a questa email.", cfg)
r.run_id            # 'c48f768bcc28'
r.raw_reply         # the echo: the task, a blank line, then the masked text
r.restored_reply    # the same with the IBAN and the email back in place
r.restore_events    # (RestoreEvent('[IBAN_1]', RESTORED, found_as=None), RestoreEvent('[EMAIL_1]', RESTORED, found_as=None))
r.fully_restored    # True
```

**`complete`** — the only way to a model. The second identical call is
answered from `<cache_dir>/cloud.jsonl`.

```python
from omissis.backends import LLMRequest, complete
complete(LLMRequest(role="cloud", prompt="Ciao"), cfg)
# LLMResponse(text='Ciao', model_id='echo', revision='1', cached=False)
complete(LLMRequest(role="cloud", prompt="Ciao"), cfg)
# LLMResponse(text='Ciao', model_id='echo', revision='1', cached=True)
```

With `backend: replay` a miss raises `CacheMissError`; a role that is not
pinned, or a provider that is not registered, raises `ConfigError`. A new
provider is one function `(ModelSpec, LLMRequest) -> str` passed to
`register_provider(name, fn)`; it does no caching.

**`load_texts`** — every `.json` text of a folder, validated; gold spans come
with `confidence=1.0` and `source="GOLD"`.

```python
from omissis.eval.datasets import load_texts, load_profiles
records = load_texts("data/fixtures")       # 5 records; profiles.json is skipped
records[0].id, records[0].scenario          # ('fx-bank-01', 'iban_change')
records[0].spans[0]                         # Span(start=60, end=74, text='Banca Corvalli', type=AZIENDA, confidence=1.0, source='GOLD', ...)
records[0].gold                             # Gold(intent='iban_change', amounts=(320.0,), dates=('2026-12-01', '2026-11-20'), requested_action='update_details', deadline=None)
load_profiles("data/fixtures/profiles.json")  # 5 profiles, ids fx01 to fx05
```

A file that breaks the format raises `DataError` naming the file.

**The two commands.** Both print to standard output only. The output holds
the restored reply, with the original values: never redirect it under
`results/`.

```
uv run omissis run   --config configs/skeleton.yaml --input data/fixtures/fx-bank-01.json
uv run omissis run   --config configs/skeleton.yaml --input data/fixtures/fx-bank-01.json --backend replay
uv run omissis batch --config configs/skeleton.yaml --input-dir data/fixtures
```

`run` prints the run id, the masked text as sent, the raw reply, the restored
reply, the disclosure list, the restoration events and `fully restored`.
`batch` prints one JSON line per text. `--task` changes the instruction,
`--input` also takes a plain text file. Exit code 2 on a configuration, data
or cache error. `configs/skeleton.yaml` writes its cache to the gitignored
`results/scratch/skeleton/` (since task 2.1).

## 3. What is not done

- **Gold spans:** `mask(..., gold_spans=...)` raises `NotImplementedError`;
  `protect_send_restore` has no `gold_spans` argument. The detectors `GOLD`
  and `NONE` and `configs/eval.yaml` do not exist (block 2).
- **Resolver:** interim. "Lidia Caprioli" and "Caprioli" are two entities;
  gender is always unknown, so every person gets `[PERSONA_n]` (block 2).
- **R2** and its restoration; **fuzzy restore** (`fuzzy_threshold` is checked
  and ignored) (block 2).
- **Cloud provider:** only `echo` is registered; `configs/models.yaml` has no
  pinned role (block 2).
- **`omissis mask`**, the app, `make demo` (block 2).
- **D1 to D4**, the dispatch table and `supported_detectors()` (block 4).
- **Everything under evaluation** except the loaders (block 3).
- **Old task ids** (A1, B5, C1, "workstream A") remain in docstrings, error
  messages and the `Makefile`: task 2.1 replaces them in the core, task 4.0 in
  `detect/`.

## 4. Known limits

- **D0 phone numbers are recognised by shape.** Any 6 to 11 digit code
  starting with 0 or 3 is reported as `TELEFONO`. Found in the review, to be
  checked on dev in task 4.4b: a phone read in a date followed by a time or in
  a time range; the second of two phone numbers in a row; decimals after a
  point; IBANs written with hyphens are not found.
- **D0 amounts need a currency** next to the number ("1.200,00" alone is not
  found).
- **An 11-digit landline that passes the partita IVA check is kept as `PIVA`.**
  Both are direct identifiers, so the masking decision does not change.
- **D0 finds no names, cities or organisations**, so with the skeleton
  configuration the sender's name is sent in clear. That is expected for D0.
- **`detect` swallows every exception** of the D0 rules and returns no spans;
  the `CacheMissError` / `ConfigError` exception asked by
  `docs/interfaces.md` comes with task 4.0.
- **Restoration** repairs case, spacing, missing brackets and underscores
  written as spaces. A placeholder whose gender suffix or number was altered
  is reported as `altered_unresolved` and left in place; one that is not in
  the vault as `hallucinated_token`. An upper-case `PERSONA 1` without
  brackets is restored; a lower-case one is not touched, to leave ordinary
  Italian alone.
- **The cache lookup reads the file from the top** on every call: fine for
  thousands of lines, slow beyond.
- **Fixtures (corrected in this task, then frozen):** a generic facility
  followed by a city is tagged as `CITTA` only ("poliambulatorio di
  Pomigliano" → "Pomigliano"); `fx-bank-01` has no deadline.

## 5. Questions the next owner should be able to answer

1. Why does `mask` return both `spans` and `entities`, and when do they
   differ?
2. Two texts share one vault and both name "Banca Corvalli": which placeholder
   does the second text get, and where is that decided?
3. What does `complete` do on a cache miss with `backend: replay`, and why
   does a run and its replay have the same run id?
4. The reply contains `[persona 1]`, `[PERSONA_1_F]` and `[IBAN_7]`, and the
   vault holds only `[PERSONA_1]`: what is the outcome of each?
5. Two spans overlap, same length, same confidence, sources D2 and D0: which
   one survives, and what happens to a source that is not in
   `source_priority`?
