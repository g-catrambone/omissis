"""The dispatch table of `detect` and `supported_detectors` (task 4.0)."""

from pathlib import Path
from types import SimpleNamespace

import pytest

import omissis.detect as detection
from omissis.backends import CacheMissError
from omissis.config import ConfigError, RunConfig
from omissis.contracts import DetectorId, Span, SpanType
from omissis.detect import detect, supported_detectors

CONFIG = RunConfig(
    detector=DetectorId.D0,
    strategy="R1",
    mask_quasi=False,
    backend="replay",
    seed=13,
    fuzzy_threshold=0.9,
    source_priority=[DetectorId.D0, DetectorId.D1, DetectorId.D2, DetectorId.D3],
    models_file=Path("configs/models.yaml"),
    cache_dir=Path("results/cache"),
)
TEXT = "Scrivetemi a giulia.verdi@example.com."
NOT_BUILT = [d for d in DetectorId if d not in detection._DETECTORS]


def fake(monkeypatch, detector, find, needs=()):
    """Put a fake detector in the table under `detector`."""
    monkeypatch.setitem(detection._DETECTORS, detector, detection._Detector(find, needs))


def raising(error):
    def find(text, config):
        raise error

    return find


@pytest.mark.parametrize("detector", NOT_BUILT)
def test_detector_not_in_the_table_raises_with_a_clear_message(detector):
    with pytest.raises(NotImplementedError, match=f"{detector.value} is not built yet"):
        detect(TEXT, detector, CONFIG)
    assert detector not in supported_detectors()


def test_id_taken_out_of_the_table_does_not_fall_through_to_d0(monkeypatch):
    assert detect(TEXT, DetectorId.D0, CONFIG) != []
    monkeypatch.delitem(detection._DETECTORS, DetectorId.D0)
    with pytest.raises(NotImplementedError):
        detect(TEXT, DetectorId.D0, CONFIG)
    assert DetectorId.D0 not in supported_detectors()


def test_detect_calls_the_detector_of_the_table_and_merges(monkeypatch):
    long = Span(0, 10, TEXT[0:10], SpanType.PERSONA, 0.8, "D1")
    short = Span(3, 6, TEXT[3:6], SpanType.CITTA, 1.0, "D1")
    fake(monkeypatch, DetectorId.D1, lambda text, config: [short, long])
    assert detect(TEXT, DetectorId.D1, CONFIG) == [long]


@pytest.mark.parametrize("error", [CacheMissError("no entry"), ConfigError("not pinned")])
def test_cache_miss_and_config_error_propagate(monkeypatch, error):
    fake(monkeypatch, DetectorId.D1, raising(error))
    with pytest.raises(type(error)):
        detect(TEXT, DetectorId.D1, CONFIG)


def test_failing_detector_stops_the_run(monkeypatch):
    # No spans would send the text unmasked.
    fake(monkeypatch, DetectorId.D1, raising(RuntimeError("model server answered HTTP 500")))
    with pytest.raises(RuntimeError, match="HTTP 500"):
        detect(TEXT, DetectorId.D1, CONFIG)


def test_any_other_error_is_raised_with_the_error_type_only(monkeypatch):
    fake(monkeypatch, DetectorId.D1, raising(IndexError(f"cannot handle {TEXT}")))
    with pytest.raises(RuntimeError, match=r"detector D1 failed \(IndexError\)") as raised:
        detect(TEXT, DetectorId.D1, CONFIG)
    assert "giulia.verdi" not in str(raised.value)  # the message never quotes the text


def test_missing_library_raises_config_error_and_is_not_supported(monkeypatch):
    called = []
    fake(monkeypatch, DetectorId.D1, lambda t, c: called.append(t) or [], ("omissis_no_such_lib",))
    assert DetectorId.D1 not in supported_detectors()
    with pytest.raises(ConfigError, match="omissis_no_such_lib"):
        detect(TEXT, DetectorId.D1, CONFIG)
    assert called == []


def test_supported_detectors_lists_built_detectors_without_calling_them(monkeypatch):
    assert DetectorId.D0 in supported_detectors()
    fake(monkeypatch, DetectorId.D1, raising(AssertionError("must not be called")), ("json",))
    assert DetectorId.D1 in supported_detectors()


def test_library_that_fails_to_import_at_run_time_is_a_config_error(monkeypatch):
    # Installed, but one of its modules does not load: no spans would send the text unmasked.
    error = ModuleNotFoundError("No module named 'x'", name="presidio_analyzer.nlp_engine")
    fake(monkeypatch, DetectorId.D1, raising(error))
    with pytest.raises(ConfigError, match=r"D1.*presidio_analyzer\.nlp_engine"):
        detect(TEXT, DetectorId.D1, CONFIG)


# --- The D1 adapter without Presidio: what it does to a span that goes over a line break.

LETTER = "Oggetto: ferie - Lidia Caprioli\n\nGentile Ufficio,\n\nSaluti,\n Lidia Caprioli \nN. 12"
NAME = "Lidia Caprioli"


def d1_spans(monkeypatch, start, end):
    """What the adapter makes of one person that Presidio found from `start` to `end`."""
    result = SimpleNamespace(start=start, end=end, entity_type="PERSON", score=0.85)
    engine = SimpleNamespace(analyze=lambda **_: [result])
    monkeypatch.setattr(detection.presidio, "_analyzer", lambda: engine)
    return [(s.start, s.text) for s in detection.presidio.find(LETTER, CONFIG)]


def test_d1_span_over_a_line_break_keeps_its_first_line(monkeypatch):
    first = LETTER.index(NAME)
    # The name at the end of the subject, two line breaks and the greeting, as one person.
    assert d1_spans(monkeypatch, first, LETTER.index(",")) == [(first, NAME)]


def test_d1_first_line_is_the_first_that_holds_a_character(monkeypatch):
    second = LETTER.rindex(NAME)
    # From the line break before the signature to the end: the name, without its spaces.
    assert d1_spans(monkeypatch, second - 2, len(LETTER)) == [(second, NAME)]


def test_d1_span_on_one_line_is_left_as_it_is(monkeypatch):
    second = LETTER.rindex(NAME)
    assert d1_spans(monkeypatch, second - 1, second + len(NAME) + 1) == [(second - 1, f" {NAME} ")]


def test_d1_span_of_line_breaks_only_is_dropped(monkeypatch):
    first = LETTER.index("\n")
    assert d1_spans(monkeypatch, first, first + 2) == []
