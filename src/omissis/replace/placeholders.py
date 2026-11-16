"""R1: typed placeholders (task B1; grammar in docs/interfaces.md, section 2).

An entity gets `[TYPE_n]`, or `[PERSONA_n_M]` / `[PERSONA_n_F]` when its gender is
known. There is one counter per type per session: the session is the vault, so the
next number for a type is one more than the highest number of that type already in
the vault. A number whose placeholder already appears in the source text (in any
gender form) is skipped, so restoration can never confuse it with ours.

"The same entity" means the same entity object within one text and, across texts
sharing a vault, an entity of the same type whose canonical value is equal after
normalising case and whitespace.
"""

from __future__ import annotations

from collections.abc import Sequence

from omissis.contracts import Entity, Gender, SpanType, VaultEntry, make_placeholder
from omissis.contracts import parse_placeholder as _parse
from omissis.vault import Vault


def normalise(value: str) -> str:
    """Case- and whitespace-insensitive form used to recognise the same value."""
    return " ".join(value.split()).casefold()


def find_entry(vault: Vault, type: SpanType, original: str) -> VaultEntry | None:
    """The vault entry holding `original` with `type`, compared after `normalise`."""
    key = normalise(original)
    for entry in vault:
        if entry.type == type and normalise(entry.original) == key:
            return entry
    return None


def _next_number(vault: Vault, type: SpanType, text: str) -> int:
    used = [parsed[1] for e in vault if (parsed := _parse(e.surrogate)) and parsed[0] == type]
    n = max(used, default=0) + 1
    while any(make_placeholder(type, n, g) in text for g in _forms(type)):
        n += 1
    return n


def _forms(type: SpanType) -> tuple[Gender, ...]:
    return (Gender.UNKNOWN, Gender.M, Gender.F) if type is SpanType.PERSONA else (Gender.UNKNOWN,)


def replace_r1(text: str, entities: Sequence[Entity], vault: Vault) -> str:
    """Write a placeholder for every mention of `entities`, recording new entries in `vault`."""
    # Check the input before touching the vault, so an error leaves it unchanged.
    mentions = sorted((m.start, m.end) for e in entities for m in e.mentions)
    if any(not m.matches(text) for e in entities for m in e.mentions):
        raise ValueError("an entity mention does not match the text")
    if any(b[0] < a[1] for a, b in zip(mentions, mentions[1:], strict=False)):
        raise ValueError("entity mentions overlap; merge spans before replacing")

    edits: list[tuple[int, int, str]] = []
    for entity in sorted(entities, key=lambda e: min(m.start for m in e.mentions)):
        entry = find_entry(vault, entity.type, entity.canonical)
        if entry is None:
            n = _next_number(vault, entity.type, text)
            gender = entity.gender if entity.type is SpanType.PERSONA else Gender.UNKNOWN
            variants = tuple(
                dict.fromkeys(m.text for m in entity.mentions if m.text != entity.canonical)
            )
            entry = VaultEntry(
                surrogate=make_placeholder(entity.type, n, gender),
                original=entity.canonical,
                type=entity.type,
                entity_id=entity.entity_id,
                original_variants=variants,
            )
            vault.add(entry)
        edits.extend((m.start, m.end, entry.surrogate) for m in entity.mentions)

    for start, end, surrogate in sorted(edits, reverse=True):  # from the end to the start
        text = text[:start] + surrogate + text[end:]
    return text
