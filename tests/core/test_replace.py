"""R1 placeholders (task B1)."""

import pytest

from omissis.contracts import Entity, Gender, Span, SpanType, Strategy
from omissis.replace import replace
from omissis.vault import Vault


def mention(text, value, type, occurrence=0):
    start = -1
    for _ in range(occurrence + 1):
        start = text.index(value, start + 1)
    return Span(start, start + len(value), value, type, 1.0, "GOLD")


def entity(entity_id, type, mentions, gender=Gender.UNKNOWN, canonical=None):
    return Entity(entity_id, type, canonical or mentions[0].text, tuple(mentions), gender)


def test_single_entity():
    text = "Sono Lidia Caprioli, IBAN IT89Y0000025613651127989360."
    people = entity("PERSONA_1", SpanType.PERSONA, [mention(text, "Lidia Caprioli", "PERSONA")])
    iban = entity("IBAN_1", SpanType.IBAN, [mention(text, "IT89Y0000025613651127989360", "IBAN")])
    masked, vault = replace(text, [people, iban], Strategy.R1, seed=1)
    assert masked == "Sono [PERSONA_1], IBAN [IBAN_1]."
    assert vault.get("[PERSONA_1]").original == "Lidia Caprioli"
    assert vault.get("[IBAN_1]").entity_id == "IBAN_1"


def test_gender_suffix_only_when_known():
    text = "Lidia e Bruno"
    lidia = entity("PERSONA_1", SpanType.PERSONA, [mention(text, "Lidia", "PERSONA")], Gender.F)
    bruno = entity("PERSONA_2", SpanType.PERSONA, [mention(text, "Bruno", "PERSONA")])
    masked, _ = replace(text, [lidia, bruno], Strategy.R1, seed=1)
    assert masked == "[PERSONA_1_F] e [PERSONA_2]"


def test_adjacent_mentions():
    text = "Lidia Caprioli333 1234567"
    name = entity("PERSONA_1", SpanType.PERSONA, [mention(text, "Lidia Caprioli", "PERSONA")])
    phone = entity("TELEFONO_1", SpanType.TELEFONO, [mention(text, "333 1234567", "TELEFONO")])
    masked, _ = replace(text, [phone, name], Strategy.R1, seed=1)
    assert masked == "[PERSONA_1][TELEFONO_1]"


def test_several_mentions_of_one_entity_get_one_placeholder():
    text = "Caprioli scrive. Firmato: Caprioli. Ancora Caprioli"
    mentions = [mention(text, "Caprioli", "PERSONA", i) for i in range(3)]
    masked, vault = replace(
        text, [entity("PERSONA_1", SpanType.PERSONA, mentions, Gender.F)], Strategy.R1, seed=1
    )
    assert masked == "[PERSONA_1_F] scrive. Firmato: [PERSONA_1_F]. Ancora [PERSONA_1_F]"
    assert len(vault) == 1


def test_two_entities_of_one_type_get_two_numbers_in_order_of_appearance():
    text = "Da Milano a Torino, poi di nuovo Milano."
    milano = entity(
        "CITTA_1",
        SpanType.CITTA,
        [mention(text, "Milano", "CITTA", 0), mention(text, "Milano", "CITTA", 1)],
    )
    torino = entity("CITTA_2", SpanType.CITTA, [mention(text, "Torino", "CITTA")])
    masked, vault = replace(text, [torino, milano], Strategy.R1, seed=1)  # input order ignored
    assert masked == "Da [CITTA_1] a [CITTA_2], poi di nuovo [CITTA_1]."
    assert [e.surrogate for e in vault] == ["[CITTA_1]", "[CITTA_2]"]


