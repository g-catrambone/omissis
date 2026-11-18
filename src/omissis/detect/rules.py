"""D0: regular expressions plus checksum validation (block 1).

One function per type, each returning spans with source `D0`:

| Function | Type | Validation | Confidence |
|---|---|---|---|
| `find_iban` | IBAN | ISO 13616 mod-97; Italian IBANs must have 27 characters | 1.0 |
| `find_cf` | CF | structure, month letter, day, check character (omocodia accepted) | 1.0 |
| `find_piva` | PIVA | 11 digits, office code, check digit | 1.0 |
| `find_telefono` | TELEFONO | mobile (3xx, 9-10 digits) or landline (0x, 6-11 digits) | 0.9 |
| `find_email` | EMAIL | shape only | 1.0 |
| `find_importo` | IMPORTO | number with €, EUR or euro before or after it | 0.9 |

Spans may overlap across types (an 11-digit landline can also pass the P.IVA
check); `detect` resolves overlaps with `merge`. The checksum types get the
higher confidence, so an identical phone/P.IVA span is kept as PIVA. Both are
direct identifiers, so the masking decision does not change.

Known limits: phone numbers are recognised by shape, so other 6-11 digit codes
starting with 0 or 3 (case numbers, account numbers) are reported as TELEFONO;
amounts written without a currency ("1.200,00") are not found.
"""

from __future__ import annotations

import re
from collections.abc import Callable

from omissis.contracts import DetectorId, Span, SpanType

SOURCE = DetectorId.D0.value

# --- IBAN -----------------------------------------------------------------------

# Candidate: country code, check digits, then 11-30 alphanumerics, optionally in groups
# separated by single spaces. Validation decides; trailing groups that do not belong to
# the IBAN are trimmed off (see `_trim`).
_IBAN_CANDIDATE = re.compile(r"(?<![A-Za-z0-9])[A-Z]{2}\d{2}(?: ?[A-Z0-9]){11,30}", re.IGNORECASE)
_IBAN_COMPACT = re.compile(r"[A-Z]{2}(0[2-9]|[1-8]\d|9[0-8])[A-Z0-9]{11,30}")
_IT_IBAN = re.compile(r"IT\d{2}[A-Z]\d{10}[A-Z0-9]{12}")


def iban_is_valid(value: str) -> bool:
    """True when `value` (spaces allowed) is an IBAN that passes the ISO 13616 mod-97 check."""
    compact = value.replace(" ", "").upper()
    if not _IBAN_COMPACT.fullmatch(compact):
        return False
    if compact.startswith("IT") and not _IT_IBAN.fullmatch(compact):
        return False
    rearranged = compact[4:] + compact[:4]
    digits = "".join(str(int(ch, 36)) for ch in rearranged)  # A=10 ... Z=35
    return int(digits) % 97 == 1


def find_iban(text: str) -> list[Span]:
    return _find_trimmed(text, _IBAN_CANDIDATE, iban_is_valid, SpanType.IBAN, 1.0)


# --- Codice fiscale --------------------------------------------------------------

_OMOCODE = "LMNPQRSTUV"  # letters that replace the digits 0-9 in omocodia
_D = f"[0-9{_OMOCODE}]"
_CF_SHAPE = rf"[A-Z]{{6}}{_D}{{2}}[ABCDEHLMPRST]{_D}{{2}}[A-Z]{_D}{{3}}[A-Z]"
_CF_RE = re.compile(rf"(?<![A-Za-z0-9]){_CF_SHAPE}(?![A-Za-z0-9])", re.IGNORECASE)
_CF_FULL = re.compile(_CF_SHAPE)

# Values of a character in an odd position (1st, 3rd, ... 15th); digits share the
# values of the letters A-J.
_CF_ODD_VALUES = [1, 0, 5, 7, 9, 13, 15, 17, 19, 21, 2, 4, 18, 20, 11, 3, 6, 8, 12, 14, 16]
_CF_ODD_VALUES += [10, 22, 25, 24, 23]


def _cf_value(ch: str, odd: bool) -> int:
    index = int(ch) if ch.isdigit() else ord(ch) - ord("A")
    return _CF_ODD_VALUES[index] if odd else index


def cf_check_character(first15: str) -> str:
    """Check character of a codice fiscale from its first 15 characters (uppercase)."""
    total = sum(_cf_value(ch, odd=i % 2 == 0) for i, ch in enumerate(first15))
    return chr(ord("A") + total % 26)


def cf_is_valid(value: str) -> bool:
    """True when `value` has the codice fiscale structure, a valid day and check character."""
    cf = value.upper()
    if not _CF_FULL.fullmatch(cf):
        return False
    day = int("".join(str(_OMOCODE.index(c)) if c in _OMOCODE else c for c in cf[9:11]))
    if not (1 <= day <= 31 or 41 <= day <= 71):  # women: day + 40
        return False
    return cf_check_character(cf[:15]) == cf[15]


def find_cf(text: str) -> list[Span]:
    return [
        _span(m.start(), m.end(), text, SpanType.CF, 1.0)
        for m in _CF_RE.finditer(text)
        if cf_is_valid(m.group())
    ]


# --- Partita IVA -----------------------------------------------------------------

# 11 digits not touching other digits or letters; an "IT" prefix is allowed but not
# part of the span (the span is the shortest stretch that carries the information).
_PIVA_RE = re.compile(r"(?:(?<=IT)|(?<![A-Za-z0-9]))\d{11}(?![A-Za-z0-9])")


