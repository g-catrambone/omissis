# CLAUDE.md — Omissis, shared project instructions

**Omissis** (formerly "Privacy Shield") is the team project for *AI Frontiers: Large Language Models* (LUISS, fall 2026).
Three members: Giuseppe, Mattia, Andrea. Each works with their own Claude agent.
The human-readable plan is `docs/Linee_Guida_Progetto.pdf` (Italian). Where this file
and the PDF disagree, stop and ask your human.

Your human's personal instructions are in `docs/agents/<name>.md`, loaded through their
`CLAUDE.local.md`. If no personal file is loaded, ask who you are working for before
doing anything.

## 1. Hard rules (never negotiable)

1. **No autonomous repository operations.** Never run `git add`, `git commit`, `git push`,
   `git pull`, `git fetch`, `git merge`, `git rebase`, `git reset`, `git stash`,
   `git checkout`/`git switch` to another branch, `git tag`, or any `gh` command
   unless your human has explicitly asked for *that specific operation* in the
   current conversation. Consent covers one operation; it does not carry over to
   the next one or to later sessions. Read-only commands are always fine:
   `git status`, `git diff`, `git log`, `git branch --show-current`.
   When work is ready, say so, list the changed files, and propose a commit
   message. Then wait.
2. **Never open `data/test/`.** Do not read, list, grep, print or summarise it.
   Only `make eval-test` touches it, and only a human launches that command.
3. **No real personal data, anywhere.** Synthetic only: no real names of private
   people, real IBANs, real codici fiscali, in code, fixtures, tests, cache or docs.
4. **No secrets or weights in the repo.** API keys live in `.env` (gitignored).
   Models are referenced by name and revision in `configs/models.yaml`.
5. **Do not change `src/omissis/contracts.py`** without your human saying the
   whole team agreed. Every workstream depends on it. It is created once at M0
   by workstream B and read together by all three members before other work starts.
6. **Stay in your workstream's paths** (see the personal file). If a task needs a
   change in someone else's path, describe the change and stop; the human opens
   an issue for the owner.
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
implementation that satisfies the requirement; do not add abstractions,
options or files that the plan does not ask for.

### Components

| Stage | Module | Core content |
|---|---|---|
| Contracts | `src/omissis/contracts.py` | `Span`, `Entity`, `VaultEntry`, taxonomy enums |
| Detect | `src/omissis/detect/` | D0 rules, D1 Presidio, D2 ready-made classifier, D3 local LLM, D4 hybrid, span merging |
| Resolve | `src/omissis/resolve.py` | group mentions of the same entity, infer grammatical gender (rules only) |
| Replace | `src/omissis/replace/` | R1 typed placeholders, R2 realistic fakes |
| Vault | `src/omissis/vault.py` | in-memory session mapping, never logged in clear |
| Backends | `src/omissis/backends/` | cloud adapter, JSONL cache, replay |
| Restore | `src/omissis/restore.py` | exact → normalised → fuzzy; outcome classes |
| Pipeline | `src/omissis/pipeline.py`, `cli.py` | `protect_send_restore`, single text and batch runs |
| App | `src/omissis/app.py` | Gradio demo with replay mode |
| Evaluation | `src/omissis/eval/` | detection, attacks, utility, judge, statistics, report |

### Fixed design decisions

- **Span contract:** `start`, `end` (character offsets), `text`, `cls`, `type`,
  `confidence` in [0,1], `source`, optional `reason`. Overlaps: longer span wins,
  then higher confidence, then source priority from the config.
- **Taxonomy:** three classes — direct identifier, quasi-identifier, special
  category — with the types listed in `contracts.py`.
- **Masking policy:** direct identifiers and special-category spans are always
  masked. Quasi-identifiers are *all* annotated by type; whether they are masked
  is a configuration switch (on for D3/D4).
- **Placeholder format (R1):** ASCII only, `[TYPE_n]` or `[PERSONA_n_M]` /
  `[PERSONA_n_F]` when gender is known. One counter per type per session. The same
  entity always gets the same placeholder. Role-specific labels are an extension.
- **D3 never returns offsets.** The local LLM returns span *text* plus type and
  reason as schema-validated JSON; offsets are found by string search in the
  source. Invalid JSON: retry once, then log a failure and return no spans.
- **R2 fakes** come from fixed lists that are disjoint from the profile pool
  (names, cities, employers). Fake IBANs pass the checksum but use a documented
  non-existent bank code. Deterministic for a given seed.
- **Restoration never guesses.** Unresolved or ambiguous tokens are reported. No
  placeholder may remain silently in the output.
- **Every LLM call goes through the cache** (`results/cache/*.jsonl`, key = hash
  of model id + prompt + parameters), temperature 0. Never call a provider SDK
  directly from evaluation code.
- **One config file defines a run**; the run id is the hash of the resolved config.

### Evaluated configurations

Detection metrics: D0, D1, D2, D3, D4 (no LLM calls beyond D3).
Privacy and utility: `D1+R1`, `D2+R1`, `D4+R1`, `D4+R2`, plus `REF-none`
(unmasked), `REF-oracle` (gold spans masked with R1) and analytic chance.
Pre-declared primary contrasts: (1) `D4+R1` vs `D1+R1` on linkage top-1;
(2) `D4+R1` vs `REF-none` on utility; (3) `D4+R2` vs `D4+R1` on full restoration.
Do not add configurations, metrics or contrasts on your own initiative.

