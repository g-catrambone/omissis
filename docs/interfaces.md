# Interface specification

How the parts of the project connect. This document is the contract: the code in
`src/omissis/contracts.py` and the boundary functions must match it exactly.
A change of behaviour changes this document in the same commit and gets a row
in `docs/decisions.md` (CLAUDE.md, rule 5).

Sections: 1 data contracts · 2 placeholder grammar · 3 boundary functions ·
4 configuration · 5 file formats · 6 who calls what.

## 1. Data contracts — `src/omissis/contracts.py`

Plain data and validation only. All dataclasses are frozen. All enums are
`StrEnum`.

### Enums

| Enum | Values |
|---|---|
| `SpanClass` | `DIRECT="direct"`, `QUASI="quasi"`, `SPECIAL="special"` |
| `SpanType` | direct: `PERSONA IBAN CF PIVA TELEFONO EMAIL INDIRIZZO DOCUMENTO CONTO DATA_NASCITA UTENTE` · quasi: `AZIENDA RUOLO CITTA STRUTTURA IMPORTO DATA ETA NAZIONALITA` · special: `SALUTE RELIGIONE POLITICA SINDACATO ORIENTAMENTO ETNIA BIOMETRICO GIUDIZIARIO` |
| `Gender` | `M`, `F`, `UNKNOWN` |
| `DetectorId` | `D0`, `D1`, `D2`, `D3`, `D4` |
| `Strategy` | `R1`, `R2` |
| `RestoreOutcome` | `restored`, `restored_fuzzy`, `dropped`, `altered_unresolved`, `hallucinated_token`, `wrong_mapping` |

`SpanType` values are the ASCII labels used inside placeholders (no accents:
`CITTA`, `ETA`, `NAZIONALITA`). `TYPE_CLASS: dict[SpanType, SpanClass]` is the
single place that maps each type to its class. `GOLD_SOURCE = "GOLD"` is the
`source` of human-annotated spans.

### Dataclasses

| Type | Fields | Validation and notes |
|---|---|---|
| `Span` | `start:int`, `end:int`, `text:str`, `type:SpanType`, `confidence:float`, `source:str`, `reason:str\|None=None` | `0 <= start < end`; `len(text) == end-start`; `0 <= confidence <= 1`; `source` is a `DetectorId` value or `GOLD_SOURCE`; when `source` is `"D3"`, `reason` is non-empty. Offsets are character offsets, `end` exclusive. Property `cls` = `TYPE_CLASS[type]` (derived, never stored). Method `matches(source_text)` is true when `source_text[start:end] == text`. |
| `Entity` | `entity_id:str`, `type:SpanType`, `canonical:str`, `mentions:tuple[Span,...]`, `gender:Gender=UNKNOWN` | At least one mention; all mentions have the entity's type. `entity_id` is `<TYPE>_<n>` with `n >= 1` and no leading zeros, numbered per type by first appearance. Property `cls`. |
| `VaultEntry` | `surrogate:str`, `original:str`, `type:SpanType`, `entity_id:str`, `original_variants:tuple[str,...]=()`, `surrogate_variants:tuple[str,...]=()` | `repr` never shows `original` or the variants. `surrogate` is the placeholder (R1, and under R2 a value without a fake) or the fake value (R2). `surrogate_variants` is for R2 (for example the fake surname alone). |
| `RestoreEvent` | `surrogate:str`, `outcome:RestoreOutcome`, `found_as:str\|None=None` | One restoration decision. |
| `DisclosureItem` | `surrogate:str`, `type:SpanType`, `source:str`, `reason:str\|None=None` | One line of the disclosure panel. Never contains the original value. Property `cls`. |
| `MaskResult` | `masked_text:str`, `spans:tuple[Span,...]`, `entities:tuple[Entity,...]`, `disclosure:tuple[DisclosureItem,...]` | Output of `mask`. |
| `PipelineResult` | `run_id:str`, `masked_text:str`, `raw_reply:str`, `restored_reply:str`, `disclosure:tuple[DisclosureItem,...]`, `restore_events:tuple[RestoreEvent,...]` | Property `fully_restored`: no event is `altered_unresolved` or `hallucinated_token`. |

