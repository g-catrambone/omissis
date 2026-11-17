"""Restore of R1 placeholders: exact and normalised steps (block 1), fuzzy step (task 2.6)."""

import pytest

from omissis.contracts import PLACEHOLDER_RE, RestoreOutcome, SpanType, VaultEntry
from omissis.restore import restore
from omissis.vault import Vault

R = RestoreOutcome


def make_vault():
    vault = Vault()
    vault.add(VaultEntry("[PERSONA_1_F]", "Lidia Caprioli", SpanType.PERSONA, "PERSONA_1"))
    vault.add(VaultEntry("[IBAN_1]", "IT89Y0000025613651127989360", SpanType.IBAN, "IBAN_1"))
    vault.add(VaultEntry("[DATA_NASCITA_1]", "14/02/1961", SpanType.DATA_NASCITA, "DATA_NASCITA_1"))
    return vault


def outcomes(events):
    return {e.surrogate: e.outcome for e in events}


def assert_no_silent_placeholder(text, events):
    """Every placeholder left in the output is the `found_as` of a reporting event."""
    reported = {e.found_as for e in events if e.outcome is not R.RESTORED}
    for match in PLACEHOLDER_RE.finditer(text):
        assert match.group() in reported, match.group()


def test_untouched_placeholders_are_restored():
    reply = "Gentile [PERSONA_1_F], l'IBAN [IBAN_1] e la data [DATA_NASCITA_1] sono corretti."
    text, events = restore(reply, make_vault(), 0.9)
    assert text == (
        "Gentile Lidia Caprioli, l'IBAN IT89Y0000025613651127989360 e la data 14/02/1961 "
        "sono corretti."
    )
    assert all(e.outcome is R.RESTORED and e.found_as is None for e in events)
    assert len(events) == 3


def test_repeated_placeholder_is_restored_everywhere_with_one_event():
    text, events = restore("[IBAN_1] e ancora [IBAN_1]", make_vault(), 0.9)
    assert text.count("IT89Y0000025613651127989360") == 2
    assert [e.outcome for e in events if e.surrogate == "[IBAN_1]"] == [R.RESTORED]


@pytest.mark.parametrize(
    "form",
    [
        "[persona_1_f]",  # changed case
        "[Persona_1_F]",
        "PERSONA_1_F",  # missing brackets
        "[PERSONA_1_F",  # one bracket missing
        "[PERSONA 1 F]",  # spaces for underscores
        "PERSONA 1 F",  # no brackets, spaces, upper case
        "[ PERSONA_1_F ]",  # spacing inside brackets
    ],
)
def test_normalised_forms_are_restored(form):
    text, events = restore(f"Cara {form}, ecco.", make_vault(), 0.9)
    assert text == "Cara Lidia Caprioli, ecco."
    assert outcomes(events)["[PERSONA_1_F]"] is R.RESTORED
    assert [e.found_as for e in events if e.surrogate == "[PERSONA_1_F]"] == [form]


def test_multiword_label_with_spaces():
    text, _ = restore("nata il [DATA NASCITA 1].", make_vault(), 0.9)
    assert text == "nata il 14/02/1961."


def test_ordinary_italian_is_not_touched():
    vault = Vault()
    vault.add(VaultEntry("[DATA_12]", "3 novembre 2026", SpanType.DATA, "DATA_12"))
    reply = "in data 12 ottobre la persona 1 ha pagato"
    text, events = restore(reply, vault, 0.9)
    assert text == reply
    assert outcomes(events) == {"[DATA_12]": R.DROPPED}


def test_placeholder_not_in_vault_is_hallucinated_and_left_in_place():
    text, events = restore("Firmato [PERSONA_7_M] e [CITTA_2]", make_vault(), 0.9)
    assert text == "Firmato [PERSONA_7_M] e [CITTA_2]"
    hallucinated = [e for e in events if e.outcome is R.HALLUCINATED_TOKEN]
    assert [e.found_as for e in hallucinated] == ["[PERSONA_7_M]", "[CITTA_2]"]
    assert_no_silent_placeholder(text, events)


def test_unbracketed_hallucination_with_underscore_is_reported():
    _, events = restore("vedi CITTA_3 qui", make_vault(), 0.9)
    assert [e.outcome for e in events if e.found_as == "CITTA_3"] == [R.HALLUCINATED_TOKEN]


@pytest.mark.parametrize("form", ["[PERSONA_1_M]", "[PERSONA_1]", "[IBAN_01]"])
def test_altered_surrogate_stays_and_is_reported(form):
    text, events = restore(f"Ciao {form}.", make_vault(), 0.9)
    assert text == f"Ciao {form}."
    altered = [e for e in events if e.outcome is R.ALTERED_UNRESOLVED]
    assert [e.found_as for e in altered] == [form]
    assert_no_silent_placeholder(text, events)


