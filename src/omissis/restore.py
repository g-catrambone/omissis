"""Restoration of original values in the cloud model's reply. Never guesses.

Three steps, for R1 placeholders and for R2 fake values: exact match, normalised
match, fuzzy match at or above the threshold (task 2.6).

R1. A *placeholder-like token* is a known type label followed by a number and,
optionally, a gender letter. The parts may be joined by underscores, white space (a
line break too), hyphens or dashes, in any case, with or without brackets; the label
may carry its Italian accent, and the brackets and underscores may be escaped with a
backslash, as Markdown does: `[PERSONA_1_M]`, `[persona_1_m]`, `[PERSONA 1 M]`,
`PERSONA_1_M`, `[PERSONA-1-M]`, `[CITTÀ_1]`, `\\[PERSONA\\_1\\_M\\]`. Its normalised form
is the canonical placeholder. A token counts only when it is written as a
placeholder: with an underscore, between two brackets, or with its three parts in
upper case (`PERSONA 1 F`). A label and a number with none of these ("in data 12
ottobre", "IMPORTO 1.250,00 EURO", "DOCUMENTO 1", the model's own slot "[Numero IBAN
1]") are ordinary text and are never touched; nor is a number that goes on as a
decimal or a file name ("documento_1.pdf"). A token with the type and number of a vault entry but
another form (gender suffix, leading zeros) is ours, altered: it stays and is
reported. Fuzzy step: a bracketed token in which no label with its number can be
read is restored when it is close enough to exactly one placeholder of the vault and
carries the same digits (`[PERSONNA_1]`); the number is never guessed.

R2. A fake value is restored on whole tokens only, so "Lodi" inside "Lodigiano" and
"225,00" at the end of "1.225,00" are left alone: first as written, then without regard to
case and to the amount of white space. Then, for a fake of two or more words only
(the whole fake, not its variants), on runs of as many words in which every word is
close enough to the word in the same place, and a word with digits is the same. A
fake of one word has no fuzzy step: ordinary words are too close to it ("Biella",
"bella"). Two different runs that are both close enough are not a safe match: the
entry is reported as `altered_unresolved`. A fake value that the reply uses on its
own account is restored too: this cannot be told apart, and it is why the number of
restored fakes per reply is reported. A fake that the reply rewrites in another
format, or shortens, is not recognised: it stays in the text and its entry is
`dropped` (docs/evaluation_protocol.md, section 10).

Every vault entry gets exactly one event; the worst outcome wins
(`altered_unresolved`, then `restored_fuzzy`, `restored`, `dropped`). After the
substitutions every bracketed token in placeholder shape still in the text has an
event, whatever its label and its case.
"""

from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher

from omissis.contracts import (
    RestoreEvent,
    RestoreOutcome,
    SpanType,
    VaultEntry,
    parse_placeholder,
)
from omissis.vault import Vault

_SEP = r"(?:\\?[\s_\-\u2010\u2011\u2013])+"
_ACCENTED = {"A": "AÀÁ", "E": "EÈÉ", "I": "IÌÍ", "O": "OÒÓ", "U": "UÙÚ"}


def _label_pattern(label: str) -> str:
    """`label` with any separator between its words and each vowel also with an accent."""
    return "".join(
        _SEP if ch == "_" else f"[{_ACCENTED[ch]}]" if ch in _ACCENTED else ch for ch in label
    )


_LABELS = sorted((t.value for t in SpanType), key=len, reverse=True)
_LABEL_ALTERNATIVES = "|".join(_label_pattern(label) for label in _LABELS)
# Before the label: no letter or digit, also behind an underscore ("NUMERO_IBAN_1" is
# not ours, "_IBAN_1_" in Markdown emphasis is). After the number: no letter or digit,
# and no decimal, date or file name going on ("1.250", "1/12", "documento_1.pdf").
_TOKEN_RE = re.compile(
    rf"(?P<open>\\?\[\s*)?(?<![^\W_])(?<![^\W_]_)(?P<label>{_LABEL_ALTERNATIVES}){_SEP}"
    rf"(?P<n>\d+)(?:{_SEP}(?P<g>[MF]))?(?![^\W_])(?![.,/]\d)(?!(?-i:\.[a-z]))"
    r"(?P<close>\s*\\?\])?",
    re.IGNORECASE,
)
_BRACKETED_RE = re.compile(r"\\?\[[^\[\]\n]{1,40}\]")
# A bracketed token in placeholder shape, with any label and in any case.
_SHAPED_RE = re.compile(r"\[[^\W\d_]+(?:_[^\W\d_]+)*_\d+(?:_[^\W\d_]+)?\]")
_EDGE_PUNCTUATION = ".,;:!?()«»\"'_*"
_RANK = {
    RestoreOutcome.DROPPED: 0,
    RestoreOutcome.RESTORED: 1,
    RestoreOutcome.RESTORED_FUZZY: 2,
    RestoreOutcome.ALTERED_UNRESOLVED: 3,
}


