"""R2 realistic fakes and their restoration."""

import re
from pathlib import Path

import pytest

from omissis.config import load_eval_configs, with_overrides
from omissis.contracts import (
    TYPE_CLASS,
    Entity,
    Gender,
    RestoreOutcome,
    Span,
    SpanClass,
    SpanType,
    Strategy,
    VaultEntry,
    parse_placeholder,
)
from omissis.detect import rules
from omissis.eval.datasets import load_profiles, load_texts
from omissis.pipeline import mask
from omissis.replace import fakes, replace
from omissis.resolve import resolve
from omissis.restore import numbers, restore
from omissis.vault import Vault

REPO = Path(__file__).resolve().parents[2]
FIXTURES = load_texts(REPO / "data" / "fixtures")
R = RestoreOutcome
LISTS = ("nomi_f", "nomi_m", "cognomi", "citta", "aziende", "banche", "vie")


def one(value, type, gender=Gender.UNKNOWN, text=None):
    text = text or f"Valore: {value}."
    start = text.index(value)
    span = Span(start, start + len(value), value, SpanType(type), 1.0, "GOLD")
    return text, Entity(f"{SpanType(type).value}_1", type, value, (span,), gender)


def fake_of(value, type, seed=1, gender=Gender.UNKNOWN):
    text, entity = one(value, type, gender)
    masked, vault = replace(text, [entity], Strategy.R2, seed)
    (entry,) = vault
    assert masked == f"Valore: {entry.surrogate}."
    return entry.surrogate


# --- the fakes -----------------------------------------------------------------------


def test_same_seed_same_fakes_other_seed_other_fakes():
    record = FIXTURES[0]
    entities = resolve(record.spans, record.text)
    first, _ = replace(record.text, entities, Strategy.R2, seed=5)
    again, _ = replace(record.text, entities, Strategy.R2, seed=5)
    other, _ = replace(record.text, entities, Strategy.R2, seed=6)
    assert first == again != other


@pytest.mark.parametrize("record", FIXTURES, ids=[r.id for r in FIXTURES])
def test_no_fake_is_a_value_of_the_source_text(record):
    masked, vault = replace(record.text, resolve(record.spans, record.text), Strategy.R2, seed=3)
    for entry in vault:
        for value in (entry.surrogate, *entry.surrogate_variants):
            assert value.casefold() not in record.text.casefold()
    for span in record.spans:  # as a whole token: "1 marzo" may sit inside "21 marzo"
        assert not re.search(rf"(?<!\w){re.escape(span.text)}(?!\w)", masked), span
    surrogates = [e.surrogate for e in vault]
    assert len(set(surrogates)) == len(surrogates)


def test_a_fake_already_in_the_text_is_drawn_again():
    drawn = fake_of("Bergamo", "CITTA", seed=1)
    text, entity = one("Bergamo", "CITTA", text=f"Da Bergamo a {drawn}, e ritorno.")
    masked, vault = replace(text, [entity], Strategy.R2, seed=1)
    (entry,) = vault
    assert entry.surrogate != drawn and entry.surrogate in fakes.load_list("citta")


@pytest.mark.parametrize("seed", range(20))
def test_fake_ibans_pass_the_d0_validator_on_bank_code_00000(seed):
    iban = fake_of("IT89Y0000025613651127989360", "IBAN", seed)
    assert rules.iban_is_valid(iban) and iban[5:10] == "00000"
    assert iban != "IT89Y0000025613651127989360"


@pytest.mark.parametrize("seed", range(20))
def test_fake_fiscal_codes_are_valid_and_belong_to_no_municipality(seed):
    cf = fake_of("CPRLDI84S52X537Z", "CF", seed)
    assert rules.cf_is_valid(cf) and cf[11] == "X"


@pytest.mark.parametrize("seed", range(20))
def test_fake_partita_iva_has_a_valid_check_digit_and_an_office_never_issued(seed):
    piva = fake_of("48768040114", "PIVA", seed)
    assert re.fullmatch(r"\d{7}000\d", piva)
    assert not rules.piva_is_valid(piva)  # office 000: D0 knows it is not a real one
    total = sum(
        (d * 2 - 9 if d * 2 > 9 else d * 2) if i % 2 else d
        for i, d in enumerate(map(int, piva[:10]))
    )
    assert (10 - total % 10) % 10 == int(piva[10])


