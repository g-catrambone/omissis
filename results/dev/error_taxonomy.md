# Error taxonomy on dev

Step C2 of `docs/TODO.md`; protocol, section 13: categorised dev examples of missed
identifiers, failed restorations, derived values and successful attacks. The 20 dev
texts, results of 22 Nov 2026. Built from `results/dev/error_examples.md`, the
`per_text` lists of `results/dev/metrics/` and `results/dev/masked/`. No model was
called, and no test text or test result was used.

**How to read the counts.** They describe 20 texts and no test is run on them. By the
decision rule of the protocol, section 12, one statement on dev is a finding: `D4+R1`
against `D1+R1` on linkage top-1 at N = 25 (difference −0.35, Holm p 0.031,
`results/dev/metrics/contrasts.json`). `D4+R2` against `D4+R1` on full restoration is
not distinguishable with this sample. Every other pair of counts in this file is set
side by side, not compared.

For each kind of error: what it is, how many on dev, one example, and which number of
the scorecard sees it. A restored reply is not stored: an example from one is rebuilt
as `results/dev/error_examples.md`, section 1, says.

## 1. Missed identifiers

297 annotated spans: 141 direct, 149 quasi-identifiers, 7 special category. The three
states (left in clear, covered in part, masked under another type) are the ones of
`results/dev/error_examples.md`, section 2, where every case of D4 is listed. Here the
spans left in clear are split by cause: whether the code of the detector can return
the type at all (`LABEL_TO_TYPE` in `src/omissis/detect/presidio.py` and
`classifier.py`, the rules of `rules.py`, `TYPES` in `llm.py`).

| Kind | D0 | D1 | D2 | D3 | D4 | Seen by |
|---|---|---|---|---|---|---|
| 1.1 Left in clear: a type the detector cannot return | 207 | 64 | 143 | 0 | 0 | recall; leak rate when direct |
| 1.2 Left in clear: a type the detector returns | 0 | 58 | 67 | 11 | 11 | recall; leak rate when direct |
| 1.3 Covered in part | 0 | 13 | 34 | 2 | 2 | recall under exact matching only; leak rate when direct |
| 1.4 Masked under another type | 0 | 24 | 0 | 8 | 11 | recall under exact matching; under overlap matching only when the class differs |

D3 is told to look for no direct identifier but `UTENTE`: the 121 others it leaves in
clear are not its errors and are not in the table.

- **1.1 A type the detector cannot return.** D0 has rules for six types
  (CF, EMAIL, IBAN, IMPORTO, PIVA, TELEFONO); D1 and D2 have no label for a role, an amount or a
  special category, and D2 none for a company or a date. By type: D0 PERSONA 53, AZIENDA 40, DATA 40, CITTA 25, RUOLO 22, UTENTE 18;
  D1 RUOLO 22, IMPORTO 21, UTENTE 14, SALUTE 5, ETA 1, SINDACATO 1; D2 AZIENDA 40, DATA 40, RUOLO 22, IMPORTO 21, IBAN 12, SALUTE 6.
  This is the larger part of what `D1+R1` and `D2+R1` leave to the attacker
  (section 4.1).
- **1.2 A type the detector returns, a mention it misses.** D1: DATA 40, CF 8, AZIENDA 7, TELEFONO 3
  (39 of the 40 dates of dev have the month in words and one is a year alone; Presidio
  finds numeric dates only). D2:
  UTENTE 18, TELEFONO 18, CF 17, PERSONA 12, CONTO 1, CITTA 1. D3 and D4, the same 11 spans: DATA 4, RUOLO 3, AZIENDA 2, UTENTE 1, IMPORTO 1.
  Example: `hr-0003`, RUOLO `Responsabile Acquisti`, in a signature line; the one direct
  identifier is `bank-0034`, UTENTE `YO-92505`.
- **1.3 Covered in part.** D2: EMAIL 20, PERSONA 12, TELEFONO 2. D1: AZIENDA 13. D3 and D4
  leave words of two special-category spans in clear (`hr-0016`: `con riabilitazione`).
- **1.4 Masked under another type.** The value is hidden, the substitute carries the
  wrong type. D1: CF 9, IBAN 5, AZIENDA 4, UTENTE 4, CONTO 1, SALUTE 1. D4: CITTA 6, IBAN 2, CF 2, CONTO 1: six
  towns returned as `STRUTTURA`, two IBANs and a fiscal code returned as a person (the
  type errors of D1, which D4 inherits), a fiscal code returned as biometric data, an
  account code returned as `UTENTE`. No leak, and one cost further on: in `hr-0003`
  the reply is signed with the fiscal code (section 2.3).

## 2. Failed restorations