`wrong_mapping` is never produced by `restore`; only evaluation against gold
assigns it.

### Vault — `src/omissis/vault.py`

`Vault` holds `VaultEntry` objects in memory, keyed by surrogate:
`add(entry)` (raises `ValueError` if the surrogate exists), `get(surrogate) ->
VaultEntry | None`, `surrogate_for(entity_id) -> str | None`, `clear()`,
iteration, `len`, `in`. `repr` and `str` show the number of entries only.
No persistence, no encryption.

## 2. Placeholder grammar (R1)

- Form: `[TYPE_n]`, or `[PERSONA_n_M]` / `[PERSONA_n_F]` when gender is known.
  ASCII only. `n` starts at 1, one counter per type per session.
- Gender suffix only for `PERSONA`; unknown gender gives `[PERSONA_n]`.
- Regular expression: `\[([A-Z]+(?:_[A-Z]+)*)_(\d+)(?:_([MF]))?\]`
  (`PLACEHOLDER_RE`).
- `make_placeholder(type, n, gender=UNKNOWN) -> str`; raises `ValueError` for
  `n < 1` or for a known gender on a non-person type.
- `parse_placeholder(token) -> (SpanType, int, Gender) | None`; `None` for an
  unknown type, a malformed token, a number with leading zeros (`[IBAN_01]`),
  or a gender suffix on a non-person type.

## 3. Boundary functions

Signatures are fixed, including parameter names.

| Function | Module |
|---|---|
| `detect(text: str, detector: DetectorId, config: RunConfig) -> list[Span]` | `omissis.detect` |
| `supported_detectors() -> tuple[DetectorId, ...]` | `omissis.detect` |
| `resolve(spans: Sequence[Span], text: str) -> list[Entity]` | `omissis.resolve` |
| `replace(text: str, entities: Sequence[Entity], strategy: Strategy, seed: int, vault: Vault \| None = None) -> tuple[str, Vault]` | `omissis.replace` |
| `restore(reply: str, vault: Vault, fuzzy_threshold: float) -> tuple[str, list[RestoreEvent]]` | `omissis.restore` |
| `complete(request: LLMRequest, config: RunConfig) -> LLMResponse` | `omissis.backends` |
| `register_provider(name: str, fn: ProviderFn) -> None` | `omissis.backends` |
| `mask(text: str, config: RunConfig, gold_spans: Sequence[Span] \| None = None, vault: Vault \| None = None) -> tuple[MaskResult, Vault]` | `omissis.pipeline` |
| `protect_send_restore(text: str, task: str, config: RunConfig, gold_spans: Sequence[Span] \| None = None) -> PipelineResult` | `omissis.pipeline` |

### Behaviour

**`detect`** — Returns spans sorted by `start`, non-overlapping. Overlaps are
resolved inside: longer span wins, then higher confidence, then earlier
position in `config.source_priority`. The winner is never cut; of a span that
overlaps it only in part, the stretch outside the winner is returned as a
shorter span of the same type and source, so that nothing a detector found
goes back to clear text. A longer quasi-identifier span can therefore absorb a
direct identifier inside it: the stretch is still masked when
`config.mask_quasi` is true, under the longer span's type. With `mask_quasi`
false the absorbed identifier stays visible: a declared limit, which no
evaluated configuration meets. Every span satisfies `span.matches(text)`.
Quasi-identifier spans are returned even when `config.mask_quasi` is false:
the caller decides whether to mask them. Never raises on bad input: a text
that is not a string gives no spans. A detector that fails stops the run,
because returning no spans would send the text unmasked: a `RuntimeError` (a
cache miss in replay, a provider or a model that fails) and a `ConfigError` (a
model that is not pinned, a library or a weights file missing on this machine)
propagate, and any other error is raised as a `RuntimeError` that names the
detector and the error type only. The same holds inside D4: with one
sub-detector missing it is not D4. One failure does not stop the run: two
replies of D3 that are not valid JSON are logged and counted, and D3 returns
no spans for that text. A detector not built yet raises `NotImplementedError`
with a clear message.

