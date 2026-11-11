# Interface specification

How the three workstreams connect. This document is the contract: the code in
`src/omissis/contracts.py` and the boundary functions must match it exactly.
If something here does not fit a task, do not work around it and do not change
it: describe the problem and stop (CLAUDE.md, rule 5).

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
| `Span` | `start:int`, `end:int`, `text:str`, `type:SpanType`, `confidence:float`, `source:str`, `reason:str\|None=None` | `0 <= start < end`; `len(text) == end-start`; `0 <= confidence <= 1`. Offsets are character offsets, `end` exclusive. Property `cls` = `TYPE_CLASS[type]` (derived, never stored). Method `matches(source_text)` is true when `source_text[start:end] == text`. `source` is a `DetectorId` value or `GOLD_SOURCE`. `reason` is required for D3. |
| `Entity` | `entity_id:str`, `type:SpanType`, `canonical:str`, `mentions:tuple[Span,...]`, `gender:Gender=UNKNOWN` | At least one mention; all mentions have the entity's type. `entity_id` is `<TYPE>_<n>`, numbered per type by first appearance. Property `cls`. |
| `VaultEntry` | `surrogate:str`, `original:str`, `type:SpanType`, `entity_id:str`, `original_variants:tuple[str,...]=()`, `surrogate_variants:tuple[str,...]=()` | `repr` never shows `original` or the variants. `surrogate` is the placeholder (R1) or the fake value (R2). `surrogate_variants` is for R2 (for example the fake surname alone). |
| `RestoreEvent` | `surrogate:str`, `outcome:RestoreOutcome`, `found_as:str\|None=None` | One restoration decision. |
| `DisclosureItem` | `surrogate:str`, `type:SpanType`, `source:str`, `reason:str\|None=None` | One line of the disclosure panel. Never contains the original value. Property `cls`. |
| `MaskResult` | `masked_text:str`, `spans:tuple[Span,...]`, `entities:tuple[Entity,...]`, `disclosure:tuple[DisclosureItem,...]` | Output of masking without any LLM call. |
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
  `n < 1`.
- `parse_placeholder(token) -> (SpanType, int, Gender) | None`; `None` for an
  unknown type, a malformed token, or a gender suffix on a non-person type.

## 3. Boundary functions

Signatures are fixed, including parameter names.

| Function | Module | Owner |
|---|---|---|
| `detect(text: str, detector: DetectorId, config: RunConfig) -> list[Span]` | `omissis.detect` | A |
| `resolve(spans: Sequence[Span], text: str) -> list[Entity]` | `omissis.resolve` | B |
| `replace(text: str, entities: Sequence[Entity], strategy: Strategy, seed: int, vault: Vault \| None = None) -> tuple[str, Vault]` | `omissis.replace` | B |
| `restore(reply: str, vault: Vault, fuzzy_threshold: float) -> tuple[str, list[RestoreEvent]]` | `omissis.restore` | B |
| `complete(request: LLMRequest, config: RunConfig) -> LLMResponse` | `omissis.backends` | B |
| `register_provider(name: str, fn: ProviderFn) -> None` | `omissis.backends` | B |
| `mask(text: str, config: RunConfig, gold_spans: Sequence[Span] \| None = None, vault: Vault \| None = None) -> tuple[MaskResult, Vault]` | `omissis.pipeline` | B |
| `protect_send_restore(text: str, task: str, config: RunConfig) -> PipelineResult` | `omissis.pipeline` | B |

### Behaviour

**`detect`** — Returns spans sorted by `start`, non-overlapping. Overlaps are
resolved inside: longer span wins, then higher confidence, then earlier
position in `config.source_priority`. Every span satisfies `span.matches(text)`.
Quasi-identifier spans are returned even when `config.mask_quasi` is false:
the caller decides whether to mask them. Never raises on bad input or on a
failing model; a failing detector logs and contributes no spans. A detector
not built yet raises `NotImplementedError` with a clear message.

**`resolve`** — Every input span ends up in exactly one entity. Person
mentions merge when one contains the other's surname; two people with one
surname and different first names stay separate. Other types merge on
normalised equality (case and whitespace). Gender from titles first
(Sig./Sig.ra, Dott./Dott.ssa), then from a first-name list, otherwise
`UNKNOWN`. Rules only; the same function serves every detector.

**`replace`** — R1 writes `make_placeholder` tokens. R2 writes realistic fake
values, deterministic for `seed`, from lists disjoint from the profile pool
and never already present in `text`. The same entity always gets the same
surrogate; a passed-in vault is reused so surrogates stay consistent across
texts of one session. Substitution runs from the end of the text to the start.

**`restore`** — Order: exact match; normalised match (case, spacing, missing
brackets, underscores as spaces); fuzzy match accepted only at or above
`fuzzy_threshold`. Never guesses. A placeholder-shaped token absent from the
vault gives `hallucinated_token`; a token that looks like a surrogate but has
no safe match stays in place and gives `altered_unresolved`; a surrogate the
reply does not use gives `dropped`. R2 surrogates match on whole tokens only.
Returns the restored text and one event per vault entry or suspicious token.

**`complete`** — Looks the request up in `config.cache_dir` by `cache_key`.
Hit: returns the stored response with `cached=True`. Miss with
`config.backend == "cloud"`: calls the provider registered for the model,
appends the exchange to the cache, returns it. Miss with `"replay"`: raises
`CacheMissError`, never touches the network. Refuses a role whose model is
not pinned. Every LLM call in the project goes through this function,
including D3, the attacker, the judge and the text generator.

