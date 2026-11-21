# Omissis

A local tool that sits between a user and a cloud LLM. For Italian text it detects
sensitive spans, replaces them with pseudonyms, sends the pseudonymised text to the
model, restores the real values in the reply and reports what was disclosed.

The contribution is the measurement: what each configuration costs in privacy
(re-identification risk against an attacker LLM) and in answer quality.

Team project for *AI Frontiers: Large Language Models* (LUISS, fall 2026).

## What it is and what it is not

- It **is** a pseudonymiser for one Italian text at a time (bank and HR
  correspondence), with a session vault that lives in memory, a restoration step
  that reports every value it could not put back, and an evaluation that measures
  what an attacker LLM can still infer.
- It is **not** an anonymiser. Pseudonymised text can still be re-identified,
  and the evaluation measures that risk. It does not encrypt or persist the vault,
  does not handle attachments, other languages or multi-turn chats, and has not
  been tested on real personal data: every person and value in this repository is
  invented.

## Quick start

Requires [`uv`](https://docs.astral.sh/uv/) and `make`. `uv` installs Python 3.11.

```
make setup              # create the environment from uv.lock
make test               # unit and integration tests
make lint               # ruff check and format check
cp .env.example .env    # then write your GroqCloud key in GROQ_API_KEY
```

Only the commands that call a hosted model need the key in `.env`, and they read
it through `uv run --env-file .env ...`. The detectors D1 to D4 need two more
things, which `make setup` and CI do not install:

```
uv sync --locked --group detect   # Presidio, spaCy and it_core_news_lg, transformers
ollama pull gpt-oss:20b           # the local model of D3, with Ollama running
```

The weights of D2 are read from the local Hugging Face cache (model and revision
in `configs/models.yaml`). Without the `detect` group the tests that need it are
skipped.

## Run one text

```
uv run omissis run --config configs/skeleton.yaml --input data/fixtures/fx-bank-01.json
```

This runs the whole pipeline on a synthetic fixture with detector D0 and
placeholders R1. Every model role points to the built-in `echo` provider, which
returns the prompt unchanged, so the command needs no network and no key. The
command prints the masked text, the reply, the restored reply and the disclosure
report to standard output. The restored reply holds the original values: do not
redirect it under `results/`. A run configuration (`docs/interfaces.md`,
section 4) chooses the detector, the strategy and the backend: `cloud` calls the
model, and `replay` answers from the cache only.

## Demo

```
make demo
```

This starts a Gradio page in replay mode, with no network: one fixture at a
time, the masked text as it is sent, the restored reply and the disclosure list.
**Not ready yet:** the page starts, but its runs have not been recorded in
`results/cache/` (step C4 of `docs/TODO.md`), so every fixture ends in a cache
miss.

## Architecture

One line per stage of the pipeline (`src/omissis/`):

- **detect** (`detect/`): finds sensitive spans. D0 rules, D1 Presidio, D2 a
  ready-made token classifier, D3 a local LLM that returns span text and never
  offsets, D4 a hybrid (direct identifiers from D0, D1 and D2, everything else
  from D3). Overlaps are merged by length, then
  confidence, then source priority.
- **resolve** (`resolve.py`): groups the mentions of one entity and infers
  grammatical gender by rules.
- **replace** (`replace/`): R1 typed placeholders (`[PERSONA_1_F]`, `[IBAN_1]`), or
  R2 realistic fakes from fixed lists disjoint from the profiles, deterministic
  for a seed.
- **vault** (`vault.py`): the in-memory mapping of the session, never logged in
  clear.
- **send** (`backends/`): every LLM call goes through one function and an
  append-only JSONL cache, at temperature 0.
- **restore** (`restore.py`): exact, then normalised, then fuzzy matching. It
  never guesses: an unresolved or invented token is reported.
- **report** (`pipeline.py`, `cli.py`, `app.py`): the reply, plus a disclosure
  report of what was masked and how it came back.

Taxonomy: direct identifiers, quasi-identifiers and special categories
(`src/omissis/contracts.py`).

## Evaluation

66 synthetic emails, written from 30 invented profiles, are split once into dev
and a held-out test set. Seven configurations are measured. Three are references:
`REF-none` (nothing masked), `REF-oracle-direct` (gold direct identifiers and
special categories masked, quasi-identifiers left visible) and `REF-oracle` (every
gold span masked). Four use detectors and replacements:
`D1+R1`, `D2+R1`, `D4+R1` and `D4+R2`. The privacy measures are an attacker LLM's
linkage and attribute attacks against the profiles. The utility measures are a
structured extraction task and a judged reply. Restoration is measured by
outcome. There are three pre-declared contrasts:

1. `D4+R1` vs `D1+R1` on linkage top-1;
2. `D4+R1` vs `REF-none` on utility;
3. `D4+R2` vs `D4+R1` on full restoration.

Each contrast is tested with paired tests and the Holm correction. Data, metrics,
attacks and statistics are fixed in `docs/evaluation_protocol.md`; the models
are described in `docs/cards.md`.

## Reproduce

```
make reproduce
```

This rebuilds every estimate, table and chart from the per-text outcomes in the
committed metrics files (`results/<split>/metrics/`). It uses no network, no model
and no detector, and it reads no text. A split without metrics is skipped with
one line. Today only `pilot` exists: it has no scorecard row, so nothing but its
metrics files is rewritten, and they come out identical.

## Results

No result is reported yet. The 66 texts are being reviewed and the evaluation
has not run. What is left is in `docs/TODO.md`.

## Limitations

- **Threat model.** The attacker is one LLM that sees the masked text and a list
  of 10 or 25 candidate profiles. A stronger attacker, external data or several
  texts from one author are not measured.
- **Pseudonymisation is not anonymisation.** Quasi-identifiers and the content of
  a request can still point to a person. The numbers measure re-identification
  risk; they do not prove it is low.
- **Derived values.** The model can compute values from the surrogates (a
  postcode for a fake town, a sum of masked amounts), and restoration cannot
  undo them.
- **Synthetic data only.** The texts were written by a model and are more regular
  than real mail. Texts by one author are not independent, so intervals over
  texts overstate precision.
- **One reviewer per text and one rater** of the judge. The judge is the same
  model as the cloud model.
- **Known and not fixed:**
  - An R2 amount that the reply writes without its decimals ("701 euro" for
    "701,00 euro") stays in the reply.
  - Two invalid JSON replies of D3 give no spans for that text. With D4 the
    direct identifiers found by D0, D1 and D2 are still masked; the
    quasi-identifiers, the special categories and the `UTENTE` codes are not.
  - An empty reply of the local model stops the run and is never cached. At
    temperature 0 the same text may stop the next launch too.
  - Under R2, two people told apart only by a title ("Sig. Ferri",
    "Sig.ra Ferri") share one fake surname.
  - Other limits are listed in `docs/handoff/block-2.md` (section 4) and
    `docs/handoff/block-3.md` (section 5).

## AI assistance

Code, tests and first drafts of documents are produced with AI coding agents
(Claude Code); every change is reviewed and merged by a team member.
Each task's AI use is recorded in `docs/ai_use.md`.
