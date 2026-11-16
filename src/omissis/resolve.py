"""Entity resolution: group span mentions into entities, rules only.

Interim version (task B4): one entity per distinct (type, span text), gender
UNKNOWN. Task B6 replaces it with the rules of the docstring below.
"""

from __future__ import annotations

from collections.abc import Sequence

from omissis.contracts import Entity, Span, SpanType


def resolve(spans: Sequence[Span], text: str) -> list[Entity]:
    """Group `spans` into entities.

    Every input span ends up in exactly one entity. Person mentions merge when one
    contains the other's surname; two people with one surname and different first
    names stay separate. Other types merge on normalised equality (case and
    whitespace). Gender from titles first (Sig./Sig.ra, Dott./Dott.ssa), then from
    a first-name list, otherwise UNKNOWN. Rules only; the same function serves
    every detector.
    """
    groups: dict[tuple[SpanType, str], list[Span]] = {}
    for span in sorted(spans, key=lambda s: (s.start, s.end)):
        groups.setdefault((span.type, span.text), []).append(span)

    counters: dict[SpanType, int] = {}
    entities = []
    for (type, value), mentions in groups.items():  # in order of first appearance
        counters[type] = counters.get(type, 0) + 1
        entities.append(Entity(f"{type.value}_{counters[type]}", type, value, tuple(mentions)))
    return entities