**`supported_detectors`** — Lists the detectors that can run on this machine:
built, and with their libraries installed. It is an import check only: no
model is loaded and none is called. Callers use it instead of probing
`detect`.

**`resolve`** — Every input span ends up in exactly one entity. Person
mentions merge when one contains the other's surname or is its first name
alone; a surname includes its particles (`De Luca`) and a title written inside
the span is ignored. They stay separate when both carry first names and these
differ, or when titles or first names give them different genders; the same
name words are one person, in any order, and the entity keeps the order that
starts with a first name of the lists. Mentions with a first name are grouped
first; a surname or a first name alone then joins the first person it is
compatible with. Other types merge on normalised equality (case and
whitespace). Gender from titles first (Sig./Sig.ra, Dott./Dott.ssa), then from
a first-name list, otherwise `UNKNOWN`. Rules only; the same function serves
every detector.

**`replace`** — R1 writes `make_placeholder` tokens. R2 writes realistic fake
values, deterministic for `seed` and never already present in `text` or in the
vault: people, employers, banks, towns and streets come from lists disjoint
from the profile pool; identifiers, phone numbers, amounts, dates and ages are
generated with the shape of the original. A value that has no realistic fake
keeps its R1 placeholder: the types `RUOLO`, `STRUTTURA`, `NAZIONALITA`,
`DATA_NASCITA` (a fake would keep the year, and with it the age) and the
special categories, a date that is not written with its day, an age or an
amount without a number, a value for which no free fake is left. An R2 vault
therefore holds fakes and placeholders together. A fake amount never has a
number that the text or the vault already holds, whatever the currency and the
separators around it. R2 is meant for one vault per text. The same entity
always gets the same surrogate; a passed-in vault is reused so surrogates stay
consistent across texts of one session (across texts the same entity means the
same type and the same canonical value after normalisation and, for a person
under R1, the same gender; entity ids restart in every text). Substitution
runs from the end of the text to the start.

**`restore`** — Order: exact match; normalised match (case, an accent on the
label, missing brackets, white space, hyphens or dashes for underscores,
Markdown escapes); fuzzy match accepted only at or above `fuzzy_threshold`:
for R1 a bracketed token with the same digits, close to exactly one
placeholder; for R2 a run of as many words as a fake of two or more words,
each word close to the word in the same place and every number identical.
Never guesses. A token counts as a placeholder only when it is written as one:
with an underscore, between two brackets, or with its three parts in upper
case (`PERSONA 1 F`); a label and a number with none of these are ordinary
text. A field between brackets with no number (`[Nome Cognome]`,
`[DATA_RICEVUTA]`) is the model's own text: it is left alone and gives no
event. A placeholder-shaped token absent from the vault gives
`hallucinated_token`; a token that looks like a surrogate but has no safe
match stays in place and gives `altered_unresolved`; a surrogate the reply
does not use gives `dropped`. R2 surrogates match on whole tokens only. A fake
amount is read as a number first: a whole number next to its currency (`€`,
`euro`, `EUR`, before or after), with the digits and the decimals of a fake
amount, is that fake, however its thousands are separated (a point, a space of
any kind, nothing); never a number that an original of the vault also holds or
that two fakes share, with or without decimals. Any other fake that the reply
reformats or shortens is not recognised and its entry is `dropped`: a declared
limit. Returns the restored text and one event per vault entry or suspicious
token.

**`complete`** — Looks the request up in `config.cache_dir` by `cache_key`.
Hit: returns the stored response with `cached=True`. Miss with
`config.backend == "cloud"`: calls the provider registered for the model,
appends the exchange to the cache, returns it. Miss with `"replay"`: raises
`CacheMissError` (a subclass of `RuntimeError`), never touches the network.
Refuses a role whose model is not pinned. Every LLM call in the project goes
through this function, including D3, the attacker, the judge and the text
generator.

**`register_provider`** — `ProviderFn = Callable[[ModelSpec, LLMRequest], str]`.
A provider turns one request into text and does no caching. `backends`
registers `groq` (the hosted models) and `local` (a model served on this
machine, which D3 uses: the text it reads is not pseudonymised yet and never
leaves the machine). Registering a name twice raises `ValueError`. A provider that cannot run on this machine (key,
library or weights missing) raises `ConfigError`.

