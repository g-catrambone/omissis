# Error examples on dev

Step C1 of `docs/TODO.md`. The 20 dev texts, results of 22 Nov 2026 (after the fix of
the D1 span, `docs/decisions.md`). No model was called to write this file.

## 1. Restored replies: the counts of the inspection

Protocol, section 10. The 20 T1 replies of `D4+R1` and the 20 of `D4+R2` were read by
Giuseppe's AI agent (two subagents, one per strategy) and Giuseppe approved the counts
on its report (`docs/decisions.md`, 22 Nov 2026). The number of replies is solid; the
cause of each case is the judgement of one reader.

| Replies, of 20 | `D4+R1` | `D4+R2` |
|---|---|---|
| `wrong_mapping`: a value of the email where another entity's value belongs | 15 | 2 |
| of which: the model gave the value to the wrong party | 15 | 2 |
| of which: the substitute held a wrong value | 1 | 0 |
| An R2 fake left in the text | n.a. | 16 |
| of which: a domain built on the fake company name | n.a. | 13 |
| of which: the fake badge number | n.a. | 6 |
| of which: the province code of the fake city | n.a. | 3 |
| of which: the place in the fake company name used as a town | n.a. | 3 |
| of which: a fake date without its year | n.a. | 1 |
| A substitute of ours left in the text | 0 | 0 |
| Not fully restored: placeholders that the model made up in our format | 3 | 5 |

No two entities under one substitute, no fake equal to a word of the model, no
substitutes of two entities exchanged. The made-up placeholders are 6 in `D4+R1` and
13 in `D4+R2`: the `hallucinated_token` events of
`results/dev/metrics/restoration.json`.

| text | configuration | in the restored reply | what it is |
|---|---|---|---|
| `bank-0008` | `D4+R1` | `al nostro servizio clienti al numero 358 044 0921` | The customer's phone as the bank's: the model gave the value to the wrong party |
| `bank-0002` | `D4+R1` | `matricola aziendale UL-67995` | The customer's badge number as the signature of the bank |
| `hr-0003` | `D4+R1` | `RPSVNZ96D27X748J. Resto` | A fiscal code that D1 returned as a person, used as the name of who signs |
| `bank-0010` | `D4+R2` | `assistenza@bancodiroccalta.it` | A domain built on the fake company name `Banco di Roccalta` |
| `bank-0013` | `D4+R2` | `CU‑39040` | The fake badge number, written by the model with a non-breaking hyphen (U+2011) |
| `bank-0034` | `D4+R2` | `13031 Pistoia (BI)` | The province code of the fake city next to the original city |
| `bank-0032` | `D4+R1` | `[TELEFONO_2]` | A placeholder that the model made up for the phone of the office |

The restored replies are not stored. One is rebuilt in replay, from
`results/cache/cloud.jsonl`, by `omissis.eval.utility.t1_reply(record, config)` with
the record of `data/dev/<text>.json` and the configuration of `configs/eval.yaml`
loaded with `backend: replay`.

## 2. Identifiers that a detector missed

From the annotation in `data/dev/<text>.json` (`spans`) and the spans in
`results/dev/detected/<detector>/<text>.json`. `start` is the character offset of the
annotated span. An annotated span is listed when it is in one of three states, read
character by character without the white space:

- **Left in clear**: no character of the identifier is under a span.
- **Covered in part**: a piece of the identifier is left in clear.
- **Masked under another type**: fully covered, by spans of other types.

These states are not the one-to-one matching of the protocol, section 6: their counts
are not the complement of the recall in `results/dev/scorecard.md`. The texts with a
direct identifier in one of the first two states are the texts that the leak rate
counts (`leak` in the `per_text` list of `results/dev/metrics/detection.json`): 20 for
D0, 16 for D1, 20 for D2, 1 for D4. The failures of D3 (a reply that is not valid
JSON) are written to no results file and are not counted here.

Annotated spans on dev: 141 direct, 149 quasi-identifiers, 7 special category.