**`register_provider`** — `ProviderFn = Callable[[ModelSpec, LLMRequest], str]`.
A provider turns one request into text and does no caching. B registers the
cloud provider; A registers the local runtime used by D3. Registering a name
twice raises `ValueError`.

**Built-in provider `echo`** — registered by `backends` itself. It returns
`request.prompt` unchanged and needs no network, key or model. It exists so
the whole pipeline can run before any real model is chosen: a models file
that sets a role to `provider: echo`, `id: echo`, `revision: "1"` counts as
pinned. `configs/models.echo.yaml` pins every role this way and
`configs/skeleton.yaml` is a run configuration that uses it (D0, R1,
`backend: cloud`). `echo` is for the skeleton, tests and debugging only; no
reported number may come from it.

**`mask`** — detect → resolve → replace, no LLM call. With `gold_spans` the
detector is skipped and those spans are masked (REF-oracle). Quasi-identifier
spans are masked only when `config.mask_quasi` is true; direct and
special-category spans always.

**`protect_send_restore`** — Masks `text`, sends `task` followed by the masked
text to the role `cloud` with `KEEP_PLACEHOLDERS_INSTRUCTION` as system
message, restores the reply. `task` is the user's instruction in Italian. The
vault is created for the call and erased before returning.
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
`{id, revision, system, prompt, params}`.

## 4. Configuration — `src/omissis/config.py`

One YAML file defines one run. Unknown keys are an error.

| Key | Type | Meaning |
|---|---|---|
| `detector` | `D0`–`D4` | detector configuration |
| `strategy` | `R1` \| `R2` | replacement strategy |
| `mask_quasi` | bool | mask quasi-identifiers (true for D3 and D4 runs) |
| `backend` | `cloud` \| `replay` | where cache misses go |
| `seed` | int | seed for fakes and resampling |
| `fuzzy_threshold` | float in [0,1] | acceptance threshold of fuzzy restore |
| `source_priority` | list of detector ids | tie-break for overlapping spans |
| `models_file` | path | normally `configs/models.yaml` |
| `cache_dir` | path | normally `results/cache` |

API: `RunConfig` (frozen dataclass with these fields), `load_config(path,
overrides=None) -> RunConfig`, `with_overrides(config, **changes)`,
`run_id(config) -> str` (first 12 hex characters of the SHA-256 of the
resolved configuration as sorted JSON), `ConfigError(ValueError)`.

`configs/models.yaml` has one entry per role — `cloud`, `attacker`, `judge`,
`generator`, `d3`, `d2` — each with `provider`, `id`, `revision`. The literal
`TO_BE_PINNED` marks an undecided value. API: `ModelSpec(role, provider, id,
revision)` with property `pinned`; `load_models(path) -> dict[str, ModelSpec]`;
`require_pinned(models, role) -> ModelSpec` raising `ConfigError` when unpinned.

## 5. File formats

All JSON is UTF-8 with `ensure_ascii=False`. Nothing written under `results/`
may contain vault contents.

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

**Profiles** — `data/profiles/profiles.json`: a list of objects with `id`,
`cohort`, `name`, `gender` (`M`/`F`), `age`, `city`, `employer`, `role`,
`bank`, `branch_city`, `financial` (object), `special` (`null` or
`{"category": "SALUTE", "fact": "…"}`).

**Candidate lists** — `data/profiles/candidates_N10.json`,
`candidates_N25.json`: `{"<text_id>": ["p07", "p03", …]}`, shuffled by seed,
always containing the true author.

**Split manifest** — `data/split.json`: `{"seed": …, "dev": [ids], "test":
[ids], "sha256": {"<text_id>": "…"}}`. `data/test_access.log` gets one line
per run of `make eval-test`.

**LLM cache** — `results/cache/<role>.jsonl`, one object per line: `key`,
`role`, `model_id`, `revision`, `system`, `prompt`, `params`, `response`,
`created_at` (ISO 8601 UTC).

**Masked batch** — `results/masked/<config_name>/<text_id>.json`:
`{"text_id", "config_name", "run_id", "masked_text", "disclosure": [{"surrogate",
"type", "class", "source", "reason"}]}`. `config_name` is one of `REF-none`,
`REF-oracle`, `D1+R1`, `D2+R1`, `D4+R1`, `D4+R2`.

**Metrics** — `results/metrics/<name>.json`, where `<name>` is `detection`,
`linkage`, `attributes`, `utility`, `restoration`, `latency`, `contrasts`.
Each file: `{"split": "dev"|"test", "generated_from": [run ids], "rows": [...]}`
with one row per configuration (and per detector, N or attribute where
relevant) holding the estimate and, where the protocol asks for it,
`ci_low` and `ci_high`.

**Figures and tables** — `results/figures/privacy_utility.png`,
`results/scorecard.md`, `results/error_taxonomy.md`.

## 6. Who calls what

- The app (A) calls `pipeline.protect_send_restore` only.
- The evaluation (C) calls `pipeline.mask`, `pipeline.protect_send_restore`
  and `backends.complete`, nothing below them.
- D3 (A) calls `backends.complete` with role `d3` and registers its local
  runtime with `backends.register_provider`.
- Nothing outside `backends/` and the registered providers imports a provider
  SDK or a model runtime.
