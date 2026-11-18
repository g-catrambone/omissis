"""Overlap resolution for detected spans (block 1).

Rule (docs/interfaces.md, `detect`): when two spans overlap, the longer span wins,
then the one with higher confidence, then the one whose source comes earlier in
`source_priority`. Sources not listed in `source_priority` (for example `GOLD`) rank
after every listed one. When all three criteria tie, the span that came first in the
input wins, so the result is deterministic for a given input order.

Spans are accepted greedily in that order of preference. The winner is never cut. Of
a span that overlaps an accepted one, the stretch outside it is kept as a shorter
span of the same type and source, so that nothing a detector found goes back to
clear text: of a phone number whose last digit is also the first of a longer amount,
the digits before the amount stay masked. A span inside an accepted one leaves
nothing, and so does a stretch with no letter and no digit. Adjacent spans (one ends
where the other starts) do not overlap and are both kept.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from omissis.contracts import DetectorId, Span


def _outside(span: Span, accepted: Sequence[Span]) -> list[Span]:
    """The stretches of `span` that no accepted span covers, without the spaces around them."""
    pieces = [(span.start, span.end)]
    for other in accepted:
        pieces = [
            (start, end)
            for a, b in pieces
            for start, end in ((a, min(b, other.start)), (max(a, other.end), b))
            if start < end
        ]
    if pieces == [(span.start, span.end)]:
        return [span]
    kept = []
    for start, end in pieces:
        text = span.text[start - span.start : end - span.start]
        start += len(text) - len(text.lstrip())
        text = text.strip()
        if any(c.isalnum() for c in text):
            kept.append(
                Span(
                    start,
                    start + len(text),
                    text,
                    span.type,
                    span.confidence,
                    span.source,
                    span.reason,
                )
            )
    return kept


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
        accepted.extend(_outside(candidates[i], accepted))
    return sorted(accepted, key=lambda s: (s.start, s.end))
