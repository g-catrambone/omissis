"""D1 Presidio (task 4.1). Skipped where the dependency group `detect` is not installed."""

from pathlib import Path

import pytest

pytest.importorskip("presidio_analyzer")
pytest.importorskip("spacy")
pytest.importorskip("it_core_news_lg")

from omissis.config import ConfigError, load_config  # noqa: E402
from omissis.contracts import DetectorId, SpanType  # noqa: E402
from omissis.detect import detect, presidio, supported_detectors  # noqa: E402
from omissis.eval.datasets import load_texts  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
CONFIG = load_config(REPO / "configs" / "skeleton.yaml")

# Synthetic: Z999 is the place code of no foreign state, so nobody holds this code.
# Presidio rejects the X codes used elsewhere in the project (module docstring).
CF = "CPRLDI84S52Z999T"
SENTENCE = f"Mi chiamo Lidia Caprioli, abito a Bergamo e il mio codice fiscale è {CF}."


def found(text):
    return {(s.type, s.text) for s in detect(text, DetectorId.D1, CONFIG)}


def test_d1_is_supported_here():
    assert DetectorId.D1 in supported_detectors()


def test_italian_name_city_and_fiscal_code_are_found():
    spans = detect(SENTENCE, DetectorId.D1, CONFIG)
    assert {
        (SpanType.PERSONA, "Lidia Caprioli"),
        (SpanType.CITTA, "Bergamo"),
        (SpanType.CF, CF),
    } <= {(s.type, s.text) for s in spans}
    assert all(s.source == "D1" and s.matches(SENTENCE) for s in spans)
    assert all(a.end <= b.start for a, b in zip(spans, spans[1:], strict=False))


def test_italian_phone_iban_and_email_are_found():
    text = (
        "Chiamatemi al 347 215 8890, IBAN IT89Y0000025613651127989360, lidia.caprioli@example.com."
    )
    assert {
        (SpanType.TELEFONO, "347 215 8890"),
        (SpanType.IBAN, "IT89Y0000025613651127989360"),
        (SpanType.EMAIL, "lidia.caprioli@example.com"),
    } <= found(text)


def test_name_at_the_end_of_a_line_does_not_take_the_next_line():
    # spaCy joins the name to the greeting two lines below: the span keeps its first line.
    text = (
        "Oggetto: Richiesta ferie - Lidia Caprioli\n\nGentile Ufficio del Personale,\n\n"
        "vi scrivo per chiedere tre giorni di ferie."
    )
    spans = detect(text, DetectorId.D1, CONFIG)
    assert (SpanType.PERSONA, "Lidia Caprioli") in {(s.type, s.text) for s in spans}
    assert not any("\n" in s.text for s in spans)


def test_synthetic_fiscal_code_with_place_code_x_is_a_known_miss():
    assert SpanType.CF not in {t for t, _ in found("Codice fiscale CPRLDI84S52X537Z.")}


def test_every_span_type_comes_from_the_mapping():
    allowed = set(presidio.LABEL_TO_TYPE.values())
    for record in load_texts(REPO / "data" / "fixtures"):
        spans = detect(record.text, DetectorId.D1, CONFIG)
        assert spans, record.id
        assert {s.type for s in spans} <= allowed
        assert all(s.matches(record.text) for s in spans)


@pytest.mark.parametrize("text", ["", " ", "\n\t", "🙂" * 20, "[PERSONA_1]"])
def test_odd_text_gives_valid_spans(text):
    assert all(s.matches(text) for s in detect(text, DetectorId.D1, CONFIG))


def test_missing_spacy_model_is_a_config_error_not_a_download(monkeypatch):
    presidio._analyzer.cache_clear()
    monkeypatch.setattr(presidio, "SPACY_MODEL", "it_no_such_model")
    with pytest.raises(ConfigError, match="it_no_such_model"):
        detect(SENTENCE, DetectorId.D1, CONFIG)
    presidio._analyzer.cache_clear()
