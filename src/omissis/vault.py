"""In-memory session vault mapping surrogates to original values (docs/interfaces.md, section 1).

No persistence, no encryption. `repr` and `str` show the number of entries only, so a
vault can never leak original values into logs.
"""

from __future__ import annotations

from collections.abc import Iterator

from omissis.contracts import VaultEntry


class Vault:
    def __init__(self) -> None:
        self._entries: dict[str, VaultEntry] = {}

    def add(self, entry: VaultEntry) -> None:
        if entry.surrogate in self._entries:
            raise ValueError(f"surrogate already in vault: {entry.surrogate!r}")
        self._entries[entry.surrogate] = entry

    def get(self, surrogate: str) -> VaultEntry | None:
        return self._entries.get(surrogate)

    def surrogate_for(self, entity_id: str) -> str | None:
        for entry in self._entries.values():
            if entry.entity_id == entity_id:
                return entry.surrogate
        return None

    def clear(self) -> None:
        self._entries.clear()

    def __iter__(self) -> Iterator[VaultEntry]:
        return iter(list(self._entries.values()))

    def __len__(self) -> int:
        return len(self._entries)

    def __contains__(self, surrogate: object) -> bool:
        return surrogate in self._entries

    def __repr__(self) -> str:
        return f"Vault({len(self)} entries)"

    __str__ = __repr__