## 3. Out of scope — do not build unless a human asks

Vault encryption or persistence, a local stand-in cloud model, fine-tuning,
generalisation as a replacement strategy, summary task (T2), role-labelled
placeholders, embedding-based restoration, public PII datasets, multi-turn
memory, non-Italian text, attachments, comparisons against third-party proxies. These are listed as extensions in the PDF.

## 4. Working method

- **One task = one branch = one pull request.** Branch names: `ws-a/…`, `ws-b/…`,
  `ws-c/…`, `shared/…`. The human creates the branch and commits.
- **Before coding:** restate the task in two or three lines and name the files
  you will touch. If the task is ambiguous or conflicts with this file, ask.
- **Tests come with the code.** Every module has unit tests in `tests/`; a task
  is not done until `make test` and `make lint` pass locally. Report the actual
  output, including failures. Never weaken or delete a test to make it pass.
- **When changing a signature, decorator or import, grep for every usage** and
  update callers in the same change (within your paths; report the others).
- **Environment:** Python 3.11, `uv` with `uv.lock`. Before installing anything
  run `which python` and `python -m pip --version` and confirm the project
  environment is active. New dependencies need the human's approval and a pinned
  version.
- **Small diffs.** Target under ~300 changed lines per pull request so a human can
  really review it. Split larger work.
- **Leave a review note** at the end of each task (your human pastes it in the
  pull request): what changed, how to verify it, what you are unsure about, and
  three questions a reviewer should be able to answer after reading the code.
- **Workstream log.** Each workstream has one log that only its own agent
  writes: `docs/log/ws-a.md`, `docs/log/ws-b.md`, `docs/log/ws-c.md`.
  - *At the start of every session* read the other two logs, so you know what
    changed elsewhere. They are only as recent as your human's last `git pull`:
    treat them as possibly stale, and never pull to refresh them yourself.
  - *At the end of every task* append one entry to your own log, using the
    format below. This is a file edit, not a repository operation: write it
    directly, then mention it in your hand-back so it goes into the human's commit.
  - Never edit another workstream's log, and never rewrite past entries; correct
    a mistake with a new entry.

  ```
  ## 2026-11-12 · short task title · branch ws-b/restore-normalised
  - Changed: what now behaves differently, in one or two lines
  - Files: paths touched
  - Affects other workstreams: none | who must do what
  - Open points: doubts, known gaps
  ```
- **Log AI use.** Propose one line for `docs/ai_use.md`: date, human, task, what
  the agent produced, what the human changed. The human adds it; do not edit
  that file yourself, because all three members append to it.
- **Decisions** that alter behaviour or scope go in `docs/decisions.md`
  (date, decision, reason, who agreed). Propose the entry; the human adds it.

## 5. Who does what

| Workstream | Owner | Reviewer | Paths |
|---|---|---|---|
| A · Detection and app | Mattia | Giuseppe | `src/omissis/detect/`, `src/omissis/app.py`, `src/omissis/eval/detection.py` |
| B · Pseudonymisation core | Giuseppe | Andrea | `contracts.py`, `resolve.py`, `replace/`, `vault.py`, `restore.py`, `backends/`, `pipeline.py`, `cli.py`, `config.py` |
| C · Data and evaluation | Andrea | Mattia | `data/`, `src/omissis/eval/` (except `detection.py`), `docs/annotation_guide.md` |

Each owner's paths also include:

- their own log in `docs/log/`;
- the tests for their modules, in a matching folder: `tests/detect/` and
  `tests/app/` (A), `tests/core/` (B), `tests/eval/` and `tests/data/` (C).
  Shared fixtures in `tests/fixtures/` are added to, never rewritten;
- A: nothing else. B: `README.md`, `Makefile`, `pyproject.toml`, `uv.lock`, CI,
  `configs/models.yaml`. C: the other files in `configs/`, `results/`,
  `docs/cards.md`.

`results/cache/` is written by any workstream's runs; never delete or rewrite
cache files that your own run did not create.

Agents do the compiling work: code, tests, first drafts of texts and docs.
Humans do the judging work: reviewing diffs, annotating and correcting data,
rating outputs, deciding scope, committing. Never present agent output as
human-verified.

## 6. Commands

```
make setup       # create the environment from uv.lock
make test        # unit and integration tests
make lint        # ruff check + ruff format --check
make demo        # Gradio app in replay mode (no network)
make eval-dev    # full evaluation on the dev split
make eval-test   # HUMANS ONLY, once, after the freeze
make reproduce   # regenerate every figure and table from the cache
```

## 7. Milestones (worst case: presentation on Thu 26 Nov 2026)

| ID | Date | Exit criterion |
|---|---|---|
| M0 | Wed 11 Nov | repo, scaffold, `contracts.py` agreed, models pinned |
| M1 | Fri 13 Nov | D0+D1 → R1 → cloud → restore end to end on 5 emails, replay works |
| M2 | Sun 15 Nov | attack pilot on 10 texts: go/no-go on the attack design; D2 integrated |
| M3 | Thu 19 Nov | D3, D4, resolver, R2, full dataset reviewed, app, first chart on dev |
| M4 | Sat 21 Nov | freeze: tag, configs locked, `make eval-test` run once |
| M5 | Mon 23 Nov | chart, scorecard, error taxonomy, `make reproduce`, clean-clone check |
| M6 | Wed 25 Nov | slides, two rehearsals, README final |

After M4 only bug fixes that do not change evaluated behaviour are allowed.
