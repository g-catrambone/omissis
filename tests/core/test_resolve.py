"""Entity resolver (task 2.3): rules only."""

import pytest

from omissis.contracts import Gender, Span, SpanType, Strategy
from omissis.replace import replace
from omissis.resolve import resolve


def spans_of(text, *wanted):
    """Spans for (value, type) pairs, each found after the previous one."""
    out, at = [], 0
    for value, type in wanted:
        start = text.index(value, at)
        at = start + len(value)
        out.append(Span(start, at, value, SpanType(type), 1.0, "GOLD"))
    return out


def summary(entities):
    return [(e.entity_id, e.canonical, [m.text for m in e.mentions], e.gender) for e in entities]


def test_full_name_surname_and_titled_surname_are_one_person():
    text = "Marco Ferri ha scritto. Ferri chiede un rinvio; il Sig. Ferri verrà lunedì."
    spans = spans_of(text, ("Marco Ferri", "PERSONA"), ("Ferri", "PERSONA"), ("Ferri", "PERSONA"))
    assert summary(resolve(spans, text)) == [
        ("PERSONA_1", "Marco Ferri", ["Marco Ferri", "Ferri", "Ferri"], Gender.M)
    ]


def test_title_inside_the_span_is_read_and_ignored_for_matching():
    text = "il Sig. Ferri e poi Marco Ferri"
    spans = spans_of(text, ("il Sig. Ferri", "PERSONA"), ("Marco Ferri", "PERSONA"))
    (person,) = resolve(spans, text)
    assert (person.canonical, person.gender, len(person.mentions)) == ("Marco Ferri", Gender.M, 2)


def test_one_surname_and_different_first_names_are_two_people():
    text = "Marco Ferri e Anna Ferri hanno firmato."
    entities = resolve(spans_of(text, ("Marco Ferri", "PERSONA"), ("Anna Ferri", "PERSONA")), text)
    assert summary(entities) == [
        ("PERSONA_1", "Marco Ferri", ["Marco Ferri"], Gender.M),
        ("PERSONA_2", "Anna Ferri", ["Anna Ferri"], Gender.F),
    ]


def test_bare_surname_joins_the_first_compatible_person():
    text = "Ferri è assente. Marco Ferri e Anna Ferri hanno firmato."
    spans = spans_of(
        text, ("Ferri", "PERSONA"), ("Marco Ferri", "PERSONA"), ("Anna Ferri", "PERSONA")
    )
    entities = resolve(spans, text)
    assert [(e.canonical, len(e.mentions)) for e in entities] == [
        ("Marco Ferri", 2),
        ("Anna Ferri", 1),
    ]
    assert sum(len(e.mentions) for e in entities) == len(spans)


def test_bare_surname_follows_the_gender_of_its_title():
    text = "Marco Ferri e Anna Ferri hanno firmato. La Sig.ra Ferri verrà lunedì."
    spans = spans_of(
        text, ("Marco Ferri", "PERSONA"), ("Anna Ferri", "PERSONA"), ("Ferri", "PERSONA")
    )
    marco, anna = resolve(spans, text)
    assert [len(marco.mentions), len(anna.mentions)] == [1, 2]


def test_first_name_alone_joins_the_full_name():
    text = "Sono Lidia Caprioli. Grazie, Lidia"
    spans = spans_of(text, ("Lidia Caprioli", "PERSONA"), ("Lidia", "PERSONA"))
    (person,) = resolve(spans, text)
    assert (person.canonical, person.gender) == ("Lidia Caprioli", Gender.F)


