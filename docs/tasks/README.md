# Task lists

The project is built as a relay of blocks, each with one owner who works on it
alone with their agent. Blocks 1, 2, 3 and 5 follow one another. Block 4 (the
detectors) runs beside blocks 2 and 3: it plugs into the rest at one point
only, the `detect` function, so it needs no coordination until it is joined to
the evaluation. This is what an agent works from when its human says "start"
or "continue".

| Block | Owner | Dates (worst case) | Content | List |
|---|---|---|---|---|
| 0 · Foundation | Giuseppe | done | scaffold, contracts, boundary stubs | — |
| 1 · Skeleton | Mattia | written; review and merge Mon 16 Nov | D0 rules, span merging, R1, restore, cache and `echo`, pipeline, command line, fixtures, loaders, annotation guide v0 | `block-1.md` |
| 2 · Core completion | Giuseppe | Mon 16 – Wed 18 Nov | references from gold spans, named configurations, entity resolver, cloud provider, R2, fuzzy restore, app | `block-2.md` |
| 3 · Data and evaluation | Andrea | Thu 19 – Sun 22 Nov | profiles, texts, attacks, pilot, utility, judge, statistics, detection metrics, report | `block-3.md` |
| 4 · Detectors | Mattia | Tue 17 – Sun 22 Nov, beside blocks 2 and 3; joined Mon 23 morning | D1 Presidio, D2 classifier, D3 local LLM, D4 hybrid; full evaluation on dev | `block-4.md` |
| 5 · Closing | Giuseppe | Mon 23 – Tue 24 Nov | final evaluation, results, reproducibility, README | `block-5.md` |
| Presentation | all three | Tue 24 – Wed 25 Nov | slides, demo, two rehearsals | `block-5.md`, last section |

## Gates

A block ends with a gate: checks that the humans do and tick here. At a gate
the owner sets a git tag.