@pytest.mark.parametrize(
    ("value", "pattern"),
    [
        ("€ 320,00", r"€ [1-9]\d\d,00"),
        ("12.400 euro", r"[1-9]\d\.\d{3} euro"),
        ("2,5 milioni di euro", r"[1-9],5 milioni di euro"),
    ],
)
def test_fake_amounts_keep_the_order_of_magnitude(value, pattern):
    for seed in range(10):
        assert re.fullmatch(pattern, fake_of(value, "IMPORTO", seed))


@pytest.mark.parametrize(
    ("value", "type", "pattern"),
    [
        ("347 215 8890", "TELEFONO", r"3\d\d \d{3} \d{4}"),
        ("+39 328 664 1027", "TELEFONO", r"\+39 3\d\d \d{3} \d{4}"),
        ("0422 518 207", "TELEFONO", r"0\d{3} \d{3} \d{3}"),
        ("CA12345XY", "DOCUMENTO", r"[A-Z]{2}\d{5}[A-Z]{2}"),
        ("000041227385", "CONTO", r"\d{12}"),
        ("NL-20417", "UTENTE", r"[A-Z]{2}-\d{5}"),
        ("16 novembre 2026", "DATA", r"([1-9]|[12]\d) novembre 2026"),
        ("2026-12-01", "DATA", r"2026-12-[012]\d"),
        ("1 dicembre", "DATA", r"([2-9]|[12]\d) dicembre"),
        ("dal 16 novembre 2026", "DATA", r"dal ([1-9]|[12]\d) novembre 2026"),
        ("16.11.2026", "DATA", r"[012]\d\.11\.2026"),
        ("1/3/2027", "DATA", r"([2-9]|[12]\d)/3/2027"),
        ("6 anni", "ETA", r"([1-9]|1[01]) anni"),
        ("52 anni", "ETA", r"(4[7-9]|5[0-7]) anni"),
        ("lidia.caprioli@example.com", "EMAIL", r"[a-z]+\.[a-z]+@example\.com"),
        ("via dei Tigli 14", "INDIRIZZO", r"(via|viale|corso|piazza) .+ \d+"),
    ],
)
def test_fakes_keep_the_shape_of_the_value(value, type, pattern):
    for seed in range(10):
        fake = fake_of(value, type, seed)
        assert re.fullmatch(pattern, fake), fake
        assert fake != value


def test_people_get_a_name_of_the_same_gender():
    for seed in range(10):
        woman = fake_of("Lidia Caprioli", "PERSONA", seed, Gender.F).split()
        man = fake_of("Bruno Ferraguti", "PERSONA", seed, Gender.M).split()
        assert woman[0] in fakes.load_list("nomi_f") and man[0] in fakes.load_list("nomi_m")
        assert woman[1] in fakes.load_list("cognomi")
    assert fake_of("Ferri", "PERSONA") in fakes.load_list("cognomi")


def test_banks_get_a_bank_and_employers_an_employer():
    assert fake_of("Banca Corvalli", "AZIENDA") in fakes.load_list("banche")
    assert fake_of("Credito Valdorsa", "AZIENDA") in fakes.load_list("banche")
    assert fake_of("Ortelli Logistica S.r.l.", "AZIENDA") in fakes.load_list("aziende")


def test_types_without_a_fake_keep_the_placeholder():
    assert fakes.NO_FAKE >= {t for t, c in TYPE_CLASS.items() if c is SpanClass.SPECIAL}
    assert fake_of("magazziniere", "RUOLO") == "[RUOLO_1]"
    assert fake_of("ernia del disco lombare", "SALUTE") == "[SALUTE_1]"
    # A fake date of birth would keep the month and the year: the age would stay readable.
    assert fake_of("14/02/1961", "DATA_NASCITA") == "[DATA_NASCITA_1]"
    dates = {SpanType.DATA: "16 novembre 2026", SpanType.DATA_NASCITA: "14/02/1961"}
    for type in SpanType:  # "valore 12" has the shape every generator needs, but for a date
        text, entity = one(dates.get(type, "valore 12"), type)
        _, vault = replace(text, [entity], Strategy.R2, seed=1)
        assert (parse_placeholder(next(iter(vault)).surrogate) is not None) == (
            type in fakes.NO_FAKE
        )


@pytest.mark.parametrize(
    ("value", "type"),
    [
        ("lunedì scorso", "DATA"),  # no day to move
        ("dicembre", "DATA"),
        ("2019", "DATA"),
        ("nata nel 1972", "DATA_NASCITA"),
        ("trentenne", "ETA"),  # no number
        ("milleduecento euro", "IMPORTO"),
        ("12/2026", "DATA"),  # a month and a year: the 12 is not a day
        ("2026-12", "DATA"),
        ("dicembre 2026", "DATA"),
        ("il 15 del mese", "DATA"),
        ("10:30 del 16 novembre", "DATA"),  # another number beside the date
        ("16-18 novembre", "DATA"),
    ],
)
def test_value_without_the_shape_of_its_fake_keeps_the_placeholder(value, type):
    for seed in range(5):
        assert fake_of(value, type, seed) == f"[{type}_1]"