| Detector | left in clear | covered in part | masked under another type |
|---|---|---|---|
| D0 | 72 direct, 128 quasi, 7 special | 0 | 0 |
| D1 | 25 direct, 91 quasi, 6 special | 13 quasi | 19 direct, 4 quasi, 1 special |
| D2 | 78 direct, 125 quasi, 7 special | 34 direct | 0 |
| D3 | 122 direct, 10 quasi | 2 special | 2 direct, 6 quasi |
| D4 | 1 direct, 10 quasi | 2 special | 5 direct, 6 quasi |

D3 is told not to look for direct identifiers: the 122 it leaves in clear are not its
errors, and they are not listed below. For D4 every case is listed; for D0 to D3 the
count by type and the first three examples of each type, in the order of the text ids.

### D4

The hybrid, the detector of `D4+R1` and `D4+R2`: every case is listed.

**Left in clear**

| text | type | span | start |
|---|---|---|---|
| `bank-0014` | AZIENDA | `Credito Tirrenico` | 88 |
| `hr-0016` | AZIENDA | `Banca Altopiano` | 803 |
| `bank-0035` | DATA | `novembre 2026` | 266 |
| `bank-0035` | DATA | `15 ottobre 2026` | 898 |
| `hr-0002` | DATA | `14 novembre 2026` | 486 |
| `hr-0016` | DATA | `dicembre 2026` | 362 |
| `bank-0035` | IMPORTO | `€ 57,50` | 1011 |
| `hr-0003` | RUOLO | `Responsabile Acquisti` | 1090 |
| `hr-0010` | RUOLO | `Responsabile Acquisti` | 1239 |
| `hr-0016` | RUOLO | `responsabile acquisti` | 294 |
| `bank-0034` | UTENTE | `YO-92505` | 1206 |

**Covered in part**

| text | type | span | start | left in clear |
|---|---|---|---|---|
| `hr-0016` | SALUTE | `intervento al ginocchio con riabilitazione` | 402 | `con riabilitazione` |
| `hr-0026` | SINDACATO | `componente della rappresentanza sindacale unitaria` | 266 | `componente della rappresentanza … unitaria` |

**Masked under another type**

| text | type | span | start | found as |
|---|---|---|---|---|
| `bank-0014` | CF | `SGTPNL13S51X806Z` | 886 | BIOMETRICO |
| `hr-0003` | CF | `RPSVNZ96D27X748J` | 657 | PERSONA |
| `bank-0001` | CITTA | `Pistoia` | 342 | STRUTTURA |
| `bank-0024` | CITTA | `Novara` | 187 | STRUTTURA |
| `bank-0032` | CITTA | `Cremona` | 163 | STRUTTURA |
| `bank-0032` | CITTA | `Cremona` | 1118 | STRUTTURA |
| `hr-0002` | CITTA | `Pistoia` | 826 | STRUTTURA |
| `hr-0016` | CITTA | `Novara` | 831 | STRUTTURA |
| `bank-0010` | CONTO | `PB-80503` | 675 | UTENTE |
| `bank-0001` | IBAN | `IT98T0000058217280776763333` | 189 | PERSONA |
| `bank-0008` | IBAN | `IT06R0000052125840795083093` | 174 | PERSONA |

### D0

Rules only: it looks for the types that have a fixed shape and for nothing else.

**Left in clear**

By type: PERSONA 53, AZIENDA 40, DATA 40, CITTA 25, RUOLO 22, UTENTE 18, SALUTE 6, CONTO 1, ETA 1, SINDACATO 1. Up to three examples of each:

