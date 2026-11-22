# Model and data cards

One entry per model role of `configs/models.yaml`, one for what D1 runs on, one for
the dataset. Model ids and revisions are copied from `configs/models.yaml`, which
prevails if the two ever differ. Every licence was read at the link given, on
19 Nov 2026, except where an entry says it was not read; **Human:** Giuseppe
confirms them.

## Hosted models (GroqCloud)

GroqCloud publishes no revision of a hosted model: the revision we pin is the day
of the pin. Use of the service is governed by the Groq Services Agreement
(<https://console.groq.com/docs/legal/services-agreement>, linked from
<https://groq.com/terms-of-use>; not read).

### `cloud`, `attacker`, `judge` — `openai/gpt-oss-120b`

- **What it is.** An open-weights reasoning model by OpenAI, served by GroqCloud.
- **Where it comes from.** <https://huggingface.co/openai/gpt-oss-120b>.
- **Revision.** `2026-11-16` (day of the pin), for all three roles.
- **Licence.** Apache 2.0, read on <https://huggingface.co/openai/gpt-oss-120b>
  ("License: apache-2.0").
- **How we use it.** Through the API at temperature 0, every call cached in
  `results/cache/`. `cloud` receives the masked text and answers it; `attacker`
  runs the linkage and attribute attacks; `judge` scores the reply of task T1.
- **Limits for us.** The judge is the judged model, which the protocol asks to
  declare. The three roles share one daily allowance of the free tier, which sets
  the pace of a run. The weights are open, but the hosted copy can change
  without a new revision.

### `generator` — `qwen/qwen3.8-27b`

- **What it is.** A model of the Qwen family, served by GroqCloud as a *preview*
  model.
- **Where it comes from.** <https://console.groq.com/docs/model/qwen/qwen3.8-27b>;
  model card <https://huggingface.co/Qwen/Qwen3.8-27B>.
- **Revision.** `2026-11-16` (day of the pin).
- **Licence.** Apache 2.0, read on the Hugging Face card
  <https://huggingface.co/Qwen/Qwen3.8-27B> ("License: apache-2.0"). The GroqCloud
  pages state no licence.
- **How we use it.** It wrote the 66 synthetic texts, once, from the profiles and
  one fixed prompt, at temperature 0. It is not called during the evaluation.
- **Limits for us.** GroqCloud lists preview models as "intended for evaluation
  purposes only and should not be used in production"
  (<https://console.groq.com/docs/models>): fine for writing test data, and a
  preview model may be withdrawn, so the cache is the only record of its output.

## Local models

### `d3` — `gpt-oss:20b`

- **What it is.** The 20-billion-parameter model of the same gpt-oss family, in
  the build that Ollama distributes (MXFP4, 14 GB).
- **Where it comes from.** <https://ollama.com/library/gpt-oss:20b>; original
  weights <https://huggingface.co/openai/gpt-oss-20b>.
- **Revision.** `f38aa0c53da5`, the digest of the model layer, also listed on the
  Ollama page.
- **Licence.** Apache 2.0, read on <https://ollama.com/library/gpt-oss:20b>
  ("Apache License Version 2.0, January 2004") and on
  <https://huggingface.co/openai/gpt-oss-20b> ("License: apache-2.0").
- **How we use it.** Detector D3, and the LLM half of D4: it returns span text,
  type and reason as JSON, at temperature 0; offsets are found by string search.
  It runs on the machine of the evaluation, so the original text it reads does
  not leave that machine.
- **Limits for us.** Two invalid JSON replies give no spans for that text. An
  empty reply stops the run. Until 18 Nov the role was on `openai/gpt-oss-20b` at
  GroqCloud: those replies stay in `results/cache/d3.jsonl` and are not read.

### `d2` — `iiiorg/piiranha-v1-detect-personal-information`

- **What it is.** A token classifier for personal data, fine-tuned from
  `microsoft/mdeberta-v3-base` on `ai4privacy/pii-masking-400k`; it covers six
  languages, Italian among them, and 17 types of personal data.
- **Where it comes from.**
  <https://huggingface.co/iiiorg/piiranha-v1-detect-personal-information>.
- **Revision.** `255acde67a2f34cf452eb42e365b24d2957352fc`.
- **Licence.** CC BY-NC-ND 4.0, read on the model card ("License:
  cc-by-nc-nd-4.0"). The full licence text was not read.
- **How we use it.** Detector D2, as it ships: no fine-tuning, weights read from
  the local Hugging Face cache and never stored in the repository. Its labels are
  mapped to our types (`src/omissis/detect/classifier.py`).
- **Limits for us.** Non-commercial and no derivatives: usable for this course
  project, not for a product built on Omissis. Its only quasi-identifier
  label is the town (`CITY`) and it has none for special categories; it covers
  only part of an email or a codice fiscale. Its window is 256 tokens, so
  longer texts are read in overlapping windows.

## What D1 runs on — Presidio and `it_core_news_lg`

- **What it is.** Microsoft Presidio (`presidio-analyzer` 2.2.362), a framework of
  pattern recognisers and an NLP engine, with the Italian spaCy pipeline
  `it_core_news_lg` 3.8.0 (spaCy 3.8.18) for names, places and organisations.
- **Where it comes from.** <https://github.com/microsoft/presidio>;
  <https://github.com/explosion/spaCy>;
  <https://github.com/explosion/spacy-models/releases/tag/it_core_news_lg-3.8.0>.
- **Revision.** The versions pinned in `pyproject.toml` and `uv.lock`
  (dependency group `detect`).
- **Licence.**
  - Presidio: MIT, read on <https://github.com/microsoft/presidio/blob/main/LICENSE>
    and on <https://pypi.org/project/presidio-analyzer/2.2.362/>.
  - spaCy (code): MIT, read on
    <https://github.com/explosion/spaCy/blob/master/LICENSE>.
  - `it_core_news_lg`: CC BY-NC-SA 3.0, read on
    <https://github.com/explosion/spacy-models/releases/tag/it_core_news_lg-3.8.0>
    and on <https://huggingface.co/spacy/it_core_news_lg>. The MIT licence of spaCy
    does not cover the model.
- **How we use it.** Detector D1, as it ships, with language, model and phone
  region set to Italian; Presidio labels are mapped to our types
  (`src/omissis/detect/presidio.py`). One correction to its output: a span that
  goes over a line break keeps its first line only (`docs/decisions.md`, 22 Nov
  2026).
- **Limits for us.** The spaCy model is non-commercial and share-alike. It is
  trained on UD Italian ISDT and WikiNER, not on correspondence. Its `LOC` label
  marks any place, not only towns, and it has no date label (Presidio finds
  numeric dates only).

## Dataset — Omissis synthetic emails

- **What it is.** 66 Italian emails, 40 to a bank and 26 to an HR office, in 13
  scenarios (`docs/evaluation_protocol.md`, section 2), each with gold spans of the
  taxonomy in `src/omissis/contracts.py`, plus 30 invented profiles in 6 cohorts
  (`data/profiles/`).
- **Where it comes from.** Written for this project by the `generator` model from
  the profiles and one fixed prompt; tagged by the generator; each text is
  reviewed by an AI agent (Claude Opus 5.5), and one team member approves its
  report (`docs/decisions.md`, 21 Nov).
- **Revision.** The files of `data/dev/`, `data/test/` (checksums in
  `data/split.json`) and `data/profiles/` at the tag `v1.0`.
  Split: 20 texts in dev (13 bank, 7 HR) and 46 in test (27 bank, 19 HR).
- **Licence.** Proposed: CC BY 4.0. Not decided (step C3 of `docs/TODO.md`).
- **How we use it.** Every number of the evaluation is measured against its gold
  spans and gold fields; the profiles are the candidates of the linkage attack.
- **Limits for us.** Every person and value is invented; identifiers use codes
  that are never issued (bank code `00000`, place code `X…`). Texts written by a
  model are more regular than real mail. No human reviewed the texts one by one: an AI
  agent did, and one member approved its report. Seven bank texts are about a
  loan or a mortgage that the profile of their author does not hold, and no
  text states the monthly instalment of its profile: the linkage attack is
  reported also without those seven. Two texts (`bank-0006`, `bank-0021`) hold
  an IBAN one character short of the 27 of an Italian IBAN, as the generator
  wrote it: it is kept and tagged, and a detector that checks the format can
  miss it. Texts of the same author are
  not independent, so intervals over texts overstate precision.
  Numbers per split, annotated spans (`gold` in
  `results/<split>/metrics/detection.json`): dev 297 (141 direct, 149
  quasi-identifiers, 7 special category); test 666 (335 direct, 315
  quasi-identifiers, 16 special category).
