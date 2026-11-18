"""Pipeline: mask without LLM calls, or mask, send and restore."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Sequence

from omissis.backends import LLMRequest, complete
from omissis.config import GOLD_DETECTOR, NO_DETECTOR, RunConfig, run_id
from omissis.contracts import DisclosureItem, MaskResult, PipelineResult, Span, SpanClass
from omissis.detect import detect
from omissis.replace import replace
from omissis.replace.placeholders import find_entry
from omissis.resolve import resolve
from omissis.restore import restore
from omissis.vault import Vault

# The only place this instruction is defined. It is the system message of every cloud call.
KEEP_PLACEHOLDERS_INSTRUCTION = (
    "Il testo contiene segnaposto tra parentesi quadre, come [PERSONA_1_M] o "
    "[IBAN_1]. Copiali esattamente come sono, senza modificarli, tradurli o "
    "spiegarli."
)

# Upper limit of the cloud reply. It is part of the request, hence of the cache key.
MAX_TOKENS = 2048


def _spans(text: str, config: RunConfig, gold_spans: Sequence[Span] | None) -> list[Span]:
    """The spans to consider, from the detector or from the annotation."""
    if config.detector == GOLD_DETECTOR:
        if gold_spans is None:
            raise ValueError("detector GOLD requires gold_spans")
        if any(not span.matches(text) for span in gold_spans):
            raise ValueError("a gold span does not match the text")
        return sorted(gold_spans, key=lambda s: (s.start, s.end))
    if gold_spans is not None:
        raise ValueError(f"gold_spans are only allowed with detector GOLD, not {config.detector}")
    if config.detector == NO_DETECTOR:
        return []
    return detect(text, config.detector, config)


# What a reason must not repeat of a masked value: a word of three letters, two digits.
_PART = re.compile(r"[^\W\d_]{3,}|\d{2,}")


def _fold(value: str) -> str:
    """`value` without case and accents: "Niccolò" and "niccolo" are one."""
    plain = unicodedata.normalize("NFD", value.casefold())
    return "".join(ch for ch in plain if not unicodedata.combining(ch))


def _compact(value: str) -> str:
    """`value` without case, accents, spaces and punctuation: "IT89 Y000" is "IT89Y000"."""
    return re.sub(r"[\W_]+", "", _fold(value))


def _safe_reason(reason: str | None, vault: Vault) -> str | None:
    """`reason` with every masked value replaced by its surrogate.

    None when what is left still quotes a masked value: in another case, spacing or
    accent, or a part of it (a word, a run of digits, three digits in a row of a
    longer number). A reason is worth less than a leak.
    """
    if reason is None:
        return None
    values = [(v, e.surrogate) for e in vault for v in (e.original, *e.original_variants)]
    for value, surrogate in sorted(values, key=lambda pair: -len(pair[0])):
        reason = reason.replace(value, surrogate)
    left = reason
    for _, surrogate in values:
        left = left.replace(surrogate, " ")
    folded = _fold(left)
    if any(_fold(value) in folded for value, _ in values):
        return None
    parts = {_fold(part) for value, _ in values for part in _PART.findall(value)}
    if parts & {_fold(part) for part in _PART.findall(left)}:
        return None
    squeezed = _compact(left)
    if any(len(_compact(value)) >= 3 and _compact(value) in squeezed for value, _ in values):
        return None
    digits = [re.sub(r"\D", "", value) for value, _ in values]
    if any(run in number for run in re.findall(r"\d{3,}", left) for number in digits):
        return None
    return reason


def mask(
    text: str,
    config: RunConfig,
    gold_spans: Sequence[Span] | None = None,
    vault: Vault | None = None,
) -> tuple[MaskResult, Vault]:
    """Detect, resolve and replace, with no call to the role `cloud`.

    Where the spans come from depends on `config.detector`: a detector (`D0`-`D4`,
    `gold_spans` must be None), the annotation (`GOLD`, `gold_spans` required) or
    nothing (`NONE`: the text is returned unchanged). A wrong combination raises
    `ValueError`. Quasi-identifier spans are masked only when `config.mask_quasi` is
    true; direct and special-category spans always.
    """
    spans = _spans(text, config, gold_spans)
    vault = Vault() if vault is None else vault
    to_mask = [s for s in spans if config.mask_quasi or s.cls is not SpanClass.QUASI]
    entities = resolve(to_mask, text)
    masked_text, vault = replace(text, entities, config.strategy, config.seed, vault)
    disclosure = tuple(
        DisclosureItem(
            surrogate=find_entry(vault, e.type, e.canonical, e.gender).surrogate,
            type=e.type,
            source=e.mentions[0].source,
            reason=_safe_reason(e.mentions[0].reason, vault),
        )
        for e in entities
    )
    # `spans` holds every span found, masked or not; `entities` only the masked ones.
    return MaskResult(masked_text, tuple(spans), tuple(entities), disclosure), vault


def protect_send_restore(
    text: str,
    task: str,
    config: RunConfig,
    gold_spans: Sequence[Span] | None = None,
) -> PipelineResult:
    """Mask `text`, send `task` followed by the masked text to role `cloud`, restore the reply.

    Masking follows `mask`, with the same rules for `config.detector` and
    `gold_spans`. `KEEP_PLACEHOLDERS_INSTRUCTION` is the system message. `task` is
    the user's instruction in Italian. The vault is created for the call and erased
    before returning, also when the call fails.
    """
    vault = Vault()
    try:
        masked, vault = mask(text, config, gold_spans, vault)
        request = LLMRequest(
            role="cloud",
            prompt=f"{task}\n\n{masked.masked_text}",
            system=KEEP_PLACEHOLDERS_INSTRUCTION,
            params={"max_tokens": MAX_TOKENS},
        )
        response = complete(request, config)
        restored, events = restore(response.text, vault, config.fuzzy_threshold)
    finally:
        vault.clear()
    return PipelineResult(
        run_id=run_id(config),
        masked_text=masked.masked_text,
        raw_reply=response.text,
        restored_reply=restored,
        disclosure=masked.disclosure,
        restore_events=tuple(events),
    )
