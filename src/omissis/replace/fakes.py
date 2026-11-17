"""R2: realistic fake values (task 2.5).

Every entity gets a fake value of its own type, drawn with a generator seeded by the
run seed, the type and the value: the same value gets the same fake in every text
and on every machine. A fake is drawn again when it, or a part of it, already occurs
in the text or in the vault, so restoration can never mistake a real value for a fake.

- PERSONA: a first name of the same gender and a surname, from `data/`; a name of
  one word gets a surname.
- AZIENDA: from `data/aziende.txt`, or `data/banche.txt` for a bank.
- CITTA: from `data/citta.txt`. There is no matching by size: the profile pool is
  disjoint from the lists, so the size of the original is not known.
- INDIRIZZO: a street of `data/vie.txt` and a number.
- EMAIL: `nome.cognome@example.com`, a domain reserved for examples.
- IBAN: Italian, valid CIN and check digits, on bank code `00000`, which no bank has.
- CF: valid check character, place code starting with X, which no municipality has.
- PIVA: valid check digit, office code `000`, which is never issued.
- TELEFONO, DOCUMENTO, CONTO, UTENTE: the same shape with other digits and letters;
  a phone keeps its prefix.
- IMPORTO: the same number of digits and the same decimals, so the same order of
  magnitude.
- DATA, DATA_NASCITA: another day of the same month.
- ETA: the age moved by one to five years.
- RUOLO, STRUTTURA, NAZIONALITA and every special category: no fake, the R1
  placeholder.

The last line is a choice: a fake job, clinic or diagnosis would change the meaning
of the text and read as true. A person of two or more words also records the fake
surname and the fake first name as `surrogate_variants`, aligned with the original
surname and first name in `original_variants`: a mention of the surname alone is
written, and restored, as the surname alone.

The lists in `data/` were written for this project. The profile pool of the
evaluation is built to be disjoint from them: do not change them after gate G2.
"""

from __future__ import annotations

import random
import re
import string
from collections.abc import Callable, Sequence
from functools import cache
from pathlib import Path

from omissis.contracts import (
    TYPE_CLASS,
    Entity,
    Gender,
    Span,
    SpanClass,
    SpanType,
    VaultEntry,
    make_placeholder,
)
from omissis.detect.rules import cf_check_character
from omissis.replace.placeholders import check_mentions, find_entry, next_number, normalise
from omissis.vault import Vault

DATA = Path(__file__).parent / "data"
MAX_DRAWS = 200
# Types that keep the R1 placeholder under R2.
NO_FAKE = frozenset(
    {SpanType.RUOLO, SpanType.STRUTTURA, SpanType.NAZIONALITA}
    | {t for t, cls in TYPE_CLASS.items() if cls is SpanClass.SPECIAL}
)


@cache
def load_list(name: str) -> tuple[str, ...]:
    """The values of `data/<name>.txt`, one per line."""
    lines = (DATA / f"{name}.txt").read_text(encoding="utf-8").splitlines()
    return tuple(line.strip() for line in lines if line.strip())


def _first_name(rng: random.Random, gender: Gender) -> str:
    lists = {Gender.F: ("nomi_f",), Gender.M: ("nomi_m",)}.get(gender, ("nomi_f", "nomi_m"))
    return rng.choice([name for source in lists for name in load_list(source)])


def _shape(rng: random.Random, value: str, keep: int = 0) -> str:
    """`value` with every digit and letter after the first `keep` characters drawn again."""
    out = []
    for i, ch in enumerate(value):
        if i < keep:
            out.append(ch)
        elif ch.isdigit():
            out.append(rng.choice(string.digits))
        elif ch.isalpha():
            letters = string.ascii_uppercase if ch.isupper() else string.ascii_lowercase
            out.append(rng.choice(letters))
        else:
            out.append(ch)
    return "".join(out)


def _iban(rng: random.Random) -> str:
    rest = f"00000{rng.randrange(10**5):05d}{rng.randrange(10**12):012d}"  # ABI, CAB, account
    bban = cf_check_character(rest) + rest  # the CIN uses the table of the codice fiscale
    digits = "".join(str(int(ch, 36)) for ch in bban + "IT00")
    return f"IT{98 - int(digits) % 97:02d}{bban}"


def _cf(rng: random.Random) -> str:
    letters = "".join(rng.choice("BCDFGLMNPRSTVZ") for _ in range(6))
    day = rng.randint(1, 28) + rng.choice((0, 40))
    first15 = f"{letters}{rng.randrange(100):02d}{rng.choice('ABCDEHLMPRST')}{day:02d}"
    first15 += f"X{rng.randrange(1000):03d}"
    return first15 + cf_check_character(first15)


def _piva(rng: random.Random) -> str:
    first10 = f"{rng.randrange(1, 10**7):07d}000"
    total = 0
    for i, ch in enumerate(first10):
        digit = int(ch) * (2 if i % 2 else 1)
        total += digit - 9 if digit > 9 else digit
    return first10 + str((10 - total % 10) % 10)


def _phone(rng: random.Random, value: str) -> str:
    prefix = re.match(r"(?:(?:\+|00)39[ .-]?|\(\+39\) ?)?\d", value)
    return _shape(rng, value, keep=prefix.end() if prefix else 0)