The T1 replies of `D4+R1` and of `D4+R2`, 20 each. The counts of 2.2, 2.3 and 2.4 are
the ones Giuseppe approved on the report of the AI reading (`docs/decisions.md`,
22 Nov 2026; `results/dev/error_examples.md`, section 1): the number of replies is
solid, the cause of each case is the judgement of one reader.

| Kind | `D4+R1` | `D4+R2` | Seen by |
|---|---|---|---|
| 2.1 A placeholder that the model made up in our format (`hallucinated_token`) | 6 in 3 replies | 13 in 5 replies | full-restoration rate |
| 2.2 A value restored where another party's value belongs: the model gave it to the wrong party | 15 replies | 2 replies | no number |
| 2.3 The same, because the substitute held a wrong value | 1 reply | 0 | no number |
| 2.4 An R2 fake, or a piece of one, left in the text | n.a. | 16 replies | no number |

- **2.1 Made-up placeholder.** The model writes a placeholder of its own for a value
  it does not have: `Telefono: [TELEFONO_2]` (`bank-0032`, `D4+R1`). Restoration does not guess and
  reports it. On dev it is the only cause of a reply that is not fully restored, in
  every masked configuration: `REF-oracle-direct` 4 in 1 reply, `REF-oracle` 12 in 6,
  `D1+R1` 3 in 1, `D2+R1` 1 in 1; none in `REF-none`. The full-restoration rate on dev
  therefore counts this habit of the model, not a loss of our substitutes.
