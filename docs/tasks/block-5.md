# Block 5 · Closing, and the presentation — task list

Owner of block 5: Giuseppe · Reviewed by: Andrea and Mattia · Mon 23 – Tue 24 Nov
How to use this file: `docs/tasks/README.md`. Start from the hand-over notes in
`docs/handoff/`.

After the `freeze` tag nothing that changes evaluated behaviour may be merged.

- [ ] **5.1 · Final evaluation and results**
  - **Human:** the three members launch `make eval-test` together, once, on
    the reference machine, after `make eval-dev` there has reproduced the
    committed dev results. A launch that stops half-way is resumed as the
    protocol says in section 4.
  - **Human:** if the judge was rejected at G3, the three members score the
    fallback items of the protocol, section 9, with the sheet tool of task 3.7,
    before any result is reported.
  - Do: chart and scorecard (detection and latency table included) from the
    metrics files, error taxonomy from `results/dev/error_examples.md` and the
    counts of task 4.5; every statement limited to what the decision rule of
    the protocol, section 12, supports; `docs/cards.md` with one entry per model and dataset
    (source, revision, licence, how we use it), starting from the lines the
    other owners proposed in their hand-over notes.
  - **Human:** check every headline number against `results/<split>/metrics/`.

- [ ] **5.2 · Reproducibility and README** — `Makefile`, `README.md`, `LICENSE`
  - Do: `make reproduce` recomputes every estimate, interval, table and figure
    from the per-text outcomes in the committed `results/<split>/metrics/`,
    with no network, no model, no detector and without reading `data/test/`
    (the target calls the command that task 3.10 provides); README with quick
    start,
    architecture, results chart, limitations (threat model, pseudonymisation
    is not anonymisation, derived values, synthetic data only) and licence.
  - Done when: the command runs with the network disabled.
  - **Human:** confirm the licences (default: MIT for code, CC BY 4.0 for the
    synthetic data); clean-clone check on a second machine; set the tag
    `v1.0`; G5 is ticked.

## Presentation · Tue 24 – Wed 25 Nov

These tasks are open to all three agents after G5. Each member's agent drafts
content for that member's part in `docs/slides/<name>.md`; every number comes
from `results/<split>/metrics/`. The drafts are a support: the humans write the slides.

- [ ] **P.1 · Giuseppe** — problem, existing tools, architecture and the
  design choices of the core; the demo with the app in replay mode, at most
  90 seconds; conclusions. **Human:** after G4, on the reference machine, run
  the fixtures of the demo once through `omissis run --backend cloud`, on a
  configuration whose `cache_dir` is `results/cache`, with the task text the
  app sends, for the combinations shown, and commit the cache (replay needs
  it; the laptop of the demo needs the `detect` group and the D2 weights to
  show D1, D2 or D4); run the demo offline before each rehearsal.
- [ ] **P.2 · Andrea** — evaluation design, the chart, what did not work,
  limits; backup slides (annotation agreement, judge validation, attack
  design, cost).
- [ ] **P.3 · Mattia** — the five detectors and what each finds and misses;
  backup slide with per-type detection.
- **Human:** write the final slides; two timed rehearsals, all three.
