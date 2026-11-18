# Block 3 · Data and evaluation — task list

Owner: Andrea · Reviewed at the gate by: Mattia · Thu 19 – Sun 22 Nov
How to use this file: `docs/tasks/README.md`. Specification:
`docs/evaluation_protocol.md` (every definition, count and threshold) and
`docs/interfaces.md` section 5 (file formats). Start from
`docs/handoff/block-1.md` and `block-2.md`.

This block builds the data and the whole measuring apparatus, and runs it on
the three reference configurations of `configs/eval.yaml`, which need no
detector: `REF-none`, `REF-oracle-direct`, `REF-oracle`. The evaluation calls
`omissis.eval.datasets`, `pipeline.mask`, `pipeline.protect_send_restore`,
`backends.complete` and `detect`, nothing below them. The detectors of block 4
arrive in `main` during these days: the evaluation must pick them up with no
code change.

- [ ] **3.1 · Annotation guide and profiles** — `docs/annotation_guide.md`, `data/profiles/`, `eval/profiles.py`
  - Do: revise the guide v0 (classes, types, span boundaries, edge cases,
    worked examples) so that it matches the protocol, section 3, and the five
    fixtures; profiles and candidate lists exactly as in the protocol, section
    1, with names, cities and employers disjoint from the lists in
    `src/omissis/replace/data/`.
  - Also: a seeded plan `data/profiles/plan.json` (`docs/interfaces.md`,
    section 5), from which the generator, the candidate lists and `make split`
    work. In the guide: a facility named by a common noun and a city is tagged
    as the city (`STRUTTURA` only with a proper name); `gold.dates` lists only
    dates with day, month and year; `deadline` is a date by which the
    recipient is asked to act; a rule for the email that seems to ask for two
    actions; the amount and date formats allowed in the texts, which the T3
    scorer must accept. The old task ids in `docs/annotation_guide.md`,
    `src/omissis/eval/datasets.py` and `tests/data/` are replaced (task 2.1
    leaves them to this block: `C1` becomes "block 1"); `load_texts` raises
    `DataError` on a missing or empty folder.
  - Done when: tests assert the cohort rule, list sizes, presence of the true
    author, determinism for the seed, and the disjointness.
  - **Human:** rewrite the guide's edge cases in your own words; approve the
    name, city and employer lists of the profiles.

- [ ] **3.2 · Text generator and pilot texts** — `eval/textgen.py`, `data/pool/`
  - Do: prompt writing an Italian email from one profile and one scenario with
    spans marked `[[TYPE|text]]`, which also returns the gold fields; parser
    that strips the tags and computes offsets, and its inverse, which writes
    a text record back as tagged text, so that texts are reviewed and
    corrected as tagged text and never as offsets in JSON; the scenarios,
    counts and text requirements of the protocol, section 2; 10 pilot texts
    from 2 cohorts.
  - Done when: parser tests cover nested-looking brackets, unknown types and
    adjacent tags; the 10 texts load with `load_texts`; a check run on every
    generated text reports each occurrence of an annotated string that lies
    outside a span, so that the reviewer tags it or accepts it.
  - **Human:** approve the prompt; review the 10 pilot texts with that tool (a
    first check: the review that sets `reviewed_by` is part of task 3.5).

- [ ] **3.3 · The two attacks** — `eval/attacks.py`
  - Do: both attacks exactly as in the protocol, section 7. Their input is
    the masked-batch files written by `omissis mask`.
  - Done when: scoring is tested with a fake provider; the call count and
    estimated cost are printed before any real batch.
  - **Human:** read and approve both prompts.

- [ ] **3.4 · Pilot**
  - Do: both attacks on the 10 pilot texts for `REF-none`,
    `REF-oracle-direct` and `REF-oracle`; a one-page note in `results/pilot/`.
  - **Human:** go or no-go with the team (fifteen minutes, all three), by the
    pilot rule of the protocol, section 2. Record the decision and the three
    numbers in `docs/decisions.md`. On no-go, change profiles and scenarios and
    repeat before writing more texts.

- [ ] **3.5 · Full dataset and split** — `data/pool/`, `make split`
  - Do: the remaining texts up to 66; `data/pool/REVIEWERS.md` assigning 22
    texts to each member by seed, and the second annotators of the 13
    double-annotation texts; the export of those 13 as plain text and the
    import of the annotated copies; the agreement script; `make split` as in
    section 4, refusing texts without `reviewed_by`. Reviewers correct tags in
    text with the export and import of task 3.2, never offsets in JSON
    (`docs/tasks/README.md` says how their agents may help). All as in the
    protocol, section 3.
  - **Human:** the 13 texts are annotated a second time first, before any
    review pull request is opened; then each member reviews 22 texts on a
    branch `b3/review-<initials>` and opens one pull request, which Andrea
    merges; the agreement script is run before any adjudication changes the
    pool; then disagreements are adjudicated and Andrea runs `make split`.
    After that no agent opens `data/test/`.

