"""D2: a ready-made token classifier for personal data.

The model is the one pinned under role `d2` in the models file (id and revision on
the Hugging Face hub). It is used as it is: no fine-tuning, and the weights are
read from the local Hugging Face cache, never downloaded here and never stored in
the repository. D2 is not an LLM call, so it does not go through
`backends.complete`.

A text longer than one window is read in overlapping windows of `WINDOW` tokens
that share `STRIDE` tokens. A token seen in two windows keeps the prediction of
the window where it is farther from the edge. Neighbouring tokens of the same type,
separated by white space at most, become one span; its confidence is the mean of
the token probabilities.

Labels of `iiiorg/piiranha-v1-detect-personal-information` -> our type:

| Label | Type |
|---|---|
| `GIVENNAME`, `SURNAME` | PERSONA |
| `EMAIL` | EMAIL |
| `TELEPHONENUM` | TELEFONO |
| `TAXNUM`, `SOCIALNUM` | CF |
| `ACCOUNTNUM`, `CREDITCARDNUMBER` | CONTO |
| `IDCARDNUM`, `DRIVERLICENSENUM` | DOCUMENTO |
| `DATEOFBIRTH` | DATA_NASCITA |
| `USERNAME` | UTENTE |
| `STREET`, `BUILDINGNUM`, `ZIPCODE` | INDIRIZZO |
| `CITY` | CITTA |

Label with no counterpart, ignored: `PASSWORD`.

Our types with no label, never found by D2: IBAN and PIVA as such (an IBAN may
come out as CONTO, a partita IVA as CF), AZIENDA, RUOLO, STRUTTURA, IMPORTO, DATA,
ETA, NAZIONALITA and every special category.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from omissis.config import ConfigError, RunConfig, load_models, require_pinned
from omissis.contracts import DetectorId, Span, SpanType

SOURCE = DetectorId.D2.value
# Modules D2 imports; `detect` reports a missing one as a `ConfigError`.
NEEDS = ("transformers", "torch")
WINDOW = 256  # tokens, the context length the model was trained with
STRIDE = 64  # tokens shared by two neighbouring windows

LABEL_TO_TYPE: dict[str, SpanType] = {
    "GIVENNAME": SpanType.PERSONA,
    "SURNAME": SpanType.PERSONA,
    "EMAIL": SpanType.EMAIL,
    "TELEPHONENUM": SpanType.TELEFONO,
    "TAXNUM": SpanType.CF,
    "SOCIALNUM": SpanType.CF,
    "ACCOUNTNUM": SpanType.CONTO,
    "CREDITCARDNUMBER": SpanType.CONTO,
    "IDCARDNUM": SpanType.DOCUMENTO,
    "DRIVERLICENSENUM": SpanType.DOCUMENTO,
    "DATEOFBIRTH": SpanType.DATA_NASCITA,
    "USERNAME": SpanType.UTENTE,
    "STREET": SpanType.INDIRIZZO,
    "BUILDINGNUM": SpanType.INDIRIZZO,
    "ZIPCODE": SpanType.INDIRIZZO,
    "CITY": SpanType.CITTA,
}

# One token of the text: start, end (character offsets), label, probability.
Token = tuple[int, int, str, float]


@lru_cache(maxsize=1)
def _load(model_id: str, revision: str) -> tuple[Any, Any]:
    """Tokenizer and model from the local cache, loaded once per process."""
    from transformers import AutoModelForTokenClassification, AutoTokenizer

    try:
        tokenizer = AutoTokenizer.from_pretrained(
            model_id, revision=revision, local_files_only=True
        )
        model = AutoModelForTokenClassification.from_pretrained(
            model_id, revision=revision, local_files_only=True
        )
    except (OSError, ValueError) as exc:
        raise ConfigError(
            f"weights of {model_id} at revision {revision} are not on this machine: "
            f"run `uv run hf download {model_id} --revision {revision}`"
        ) from exc
    model.eval()
    return tokenizer, model


def _windows(text: str, model_id: str, revision: str) -> list[list[Token]]:
    """The model's prediction for every token of every window of `text`."""
    import torch

    tokenizer, model = _load(model_id, revision)
    encoded = tokenizer(
        text,
        max_length=WINDOW,
        stride=STRIDE,
        truncation=True,
        padding=True,
        return_overflowing_tokens=True,
        return_offsets_mapping=True,
        return_tensors="pt",
    )
    offsets = encoded.pop("offset_mapping").tolist()
    encoded.pop("overflow_to_sample_mapping")
    with torch.no_grad():
        scores, labels = model(**encoded).logits.softmax(dim=-1).max(dim=-1)
    id2label = model.config.id2label
    return [
        [
            (start, end, id2label[label], score)
            for (start, end), label, score in zip(window, row_labels, row_scores, strict=True)
            if start < end  # special and padding tokens have an empty range
        ]
        for window, row_labels, row_scores in zip(
            offsets, labels.tolist(), scores.tolist(), strict=True
        )
    ]


def _stitch(windows: list[list[Token]]) -> list[Token]:
    """One prediction per token: where windows overlap, the one farther from an edge."""
    best: dict[tuple[int, int], tuple[int, Token]] = {}
    for window in windows:
        for i, token in enumerate(window):
            margin = min(i, len(window) - 1 - i)
            key = token[:2]
            if key not in best or margin > best[key][0]:
                best[key] = (margin, token)
    return [token for _, token in sorted(best.values(), key=lambda item: item[1][:2])]


def _group(text: str, tokens: list[Token]) -> list[Span]:
    """Join neighbouring tokens of one type into spans; unmapped labels end a span."""
    groups: list[tuple[SpanType, int, int, list[float]]] = []
    for start, end, label, score in tokens:
        type = LABEL_TO_TYPE.get(label.split("-", 1)[-1])
        if type is None:
            continue
        if groups and groups[-1][0] is type and not text[groups[-1][2] : start].strip():
            _, first, _, scores = groups[-1]
            groups[-1] = (type, first, end, [*scores, score])
        else:
            groups.append((type, start, end, [score]))

    spans = []
    for type, start, end, scores in groups:
        value = text[start:end]
        start += len(value) - len(value.lstrip())
        end -= len(value) - len(value.rstrip())
        if start < end:
            confidence = min(1.0, sum(scores) / len(scores))
            spans.append(Span(start, end, text[start:end], type, confidence, SOURCE))
    return spans


def find(text: str, config: RunConfig) -> list[Span]:
    """Spans found by the classifier in `text`; `detect` merges them."""
    model = require_pinned(load_models(config.models_file), "d2")
    return _group(text, _stitch(_windows(text, model.id, model.revision)))