**Built-in provider `echo`** — registered by `backends` itself. It returns
`request.prompt` unchanged and needs no network, key or model. It exists so
the whole pipeline can run before any real model is chosen: a models file
that sets a role to `provider: echo`, `id: echo`, `revision: "1"` counts as
pinned. `configs/models.echo.yaml` pins every role this way and
`configs/skeleton.yaml` is a run configuration that uses it (D0, R1,
`backend: cloud`). `echo` is for the skeleton, tests and debugging only; no
reported number may come from it.

**`mask`** — detect → resolve → replace. It never calls the role `cloud`; with
D3 or D4 the detector calls the role `d3` through `complete`. What it masks
depends on `config.detector` (section 4):

- `D0`–`D4`: the spans come from `detect`; passing `gold_spans` is an error.
- `GOLD`: the spans are `gold_spans`, which is then required (the references
  `REF-oracle` and `REF-oracle-direct`).
- `NONE`: nothing is masked; the text is returned unchanged with no spans, no
  entities and an empty vault (the reference `REF-none`).

Quasi-identifier spans are masked only when `config.mask_quasi` is true;
direct and special-category spans always. A wrong combination of detector and
`gold_spans` raises `ValueError`.

`MaskResult.spans` holds every span found (every gold span with `GOLD`);
`entities` and `disclosure` hold only what was masked, one disclosure item per
entity. Without a `vault` argument each call starts from an empty vault: the
evaluation and `omissis mask` do so for every text, and the masked text is then
identical to the one `protect_send_restore` sends.

**`protect_send_restore`** — Masks `text` exactly as `mask` does, with the
same rules for `config.detector` and `gold_spans`, sends the prompt
`f"{task}\n\n{masked_text}"` to the role `cloud` with
`KEEP_PLACEHOLDERS_INSTRUCTION` as system message, restores the reply. `task` is the user's instruction in Italian. The
vault is created for the call and erased before returning. With detector
`NONE` the text is sent as it is and restoration finds nothing to do, so every
configuration, references included, runs through this one function.
`KEEP_PLACEHOLDERS_INSTRUCTION` is defined once, in `pipeline.py`:

> Il testo contiene segnaposto tra parentesi quadre, come [PERSONA_1_M] o
> [IBAN_1]. Copiali esattamente come sono, senza modificarli, tradurli o
> spiegarli.

### LLM request types — `src/omissis/backends`

| Type | Fields |
|---|---|
| `LLMRequest` | `role:str` (a key of `configs/models.yaml`), `prompt:str`, `system:str\|None=None`, `params:Mapping[str,Any]={"temperature": 0}` |
| `LLMResponse` | `text:str`, `model_id:str`, `revision:str`, `cached:bool` |

`cache_key(model: ModelSpec, request: LLMRequest) -> str` is the SHA-256 hex
digest of the JSON (sorted keys, `ensure_ascii=False`) of
`{id, revision, system, prompt, params}`. `temperature: 0` is always part of
`params`, and no call of the project passes another value. Integral floats in
`params` are written as integers first, so `0` and `0.0` give one key.

## 4. Configuration — `src/omissis/config.py`

One YAML file defines one run. Every key is required; a missing or unknown key
is an error.

| Key | Type | Meaning |
|---|---|---|
| `detector` | `D0`–`D4`, `GOLD`, `NONE` | where the spans come from: a detector, the human annotation, or nothing (no masking) |
| `strategy` | `R1` \| `R2` | replacement strategy |
| `mask_quasi` | bool | mask quasi-identifiers (true in every evaluated configuration that has a detector) |
| `backend` | `cloud` \| `replay` | where cache misses go |
| `seed` | int | seed for fakes and resampling |
| `fuzzy_threshold` | float in [0,1] | acceptance threshold of fuzzy restore |
| `source_priority` | list of detector ids | tie-break for overlapping spans |
| `models_file` | path | normally `configs/models.yaml` |
| `cache_dir` | path | normally `results/cache` |

