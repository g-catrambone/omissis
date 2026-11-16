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
  - Done when: tests assert the cohort rule, list sizes, presence of the true
    author, determinism for the seed, and the disjointness.
  - **Human:** rewrite the guide's edge cases in your own words.

- [ ] **3.2 · Text generator and pilot texts** — `eval/textgen.py`, `data/pool/`
  - Do: prompt writing an Italian email from one profile and one scenario with
    spans marked `[[TYPE|text]]`; parser that strips the tags and computes
    offsets; the scenarios, counts and text requirements of the protocol,
    section 2; 10 pilot texts from 2 cohorts.
  - Done when: parser tests cover nested-looking brackets, unknown types and
    adjacent tags; the 10 texts load with `load_texts`.
  - **Human:** approve the prompt; review the 10 pilot texts.

- [ ] **3.3 · The two attacks** — `eval/attacks.py`
  - Do: both attacks exactly as in the protocol, section 7. Their input is
    the masked-batch files written by `omissis mask`.
  - Done when: scoring is tested with a fake provider; the call count and
    estimated cost are printed before any real batch.
  - **Human:** read and approve both prompts.

- [ ] **3.4 · Pilot**
  - Do: both attacks on the 10 pilot texts for `REF-none`,
    `REF-oracle-direct` and `REF-oracle`; a one-page note in `results/`.
  - **Human:** go or no-go with the team (fifteen minutes, all three), by the
    pilot rule of the protocol, section 2. Record the decision and the three
    numbers in `docs/decisions.md`. On no-go, change profiles and scenarios and
    repeat before writing more texts.

- [ ] **3.5 · Full dataset and split** — `data/pool/`, `make split`
  - Do: the remaining texts up to 66; `data/pool/REVIEWERS.md` assigning 22
    texts to each member by seed; the export of the 13 double-annotation texts
    as plain text and the import of the annotated copies; the agreement
    script; `make split` as in section 4, refusing texts without
    `reviewed_by`. All as in the protocol, section 3.
  - **Human:** each member reviews 22 texts on a branch `b3/review-<initials>`
    and opens one pull request, which Andrea merges; 13 texts are annotated
    twice; disagreements are adjudicated; Andrea runs `make split`. After that
    no agent opens `data/test/`.

- [ ] **3.6 · Utility tasks** — `eval/utility.py`
  - Do: T3 and T1 exactly as in the protocol, section 8.
  - Done when: scoring tests cover equal values in different formats and
    missing fields.
  - **Human:** read and approve the T3 and T1 prompts.

- [ ] **3.7 · Judge and its validation** — `eval/judge.py`
  - Do: the judge, the rating-sheet tool and the acceptance computation exactly
    as in the protocol, section 9. The sheet tool takes a split and two
    configuration names, so that it also serves the fallback of task 5.1.
  - **Human:** read and approve the judge prompt. Giuseppe and Mattia fill
    their sheets and send them privately to Andrea, who commits both together
    and records the outcome in `docs/decisions.md`.

- [ ] **3.8 · Statistics** — `eval/stats.py`
  - Do: the procedures of the protocol, section 12.
  - Done when: tests compare against hand-computed or textbook values.

- [ ] **3.9 · Detection metrics and latency** — `eval/detection.py`
  - Do: `run(split)`, which for every detector that `detect` supports at that
    moment (it raises `NotImplementedError` for the others: skip them) writes
    the detected spans to `results/detected/`, with the seconds taken per
    text, then the detection metrics of the protocol, section 6, to
    `results/metrics/detection.json` and p50 and p95 latency per detector to
    `results/metrics/latency.json`, with the machine named.
  - Done when: hand-computed toy cases give the expected numbers, including a
    text with zero gold spans and a detector with zero predictions; the
    metrics can be recomputed from `results/detected/` without running a
    detector; it runs on dev for D0 and for every other detector already in
    `main`.

- [ ] **3.10 · Evaluation runner and report** — `eval/run.py`, `eval/report.py`, `make eval-dev`, `make eval-test`
  - Do: one runner that evaluates the configurations of `configs/eval.yaml`
    (read with `load_eval_configs`; now the three references, block 4 appends
    four), runs the detection evaluation, and writes the metrics files; chart
    and scorecard as in the protocol, sections 10 to 13; `make eval-test`
    refusing a second run and writing the access log.
  - Done when: `make eval-dev` produces chart and scorecard on dev for the
    three references; a test shows that adding a configuration to the file
    needs no code change; `results/cache/`, `results/masked/`,
    `results/detected/`, `results/metrics/` and `results/figures/` are
    committed.

- [ ] **3.11 · Hand-over note** — `docs/handoff/block-3.md`
  - Do: the note described in `docs/tasks/README.md`: how to load dev texts
    with gold spans, how to add a configuration and run the evaluation, what
    the pilot showed, the state of the judge, the LLM spend so far; the
    `docs/cards.md` lines proposed for the dataset.
  - **Human:** set the tag `block-3`; Mattia reads the note and the code, and
    G3 is ticked.