def test_surrogate_the_reply_does_not_use_is_dropped():
    text, events = restore("Grazie, a presto.", make_vault(), 0.9)
    assert text == "Grazie, a presto."
    assert set(outcomes(events).values()) == {R.DROPPED}
    assert len(events) == 3


def test_one_event_per_vault_entry_then_suspicious_tokens():
    reply = "[IBAN_1] [CITTA_9] [CITTA_9] [PERSONA_1]"
    _, events = restore(reply, make_vault(), 0.9)
    assert [(e.surrogate, e.outcome) for e in events] == [
        ("[PERSONA_1_F]", R.ALTERED_UNRESOLVED),  # one outcome per entry: no `dropped` too
        ("[IBAN_1]", R.RESTORED),
        ("[DATA_NASCITA_1]", R.DROPPED),
        ("[CITTA_9]", R.HALLUCINATED_TOKEN),
    ]


def test_adjacent_letters_do_not_form_a_token():
    text, events = restore("XPERSONA_1_F e [PERSONA_1_F]a", make_vault(), 0.9)
    assert text == "XPERSONA_1_F e Lidia Capriolia"
    assert outcomes(events)["[PERSONA_1_F]"] is R.RESTORED


def test_empty_vault_and_reply():
    assert restore("", Vault(), 0.9) == ("", [])


def test_threshold_out_of_range_is_rejected():
    with pytest.raises(ValueError):
        restore("x", Vault(), 1.5)


# --- task 2.6: escapes, hyphens, fuzzy step, final scan -------------------------------


@pytest.mark.parametrize(
    "form",
    [
        "\\[PERSONA\\_1\\_F\\]",  # Markdown escapes
        "[PERSONA\\_1\\_F]",
        "[PERSONA-1-F]",  # hyphens
        "[PERSONA\u20111\u2011F]",  # non-breaking hyphens
        "PERSONA-1-F",
    ],
)
def test_escaped_and_hyphenated_placeholders_are_restored(form):
    text, events = restore(f"Gentile {form}, grazie.", make_vault(), 0.9)
    assert text == "Gentile Lidia Caprioli, grazie."
    assert outcomes(events)["[PERSONA_1_F]"] is R.RESTORED


@pytest.mark.parametrize(
    "form", ["[PERSONNA_1_F]", "[PERSON_1_F]", "[IBANN_1]", "[DATA_NASCITTA_1]"]
)
def test_near_miss_above_the_threshold_is_restored_fuzzy(form):
    text, events = restore(f"Ciao {form}.", make_vault(), 0.9)
    assert form not in text
    fuzzy = [e for e in events if e.outcome is R.RESTORED_FUZZY]
    assert [e.found_as for e in fuzzy] == [form]
    assert_no_silent_placeholder(text, events)


@pytest.mark.parametrize("form", ["[PERS_1_F]", "[P_1_F]", "[vedi allegato 1]"])
def test_near_miss_below_the_threshold_is_left_alone(form):
    text, events = restore(f"Ciao {form}.", make_vault(), 0.9)
    assert text == f"Ciao {form}."
    assert R.RESTORED_FUZZY not in outcomes(events).values()
    assert_no_silent_placeholder(text, events)


def test_fuzzy_never_changes_the_number():
    vault = make_vault()
    vault.add(VaultEntry("[IBAN_2]", "IT77V0000094829785481207069", SpanType.IBAN, "IBAN_2"))
    # One wrong letter is close to both IBAN placeholders; the digit decides.
    text, events = restore("Vecchio [IBAM_2], nuovo [IBAM_3].", vault, 0.8)
    assert text == "Vecchio IT77V0000094829785481207069, nuovo [IBAM_3]."
    assert outcomes(events)["[IBAN_2]"] is R.RESTORED_FUZZY
    assert outcomes(events)["[IBAN_1]"] is R.DROPPED


def test_restored_and_altered_entry_reports_the_worse_outcome():
    text, events = restore("[PERSONA_1_F] e poi [PERSONA_1_M]", make_vault(), 0.9)
    assert text == "Lidia Caprioli e poi [PERSONA_1_M]"
    person = [e for e in events if e.surrogate == "[PERSONA_1_F]"]
    assert [(e.outcome, e.found_as) for e in person] == [(R.ALTERED_UNRESOLVED, "[PERSONA_1_M]")]


def test_placeholder_shaped_token_with_an_unknown_label_has_an_event():
    text, events = restore("Vedi [ALLEGATO_2] e [IBAN_1].", make_vault(), 0.9)
    assert text == "Vedi [ALLEGATO_2] e IT89Y0000025613651127989360."
    unknown = [e for e in events if e.found_as == "[ALLEGATO_2]"]
    assert [e.outcome for e in unknown] == [R.HALLUCINATED_TOKEN]
    assert_no_silent_placeholder(text, events)


