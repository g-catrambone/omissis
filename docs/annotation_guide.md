# Annotation guide (v0)

How to tag sensitive spans in the Italian texts. The policy is fixed in
`docs/evaluation_protocol.md`, section 3; this guide applies it. The file
format is in `docs/interfaces.md`, section 5. Draft written by an agent
(task C1); the edge cases are to be rewritten by the team.

## 1. Policy in one paragraph

Tag **every** direct identifier, quasi-identifier and special-category span
with its type. Do not decide whether a quasi-identifier "should" be masked:
that is the run's `mask_quasi` switch. A span is the **shortest stretch that
carries the information**: the name without the title, the amount with its
currency, the date without the weekday. Spans never overlap and are never
nested: when two readings compete, tag the longer, more specific one (see 4.3).

## 2. Classes and types

The type labels are the ASCII values of `SpanType` in `src/omissis/contracts.py`.

### Direct identifiers — identify a person on their own

| Type | What | Examples |
|---|---|---|
| `PERSONA` | name of a person: first name, surname or both | `Lidia Caprioli`, `Caprioli`, `Lidia` |
| `IBAN` | an IBAN, spaced or compact | `IT89Y0000025613651127989360` |
| `CF` | codice fiscale | `CPRLDI84S52X537Z` |
| `PIVA` | partita IVA, without the `IT` prefix | `48768040114` |
| `TELEFONO` | phone number with its international prefix if written | `+39 328 664 1027`, `0422 518 207` |
| `EMAIL` | email address | `lidia.caprioli@example.com` |
| `INDIRIZZO` | street address: street, number, and postcode if attached | `via dei Tigli 14`, `via dei Tigli 14, 24121` |
| `DOCUMENTO` | number of an identity document: carta d'identità, passaporto, patente | `CA12345XY` |
| `CONTO` | account, card, policy or contract number that is not an IBAN | `000041227385` |
| `DATA_NASCITA` | date of birth | `14/02/1961` |
| `UTENTE` | username, customer code, employee number (matricola), badge | `NL-20417` |

### Quasi-identifiers — identify a person in combination

| Type | What | Examples |
|---|---|---|
| `AZIENDA` | a named organisation: employer, bank, shop, school as an institution | `Banca Corvalli`, `Ortelli Logistica S.r.l.` |
| `RUOLO` | job title or role | `magazziniere`, `insegnante di scuola primaria` |
| `CITTA` | city, town or village | `Bergamo`, `Nola` |
| `STRUTTURA` | a specific site or facility: hospital, clinic, branch, plant, office building | `Ospedale Maggiore`, `poliambulatorio di Pomigliano` |
| `IMPORTO` | an amount of money, with its currency | `€ 320,00`, `12.400 euro` |
| `DATA` | a calendar date other than a date of birth | `16 novembre 2026`, `1 marzo 2027` |
| `ETA` | age | `52 anni` |
| `NAZIONALITA` | nationality or citizenship | `cittadina rumena` → tag `rumena` |

### Special categories — GDPR art. 9 and 10

| Type | What | Examples |
|---|---|---|
| `SALUTE` | health: diagnosis, condition, therapy, disability, pregnancy | `ernia del disco lombare`, `fisioterapia` |
| `RELIGIONE` | religious belief or practice | `Ramadan`, `testimone di Geova` |
| `POLITICA` | political opinion or party membership | `iscritto al partito` |
| `SINDACATO` | trade-union membership or role | `delegato sindacale`, `iscritta alla CGIL` |
| `ORIENTAMENTO` | sexual orientation or sex life | `il mio compagno` only when it reveals orientation |
| `ETNIA` | racial or ethnic origin | `di origine rom` |
| `BIOMETRICO` | biometric or genetic data | `impronta digitale`, `test genetico` |
| `GIUDIZIARIO` | criminal convictions and offences | `condanna per guida in stato di ebbrezza` |

## 3. Boundaries

