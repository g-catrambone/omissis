# Block 1 · Skeleton — review and merge

Owner: Mattia · Reviewed by: Giuseppe and Andrea · Mon 16 Nov
How to use this file: `docs/tasks/README.md`.

The code of this block is already written, on the branch `Step1` (one commit,
about 3,000 lines): D0 rules, span merging and `detect` for D0, R1
placeholders, restore (exact and normalised), JSONL cache with replay and the
`echo` provider, an interim entity resolver, `mask` and `protect_send_restore`,
the `omissis` command line, five fixture emails, the loaders in
`src/omissis/eval/datasets.py`, the annotation guide v0. It was written under
the earlier plan and is accepted as it is: one large pull request is a declared
exception to the 300-line rule (`docs/decisions.md`).

What remains is checking and merging.

- [ ] **1.1 · Pull request**
  - **Human (Mattia):** open the pull request from `Step1` to `main`; CI must
    be green.

- [ ] **1.2 · Human checks left open by the commit**
  - **Human (Mattia):** check two D0 validators by hand against the official
    algorithm; confirm that bank code `00000` is not assigned to a real bank,
    and that the partita IVA and phone values in the tests, the fixtures and
    the guide belong to nobody (note in `docs/decisions.md` how they were
    chosen).
  - **Human (Giuseppe):** run the five fixtures and read what is sent to the
    provider: no detected value may appear in it.
  - **Human (Andrea):** confirm the five emails read like real correspondence
    and contain nothing real; read the annotation guide and note what to
    change (it is revised in task 3.1).

- [ ] **1.3 · Reading**
  - **Human (Giuseppe):** read `replace/placeholders.py`, `restore.py`,
    `backends/__init__.py`, `pipeline.py`, `cli.py`: block 2 builds on them.
  - **Human (Andrea):** read `eval/datasets.py` and the fixtures: block 3
    builds on them.
  - Each agent may help its human by answering questions on the code. It
    changes nothing.

- [ ] **1.4 · Hand-over note and fixture corrections** — `docs/handoff/block-1.md`, `data/fixtures/`, `docs/annotation_guide.md`
  - Do (Mattia's agent, on a branch `b1/handover`): the note described in
    `docs/tasks/README.md`, with one worked call for `detect`, `mask`,
    `protect_send_restore`, `complete`, `load_texts`, and the two commands.
  - Do (same branch): three corrections to the fixtures found in the review,
    the last changes before they are frozen. In `fx-hr-02.json` add the span
    `CITTA` 49–56 ("Bologna" in the subject line). In `fx-hr-01.json` the span
    496–525 `STRUTTURA` "poliambulatorio di Pomigliano" becomes `CITTA` 515–525
    "Pomigliano", as in the six other "facility of a city" cases, and the three
    places of `docs/annotation_guide.md` that depend on it are aligned: the
    type table and edge case 3, which give that span as a `STRUTTURA` example,
    and the pointer "(see 4.3)" in section 1, which would otherwise cite a
    rule that now says the opposite. In
    `fx-bank-01.json` `gold.deadline` becomes `null`: 1 December 2026 is when
    the salary changes account, not a date by which the bank is asked to act.
    `make test` must pass.
  - **Human (Mattia):** merge the pull request of this task; set the tag
    `block-1`; G1 is ticked.