def test_two_dates_without_a_day_are_masked_apart_and_restored():
    text = "Ho scritto lunedì scorso e parto a fine mese, non il 1 gennaio."
    spans = [
        Span(text.index(value), text.index(value) + len(value), value, SpanType.DATA, 1.0, "GOLD")
        for value in ("lunedì scorso", "fine mese")
    ]
    masked, vault = replace(text, resolve(spans, text), Strategy.R2, seed=1)
    assert masked == "Ho scritto [DATA_1] e parto a [DATA_2], non il 1 gennaio."
    restored, events = restore(masked, vault, 0.9)
    assert restored == text
    assert [e.outcome for e in events] == [R.RESTORED, R.RESTORED]


def test_no_free_fake_left_keeps_the_placeholder(monkeypatch):
    # Every draw gives a value that is already in the text.
    monkeypatch.setitem(fakes._GENERATORS, SpanType.CITTA, lambda rng, value: "Lodi")
    text, entity = one("Bergamo", "CITTA", text="Da Bergamo a Lodi.")
    masked, _ = replace(text, [entity], Strategy.R2, seed=1)
    assert masked == "Da [CITTA_1] a Lodi."


def test_person_without_a_free_fake_keeps_a_placeholder_with_the_gender(monkeypatch):
    monkeypatch.setattr(fakes, "load_list", lambda name: ("Ferri",))
    text, entity = one("Anna Ferri", "PERSONA", Gender.F, text="Scrive Anna Ferri.")
    masked, vault = replace(text, [entity], Strategy.R2, seed=1)
    assert masked == "Scrive [PERSONA_1_F]."
    again, _ = replace(text, [entity], Strategy.R2, seed=1, vault=vault)  # the same session
    assert again == masked and len(vault) == 1


def test_surname_alone_is_written_as_the_fake_surname():
    text = "Sono Marco Ferri. Il Sig. Ferri chiede un rinvio; grazie, Marco."
    spans = [
        Span(5, 16, "Marco Ferri", SpanType.PERSONA, 1.0, "GOLD"),
        Span(26, 31, "Ferri", SpanType.PERSONA, 1.0, "GOLD"),
        Span(58, 63, "Marco", SpanType.PERSONA, 1.0, "GOLD"),
    ]
    masked, vault = replace(text, resolve(spans, text), Strategy.R2, seed=2)
    (entry,) = vault
    first, surname = entry.surrogate.split()
    assert masked == f"Sono {first} {surname}. Il Sig. {surname} chiede un rinvio; grazie, {first}."
    assert (entry.original_variants, entry.surrogate_variants) == (
        ("Ferri", "Marco"),
        (surname, first),
    )
    assert restore(masked, vault, 0.9)[0] == text


def test_same_value_in_a_second_text_of_the_session_gets_the_same_fake():
    text, entity = one("Bergamo", "CITTA")
    _, vault = replace(text, [entity], Strategy.R2, seed=1)
    other, again = one("Bergamo", "CITTA", text="Abito a Bergamo.")
    masked, vault = replace(other, [again], Strategy.R2, seed=1, vault=vault)
    assert len(vault) == 1 and masked == f"Abito a {next(iter(vault)).surrogate}."


def test_lists_have_no_duplicates_and_share_nothing_with_the_fixtures():
    profiles = load_profiles(REPO / "data" / "fixtures" / "profiles.json")
    real = " ".join(
        f"{p.name} {p.city} {p.employer} {p.bank} {p.branch_city}" for p in profiles
    ).casefold()
    for name in LISTS:
        values = fakes.load_list(name)
        assert len(values) >= 8 and len(set(values)) == len(values), name
        for value in values:
            assert not re.search(rf"(?<!\w){re.escape(value.casefold())}(?!\w)", real), value
    assert not set(fakes.load_list("nomi_f")) & set(fakes.load_list("nomi_m"))


# --- restoring fakes -----------------------------------------------------------------


