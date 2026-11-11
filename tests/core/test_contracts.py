from dataclasses import FrozenInstanceError

import pytest

from omissis.contracts import (
    GOLD_SOURCE,
    PLACEHOLDER_RE,
    TYPE_CLASS,
    DetectorId,
    DisclosureItem,
    Entity,
    Gender,
    PipelineResult,
    RestoreEvent,
    RestoreOutcome,
    Span,
    SpanClass,
    SpanType,
    make_placeholder,
    parse_placeholder,
)

TEXT = "Gentile Marco Ferri, il suo IBAN è IT00X0000000000000000000000."


def span(start=8, end=19, text="Marco Ferri", type=SpanType.PERSONA, **kw):
    return Span(
        start=start,
        end=end,
        text=text,
        type=type,
        confidence=kw.pop("confidence", 1.0),
        source=kw.pop("source", GOLD_SOURCE),
        **kw,
    )


# --- taxonomy ---


def test_every_type_has_exactly_one_class():
    assert set(TYPE_CLASS) == set(SpanType)
    assert TYPE_CLASS[SpanType.IBAN] is SpanClass.DIRECT
    assert TYPE_CLASS[SpanType.CITTA] is SpanClass.QUASI
    assert TYPE_CLASS[SpanType.SALUTE] is SpanClass.SPECIAL


def test_class_counts_match_the_spec():
    counts = {c: sum(1 for v in TYPE_CLASS.values() if v is c) for c in SpanClass}
    assert counts == {SpanClass.DIRECT: 11, SpanClass.QUASI: 8, SpanClass.SPECIAL: 8}


def test_type_labels_are_ascii():
    assert all(t.value.isascii() and t.value == t.name for t in SpanType)


def test_restore_outcome_values():
    assert {o.value for o in RestoreOutcome} == {
        "restored",
        "restored_fuzzy",
        "dropped",
        "altered_unresolved",
        "hallucinated_token",
        "wrong_mapping",
    }


# --- Span ---


def test_valid_span_matches_and_derives_class():
    s = span()
    assert s.matches(TEXT)
    assert s.cls is SpanClass.DIRECT
    assert not span(start=9, end=20, text="arco Ferri,").matches("x" * 30)


def test_span_is_frozen():
    with pytest.raises(FrozenInstanceError):
        span().start = 0


def test_span_type_from_string_label():
    assert span(type="PERSONA").type is SpanType.PERSONA
    with pytest.raises(ValueError):
        span(type="NOT_A_TYPE")


@pytest.mark.parametrize(
    ("start", "end", "text"),
    [(-1, 4, "abcde"), (5, 5, ""), (6, 5, "x"), (0, 3, "ab")],
)
def test_span_rejects_bad_offsets_or_length(start, end, text):
    with pytest.raises(ValueError):
        span(start=start, end=end, text=text)


@pytest.mark.parametrize("confidence", [-0.01, 1.01, float("nan")])
def test_span_rejects_confidence_out_of_range(confidence):
    with pytest.raises(ValueError):
        span(confidence=confidence)


def test_span_accepts_confidence_bounds():
    assert span(confidence=0.0).confidence == 0.0
    assert span(confidence=1.0).confidence == 1.0


@pytest.mark.parametrize("source", ["D0", "D1", "D2", "D4", GOLD_SOURCE])
def test_span_accepts_known_sources(source):
    assert span(source=source).source == source


@pytest.mark.parametrize("source", ["D5", "gold", "presidio", ""])
def test_span_rejects_unknown_source(source):
    with pytest.raises(ValueError):
        span(source=source)


def test_d3_span_requires_reason():
    assert span(source=DetectorId.D3, reason="nome proprio").reason == "nome proprio"
    for reason in (None, "", "   "):
        with pytest.raises(ValueError):
            span(source="D3", reason=reason)


# --- Entity ---


def test_entity_valid():
    e = Entity("PERSONA_1", SpanType.PERSONA, "Marco Ferri", (span(),), Gender.M)
    assert e.cls is SpanClass.DIRECT
    assert e.gender is Gender.M


