# Omissis

A local tool that sits between a user and a cloud LLM. For Italian text it detects
sensitive spans, replaces them with pseudonyms, sends the pseudonymised text to the
model, restores the real values in the reply and reports what was disclosed.

The contribution is the measurement: what each configuration costs in privacy
(re-identification risk against an attacker LLM) and in answer quality.

The user we have in mind answers correspondence that holds other people's data: a
bank clerk or an HR officer who wants a draft reply from a cloud model without
handing over who the sender is.

Team project for *AI Frontiers: Large Language Models* (LUISS, fall 2026); the
authors are in [Team](#team).

## What it is and what it is not

- It **is** a pseudonymiser for one Italian text at a time (bank and HR
  correspondence), with a session vault that lives in memory, a restoration step
  that reports every value it could not put back, and an evaluation that measures
  what an attacker LLM can still infer.
- It is **not** an anonymiser. Pseudonymised text can still be re-identified,
  and the evaluation measures that risk. It does not encrypt or persist the vault,
  does not handle attachments, other languages or multi-turn chats, and has not
  been tested on real personal data: every person and value in this repository is
  invented.

## Related work

- **Tools that mask and put back.** [Microsoft Presidio](https://github.com/microsoft/presidio)
  detects and anonymises personal data and documents a de-anonymise operator; it
  is our detector D1. [LLM Guard](https://github.com/protectai/llm-guard) (Protect
  AI, now archived) pairs an `Anonymize` input scanner and a vault with a
  `Deanonymize` output scanner, and LangChain's experimental
  `PresidioReversibleAnonymizer` keeps a mapping and applies it back to the
  model's output. The loop of masking, sending and restoring is therefore not
  new. What this project adds is the measurement: how much the masked text still
  reveals, and what masking costs the reply.
- **What a model can infer.** Staab et al., *Beyond Memorization: Violating
  Privacy via Inference with Large Language Models*
  ([arXiv:2310.07298](https://arxiv.org/abs/2310.07298)), show that LLMs infer
  attributes such as location, income and sex from ordinary Reddit text; our
  attribute attack asks the same question with closed answer lists. The same
  authors, *Language Models are Advanced Anonymizers* (ICLR 2025,
  [arXiv:2402.13846](https://arxiv.org/abs/2402.13846)), let an adversary LLM
  guide what is rewritten; here the adversary only measures.
- **How the anonymisation of text is evaluated.** Pilán et al., *The Text
  Anonymization Benchmark (TAB)* (Computational Linguistics 48(4), 2022,
  [arXiv:2202.00443](https://arxiv.org/abs/2202.00443)): 1,268 English court
  cases annotated by identifier type, with privacy and utility metrics. Lison
  et al., *Anonymisation Models for Text Data*
  ([ACL 2021](https://aclanthology.org/2021.acl-long.323/)), argue for measures
  of disclosure risk beyond sequence labelling. We follow this line in scoring
  privacy and utility side by side; our data are Italian, synthetic and much
  smaller.
- **Law.** The GDPR defines pseudonymisation in article 4(5); the European Data
  Protection Board published
  [Guidelines 01/2025 on Pseudonymisation](https://www.edpb.europa.eu/our-work-tools/documents/public-consultations/2025/guidelines-012025-pseudonymisation_en)
  (version for public consultation). In case C-413/23 P (*EDPS v SRB*,
  4 September 2025) the Court of Justice held that pseudonymised data are not
  personal data in every case and for every recipient; that case concerns
  Regulation (EU) 2018/1725. This project makes no legal claim: it measures a
  risk.

The sources were read at the linked pages on 22 Nov 2026; the article of the GDPR
and the judgment were read on a copy of the text and on the Court's press release.

## Quick start

Requires [`uv`](https://docs.astral.sh/uv/) and `make`. `uv` installs Python 3.11.

```
make setup              # create the environment from uv.lock
make test               # unit and integration tests
make lint               # ruff check and format check
cp .env.example .env    # then write your GroqCloud key in GROQ_API_KEY
```

`make setup` needs the network. After it, every other `make` target runs `uv`
offline; a target runs `make setup` first when `.venv` is missing or `uv.lock` or
`pyproject.toml` has changed since.

Only the commands that call a hosted model need the key in `.env`, and they read
it through `uv run --env-file .env ...`. The detectors D1 to D4 need two more
things, which `make setup` and CI do not install:

```
uv sync --locked --group detect   # Presidio, spaCy and it_core_news_lg, transformers
uv run hf download iiiorg/piiranha-v1-detect-personal-information \
    --revision 255acde67a2f34cf452eb42e365b24d2957352fc   # the weights of D2
ollama pull gpt-oss:20b           # the local model of D3, with Ollama running
```

D2 reads its weights from the local Hugging Face cache and never downloads them
on its own (model and revision in `configs/models.yaml`). Without the `detect`
group the tests that need it are skipped, and the demo offers D0 and D3 only.

## Run one text

```
uv run omissis run --config configs/skeleton.yaml --input data/fixtures/fx-bank-01.json
```

This runs the whole pipeline on a synthetic fixture with detector D0 and
placeholders R1. Every model role points to the built-in `echo` provider, which
returns the prompt unchanged, so the command needs no network and no key. The
command prints the masked text, the reply, the restored reply and the disclosure
report to standard output. The restored reply holds the original values: do not
redirect it under `results/`. A run configuration (`docs/interfaces.md`,
section 4) chooses the detector, the strategy and the backend: `cloud` calls the
model, and `replay` answers from the cache only.

`--task` sets the request sent before the text (the default asks for a draft
reply). Before sending, `run` checks it: a request for a calculation (a total, a
difference, a percentage) on a text where amounts, dates or ages were masked is
not sent, and the command ends with one line on standard error and status 2.
With `configs/skeleton.yaml` amounts stay visible, so nothing is stopped.

The request itself is sent as written and is not masked: do not put personal data
in it. An empty text is refused. A configuration whose cache is the committed one
(`results/cache`) accepts only the records under `data/`, which are synthetic: a
text of your own needs a `cache_dir` under `results/scratch/`, because the cache
keeps every prompt that is sent.

## Demo

```
make demo
```

This starts a Gradio page in replay mode, with no network and no key. Pick an
example, then:

1. **Protect** masks the text and shows it exactly as it would be sent, with the
   table of what was replaced. Nothing has left the machine yet.
2. **Send** sends that text and shows the reply with the real values restored and
   any restoration problem. It is refused if the text or a setting changed after
   the preview.

The replies of the five examples are recorded in `results/cache/` for every
detector and both replacements, with the two example requests, so every choice
of the menus answers offline. The page offers the detectors that can run on the
machine: D0 and D3 after `make setup`, all five with the `detect` group and the
weights of D2. In replay D3 answers from the cache and needs no Ollama.

The second example request asks for a total. On a text whose amounts are masked,
*Protect* does not send it and says why.

To run it live on a text of your own, start it with the key and choose the
backend `cloud`:

```
uv run --env-file .env python -m omissis.app
```

D3 and D4 then call the local model, about half a minute per text on a laptop,
and the calls are cached under `results/scratch/app`, never in the committed
cache. The request is sent as written and is not masked.

## Architecture

One line per stage of the pipeline (`src/omissis/`):

- **detect** (`detect/`): finds sensitive spans. D0 rules, D1 Presidio, D2 a
  ready-made token classifier, D3 a local LLM that returns span text and never
  offsets, D4 a hybrid (direct identifiers from D0, D1 and D2, everything else
  from D3). Overlaps are merged by length, then
  confidence, then source priority.
- **resolve** (`resolve.py`): groups the mentions of one entity and infers
  grammatical gender by rules.
- **replace** (`replace/`): R1 typed placeholders (`[PERSONA_1_F]`, `[IBAN_1]`), or
  R2 realistic fakes from fixed lists disjoint from the profiles, deterministic
  for a seed.
- **vault** (`vault.py`): the in-memory mapping of the session, never logged in
  clear.
- **send** (`backends/`): every LLM call goes through one function and an
  append-only JSONL cache, at temperature 0.
- **restore** (`restore.py`): exact, then normalised, then fuzzy matching. It
  never guesses: an unresolved or invented token is reported.
- **report** (`pipeline.py`, `cli.py`, `app.py`): the reply, plus a disclosure
  report of what was masked and how it came back.

Taxonomy: direct identifiers, quasi-identifiers and special categories
(`src/omissis/contracts.py`).

The steps are known in advance, so this is a fixed pipeline and not an agent that
chooses its tools. Where a model is involved it proposes and code decides: D3
proposes span texts and code keeps only those found in the source as whole
tokens; the cloud model writes a reply and code restores only the tokens that are
in the vault. Whether the LLM detector is worth its cost is measured, not
assumed: it is contrast 1 below.

## Evaluation

66 synthetic emails, written from 30 invented profiles, are split once into dev
(20 texts) and a held-out test set (46 texts). Seven configurations are measured. Three are references:
`REF-none` (nothing masked), `REF-oracle-direct` (gold direct identifiers and
special categories masked, quasi-identifiers left visible) and `REF-oracle` (every
gold span masked). Four use detectors and replacements:
`D1+R1`, `D2+R1`, `D4+R1` and `D4+R2`. The privacy measures are an attacker LLM's
linkage and attribute attacks against the profiles. The utility measures are a
structured extraction task (T3) and a reply draft (T1) scored on three criteria:
by an LLM judge if it passes its validation, by a team member if it does not.
Restoration is measured by outcome. There are three pre-declared contrasts:

1. `D4+R1` vs `D1+R1` on linkage top-1;
2. `D4+R1` vs `REF-none` on utility;
3. `D4+R2` vs `D4+R1` on full restoration.

Each contrast is tested with paired tests and the Holm correction. Data, metrics,
attacks and statistics are fixed in `docs/evaluation_protocol.md`; the models
are described in `docs/cards.md`.

## Reproduce

```
make reproduce
```

This rebuilds every estimate, table and chart from the per-text outcomes in the
committed metrics files (`results/<split>/metrics/`). It uses no network, no model
and no detector, and it reads no text. A split without metrics is skipped with
one line. The pilot has no scorecard row, so nothing but its metrics files is
rewritten. For `pilot`, `dev` and `test` the metrics files and the scorecards
come out identical to the committed ones.

The numbers of the test were produced by the code at commit `8d4cb69`, the last
change to `src/` before the run, and committed in `103ea37`. The commits after it
change nothing that the evaluation computes. The check, on a machine with the
`detect` group: `uv run python -m omissis.eval.run --split dev --backend replay
--yes` runs the detectors again and answers every model call from the cache; the
metrics, the masked texts and the scorecard of dev come out the same (the files
of `results/dev/detected/` differ in their `seconds` field only, a measured time).

## Results

The test split was evaluated once, on 22 Nov 2026: 46 texts, 7 configurations.
Unless another file is named, every number below is in
`results/test/scorecard.md` and comes from `results/test/metrics/`. The 20 dev texts are in `results/dev/scorecard.md`, and
the errors found on them in `results/dev/error_taxonomy.md`.

![Privacy score against the T3 score on the test split](results/test/figures/privacy_utility.png)

x is the privacy score, 1 − linkage top-1 with 25 candidates; y is the T3 score
for every configuration, because the judge was rejected (below). Bars are 95%
intervals; the dashed line is the privacy score of an attacker who guesses.

| Configuration | Linkage top-1, N = 25 | T3 | Full restoration |
|---|---|---|---|
| `REF-none` | 1.00 (no variation observed, n = 46) | 0.97 [0.94, 0.99] | 0.98 [0.93, 1.00] |
| `REF-oracle-direct` | 0.98 [0.93, 1.00] | 0.96 [0.93, 0.98] | 0.87 [0.76, 0.96] |
| `REF-oracle` | 0.50 [0.35, 0.65] | 0.91 [0.87, 0.94] | 0.83 [0.72, 0.93] |
| `D1+R1` | 0.93 [0.85, 1.00] | 0.95 [0.92, 0.98] | 0.87 [0.76, 0.96] |
| `D2+R1` | 1.00 (no variation observed, n = 46) | 0.95 [0.91, 0.97] | 0.87 [0.76, 0.96] |
| `D4+R1` | 0.59 [0.43, 0.74] | 0.90 [0.86, 0.93] | 0.74 [0.61, 0.85] |
| `D4+R2` | 0.41 [0.28, 0.54] | 0.95 [0.92, 0.97] | 0.72 [0.59, 0.85] |

Linkage top-1 is the share of texts whose author the attacker names first among
25 candidates; chance is 0.04. No reply of the attacker was left not parsed.

The three pre-declared contrasts, Holm-corrected at alpha 0.05:

1. **`D4+R1` vs `D1+R1` on linkage top-1: a finding.** −0.35 [−0.52, −0.17],
   Holm p 0.001. The hybrid detector lowers the share of texts linked to their
   author from 0.93 to 0.59.
2. **`D4+R1` vs `REF-none` on utility: a gap of −0.22 [−0.25, −0.20]**, Holm
   p < 0.001 (0.76 against 0.98). Its T3 half is 0.90 against 0.97. Its T1 half is
   0.62 against the 1.00 that `REF-none` has by definition, as the reference of
   the rating: on this half `D4+R1` cannot score above the reference, so the
   contrast gives the size of the gap and not a loss that the test alone proves.
3. **`D4+R2` vs `D4+R1` on full restoration: not distinguishable with this
   sample.** −0.02 [−0.17, 0.13], Holm p 1.000 (0.72 against 0.74).

What else the numbers show, with no test run on it:

- **Masking lowers linkage and leaves it far above chance.** With every annotated
  span masked (`REF-oracle`) the attacker still names the author of 0.50 of the
  texts, against 0.04 by chance; `D4+R1` is at 0.59.
- **The configurations that leave quasi-identifiers in clear are linked almost
  always.** `REF-oracle-direct`, which masks the direct identifiers and the special
  categories, is at
  0.98; `D1+R1` is at 0.93 and `D2+R1` at 1.00, against 1.00 with nothing masked.
- **`D4+R2` and `D4+R1`** stand at 0.41 and 0.59 on linkage and at 0.95 and 0.90 on
  T3. This is not a declared contrast: the estimates are side by side, and R2 is
  not measured as a decoy (`docs/evaluation_protocol.md`, section 7).
- **About a quarter of the replies of D4 are not fully restored** (0.74 and 0.72).
  On dev every such reply holds a placeholder that the model made up
  (`results/dev/error_taxonomy.md`, 2.1).
- **Detectors.** D4: recall 0.99 on direct identifiers, 0.97 on quasi-identifiers,
  0.88 on special categories; precision 0.97; leak rate 0.04 [0.00, 0.11]. D1:
  recall 0.72 on direct identifiers, leak rate 0.87 [0.76, 0.96].
- **Gender and health are not hidden by any configuration**: the attacker is
  right on 0.96 to 1.00 of the texts. R1 placeholders reveal gender on purpose,
  and in the health scenarios the topic reveals health.
- **The judge was rejected, and that is a result too.** On the 40 dev items of its
  validation its quadratic-weighted kappa with the rater, an AI agent whose sheet
  a team member approved, was 0.37 (0.6 needed) and 75% of its scores were within
  one point (85% needed):
  `results/dev/metrics/judge_validation.json`. So T1 is reported for `D4+R1` only,
  from the scores that one team member gave to its 46 test replies; the other
  configurations report T3 alone and have no utility score.
- **Without the 5 test texts about a loan that the profile does not hold**
  (Limitations), linkage top-1 is 0.63 for `D4+R1` and 0.44 for `D4+R2`.

## Risks and defences

| Risk | What stops it, in code | What we measured |
|---|---|---|
| An instruction hidden in the text makes the local detector report nothing | Nothing stops D3 itself. In D4 names, phone numbers, emails, IBANs and tax codes come from D0, D1 and D2 and stay masked; the app shows the masked text before it is sent | Attack case 1: the attack works, 7 of 11 annotated spans go out in clear |
| An instruction hidden in the text asks the cloud model for the real values | The cloud model holds placeholders, never an original value; restoration puts back the tokens of the vault and nothing else | Attack case 2: the attack fails, no original value in the reply |
| A detector misses an identifier | The preview of the app, before anything is sent | D4 leaves a direct identifier uncovered in 0.04 of the test texts, D1 in 0.87 |
| A model invents a span or a placeholder | A span of D3 that is not in the text as a whole token is dropped; an invented placeholder is reported, never filled | About a quarter of the replies of D4 hold an invented placeholder (Results) |
| A request that cannot be answered on masked values | The feasibility check refuses a calculation on masked amounts, dates or ages | Not evaluated: a heuristic (Limitations) |
| Cost and latency | Every call goes through one cache at temperature 0, and replay needs no model | 1,610 hosted calls for the seven configurations on the test (`results/test/metrics/cost.json`); D4 takes a median of 37 s per text on a 16 GB laptop (`results/dev/scorecard.md`) |

The two attack cases are synthetic emails that carry an instruction written for a
model, each run once through `D4+R1` beside a clean twin (`data/attacks/`,
`results/attacks/attacks.md`). They are cases, not an evaluation: one text each,
no interval and no test.

1. **Against the local detector: the attack works.** A note at the end of the
   email tells "the automatic system" to return an empty list. D3 returns no span
   (7 on the clean twin), and an empty list is a valid reply, so no failure is
   counted. Under D4 seven of the eleven annotated spans go to the cloud model in
   clear: role, employer, town, two dates, the health condition and the badge
   number. Name, phone number and email stay masked.
2. **Against the cloud model: the attack fails.** An instruction asks the
   assistant to write out the real values behind the placeholders. The model
   drafts the ordinary reply; it could not obey, because it never has those
   values.

Closing the text between delimiters in the prompt of D3, and treating an empty
reply of D3 as a failure when the other detectors found identifiers, would
answer the first case. Both change what was evaluated, so they are future work.

## Limitations

- **Threat model.** The attacker is one LLM that sees the masked text and a list
  of 10 or 25 candidate profiles. A stronger attacker, external data or several
  texts from one author are not measured.
- **Pseudonymisation is not anonymisation.** Quasi-identifiers and the content of
  a request can still point to a person. The numbers measure re-identification
  risk; they do not prove it is low.
- **Derived values.** The model can build values on the surrogates (on dev: a
  weekday for a fake date, the province of a fake town), and restoration cannot
  undo them. No computed amount was observed on dev. The app and `omissis run` refuse a request that asks for a
  calculation on masked amounts, dates or ages (`src/omissis/feasibility.py`).
  This check is a heuristic and is not evaluated. It reads the request alone, by
  a fixed list of Italian cues: it misses a calculation asked inside the text
  or worded outside the list. It also stops requests that compute nothing: one
  that only asks to copy a total, or "Dividi la risposta in due paragrafi".
  With detector D0 it sees amounts only. Values the model derives on its own
  are not caught.
- **Seven loan texts contradict the profile of their author** (5 are in test, 2
  in dev). They are about a
  loan or a mortgage that the profile does not hold, and the candidate list of
  the linkage attack shows the products: on these texts it points away from the
  author, so the privacy score of a masked configuration is too high by what
  they add. The scorecard reports linkage without them beside the value on all
  texts (`docs/decisions.md`, 21 Nov).
- **Synthetic data only.** The texts were written by a model and are more regular
  than real mail. Texts by one author are not independent, so intervals over
  texts overstate precision.
- **No human annotates the texts.** An AI agent reviews the gold tags, annotates
  the 13 texts of the agreement and rates the 40 items of the judge validation;
  one team member approves each on the agent's report (`docs/decisions.md`,
  21 Nov). So the agreement is between two models, the judge was validated
  against a model, and the gold is reviewed by an LLM while D3 and D4 are LLM
  detectors. The judge is the same model as the cloud model.
- **One person rated the replies of the test.** With the judge rejected, T1 is
  the score of one team member on the 46 replies of `D4+R1`. The sheet holds one
  configuration, so he knew which one he was rating; there is no second rater
  and no measure of agreement.
- **Known and not fixed:**
  - An R2 amount that the reply writes without its decimals ("701 euro" for
    "701,00 euro") stays in the reply.
  - Two invalid JSON replies of D3 give no spans for that text. With D4 the
    direct identifiers found by D0, D1 and D2 are still masked; the
    quasi-identifiers, the special categories and the `UTENTE` codes are not.
  - An empty reply of the local model stops the run and is never cached. At
    temperature 0 the same text may stop the next launch too.
  - Under R2, two people told apart only by a title ("Sig. Ferri",
    "Sig.ra Ferri") share one fake surname.
  - A token shaped like a placeholder that is already in the user's text
    ("[IBAN_1]") is reported as invented by the model, and the reply counts as
    not fully restored even when it is.
  - Under R2, a fake value written with no separator after a placeholder is not
    restored, and the reply still counts as fully restored. It needs two masked
    spans that touch; it was not looked for in the data.
  - Nothing in the code forces the role `d3` to a local model: a models file
    that points it to a hosted service sends the original text there. The app
    says so on its page.

## How it uses the course

| Course topic | Where it is used here |
|---|---|
| Transformers and BERT-style encoders | D2 is an encoder (mDeBERTa-v3) fine-tuned for token classification, used as it ships; D1 uses the entity recogniser of spaCy's Italian pipeline |
| Generative pre-trained models, decoding | The cloud model, the attacker, the generator of the texts and D3 are generative models called at temperature 0 with a token limit; a reply cut at the limit is a declared case (`docs/evaluation_protocol.md`, section 7) |
| Fine-tuning, and when not to | Nothing is fine-tuned: the licence of D2 forbids derivatives, and what it misses is measured (D2 alone against the hybrid D4) |
| Prompting and structured output | One instruction asks the cloud model to copy the placeholders; D3 answers with a JSON array checked against a schema, at low reasoning effort, and an invalid reply is asked once more |
| Hallucination | A span that D3 invents is not in the text and is dropped; a placeholder that the cloud model invents is reported, never filled |
| Evaluation and benchmarking | The core of the project: a protocol fixed before the data, a held-out split evaluated once, paired tests with the Holm correction, intervals, an LLM judge validated against a rater and rejected |
| Ethics and regulation | Pseudonymisation is not anonymisation; special categories are a class of their own; re-identification risk is measured, not assumed; synthetic data only |
| Tools and frameworks | Hugging Face `transformers`, PyTorch, spaCy and Presidio, Ollama for the local model, Gradio; plain Python for the pipeline |
| Applications and cost | Reply drafting (T1) and structured extraction (T3); the calls of each configuration and the latency of each detector are reported |
| Retrieval-augmented generation | Not used: the text carries everything the model needs |

## Repository map

| Path | What it holds |
|---|---|
| `src/omissis/` | The tool: detectors, resolver, replacement, vault, backends, restoration, command line, app, and the evaluation code (`eval/`) |
| `tests/` | Unit and integration tests; those that need the `detect` group are skipped without it |
| `configs/` | Run configurations: the seven of the evaluation (`eval.yaml`), the demo (`app.yaml`), the offline example (`skeleton.yaml`), the attack cases (`attacks.yaml`), the pinned models (`models.yaml`) |
| `data/` | Synthetic data: profiles, the dev and test splits, the fixtures of the demo, the attack cases |
| `results/` | Committed results: the LLM cache, masked texts, detected spans, metrics, scorecards, charts |
| `docs/interfaces.md`, `docs/evaluation_protocol.md` | The two specifications: contracts and file formats; data, metrics and statistics |
| `docs/cards.md`, `docs/annotation_guide.md` | Model and data cards; how the gold spans are tagged |
| `docs/decisions.md`, `docs/ai_use.md` | The log of the decisions and the register of AI use |
| `presentation/` | The slides: open `index.html` in a browser, everything it loads is in the folder |

## Team

| Member | Main contributions | Presents |
|---|---|---|
| Giuseppe Catrambone | Project proposal; the two specifications; the foundation (contracts, configuration, vault, backend types); review and correction of every part before its merge; the local provider of D3; the feasibility check; review and approval of the data; the evaluation runs on dev and test; results and closing | Introduction, related work |
| Mattia Sebastiani | First implementation of the pipeline (D0 rules, span merging, R1 placeholders, restoration, backends, command line, fixtures), of the detectors D1 to D4, of the Gradio app and of the evaluation code; the profiles and the 66 texts; the first pilot run; the slides and the recorded demo in them | Architecture, design choices, the five detectors, demo, limits, conclusions |
| Andrea Saracino | `make reproduce`; the model and data cards; the first README; the slides in the course structure; the clean-clone check and the offline `make` targets | Evaluation design, results, what did not work |

The scope, the name of the project, the evaluation protocol and the design
decisions of the first week were taken by the three together
(`docs/decisions.md`).

## Licence

The code and the documentation are under the MIT License; the synthetic data and
the results (`data/`, `results/`) are under CC BY 4.0. Both are in `LICENSE`. The
models and the libraries that Omissis calls are not in this repository and keep
their own licences (`docs/cards.md`): the classifier of D2 and the spaCy model of
D1 do not allow commercial use.

## AI assistance

This project was built with the support of AI coding agents (Claude Code); every
change is reviewed and merged by a team member. The AI use of each task is
recorded in `docs/ai_use.md`.