def test_one_counter_per_type():
    text = "Lidia, Bruno, Torino"
    ents = [
        entity("PERSONA_1", SpanType.PERSONA, [mention(text, "Lidia", "PERSONA")], Gender.F),
        entity("PERSONA_2", SpanType.PERSONA, [mention(text, "Bruno", "PERSONA")], Gender.M),
        entity("CITTA_1", SpanType.CITTA, [mention(text, "Torino", "CITTA")]),
    ]
    masked, _ = replace(text, ents, Strategy.R1, seed=1)
    assert masked == "[PERSONA_1_F], [PERSONA_2_M], [CITTA_1]"


def test_vault_reused_across_two_texts():
    first = "Scrive Lidia Caprioli da Torino."
    ents1 = [
        entity("PERSONA_1", SpanType.PERSONA, [mention(first, "Lidia Caprioli", "PERSONA")]),
        entity("CITTA_1", SpanType.CITTA, [mention(first, "Torino", "CITTA")]),
    ]
    masked1, vault = replace(first, ents1, Strategy.R1, seed=1)

    second = "Bruno Neri e lidia  caprioli, entrambi a Torino."
    ents2 = [
        entity("PERSONA_1", SpanType.PERSONA, [mention(second, "Bruno Neri", "PERSONA")]),
        entity("PERSONA_2", SpanType.PERSONA, [mention(second, "lidia  caprioli", "PERSONA")]),
        entity("CITTA_1", SpanType.CITTA, [mention(second, "Torino", "CITTA")]),
    ]
    masked2, same_vault = replace(second, ents2, Strategy.R1, seed=1, vault=vault)

    assert same_vault is vault
    assert masked1 == "Scrive [PERSONA_1] da [CITTA_1]."
    # Lidia keeps her placeholder; Bruno, new in the session, gets the next number.
    assert masked2 == "[PERSONA_2] e [PERSONA_1], entrambi a [CITTA_1]."
    assert len(vault) == 3


def test_source_text_with_square_brackets():
    text = "Nota [vedi allegato] di Lidia [PERSONA_1] e [IBAN_1_X]"
    lidia = entity("PERSONA_1", SpanType.PERSONA, [mention(text, "Lidia", "PERSONA")], Gender.F)
    masked, vault = replace(text, [lidia], Strategy.R1, seed=1)
    # Brackets are left alone; number 1 is taken by the text, so Lidia gets 2.
    assert masked == "Nota [vedi allegato] di [PERSONA_2_F] [PERSONA_1] e [IBAN_1_X]"
    assert "[PERSONA_1]" not in vault


def test_no_entities_returns_the_text_unchanged():
    masked, vault = replace("Nessun dato.", [], Strategy.R1, seed=1)
    assert masked == "Nessun dato." and len(vault) == 0


def test_variants_are_recorded():
    text = "Lidia Caprioli, ovvero Caprioli"
    mentions = [mention(text, "Lidia Caprioli", "PERSONA"), mention(text, "Caprioli", "PERSONA", 1)]
    _, vault = replace(text, [entity("PERSONA_1", SpanType.PERSONA, mentions)], Strategy.R1, seed=1)
    assert vault.get("[PERSONA_1]").original_variants == ("Caprioli",)


def test_mismatched_mention_is_rejected_and_vault_untouched():
    vault = Vault()
    bad = Span(0, 5, "Bruno", SpanType.PERSONA, 1.0, "GOLD")
    with pytest.raises(ValueError):
        replace("Lidia", [entity("PERSONA_1", SpanType.PERSONA, [bad])], Strategy.R1, 1, vault)
    assert len(vault) == 0


def test_overlapping_mentions_are_rejected():
    text = "Lidia Caprioli"
    a = entity("PERSONA_1", SpanType.PERSONA, [mention(text, "Lidia Caprioli", "PERSONA")])
    b = entity("PERSONA_2", SpanType.PERSONA, [mention(text, "Caprioli", "PERSONA")])
    with pytest.raises(ValueError):
        replace(text, [a, b], Strategy.R1, seed=1)


def test_r2_is_not_built_yet():
    with pytest.raises(NotImplementedError, match="B7"):
        replace("x", [], Strategy.R2, seed=1)
