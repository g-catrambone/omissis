"""R2: realistic fake values (task 2.5).

Every entity gets a fake value of its own type, drawn with a generator seeded by the
run seed, the type and the value: the same value gets the same fake in every text
and on every machine. A fake is drawn again when it, or a part of it, already occurs
in the text or in the vault, so restoration can never mistake a real value for a fake.
An amount is compared as a number: a fake amount never has the digits of a number of
the text or of the vault, whatever the currency, the separators and the decimals
around them ("€ 98", "98 Euro", "98,00 euro").

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
  a phone keeps `+39` and its first digit (0 for a landline, 3 for a mobile).
- IMPORTO: the same number of digits and the same decimals, so the same order of
  magnitude.
- DATA, DATA_NASCITA: another day of the same month, for a date written with its day
  (`16 novembre 2026`, `16/11/2026`, `2026-11-16`).
- ETA: the age moved by one to five years.
- RUOLO, STRUTTURA, NAZIONALITA and every special category: no fake, the R1
  placeholder.

The last line is a choice: a fake job, clinic or diagnosis would change the meaning
of the text and read as true. The same placeholder is written whenever there is no
realistic fake to give: a date that is not one of the three shapes above ("a
dicembre", "2019", "lunedì scorso", a date with an hour), an age or an amount
without a number ("trentenne"), or a value for which no free fake is left after
`MAX_DRAWS` draws. A person with a first name also records the fake surname and the
fake first name as `surrogate_variants`, aligned with the original surname and first
names in `original_variants`, read as the resolver reads them ("De Luca", "Maria
Grazia", no title): a mention of the surname alone is written, and restored, as the
surname alone.

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
from omissis.resolve import name_parts
from omissis.restore import numbers
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


def _amount(rng: random.Random, value: str) -> str | None:
    number = re.search(r"\d[\d.]*", value)  # the whole part, with the dots of the thousands
    if number is None:
        return None
    digits = [rng.choice("123456789")] + [rng.choice(string.digits) for _ in number.group()[1:]]
    whole = "".join(d if ch.isdigit() else ch for d, ch in zip(digits, number.group(), strict=True))
    return value[: number.start()] + whole + value[number.end() :]


_MONTHS = (
    "gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre"
)
# The three ways of writing a date with its day. Group `day` is what changes.
_DATE_SHAPES = (
    re.compile(
        rf"(?<![\d/.-])(?P<day>\d{{1,2}})\s+(?:{_MONTHS})\b(?:\s+\d{{4}}(?!\d))?", re.IGNORECASE
    ),
    re.compile(r"(?<![\d/.-])(?P<day>\d{1,2})[/.-]\d{1,2}[/.-]\d{2,4}(?![\d/.-])"),
    re.compile(r"(?<![\d/.-])\d{4}-\d{2}-(?P<day>\d{2})(?![\d/.-])"),
)


def _date(rng: random.Random, value: str) -> str | None:
    found = [(shape, m) for shape in _DATE_SHAPES for m in shape.finditer(value)]
    if len(found) != 1:
        return None  # no day to move, or more than one date
    shape, date = found[0]
    if re.search(r"\d", value[: date.start()] + value[date.end() :]):
        return None  # another number beside the date: an hour, a second day
    old = date.group("day")
    new = rng.choice([d for d in range(1, 29) if d != int(old)])
    # Two digits when the day was written so; a day before a month name only with its zero.
    padded = old.startswith("0") or (len(old) == 2 and shape is not _DATE_SHAPES[0])
    return value[: date.start("day")] + f"{new:0{2 if padded else 1}d}" + value[date.end("day") :]


def _age(rng: random.Random, value: str) -> str | None:
    number = re.search(r"\d+", value)
    if number is None:
        return None
    age, move = int(number.group()), rng.choice((-5, -4, -3, -2, -1, 1, 2, 3, 4, 5))
    new = age + move if age + move >= 1 else age - move  # a child does not get an age below 1
    return value[: number.start()] + str(new) + value[number.end() :]


def _email(rng: random.Random) -> str:
    name, surname = _first_name(rng, Gender.UNKNOWN), rng.choice(load_list("cognomi"))
    return f"{name}.{surname}@example.com".lower()


_BANK = re.compile(r"\b(banc[ao]|cassa|credito)\b", re.IGNORECASE)

# A generator gives None for a value that has not the shape it knows how to fake.
_GENERATORS: dict[SpanType, Callable[[random.Random, str], str | None]] = {
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


def _draw(
    rng: random.Random, entity: Entity
) -> tuple[str, tuple[str, ...], tuple[str, ...]] | None:
    """One candidate: the fake, the original variants and the fake variants, aligned.

    None when the value has not the shape its generator knows how to fake.
    """
    if entity.type is not SpanType.PERSONA:
        fake = _GENERATORS[entity.type](rng, entity.canonical)
        return None if fake is None else (fake, (), ())
    first_names, surname = name_parts(entity.canonical)
    fake_surname = rng.choice(load_list("cognomi"))
    if not first_names:
        return fake_surname, (), ()
    fake_first = _first_name(rng, entity.gender)
    originals, fakes = (surname, first_names), (fake_surname, fake_first)
    if " " in first_names:  # the first of two first names is also written alone
        originals, fakes = (*originals, first_names.split()[0]), (*fakes, fake_first)
    return f"{fake_first} {fake_surname}", originals, fakes


def _whole_numbers(value: str) -> set[str]:
    """The digits of every number of `value`, before the comma and without separators."""
    return {whole for whole, _ in numbers(value)}


def _gender(entity: Entity) -> Gender:
    """The gender a placeholder of `entity` carries: only a person has one."""
    return entity.gender if entity.type is SpanType.PERSONA else Gender.UNKNOWN


def _new_entry(text: str, entity: Entity, seed: int, vault: Vault) -> VaultEntry:
    if entity.type not in NO_FAKE:
        rng = random.Random(f"{seed}|{entity.type.value}|{normalise(entity.canonical)}")
        folded = text.casefold()
        taken = {
            normalise(v) for e in vault for v in (e.surrogate, e.original, *e.surrogate_variants)
        }
        values = (text, *(v for e in vault for v in (e.surrogate, e.original)))
        taken_numbers = set().union(*map(_whole_numbers, values))
        for _ in range(MAX_DRAWS):
            drawn = _draw(rng, entity)
            if drawn is None:
                break
            fake, originals, fakes = drawn
            parts = (fake, *fakes)
            if entity.type is SpanType.IMPORTO and _whole_numbers(fake) & taken_numbers:
                continue  # one number in two shapes cannot be restored safely
            if all(p.casefold() not in folded and normalise(p) not in taken for p in parts):
                return VaultEntry(
                    fake, entity.canonical, entity.type, entity.entity_id, originals, fakes
                )
    # No realistic fake: the type has none, the value has not the shape of one, or no
    # free value is left. The entity keeps the R1 placeholder.
    number = next_number(vault, entity.type, text)
    placeholder = make_placeholder(entity.type, number, _gender(entity))
    variants = tuple(dict.fromkeys(m.text for m in entity.mentions if m.text != entity.canonical))
    return VaultEntry(placeholder, entity.canonical, entity.type, entity.entity_id, variants)


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
        entry = find_entry(vault, entity.type, entity.canonical, _gender(entity))
        if entry is None:
            entry = _new_entry(text, entity, seed, vault)
            vault.add(entry)
        edits.extend((m.start, m.end, _written(entry, m)) for m in entity.mentions)
    for start, end, surrogate in sorted(edits, reverse=True):  # from the end to the start
        text = text[:start] + surrogate + text[end:]
    return text
