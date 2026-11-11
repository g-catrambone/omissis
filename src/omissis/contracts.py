"""Data contracts shared by every workstream (docs/interfaces.md, sections 1 and 2).

Plain data and validation only. All dataclasses are frozen; all enums are StrEnum.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum


class SpanClass(StrEnum):
    DIRECT = "direct"
    QUASI = "quasi"
    SPECIAL = "special"


class SpanType(StrEnum):
    # direct identifiers
    PERSONA = "PERSONA"
    IBAN = "IBAN"
    CF = "CF"
    PIVA = "PIVA"
    TELEFONO = "TELEFONO"
    EMAIL = "EMAIL"
    INDIRIZZO = "INDIRIZZO"
    DOCUMENTO = "DOCUMENTO"
    CONTO = "CONTO"
    DATA_NASCITA = "DATA_NASCITA"
    UTENTE = "UTENTE"
    # quasi-identifiers
    AZIENDA = "AZIENDA"
    RUOLO = "RUOLO"
    CITTA = "CITTA"
    STRUTTURA = "STRUTTURA"
    IMPORTO = "IMPORTO"
    DATA = "DATA"
    ETA = "ETA"
    NAZIONALITA = "NAZIONALITA"
    # special categories
    SALUTE = "SALUTE"
    RELIGIONE = "RELIGIONE"
    POLITICA = "POLITICA"
    SINDACATO = "SINDACATO"
    ORIENTAMENTO = "ORIENTAMENTO"
    ETNIA = "ETNIA"
    BIOMETRICO = "BIOMETRICO"
    GIUDIZIARIO = "GIUDIZIARIO"


class Gender(StrEnum):
    M = "M"
    F = "F"
    UNKNOWN = "UNKNOWN"


class DetectorId(StrEnum):
    D0 = "D0"
    D1 = "D1"
    D2 = "D2"
    D3 = "D3"
    D4 = "D4"


class Strategy(StrEnum):
    R1 = "R1"
    R2 = "R2"


class RestoreOutcome(StrEnum):
    RESTORED = "restored"
    RESTORED_FUZZY = "restored_fuzzy"
    DROPPED = "dropped"
    ALTERED_UNRESOLVED = "altered_unresolved"
    HALLUCINATED_TOKEN = "hallucinated_token"
    WRONG_MAPPING = "wrong_mapping"  # assigned by evaluation only, never by restore


_DIRECT = "PERSONA IBAN CF PIVA TELEFONO EMAIL INDIRIZZO DOCUMENTO CONTO DATA_NASCITA UTENTE"
_QUASI = "AZIENDA RUOLO CITTA STRUTTURA IMPORTO DATA ETA NAZIONALITA"
_SPECIAL = "SALUTE RELIGIONE POLITICA SINDACATO ORIENTAMENTO ETNIA BIOMETRICO GIUDIZIARIO"

TYPE_CLASS: dict[SpanType, SpanClass] = {
    **{SpanType(t): SpanClass.DIRECT for t in _DIRECT.split()},
    **{SpanType(t): SpanClass.QUASI for t in _QUASI.split()},
    **{SpanType(t): SpanClass.SPECIAL for t in _SPECIAL.split()},
}

GOLD_SOURCE = "GOLD"
_VALID_SOURCES = frozenset({*(d.value for d in DetectorId), GOLD_SOURCE})


@dataclass(frozen=True)
class Span:
    start: int
    end: int
    text: str
    type: SpanType
    confidence: float
    source: str
    reason: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "type", SpanType(self.type))
        if not 0 <= self.start < self.end:
            raise ValueError(
                f"span offsets must satisfy 0 <= start < end, got {self.start}, {self.end}"
            )
        if len(self.text) != self.end - self.start:
            raise ValueError("span text length must equal end - start")
        if not 0 <= self.confidence <= 1:
            raise ValueError(f"confidence must be in [0, 1], got {self.confidence}")
        if self.source not in _VALID_SOURCES:
            raise ValueError(
                f"span source must be a DetectorId or {GOLD_SOURCE!r}, got {self.source!r}"
            )
        if self.source == DetectorId.D3 and not (self.reason and self.reason.strip()):
            raise ValueError("spans from D3 require a non-empty reason")

    @property
    def cls(self) -> SpanClass:
        return TYPE_CLASS[self.type]

    def matches(self, source_text: str) -> bool:
        return source_text[self.start : self.end] == self.text


@dataclass(frozen=True)
class Entity:
    entity_id: str
    type: SpanType
    canonical: str
    mentions: tuple[Span, ...]
    gender: Gender = Gender.UNKNOWN

    def __post_init__(self) -> None:
        object.__setattr__(self, "type", SpanType(self.type))
        object.__setattr__(self, "gender", Gender(self.gender))
        object.__setattr__(self, "mentions", tuple(self.mentions))
        if not self.mentions:
            raise ValueError("an entity needs at least one mention")
        if any(m.type != self.type for m in self.mentions):
            raise ValueError("all mentions must have the entity's type")
        if not re.fullmatch(rf"{self.type.value}_[1-9]\d*", self.entity_id):
            raise ValueError(f"entity_id must be <TYPE>_<n>, got {self.entity_id!r}")

    @property
    def cls(self) -> SpanClass:
        return TYPE_CLASS[self.type]


@dataclass(frozen=True, repr=False)
class VaultEntry:
    surrogate: str
    original: str
    type: SpanType
    entity_id: str
    original_variants: tuple[str, ...] = ()
    surrogate_variants: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "type", SpanType(self.type))
        object.__setattr__(self, "original_variants", tuple(self.original_variants))
        object.__setattr__(self, "surrogate_variants", tuple(self.surrogate_variants))

    def __repr__(self) -> str:
        # Never show the original value or its variants.
        return (
            f"VaultEntry(surrogate={self.surrogate!r}, type={self.type.value}, "
            f"entity_id={self.entity_id!r})"
        )


@dataclass(frozen=True)
class RestoreEvent:
    surrogate: str
    outcome: RestoreOutcome
    found_as: str | None = None


@dataclass(frozen=True)
class DisclosureItem:
    surrogate: str
    type: SpanType
    source: str
    reason: str | None = None

    @property
    def cls(self) -> SpanClass:
        return TYPE_CLASS[self.type]


@dataclass(frozen=True)
class MaskResult:
    masked_text: str
    spans: tuple[Span, ...]
    entities: tuple[Entity, ...]
    disclosure: tuple[DisclosureItem, ...]


@dataclass(frozen=True)
class PipelineResult:
    run_id: str
    masked_text: str
    raw_reply: str
    restored_reply: str
    disclosure: tuple[DisclosureItem, ...]
    restore_events: tuple[RestoreEvent, ...]

    @property
    def fully_restored(self) -> bool:
        unresolved = {RestoreOutcome.ALTERED_UNRESOLVED, RestoreOutcome.HALLUCINATED_TOKEN}
        return not any(e.outcome in unresolved for e in self.restore_events)


# --- Placeholder grammar (R1), docs/interfaces.md section 2 ---

PLACEHOLDER_RE = re.compile(r"\[([A-Z]+(?:_[A-Z]+)*)_(\d+)(?:_([MF]))?\]")


def make_placeholder(type: SpanType, n: int, gender: Gender = Gender.UNKNOWN) -> str:
    """Return `[TYPE_n]`, or `[PERSONA_n_M]` / `[PERSONA_n_F]` when gender is known."""
    type, gender = SpanType(type), Gender(gender)
    if n < 1:
        raise ValueError(f"placeholder number must be >= 1, got {n}")
    if gender is Gender.UNKNOWN:
        return f"[{type.value}_{n}]"
    if type is not SpanType.PERSONA:
        raise ValueError("a gender suffix is only allowed on PERSONA placeholders")
    return f"[{type.value}_{n}_{gender.value}]"


def parse_placeholder(token: str) -> tuple[SpanType, int, Gender] | None:
    """Parse a whole placeholder token; None if unknown type, malformed or invalid suffix."""
    match = PLACEHOLDER_RE.fullmatch(token)
    if match is None:
        return None
    label, number, suffix = match.groups()
    if label not in SpanType.__members__ or number.startswith("0"):
        return None
    type = SpanType(label)
    if suffix is not None and type is not SpanType.PERSONA:
        return None
    return type, int(number), Gender(suffix) if suffix else Gender.UNKNOWN
