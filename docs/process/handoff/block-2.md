# Hand-over note — block 2 · Core completion

> History: this note describes the code as its block left it. Later changes are
> in `docs/decisions.md`, what is left is in `docs/process/TODO.md`.

Owner: Giuseppe · Written by Mattia's agent on 16 Nov 2026, revised on 17 Nov
after the review of the core · For: block 3 (data and evaluation).
Start from `docs/process/handoff/block-1.md`; this note says what changed since.

Block 2 completes the core: the three references that come from the human
annotation, the real cloud model, the entity resolver, the second replacement
strategy and fuzzy restoration. The evaluation can now be built on `mask`,
`protect_send_restore`, `complete` and `load_eval_configs` alone. The app (task
2.7) is not in this pull request: it lists the detectors with
`supported_detectors()`, so it is merged with block 4, and `make demo` still
answers "not built yet". `make test` runs 817 tests.

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

Pinned models (`configs/models.yaml`), on the free tier of GroqCloud except `d2`
and `d3`, which run on this machine:

| Role | Model |
|---|---|
| `cloud`, `attacker`, `judge` | `openai/gpt-oss-120b` |
| `generator` | `qwen/qwen3.8-27b` (a preview model) |
| `d3` | `gpt-oss:20b` served by Ollama on this machine, provider `local`, digest `f38aa0c5…` (since 18 Nov; before, `openai/gpt-oss-20b` on GroqCloud) |
| `d2` | `iiiorg/piiranha-v1-detect-personal-information`, revision `255acde6…` |

Groq publishes no revision of a hosted model: `revision` is the day of the pin,
`"2026-11-16"`. The key is read from the environment variable `GROQ_API_KEY`
(further keys from `GROQ_API_KEY2` to `GROQ_API_KEY9`, and from no other
name); the code never reads `.env`. Every command that calls a model
starts with `uv run --env-file .env`.

**D3 runs on this machine** (provider `local`, `src/omissis/backends/local.py`), so
the original text it reads never goes to a service. To run it: install Ollama,
`ollama pull gpt-oss:20b`, `ollama serve`. The provider posts to
`http://localhost:11434/v1/chat/completions`; `OMISSIS_LOCAL_URL` may name another
port, and an address that is not this machine is refused. A server that is down, or
that has not the model, is a `ConfigError`: D3 and D4 stop instead of going on
without spans. Who has not the model replays D3 from `results/cache/d3.jsonl`.

Measured on 18 Nov on an Apple M5 with 16 GB, on the ten pilot texts: the model
takes 14 GB (82% on the GPU), the first text 168 s with the loading, the others 56 s
on average. Run the D3 pass alone and `ollama stop gpt-oss:20b` before D4 loads
Presidio and the classifier: together they do not fit. Against the hosted D3 of 17
Nov, gold spans not fully covered:

| | direct, of 72 | quasi, of 66 | special, of 4 | spans found | touching no gold |
|---|---|---|---|---|---|
| D3 hosted | 63 | 5 | 0 | 83 | 8 |
| D3 local | 63 | 2 | 1 | 86 | 9 |
| D4, hosted D3 | 1 | 5 | 0 | 143 | 7 |
| D4, local D3 | 1 | 2 | 1 | 147 | 9 |

The two give 70 identical spans of 86 and 83: the numbers of one are not those of the
other.

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
far: `results/cache/cloud.jsonl` holds fourteen exchanges, the eleven of 16 Nov
and three of 18 Nov. The corrections of 17 Nov changed the R2 text of
`fx-bank-01`, `fx-bank-03` and `fx-hr-02`, which Giuseppe sent again with
`configs/gold-r2.yaml`: the ten fixture calls (five with R1, five with R2) are
all answered from the file, and the three R2 replies of 16 Nov stay in it,
no longer read. An empty reply, or one cut at the
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
  amount written twice with its currency ("€ 320,00 €/mese"). A calculation on
  a masked amount is out of reach for the same reason: with R1 the model has
  no number, with R2 it computes on the fake and the result stays wrong.
  Amounts stay masked all the same, because the profiles shown to the attacker
  carry them (`financial`, the monthly instalment). Future work, not built:
  the model writes the operation on the placeholders and the tool computes it
  locally with the real values.
- **The model confuses whose data is whose.** In `fx-hr-02` the HR manager's
  signature carries the employee's role, phone and email; in `fx-bank-02` the
  bank signs with the customer's phone. Restoration is complete by our
  definition and the reply is wrong.
- **The model's own template slots** (`[Nome Cognome]`, `[NUMERO_TELEFONO]`)
  have no number, are not placeholders of ours and are left alone. A slot
  shaped like one of ours and absent from the vault (`[EMAIL_1]` in
  `fx-bank-03` with R1; `[PERSONA_1_M]` in `fx-hr-02` with R2, where the text
  sent holds fakes and placeholders together) is reported as
  `hallucinated_token`.
