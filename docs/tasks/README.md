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
  green; the three human checks of `block-1.md` are done; Giuseppe has read
  the core modules and Andrea the fixtures, the loaders and the guide; on each
  member's machine `uv run omissis run --config configs/skeleton.yaml --input
  data/fixtures/fx-bank-01.json` works, and again with `--backend replay`.
- [ ] **G2** (tag `block-2`) — every fixture goes through the three reference
  configurations of `configs/eval.yaml`; the five fixtures have been sent once
  to the real cloud model with R1 and once with R2; the models for `cloud`,
  `generator`, `attacker` and `judge` are pinned; `docs/handoff/block-2.md`
  exists; Andrea has read it and the block's code. `docs/interfaces.md` is
  frozen from here.
- [ ] **G3** (tag `block-3`) — pilot go/no-go recorded in `docs/decisions.md`;
  66 texts reviewed and split; judge validation outcome recorded in
  `docs/decisions.md`; `make eval-dev` produces chart and scorecard for the
  three references and the detection metrics for every detector merged so far;
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

## For agents

The specification is in two documents: `docs/interfaces.md` (data contracts,
boundary functions, configuration, file formats) and
`docs/evaluation_protocol.md` (data and every reported number). A task says
what to build and when it is finished; the two documents say exactly how it
must behave. If a task and a specification disagree, stop and ask.

1. Your personal file says which blocks are yours. If the gate your block
   waits for is not ticked, or your block's own gate is already ticked, there
   is no block task for you: say so and stop. Do not work on another block's
   tasks. Two things remain possible outside your turn, when your human asks:
   a `fix/…` branch in your own block's code (see below), and, after G5, your
   presentation task.
2. At the start of your block, read the hand-over notes of the earlier blocks
   in `docs/handoff/`.
3. Take the first unticked task of your block. Tasks inside a block are in
   order: each one may rely on the ones above it.
4. Restate the task and the files you will touch. Ask only if something is
   ambiguous; otherwise proceed.
5. Work until every *Done when* line is true. Run `make test` and `make lint`.
6. Hand back as described in your personal file. Do not tick the box: your
   human ticks it when the pull request is merged.
7. One task = one branch = one pull request. If a task grows beyond about 300
   changed lines, propose a split before continuing.
8. The last task of every block is the hand-over note. Write it for someone
   who has not seen your code: what exists, how to call it with one worked
   example per call, what is not done, known limits, and five questions the
   next owner should be able to answer.

A line starting with **Human:** is a decision or a check that only a person
can make. Stop there and ask; never fill it in yourself.

**A bug in another block.** If your task is blocked by a defect in code of
another block, do not change that code. Describe the defect and the smallest
fix, and stop. Your human passes it to the owner of that block, who writes the
fix with their agent on a branch `fix/…`; you review it.

**Working beside another block.** Blocks 2 and 3 on one side and block 4 on
the other are merged into `main` in the same days. They share two files:
`pyproject.toml` and `uv.lock`. When a new dependency is approved, add it to
`pyproject.toml` and run `uv lock`; if `uv.lock` conflicts on merge, keep both
dependencies in `pyproject.toml` and run `uv lock` again, never edit the lock
by hand.

## For humans

- During your block you merge your own pull requests once CI is green and you
  have read the diff. The next owner reviews the whole block at the gate.
- Before each task: `git switch main && git pull`, then a new branch.
- Tick a task (`- [x]`) after its pull request is merged. Ticks, gate ticks and
  register lines may be committed directly to `main`.
- Pinning a model is a human edit of `configs/models.yaml`, committed directly
  to `main` with a line in `docs/decisions.md`. It is allowed at any time until
  the `freeze` tag, whoever's turn it is.
- If a task turns out to be wrong or too big, edit it here in a commit of its
  own, and tell the others.
- Shared human work that no block can absorb: reviewing 22 texts each and the
  double annotation (block 3), two raters for the judge (block 3), launching
  the final evaluation together and, if the judge was rejected, the 92 fallback
  ratings (block 5), slides and rehearsals.
- If a block is late, cut inside it instead of moving the dates. Order of the
  cuts: the app; R2 and fuzzy restore; D3 and therefore D4; the judge and the
  reply draft, keeping extraction only. Record every cut in `docs/decisions.md`.
