"""D0 rules (task A1): curated valid and invalid sets, all synthetic.

Synthetic by construction:
- IBANs are Italian, built on bank code (ABI) 00000, which no bank uses; CIN and
  check digits are computed, so the valid ones pass every check.
- Codici fiscali use cadastral codes starting with X; Italian municipalities use
  A-M and foreign states Z, so no real person can have one of these codes.
- Partite IVA are random company numbers with a computed check digit.
"""

import pytest

from omissis.contracts import SpanType
from omissis.detect import rules

# --- IBAN -----------------------------------------------------------------------

VALID_IBANS = [
    "IT89Y0000025613651127989360",
    "IT77V0000094829785481207069",
    "IT87L0000085047953541165689",
    "IT08R0000086876CC3887493642",
    "IT56M0000020580414008222453",
    "IT04V0000068937993402541721",
    "IT10Y0000074262CC6515336977",
    "IT44K0000042966986295003154",
    # the same kind of IBAN written in groups of four, as on paper
    "IT12 C000 0077 3161 8434 3354 252",
    "IT96 R000 0021 752C C080 4751 375",
    "IT72 S000 0069 9588 7586 3486 907",
    # lower case is accepted
    "it92q0000050501506780056288",
]

INVALID_IBANS = [
    "IT88Y0000025613651127989360",  # check digits changed (89 -> 88)
    "IT77V0000094829785481207068",  # last digit changed
    "IT87L0000085047953541165698",  # two adjacent digits swapped
    "IT08R0000086876CC388749364",  # one character short
    "IT56M00000205804140082224531",  # one character too many
    "IT04V0000068937993402541712",  # last two digits swapped
    "IT10Y0001074262CC6515336977",  # bank code changed
    "IT4K40000042966986295003154",  # check digits not numeric
    "IT1220000077316184343354252",  # CIN is a digit, not a letter
    "IT00Y0000025613651127989360",  # check digits 00 are never issued
    "XX89Y0000025613651127989360",  # same digits, wrong country
]


@pytest.mark.parametrize("iban", VALID_IBANS)
def test_valid_iban_is_found(iban):
    text = f"Vi prego di accreditare la somma sull'IBAN {iban} entro venerdì."
    spans = rules.find_iban(text)
    assert [s.text for s in spans] == [iban]
    assert spans[0].type is SpanType.IBAN and spans[0].source == "D0"
    assert rules.iban_is_valid(iban)


@pytest.mark.parametrize("iban", INVALID_IBANS)
def test_invalid_iban_is_rejected(iban):
    assert not rules.iban_is_valid(iban)
    assert rules.find_iban(f"IBAN: {iban}.") == []


def test_iban_followed_by_more_groups_is_trimmed():
    text = "conto IT12 C000 0077 3161 8434 3354 252 2026 aperto"
    assert [s.text for s in rules.find_iban(text)] == ["IT12 C000 0077 3161 8434 3354 252"]


def test_iban_inside_a_longer_word_is_ignored():
    assert rules.find_iban("codiceIT89Y0000025613651127989360") == []
    assert rules.find_iban("IT89Y0000025613651127989360X") == []


# --- Codice fiscale --------------------------------------------------------------

VALID_CFS = [
    "MCMIFA82R56X537I",
    "GZMIOO51R08X837M",
    "BTPFAI59M08X124Z",
    "STNIPV92E18X513X",
    "TNVVAM68E41X671W",
    "RNVOIT62E63X523L",
    "VZNACR70M66X705E",
    "TVPPEL77T16X664Y",
    "GNLFMA59M41X462M",
    "RPZDMN57R02X979D",
    "BTPFAI59M08X12QW",  # omocodia: last digit of the place code written as a letter
    "STNIPV92E18XRMPZ",  # omocodia on all three digits of the place code
    "gsvtgb70s19x948o",  # lower case is accepted
]

INVALID_CFS = [
    "MCMIFA82R56X537J",  # wrong check character
    "GZMIOO51R08X873M",  # two digits swapped
    "BTPFAI59F08X124Z",  # F is not a month letter
    "MCMIFA82R35X537E",  # day 35, check character correct
    "MCMIFA82R00X537P",  # day 00, check character correct
    "MCMIFA82R72X537A",  # day 72, check character correct
    "GZMIOO51R32X837B",  # day 32, check character correct
    "STNIPV92E18X513",  # 15 characters
    "TN1VAM68E41X671W",  # digit in the name part
    "RNVOIT6AE63X523L",  # A is not an omocodia letter
    "VZNACR70M66X7O5E",  # letter O in place of a zero
]


@pytest.mark.parametrize("cf", VALID_CFS)
def test_valid_cf_is_found(cf):
    text = f"Il mio codice fiscale è {cf}, come da documento allegato."
    spans = rules.find_cf(text)
    assert [s.text for s in spans] == [cf]
    assert spans[0].type is SpanType.CF
    assert rules.cf_is_valid(cf)


@pytest.mark.parametrize("cf", INVALID_CFS)
def test_invalid_cf_is_rejected(cf):
    assert not rules.cf_is_valid(cf)
    assert rules.find_cf(f"C.F. {cf}") == []


def test_cf_inside_a_longer_token_is_ignored():
    assert rules.find_cf("XMCMIFA82R56X537I") == []
    assert rules.find_cf("MCMIFA82R56X537I9") == []


# --- Partita IVA -----------------------------------------------------------------

VALID_PIVAS = [
    "48768040114",
    "70091680861",
    "26863940180",
    "98319390401",
    "85178250537",
    "65499489998",  # office code 999
    "24920260676",
    "33000300492",
    "02370940146",
    "65321760103",
    "08619360459",
]