- [ ] **3.6 · Utility tasks** — `eval/utility.py`
  - Do: T3 and T1 exactly as in the protocol, section 8.
  - Done when: scoring tests cover equal values in different formats and
    missing fields.
  - **Human:** read and approve the T3 and T1 prompts.

- [ ] **3.7 · Judge and its validation** — `eval/judge.py`
  - Do: the judge, the rating-sheet tool and the acceptance computation exactly
    as in the protocol, section 9. The sheet tool takes a split and the
    configurations to rate, so that it also serves the fallback of task 5.1.
    The R2 items of the validation come from `REF-oracle` with `strategy`
    overridden to `R2` (`with_overrides`), as the protocol says: nothing is
    added to `configs/eval.yaml`.
  - **Human:** read and approve the judge prompt. Giuseppe and Mattia fill
    their sheets and send them privately to Andrea, who commits both together
    and records the outcome in `docs/decisions.md`.

- [ ] **3.8 · Statistics** — `eval/stats.py`
  - Do: the procedures of the protocol, section 12.
  - Done when: tests compare against hand-computed or textbook values.

- [ ] **3.9 · Detection metrics and latency** — `eval/detection.py`
  - Blocked by: task 4.0 merged (`omissis.detect.supported_detectors` exists).
  - Do: `run(split, config)`, which for every detector listed by
    `omissis.detect.supported_detectors()` writes the detected spans to
    `results/<split>/detected/`, then the detection metrics of the protocol,
    section 6, to `results/<split>/metrics/detection.json`. It never deletes
    the files of a detector it did not run. A separate command, which
    `make eval-dev` never calls, runs the timing pass: each detector once per
    dev text, each with its own empty cache under `results/scratch/`, so that
    no LLM call is answered from the cache; it writes p50 and p95 per
    detector, the per-text times and the machine name to
    `results/dev/metrics/latency.json`. The official file is written in task
    4.5, on the reference machine.
  - Done when: hand-computed toy cases give the expected numbers, including a
    text with zero gold spans and a detector with zero predictions; the
    metrics can be recomputed from `results/<split>/detected/` without running
    a detector; the tests fake `supported_detectors` and `detect`, and never
    rely on a real detector being absent; it runs on dev for D0 (D1 to D4 are
    run in task 4.5, on the reference machine).

- [ ] **3.10 · Evaluation runner and report** — `eval/run.py`, `eval/report.py`, `make eval-dev`, `make eval-test`
  - Do: one runner that evaluates the configurations of `configs/eval.yaml`
    (read with `load_eval_configs`; now the three references, block 4 appends
    four), runs the detection evaluation, and writes the metrics files; chart
    and scorecard as in the protocol, sections 10 to 13; `make eval-test`
    refusing a second run and writing the access log.
  - Also: every metrics file carries the per-text outcomes (`per_text`,
    `docs/interfaces.md` section 5), and one command of the report module
    rebuilds rows, scorecard and chart from those files alone: it is what
    `make reproduce` calls in task 5.2. `make eval-test` counts as run once
    its last metrics file is written, a launch that stops earlier resumes
    from the cache, and every launch is logged (protocol, section 4). The
    runner stops with a clear message when a configuration's detector is not
    in `supported_detectors()` on that machine, and on a `CacheMissError` or
    `ConfigError`, instead of scoring the text as if nothing had been found.
  - **Human:** approve the plotting dependency.
  - Done when: `make eval-dev` produces chart and scorecard on dev for the
    three references; rebuilding from `results/dev/metrics/` alone gives the
    same rows; a test with fake providers and fake detectors shows that
    adding a configuration to the file needs no code change; `results/cache/`
    and `results/dev/` are committed.

- [ ] **3.11 · Hand-over note** — `docs/handoff/block-3.md`
  - Do: the note described in `docs/tasks/README.md`: how to load dev texts
    with gold spans, how to add a configuration and run the evaluation, what
    the pilot showed, the state of the judge, the LLM spend so far; the
    `docs/cards.md` lines proposed for the dataset.
  - **Human:** set the tag `block-3`; Mattia reads the note and the code, and
    G3 is ticked.
