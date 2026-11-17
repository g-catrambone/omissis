# Hand-over note — block 2 · Core completion

Owner: Giuseppe · Written by Mattia's agent on 16 Nov 2026, revised on 17 Nov
after the review of the core · For: block 3 (data and evaluation).
Start from `docs/handoff/block-1.md`; this note says what changed since.

Block 2 completes the core: the three references that come from the human
annotation, the real cloud model, the entity resolver, the second replacement
strategy and fuzzy restoration. The evaluation can now be built on `mask`,
`protect_send_restore`, `complete` and `load_eval_configs` alone. The app (task
2.7) is not in this pull request: it lists the detectors with
`supported_detectors()`, so it is merged with block 4, and `make demo` still
answers "not built yet". `make test` runs 753 tests.

## 1. What exists

| Task | Module | Content |
|---|---|---|
| 2.2 | `config.py` | key `detector` also accepts `GOLD` and `NONE`; `load_eval_configs`; a YAML syntax error is a `ConfigError` |
| 2.2 | `pipeline.py` | `mask` and `protect_send_restore` take `gold_spans`; a D3 reason that quotes a masked value is rewritten or dropped |
| 2.2 | `cli.py` | `run` and `batch` take gold spans from the record with detector `GOLD`; new command `mask` |
| 2.2 | `configs/eval.yaml` | `REF-none`, `REF-oracle-direct`, `REF-oracle` |
| 2.3 | `resolve.py` | the resolver of the specification, with its first-name lists |
| 2.4 | `backends/groq.py` | provider `groq`, registered when `omissis.backends` is imported |
| 2.4 | `backends/__init__.py` | `temperature: 0` always in the params; integral floats normalised; the cache writer repairs a missing final newline |
| 2.5 | `replace/fakes.py`, `replace/data/` | R2 and its lists |
| 2.6 | `restore.py` | fuzzy step, R2 restoration, one outcome per vault entry |
| 2.6 | `configs/gold-r1.yaml`, `configs/gold-r2.yaml` | gold spans with R1 and with R2, on the real model |
| 2.7 | `configs/app.yaml` | the defaults of the Gradio page; `app.py` and `make demo` come with block 4 |

Pinned models (`configs/models.yaml`), all on the free tier of GroqCloud except
`d2`:

| Role | Model |
|---|---|
| `cloud`, `attacker`, `judge` | `openai/gpt-oss-120b` |
| `generator` | `qwen/qwen3.8-27b` (a preview model) |
| `d3` | `openai/gpt-oss-20b` |
| `d2` | `iiiorg/piiranha-v1-detect-personal-information`, revision `255acde6…` |

Groq publishes no revision of a hosted model: `revision` is the day of the pin,
`"2026-11-16"`. The key is read from the environment variable `GROQ_API_KEY`
(further keys from `GROQ_API_KEY2` to `GROQ_API_KEY9`, and from no other
name); the code never reads `.env`. Every command that calls a model
starts with `uv run --env-file .env`.

## 2. How to call it

**`load_eval_configs`** — the named configurations, in file order. Pass
`{"backend": "replay"}` to forbid the network.

```python
from omissis.config import load_eval_configs, run_id
configs = load_eval_configs("configs/eval.yaml", {"backend": "replay"})
{name: (c.detector, c.mask_quasi, run_id(c)) for name, c in configs.items()}
# {'REF-none': ('NONE', False, '0c014883cf98'),
#  'REF-oracle-direct': ('GOLD', False, '84e17a5e7ba0'),
#  'REF-oracle': ('GOLD', True, 'ea61d1c68a82')}
```

**`mask` with gold spans** — pass the spans of the record when, and only when,
the detector is `GOLD`. Each call without a `vault` starts from an empty one.

```python
from omissis.eval.datasets import load_text
from omissis.pipeline import mask
record = load_text("data/fixtures/fx-hr-01.json")

result, vault = mask(record.text, configs["REF-oracle"], record.spans)         # mask_quasi: true
# "sono [PERSONA_1_M], [RUOLO_1] del turno di notte nello stabilimento di [CITTA_1],
#  matricola [UTENTE_1]. ... da lunedì [DATA_1] ... un'[SALUTE_1] ..."
# 12 spans, 11 entities, 11 vault entries

result, vault = mask(record.text, configs["REF-oracle-direct"], record.spans)  # mask_quasi: false
# "sono [PERSONA_1_M], magazziniere del turno di notte nello stabilimento di Nola,
#  matricola [UTENTE_1]. ... da lunedì 16 novembre 2026 ... un'[SALUTE_1] ..."
# 12 spans, 6 entities: direct identifiers and special categories only

result, vault = mask(record.text, configs["REF-none"])                         # no gold_spans
# the text unchanged; no spans, no entities, an empty vault
```

