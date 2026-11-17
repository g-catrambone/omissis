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