def _label(match: re.Match[str]) -> str:
    plain = unicodedata.normalize("NFD", match["label"].upper())
    plain = "".join(ch for ch in plain if not unicodedata.combining(ch))
    return re.sub(_SEP, "_", plain)


def _normalise(match: re.Match[str]) -> str:
    gender = f"_{match['g'].upper()}" if match["g"] else ""
    return f"[{_label(match)}_{match['n']}{gender}]"


def _is_written_as_placeholder(match: re.Match[str]) -> bool:
    """False for a label and a number that are ordinary text ("DATA 12", "IBAN 1").

    Ours are a token with an underscore, one between two brackets, and the three
    parts of a person's placeholder in upper case ("PERSONA 1 F").
    """
    if "_" in match.group() or (match["open"] and match["close"]):
        return True
    return bool(match["g"]) and match["label"].isupper() and match["g"].isupper()


def placeholder_numbers(text: str) -> set[tuple[SpanType, int]]:
    """The type and number of every token of `text` that restoration reads as a placeholder."""
    return {
        (SpanType(_label(match)), int(match["n"]))
        for match in _TOKEN_RE.finditer(text)
        if _is_written_as_placeholder(match)
    }


def _digits(value: str) -> str:
    return re.sub(r"\D", "", value)


def _close(a: str, b: str, threshold: float) -> bool:
    """True when `a` and `b` carry the same digits and are similar enough."""
    if _digits(a) != _digits(b):
        return False
    return SequenceMatcher(None, a.casefold(), b.casefold()).ratio() >= threshold


class _Outcomes:
    """The outcome of every vault entry (the worst one wins) and the suspicious tokens."""

    def __init__(self, entries: list[VaultEntry]) -> None:
        self.entries = {e.surrogate: (RestoreOutcome.DROPPED, None) for e in entries}
        self.suspicious: dict[str, RestoreEvent] = {}  # raw token -> event, as they appear

    def record(self, surrogate: str, outcome: RestoreOutcome, found_as: str | None) -> None:
        current, current_form = self.entries[surrogate]
        if _RANK[outcome] > _RANK[current]:
            self.entries[surrogate] = (outcome, found_as)
        elif outcome is current and current_form is None:
            self.entries[surrogate] = (outcome, found_as)  # the first form that was repaired

    def events(self) -> list[RestoreEvent]:
        own = [RestoreEvent(s, outcome, form) for s, (outcome, form) in self.entries.items()]
        return own + list(self.suspicious.values())


def _restore_placeholders(
    reply: str, vault: Vault, entries: list[VaultEntry], out: _Outcomes
) -> str:
    """Steps 1 and 2 for R1: exact and normalised placeholders."""
    by_type_number = {parse_placeholder(e.surrogate)[:2]: e.surrogate for e in entries}

    def substitute(match: re.Match[str]) -> str:
        raw = match.group()
        if not _is_written_as_placeholder(match):
            return raw
        token = _normalise(match)
        entry = vault.get(token)
        if entry is not None:
            out.record(entry.surrogate, RestoreOutcome.RESTORED, None if raw == token else raw)
            return entry.original
        # Same type and number as a vault entry, but a different form (gender suffix,
        # leading zeros): it is ours, altered, and there is no safe way to map it.
        near = by_type_number.get((SpanType(_label(match)), int(match["n"])))
        if near is not None:
            out.record(near, RestoreOutcome.ALTERED_UNRESOLVED, raw)
        elif raw not in out.suspicious:
            out.suspicious[raw] = RestoreEvent(token, RestoreOutcome.HALLUCINATED_TOKEN, raw)
        return raw

    return _TOKEN_RE.sub(substitute, reply)


def _restore_placeholders_fuzzy(
    text: str, entries: list[VaultEntry], threshold: float, out: _Outcomes
) -> str:
    """Step 3 for R1: a malformed bracketed token close to exactly one placeholder."""

    def substitute(match: re.Match[str]) -> str:
        raw = match.group()
        clean = raw.replace("\\", "")
        if parse_placeholder(clean) is not None or _TOKEN_RE.search(clean):
            # Well formed, or read by the steps before (and left there as altered or
            # unknown): never mapped to another entry.
            return raw
        near = [e for e in entries if _close(clean, e.surrogate, threshold)]
        if len(near) != 1:
            return raw
        out.record(near[0].surrogate, RestoreOutcome.RESTORED_FUZZY, raw)
        return near[0].original

    return _BRACKETED_RE.sub(substitute, text)


