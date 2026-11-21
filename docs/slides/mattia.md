# Slides — Mattia (draft, no numbers)

Part: the five detectors, what each finds and misses; backup slide with detection
per type. A draft for the human who writes the slides. Where a number will go,
the file it comes from is named; no number is written here.

## 1. Five detectors, one contract

- On screen: five boxes, D0 to D4, all returning the same span (offsets, type,
  confidence, source) into one merge rule: longer span wins, then confidence,
  then source priority.
- Say: they go from cheap and predictable to slow and general. D1 and D2 are
  used as they ship, with no tuning to our texts.

## 2. D0 — rules

- Finds: identifiers with a fixed shape, most with a checksum: IBAN, codice
  fiscale, partita IVA, phone, email, amounts next to a currency.
- Misses: everything without a shape (names, towns, employers, health, dates);
  amounts without a currency; other 6–11 digit codes are taken for phones.
- Say: the floor every other detector is compared with, and the part of D4 that
  never fails.

## 3. D1 — Presidio with Italian spaCy

- Finds: names, places and organisations from `it_core_news_lg`, plus Presidio's
  Italian pattern recognisers.
- Misses: `LOC` marks any place, not only towns; no date label, so only numeric
  dates; nothing on quasi-identifiers like job or age, nor on health.
- Say: the standard off-the-shelf choice, and the baseline of contrast 1.

## 4. D2 — a ready-made PII classifier

- Finds: names, emails, phones, tax and account numbers, from a multilingual
  token classifier (piiranha).
- Misses: its only quasi-identifier label is the town, and it has none for
  special categories; it covers only part of an email or a codice fiscale; long
  texts are read in windows.
- Say: licence is non-commercial: fine for a course project, a limit for reuse.

## 5. D3 — a local LLM

- Finds: quasi-identifiers (job, employer, town, age), special categories
  (health, union membership), and user codes that have no fixed shape.
- How: it returns span text, type and reason as JSON, never offsets; we find the
  text in the source by string search, so an invented span is dropped.
- Misses: an invalid JSON reply, twice, means no spans for that text; it is the
  slowest detector.
- Say: the model runs on the machine: the original text it reads never leaves it.

## 6. D4 — the hybrid

- On screen: D0 + D1 + D2 for direct identifiers, D3 for everything else.
- Say: composition only, no new logic. D1 was added after the pilot: D2 alone
  missed person names that D1 found.
- Numbers here: recall by class, precision and leak rate per detector from
  `results/test/metrics/detection.json`; latency p50 and p95 from
  `results/dev/metrics/latency.json`.
- Say: recall is the primary metric, because a missed identifier leaks; leak
  rate is the share of texts where at least one direct identifier is not fully
  covered.

## Backup. Detection per type

- On screen: a table, one row per type, one column per detector, recall under
  overlap matching (precision next to it).
- Numbers here: the per-type rows of `results/test/metrics/detection.json`.
- Say: which types each detector never finds, and which ones only D3 finds.
