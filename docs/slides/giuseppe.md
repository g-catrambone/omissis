# Slides — Giuseppe (draft, no numbers)

Part: problem, existing tools, architecture and design choices, demo, conclusions.
A draft for the human who writes the slides. Where a number will go, the file it
comes from is named; no number is written here.

## 1. The problem

- On screen: an email to a bank or to HR (synthetic), with an IBAN, a codice
  fiscale, a health condition, highlighted.
- Say: people paste this kind of text into a cloud LLM to get a draft reply.
  The provider sees every identifier, and the provider is a third party. We want
  the reply without handing over who the writer is.
- Say: the question is not only "can we hide the IBAN" but "after hiding, can a
  model still tell who wrote it, and is the reply still useful?".

## 2. Existing tools and why they are not enough

- On screen: three columns. Rule- and NER-based redactors (Presidio), ready-made
  PII classifiers, "ask the LLM to redact".
- Say: they find direct identifiers, mostly in English. They do not measure what
  is left: job, town, employer and age together can point to one person. And
  redaction alone breaks the reply: the user needs the real values back.
- Say: our contribution is the measurement of that trade-off, not a new detector.

## 3. Architecture

- On screen: the pipeline as one row of boxes: detect → resolve → replace (vault)
  → send → restore → reply + disclosure report.
- Say, one line per box:
  - detect: five detectors, from rules to a local LLM, merged by one overlap rule;
  - resolve: mentions of one person become one entity, with grammatical gender;
  - replace: typed placeholders (R1) or realistic fakes (R2), recorded in an
    in-memory vault;
  - send: one function for every LLM call, with a cache, temperature 0;
  - restore: exact, normalised, fuzzy; it never guesses and reports what it
    could not put back.
- Say: everything except the cloud call runs on the user's machine; D3's model too.

## 4. Design choices

- On screen: five short claims, each with its reason.
  - **Taxonomy in three classes** (direct, quasi, special): masking policy is
    per class, and two reference configurations isolate the effect of masking
    quasi-identifiers.
  - **The local LLM never returns offsets**: it returns text, we find it by
    string search. A model that invents a span cannot place it.
  - **Placeholders carry gender** (`[PERSONA_1_F]`): Italian agreement in the
    reply stays right. We measure what that costs in privacy (attribute `gender`).
  - **Restoration never guesses**: an unresolved token is reported, never
    silently filled.
  - **A request that masking makes impossible is refused, not answered wrong**:
    a calculation on masked amounts is stopped before it is sent. With
    placeholders the model has no number; with fakes it would return a
    plausible, wrong one. The check is a heuristic and is not evaluated: it
    reads the request alone, by a fixed list of Italian cues, so it misses a
    calculation asked inside the text or worded outside the list.
- Say: the text is pseudonymised, and what we measure is its re-identification
  risk.

## 5. Demo (at most 90 seconds)

- On screen: the Gradio page in replay mode (`make demo`), no network.
- Do: pick one fixture and press *Protect*: the masked text appears, with
  surrogates highlighted and the table of what was replaced. Nothing has left
  the machine yet.
- Say: this is the human check before an irreversible step: what you see is
  exactly what will be sent.
- Do: press *Send*: show the reply restored and scroll the table.
- Do: on a bank fixture, pick the second example request (a total of the
  amounts): *Protect* does not send it and says why. This is the failure we
  show on purpose.
- Fallback: a screen recording of the same steps, in case the laptop fails.

## 6. Conclusions

- On screen: the privacy–utility chart again (`results/test/figures/privacy_utility.png`),
  with the three contrasts stated as findings or "not distinguishable".
- Numbers here: the three contrasts from `results/test/metrics/contrasts.json`
  (difference, interval, Holm p).
- Say: what the measurement supports and what it does not, in the wording of the
  decision rule (protocol, section 12). Negative results get the same space.
- Say: what we would do next: derived values computed locally, a second
  annotator, real (consented) data.