@pytest.mark.parametrize("form", ["[PERSONA_1_X]", "[PERSONA_1_FF]"])
def test_altered_token_close_to_a_placeholder_stays_in_place(form):
    text, events = restore(f"Gentile {form}.", make_vault(), 0.8)
    assert text == f"Gentile {form}."
    assert outcomes(events)["[PERSONA_1_F]"] is R.ALTERED_UNRESOLVED


def test_label_at_the_end_of_a_longer_token_is_not_ours():
    text, events = restore("Chiami il [NUMERO_IBAN_1].", make_vault(), 0.9)
    assert text == "Chiami il [NUMERO_IBAN_1]."
    assert outcomes(events)["[IBAN_1]"] is R.DROPPED
    assert outcomes(events)["[NUMERO_IBAN_1]"] is R.HALLUCINATED_TOKEN


def bigger_vault():
    vault = make_vault()
    vault.add(VaultEntry("[DATA_1]", "1 dicembre 2026", SpanType.DATA, "DATA_1"))
    vault.add(VaultEntry("[IMPORTO_1]", "€ 320,00", SpanType.IMPORTO, "IMPORTO_1"))
    vault.add(VaultEntry("[DOCUMENTO_1]", "CA12345XY", SpanType.DOCUMENTO, "DOCUMENTO_1"))
    vault.add(VaultEntry("[CITTA_1]", "Bergamo", SpanType.CITTA, "CITTA_1"))
    vault.add(VaultEntry("[ETA_1]", "52 anni", SpanType.ETA, "ETA_1"))
    vault.add(VaultEntry("[ETNIA_1]", "rom", SpanType.ETNIA, "ETNIA_1"))
    return vault


@pytest.mark.parametrize(
    "reply",
    [
        "IMPORTO 1.250,00 EURO",
        "IN DATA 1 DICEMBRE 2026 RICEVERETE CONFERMA",
        "ALLEGATI: DOCUMENTO 1 (CARTA D'IDENTITA), DOCUMENTO 2 (BUSTA PAGA)",
        "RIEPILOGO\nIBAN 1: da verificare",
        "in allegato il file documento_1.pdf",
        "Compili il campo [Numero IBAN 1] del modulo.",  # a slot written by the model
        "Scadenza: [data 1 dicembre 2026].",
        "Gentile PERSONA 1, grazie.",
    ],
)
def test_label_and_number_that_are_not_written_as_a_placeholder_are_ordinary_text(reply):
    text, events = restore(reply, bigger_vault(), 0.9)
    assert text == reply
    assert {e.outcome for e in events} == {R.DROPPED}


def test_label_with_its_italian_accent_is_restored_and_reported():
    reply = "La filiale di [CITTÀ_1] ha registrato la sua età ([ETÀ_1])."
    text, events = restore(reply, bigger_vault(), 0.9)
    assert text == "La filiale di Bergamo ha registrato la sua età (52 anni)."
    assert [(e.outcome, e.found_as) for e in events if e.surrogate in ("[CITTA_1]", "[ETA_1]")] == [
        (R.RESTORED, "[CITTÀ_1]"),
        (R.RESTORED, "[ETÀ_1]"),
    ]


@pytest.mark.parametrize("form", ["[IBAN_\n1]", "[IBAN\u00a01]", "[IBAN\u20131]"])
def test_placeholder_split_by_a_line_break_or_an_unusual_space_is_restored(form):
    text, events = restore(f"L'IBAN {form} è attivo.", make_vault(), 0.9)
    assert text == "L'IBAN IT89Y0000025613651127989360 è attivo."
    assert outcomes(events)["[IBAN_1]"] is R.RESTORED


def test_lower_case_token_in_placeholder_shape_never_stays_without_an_event():
    text, events = restore("Ha [etia_1] e [nome_2].", bigger_vault(), 0.9)
    assert text == "Ha [etia_1] e [nome_2]."
    reported = {e.found_as for e in events if e.outcome is R.HALLUCINATED_TOKEN}
    assert reported == {"[etia_1]", "[nome_2]"}


@pytest.mark.parametrize(
    ("reply", "restored"),
    [
        ("Gentile _PERSONA_1_F_, confermo.", "Gentile _Lidia Caprioli_, confermo."),
        ("Gentile __PERSONA_1_F__, confermo.", "Gentile __Lidia Caprioli__, confermo."),
        ("IBAN: _IBAN_1_", "IBAN: _IT89Y0000025613651127989360_"),
        (
            "Bonifico su IBAN_1/IBAN_1.",
            "Bonifico su IT89Y0000025613651127989360/IT89Y0000025613651127989360.",
        ),
        ("Gentile PERSONA_1_F.Grazie", "Gentile Lidia Caprioli.Grazie"),
    ],
)
def test_placeholder_in_markdown_emphasis_or_next_to_punctuation_is_restored(reply, restored):
    text, events = restore(reply, make_vault(), 0.9)
    assert text == restored
    assert {e.outcome for e in events} <= {R.RESTORED, R.DROPPED}