- [x] **G0** — foundation read by the three members; tests pass on each machine.
- [ ] **G1** (tag `block-1`) — the pull request of block 1 is merged with CI
  green; the three human checks of `block-1.md` are done; task 1.4 (the
  hand-over note and the fixture corrections) is merged; Giuseppe has read
  the core modules and Andrea the fixtures, the loaders and the guide; on each
  member's machine `uv run omissis run --config configs/skeleton.yaml --input
  data/fixtures/fx-bank-01.json` works, and again with `--backend replay`. Each
  member then deletes the local `results/` folder the command created: nothing
  in it is committed.
- [ ] **G2** (tag `block-2`) — every fixture goes through the three reference
  configurations of `configs/eval.yaml`; the five fixtures have been sent once
  to the real cloud model with R1 and once with R2; the models for `cloud`,
  `generator`, `attacker` and `judge` are pinned; `docs/handoff/block-2.md`
  exists; Andrea has read it and the block's code. `docs/interfaces.md` is
  frozen from here. The app (task 2.7) is not a condition of this gate.
- [ ] **G3** (tag `block-3`) — pilot go/no-go recorded in `docs/decisions.md`;
  66 texts reviewed and split; judge validation outcome recorded in
  `docs/decisions.md`; `make eval-dev` produces chart and scorecard for the
  three references and the detection metrics for D0 (D1 to D4 are measured in
  task 4.5, on the reference machine);
  `docs/handoff/block-3.md` exists; Mattia has read it and the block's code.
  `docs/evaluation_protocol.md` is frozen from here.
- [ ] **G4** (tag `freeze`) — D1, D2, D3 and D4 are merged; the four
  configurations with detectors are in `configs/eval.yaml`; `make eval-dev`
  produces chart and scorecard for every configuration; `docs/handoff/block-4.md`
  exists; Giuseppe has read it and the block's code. Design freeze: after this
  only bug fixes that do not change evaluated behaviour.
- [ ] **G5** (tag `v1.0`) — `make eval-test` run once by the three members
  together; `make reproduce` rebuilds every table and figure from the committed
  `results/` on a clean clone on a second machine, with no network.

Block 2 starts after G1; block 3 after G2; block 5 after G3 and G4. Block 4
starts after G1 and does not wait for G2 or G3, except its last task (4.5),
which needs G3.

A few exceptions keep everyone working.

- Task 2.1 does not wait for G1: the pull request of block 1 is merged, and the
  task changes no behaviour and needs no hand-over note.
- Three tasks of block 3 may start after G1, while block 2 is running, when
  Andrea names one: 3.8 (statistics), the code and tests of 3.9 (detection
  metrics, on the fixtures; after task 4.0 is merged) and the guide half of
  3.1 (its edits to `docs/annotation_guide.md`, `src/omissis/eval/datasets.py`
  and `tests/data/`).
- Task 2.7 (the app) may be finished after G2 and until the `freeze` tag,
  beside block 3: it touches only `app.py`, `tests/app/`, the `demo` target
  and, for its dependency, `pyproject.toml` and `uv.lock`.
- During the review of task 3.5 each agent may run the export and import tool
  of task 3.2 on its human's 22 pool texts, on the review branch. The import
  never writes `reviewed_by`: the human adds it by hand.

## For agents

The specification is in two documents: `docs/interfaces.md` (data contracts,
boundary functions, configuration, file formats) and
`docs/evaluation_protocol.md` (data and every reported number). A task says
what to build and when it is finished; the two documents say exactly how it
must behave. If a task and a specification disagree, stop and ask. If they are
only silent on a detail, choose the simplest option, say so in the hand-back
and propose the line to add.

1. Your personal file says which blocks are yours. If the gate your block
   waits for is not ticked, or your block's own gate is already ticked, there
   is no block task for you, unless one of the exceptions above applies.
   Otherwise say so and stop, after listing what waits on your human: every
   **Human** line of an unticked task, in any task list, that names your human
   or the three members; every bare **Human:** line of your own block's list;
   every gate that waits on your human's reading. Do not work on another
   block's tasks. Two things remain possible outside your
   turn, when your human asks: a `fix/…` branch in your own block's code (see
   below), and, after G5, your presentation task.
2. At the start of your block, read the hand-over notes of the earlier blocks
   in `docs/handoff/`.
3. Take the first unticked task of your block that has a *Do* line and whose
   own work is not merged yet. A task that waits only for a **Human:** line is
   reported as open, not redone. Tasks inside a block are in order: each one
   may rely on the ones above it. If the task has a *Blocked by* line that is
   not satisfied, say what is missing, do the part of the task that does not
   need it (code and tests on fakes) and stop: your human provides it, or
   names another task whose inputs are ready.
4. Restate the task and the files you will touch. Ask only if something is
   ambiguous; otherwise proceed.
5. Work until every *Done when* line is true. Run `make test` and `make lint`.
6. Hand back as described in your personal file. Do not tick the box: your
   human does.
7. One task = one branch = one pull request. If a task grows beyond about 300
   changed lines, propose a split before continuing.
8. The last task of every block is the hand-over note. Write it for someone
   who has not seen your code: what exists, how to call it with one worked
   example per call, what is not done, known limits, and five questions the
   next owner should be able to answer.

A line starting with **Human:** is a decision or a check that only a person
can make: never fill it in yourself. It blocks only what depends on it: finish
the rest of the task and hand back with the line listed as open; your human may
then start you on the next task whose inputs are ready. A task is ticked, and a
gate is ticked, only when its **Human:** lines are done. A check the team
decides to skip is recorded in `docs/decisions.md`, never left silent.

**A bug in another block.** If your task is blocked by a defect in code of
another block, do not change that code. Describe the defect and the smallest
fix, and stop. Your human passes it to the owner of that block, who writes the
fix with their agent on a branch `fix/…`; you review it.

**Working beside another block.** Blocks 2 and 3 on one side and block 4 on
the other are merged into `main` in the same days. They share two files:
`pyproject.toml` and `uv.lock`. When a new dependency is approved, add it to
`pyproject.toml` and run `uv lock`; if `uv.lock` conflicts on merge, keep both
dependencies in `pyproject.toml` and run `uv lock` again, never edit the lock
by hand. The detectors' libraries go in a dependency group `detect`, installed
only where the detectors run (`uv sync --locked --group detect`, to be run
again after any `make setup`, which removes the group): `make setup` and CI do
not install it, and the tests that need it use `pytest.importorskip`.
The files in `results/cache/` are append-only and written on several machines:
only a run that a task asks for writes there, on that task's branch; any other
run uses a `cache_dir` under `results/scratch/`, which is gitignored. If a
pull request conflicts on a cache file, the human merges `main` into the
branch locally, where `.gitattributes` keeps the lines of both sides, and
pushes.

## For humans

- First time on this repository: clone it, run `make setup` and `make test`,
  and create `CLAUDE.local.md` in the repository root with the single line
  `@docs/agents/<your name>.md` (the file is gitignored). Set `git config
  user.name` and `user.email` to your GitHub identity, so that your commits
  count as yours. Start your agent from the repository root. When it asks to
  run a git command, answer for that command only: never "don't ask again".
- Decisions the tasks wait for: the API key and the models for `cloud`,
  `generator`, `attacker` and `judge` by Tue 17 (task 2.4); `d2` by Tue 17
  (task 4.2); `d3` and the reference machine by Thu 19 (task 4.3). The
  generator must differ from `d3` and from the attacker. There is one
  reference machine: the official D3 runs, task 4.5 and `make eval-test` all
  run on it.
- During your block you merge your own pull requests once CI is green and you
  have read the diff. The next owner reviews the whole block at the gate.
- Before each task: `git switch main && git pull`, then a new branch.
- Tick a task (`- [x]`) after its pull request is merged and its **Human:**
  lines are done. Ticks, gate ticks and
  the lines of `docs/ai_use.md` and `docs/decisions.md` are always committed
  directly to `main`, never inside a task's pull request: two branches that
  append to the same table conflict.
- Pinning a model is a human edit of `configs/models.yaml`, committed directly
  to `main` with a line in `docs/decisions.md`. It is allowed at any time until
  the `freeze` tag, whoever's turn it is, but not before task 2.1 is merged
  (until then a test reads `configs/models.yaml` and a pin would turn CI
  red). Every pin changes the run id of every
  configuration, so pin the six roles in as few sittings as possible; a role
  already used in committed results is re-pinned only by a decision of all
  three, followed by a new `make eval-dev` (the unchanged calls come from the
  cache).
- If a task turns out to be wrong or too big, edit it here in a commit of its
  own, and tell the others.
- Shared human work that no block can absorb: reviewing 22 texts each and the
  double annotation (block 3), two raters for the judge (block 3), launching
  the final evaluation together and, if the judge was rejected, the fallback
  ratings (block 5), slides and rehearsals.
- If a block is late, cut inside it instead of moving the dates. Order of the
  cuts: the app; R2 and fuzzy restore; D3 and therefore D4; the judge and the
  reply draft, keeping extraction only. Record every cut in `docs/decisions.md`.
