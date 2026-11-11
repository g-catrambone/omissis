"""Replacement of entities with surrogates: R1 placeholders, R2 realistic fakes."""

from __future__ import annotations

from collections.abc import Sequence

from omissis.contracts import Entity, Strategy
from omissis.vault import Vault


def replace(
    text: str,
    entities: Sequence[Entity],
    strategy: Strategy,
    seed: int,
    vault: Vault | None = None,
) -> tuple[str, Vault]:
    """Replace every mention of `entities` in `text` and record the mapping in a vault.

    R1 writes `make_placeholder` tokens. R2 writes realistic fake values,
    deterministic for `seed`, from lists disjoint from the profile pool and never
    already present in `text`. The same entity always gets the same surrogate; a
    passed-in vault is reused so surrogates stay consistent across texts of one
    session. Substitution runs from the end of the text to the start.
    """
    raise NotImplementedError("replace is built by tasks B1 (R1) and B7 (R2)")
