# CLAUDE.md — Omissis, shared project instructions

**Omissis** (formerly "Privacy Shield") is the team project for *AI Frontiers: Large
Language Models* (LUISS, fall 2026). Three members: Giuseppe, Mattia, Andrea.

The code of every part is on `main` since 18 Nov 2026. The relay of blocks, its gates
and its path ownership are over (`docs/decisions.md`, 18 Nov): what is left is data,
evaluation runs and closing, and it is one list, `docs/TODO.md`, written on the branch
`final-steps`. Giuseppe decides what changes, reviews each step and merges. Your human's personal instructions are in `docs/agents/<name>.md`, loaded
through their `CLAUDE.local.md`; if no personal file is loaded, ask who you are
working for before doing anything.

## 1. Hard rules

1. **No repository operation your human has not asked for.** Committing, pushing,
   pulling, merging, rebasing, resetting, switching branch, tagging and any `gh`
   command happen only when your human asks for them in the current conversation.
   Read-only commands are always fine (`git status`, `git diff`, `git log`). When
   work is ready, say so, list the changed files and propose a commit message.
2. **Never open `data/test/`.** Do not read, list, grep, print or summarise it, with
   any tool or script. Only `make eval-test` touches it, and only a human launches
   that command; `make split` is launched by a human only. After the split the same
   holds for the other copies of the test texts: `results/cache/generator.jsonl`,
   `data/annotation/`, `results/scratch/pool-txt/` and the git history of
   `data/pool/`.
3. **No real personal data, anywhere.** Synthetic only: no real names of private
   people, real IBANs, real codici fiscali, in code, fixtures, tests, cache or docs.
4. **No secrets or weights in the repo.** API keys live in `.env` (gitignored).
   Models are referenced by name and revision in `configs/models.yaml`, which only a
   human edits: a new pin changes every run id.
5. **Specifications and code change together.** `docs/interfaces.md` fixes the
   contracts, the boundary functions, the configuration and the file formats;
   `docs/evaluation_protocol.md` fixes the data and every reported number. A change
   of behaviour updates them in the same commit and gets a row in
   `docs/decisions.md` that names who decided it. Never write that someone agreed
   who did not.
6. **The design is frozen (18 Nov).** From here: data, results, closing, and fixes
   of defects. Nothing that changes evaluated behaviour without a row in
   `docs/decisions.md`; no new configuration, metric or contrast; the fake lists in
   `src/omissis/replace/data/` do not change. A prompt (generator, attacker, T3,
   judge, D3) is part of the cache key: changing one needs a row in
   `docs/decisions.md`, and every call of that role is made again.
7. **Never claim legal anonymity.** The tool pseudonymises. Wording in code, docs
   and UI: "pseudonymised", "re-identification risk", never "anonymous".

## 2. What we are building

A local tool that sits between a user and a cloud LLM. For Italian text it:
`detect` sensitive spans → `resolve` them into entities → `replace` them with
pseudonyms (recording a session vault) → `send` the masked text → `restore` the
real values in the reply → return the reply plus a disclosure report.

The contribution is the **measurement**: what each configuration costs in privacy
(re-identification by an attacker LLM) and in answer quality. A small, complete,
well-tested system beats a large incomplete one. Prefer the simplest
implementation that satisfies the requirement; do not add abstractions, options or
files that nothing asks for.

### Components

| Stage | Module | Core content |
|---|---|---|
| Contracts | `src/omissis/contracts.py` | `Span`, `Entity`, `VaultEntry`, taxonomy enums |
| Detect | `src/omissis/detect/` | D0 rules, D1 Presidio, D2 ready-made classifier, D3 local LLM, D4 hybrid, span merging |
| Resolve | `src/omissis/resolve.py` | group mentions of the same entity, infer grammatical gender (rules only) |
| Replace | `src/omissis/replace/` | R1 typed placeholders, R2 realistic fakes |
| Vault | `src/omissis/vault.py` | in-memory session mapping, never logged in clear |
| Backends | `src/omissis/backends/` | providers `groq` (hosted) and `local` (this machine), JSONL cache, replay |
| Restore | `src/omissis/restore.py` | exact → normalised → fuzzy; outcome classes |
| Pipeline | `src/omissis/pipeline.py`, `cli.py` | `mask`, `protect_send_restore`; the `omissis` command |
| App | `src/omissis/app.py` | Gradio demo with replay mode |
| Evaluation | `src/omissis/eval/` | data files, text generation, review, split, pilot, detection, attacks, utility, judge, statistics, report, runner |

### Fixed design decisions

- **Span contract:** `start`, `end` (character offsets), `text`, `type`,
  `confidence` in [0,1], `source`, optional `reason`; `cls` is derived from `type`.
  Overlaps: longer span wins, then higher confidence, then source priority from the
  config; what is left of the other span outside the winner stays masked.
- **Taxonomy:** three classes — direct identifier, quasi-identifier, special
  category — with the types listed in `contracts.py`.
- **Masking policy:** direct identifiers and special-category spans are always
  masked. Quasi-identifiers are *all* annotated by type; whether they are masked is
  a configuration switch, on in every evaluated configuration that has a detector;
  `REF-oracle-direct` is the reference that leaves them visible.
