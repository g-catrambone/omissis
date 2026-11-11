"""Detection entry point. Owned by workstream A from the merge of task B0."""

from __future__ import annotations

from omissis.config import RunConfig
from omissis.contracts import DetectorId, Span


def detect(text: str, detector: DetectorId, config: RunConfig) -> list[Span]:
    """Return the sensitive spans of `text` found by `detector`.

    Spans are sorted by `start` and non-overlapping. Overlaps are resolved inside:
    longer span wins, then higher confidence, then earlier position in
    `config.source_priority`. Every span satisfies `span.matches(text)`.
    Quasi-identifier spans are returned even when `config.mask_quasi` is false.
    Never raises on bad input or on a failing model: a failing detector logs and
    contributes no spans. A detector not built yet raises `NotImplementedError`.
    """
    raise NotImplementedError("detect is built by tasks A1 and A2 (workstream A)")