API: `RunConfig` (frozen dataclass with these fields), `load_config(path,
overrides=None) -> RunConfig`, `with_overrides(config, **changes)`,
`run_id(config) -> str`, `ConfigError(ValueError)`.

`GOLD` and `NONE` are values of the configuration key only: they are not
members of `DetectorId`, and `detect` is never called with them. `strategy`
and `mask_quasi` are still required when the detector is `NONE`, and must be
`R1` and `false` (validated), so that `REF-none` has a single run id.

`run_id` identifies what a run computes, not where its responses come from:
the first 12 hex characters of the SHA-256 of the sorted JSON of `detector`,
`strategy`, `mask_quasi`, `seed`, `fuzzy_threshold`, `source_priority` and the
resolved content of the models file (`provider`, `id`, `revision` for each
role). `backend`, `cache_dir` and the `models_file` path are excluded, so a
run and its replay from the cache share one run id. Since every role enters
the hash, pinning any model changes the run id of every configuration: what
was written before the last pin is regenerated (the LLM calls come from the
cache).

**Named configurations — `configs/eval.yaml`.** The evaluation and
`omissis mask` read the configurations to run from this file:

```yaml
base:                      # keys shared by every configuration
  backend: cloud
  seed: 20261111
  fuzzy_threshold: 0.9
  source_priority: [D0, D2, D1, D3]
  models_file: configs/models.yaml
  cache_dir: results/cache
configurations:
  - {name: REF-none,          detector: NONE, strategy: R1, mask_quasi: false}
  - {name: REF-oracle-direct, detector: GOLD, strategy: R1, mask_quasi: false}
  - {name: REF-oracle,        detector: GOLD, strategy: R1, mask_quasi: true}
  - {name: D1+R1,             detector: D1,   strategy: R1, mask_quasi: true}
  - {name: D2+R1,             detector: D2,   strategy: R1, mask_quasi: true}
  - {name: D4+R1,             detector: D4,   strategy: R1, mask_quasi: true}
  - {name: D4+R2,             detector: D4,   strategy: R2, mask_quasi: true}
```

`load_eval_configs(path, overrides=None) -> dict[str, RunConfig]` (in
`config.py`) merges `base` into each entry, then applies `overrides` over both
(this is how a caller forces `backend: replay`), and returns the
configurations by name, in file order. Names are unique; an unknown key is an
error. `base.fuzzy_threshold` changes only with a row in `docs/decisions.md`.

**Command line — `omissis`** (run through `uv run`):

```
omissis run   --config <run config .yaml> --input <text record .json or text file> [--task "<instruction>"] [--backend cloud|replay]
omissis batch --config <run config .yaml> --input-dir <dir of text records> [--task "<instruction>"] [--backend cloud|replay]
omissis mask  --eval-config configs/eval.yaml [--names A,B,...] --input-dir <dir of text records> --output results/<split>/masked [--backend cloud|replay]
```

`run` prints the masked text, the raw and the restored reply, the disclosure
report and the restoration events. `batch` prints one JSON line per record
with the whole result. Both outputs contain the restored reply, which holds
the original values: they go to standard output only and are never saved
under `results/`. With detector `GOLD` both take the gold spans from the JSON
record, so the input must be a text record. `mask` never calls the
role `cloud`: it masks every record, each with a fresh vault, under each named
configuration (all of them when `--names` is omitted) and writes the
masked-batch format of section 5. It is for synthetic texts only (the
evaluation texts and the fixtures). Every command exits with status 2 and a
one-line message on any error: a `ConfigError`, a `DataError`, a
`CacheMissError`, a detector that fails or is not built yet, a provider that
fails after its retries, a cache line that is not a record, an input folder
that is missing or holds no text record.

`configs/models.yaml` has one entry per role — `cloud`, `attacker`, `judge`,
`generator`, `d3`, `d2` — each with `provider`, `id`, `revision`, all
non-empty strings (quote a numeric revision: `revision: "1"`). The literal
`TO_BE_PINNED` marks an undecided value. API: `ModelSpec(role, provider, id,
revision)` with property `pinned`; `load_models(path) -> dict[str, ModelSpec]`;
`require_pinned(models, role) -> ModelSpec` raising `ConfigError` when unpinned.

## 5. File formats

