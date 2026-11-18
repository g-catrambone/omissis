"""R1: typed placeholders (block 1; grammar in docs/interfaces.md, section 2).

An entity gets `[TYPE_n]`, or `[PERSONA_n_M]` / `[PERSONA_n_F]` when its gender is
known. There is one counter per type per session: the session is the vault, so the
next number for a type is one more than the highest number of that type already in
the vault. A number that the source text already writes with the label, in any form
that restoration reads as a placeholder (`[IBAN_1]`, `IBAN_1`, `[iban 1]`), is
skipped, so restoration can never confuse it with ours.

"The same entity" means the same entity object within one text and, across texts
sharing a vault, an entity of the same type whose canonical value is equal after
normalising case and whitespace. Two people that the resolver keeps apart by gender
("Sig. Ferri", "Sig.ra Ferri") have the same canonical value and still get two
placeholders: a person matches an entry only when the gender is the same.
"""

from __future__ import annotations

from collections.abc import Sequence

from omissis.contracts import Entity, Gender, SpanType, VaultEntry, make_placeholder
from omissis.contracts import parse_placeholder as _parse
from omissis.restore import placeholder_numbers
from omissis.vault import Vault


def normalise(value: str) -> str:
    """Case- and whitespace-insensitive form used to recognise the same value."""
    return " ".join(value.split()).casefold()


def find_entry(
    vault: Vault, type: SpanType, original: str, gender: Gender = Gender.UNKNOWN
) -> VaultEntry | None:
    """The vault entry holding `original` with `type`, compared after `normalise`.

    A placeholder of a person must also carry `gender`.
    """
    key = normalise(original)
    for entry in vault:
        if entry.type != type or normalise(entry.original) != key:
            continue
        parsed = _parse(entry.surrogate)
        if type is SpanType.PERSONA and parsed and parsed[2] is not gender:
            continue
        return entry
    return None


def next_number(vault: Vault, type: SpanType, text: str) -> int:
    """The next free placeholder number of `type` in this session."""
    used = [parsed[1] for e in vault if (parsed := _parse(e.surrogate)) and parsed[0] == type]
    written = {number for label, number in placeholder_numbers(text) if label is type}
    n = max(used, default=0) + 1
    while n in written:
        n += 1
    return n


def check_mentions(text: str, entities: Sequence[Entity]) -> None:
    """Refuse mentions that do not match the text or that overlap.

    Called before the vault is touched, so an error leaves it unchanged.
    """
    mentions = sorted((m.start, m.end) for e in entities for m in e.mentions)
    if any(not m.matches(text) for e in entities for m in e.mentions):
        raise ValueError("an entity mention does not match the text")
    if any(b[0] < a[1] for a, b in zip(mentions, mentions[1:], strict=False)):
        raise ValueError("entity mentions overlap; merge spans before replacing")


def replace_r1(text: str, entities: Sequence[Entity], vault: Vault) -> str:
    """Write a placeholder for every mention of `entities`, recording new entries in `vault`."""
    check_mentions(text, entities)

    edits: list[tuple[int, int, str]] = []
    for entity in sorted(entities, key=lambda e: min(m.start for m in e.mentions)):
        gender = entity.gender if entity.type is SpanType.PERSONA else Gender.UNKNOWN
        entry = find_entry(vault, entity.type, entity.canonical, gender)
        if entry is None:
            n = next_number(vault, entity.type, text)
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