`result.spans` holds every gold span; `result.entities` and
`result.disclosure` only what was masked. `GOLD` without `gold_spans`, or any
other detector with `gold_spans`, raises `ValueError`.

**`protect_send_restore` with gold spans** — the same rules. This call was made
once on the real model, on 16 Nov, and is now answered from `results/cache/`:

```python
from omissis.config import load_config
from omissis.pipeline import protect_send_restore
config = load_config("configs/gold-r1.yaml", {"backend": "replay"})
r = protect_send_restore(record.text, "Scrivi una bozza di risposta a questa email.", config, record.spans)
r.run_id            # 'ea61d1c68a82', the run id of REF-oracle
r.raw_reply         # "... Gentile [PERSONA_1_M], la ringrazio per averci comunicato ..."
r.restored_reply    # "... Gentile Davide Sorrentino, la ringrazio per averci comunicato ..."
r.restore_events    # [PERSONA_1_M] restored, [RUOLO_1] dropped, [CITTA_1] dropped, ...
r.fully_restored    # True
```

`dropped` means the reply did not use the surrogate: it is not a failure.
`fully_restored` is false only on `altered_unresolved` or `hallucinated_token`.
The request carries `max_tokens: 2048` (`pipeline.MAX_TOKENS`), which is part of
the cache key.

**`complete` on a pinned role** — one function for every role; the role picks
the model. `temperature: 0` is added to the params.

```python
from omissis.backends import LLMRequest, complete
for role in ("cloud", "attacker", "judge", "generator", "d3"):
    complete(LLMRequest(role, "Rispondi con una parola: di che colore è il cielo?"), config)
# with backend cloud: LLMResponse(text=..., model_id='openai/gpt-oss-120b', revision='2026-11-16', cached=False)
# with backend replay and nothing cached: CacheMissError
```

Each role writes `<cache_dir>/<role>.jsonl`. Only `cloud` has been called so
far: `results/cache/cloud.jsonl` holds the eleven exchanges of 16 Nov. Seven of
the ten fixture calls are still answered from it (the five with R1, and
`fx-bank-02` and `fx-hr-01` with R2); the corrections of 17 Nov changed the R2
text of `fx-bank-01`, `fx-bank-03` and `fx-hr-02`, which a human sends again
with `configs/gold-r2.yaml` (three calls). An empty reply, or one cut at the
token limit, raises `RuntimeError` and is not cached; a missing key raises
`ConfigError`. On a rate limit the provider tries the next key; when every key
is refused it waits for the shortest time one of them asks and tries again, up
to five times, then raises `RuntimeError("Groq API answered HTTP 429")`. A wait
longer than two minutes is a daily limit: the provider stops at once and says
so. The command line prints the error on one line and exits with status 2; the
calls already answered are in the cache.

**`omissis mask`** — the masked-batch files, no call to the role `cloud`:

```
uv run omissis mask --eval-config configs/eval.yaml --input-dir data/fixtures --output results/scratch/fixtures/masked
# REF-none: 5 texts written to results/scratch/fixtures/masked/REF-none
# REF-oracle-direct: 5 texts written to ...
# REF-oracle: 5 texts written to ...
```

`--names A,B` limits the configurations; an unknown name exits with status 2
and writes nothing. The masked text of each file equals
`protect_send_restore(...).masked_text` for the same record and configuration
(asserted in `tests/core/test_references.py`).

## 3. What block 3 must know

- **The free tier is the bottleneck.** Each Groq model allows 200,000 tokens
  and 1,000 requests a day, 8,000 tokens a minute. `cloud`, `attacker` and
  `judge` share one model, hence one allowance. A fixture reply costs about
  1,500 tokens. Count the calls before every run and spread the evaluation
  over days, or move the judge to `qwen/qwen3.8-27b` before any judged result
  exists (a re-pin changes every run id).
