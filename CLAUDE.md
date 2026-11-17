# CLAUDE.md — Omissis, shared project instructions

**Omissis** (formerly "Privacy Shield") is the team project for *AI Frontiers: Large Language Models* (LUISS, fall 2026).
Three members: Giuseppe, Mattia, Andrea. Each works with their own Claude agent.
The work is a relay of blocks: one member owns each block and works on it alone,
then hands it over frozen to the next; the detectors are a block of their own
that runs beside the others (`docs/tasks/README.md`).
`docs/Linee_Guida_Progetto.pdf` (Italian) is the summary for the three humans. Agents
work from this file and from the markdown files under `docs/`, which prevail: the
humans update the PDF last, so it may lag behind, and a difference from it is not a
reason to stop.

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
2. **Never open `data/test/`.** Do not read, list, grep, print or summarise it,
   with any tool or script. Only `make eval-test` touches it, and only a human
   launches that command. `make split` is also launched by a human only. After
   the split the same holds for the other copies of the test texts:
   `results/cache/generator.jsonl`, `data/annotation/` and the git history of
   `data/pool/`.
3. **No real personal data, anywhere.** Synthetic only: no real names of private
   people, real IBANs, real codici fiscali, in code, fixtures, tests, cache or docs.
4. **No secrets or weights in the repo.** API keys live in `.env` (gitignored).
   Models are referenced by name and revision in `configs/models.yaml`.
5. **Do not change `src/omissis/contracts.py`, `docs/interfaces.md` or
   `docs/evaluation_protocol.md`** on your own. Every block depends on
   them. They are drafts until the gate that freezes them (`docs/tasks/README.md`):
   before it, propose the change and your human agrees it with the team in
   chat; after it, a change needs an entry in `docs/decisions.md` agreed by all
   three.