def test_entity_defaults_to_unknown_gender_and_tuple_mentions():
    e = Entity("PERSONA_2", SpanType.PERSONA, "Marco Ferri", [span()])
    assert e.gender is Gender.UNKNOWN
    assert isinstance(e.mentions, tuple)


def test_entity_rejects_no_mentions():
    with pytest.raises(ValueError):
        Entity("PERSONA_1", SpanType.PERSONA, "Marco Ferri", ())


def test_entity_rejects_mention_of_other_type():
    iban = span(start=35, end=62, text="IT00X0000000000000000000000", type=SpanType.IBAN)
    with pytest.raises(ValueError):
        Entity("PERSONA_1", SpanType.PERSONA, "Marco Ferri", (span(), iban))


@pytest.mark.parametrize("entity_id", ["PERSONA_0", "IBAN_1", "PERSONA", "persona_1", "PERSONA_01"])
def test_entity_rejects_bad_id(entity_id):
    with pytest.raises(ValueError):
        Entity(entity_id, SpanType.PERSONA, "Marco Ferri", (span(),))


# --- results ---


def test_disclosure_item_class():
    item = DisclosureItem("[CITTA_1]", SpanType.CITTA, "D0")
    assert item.cls is SpanClass.QUASI


def _result(*outcomes):
    events = tuple(RestoreEvent(f"[X_{i}]", o) for i, o in enumerate(outcomes, 1))
    return PipelineResult("abc", "m", "r", "r", (), events)


def test_fully_restored():
    assert _result().fully_restored
    assert _result(RestoreOutcome.RESTORED, RestoreOutcome.DROPPED).fully_restored
    assert _result(RestoreOutcome.RESTORED_FUZZY).fully_restored
    assert not _result(RestoreOutcome.RESTORED, RestoreOutcome.ALTERED_UNRESOLVED).fully_restored
    assert not _result(RestoreOutcome.HALLUCINATED_TOKEN).fully_restored


# --- placeholder grammar ---


@pytest.mark.parametrize("type", list(SpanType))
@pytest.mark.parametrize("n", [1, 2, 17])
def test_placeholder_round_trip(type, n):
    token = make_placeholder(type, n)
    assert token.isascii() and PLACEHOLDER_RE.fullmatch(token)
    assert parse_placeholder(token) == (type, n, Gender.UNKNOWN)


@pytest.mark.parametrize("gender", [Gender.M, Gender.F])
def test_person_placeholder_round_trip_with_gender(gender):
    token = make_placeholder(SpanType.PERSONA, 3, gender)
    assert token == f"[PERSONA_3_{gender.value}]"
    assert parse_placeholder(token) == (SpanType.PERSONA, 3, gender)


def test_placeholder_examples():
    assert make_placeholder(SpanType.IBAN, 1) == "[IBAN_1]"
    assert make_placeholder(SpanType.DATA_NASCITA, 2) == "[DATA_NASCITA_2]"
    assert make_placeholder(SpanType.PERSONA, 1) == "[PERSONA_1]"


@pytest.mark.parametrize("n", [0, -1])
def test_make_placeholder_rejects_n_below_one(n):
    with pytest.raises(ValueError):
        make_placeholder(SpanType.IBAN, n)


def test_make_placeholder_rejects_gender_on_non_person():
    with pytest.raises(ValueError):
        make_placeholder(SpanType.IBAN, 1, Gender.F)


@pytest.mark.parametrize(
    "token",
    [
        "[FOO_1]",  # unknown type
        "[IBAN_1_M]",  # gender suffix on a non-person type
        "[PERSONA_1_X]",  # bad suffix
        "[IBAN_0]",  # numbers start at 1
        "[IBAN_01]",  # not canonical
        "IBAN_1",  # missing brackets
        "[iban_1]",  # lower case
        "[IBAN 1]",  # space for underscore
        "[IBAN_1] ",  # not a whole token
        "[IBAN_]",
        "",
    ],
)
def test_parse_placeholder_rejections(token):
    assert parse_placeholder(token) is None