| text | type | span | start |
|---|---|---|---|
| `bank-0001` | AZIENDA | `Banca Popolare di Rocciaviva` | 85 |
| `bank-0001` | AZIENDA | `Cooperativa Edile Pietrafitta` | 399 |
| `bank-0002` | AZIENDA | `Banca Altopiano` | 76 |
| `bank-0001` | CITTA | `Pistoia` | 342 |
| `bank-0002` | CITTA | `Pistoia` | 161 |
| `bank-0008` | CITTA | `Trapani` | 413 |
| `bank-0010` | CONTO | `PB-80503` | 675 |
| `bank-0001` | DATA | `15 dicembre 2026` | 645 |
| `bank-0001` | DATA | `30 marzo 2027` | 713 |
| `bank-0002` | DATA | `15 dicembre 2026` | 653 |
| `hr-0020` | ETA | `65 anni` | 453 |
| `bank-0001` | PERSONA | `Nicola Scarpellini` | 57 |
| `bank-0001` | PERSONA | `Nicola Scarpellini` | 126 |
| `bank-0001` | PERSONA | `Nicola Scarpellini` | 1059 |
| `bank-0001` | RUOLO | `elettricista` | 376 |
| `bank-0002` | RUOLO | `contabile` | 296 |
| `bank-0008` | RUOLO | `elettricista` | 569 |
| `bank-0001` | SALUTE | `asma bronchiale` | 470 |
| `bank-0002` | SALUTE | `emicrania cronica` | 419 |
| `hr-0002` | SALUTE | `ipertensione arteriosa` | 235 |
| `hr-0026` | SINDACATO | `componente della rappresentanza sindacale unitaria` | 266 |
| `bank-0001` | UTENTE | `KK-50663` | 848 |
| `bank-0002` | UTENTE | `UL-67995` | 904 |
| `bank-0008` | UTENTE | `WJ-93942` | 1055 |

### D1

Presidio: no label for roles, amounts, badge numbers or special categories.

**Left in clear**

By type: DATA 40, RUOLO 22, IMPORTO 21, UTENTE 14, CF 8, AZIENDA 7, SALUTE 5, TELEFONO 3, ETA 1, SINDACATO 1. Up to three examples of each:

| text | type | span | start |
|---|---|---|---|
| `bank-0002` | AZIENDA | `Banca Altopiano` | 76 |
| `bank-0008` | AZIENDA | `Banca Altopiano` | 81 |
| `bank-0013` | AZIENDA | `Banca Altopiano` | 79 |
| `bank-0001` | CF | `BMDCST55B21X401A` | 804 |
| `bank-0010` | CF | `ZLFNCT54D15X978K` | 1208 |
| `bank-0013` | CF | `VGBZNC71L27X275W` | 1089 |
| `bank-0001` | DATA | `15 dicembre 2026` | 645 |
| `bank-0001` | DATA | `30 marzo 2027` | 713 |
| `bank-0002` | DATA | `15 dicembre 2026` | 653 |
| `hr-0020` | ETA | `65 anni` | 453 |
| `bank-0001` | IMPORTO | `€ 450,00` | 620 |
| `bank-0002` | IMPORTO | `€ 450,00` | 628 |
| `bank-0008` | IMPORTO | `€ 145,00` | 342 |
| `bank-0001` | RUOLO | `elettricista` | 376 |
| `bank-0002` | RUOLO | `contabile` | 296 |
| `bank-0008` | RUOLO | `elettricista` | 569 |
| `bank-0001` | SALUTE | `asma bronchiale` | 470 |
| `bank-0002` | SALUTE | `emicrania cronica` | 419 |
| `hr-0002` | SALUTE | `ipertensione arteriosa` | 235 |
| `hr-0026` | SINDACATO | `componente della rappresentanza sindacale unitaria` | 266 |
| `bank-0001` | TELEFONO | `305 331 7289` | 979 |
| `bank-0002` | TELEFONO | `300 108 4408` | 968 |
| `bank-0016` | TELEFONO | `308 057 6591` | 1133 |
| `bank-0001` | UTENTE | `KK-50663` | 848 |
| `bank-0002` | UTENTE | `UL-67995` | 904 |
| `bank-0008` | UTENTE | `WJ-93942` | 1055 |

**Covered in part**

By type: AZIENDA 13. Up to three examples of each:

| text | type | span | start | left in clear |
|---|---|---|---|---|
| `bank-0001` | AZIENDA | `Banca Popolare di Rocciaviva` | 85 | `di` |
| `bank-0008` | AZIENDA | `Tessitura Valgrande S.r.l.` | 589 | `.` |
| `bank-0010` | AZIENDA | `Banca Popolare di Rocciaviva` | 74 | `di` |

**Masked under another type**

By type: CF 9, IBAN 5, AZIENDA 4, UTENTE 4, CONTO 1, SALUTE 1. Up to three examples of each:

| text | type | span | start | found as |
|---|---|---|---|---|
| `bank-0014` | AZIENDA | `Credito Tirrenico` | 88 | CITTA |
| `bank-0034` | AZIENDA | `Cassa Rurale di Montevago` | 73 | CITTA |
| `bank-0035` | AZIENDA | `Credito Tirrenico` | 73 | CITTA |
| `bank-0002` | CF | `DTPBGT37E51X984X` | 865 | CITTA |
| `bank-0016` | CF | `NDLMTZ55P62X312Q` | 701 | CITTA |
| `bank-0024` | CF | `NFBRVS81E49X157N` | 931 | CITTA |
| `bank-0010` | CONTO | `PB-80503` | 675 | AZIENDA |
| `bank-0001` | IBAN | `IT98T0000058217280776763333` | 189 | PERSONA |
| `bank-0008` | IBAN | `IT06R0000052125840795083093` | 174 | PERSONA |
| `bank-0010` | IBAN | `IT57J0000013140124244953600` | 179 | CITTA |
| `hr-0003` | SALUTE | `celiachia` | 334 | CITTA |
| `bank-0032` | UTENTE | `BJ-27692` | 1293 | AZIENDA |
| `hr-0002` | UTENTE | `NT-86613` | 723 | AZIENDA |
| `hr-0003` | UTENTE | `YT-67363` | 622 | AZIENDA |

### D2

The ready-made classifier: no label for companies, roles, amounts, dates or special categories.

**Left in clear**

By type: AZIENDA 40, DATA 40, RUOLO 22, IMPORTO 21, TELEFONO 18, UTENTE 18, CF 17, IBAN 12, PERSONA 12, SALUTE 6, CITTA 1, CONTO 1, ETA 1, SINDACATO 1. Up to three examples of each:

| text | type | span | start |
|---|---|---|---|
| `bank-0001` | AZIENDA | `Banca Popolare di Rocciaviva` | 85 |
| `bank-0001` | AZIENDA | `Cooperativa Edile Pietrafitta` | 399 |
| `bank-0002` | AZIENDA | `Banca Altopiano` | 76 |
| `bank-0001` | CF | `BMDCST55B21X401A` | 804 |
| `bank-0002` | CF | `DTPBGT37E51X984X` | 865 |
| `bank-0010` | CF | `ZLFNCT54D15X978K` | 1208 |
| `hr-0020` | CITTA | `Milano` | 200 |
| `bank-0010` | CONTO | `PB-80503` | 675 |
| `bank-0001` | DATA | `15 dicembre 2026` | 645 |
| `bank-0001` | DATA | `30 marzo 2027` | 713 |
| `bank-0002` | DATA | `15 dicembre 2026` | 653 |
| `hr-0020` | ETA | `65 anni` | 453 |
| `bank-0001` | IBAN | `IT98T0000058217280776763333` | 189 |
| `bank-0008` | IBAN | `IT06R0000052125840795083093` | 174 |
| `bank-0010` | IBAN | `IT57J0000013140124244953600` | 179 |
| `bank-0001` | IMPORTO | `€ 450,00` | 620 |
| `bank-0002` | IMPORTO | `€ 450,00` | 628 |
| `bank-0008` | IMPORTO | `€ 145,00` | 342 |
| `bank-0001` | PERSONA | `Nicola Scarpellini` | 57 |
| `bank-0001` | PERSONA | `Nicola Scarpellini` | 126 |
| `bank-0013` | PERSONA | `Giorgia Zamparini` | 52 |
| `bank-0001` | RUOLO | `elettricista` | 376 |
| `bank-0002` | RUOLO | `contabile` | 296 |
| `bank-0008` | RUOLO | `elettricista` | 569 |
| `bank-0001` | SALUTE | `asma bronchiale` | 470 |
| `bank-0002` | SALUTE | `emicrania cronica` | 419 |
| `hr-0002` | SALUTE | `ipertensione arteriosa` | 235 |
| `hr-0026` | SINDACATO | `componente della rappresentanza sindacale unitaria` | 266 |
| `bank-0002` | TELEFONO | `300 108 4408` | 968 |
| `bank-0008` | TELEFONO | `358 044 0921` | 901 |
| `bank-0010` | TELEFONO | `350 286 0569` | 1195 |
| `bank-0001` | UTENTE | `KK-50663` | 848 |
| `bank-0002` | UTENTE | `UL-67995` | 904 |
| `bank-0008` | UTENTE | `WJ-93942` | 1055 |

