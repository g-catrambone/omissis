"""R2 realistic fakes (task 2.5) and their restoration (task 2.6)."""

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
from omissis.restore import restore
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
        ("14/02/1961", "DATA_NASCITA", r"[012]\d/02/1961"),
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