INVALID_PIVAS = [
    "48768040115",  # wrong check digit
    "70091680816",  # last two digits swapped
    "26863940108",  # last two digits swapped
    "98319390402",  # wrong check digit
    "12345670009",  # office code 000, check digit correct
    "12345671015",  # office code 101, check digit correct
    "76543215008",  # office code 500, check digit correct
    "00000000554",  # company number all zeros, check digit correct
    "8517825053",  # 10 digits
    "655994899980",  # 12 digits
]


@pytest.mark.parametrize("piva", VALID_PIVAS)
def test_valid_piva_is_found(piva):
    text = f"Fattura intestata alla ditta, partita IVA {piva}."
    spans = rules.find_piva(text)
    assert [s.text for s in spans] == [piva]
    assert spans[0].type is SpanType.PIVA
    assert rules.piva_is_valid(piva)


@pytest.mark.parametrize("piva", INVALID_PIVAS)
def test_invalid_piva_is_rejected(piva):
    assert not rules.piva_is_valid(piva)
    assert rules.find_piva(f"P.IVA {piva}") == []


def test_piva_with_it_prefix_excludes_the_prefix():
    spans = rules.find_piva("VAT IT48768040114.")
    assert [s.text for s in spans] == ["48768040114"]


# --- Telefono --------------------------------------------------------------------

VALID_PHONES = [
    "333 1234567",
    "3331234567",
    "+39 333 123 4567",
    "+393331234567",
    "0039 347 765 4321",
    "(+39) 320 111 2233",
    "339-123-4567",
    "340.123.45.67",
    "06 1234 5678",
    "02/12345678",
    "011 123 4567",
    "0471 123456",
]

NOT_PHONES = [
    "01/02/2026",  # a date
    "15.03.2026",  # a date
    "03/2026",  # month and year
    "180000",  # an amount without currency
    "00185",  # a postal code
    "33312",  # too short for a mobile
    "333 12345678901",  # too long
    "2026",
]


@pytest.mark.parametrize("phone", VALID_PHONES)
def test_valid_phone_is_found(phone):
    text = f"Potete chiamarmi al {phone} dalle 9 alle 18."
    spans = rules.find_telefono(text)
    assert [s.text for s in spans] == [phone]
    assert spans[0].type is SpanType.TELEFONO


@pytest.mark.parametrize("value", NOT_PHONES)
def test_non_phone_is_rejected(value):
    assert rules.find_telefono(f"Riferimento {value} del fascicolo.") == []


def test_phone_followed_by_a_year_is_trimmed():
    spans = rules.find_telefono("cell. 333 1234567 2026")
    assert [s.text for s in spans] == ["333 1234567"]


# --- Email -----------------------------------------------------------------------


@pytest.mark.parametrize(
    "email",
    ["giulia.verdi@example.com", "a.b-c_d+tag@mail.example.org", "UFFICIO.HR@example.net"],
)
def test_email_is_found(email):
    spans = rules.find_email(f"Scrivetemi a {email}. Grazie")
    assert [s.text for s in spans] == [email]
    assert spans[0].type is SpanType.EMAIL


@pytest.mark.parametrize("value", ["giulia@", "@example.com", "giulia.example.com", "a@b"])
def test_non_email_is_rejected(value):
    assert rules.find_email(f"contatto {value} fine") == []


# --- Importo ---------------------------------------------------------------------


@pytest.mark.parametrize(
    "amount",
    [
        "€ 1.200,50",
        "€1.200",
        "1.200,50 €",
        "180.000 euro",
        "350 Euro",
        "EUR 2.450,00",
        "75,90 EUR",
        "2,5 milioni di euro",
        "€ 30 mila",
        "1200 euro",
    ],
)
def test_amount_is_found(amount):
    spans = rules.find_importo(f"La rata è di {amount} al mese.")
    assert [s.text for s in spans] == [amount]
    assert spans[0].type is SpanType.IMPORTO


@pytest.mark.parametrize(
    "text", ["sono 50 persone", "nel 2026", "il parlamento europeo 50", "1.200,00 senza valuta"]
)
def test_non_amount_is_rejected(text):
    assert rules.find_importo(text) == []


# --- all rules on one text --------------------------------------------------------

MULTI = (
    "Buongiorno, sono titolare del conto IT89Y0000025613651127989360 "
    "(codice fiscale MCMIFA82R56X537I, P.IVA 48768040114). Vi chiedo il rimborso di "
    "€ 1.250,00 addebitati il 03/10/2026. Recapiti: 333 1234567, "
    "mail giulia.verdi@example.com."
)


def test_all_rules_on_a_multi_entity_text():
    spans = rules.find_all(MULTI)
    assert all(s.matches(MULTI) for s in spans)
    assert {(s.type, s.text) for s in spans} == {
        (SpanType.IBAN, "IT89Y0000025613651127989360"),
        (SpanType.CF, "MCMIFA82R56X537I"),
        (SpanType.PIVA, "48768040114"),
        (SpanType.IMPORTO, "€ 1.250,00"),
        (SpanType.TELEFONO, "333 1234567"),
        (SpanType.EMAIL, "giulia.verdi@example.com"),
    }


def test_curated_sets_are_large_enough():
    for valid, invalid in [
        (VALID_IBANS, INVALID_IBANS),
        (VALID_CFS, INVALID_CFS),
        (VALID_PIVAS, INVALID_PIVAS),
    ]:
        assert len(valid) >= 10 and len(invalid) >= 10


def test_valid_ibans_use_bank_code_00000():
    for iban in VALID_IBANS:
        assert iban.replace(" ", "").upper()[5:10] == "00000"


def test_valid_cfs_use_a_non_existent_place_code():
    assert all(cf.upper()[11] == "X" for cf in VALID_CFS)