- **Every call is cached**, so a run stopped by the daily limit resumes from
  where it stopped at no cost.
- **Keep the profile pool disjoint from `src/omissis/replace/data/`** (first
  names, surnames, towns, employers, banks, streets). The lists must not
  change after gate G2.
- **R2 keeps the R1 placeholder** for RUOLO, STRUTTURA, NAZIONALITA and every
  special category (`fakes.NO_FAKE`), and for any value that has no realistic
  fake: a date that is not written as `16 novembre 2026`, `16 novembre`,
  `16/11/2026` or `2026-11-16` (so `a dicembre`, `2019`, `1° dicembre`, `16
  nov. 2026`, a date with an hour), an age or an amount without a number, a
  value for which no free fake is left. An R2 vault holds fakes and placeholders together, and
  `restore` handles both. R2 never raises for lack of a fake.
- **Restored fakes per reply** (protocol, section 10) is the number of
  `restored` and `restored_fuzzy` events of an R2 run whose surrogate is not a
  placeholder (`parse_placeholder(e.surrogate) is None`). It counts vault
  entries, not occurrences.
- **Entity ids restart in every text.** Across texts that share a vault, the
  same entity is the same type and the same canonical value and, for a person
  under R1, the same gender. R2 is meant for one vault per text, as `mask` and
  `protect_send_restore` use it: a fake reused in a later text of the same
  vault is not checked against that text.
- **A text that is not a record** (`omissis run --input lettera.txt`) is
  refused when the configuration writes to a cache under `results/` outside
  `results/scratch/`: the cache keeps the prompt that is sent.
  `configs/example.yaml` and `configs/skeleton.yaml` write to
  `results/scratch/`.
- **An input folder that is missing or holds no record** makes `batch` and
  `mask` exit with status 2.

## 4. Known limits

- **Derived values.** On the ten real calls the model computed or invented
  values from the surrogates, and restoration cannot undo them: with R2 the
  postcode and province of the fake town ("13012 Bergamo (VC)" after
  restoration) and an email address built on the fake bank's name; with R1 an
  amount written twice with its currency ("€ 320,00 €/mese").
- **The model confuses whose data is whose.** In `fx-hr-02` the HR manager's
  signature carries the employee's role, phone and email; in `fx-bank-02` the
  bank signs with the customer's phone. Restoration is complete by our
  definition and the reply is wrong.
- **The model's own template slots** (`[Nome Cognome]`, `[NUMERO_TELEFONO]`)
  have no number, are not placeholders of ours and are left alone. A slot
  shaped like one of ours and absent from the vault (`[EMAIL_1]` in
  `fx-bank-03`) is reported as `hallucinated_token`.
- **A fake value the reply uses on its own account is restored too.** This
  cannot be told apart, so the full-restoration rate of R2 is an upper bound.
  Names that are also Italian words are kept out of the lists: ten of them
  (Quaranta, Albanesi, Fiorentini, Montanari, Pellegrini, Calderoni, Benedetta,
  Brando, Valentino, Macerata) were replaced on 17 Nov.
- **A fake the reply rewrites is not recognised.** Another format ("701 euro"
  for "701,00 euro"), a shortened name of a company, a misspelt fake of one
  word: the fake stays in the reply and its entry is `dropped`, with
  `fully_restored` true. A fake of one word has no fuzzy step on purpose:
  ordinary words are too close to it ("Biella", "bella"). The protocol counts
  the fakes left in the text by hand (section 10).
- **A fake that starts with a digit is not restored after a digit and a point
  or a comma**, so that "225,00 euro" is never found at the end of "1.225,00
  euro". A span that starts in the middle of a number (the decimals alone) is
  therefore not restored under R2; a span that stops before the decimals
  ("€ 320" in "€ 320,00") is.
- **The fuzzy step of R2 is strict on short words**: "869,00 EUR" for the
  fake "869,00 euro", or "Srl" for "S.r.l.", is not close enough word by word,
  so the fake stays (`dropped`). The whole-string comparison of before also
  restored "Lavorazioni Meccaniche Sbrana ha" and deleted the verb.