def r2_vault():
    vault = Vault()
    vault.add(
        VaultEntry(
            "Iris Marangoni",
            "Lidia Caprioli",
            SpanType.PERSONA,
            "PERSONA_1",
            ("Caprioli", "Lidia"),
            ("Marangoni", "Iris"),
        )
    )
    vault.add(VaultEntry("Lodi", "Bergamo", SpanType.CITTA, "CITTA_1"))
    vault.add(
        VaultEntry("IT81O0000010618943216096700", "IT89Y0000025613651127989360", "IBAN", "IBAN_1")
    )
    vault.add(VaultEntry("[RUOLO_1]", "impiegata", SpanType.RUOLO, "RUOLO_1"))
    return vault


def outcome(events):
    return {e.surrogate: (e.outcome, e.found_as) for e in events}


def test_fakes_and_placeholders_of_one_vault_are_restored_together():
    reply = "Gentile Iris Marangoni, [RUOLO_1] a Lodi: l'IBAN IT81O0000010618943216096700 è attivo."
    text, events = restore(reply, r2_vault(), 0.9)
    assert text == (
        "Gentile Lidia Caprioli, impiegata a Bergamo: l'IBAN IT89Y0000025613651127989360 è attivo."
    )
    assert all(e.outcome is R.RESTORED and e.found_as is None for e in events)
    assert len(events) == 4


def test_fake_inside_another_word_is_not_restored():
    text, events = restore("Nel Lodigiano e a Lodicchio piove.", r2_vault(), 0.9)
    assert text == "Nel Lodigiano e a Lodicchio piove."
    assert outcome(events)["Lodi"] == (R.DROPPED, None)


def test_fake_surname_alone_goes_back_to_the_surname_alone():
    text, events = restore("Gentile Sig.ra Marangoni, cara Iris,", r2_vault(), 0.9)
    assert text == "Gentile Sig.ra Caprioli, cara Lidia,"
    assert outcome(events)["Iris Marangoni"][0] is R.RESTORED


def test_fake_in_another_case_or_spacing_is_restored_and_reported():
    text, events = restore("IRIS  MARANGONI vive a lodi.", r2_vault(), 0.9)
    assert text == "Lidia Caprioli vive a Bergamo."
    assert outcome(events)["Iris Marangoni"] == (R.RESTORED, "IRIS  MARANGONI")
    assert outcome(events)["Lodi"] == (R.RESTORED, "lodi")


def test_near_miss_of_a_fake_above_the_threshold_is_restored_fuzzy():
    text, events = restore("Gentile Iris Marangon, grazie.", r2_vault(), 0.9)
    assert text == "Gentile Lidia Caprioli, grazie."
    assert outcome(events)["Iris Marangoni"] == (R.RESTORED_FUZZY, "Iris Marangon")


def test_near_miss_of_a_fake_below_the_threshold_is_not_restored():
    text, events = restore("Gentile Ines Maranghi, grazie.", r2_vault(), 0.9)
    assert text == "Gentile Ines Maranghi, grazie."
    assert outcome(events)["Iris Marangoni"] == (R.DROPPED, None)


def test_fake_number_with_another_digit_is_never_restored():
    reply = "L'IBAN IT81O0000010618943216096701 è attivo."
    text, events = restore(reply, r2_vault(), 0.5)
    assert text == reply
    assert outcome(events)["IT81O0000010618943216096700"] == (R.DROPPED, None)


def test_two_different_near_misses_are_not_a_safe_match():
    reply = "Iris Marangon oppure Iris Marangonii?"
    text, events = restore(reply, r2_vault(), 0.9)
    assert text == reply
    assert outcome(events)["Iris Marangoni"][0] is R.ALTERED_UNRESOLVED


@pytest.mark.parametrize("record", FIXTURES, ids=[r.id for r in FIXTURES])
def test_fixture_masked_with_r2_is_restored_exactly(record):
    configs = load_eval_configs(REPO / "configs" / "eval.yaml")
    config = with_overrides(configs["REF-oracle"], strategy="R2")
    result, vault = mask(record.text, config, record.spans)
    text, events = restore(result.masked_text, vault, config.fuzzy_threshold)
    assert text == record.text
    assert {e.outcome for e in events} == {R.RESTORED}
    assert len(events) == len(vault)


def test_two_children_get_two_ages_and_none_becomes_an_adult():
    text = "Ho due figli, di 6 anni e di 9 anni, e lavoro qui da 18 anni."
    spans = [
        Span(text.index(v), text.index(v) + len(v), v, SpanType.ETA, 1.0, "GOLD")
        for v in ("6 anni", "9 anni")
    ]
    masked, vault = replace(text, resolve(spans, text), Strategy.R2, seed=1)
    ages = sorted(int(e.surrogate.split()[0]) for e in vault)
    assert len(ages) == 2 and all(1 <= age <= 14 for age in ages)
    assert restore(masked, vault, 0.9)[0] == text


