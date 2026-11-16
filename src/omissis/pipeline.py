"""Pipeline: mask without LLM calls, or mask, send and restore."""

from __future__ import annotations

from collections.abc import Sequence

from omissis.backends import LLMRequest, complete
from omissis.config import RunConfig, run_id
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


def mask(
    text: str,
    config: RunConfig,
    gold_spans: Sequence[Span] | None = None,
    vault: Vault | None = None,
) -> tuple[MaskResult, Vault]:
    """Detect, resolve and replace, with no LLM call.

    With `gold_spans` the detector is skipped and those spans are masked
    (REF-oracle). Quasi-identifier spans are masked only when `config.mask_quasi`
    is true; direct and special-category spans always.
    """
    if gold_spans is not None:
        raise NotImplementedError("pipeline.mask with gold_spans is built by task B5")
    spans = detect(text, config.detector, config)
    to_mask = [s for s in spans if config.mask_quasi or s.cls is not SpanClass.QUASI]
    entities = resolve(to_mask, text)
    masked_text, vault = replace(text, entities, config.strategy, config.seed, vault)
    disclosure = tuple(
        DisclosureItem(
            surrogate=find_entry(vault, e.type, e.canonical).surrogate,
            type=e.type,
            source=e.mentions[0].source,
            reason=e.mentions[0].reason,
        )
        for e in entities
    )
    # `spans` holds every detected span, masked or not; `entities` only the masked ones.
    return MaskResult(masked_text, tuple(spans), tuple(entities), disclosure), vault


def protect_send_restore(text: str, task: str, config: RunConfig) -> PipelineResult:
    """Mask `text`, send `task` followed by the masked text to role `cloud`, restore the reply.

    `KEEP_PLACEHOLDERS_INSTRUCTION` is the system message. `task` is the user's
    instruction in Italian. The vault is created for the call and erased before
    returning.
    """
    vault = Vault()
    try:
        masked, vault = mask(text, config, vault=vault)
        request = LLMRequest(
            role="cloud",
            prompt=f"{task}\n\n{masked.masked_text}",
            system=KEEP_PLACEHOLDERS_INSTRUCTION,
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