@pytest.mark.parametrize(
    ("text", "name", "gender"),
    [
        ("Gentile dott.ssa Paola Ricciardelli,", "Paola Ricciardelli", Gender.F),
        ("Gentile Dott. Ricciardelli,", "Ricciardelli", Gender.M),
        ("la Sig.ra Bruno", "Bruno", Gender.F),  # the title wins over the name list
        ("il Sig. Rosa", "Rosa", Gender.M),
        ("sono Bruno Ferraguti", "Bruno Ferraguti", Gender.M),  # from the name list
        ("sono Marta Zanchetti", "Marta Zanchetti", Gender.F),
        ("sono Andrea Zanchetti", "Andrea Zanchetti", Gender.UNKNOWN),  # used for both
        ("sono Zanchetti", "Zanchetti", Gender.UNKNOWN),
        ("sono Xhevdet Krasniqi", "Xhevdet Krasniqi", Gender.UNKNOWN),  # not in the lists
    ],
)
def test_gender_from_title_then_name_list_else_unknown(text, name, gender):
    (person,) = resolve(spans_of(text, (name, "PERSONA")), text)
    assert person.gender is gender


def test_other_types_merge_on_case_and_white_space():
    text = "Banca Corvalli, BANCA  CORVALLI e Banca Corvalli di Bergamo, non bergamasca; Bergamo."
    spans = spans_of(
        text,
        ("Banca Corvalli", "AZIENDA"),
        ("BANCA  CORVALLI", "AZIENDA"),
        ("Banca Corvalli", "AZIENDA"),
        ("Bergamo", "CITTA"),
        ("Bergamo", "CITTA"),
    )
    entities = resolve(list(reversed(spans)), text)
    assert [(e.entity_id, e.canonical, len(e.mentions), e.gender) for e in entities] == [
        ("AZIENDA_1", "Banca Corvalli", 3, Gender.UNKNOWN),
        ("CITTA_1", "Bergamo", 2, Gender.UNKNOWN),
    ]


def test_same_value_with_two_types_is_two_entities():
    text = "Rosa abita a Rosa."
    entities = resolve(spans_of(text, ("Rosa", "PERSONA"), ("Rosa", "CITTA")), text)
    assert [e.entity_id for e in entities] == ["PERSONA_1", "CITTA_1"]


def test_every_span_ends_up_in_exactly_one_entity_and_no_spans_give_no_entities():
    assert resolve([], "testo") == []
    text = "Marco Ferri, Ferri, Anna Ferri, Roma, roma, Marco"
    spans = spans_of(
        text,
        ("Marco Ferri", "PERSONA"),
        ("Ferri", "PERSONA"),
        ("Anna Ferri", "PERSONA"),
        ("Roma", "CITTA"),
        ("roma", "CITTA"),
        ("Marco", "PERSONA"),
    )
    entities = resolve(spans, text)
    found = sorted((m.start, m.end) for e in entities for m in e.mentions)
    assert found == sorted((s.start, s.end) for s in spans)


# --- placeholders -----------------------------------------------------------------


def test_placeholders_carry_the_gender_when_it_is_known():
    text = "Gentile dott.ssa Paola Ricciardelli, sono Alessio Mondini con Xhevdet Krasniqi."
    spans = spans_of(
        text,
        ("Paola Ricciardelli", "PERSONA"),
        ("Alessio Mondini", "PERSONA"),
        ("Xhevdet Krasniqi", "PERSONA"),
    )
    masked, _ = replace(text, resolve(spans, text), Strategy.R1, seed=1)
    assert masked == "Gentile dott.ssa [PERSONA_1_F], sono [PERSONA_2_M] con [PERSONA_3]."


def test_two_people_kept_apart_never_share_a_placeholder():
    text = "Il Sig. Ferri e la Sig.ra Ferri hanno firmato."
    spans = spans_of(text, ("Ferri", "PERSONA"), ("Ferri", "PERSONA"))
    entities = resolve(spans, text)
    assert [(e.canonical, e.gender) for e in entities] == [("Ferri", Gender.M), ("Ferri", Gender.F)]
    masked, vault = replace(text, entities, Strategy.R1, seed=1)
    assert masked == "Il Sig. [PERSONA_1_M] e la Sig.ra [PERSONA_2_F] hanno firmato."
    assert len(vault) == 2
    # The same two people in a second text of the session keep their placeholders.
    again, vault = replace(text, resolve(spans, text), Strategy.R1, seed=1, vault=vault)
    assert again == masked and len(vault) == 2