@pytest.mark.parametrize(
    ("written", "surname", "first"),
    [
        ("Marco De Luca", "De Luca", "Marco"),
        ("Anna Di Stefano", "Di Stefano", "Anna"),
        ("Maria Grazia Bianchi", "Bianchi", "Maria Grazia"),
        ("Sig. Marco Ferri", "Ferri", "Marco"),  # a title written inside the span
    ],
)
def test_fake_surname_and_first_name_go_back_to_the_real_ones(written, surname, first):
    text = f"Scrive {written}."
    span = Span(7, 7 + len(written), written, SpanType.PERSONA, 1.0, "GOLD")
    _, vault = replace(text, resolve([span], text), Strategy.R2, seed=1)
    (entry,) = vault
    fake_first, fake_surname = entry.surrogate.split()
    assert entry.original_variants[:2] == (surname, first)
    assert restore(f"Gentile {fake_surname}.", vault, 0.9)[0] == f"Gentile {surname}."
    assert restore(f"Cara {fake_first},", vault, 0.9)[0] == f"Cara {first},"


def fakes_vault(*entries):
    vault = Vault()
    for n, (fake, original, type) in enumerate(entries, start=1):
        vault.add(VaultEntry(fake, original, SpanType(type), f"{type}_{n}"))
    return vault


@pytest.mark.parametrize(
    ("fake", "reply"),
    [
        ("Biella", "Gentile cliente, è una bella notizia."),
        ("Chieti", "Abbiamo ricevuto i documenti chiesti."),
        ("Matera", "La normativa in materia di mutui è cambiata."),
        ("Benevento", "È un prodotto del territorio beneventano."),
    ],
)
def test_ordinary_word_close_to_a_one_word_fake_is_not_restored(fake, reply):
    text, events = restore(reply, fakes_vault((fake, "Padova", "CITTA")), 0.8)
    assert text == reply
    assert outcome(events)[fake] == (R.DROPPED, None)


def test_shortened_fake_never_takes_the_word_that_follows():
    vault = fakes_vault(("Lavorazioni Meccaniche Sbrana S.p.A.", "Sardelec Impianti", "AZIENDA"))
    reply = "La Lavorazioni Meccaniche Sbrana ha confermato il bonifico."
    text, _ = restore(reply, vault, 0.9)
    assert "ha confermato il bonifico." in text


@pytest.mark.parametrize(
    "reply",
    [
        "Il plafond della carta resta di 1.225,00 euro.",  # inside a longer number
        "Un accredito di 22.500 euro.",  # the same digits, another size
        "Il totale è 225,005 euro.",
    ],
)
def test_fake_amount_is_not_found_in_another_number(reply):
    text, events = restore(reply, fakes_vault(("225,00 euro", "245,00 euro", "IMPORTO")), 0.8)
    assert text == reply
    assert outcome(events)["225,00 euro"] == (R.DROPPED, None)


def test_altered_second_copy_of_a_fake_is_restored_whole_and_reported():
    reply = "Gentile Iris Marangoni, confermiamo. Cordiali saluti a Iris Marangon."
    text, events = restore(reply, r2_vault(), 0.9)
    assert text == "Gentile Lidia Caprioli, confermiamo. Cordiali saluti a Lidia Caprioli."
    assert outcome(events)["Iris Marangoni"] == (R.RESTORED_FUZZY, "Iris Marangon")


@pytest.mark.parametrize("marked", ["€ 320", "320", "320,00"])
def test_amount_marked_without_its_decimals_or_its_currency_is_restored(marked):
    # A detector may give only a part of "€ 320,00": what follows the fake is not ours.
    text = "La rata è pari a € 320,00 al mese."
    start = text.index(marked)
    span = Span(start, start + len(marked), marked, SpanType.IMPORTO, 0.8, "D3", "rata")
    for seed in range(5):
        masked, vault = replace(text, resolve([span], text), Strategy.R2, seed)
        restored, events = restore(masked, vault, 0.9)
        assert restored == text, masked
        assert [e.outcome for e in events] == [R.RESTORED]


def test_fake_in_markdown_underscore_emphasis_is_restored():
    reply = "Gentile _Iris Marangoni_, da _Lodi_: IBAN _IT81O0000010618943216096700_."
    text, events = restore(reply, r2_vault(), 0.9)
    assert text == "Gentile _Lidia Caprioli_, da _Bergamo_: IBAN _IT89Y0000025613651127989360_."
    assert {e.outcome for e in events} == {R.RESTORED, R.DROPPED}  # [RUOLO_1] is not used


