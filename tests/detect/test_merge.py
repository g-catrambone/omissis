"""Span merging and the `detect` entry point (block 1)."""

import logging
from pathlib import Path

import pytest

from omissis.config import RunConfig
from omissis.contracts import DetectorId, Span, SpanType
from omissis.detect import detect, rules
from omissis.detect.merge import merge

TEXT = "abcdefghijklmnopqrstuvwxyz0123456789"
PRIORITY = [DetectorId.D0, DetectorId.D1, DetectorId.D2, DetectorId.D3]


def s(start, end, source="D0", confidence=1.0, type=SpanType.PERSONA):
    reason = "test" if source == "D3" else None
    return Span(start, end, TEXT[start:end], type, confidence, source, reason)


def spans_of(result):
    return [(x.start, x.end, x.source) for x in result]


def test_empty_input():
    assert merge([], PRIORITY) == []


def test_disjoint_spans_are_kept_and_sorted():
    assert spans_of(merge([s(10, 12), s(0, 3)], PRIORITY)) == [(0, 3, "D0"), (10, 12, "D0")]


def test_adjacent_spans_do_not_overlap():
    assert spans_of(merge([s(0, 5), s(5, 9)], PRIORITY)) == [(0, 5, "D0"), (5, 9, "D0")]


def test_nested_span_loses_to_the_longer_one():
    result = merge([s(2, 4, confidence=1.0), s(0, 10, confidence=0.1)], PRIORITY)
    assert spans_of(result) == [(0, 10, "D0")]


def test_partial_overlap_longer_wins():
    result = merge([s(0, 6), s(4, 12)], PRIORITY)
    assert spans_of(result) == [(4, 12, "D0")]


def test_identical_spans_are_deduplicated():
    assert spans_of(merge([s(3, 8), s(3, 8)], PRIORITY)) == [(3, 8, "D0")]


def test_tie_on_length_decided_by_confidence():
    result = merge([s(0, 6, "D0", 0.5), s(3, 9, "D1", 0.9)], PRIORITY)
    assert spans_of(result) == [(3, 9, "D1")]


def test_tie_on_length_and_confidence_decided_by_source_priority():
    result = merge([s(3, 9, "D2", 0.9), s(0, 6, "D1", 0.9)], PRIORITY)
    assert spans_of(result) == [(0, 6, "D1")]
    reversed_priority = [DetectorId.D2, DetectorId.D1]
    assert spans_of(merge([s(3, 9, "D2", 0.9), s(0, 6, "D1", 0.9)], reversed_priority)) == [
        (3, 9, "D2")
    ]


def test_full_tie_keeps_the_first_in_input_order():
    a, b = s(0, 6, type=SpanType.PIVA), s(0, 6, type=SpanType.TELEFONO)
    assert merge([a, b], PRIORITY) == [a]
    assert merge([b, a], PRIORITY) == [b]


def test_unlisted_source_ranks_last():
    result = merge([s(0, 6, "GOLD"), s(3, 9, "D3")], PRIORITY)
    assert spans_of(result) == [(3, 9, "D3")]


def test_a_dropped_span_is_dropped_whole():
    # The long middle span wins against both neighbours; neither is cut.
    result = merge([s(0, 5), s(3, 15), s(13, 18)], PRIORITY)
    assert spans_of(result) == [(3, 15, "D0")]


def test_result_is_non_overlapping_and_sorted():
    many = [s(i, i + w) for i in range(0, 30, 3) for w in (2, 4, 5)]
    result = merge(many, PRIORITY)
    assert all(a.end <= b.start for a, b in zip(result, result[1:], strict=False))


# --- detect ------------------------------------------------------------------------

CONFIG = RunConfig(
    detector=DetectorId.D0,
    strategy="R1",
    mask_quasi=False,
    backend="replay",
    seed=13,
    fuzzy_threshold=0.9,
    source_priority=PRIORITY,
    models_file=Path("configs/models.yaml"),
    cache_dir=Path("results/cache"),
)

SAMPLE = (
    "Gentile ufficio, il mio IBAN è IT89Y0000025613651127989360 e la partita IVA "
    "02370940146. Per il rimborso di 180.000 euro chiamate il 333 1234567 o "
    "scrivete a giulia.verdi@example.com."
)


def test_detect_d0_returns_merged_rule_spans():
    spans = detect(SAMPLE, DetectorId.D0, CONFIG)
    assert all(x.matches(SAMPLE) for x in spans)
    assert [x.start for x in spans] == sorted(x.start for x in spans)
    assert all(a.end <= b.start for a, b in zip(spans, spans[1:], strict=False))
    assert [(x.type, x.text) for x in spans] == [
        (SpanType.IBAN, "IT89Y0000025613651127989360"),
        # also an 11-digit landline by shape; the checksum type wins on confidence
        (SpanType.PIVA, "02370940146"),
        (SpanType.IMPORTO, "180.000 euro"),
        (SpanType.TELEFONO, "333 1234567"),
        (SpanType.EMAIL, "giulia.verdi@example.com"),
    ]
    assert len(rules.find_all(SAMPLE)) == 6  # the phone duplicate was merged away


ODD_TEXTS = [
    "",
    " ",
    "\n\t",
    "[[[]]]",
    "€",
    "@@@",
    "IT",
    "+39",
    "🙂" * 50,
    "è" * 10_000,
    "\x00\x01\x02",
    "IT89Y0000025613651127989360" * 3,
]


# Short ids: Windows limits the environment variable that holds the test id.
@pytest.mark.parametrize("text", ODD_TEXTS, ids=[f"odd{i}" for i in range(len(ODD_TEXTS))])
def test_detect_never_raises_on_odd_text(text):
    spans = detect(text, DetectorId.D0, CONFIG)
    assert all(x.matches(text) for x in spans)


@pytest.mark.parametrize("value", [None, 42, b"bytes", ["a list"]])
def test_detect_returns_nothing_for_non_text(value, caplog):
    with caplog.at_level(logging.WARNING):
        assert detect(value, DetectorId.D0, CONFIG) == []


def test_failing_detector_stops_the_run_without_quoting_the_text(monkeypatch):
    def broken(text):
        raise KeyError(f"cannot handle {text}")

    monkeypatch.setattr(rules, "find_all", broken)
    with pytest.raises(RuntimeError, match=r"detector D0 failed \(KeyError\)") as raised:
        detect("Mario 333 1234567", DetectorId.D0, CONFIG)
    assert "333 1234567" not in str(raised.value)