6. **Work only on your own block, and only during its turn.** Your personal
   file says which block is yours, which gate it waits for and which paths it
   owns. Before that gate is ticked, or after your own gate is ticked, you
   change nothing, except what the exceptions listed in
   `docs/tasks/README.md` allow. If a
   task needs a change in another block's paths, describe the change and stop:
   the owner of that block writes the fix (`docs/tasks/README.md`, "A bug in
   another block").
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
| Data files | `src/omissis/eval/datasets.py` | loaders for annotated texts and profiles |
| Detect | `src/omissis/detect/` | D0 rules, D1 Presidio, D2 ready-made classifier, D3 local LLM, D4 hybrid, span merging |
| Resolve | `src/omissis/resolve.py` | group mentions of the same entity, infer grammatical gender (rules only) |
| Replace | `src/omissis/replace/` | R1 typed placeholders, R2 realistic fakes |
| Vault | `src/omissis/vault.py` | in-memory session mapping, never logged in clear |
| Backends | `src/omissis/backends/` | cloud adapter, JSONL cache, replay |
| Restore | `src/omissis/restore.py` | exact → normalised → fuzzy; outcome classes |
| Pipeline | `src/omissis/pipeline.py`, `cli.py` | `mask`, `protect_send_restore`; the `omissis` command |
| App | `src/omissis/app.py` | Gradio demo with replay mode |
| Evaluation | `src/omissis/eval/` | detection, attacks, utility, judge, statistics, report |

### Fixed design decisions

- **Span contract:** `start`, `end` (character offsets), `text`, `type`,
  `confidence` in [0,1], `source`, optional `reason`; `cls` is derived from
  `type`. Overlaps: longer span wins,
  then higher confidence, then source priority from the config.
- **Taxonomy:** three classes — direct identifier, quasi-identifier, special
  category — with the types listed in `contracts.py`.
- **Masking policy:** direct identifiers and special-category spans are always
  masked. Quasi-identifiers are *all* annotated by type; whether they are masked
  is a configuration switch, on in every evaluated configuration that has a
  detector; `REF-oracle-direct` is the reference that leaves them visible.
- **Placeholder format (R1):** ASCII only, `[TYPE_n]` or `[PERSONA_n_M]` /
  `[PERSONA_n_F]` when gender is known. One counter per type per session. The same
  entity always gets the same placeholder. Role-specific labels are an extension.
- **D3 never returns offsets.** The local LLM returns span *text* plus type and
  reason as schema-validated JSON; offsets are found by string search in the
  source. Invalid JSON: retry once with a different prompt (the cache answers
  an identical one with the same reply), then log a failure and return no spans.
- **R2 fakes** come from fixed lists that are disjoint from the profile pool
  (names, cities, employers). Fake IBANs pass the checksum but use a documented
  non-existent bank code. Deterministic for a given seed.
- **Restoration never guesses.** Unresolved or ambiguous tokens are reported. No
  placeholder may remain silently in the output.
- **Every LLM call goes through `backends.complete` and its cache**
  (`results/cache/*.jsonl`, key = hash of model id, revision, system, prompt and
  parameters), temperature 0, including the local D3 model, the attacker, the
  judge and the text generator. Only provider functions registered with
  `backends.register_provider` talk to a model.
- **One config file defines a run**; the run id is the hash of what the run
  computes. The key `detector` is `D0`–`D4`, or `GOLD` (mask the human
  annotation) or `NONE` (mask nothing): the three references are ordinary
  configurations and run through the same pipeline as the others. The named
  configurations to evaluate are listed in `configs/eval.yaml`.
- **Results are committed.** `results/cache/` and, for each split (`pilot`,
  `dev`, `test`), `results/<split>/masked/`, `detected/`, `metrics/` and
  `figures/` go in the repository; `make reproduce` rebuilds every estimate,
  table and figure from the per-text outcomes in the metrics files alone.

### Evaluated configurations

Detection metrics: D0, D1, D2, D3, D4 (no LLM calls beyond D3).
Privacy and utility: `D1+R1`, `D2+R1`, `D4+R1`, `D4+R2`, plus three references
that need no detector — `REF-none` (unmasked), `REF-oracle-direct` (gold spans,
quasi-identifiers left visible) and `REF-oracle` (all gold spans masked) — and
analytic chance.
Pre-declared primary contrasts: (1) `D4+R1` vs `D1+R1` on linkage top-1;
(2) `D4+R1` vs `REF-none` on utility; (3) `D4+R2` vs `D4+R1` on full restoration.
Do not add configurations, metrics or contrasts on your own initiative.

## 3. Out of scope — do not build unless a human asks

Vault encryption or persistence, a local stand-in cloud model, fine-tuning,
generalisation as a replacement strategy, summary task (T2), role-labelled
placeholders, embedding-based restoration, public PII datasets, multi-turn
memory, non-Italian text, attachments, comparisons against third-party proxies.
The PDF describes some of them as possible extensions: that does not put them
in scope.

## 4. Working method

- **A relay of blocks.** Block 1 skeleton (Mattia, written) → block 2 core
  completion (Giuseppe) → block 3 data and evaluation (Andrea) → block 5
  closing (Giuseppe) → presentation (all). Block 4, the detectors (Mattia),
  runs beside blocks 2 and 3 because it touches only `src/omissis/detect/`,
  and joins the evaluation after block 3. Each block ends with a gate ticked by
  the humans and a git tag; what comes next builds on code that has been run
  and checked, not on code that is only written.
- **Starting work.** When your human says "start", "continue" or similar without
  naming a task, follow `docs/tasks/README.md`: check that it is your block's
  turn, read the hand-over notes of the earlier blocks, take the task that
  step 3 of that file selects, work until its *Done when* lines are true, and
  hand back. Never fill in a line marked **Human:** yourself; it blocks only
  what depends on it (`docs/tasks/README.md`). Do one task per hand-back; do
  not chain tasks without your human's go-ahead.
- **Two documents are the specification.** `docs/interfaces.md` fixes the data
  contracts, the boundary functions (`detect`, `resolve`, `replace`, `restore`,
  `backends.complete`, `pipeline.mask`, `pipeline.protect_send_restore`), the
  configuration and every file format. `docs/evaluation_protocol.md` fixes the
  data and every reported number. Build exactly what they say. If one of them
  does not fit your task, or disagrees with a task or with the code, do not
  work around it and do not change it: describe the problem and stop. Where
  they are only silent on a detail (a rounding, a tie-break, an error
  message), choose the simplest option, say so in the hand-back and propose
  the line to add; stop only on a contradiction, or on a choice that would
  change what a reported number means.
- **One task = one branch = one pull request.** Branch names: `b1/…` to `b5/…`, and
  `fix/…`. The human creates the branch, commits, and merges
  once CI is green; the next block's owner reviews the whole block at the gate.
- **Before coding:** restate the task in two or three lines and name the files
  you will touch. If the task is ambiguous or conflicts with this file, ask.
- **Tests come with the code.** Every module has unit tests in `tests/`; a task
  is not done until `make test` and `make lint` pass locally. Report the actual
  output, including failures. Never weaken or delete a test to make it pass.
  A test that asserts "not built yet" is replaced by the task that builds the
  feature: that is a change of behaviour, not a weakened test.
- **When changing a signature, decorator or import, grep for every usage** and
  update callers in the same change (within your paths; report the others).
- **Environment:** Python 3.11, `uv` with `uv.lock`. Install only through `uv`,
  after checking that the project environment is the one in use
  (`uv run python --version`). New dependencies need the human's approval and a
  pinned version.
- **Small diffs.** Target under ~300 changed lines per pull request so a human can
  really review it (`uv.lock` and data files do not count). Split larger work.
- **Leave a review note** at the end of each task (your human pastes it in the
  pull request): what changed, how to verify it, what you are unsure about, and three
  questions a reviewer should be able to answer after reading the code. The
  last task of a block is its hand-over note in `docs/handoff/`: that is how
  the next owner learns what exists.
- **Log AI use.** Propose one line for `docs/ai_use.md`: date, human, task, what
  the agent produced, what the human changed. The human adds it; do not edit
  that file yourself, because all three members append to it.
- **Decisions** that alter behaviour or scope go in `docs/decisions.md`
  (date, decision, reason, who agreed). Propose the entry; the human adds it.

## 5. Who does what

| Block | Owner | Reviewed at the gate by | Paths |
|---|---|---|---|
| 1 · Skeleton | Mattia | Giuseppe and Andrea | everything in the pull request of `Step1`: `src/omissis/detect/` (`rules.py`, `merge.py`), `replace/placeholders.py`, `restore.py`, `backends/`, `resolve.py`, `pipeline.py`, `cli.py`, `eval/datasets.py`, `data/fixtures/`, `configs/skeleton.yaml`, `configs/models.echo.yaml`, `docs/annotation_guide.md`, their tests |
| 2 · Core completion | Giuseppe | Andrea | `src/omissis/contracts.py`, `config.py`, `vault.py`, `resolve.py`, `replace/`, `restore.py`, `backends/`, `pipeline.py`, `cli.py`, `app.py`; `configs/`; `.env.example`; `tests/core/`, `tests/app/` |
| 3 · Data and evaluation | Andrea | Mattia | `data/` except `fixtures/`; `src/omissis/eval/` (all of it, `datasets.py` included); `docs/annotation_guide.md`; `tests/eval/`, `tests/data/` |
| 4 · Detectors | Mattia | Giuseppe | `src/omissis/detect/`; `tests/detect/`; in `configs/eval.yaml`, only the two edits allowed by `docs/interfaces.md` section 4 |
| 5 · Closing | Giuseppe | Andrea and Mattia | `README.md`, `LICENSE`, `docs/cards.md` |

From gate G1, the files of block 1 belong to the block that lists them above:
the core modules to block 2, `eval/datasets.py` and the guide to block 3, the
detection modules to block 4. `data/fixtures/` belongs to nobody after G1.

Also:

- Every block owns its task list in `docs/tasks/` and its hand-over note in
  `docs/handoff/`. After G5 each member owns `docs/slides/<name>.md`.
- `results/` is written by blocks 2 to 5: each writes only the files its
  tasks name, and never deletes another block's files.
- `Makefile`: a block fills in its own targets (`demo` in block 2, `split` and
  `eval-*` in block 3, `reproduce` in block 5) and touches no other target.
- `pyproject.toml` and `uv.lock` change only when a human approves a new
  dependency, in the block that needs it. Blocks working in the same days may
  conflict on `uv.lock`: keep both dependencies in `pyproject.toml` and run
  `uv lock` again; never edit the lock by hand. The detectors' libraries go in
  a dependency group `detect` that `make setup` and CI do not install; the
  tests that need them use `pytest.importorskip`.
- `configs/models.yaml` is edited by humans only: pinning a model is a human
  commit to `main` with a line in `docs/decisions.md`, allowed until `freeze`.
- The example texts in `data/fixtures/` are read by every block's tests and
  edited by none after G1.

`results/cache/` is written by every block's runs; never delete or rewrite
cache files that your own run did not create. Only a run that a task asks for
writes there; every other run (trying the pipeline, the app or a detector)
uses a configuration whose `cache_dir` is under `results/scratch/`, which is
gitignored.

What no block lists (`.github/`, `.claude/`, `.gitignore`, `.gitattributes`,
the `setup`, `test`, `lint` and `format` targets, the pytest and ruff
settings) is changed by Giuseppe only, on request.

Agents do the compiling work: code, tests, first drafts of texts and docs.
Humans do the judging work: reviewing diffs, annotating and correcting data,
rating outputs, deciding scope, committing. Never present agent output as
human-verified.

## 6. Commands

```
make setup       # create the environment from uv.lock
make test        # unit and integration tests
make lint        # ruff check + ruff format --check
make format      # apply formatting
make demo        # Gradio app in replay mode (no network)
make split       # HUMANS ONLY: write data/dev and data/test, once
make eval-dev    # full evaluation on the dev split
make eval-test   # HUMANS ONLY, once, after the freeze
make reproduce   # rebuild every table and figure from the committed results
```

## 7. Calendar (worst case: presentation on Thu 26 Nov 2026)

| Block | Owner | Dates | Gate and tag |
|---|---|---|---|
| 0 · Foundation | Giuseppe | Wed 11 Nov | G0, done |
| 1 · Skeleton | Mattia | written; merged Mon 16 Nov | G1, `block-1`: reviewed, human checks done, merged |
| 2 · Core completion | Giuseppe | Mon 16 – Wed 18 Nov | G2, `block-2`: references from gold spans, real cloud model; interfaces frozen |
| 3 · Data and evaluation | Andrea | Thu 19 – Sun 22 Nov | G3, `block-3`: pilot decided, 66 texts split, chart for the references; protocol frozen |
| 4 · Detectors | Mattia | Tue 17 – Sun 22 Nov, beside 2 and 3; joined Mon 23 morning | G4, `freeze`: chart for every configuration on dev |
| 5 · Closing | Giuseppe | Mon 23 – Tue 24 Nov | G5, `v1.0`: `make eval-test` once; `make reproduce` from a clean clone |
| Presentation | all | Tue 24 – Wed 25 Nov | two timed rehearsals |

Workshop with the teaching team: Thu 19 Nov. The presentation date is not
known yet; the plan assumes the earliest one. After the `freeze`
tag only bug fixes that do not change evaluated behaviour are allowed.