- **A suffix added to a placeholder without a gender** (`[IBAN_1_X]`,
  `[PERSONA_1_X]` when the vault holds `[PERSONA_1]`) is read as the
  placeholder followed by `_X]`: the value is restored and the tail stays. With
  a gender in the vault the token stays and is `altered_unresolved`. Same as in
  block 1; no real reply has shown it.
- **A placeholder is read only when it is written as one**: with an
  underscore, between two brackets, or with its three parts in upper case
  (`PERSONA 1 F`). `PERSONA 1` or `IBAN 1` with no bracket and no underscore
  are ordinary text and stay as they are, with no event: "DOCUMENTO 1" in a
  list of attachments must never receive a document number.
- **Fake phone numbers** are random digits after `+39` and the first digit (0
  or 3): one could be a real number.
- **A fake date of birth keeps the month and the year**, like any date: under
  R2 the year of birth is readable. Decision open (section 5).
- **The resolver** gives a bare surname shared by two people to the first one
  it is compatible with. A name of one word gets a fake surname under R2, even
  when it is a first name. Gender follows the title before the first name, as
  the specification says: "Prof. Maria Rossi" is read as M.
- **A disclosure reason is dropped** whenever it repeats a word of three
  letters or two digits of any masked value, common words included ("euro").
- **With `mask_quasi: false`** a direct identifier that a longer
  quasi-identifier span absorbed in `merge` stays visible. No evaluated
  configuration meets it; the rule is in `detect/merge.py` (block 4).
- **Two people kept apart only by the gender of a title** ("Sig. Ferri",
  "Sig.ra Ferri") get two placeholders under R1 and one shared fake under R2.
- **The cities of R2 are not matched by size**: the size of the original is
  not known.
- **The app**, when it is merged, replays only what is in `results/cache/`
  for its own configuration (`configs/app.yaml`: D0, R1, `mask_quasi: true`).
  Nothing is recorded for it yet: task P.1 records the demo runs.

## 5. Open points for the humans

- Approve the first-name lists of `resolve.py` and the fake lists of
  `replace/data/` (written for this project, no external source), with the ten
  replacements of 17 Nov. They are frozen at gate G2.
- Send `fx-bank-01`, `fx-bank-03` and `fx-hr-02` again with
  `configs/gold-r2.yaml`, and read the ten restored replies (task 2.6).
- Decide: whether `DATA_NASCITA` keeps a fake date under R2 or the
  placeholder; whether a caller may pass a `temperature` other than 0
  (`docs/interfaces.md` allows it, `CLAUDE.md` fixes 0).
- Whoever has the key under `API_KEY` in a local `.env` renames it to
  `GROQ_API_KEY`: the generic names are no longer read, so that a key of
  another service is never sent to Groq.
- Record in `docs/decisions.md`: the models pinned and the free tier; D3 on a
  hosted model instead of a local one; R2 keeping placeholders for four kinds
  of type and for values without a realistic fake; a label and a number with
  no bracket and no underscore are no longer restored (block 1 restored them
  in upper case); errors of the command line all exit with status 2.
- `docs/interfaces.md` still describes D3 as local and does not list the
  choices of task 2.2 (`NONE` with `gold_spans` is an error; `GOLD` with an
  empty list masks nothing; an unknown `--names` and a plain-text input with
  `GOLD` exit with status 2).

## 6. Lines proposed for `docs/cards.md`

- `openai/gpt-oss-120b` — open-weights model by OpenAI (Apache 2.0), served by
  GroqCloud; roles `cloud`, `attacker`, `judge`; pinned 2026-11-16; used
  through the API, temperature 0.
- `openai/gpt-oss-20b` — same family and licence, served by GroqCloud; role
  `d3`; the text is sent unmasked to the service for detection.
- `qwen/qwen3.8-27b` — preview model served by GroqCloud; role `generator`;
  licence to be confirmed on the model card.

## 7. Questions the next owner should be able to answer

1. Which of the three references needs `gold_spans`, and what happens if the
   evaluation passes them to `REF-none`?
2. Why do `REF-oracle` and `configs/gold-r1.yaml` have the same run id, and
   what would change it?
3. A run stops at the daily token limit after 60 of 100 texts: what do you do,
   and what does it cost?
4. Under R2 the reply contains the fake surname alone: what is written back,
   and where is that pairing stored?
5. Which events make `fully_restored` false, and why is `dropped` not one of
   them?
