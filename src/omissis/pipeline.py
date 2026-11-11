"""Pipeline: mask without LLM calls, or mask, send and restore."""

from __future__ import annotations

from collections.abc import Sequence

from omissis.config import RunConfig
from omissis.contracts import MaskResult, PipelineResult, Span
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
    raise NotImplementedError("pipeline.mask is built by task B4 (gold spans in B5)")


def protect_send_restore(text: str, task: str, config: RunConfig) -> PipelineResult:
    """Mask `text`, send `task` followed by the masked text to role `cloud`, restore the reply.

    `KEEP_PLACEHOLDERS_INSTRUCTION` is the system message. `task` is the user's
    instruction in Italian. The vault is created for the call and erased before
    returning.
    """
    raise NotImplementedError("pipeline.protect_send_restore is built by task B4")