def test_first_word_of_two_first_names_is_written_as_the_fake_first_name():
    text = "Cara Maria, la Sig.ra Maria Grazia Ferri conferma."
    spans = [
        Span(5, 10, "Maria", SpanType.PERSONA, 1.0, "GOLD"),
        Span(22, 40, "Maria Grazia Ferri", SpanType.PERSONA, 1.0, "GOLD"),
    ]
    masked, vault = replace(text, resolve(spans, text), Strategy.R2, seed=13)
    (entry,) = vault
    first, surname = entry.surrogate.split()
    assert masked == f"Cara {first}, la Sig.ra {first} {surname} conferma."
    # The fake first name goes back to the two first names, never to the whole name.
    assert (
        restore(masked, vault, 0.9)[0]
        == "Cara Maria Grazia, la Sig.ra Maria Grazia Ferri conferma."
    )


# --- an amount the reply writes in another form --------------------------------------


@pytest.mark.parametrize(
    "written",
    [
        "€ 225,00",  # the currency moved, as in the real replies of 18 Nov
        "€\u202f225,00",  # with the narrow no-break space the model uses
        "€225,00",
        "EUR 225,00",
        "225,00 EUR",
        "225,00 €",
    ],
)
def test_fake_amount_written_in_another_form_is_restored_by_its_value(written):
    vault = fakes_vault(("225,00 euro", "245,00 euro", "IMPORTO"))
    text, events = restore(f"| 5 novembre | {written} |, come richiesto.", vault, 0.9)
    assert text == "| 5 novembre | 245,00 euro |, come richiesto."
    assert outcome(events)["225,00 euro"] == (R.RESTORED, written)


@pytest.mark.parametrize("written", ["98\u202f937\u202feuro", "98\u00a0937 euro", "98937 euro"])
def test_fake_amount_with_other_thousands_separators_is_restored_by_its_value(written):
    vault = fakes_vault(("98.937 euro", "12.400 euro", "IMPORTO"))
    text, events = restore(f"Il saldo residuo (circa {written}) sarà trasferito.", vault, 0.9)
    assert text == "Il saldo residuo (circa 12.400 euro) sarà trasferito."
    assert outcome(events)["98.937 euro"] == (R.RESTORED, written)


@pytest.mark.parametrize(
    "reply",
    [
        "Il totale è 225.",  # no currency next to the number
        "Un addebito di € 226.",  # another amount
        "Un addebito di € 1.225.",  # a longer number
        "Un addebito di € 225.000.",
        "Un addebito di € 225,50.",
        "Un addebito di € 225.00.",  # a point before the decimals is not read
        "Erano 15 225 EUR.",  # read whole, as 15.225: another number
        "Rif. A1.225 EUR.",
        "Circa 225 europei.",
        "Un addebito di € 225mila.",
        "Bonifico rif. A225 EUR.",
        "Un debito di € 225 672.",  # read whole again, with the currency in front
        "| Debito | €225 672,00 |",
        "Circa € 225 mila.",
        "Circa € 225 milioni.",
    ],
)
def test_number_that_is_not_the_fake_amount_is_left_alone(reply):
    text, events = restore(reply, fakes_vault(("225 euro", "245 euro", "IMPORTO")), 0.9)
    assert text == reply
    assert outcome(events)["225 euro"] == (R.DROPPED, None)


@pytest.mark.parametrize(
    ("fake", "reply"),
    [
        ("225,00 euro", "Un addebito di € 225."),  # the decimals dropped
        ("225,00 euro", "Un addebito di 225 EUR."),
        ("225 euro", "Un addebito di € 225,00."),  # the decimals added
        ("€ 752,00 al mese", "La rata è di 752,00 € al mese."),  # more than an amount
    ],
)
def test_amount_with_other_decimals_or_inside_a_longer_fake_is_not_read(fake, reply):
    text, events = restore(reply, fakes_vault((fake, "€ 320,00 al mese", "IMPORTO")), 0.9)
    assert text == reply
    assert outcome(events)[fake] == (R.DROPPED, None)


