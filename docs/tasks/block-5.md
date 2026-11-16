# Block 5 · Closing, and the presentation — task list

Owner of block 5: Giuseppe · Reviewed by: Andrea and Mattia · Mon 23 – Tue 24 Nov
How to use this file: `docs/tasks/README.md`. Start from the hand-over notes in
`docs/handoff/`.

After the `freeze` tag nothing that changes evaluated behaviour may be merged.

- [ ] **5.1 · Final evaluation and results**
  - **Human:** the three members launch `make eval-test` together, once.
  - **Human:** if the judge was rejected at G3, the three members score the 92
    fallback items of the protocol, section 9, with the sheet tool of task 3.7,
    before any result is reported.
  - Do: chart, scorecard (detection and latency columns included) and error
    taxonomy from the metrics files; every statement limited to what the
    intervals support; `docs/cards.md` with one entry per model and dataset
    (source, revision, licence, how we use it), starting from the lines the
    other owners proposed in their hand-over notes.
  - **Human:** check every headline number against `results/metrics/`.

- [ ] **5.2 · Reproducibility and README** — `Makefile`, `README.md`, `LICENSE`
  - Do: `make reproduce` rebuilds every metric, table and figure from the
    committed `results/cache/`, `results/masked/` and `results/detected/`, with
    no network, no model and no detector; README with quick start,
    architecture, results chart, limitations (threat model, pseudonymisation
    is not anonymisation, derived values, synthetic data only) and licence.
  - Done when: the command runs with the network disabled.
  - **Human:** confirm the licences (default: MIT for code, CC BY 4.0 for the
    synthetic data); clean-clone check on a second machine; set the tag
    `v1.0`; G5 is ticked.

## Presentation · Tue 24 – Wed 25 Nov

These tasks are open to all three agents after G5. Each member's agent drafts
content for that member's part in `docs/slides/<name>.md`; every number comes
from `results/metrics/`. The drafts are a support: the humans write the slides.

- [ ] **P.1 · Giuseppe** — problem, existing tools, architecture and the
  design choices of the core; the demo with the app in replay mode, at most
  90 seconds; conclusions. **Human:** run the demo offline before each rehearsal.
- [ ] **P.2 · Andrea** — evaluation design, the chart, what did not work,
  limits; backup slides (annotation agreement, judge validation, attack
  design, cost).
- [ ] **P.3 · Mattia** — the five detectors and what each finds and misses;
  backup slide with per-type detection.
- **Human:** write the final slides; two timed rehearsals, all three.