**Covered in part**

By type: EMAIL 20, PERSONA 12, TELEFONO 2. Up to three examples of each:

| text | type | span | start | left in clear |
|---|---|---|---|---|
| `bank-0001` | EMAIL | `nicola.scarpellini@example.com` | 1008 | `. … @example.com` |
| `bank-0002` | EMAIL | `teresa.dellavalle@example.com` | 1003 | `della … @example.com` |
| `bank-0008` | EMAIL | `federica.quattrocchi@example.com` | 930 | `@example.com` |
| `bank-0002` | PERSONA | `Teresa Dellavalle` | 49 | `valle` |
| `bank-0008` | PERSONA | `Federica Quattrocchi` | 51 | `Federica Qu … occhi` |
| `bank-0015` | PERSONA | `Carlotta Castellani` | 116 | `Castellani` |
| `bank-0001` | TELEFONO | `305 331 7289` | 979 | `305 331 7` |
| `hr-0003` | TELEFONO | `372 448 9836` | 767 | `372 448 9` |

### D3

The local LLM is told not to look for direct identifiers: those are not errors.

**Left in clear**

By type: DATA 4, RUOLO 3, AZIENDA 2, IMPORTO 1. Up to three examples of each:

| text | type | span | start |
|---|---|---|---|
| `bank-0014` | AZIENDA | `Credito Tirrenico` | 88 |
| `hr-0016` | AZIENDA | `Banca Altopiano` | 803 |
| `bank-0035` | DATA | `novembre 2026` | 266 |
| `bank-0035` | DATA | `15 ottobre 2026` | 898 |
| `hr-0002` | DATA | `14 novembre 2026` | 486 |
| `bank-0035` | IMPORTO | `€ 57,50` | 1011 |
| `hr-0003` | RUOLO | `Responsabile Acquisti` | 1090 |
| `hr-0010` | RUOLO | `Responsabile Acquisti` | 1239 |
| `hr-0016` | RUOLO | `responsabile acquisti` | 294 |

**Covered in part**

By type: SALUTE 1, SINDACATO 1. Up to three examples of each:

| text | type | span | start | left in clear |
|---|---|---|---|---|
| `hr-0016` | SALUTE | `intervento al ginocchio con riabilitazione` | 402 | `con riabilitazione` |
| `hr-0026` | SINDACATO | `componente della rappresentanza sindacale unitaria` | 266 | `componente della rappresentanza … unitaria` |

**Masked under another type**

By type: CITTA 6, CF 1, CONTO 1. Up to three examples of each:

| text | type | span | start | found as |
|---|---|---|---|---|
| `bank-0014` | CF | `SGTPNL13S51X806Z` | 886 | BIOMETRICO |
| `bank-0001` | CITTA | `Pistoia` | 342 | STRUTTURA |
| `bank-0024` | CITTA | `Novara` | 187 | STRUTTURA |
| `bank-0032` | CITTA | `Cremona` | 163 | STRUTTURA |
| `bank-0010` | CONTO | `PB-80503` | 675 | UTENTE |