def test_fake_amount_as_it_was_sent_is_restored_with_no_other_form_reported():
    vault = fakes_vault(("225,00 euro", "245,00 euro", "IMPORTO"))
    text, events = restore("Totale: 225,00 euro, poi € 225,00.", vault, 0.9)
    assert text == "Totale: 245,00 euro, poi 245,00 euro."
    assert outcome(events)["225,00 euro"] == (R.RESTORED, "€ 225,00")
    _, events = restore("Totale: 225,00 euro.", vault, 0.9)
    assert outcome(events)["225,00 euro"] == (R.RESTORED, None)


@pytest.mark.parametrize(
    ("reply", "restored"),
    [
        ("Erano 15 225 euro.", "Erano 12.400 euro."),
        ("| Debito | € 15 225 |", "| Debito | 12.400 euro |"),
        # the shorter fake is never taken from the head or the tail of the longer one
        ("Rata di € 15, debito di € 15 225.", "Rata di 45 euro, debito di 12.400 euro."),
        ("Debito di 15 225 EUR, più 225 EUR.", "Debito di 12.400 euro, più 80 euro."),
        # with the decimals added it is not the number that was sent: nothing is touched
        ("Debito di €15 225,00.", "Debito di €15 225,00."),
    ],
)
def test_fake_amount_with_its_thousands_after_a_plain_space_is_read_whole(reply, restored):
    vault = fakes_vault(
        ("15.225 euro", "12.400 euro", "IMPORTO"),
        ("15 euro", "45 euro", "IMPORTO"),
        ("225 euro", "80 euro", "IMPORTO"),
    )
    assert restore(reply, vault, 0.9)[0] == restored


def test_fake_amount_after_a_number_that_is_not_its_thousands_is_restored_as_before():
    # "il 15 225 euro" is read as 15.225, which is no fake; the step on the whole fakes
    # then finds "225 euro", as it did before the amounts were read as numbers.
    vault = fakes_vault(("225 euro", "80 euro", "IMPORTO"))
    assert restore("Entro il 15 225 euro.", vault, 0.9)[0] == "Entro il 15 80 euro."


@pytest.mark.parametrize(
    ("text", "read"),
    [
        ("1.250,00 euro", [("1250", "00")]),
        ("98 937 euro e 15 rate", [("98937", ""), ("15", "")]),
        ("il 3 e il 12,5", [("3", ""), ("12", "5")]),
        ("€ 19.99", []),  # a point before the decimals: not a number as Italian writes it
        ("1250.00 euro", []),
    ],
)
def test_numbers_are_read_as_italian_writes_them(text, read):
    assert numbers(text) == read


@pytest.mark.parametrize("value", ["€ 19.99", "1250.00 euro", "€ 12,345", "€ 1.2.3"])
def test_amount_that_is_not_read_as_a_number_still_gets_a_fake_and_comes_back(value):
    text = f"Importo: {value}, grazie."
    span = Span(9, 9 + len(value), value, SpanType.IMPORTO, 1.0, "GOLD")
    for seed in (1, 2, 3):
        masked, vault = replace(text, resolve([span], text), Strategy.R2, seed)
        assert masked != text
        assert restore(masked, vault, 0.9)[0] == text


def test_fake_amount_with_the_number_of_an_original_is_not_read_as_a_number():
    # The fake of the first amount has the number of the second original. A placeholder
    # puts that original back before the amounts are read: it must not be taken for the fake.
    vault = fakes_vault(("€ 37,00", "€ 80,00", "IMPORTO"), ("[IMPORTO_1]", "37,00 euro", "IMPORTO"))
    text, events = restore("Un bollo di [IMPORTO_1] e una rata di € 37,00.", vault, 0.9)
    assert text == "Un bollo di 37,00 euro e una rata di € 80,00."
    assert {o for o, _ in outcome(events).values()} == {R.RESTORED}
    # Two fakes, each with the number of the other's original, in another shape.
    vault = fakes_vault(("€ 37,00", "€ 80,00", "IMPORTO"), ("80,00 euro", "37,00 euro", "IMPORTO"))
    text, _ = restore("Una rata di € 37,00 e un bollo di 80,00 euro.", vault, 0.9)
    assert text == "Una rata di € 80,00 e un bollo di 37,00 euro."


@pytest.mark.parametrize(
    ("reply", "restored"),
    [
        # the longer fake rewritten with the currency in front starts like the shorter one
        ("Pari a €89.407, poi 89 euro.", "Pari a 74.281 Euro, poi €38."),
        # with a no-break space it ends like the third
        ("Saldo di 89\u202f407 Euro e 407 euro.", "Saldo di 74.281 Euro e 120 euro."),
    ],
)
def test_fake_amount_is_never_found_inside_another_fake_amount_rewritten(reply, restored):
    vault = fakes_vault(
        ("€89", "€38", "IMPORTO"),
        ("89.407 Euro", "74.281 Euro", "IMPORTO"),
        ("407 euro", "120 euro", "IMPORTO"),
    )
    assert restore(reply, vault, 0.9)[0] == restored


