"""Amounts and dates as written in the texts, turned into comparable values.

The formats are the ones the annotation guide allows (section 5): amounts with a dot
for the thousands and a comma for the decimals, next to `€`, `EUR` or `euro`; dates
as `16 novembre 2026`, `16/11/2026`, `16.11.2026`, and ISO `2026-11-16`. Anything
else gives None: the caller decides what that means, nothing is guessed.
"""

from __future__ import annotations

import re
from datetime import date

MONTHS = (
    "gennaio febbraio marzo aprile maggio giugno luglio agosto settembre ottobre novembre dicembre"
).split()
_NUMBER = re.compile(r"(?<![\d.,])(\d{1,3}(?:\.\d{3})+|\d+)(?:,(\d{1,2}))?(?![\d.,]*\d)")
_MULTIPLIERS = {"mila": 1_000, "milioni": 1_000_000, "milione": 1_000_000}
_NUMERIC_DATE = re.compile(r"(\d{1,2})[/.\-](\d{1,2})[/.\-](\d{4})")
_ISO_DATE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
_WORD_DATE = re.compile(rf"(\d{{1,2}})°?\s+({'|'.join(MONTHS)})\s+(\d{{4}})", re.IGNORECASE)


def parse_amount(value: str) -> float | None:
    """The euro amount written in `value`, rounded to 2 decimals; None without one number."""
    numbers = _NUMBER.findall(value)
    if len(numbers) != 1:
        return None
    whole, cents = numbers[0]
    amount = float(whole.replace(".", "")) + (float(f"0.{cents}") if cents else 0.0)
    for word, factor in _MULTIPLIERS.items():
        if re.search(rf"\b{word}\b", value, re.IGNORECASE):
            amount *= factor
    return round(amount, 2)


def parse_date(value: str) -> str | None:
    """The date written in `value` as `YYYY-MM-DD`; None when day, month or year is missing."""
    value = value.strip()
    if match := _ISO_DATE.fullmatch(value):
        year, month, day = (int(g) for g in match.groups())
    elif match := _NUMERIC_DATE.search(value):
        day, month, year = (int(g) for g in match.groups())
    elif match := _WORD_DATE.search(value):
        day, year = int(match[1]), int(match[3])
        month = MONTHS.index(match[2].lower()) + 1
    else:
        return None
    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None


_THINK = re.compile(r"<think>.*?</think>", re.DOTALL)


def extract_json(reply: str):
    """The JSON object written in a model reply, or None.

    Reasoning in `<think>` tags, a code fence and words around the object are ignored:
    the object is what lies between the first `{` and the last `}`.
    """
    import json

    reply = _THINK.sub("", reply)
    start, end = reply.find("{"), reply.rfind("}")
    if start == -1 or end < start:
        return None
    try:
        value = json.loads(reply[start : end + 1])
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None