def _whole(form: str) -> str:
    """The pattern of `form` as a whole token: not inside a word, nor the end of a number.

    A letter or a digit next to the form makes it a part of a longer token; an
    underscore does not (Markdown emphasis). What follows a number is left free: a
    detector may mark "€ 320" in "€ 320,00", and the fake is then followed by the
    decimals of the original.
    """
    pattern = r"\s+".join(re.escape(word) for word in form.split())
    before = r"(?<![^\W_])(?<!\d[.,])" if form[:1].isdigit() else r"(?<![^\W_])"
    return before + pattern + r"(?![^\W_])"


def _restore_forms(text: str, forms: list[tuple[str, str, VaultEntry]], out: _Outcomes) -> str:
    """Steps 1 and 2 for R2: each fake form on whole tokens, the longest first."""
    for fake, original, entry in sorted(forms, key=lambda form: -len(form[0])):

        def substitute(match: re.Match[str], fake=fake, original=original, entry=entry) -> str:
            raw = match.group()
            out.record(entry.surrogate, RestoreOutcome.RESTORED, None if raw == fake else raw)
            return original

        text = re.sub(_whole(fake), substitute, text, flags=re.IGNORECASE)
    return text


def _near_miss(words: list[str], fake: list[str], threshold: float) -> bool:
    """True when every word is close to the word of the fake in the same place.

    A word with digits must be the same: another number is never a misspelling.
    """
    for got, want in zip(words, fake, strict=True):
        if re.search(r"\d", got + want):
            if got != want:
                return False
        elif SequenceMatcher(None, got.casefold(), want.casefold()).ratio() < threshold:
            return False
    return True


def _restore_fakes(text: str, entries: list[VaultEntry], threshold: float, out: _Outcomes) -> str:
    """Steps 1 to 3 for R2: the whole fakes, their near misses, then their variants."""
    text = _restore_forms(text, [(e.surrogate, e.original, e) for e in entries], out)
    for entry in entries:
        fake = entry.surrogate.split()
        if len(fake) < 2:
            continue  # ordinary words are too close to a fake of one word
        words = list(re.finditer(r"\S+", text))
        found: dict[str, None] = {}
        for i in range(len(words) - len(fake) + 1):
            run = text[words[i].start() : words[i + len(fake) - 1].end()]
            candidate = run.strip(_EDGE_PUNCTUATION)
            got = candidate.split()
            if len(got) == len(fake) and _near_miss(got, fake, threshold):
                found[candidate] = None
        if len(found) == 1:
            (candidate,) = found
            out.record(entry.surrogate, RestoreOutcome.RESTORED_FUZZY, candidate)
            text = re.sub(_whole(candidate), lambda m, e=entry: e.original, text)
        elif found:
            out.record(entry.surrogate, RestoreOutcome.ALTERED_UNRESOLVED, next(iter(found)))
    variants = [
        (fake, original, e)
        for e in entries
        if out.entries[e.surrogate][0] is not RestoreOutcome.ALTERED_UNRESOLVED
        for fake, original in zip(e.surrogate_variants, e.original_variants, strict=False)
    ]
    return _restore_forms(text, variants, out)


def restore(reply: str, vault: Vault, fuzzy_threshold: float) -> tuple[str, list[RestoreEvent]]:
    """Put the original values back into `reply`.

    Order: (1) exact match; (2) normalised match (case, spacing, missing brackets,
    underscores as spaces); (3) fuzzy match accepted only at or above
    `fuzzy_threshold`. A placeholder-shaped token absent from the vault gives
    `hallucinated_token`; a token that looks like a surrogate but has no safe match
    stays in place and gives `altered_unresolved`; a surrogate the reply does not
    use gives `dropped`. R2 surrogates match on whole tokens only. Returns the
    restored text and one event per vault entry or suspicious token.
    """
    if not 0 <= fuzzy_threshold <= 1:
        raise ValueError(f"fuzzy_threshold must be in [0, 1], got {fuzzy_threshold}")
    entries = list(vault)
    placeholders = [e for e in entries if parse_placeholder(e.surrogate) is not None]
    fakes = [e for e in entries if parse_placeholder(e.surrogate) is None]
    out = _Outcomes(entries)

    text = _restore_placeholders(reply, vault, placeholders, out)
    text = _restore_placeholders_fuzzy(text, placeholders, fuzzy_threshold, out)
    text = _restore_fakes(text, fakes, fuzzy_threshold, out)

    # No placeholder may remain silently: whatever is still there has an event. A token
    # is covered when an event names it, or the part of it that was read ("[PERSONA_1").
    reported = [form for _, form in out.entries.values() if form] + list(out.suspicious)
    for match in _SHAPED_RE.finditer(text):
        raw = match.group()
        if not any(raw.startswith(form) for form in reported):
            out.suspicious[raw] = RestoreEvent(raw, RestoreOutcome.HALLUCINATED_TOKEN, raw)
    return text, out.events()
