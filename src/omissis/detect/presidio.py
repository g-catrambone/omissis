"""D1: Microsoft Presidio with an Italian spaCy pipeline (task 4.1).

Presidio runs as it ships: the spaCy model `it_core_news_lg` for names, places and
organisations, plus Presidio's predefined pattern recognisers loaded for Italian.
English is the default language of every part of Presidio, so the language, the
model and the phone region are set here explicitly. Nothing is tuned to our texts.

Presidio label -> our type:

| Presidio | Type | Found by |
|---|---|---|
| `PERSON` | PERSONA | spaCy `PER` |
| `LOCATION` | CITTA | spaCy `LOC` (any place, not only towns) |
| `ORGANIZATION` | AZIENDA | spaCy `ORG` |
| `DATE_TIME` | DATA | date patterns (numeric dates only; the model has no date label) |
| `EMAIL_ADDRESS` | EMAIL | pattern |
| `IBAN_CODE` | IBAN | pattern and checksum |
| `IT_FISCAL_CODE` | CF | pattern and check character |
| `IT_VAT_CODE` | PIVA | pattern and check digit |
| `PHONE_NUMBER` | TELEFONO | `phonenumbers`, region IT |
| `IT_IDENTITY_CARD`, `IT_PASSPORT`, `IT_DRIVER_LICENSE` | DOCUMENTO | pattern |

Unmapped Presidio labels, not requested: `URL`, `IP_ADDRESS`, `MAC_ADDRESS`,
`CREDIT_CARD`, `CRYPTO`, `MEDICAL_LICENSE` (no counterpart in our taxonomy);
`NRP`, `AGE`, `ID`, `EMAIL` (spaCy labels that the Italian model never emits).
The spaCy label `MISC` is not mapped by Presidio.

Our types with no Presidio label, never found by D1: INDIRIZZO, CONTO,
DATA_NASCITA, UTENTE, RUOLO, STRUTTURA, IMPORTO, ETA, NAZIONALITA and every
special category.

Known limit: Presidio's fiscal-code pattern accepts only the place codes of real
municipalities (A-M) and foreign states (Z). The synthetic codes of this project
use the unassigned letter X, so D1 does not find them.
"""

from __future__ import annotations

from functools import lru_cache
from importlib.util import find_spec
from typing import Any

from omissis.config import ConfigError, RunConfig
from omissis.contracts import DetectorId, Span, SpanType

SOURCE = DetectorId.D1.value
SPACY_MODEL = "it_core_news_lg"
# Modules D1 imports; `detect` reports a missing one as a `ConfigError`.
NEEDS = ("presidio_analyzer", "spacy", SPACY_MODEL)

LABEL_TO_TYPE: dict[str, SpanType] = {
    "PERSON": SpanType.PERSONA,
    "LOCATION": SpanType.CITTA,
    "ORGANIZATION": SpanType.AZIENDA,
    "DATE_TIME": SpanType.DATA,
    "EMAIL_ADDRESS": SpanType.EMAIL,
    "IBAN_CODE": SpanType.IBAN,
    "IT_FISCAL_CODE": SpanType.CF,
    "IT_VAT_CODE": SpanType.PIVA,
    "PHONE_NUMBER": SpanType.TELEFONO,
    "IT_IDENTITY_CARD": SpanType.DOCUMENTO,
    "IT_PASSPORT": SpanType.DOCUMENTO,
    "IT_DRIVER_LICENSE": SpanType.DOCUMENTO,
}


@lru_cache(maxsize=1)
def _analyzer() -> Any:
    """The Presidio analyser for Italian, built once per process."""
    if find_spec(SPACY_MODEL) is None:
        # Presidio would download a missing model: refuse instead.
        raise ConfigError(
            f"spaCy model {SPACY_MODEL} is not installed: run `uv sync --locked --group detect`"
        )
    from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
    from presidio_analyzer.nlp_engine import NlpEngineProvider
    from presidio_analyzer.predefined_recognizers import PhoneRecognizer

    nlp_engine = NlpEngineProvider(
        nlp_configuration={
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "it", "model_name": SPACY_MODEL}],
        }
    ).create_engine()
    registry = RecognizerRegistry(supported_languages=["it"])
    registry.load_predefined_recognizers(languages=["it"], nlp_engine=nlp_engine)
    # The predefined phone recogniser checks a list of regions without Italy.
    registry.remove_recognizer("PhoneRecognizer")
    registry.add_recognizer(PhoneRecognizer(supported_language="it", supported_regions=("IT",)))
    return AnalyzerEngine(nlp_engine=nlp_engine, registry=registry, supported_languages=["it"])


def find(text: str, config: RunConfig) -> list[Span]:
    """Spans found by Presidio in `text`, possibly overlapping; `detect` merges them."""
    results = _analyzer().analyze(text=text, language="it", entities=list(LABEL_TO_TYPE))
    return [
        Span(
            r.start,
            r.end,
            text[r.start : r.end],
            LABEL_TO_TYPE[r.entity_type],
            min(1.0, max(0.0, float(r.score))),
            SOURCE,
        )
        for r in results
        if r.start < r.end
    ]
