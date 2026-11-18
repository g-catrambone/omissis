"""Overlap resolution for detected spans (block 1).

Rule (docs/interfaces.md, `detect`): when two spans overlap, the longer span wins,
then the one with higher confidence, then the one whose source comes earlier in
`source_priority`. Sources not listed in `source_priority` (for example `GOLD`) rank
after every listed one. When all three criteria tie, the span that came first in the
input wins, so the result is deterministic for a given input order.

Spans are accepted greedily in that order of preference; a span that overlaps an
already accepted span is dropped whole, never cut. Adjacent spans (one ends where the
other starts) do not overlap and are both kept.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from omissis.contracts import DetectorId, Span


def merge(spans: Iterable[Span], source_priority: Sequence[DetectorId | str]) -> list[Span]:
    """Return non-overlapping spans sorted by `start`, resolving overlaps by the rule above."""
    rank = {str(source): i for i, source in enumerate(source_priority)}
    candidates = list(spans)
    order = sorted(
        range(len(candidates)),
        key=lambda i: (
            -(candidates[i].end - candidates[i].start),
            -candidates[i].confidence,
            rank.get(candidates[i].source, len(rank)),
            i,
        ),
    )
    accepted: list[Span] = []
    for i in order:
        span = candidates[i]
        if all(span.end <= other.start or other.end <= span.start for other in accepted):
            accepted.append(span)
    return sorted(accepted, key=lambda s: (s.start, s.end))