- **A fake value the reply uses on its own account is restored too.** This
  cannot be told apart, so the full-restoration rate of R2 is an upper bound.
  Names that are also Italian words are kept out of the lists: ten of them
  (Quaranta, Albanesi, Fiorentini, Montanari, Pellegrini, Calderoni, Benedetta,
  Brando, Valentino, Macerata) were replaced on 17 Nov.
- **A fake amount the reply rewrites is read as a number** (18 Nov). On the
  five real R2 replies the model rewrote three of the four amounts it repeated
  ("€ 82,90" for "82,90 euro"; "98 937 euro", with narrow no-break spaces, for
  "98.937 euro"), and two replies with `fully_restored` true showed a fake
  amount. A whole number next to its currency, with the digits and the
  decimals of a fake amount, is now that fake, however its thousands are
  separated (a point, a space of any kind, nothing); and a fake amount never
  has the digits of a number of the text or of the vault, with or without
  decimals, so that two fakes are never one number in two shapes ("€ 98",
  "98,00 euro"). Still not read: an amount without its decimals ("701 euro"
  for "701,00 euro"), a number with no currency next to it, an amount written
  with a point before the decimals ("€ 19.99").
- **Any other fake the reply rewrites is not recognised.** A shortened name of
  a company, a misspelt fake of one word, a date in another format: the fake
  stays in the reply and its entry is `dropped`, with `fully_restored` true. A
  fake of one word has no fuzzy step on purpose: ordinary words are too close
  to it ("Biella", "bella"). The protocol counts the fakes left in the text by
  hand (section 10).
- **A fake that starts with a digit is not restored after a digit and a point
  or a comma**, so that "225,00 euro" is never found at the end of "1.225,00
  euro". A span that starts in the middle of a number (the decimals alone) is
  therefore not restored under R2; a span that stops before the decimals
  ("€ 320" in "€ 320,00") is.
- **The fuzzy step of R2 is strict on short words**: "Srl" for "S.r.l." is
  not close enough word by word, so the fake stays (`dropped`). The
  whole-string comparison of before also restored "Lavorazioni Meccaniche
  Sbrana ha" and deleted the verb.
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
- **A name is read first name first.** Of one name written in both orders
  ("De Luca Rosa", "Rosa De Luca") the entity keeps the one that starts with a
  first name of the lists. A name written only surname first ("Ferri Marco")
  has its parts swapped: under R2 the fake surname alone comes back as "Marco",
  the fake first name as "Ferri". No fixture and no profile is written so.
- **A disclosure reason is dropped** whenever it repeats a word of three
  letters or two digits of any masked value, common words included ("euro"),
  three digits in a row of a masked number ("termina con 3456"), or a value
  without its accent.
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
- Read the ten restored replies (task 2.6); the three R2 calls that the
  corrections had changed were sent again on 18 Nov.
- Decide: whether `DATA_NASCITA` keeps a fake date under R2 or the
  placeholder; whether a caller may pass a `temperature` other than 0
  (`docs/interfaces.md` allows it, `CLAUDE.md` fixes 0).
- Agree with the team that a fake amount is read as a number (section 4):
  Giuseppe decided it on 18 Nov, after the real replies. For amounts, the
  sentence of `docs/evaluation_protocol.md`, section 10, "a fake value that
  the model reformats or abbreviates is neither restored nor flagged" no
  longer holds in full; the rate stays an upper bound for every other fake.
- Whoever has the key under `API_KEY` in a local `.env` renames it to
  `GROQ_API_KEY`: the generic names are no longer read, so that a key of
  another service is never sent to Groq.
- Record in `docs/decisions.md`: the models pinned and the free tier; D3 on a
  hosted model from 16 to 18 Nov and local since then; R2 keeping placeholders for four kinds
  of type and for values without a realistic fake; a label and a number with
  no bracket and no underscore are no longer restored (block 1 restored them
  in upper case); errors of the command line all exit with status 2.
- `docs/interfaces.md` says that block 4 registers the local runtime of D3: the
  provider `local` is registered in `backends`, with `groq`. It does not list the
  choices of task 2.2 (`NONE` with `gold_spans` is an error; `GOLD` with an
  empty list masks nothing; an unknown `--names` and a plain-text input with
  `GOLD` exit with status 2).

## 6. Lines proposed for `docs/cards.md`

- `openai/gpt-oss-120b` — open-weights model by OpenAI (Apache 2.0), served by
  GroqCloud; roles `cloud`, `attacker`, `judge`; pinned 2026-11-16; used
  through the API, temperature 0.
- `gpt-oss:20b` — the same family and licence, in the GGUF build that Ollama
  distributes (digest `f38aa0c5…`), served on this machine; role `d3`. The
  original text that D3 reads does not leave the machine. Until 18 Nov the role
  was on `openai/gpt-oss-20b` at GroqCloud: the 26 replies of that model stay in
  `results/cache/d3.jsonl` and are no longer read.
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
