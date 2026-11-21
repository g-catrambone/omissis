"""Feasibility check before sending (step B5; docs/decisions.md, 21 Nov 2026).

A calculation on a masked value cannot come back right. With R1 the cloud model has no
number; with R2 it computes on the fake, and restoration cannot undo the result
(docs/evaluation_protocol.md, section 10). The app and `omissis run` ask `check_text`
before they send: a request that asks for a calculation, on a text where an amount, a
date or an age is masked, is not sent.

It is a heuristic and it is not evaluated. It reads the request alone, by a fixed list
of Italian cues. It does not see a calculation asked inside the text or worded outside
the list ("il 10% della rata"). It also stops requests that compute nothing: one that
only asks to copy a total, or "Dividi la risposta in due paragrafi". `batch`, `mask`
and the evaluation never call it.
"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter
from collections.abc import Sequence

from omissis.config import RunConfig
from omissis.contracts import Entity, Span, SpanType
from omissis.pipeline import mask
from omissis.vault import Vault

# The masked types a calculation needs, in the order they are reported.
COMPUTABLE = (SpanType.IMPORTO, SpanType.DATA, SpanType.ETA, SpanType.DATA_NASCITA)

# Calculation cues, read at the start of a word of the request, without case and accents.
_CUES = re.compile(
    r"\b(?:"
    r"(?:ri)?calcol\w*|somm(?:a|e|i|o|are|ate|ando|iamo)(?:l[aeio]|ne)?\b|"
    r"sommarl[aeio]\b|addizion\w*|sottra\w*|"
    r"moltiplic\w*|divid\w*|division\w*|differenz[ae]\b|percentual\w*|total[ei]\b|"
    r"complessiv\w*|medi[ae]\b|in\s+tutto\b|"
    r"quant[oaie]\s+(?:fa|fanno|resta|restano|rimane|rimangono|manca|mancano)\b|"
    r"quant[ie]\s+(?:giorni|settimane|mesi|anni)\b"
    r")"
)


def _fold(value: str) -> str:
    """`value` without case and accents: "Qual È" and "qual e" are one."""
    plain = unicodedata.normalize("NFD", value.casefold())
    return "".join(ch for ch in plain if not unicodedata.combining(ch))


def asks_calculation(task: str) -> bool:
    """True when the request `task` holds a calculation cue."""
    return bool(_CUES.search(_fold(task)))


def check(task: str, entities: Sequence[Entity]) -> dict[SpanType, int]:
    """The masked types that block `task`, each with its number of entities.

    `entities` are the masked entities of the text (`MaskResult.entities`). The result
    is empty when the request can be sent: it holds no calculation cue, or no amount,
    date, age or date of birth is masked. It never holds a value of the text.
    """
    if not asks_calculation(task):
        return {}
    counts = Counter(entity.type for entity in entities)
    return {kind: counts[kind] for kind in COMPUTABLE if counts[kind]}


def check_text(
    text: str,
    task: str,
    config: RunConfig,
    gold_spans: Sequence[Span] | None = None,
) -> dict[SpanType, int]:
    """`check` on what `pipeline.mask` masks in `text`, with no call to the role `cloud`.

    `config` and `gold_spans` are the ones the run would use, so the check sees the
    entities the run would mask. A request without a cue is answered without masking:
    an ordinary request costs nothing. The vault of the masking is erased before
    returning, also when masking fails.
    """
    if not asks_calculation(task):
        return {}
    vault = Vault()
    try:
        result, _ = mask(text, config, gold_spans, vault)
    finally:
        vault.clear()
    return check(task, result.entities)