All JSON is UTF-8 with `ensure_ascii=False`. No serialised `Vault` or
`VaultEntry` is ever written under `results/`. The evaluation texts are
synthetic, so the cache, the rating sheets and the outcomes of the evaluation
hold their original values by design. A text a user gives to `omissis run`,
`omissis batch` or the app is written nowhere except the LLM cache of the
configuration in use (`cache_dir`): the prompt that was sent, which is the
masked text with whatever the detector missed in clear, and, with D3 or D4,
the detector's own prompt, which is the whole text. Such a run uses a
`cache_dir` under the gitignored `results/scratch/`: `omissis run` refuses a
plain-text input when the cache is under `results/` outside
`results/scratch/`. The restored reply is never saved. `<split>` below is
`pilot`, `dev` or `test`.

**Text with gold** — `data/{fixtures,pool,dev,test}/<text_id>.json`

```json
{
  "id": "bank-0001",
  "domain": "bank",
  "scenario": "mortgage_suspension",
  "profile_id": "p07",
  "has_special": true,
  "reviewed_by": "GC",
  "text": "…",
  "spans": [{"start": 0, "end": 5, "text": "…", "type": "PERSONA"}],
  "gold": {
    "intent": "mortgage_suspension",
    "amounts": [180000.0],
    "dates": ["2026-10-01"],
    "requested_action": "suspend_payment",
    "deadline": null
  }
}
```

`domain` is `bank` or `hr`. `reviewed_by` holds the initials of the human
reviewer and is absent until the review is done. Loaded spans get `confidence=1.0` and
`source="GOLD"`. Vocabularies for `scenario`, `intent` and `requested_action`
are in `docs/evaluation_protocol.md`.

**Loaders** — `src/omissis/eval/datasets.py`. Frozen dataclasses:
`TextRecord` (`id`, `domain`, `scenario`, `profile_id`, `has_special`, `text`,
`spans: tuple[Span, ...]`, `gold: Gold`, `reviewed_by: str | None`), `Gold`
(`intent`, `amounts`, `dates`, `requested_action`, `deadline`) and `Profile`
(the fields of the profile format below, with `gender: Gender`).
`load_text(path) -> TextRecord`; `load_texts(folder) -> list[TextRecord]`;
`load_profiles(path) -> list[Profile]`. `SCENARIOS` holds the scenario
vocabulary of the protocol. A file that breaks the format, or a span that does
not match the text, raises `DataError` (a `ValueError`) naming the file. So
does a missing or empty folder passed to `load_texts`. These
are the only functions that read text and profile files. The loader does not
check that `profile_id` exists among the profiles. The fixtures are
`data/fixtures/fx-bank-01.json` … `fx-hr-02.json`, with their own five
profiles `fx01`–`fx05` in `data/fixtures/profiles.json`; these are not part
of the 30 profiles of the evaluation.

**Profiles** — `data/profiles/profiles.json`: a list of objects with `id`,
`cohort`, `name`, `gender` (`M`/`F`), `age`, `city`, `employer`, `role`,
`bank`, `branch_city`, `financial` (object), `special` (`null` or
`{"category": "SALUTE", "fact": "…"}`).

**Candidate lists** — `data/profiles/candidates_N10.json`,
`candidates_N25.json`: `{"<text_id>": ["p07", "p03", …]}`, shuffled by seed,
always containing the true author.

**Text plan** — `data/profiles/plan.json`: `{"<text_id>": {"profile_id",
"scenario", "has_special", "requested_action", "pilot"}}`, fixed by seed. The
generator and the candidate lists work from it; `make split` reads `pilot`
from it.

**Split manifest** — `data/split.json`: `{"seed": …, "dev": [ids], "test":
[ids], "sha256": {"<text_id>": "…"}}`. `data/test_access.log` gets one line
per launch of `make eval-test`.

**LLM cache** — `results/cache/<role>.jsonl`, one object per line: `key`,
`role`, `model_id`, `revision`, `system`, `prompt`, `params`, `response`,
`created_at` (ISO 8601 UTC).

