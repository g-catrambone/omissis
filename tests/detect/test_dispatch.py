"""The dispatch table of `detect` and `supported_detectors` (task 4.0)."""

import logging
from pathlib import Path

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


def test_any_other_error_logs_and_returns_nothing(monkeypatch, caplog):
    fake(monkeypatch, DetectorId.D1, raising(RuntimeError(f"cannot handle {TEXT}")))
    with caplog.at_level(logging.ERROR):
        assert detect(TEXT, DetectorId.D1, CONFIG) == []
    assert "RuntimeError" in caplog.text
    assert "giulia.verdi" not in caplog.text  # never log the text


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
