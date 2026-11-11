# Task lists

One ordered list per workstream. This is what an agent works from when its
human says "start" or "continue".

## For agents

The specification is in two documents: `docs/interfaces.md` (data contracts,
boundary functions, configuration, file formats) and
`docs/evaluation_protocol.md` (data and every reported number). A task says
what to build and when it is finished; the two documents say exactly how it
must behave. If a task and a specification disagree, stop and ask.

1. Open the list of your workstream (your personal file says which).
2. Take the first task of the current step whose box is unticked and whose
   *Blocked by* line is cleared. The current step is the first one whose gate
   is unticked in the table below. A blocker is cleared when the named task is ticked in its own list,
   or when the named decision appears in `docs/decisions.md` or in
   `configs/models.yaml`. If you cannot tell, ask your human.
3. Restate the task and the files you will touch, then wait for the go-ahead
   only if something is ambiguous; otherwise proceed.
4. Work until every *Done when* line is true. Run `make test` and `make lint`.
5. Hand back as described in your personal file. Do not tick the box: your
   human ticks it when the pull request is merged.
6. One task = one branch = one pull request. If a task grows beyond about 300
   changed lines, propose a split before continuing.

A line starting with **Human:** is a decision or a check that only a person
can make. Stop there and ask; never fill it in yourself.

If every remaining task is blocked, say which blockers are open and stop.

## Steps and gates

The project is built in steps. Each step ends with a gate: a check that the
humans do together and tick here. No task of a later step starts before the
gate of the current one is ticked.

| Step | Tasks | Gate (ticked by the humans) |
|---|---|---|
| 0 · Foundation | B0 | - [x] **G0** — the three members have read `contracts.py` and the stubs together; `make test` and `make lint` pass on each member's machine |
| 1 · Skeleton | A1, A2, B1, B2, B3, B4, C1 | - [ ] **G1** — `omissis run --config configs/skeleton.yaml` takes a fixture email through D0 → R1 → `echo` → restore on each member's machine, and again from the cache with `backend: replay`. No real model is needed for this step. `docs/interfaces.md` is frozen from here |
| 2 · Second detector and pilot | A3, A4, A5, B11, B5, C2, C3, C4, C5, C9 | - [ ] **G2** — pilot go/no-go recorded in `docs/decisions.md`. `docs/evaluation_protocol.md` is frozen from here |
| 3 · Full system | A6, A7, A8, A9, B6, B7, B8, C6, C7, C8, C10 | - [ ] **G3** — `make eval-dev` produces chart and scorecard on dev; the app runs in replay mode; freeze tag set |
| 4 · Results | A10, B9, C11 | - [ ] **G4** — `make eval-test` run once; `make reproduce` works from a clean clone |
| 5 · Presentation | A11, B10, C12 | two timed rehearsals |

Steps 0 to 5 correspond to milestones M0 to M6 in `CLAUDE.md` (step 4 covers
M4 and M5). Inside a step, tasks of different workstreams run in parallel.

## For humans

- Tick a box (`- [x]`) only after the pull request is merged.
- If a task turns out to be wrong or too big, edit it here in a commit of its
  own, and tell the others.
- The lists follow the milestones in `CLAUDE.md`, section 7.