- **Titles out**: `dott.ssa Paola Ricciardelli` → tag `Paola Ricciardelli`.
- **Currency in**: `€ 320,00`, `89,90 euro`, `2,5 milioni di euro`.
- **Weekday out**: `lunedì 16 novembre 2026` → tag `16 novembre 2026`.
- **Prepositions and articles out**: `dal 1 marzo 2027` → `1 marzo 2027`;
  `all'Ospedale Maggiore` → `Ospedale Maggiore`; `un'ernia del disco` →
  `ernia del disco`.
- **Punctuation out**: a trailing full stop or comma is never part of a span.
- **Every mention is tagged**, including repeats and the signature.

## 4. Edge cases (to be rewritten by the team in their own words)

1. **Durations are not dates.** `venti giorni`, `da cinque anni`: not tagged.
   A year alone (`dal 2019`) is tagged `DATA` only if it locates an event in
   the person's life (start of employment, purchase of a house).
2. **Public bodies everyone deals with are not tagged**: INPS, Agenzia delle
   Entrate, "il medico di base", "l'ufficio risorse umane". They do not narrow
   down who the author is. A named local office (`sede INPS di Nola`) is
   `STRUTTURA`.
3. **A facility named after a place** is one `STRUTTURA` span
   (`poliambulatorio di Pomigliano`), not `STRUTTURA` + `CITTA`, because spans
   do not nest. When the city is separated by other words
   (`Ospedale Maggiore di Bologna`), tag `Ospedale Maggiore` as `STRUTTURA`
   and `Bologna` as `CITTA`.
4. **Bank names are `AZIENDA`**, the branch as a place is `STRUTTURA`
   (`filiale di via Roma`), the branch's city alone is `CITTA`.
5. **Other people** (a manager, a relative, a doctor) are tagged exactly like
   the author: `PERSONA` for names. A job title is `RUOLO` when it describes a
   specific person (`la mia responsabile, capo reparto amministrazione`); a
   function named in passing (`avvisare il capoturno`) and family relations
   (`mia moglie`) are not tagged.
6. **Health in passing is still `SALUTE`**: `fisioterapia`, `visita
   cardiologica`, `in gravidanza`. The reason for an absence written only as
   `malattia` is not tagged: it says nothing specific.
7. **Account numbers vs IBAN**: a full IBAN is `IBAN`; an account number on its
   own (`conto n. 000041227385`) is `CONTO`; the last four digits of a card
   (`carta che termina con 4821`) are `CONTO`.
8. **Dates of birth**: `DATA_NASCITA`, never `DATA`, and they do not go into
   the gold `dates` field (see 5).
9. **Ages written as birth years** (`classe 1972`): `ETA`.

## 5. Gold fields

| Field | Content |
|---|---|
| `intent` | equals `scenario` |
| `requested_action` | one of the two actions allowed for the scenario (protocol, section 2) |
| `amounts` | every `IMPORTO` in the text, as euro floats (`€ 1.200,50` → `1200.5`) |
| `dates` | every `DATA` in the text as `YYYY-MM-DD`; dates of birth excluded |
| `deadline` | the date by which the author asks for the action, or `null` |

## 6. Worked example (fixture `fx-hr-01`, excerpt)

> sono **Davide Sorrentino**`PERSONA`, **magazziniere**`RUOLO` del turno di
> notte nello stabilimento di **Nola**`CITTA`, matricola **NL-20417**`UTENTE`.
> Vi informo che da lunedì **16 novembre 2026**`DATA` sarò assente per
> malattia: il medico di base mi ha diagnosticato un'**ernia del disco
> lombare**`SALUTE` e mi ha prescritto riposo fino al **5 dicembre
> 2026**`DATA`. Il certificato telematico è già stato trasmesso all'INPS.

Not tagged: `turno di notte` (not a role), `lunedì` (weekday), `malattia`
(edge case 6), `medico di base` and `INPS` (edge case 2).
Gold: `intent` and `scenario` `sick_leave`, `requested_action`
`register_absence`, `dates` `["2026-11-16", "2026-12-05"]`, `amounts` `[]`,
`deadline` `null`.

## 7. Adjudications

One line per disagreement settled by the third member (protocol, section 3):
date, text id, span, decision, who decided.

| Date | Text | Span | Decision | By |
|---|---|---|---|---|
