"""Entity resolution: group span mentions into entities, rules only."""

from __future__ import annotations

from collections.abc import Sequence

from omissis.contracts import Entity, Span


def resolve(spans: Sequence[Span], text: str) -> list[Entity]:
    """Group `spans` into entities.

    Every input span ends up in exactly one entity. Person mentions merge when one
    contains the other's surname; two people with one surname and different first
    names stay separate. Other types merge on normalised equality (case and
    whitespace). Gender from titles first (Sig./Sig.ra, Dott./Dott.ssa), then from
    a first-name list, otherwise UNKNOWN. Rules only; the same function serves
    every detector.
    """
    raise NotImplementedError("resolve is built by task B6 (interim resolver in B4)")