def test_two_fake_amounts_that_differ_in_the_decimals_only_are_not_read_as_numbers():
    # "€39" may be the first fake, or the second without its decimals.
    vault = fakes_vault(("€ 39", "€ 59", "IMPORTO"), ("€ 39,00", "€ 64,00", "IMPORTO"))
    for reply in ("Importo: €39.", "Importo: 39,00 EUR."):
        text, events = restore(reply, vault, 0.9)
        assert text == reply
        assert {o for o, _ in outcome(events).values()} == {R.DROPPED}
    # As they were sent, both are still restored.
    assert restore("Prima € 39, poi € 39,00.", vault, 0.9)[0] == "Prima € 59, poi € 64,00."


def test_two_fake_amounts_of_one_value_are_not_restored_by_their_value():
    vault = fakes_vault(("€ 50,00", "€ 80,00", "IMPORTO"), ("50,00 euro", "70,00 euro", "IMPORTO"))
    reply = "Un totale di 50,00 EUR."
    text, events = restore(reply, vault, 0.9)
    assert text == reply
    assert {o for o, _ in outcome(events).values()} == {R.DROPPED}


def test_amounts_rewritten_by_the_model_go_back_to_the_real_ones():
    text = "Contesto due addebiti: 89,90 euro e 245,00 euro."
    spans = [
        Span(text.index(v), text.index(v) + len(v), v, SpanType.IMPORTO, 1.0, "GOLD")
        for v in ("89,90 euro", "245,00 euro")
    ]
    for seed in range(5):
        masked, vault = replace(text, resolve(spans, text), Strategy.R2, seed)
        first, second = (entry.surrogate.removesuffix(" euro") for entry in vault)
        reply = f"| Importo |\n| €\u202f{first} |\n| €\u202f{second} |"
        restored, events = restore(reply, vault, 0.9)
        assert restored == "| Importo |\n| 89,90 euro |\n| 245,00 euro |", masked
        assert [e.outcome for e in events] == [R.RESTORED, R.RESTORED]


def test_fake_amount_never_has_the_number_of_another_amount_or_of_the_text():
    # "€ 98,00" and "98 Euro" are two strings and one number, with or without the
    # decimals: a reply that writes the first as "98 euro" could not be restored safely.
    text = "Il 15 marzo ho versato € 91,00, poi 58 Euro."
    spans = [
        Span(text.index(v), text.index(v) + len(v), v, SpanType.IMPORTO, 1.0, "GOLD")
        for v in ("€ 91,00", "58 Euro")
    ]
    in_text = {whole for whole, _ in numbers(text)}
    for seed in range(400):
        _, vault = replace(text, resolve(spans, text), Strategy.R2, seed)
        first, second = ({whole for whole, _ in numbers(e.surrogate)} for e in vault)
        assert first.isdisjoint(second), seed
        assert (first | second).isdisjoint(in_text), seed


@pytest.mark.parametrize(
    ("reply", "restored"),
    [
        ("Rate di € 225, 300 e 400.", "Rate di 245 euro, 300 e 400."),
        ("Rata di € 225 e 12 rate.", "Rata di 245 euro e 12 rate."),
        ("1. € 225\n2. Secondo punto", "1. 245 euro\n2. Secondo punto"),
        ("Rata di € 225 1000 volte.", "Rata di 245 euro 1000 volte."),
    ],
)
def test_fake_amount_before_another_number_that_is_not_its_thousands_is_restored(reply, restored):
    assert restore(reply, fakes_vault(("225 euro", "245 euro", "IMPORTO")), 0.9)[0] == restored


@pytest.mark.parametrize(
    "value", ["98 937 euro", "€ 320,00 al mese per 12 mesi", "1.250,00 euro (rata 3)"]
)
def test_amount_with_more_than_one_number_still_gets_a_fake(value):
    # Only the number that is drawn is compared with the numbers of the text.
    text = f"Importo: {value}."
    span = Span(9, 9 + len(value), value, SpanType.IMPORTO, 1.0, "GOLD")
    for seed in (1, 2, 3):
        masked, vault = replace(text, resolve([span], text), Strategy.R2, seed)
        (entry,) = vault
        assert not entry.surrogate.startswith("["), entry.surrogate
        assert restore(masked, vault, 0.9)[0] == text