**Masked batch** — `results/<split>/masked/<config_name>/<text_id>.json`:
`{"text_id", "config_name", "run_id", "masked_text", "disclosure": [{"surrogate",
"type", "class", "source", "reason"}]}`. `config_name` is one of `REF-none`, `REF-oracle-direct`,
`REF-oracle`, `D1+R1`, `D2+R1`, `D4+R1`, `D4+R2`.

**Detected spans** — `results/<split>/detected/<detector>/<text_id>.json`:
`{"text_id", "detector", "spans": [{"start", "end", "text", "type",
"confidence", "source", "reason"}], "seconds": 0.0}`. Written by the detection
evaluation for every detector, so that detection metrics can be recomputed
without running any model. `seconds` is the wall time of that run and is
informative only: the reported latency comes from the timing pass of the
protocol, section 11.

**What is committed.** Everything under `results/` except `results/scratch/`
is committed: all data are synthetic. `make reproduce` recomputes every estimate,
interval, table and figure from the per-text outcomes stored in the metrics
files, with no network, no model, no detector and without reading
`data/test/`.

**Metrics** — `results/<split>/metrics/<name>.json`, where `<name>` is
`detection`, `linkage`, `attributes`, `utility`, `restoration`, `contrasts`,
`cost` and, under `results/dev/` only, `latency`, `judge_validation` and
`agreement` (computed once on the pool by `python -m omissis.eval.review
agreement`, before the review and before `make split`, with `"split":
"pool"`; `make eval-dev` never rewrites it). Each file: `{"split":
"pilot"|"dev"|"test", "seed": …, "generated_from": [run ids], "rows": [...],
"per_text": [...]}` with one row per configuration (and per detector, N or
attribute where relevant) holding the estimate and, where the protocol asks
for it, `ci_low` and `ci_high`. `per_text` holds one object per text and
configuration (or detector) with everything the rows are computed from:
`text_id`, the configuration or detector, the binary outcomes and scores, for
detection the counts of matched, missed and spurious spans per class and
type, for the attributes the true value; no text. The rows can be rebuilt
from `per_text` and `seed` alone.
`linkage` holds two more keys, written by `make reproduce`: `control_excluded`,
the ids of the texts of the split that the control of the protocol, section 7,
leaves out (the seven ids are a constant of `eval/report.py`), and
`control_rows`, the rows computed without them; both are empty when the split
holds none of the seven.

**Figures and tables** — `results/<split>/figures/privacy_utility.png`,
`results/<split>/scorecard.md`; on dev only, `results/dev/error_examples.md`
and `results/dev/error_taxonomy.md`.

## 6. Who calls what

- The app and `omissis run` first ask
  `feasibility.check_text(text, task, config, gold_spans=None) -> dict[SpanType, int]`.
  A request without a calculation cue returns an empty dict at once, with no
  masking: an ordinary request is handled as before. With a cue, it masks the text
  with `pipeline.mask`, erases that vault, and returns the masked types that block
  the request, each with its number of entities: amounts, dates, ages and dates of
  birth. It returns an empty dict when nothing blocks, and never a value of the text. Only then, and only
  when nothing blocks, they run the text through `pipeline.protect_send_restore`. A
  blocked request is not sent: the app shows the reason, `omissis run` prints one
  line on standard error and exits with status 2. `omissis batch`, `omissis mask`
  and the evaluation never call the check.
- The app also calls `supported_detectors` for its detector selector and
  `omissis.eval.datasets` to load its examples.
- The evaluation calls `omissis.eval.datasets`, `pipeline.mask`,
  `pipeline.protect_send_restore`, `backends.complete` and, for the detection
  metrics, `detect` and `supported_detectors`; nothing below them.
  `omissis.eval.detection.run(split, config)` measures every detector that
  `supported_detectors()` lists; `config` is any `RunConfig` read from `configs/eval.yaml`,
  from which `detect` takes the backend, the models file and the cache.
- D3 calls `backends.complete` with role `d3`, which is pinned to the provider
  `local`.
- Nothing outside `backends/` and the registered providers imports an LLM
  provider SDK or an LLM runtime. The libraries of D1 and D2 (Presidio, spaCy,
  `transformers`) are imported inside `src/omissis/detect/` only.