- **A detector that fails stops the run:** no spans would send the text unmasked.
- **Placeholder format (R1):** ASCII only, `[TYPE_n]` or `[PERSONA_n_M]` /
  `[PERSONA_n_F]` when gender is known. One counter per type per session. The same
  entity always gets the same placeholder.
- **D3 never returns offsets** and runs on this machine (provider `local`): the
  text it reads is not pseudonymised yet. The model returns span *text* plus type
  and reason as schema-validated JSON; each text is found in the source as a whole
  token. Invalid JSON: retry once with a different prompt (the cache answers an
  identical one with the same reply), then count a failure and return no spans.
- **D4** takes direct identifiers from D0, D1 and D2; quasi-identifiers, special
  categories and `UTENTE` from D3.
- **R2 fakes** come from fixed lists that are disjoint from the profile pool (names,
  cities, employers) or keep the shape of the original (identifiers, amounts,
  dates). Fake IBANs pass the checksum but use a bank code that no bank has. A
  value without a realistic fake keeps its R1 placeholder: `RUOLO`, `STRUTTURA`,
  `NAZIONALITA`, `DATA_NASCITA`, the special categories. Deterministic for a seed.
- **Restoration never guesses.** Unresolved or ambiguous tokens are reported. No
  placeholder may remain silently in the output.
- **Every LLM call goes through `backends.complete` and its cache**
  (`results/cache/*.jsonl`, key = hash of model id, revision, system, prompt and
  parameters), temperature 0, including D3, the attacker, the judge and the text
  generator. Only provider functions registered with `backends.register_provider`
  talk to a model. Replay fails loudly on a cache miss.
- **One config file defines a run**; the run id is the hash of what the run
  computes. The key `detector` is `D0`–`D4`, or `GOLD` (mask the human annotation)
  or `NONE` (mask nothing): the three references are ordinary configurations. The
  configurations to evaluate are the seven of `configs/eval.yaml`.
- **Results are committed.** Everything under `results/` except the gitignored
  `results/scratch/`; `make reproduce` rebuilds every estimate, table and figure
  from the per-text outcomes in the metrics files alone.
- **The cache is append-only.** Only a run that `docs/TODO.md` asks for writes to
  `results/cache/`; every other run uses a `cache_dir` under `results/scratch/`.
  Never delete or rewrite cache records.

### Evaluated configurations

Detection metrics: D0, D1, D2, D3, D4.
Privacy and utility: `D1+R1`, `D2+R1`, `D4+R1`, `D4+R2`, plus three references that
need no detector — `REF-none` (unmasked), `REF-oracle-direct` (gold spans,
quasi-identifiers left visible) and `REF-oracle` (all gold spans masked) — and
analytic chance.
Pre-declared primary contrasts: (1) `D4+R1` vs `D1+R1` on linkage top-1;
(2) `D4+R1` vs `REF-none` on utility; (3) `D4+R2` vs `D4+R1` on full restoration.

## 3. Out of scope — do not build unless a human asks

Vault encryption or persistence, a local stand-in cloud model, fine-tuning,
generalisation as a replacement strategy, summary task (T2), role-labelled
placeholders, embedding-based restoration, public PII datasets, multi-turn memory,
non-Italian text, attachments, comparisons against third-party proxies.

## 4. Working method

- **Before coding:** restate the task in two or three lines and name the files you
  will touch. If it is ambiguous or conflicts with this file, ask.
- **Tests come with the code.** A task is not done until `make test` and
  `make lint` pass locally. Report the actual output, including failures. Never
  weaken or delete a test to make it pass; a test of a behaviour that a decision
  changed is rewritten for the new behaviour.
- **When changing a signature, decorator or import, grep for every usage** and
  update the callers in the same change.
- **Environment:** Python 3.11, `uv` with `uv.lock`. Install only through `uv`. A
  new dependency needs the human's approval and a pinned version. The detectors'
  libraries are in the dependency group `detect`, which `make setup` and CI do not
  install; the tests that need them use `pytest.importorskip`.
- **Small commits, one step each**, on the branch `final-steps`, by the rules at
  the top of `docs/TODO.md`. A defect found on `main` is fixed on a `fix/…`
  branch. Giuseppe reviews and merges once CI is green.
- **Hand back** with: files changed; commands run and their real output; what you
  are unsure about; a proposed commit message; one line for `docs/ai_use.md`
  (date, human, task, what the agent produced, what the human decided).
- **Agents compile, humans judge.** Agents write code, tests and first drafts.
  Humans review diffs, annotate and correct data, rate outputs, decide scope.
  Never present agent output as human-verified, never mark a text as reviewed and
  never fill a rating sheet.

## 5. Commands

```
make setup       # create the environment from uv.lock
make test        # unit and integration tests
make lint        # ruff check + ruff format --check
make format      # apply formatting
make demo        # Gradio app in replay mode (no network)
make split       # HUMANS ONLY: write data/dev and data/test, once
make eval-dev    # full evaluation on the dev split
make eval-test   # HUMANS ONLY, once
make reproduce   # rebuild every table and figure from the committed results
```

The presentation is on Thu 26 Nov 2026 at the earliest; the order of what is left
is in `docs/TODO.md`.
