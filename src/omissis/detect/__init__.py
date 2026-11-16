"""Detection entry point. Owned by workstream A from the merge of task B0."""

from __future__ import annotations

import logging

from omissis.config import RunConfig
from omissis.contracts import DetectorId, Span
from omissis.detect import rules
from omissis.detect.merge import merge

logger = logging.getLogger(__name__)

# Task that builds each detector not available yet.
_NOT_BUILT = {
    DetectorId.D1: "A3 (Presidio)",
    DetectorId.D2: "A4 (ready-made classifier)",
    DetectorId.D3: "A6 (local LLM)",
    DetectorId.D4: "A7 (hybrid)",
}


def detect(text: str, detector: DetectorId, config: RunConfig) -> list[Span]:
    """Return the sensitive spans of `text` found by `detector`.

    Spans are sorted by `start` and non-overlapping. Overlaps are resolved inside:
    longer span wins, then higher confidence, then earlier position in
    `config.source_priority`. Every span satisfies `span.matches(text)`.
    Quasi-identifier spans are returned even when `config.mask_quasi` is false.
    Never raises on bad input or on a failing model: a failing detector logs and
    contributes no spans. A detector not built yet raises `NotImplementedError`.
    """
    detector = DetectorId(detector)
    if detector in _NOT_BUILT:
        raise NotImplementedError(
            f"detector {detector.value} is not built yet: task {_NOT_BUILT[detector]}"
        )
    if not isinstance(text, str):
        logger.warning("detect: expected str, got %s; returning no spans", type(text).__name__)
        return []
    try:
        found = rules.find_all(text)
    except Exception as exc:  # a failing detector contributes no spans
        # Log the error type only: the message could quote the text.
        logger.error("detector %s failed (%s); returning no spans", detector, type(exc).__name__)
        return []
    return merge(found, config.source_priority)