def _amount(rng: random.Random, value: str) -> str:
    number = re.search(r"\d[\d.]*", value)  # the whole part, with the dots of the thousands
    if number is None:
        return _shape(rng, value)
    digits = [rng.choice("123456789")] + [rng.choice(string.digits) for _ in number.group()[1:]]
    whole = "".join(d if ch.isdigit() else ch for d, ch in zip(digits, number.group(), strict=True))
    return value[: number.start()] + whole + value[number.end() :]


def _date(rng: random.Random, value: str) -> str:
    groups = [m for m in re.finditer(r"\d+", value) if len(m.group()) <= 2]
    if not groups:
        return _shape(rng, value) if re.search(r"\d", value) else "1 gennaio"
    day = groups[-1] if re.match(r"\d{4}", value) else groups[0]  # 2026-12-01 or 1 dicembre
    new = rng.choice([d for d in range(1, 29) if d != int(day.group())])
    width = 2 if day.group().startswith("0") or re.search(r"\d[/.-]\d", value) else 1
    return value[: day.start()] + f"{new:0{width}d}" + value[day.end() :]


def _age(rng: random.Random, value: str) -> str:
    number = re.search(r"\d+", value)
    if number is None:
        return _shape(rng, value)
    new = max(18, int(number.group()) + rng.choice((-5, -4, -3, -2, -1, 1, 2, 3, 4, 5)))
    if new == int(number.group()):
        new += 1
    return value[: number.start()] + str(new) + value[number.end() :]


def _email(rng: random.Random) -> str:
    name, surname = _first_name(rng, Gender.UNKNOWN), rng.choice(load_list("cognomi"))
    return f"{name}.{surname}@example.com".lower()


_BANK = re.compile(r"\b(banc[ao]|cassa|credito)\b", re.IGNORECASE)

_GENERATORS: dict[SpanType, Callable[[random.Random, str], str]] = {
    SpanType.AZIENDA: lambda rng, value: rng.choice(
        load_list("banche" if _BANK.search(value) else "aziende")
    ),
    SpanType.CITTA: lambda rng, value: rng.choice(load_list("citta")),
    SpanType.INDIRIZZO: lambda rng, value: f"{rng.choice(load_list('vie'))} {rng.randint(1, 120)}",
    SpanType.EMAIL: lambda rng, value: _email(rng),
    SpanType.IBAN: lambda rng, value: _iban(rng),
    SpanType.CF: lambda rng, value: _cf(rng),
    SpanType.PIVA: lambda rng, value: _piva(rng),
    SpanType.TELEFONO: _phone,
    SpanType.DOCUMENTO: _shape,
    SpanType.CONTO: _shape,
    SpanType.UTENTE: _shape,
    SpanType.IMPORTO: _amount,
    SpanType.DATA: _date,
    SpanType.DATA_NASCITA: _date,
    SpanType.ETA: _age,
}


def _draw(rng: random.Random, entity: Entity) -> tuple[str, tuple[str, ...], tuple[str, ...]]:
    """One candidate: the fake, the original variants and the fake variants, aligned."""
    if entity.type is not SpanType.PERSONA:
        return _GENERATORS[entity.type](rng, entity.canonical), (), ()
    words = entity.canonical.split()
    surname = rng.choice(load_list("cognomi"))
    if len(words) < 2:
        return surname, (), ()
    first = _first_name(rng, entity.gender)
    return f"{first} {surname}", (words[-1], words[0]), (surname, first)


def _new_entry(text: str, entity: Entity, seed: int, vault: Vault) -> VaultEntry:
    if entity.type in NO_FAKE:
        placeholder = make_placeholder(entity.type, next_number(vault, entity.type, text))
        variants = tuple(
            dict.fromkeys(m.text for m in entity.mentions if m.text != entity.canonical)
        )
        return VaultEntry(placeholder, entity.canonical, entity.type, entity.entity_id, variants)

    rng = random.Random(f"{seed}|{entity.type.value}|{normalise(entity.canonical)}")
    folded = text.casefold()
    taken = {normalise(v) for e in vault for v in (e.surrogate, e.original, *e.surrogate_variants)}
    for _ in range(MAX_DRAWS):
        fake, originals, fakes = _draw(rng, entity)
        parts = (fake, *fakes)
        if all(p.casefold() not in folded and normalise(p) not in taken for p in parts):
            return VaultEntry(
                fake, entity.canonical, entity.type, entity.entity_id, originals, fakes
            )
    raise RuntimeError(f"no free fake value for an entity of type {entity.type.value}")


def _written(entry: VaultEntry, mention: Span) -> str:
    """What replaces `mention`: the fake, or its variant for a surname or first name alone."""
    pairs = dict(
        zip(map(normalise, entry.original_variants), entry.surrogate_variants, strict=False)
    )
    if normalise(mention.text) != normalise(entry.original):
        return pairs.get(normalise(mention.text), entry.surrogate)
    return entry.surrogate


def replace_r2(text: str, entities: Sequence[Entity], seed: int, vault: Vault) -> str:
    """Write a fake value for every mention of `entities`, recording new entries in `vault`."""
    check_mentions(text, entities)
    edits: list[tuple[int, int, str]] = []
    for entity in sorted(entities, key=lambda e: min(m.start for m in e.mentions)):
        entry = find_entry(vault, entity.type, entity.canonical)
        if entry is None:
            entry = _new_entry(text, entity, seed, vault)
            vault.add(entry)
        edits.extend((m.start, m.end, _written(entry, m)) for m in entity.mentions)
    for start, end, surrogate in sorted(edits, reverse=True):  # from the end to the start
        text = text[:start] + surrogate + text[end:]
    return text
