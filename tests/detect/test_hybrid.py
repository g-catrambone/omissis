"""D4 hybrid (task 4.4), with fake detectors."""

import logging
from pathlib import Path

import pytest

from omissis.backends import CacheMissError
from omissis.config import ConfigError, RunConfig
from omissis.contracts import DetectorId, Span, SpanType
from omissis.detect import hybrid
from omissis.detect.merge import merge

TEXT = "Lidia Caprioli, magazziniere a Nola, 347 215 8890, deve € 320,00."
PRIORITY = [DetectorId.D0, DetectorId.D2, DetectorId.D1, DetectorId.D3]
CONFIG = RunConfig(
    detector=DetectorId.D4,
    strategy="R1",
    mask_quasi=True,
    backend="replay",
    seed=13,
    fuzzy_threshold=0.9,
    source_priority=PRIORITY,
    models_file=Path("configs/models.yaml"),
    cache_dir=Path("results/cache"),
)


def span(value, type, source, confidence=0.9):
    start = TEXT.index(value)
    reason = "test" if source == "D3" else None
    return Span(start, start + len(value), value, type, confidence, source, reason)


PHONE = span("347 215 8890", SpanType.TELEFONO, "D0")
AMOUNT_D0 = span("€ 320,00", SpanType.IMPORTO, "D0")
NAME = span("Lidia Caprioli", SpanType.PERSONA, "D2")
CITY_D2 = span("Nola", SpanType.CITTA, "D2")
ROLE = span("magazziniere", SpanType.RUOLO, "D3", 0.8)
CITY_D3 = span("Nola", SpanType.CITTA, "D3", 0.8)
AMOUNT_D3 = span("€ 320,00", SpanType.IMPORTO, "D3", 0.8)


def fakes(d3=None):
    return {
        DetectorId.D0: lambda text, config: [PHONE, AMOUNT_D0],
        DetectorId.D2: lambda text, config: [NAME, CITY_D2],
        DetectorId.D3: d3 or (lambda text, config: [ROLE, CITY_D3, AMOUNT_D3]),
    }


def raising(error):
    def find(text, config):
        raise error

    return find


def test_direct_identifiers_come_from_d0_and_d2_the_rest_from_d3():
    found = hybrid.find(TEXT, CONFIG, fakes())
    assert found == [PHONE, NAME, ROLE, CITY_D3, AMOUNT_D3]
    # The quasi-identifiers of D0 and D2 are dropped, so nothing overlaps here.
    assert merge(found, PRIORITY) == [NAME, ROLE, CITY_D3, PHONE, AMOUNT_D3]


def test_direct_identifier_from_d3_is_dropped():
    name_d3 = span("Lidia Caprioli", SpanType.PERSONA, "D3", 0.8)
    found = hybrid.find(TEXT, CONFIG, fakes(lambda text, config: [name_d3, ROLE]))
    assert found == [PHONE, NAME, ROLE]


def test_failing_d3_keeps_the_spans_of_d0_and_d2(caplog):
    with caplog.at_level(logging.ERROR):
        found = hybrid.find(TEXT, CONFIG, fakes(raising(RuntimeError(f"cannot read {TEXT}"))))
    assert found == [PHONE, NAME]
    assert "D3" in caplog.text and "RuntimeError" in caplog.text
    assert "Caprioli" not in caplog.text  # never log the text


@pytest.mark.parametrize("error", [ConfigError("d3 is not pinned"), CacheMissError("no entry")])
def test_config_error_and_cache_miss_in_d3_propagate(error):
    with pytest.raises(type(error)):
        hybrid.find(TEXT, CONFIG, fakes(raising(error)))


def test_a_missing_sub_detector_is_an_error_not_a_silent_skip():
    detectors = fakes()
    del detectors[DetectorId.D2]
    with pytest.raises(KeyError):
        hybrid.find(TEXT, CONFIG, detectors)