def piva_is_valid(value: str) -> bool:
    """True when `value` is 11 digits with a valid office code and check digit."""
    if not re.fullmatch(r"\d{11}", value) or value[:7] == "0000000":
        return False
    office = int(value[7:10])
    if not (1 <= office <= 100 or office in (120, 121, 888, 999)):
        return False
    total = 0
    for i, ch in enumerate(value[:10]):
        digit = int(ch)
        if i % 2 == 1:  # 2nd, 4th, ... 10th digit: doubled, minus 9 if above 9
            digit = digit * 2 - 9 if digit > 4 else digit * 2
        total += digit
    return (10 - total % 10) % 10 == int(value[10])


def find_piva(text: str) -> list[Span]:
    return [
        _span(m.start(), m.end(), text, SpanType.PIVA, 1.0)
        for m in _PIVA_RE.finditer(text)
        if piva_is_valid(m.group())
    ]


# --- Telefono --------------------------------------------------------------------

# Optional +39 / 0039 / (+39) prefix, then digit runs separated by single spaces, dots,
# slashes or hyphens. The first run starts with 3 (mobile) or 0 plus a non-zero digit
# (landline). Runs that make the number too long are trimmed off.
_PHONE_RE = re.compile(
    r"(?<![\w+.,/-])(?:(?:\+|00)39[ .-]?|\(\+39\) ?)?(?:3|0[1-9])\d*(?:[ ./-]\d+)*"
)
_PHONE_PREFIX = re.compile(r"(?:\+|00)39[ .-]?|\(\+39\) ?")


def _phone_digits_ok(runs: list[str]) -> bool:
    digits = "".join(runs)
    lengths = [len(r) for r in runs]
    if len(lengths) == 3 and lengths[0] <= 2 and lengths[1] <= 2 and lengths[2] in (2, 4):
        return False  # a date such as 01/02/2026
    if len(lengths) == 2 and lengths[0] <= 2 and lengths[1] == 4:
        return False  # a month and year such as 03/2026
    if digits[0] == "3":
        return 9 <= len(digits) <= 10
    return 6 <= len(digits) <= 11


def find_telefono(text: str) -> list[Span]:
    spans = []
    for m in _PHONE_RE.finditer(text):
        prefix = _PHONE_PREFIX.match(m.group())
        body_start = m.start() + (prefix.end() if prefix else 0)
        runs = [(r.start(), r.end()) for r in re.finditer(r"\d+", text[body_start : m.end()])]
        for k in range(len(runs), 0, -1):
            end = body_start + runs[k - 1][1]
            if end < len(text) and text[end].isalnum():
                continue  # the last run runs into a word
            if _phone_digits_ok([text[body_start + a : body_start + b] for a, b in runs[:k]]):
                spans.append(_span(m.start(), end, text, SpanType.TELEFONO, 0.9))
                break
    return spans


# --- Email -----------------------------------------------------------------------

_EMAIL_RE = re.compile(
    r"(?<![\w.%+-])[A-Za-z0-9](?:[A-Za-z0-9._%+-]*[A-Za-z0-9_%+-])?"
    r"@(?:[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?\.)+[A-Za-z]{2,}(?![A-Za-z0-9-])"
)


def find_email(text: str) -> list[Span]:
    return [_span(m.start(), m.end(), text, SpanType.EMAIL, 1.0) for m in _EMAIL_RE.finditer(text)]


# --- Importo in euro -------------------------------------------------------------

# Italian number format: thousands with dots, up to two decimals with a comma.
_NUMBER = r"(?:\d{1,3}(?:\.\d{3})+|\d+)(?:,\d{1,2})?"
_MULTIPLIER = r"(?: ?(?:mila|milioni|miliardi)(?: di)?)?"
_CURRENCY = r"(?:€|EUR|EURO|[Ee]uro)"
_IMPORTO_RE = re.compile(
    rf"(?<![\w.,]){_CURRENCY} ?{_NUMBER}{_MULTIPLIER}(?![\d\w])"
    rf"|(?<![\w.,]){_NUMBER}{_MULTIPLIER} ?{_CURRENCY}(?!\w)"
)


def find_importo(text: str) -> list[Span]:
    return [
        _span(m.start(), m.end(), text, SpanType.IMPORTO, 0.9) for m in _IMPORTO_RE.finditer(text)
    ]


# --- All rules -------------------------------------------------------------------

RULES: tuple[Callable[[str], list[Span]], ...] = (
    find_iban,
    find_cf,
    find_piva,
    find_telefono,
    find_email,
    find_importo,
)


def find_all(text: str) -> list[Span]:
    """Every D0 span of `text`, possibly overlapping; `detect` merges them."""
    return [span for rule in RULES for span in rule(text)]


# --- helpers ---------------------------------------------------------------------


def _span(start: int, end: int, text: str, type: SpanType, confidence: float) -> Span:
    return Span(start, end, text[start:end], type, confidence, SOURCE)


def _find_trimmed(
    text: str,
    pattern: re.Pattern[str],
    is_valid: Callable[[str], bool],
    type: SpanType,
    confidence: float,
) -> list[Span]:
    """Longest valid prefix of each candidate that ends at a space or at the candidate's end.

    The search goes on from the end of what was accepted, or right after the start of a
    candidate with no valid prefix: a candidate may run into the start of the next value
    ("da IT… a IT…"), which must still be found.
    """
    spans = []
    position = 0
    while (m := pattern.search(text, position)) is not None:
        candidate = m.group()
        cuts = [i for i, ch in enumerate(candidate) if ch == " "] + [len(candidate)]
        position = m.start() + 1
        for cut in reversed(cuts):
            if m.start() + cut < len(text) and text[m.start() + cut].isalnum():
                continue  # the candidate runs into a word
            if is_valid(candidate[:cut]):
                spans.append(_span(m.start(), m.start() + cut, text, type, confidence))
                position = m.start() + cut
                break
    return spans