- **2.2 Value given to the wrong party** (`wrong_mapping`, the sentence of the
  protocol, section 10, as it is written). The substitute goes back to its own value,
  but the model used the sender's phone, email, name or badge number as the contacts
  or the signature of the office that answers: `al nostro servizio clienti al numero 358 044 0921`
  (`bank-0008`, `D4+R1`; the number is the customer's). The restore events are all
  `restored`: no number of the scorecard sees it.
- **2.3 Substitute with a wrong value.** The type error of 1.4: `RPSVNZ96D27X748J. Resto`
  as the name of who signs (`hr-0003`, `D4+R1`).
- **2.4 R2 fake left in the text.** By what is left, in replies: a domain built on the
  fake company name 13, the fake badge number 6, the province code of the fake city 3,
  the place in the fake company name used as a town 3, a fake date without its year 1.
  Two causes: the model rewrites the fake (the badge number with a non-breaking hyphen,
  U+2011: `CU‑39040`, `bank-0013`) or builds a new value on it (section 3.1). The
  full-restoration rate of R2 is an upper bound and sees none of them.
- **2.5 A restored value that does not fit the sentence.** One example, outside the
  counts: `[SINDACATO_1]` stands for the adjective `sindacale`, and the reply reads
  `all’incontro organizzato da sindacale in data 16 novembre 2026` (`hr-0026`, `D4+R1`).

Not failures by themselves, and not observed. `dropped` is a substitute that is not
found in the reply (84 of 260 events in `D4+R1`, 97 of 267 in `D4+R2`): the reply did not use
the value or, under R2, wrote the fake in another form, which is a case of 2.4. On
dev no event is `restored_fuzzy` or `altered_unresolved`, and no substitute of ours is
left in a reply (approved count: 0 and 0).

## 3. Derived values

Values that the model builds on a masked value. Restoration cannot bring them back
(protocol, section 10); the scorecard counts them only where the model writes a
placeholder of its own (3.2). Examples only: where a count is given it is one of the
approved counts of 2.4. Each fake named here is in the masked text of
`results/dev/masked/D4+R2/`.

- **3.1 Built on a fake value (R2).** The fake goes back to the original, what was
  built on it stays.
  - A domain on the fake company name: `assistenza@cassaruralevalfiorita.it` under the
    restored name `Cassa Rurale di Montevago` (`bank-0034`; the fake was
    `Cassa Rurale Valfiorita`). 13 replies.
  - The province of the fake city: `13031 Pistoia (BI)` (`bank-0034`): the fake city was
    `Biella`, `Pistoia` is restored and `(BI)` stays; the postcode is not in the email.
    3 replies.
  - The place in the fake company name used as a town: `Filiale di Montalfiore`
    (`bank-0032`; the fake was `Cassa di Risparmio di Montalfiore`). 3 replies.
  - A weekday computed on a fake date: `Giovedì 20 novembre 2026` (`hr-0010`). The
    model read `5 novembre 2026`, a Thursday; 20 November 2026 is a Friday.
  - Dates set around a fake date: in the same reply `Mercoledì 4 novembre 2026` is
    offered among slots `tutte entro il 20 novembre 2026`; the model read the
    deadline as 5 November.
- **3.2 Asked of a placeholder (R1).** The model reads `[DATA_1]` for the one date of
  the email; for the two deadlines it sets, it writes placeholders of its own,
  `entro il [DATA_2] (se possibile)` and `entro il [DATA_3]` (`hr-0020`, `D4+R1`).
  They are counted in 2.1.
- **3.3 Not observed on dev: a computed amount.** No restored reply of `D4+R1` or of
  `D4+R2` holds an amount in euro that is not in the email.

## 4. Successful attacks

The attacker returns a ranking and no reason: a kind is defined by what the masked text
shows (`results/dev/masked/<configuration>/`), not by what the attacker used.

**Linkage**, top-1 at N = 25, texts linked of 20 (`per_text` of
`results/dev/metrics/linkage.json`; chance is 0.04).

| Kind | Configuration | Linked |
|---|---|---|
| 4.1 Quasi-identifiers of the author in clear | `REF-none` | 20 |
| | `REF-oracle-direct` | 19 |
| | `D2+R1` | 20 |
| | `D1+R1` | 18 |
| 4.2 Every annotated span is masked | `REF-oracle` | 10 |
| 4.3 Masked by D4 | `D4+R1` | 11 |
| | `D4+R2` | 9 |

- **4.1 Quasi-identifiers in clear.** Masking the direct identifiers alone leaves role,
  employer and city to be matched with the candidate list: `REF-oracle-direct`, which
  masks every direct identifier from the annotation, is linked on 19 texts of 20.
  D1 and D2 are in this kind for the types of 1.1: `D2+R1` leaves role and employer in
  clear, `D1+R1` the role (4.4).
- **4.2 Every annotated span masked.** What the text still shows is the type of each
  placeholder, the gender in the placeholder of a person, and the words that are not
  annotated. Example, `hr-0026`, linked under `REF-oracle`, `D4+R1` and `D4+R2`: the
  masked text holds `Richiesta permesso sindacale per [PERSONA_1_M]`,
  `ricopro la carica di [SINDACATO_1]` and `le mie attività commerciali`; the
  author is a man, an `agente di commercio`, and the candidate list shows gender, role
  and the fact of a special category.
- **4.3 Masked by D4.** 9 of the 11 texts linked under `D4+R1` are among the 10 linked
  under `REF-oracle`. D4 leaves a role or a company name in clear in 4 texts (1.2:
  `bank-0014`, `hr-0003`, `hr-0010`, `hr-0016`); 3 of them are linked under `D4+R1`, and
  2 of those under `REF-oracle` as well. The two texts linked under `D4+R1` and not
  under `REF-oracle` are `hr-0016`, with a role and a company name in clear, and
  `bank-0002`, one of the two dev texts about a loan that the profile does not hold
  (protocol, section 7).
- **Not linked.** 7 texts are linked under none of `REF-oracle`, `D4+R1` and `D4+R2`:
  all are bank texts (`bank-0008`, `bank-0010`, `bank-0013`, `bank-0015`, `bank-0024`, `bank-0032`, `bank-0035`).

**Attribute inference**, correct answers of 20 (`per_text` of
`results/dev/metrics/attributes.json`). The last column is the majority class of dev.

| Attribute | `REF-none` | `REF-oracle-direct` | `REF-oracle` | `D1+R1` | `D2+R1` | `D4+R1` | `D4+R2` | Majority |
|---|---|---|---|---|---|---|---|---|
| `city` | 20 | 20 | 3 | 3 | 3 | 3 | 5 | 6 |
| `role` | 19 | 19 | 6 | 19 | 19 | 8 | 8 | 6 |
| `employer` | 20 | 20 | 5 | 6 | 20 | 6 | 3 | 12 |
| `age_bracket` | 7 | 6 | 4 | 4 | 7 | 4 | 6 | 11 |
| `gender` | 18 | 20 | 20 | 20 | 20 | 20 | 20 | 10 |
| `health` | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 15 |

- **4.4 Read from what the detector leaves in clear.** Role under `D1+R1` and `D2+R1`
  (19 and 19): neither detector returns a role. Employer under `D2+R1` (20): D2 has no
  label for a company.
- **4.5 Not hidden by any masking**, as the protocol says (section 7). Gender is right on 20 texts of 20 under every masked configuration: R1
  placeholders reveal it on purpose, and under `D4+R2` the text shows a fake name and
  the grammar of the email. `health` is right on 20 of 20 under every
  configuration: in the health scenarios the topic reveals it.
- **Not successful.** Where the city is masked (every configuration but `REF-none`
  and `REF-oracle-direct`), city is right on 3 to 5 texts
  (six cities to choose from). The age bracket is right on 4 to 7 texts under every
  configuration, `REF-none` included, below the 11 of its majority class.
