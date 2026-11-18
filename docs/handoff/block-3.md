# Hand-over note — block 3 · Data and evaluation

> History: this note describes the code as its block left it. Later changes are
> in `docs/decisions.md`, what is left is in `docs/TODO.md`.

Written by Mattia's agent · 17 Nov 2026 · For: block 4 (task 4.5) and block 5.
Start from `docs/handoff/block-2.md`.

**See `docs/STATUS.md` for the situation at the end of the session of 17 Nov.**

**State: the code of the block is complete; the data are not.** The 66 texts are
generated and not yet reviewed, so there is no dev or test split and
`make eval-dev` has never run on real data. Everything below that needs the split
is marked *pending*.

## 1. What exists

| Task | Module | Content |
|---|---|---|
| 3.1 | `eval/profiles.py`, `data/profiles/` | 30 profiles in 6 cohorts, the plan of the 66 texts, candidate lists for N = 10 and 25, all from seed 20261111 and `pools.json` |
| 3.1 | `docs/annotation_guide.md` (v1) | rules for full dates, deadline, one requested action, allowed formats |
| 3.2 | `eval/textgen.py`, `eval/normalise.py` | generator prompt, tagged-text parser and its inverse, `generate`, `check`, `export`, `import` |
| 3.3 | `eval/attacks.py` | linkage and attribute inference, their rows |
| 3.4 | `eval/pilot.py`, `results/pilot/` | the pilot command; its note and metrics |
| 3.5 | `eval/review.py`, `eval/split.py`, `make split` | reviewer assignment, double annotation, agreement, the split |
| 3.6 | `eval/utility.py` | T3 scoring, the restoration record of the T1 reply |
| 3.7 | `eval/judge.py` | the judge, the rating sheets, the acceptance computation |
| 3.8 | `eval/stats.py` | paired bootstrap, McNemar exact, Holm |
| 3.9 | `eval/detection.py` | detection metrics from files, the timing pass |
| 3.10 | `eval/run.py`, `eval/report.py`, `make eval-dev`, `make eval-test` | the runner, the rows, scorecard and chart |

`make test` runs 919 tests; none needs the network or the split.

## 2. How to use it

**Load dev texts with their gold spans** (*pending the split*):

```python
from omissis.eval.datasets import load_texts
records = load_texts("data/dev")      # 20 TextRecord, each with .spans and .gold
```

**Add a configuration and run the evaluation.** Append one line to
`configs/eval.yaml`; nothing else changes:

```yaml
  - {name: D4+R1, detector: D4, strategy: R1, mask_quasi: true}
```

```
make eval-dev        # uv run --env-file .env python -m omissis.eval.run --split dev
```

The command prints the number of calls and waits for `y`. It writes
`results/dev/masked/`, `detected/`, `metrics/*.json`, `scorecard.md` and, when
matplotlib is installed, `figures/privacy_utility.png`. It stops with a message
when a configuration needs a detector that cannot run on the machine. A second
launch makes no new call: everything comes from `results/cache/`.

**Rebuild tables and chart from the committed metrics** (what `make reproduce`
will call in task 5.2): no model, no detector, no text.

```
uv run python -m omissis.eval.report --split dev
```

**Review a text as tagged text.**

```
uv run python -m omissis.eval.textgen export data/pool results/scratch/pool-txt
# edit results/scratch/pool-txt/bank-0001.txt: fix the [[TYPE|text]] tags and SCADENZA
uv run python -m omissis.eval.textgen import results/scratch/pool-txt/bank-0001.txt data/pool
uv run python -m omissis.eval.textgen check data/pool
```

`import` recomputes offsets, amounts and dates. It never writes `reviewed_by`:
the reviewer adds `"reviewed_by": "<initials>"` to the JSON by hand.

**Double annotation and agreement.**

```
uv run python -m omissis.eval.review export        # 13 plain texts in data/annotation/
# the second annotator saves data/annotation/<text_id>.<initials>.txt with tags added
uv run python -m omissis.eval.review agreement     # results/dev/metrics/agreement.json
```

**Judge validation** (*pending the split and a first `make eval-dev`*).

```
uv run python -m omissis.eval.judge sheets --split dev --raters GC MS
# each rater fills results/dev/judge_validation/sheet_<initials>.csv; nobody opens key.json
uv run --env-file .env python -m omissis.eval.judge accept --split dev
```

## 3. What the pilot showed

Ten texts, attacker `openai/gpt-oss-120b`, linkage top-1 (`results/pilot/pilot.md`):

| Configuration | N = 10 | N = 25 |
|---|---|---|
| `REF-none` | 10 | 10 |
| `REF-oracle-direct` | 10 | 9 |
| `REF-oracle` | 6 | 5 |

Both halves of the pilot rule are met (at least 6 under `REF-oracle-direct`; 4
fewer under `REF-oracle`, 3 needed). The go or no-go is the team's and is not yet
recorded in `docs/decisions.md`. Under `REF-oracle` the attacker still finds 6
authors of 10 and reads gender and health in every text: placeholders show the
gender by design and the topic shows the health.

## 4. Not done, and who it waits for

- **Review of the 66 texts** (22 each, `data/pool/REVIEWERS.md`), **double
  annotation** of 13, adjudication, then `make split`: humans.
- **The pilot texts were not reviewed** before the pilot ran.
- **Judge validation**: two raters, after the split.
- **Prompts to approve**: generator (`textgen.PROMPT`), attacks
  (`attacks.LINKAGE_PROMPT`, `ATTRIBUTES_PROMPT`), T3 (`utility.T3_TASK`), judge
  (`judge.PROMPT`).
- **Plotting dependency**: matplotlib 3.11.2, approved and added on 17 Nov.
- **`make eval-dev` on real data**, and committing `results/cache/` and
  `results/dev/`.

## 5. Known limits

- **Judge and cloud are the same model** (`openai/gpt-oss-120b`): the protocol
  asks to declare it.
- **The free tier of GroqCloud** sets the pace: one dev run with seven
  configurations is about 700 calls and roughly 1.5 million tokens.
- **An attacker reply cut at the token limit counts as a miss** and is not
  cached: it is asked again at every launch. None occurred in the pilot at 4,096
  tokens.
- **A cloud reply cut at 2,048 tokens stops the run** with an error.
- **Texts of the same author are not independent**, so intervals over texts
  overstate precision (protocol, section 12).
- **The two union members write two `union_leave` texts each**: the counts of
  the protocol force it.

## 6. LLM spend so far

All on the free tier, no charge. In `results/cache/`: 11 cloud calls (fixtures),
about 68 generator calls (66 texts and two discarded first attempts), about 160
attacker calls (the pilot, run twice: once at 2,048 tokens, once at 4,096).

## 7. Lines proposed for `docs/cards.md`

- **Omissis synthetic emails** — 66 Italian emails (40 bank, 26 HR), written by
  `qwen/qwen3.8-27b` from 30 invented profiles and one fixed prompt, each
  reviewed by one team member; 20 dev, 46 held out. Every person and value is
  invented; identifiers use codes that are never issued (bank code `00000`,
  place code `X…`). Licence proposed: CC BY 4.0.

## 8. Questions the next owner should be able to answer

1. Which files does `make reproduce` need, and why does it need no text?
2. What stops `make eval-test` from running twice, and what happens to a launch
   that fails half-way?
3. How is a text counted as a leak, and why does D3 have no leak rate?
4. When the judge is rejected, which numbers change and which run is completed
   later?
5. Why is the T1 score of `REF-none` exactly 1?
