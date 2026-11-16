"""Restoration of original values in the cloud model's reply. Never guesses.

Three steps, for R1 placeholders and for R2 fake values: exact match, normalised
match, fuzzy match at or above the threshold (task 2.6).

R1. A *placeholder-like token* is a known type label followed by a number and,
optionally, a gender letter. The parts may be joined by underscores, spaces, hyphens
or non-breaking hyphens, in any case, with or without brackets, and the brackets and
underscores may be escaped with a backslash, as Markdown does: `[PERSONA_1_M]`,
`[persona_1_m]`, `[PERSONA 1 M]`, `PERSONA_1_M`, `[PERSONA-1-M]`, `\\[PERSONA\\_1\\_M\\]`.
Its normalised form is the canonical placeholder. To avoid touching ordinary Italian
("in data 12 ottobre"), a token counts only when it shows a placeholder signal: a
bracket, an underscore, or (to be restored, not to be reported) an upper-case label
such as `PERSONA 1`. A token with the type and number of a vault entry but another
form (gender suffix, leading zeros) is ours, altered: it stays and is reported.
Fuzzy step: a bracketed token that is not a well-formed placeholder is restored
when it is close enough to exactly one placeholder of the vault and carries the same
digits (`[PERSONNA_1]`); the number is never guessed.

R2. A fake value is restored on whole tokens only, so "Lodi" inside "Lodigiano" is
left alone: first as written, then without regard to case and to the amount of white
space, then (the whole fake only, not its variants) on runs of as many words that
are close enough and carry the same digits. Two different runs that are both close
enough are not a safe match: the entry is reported as `altered_unresolved`. A fake
value that the reply uses on its own account is restored too: this cannot be told
apart, and it is why the number of restored fakes per reply is reported.

Every vault entry gets exactly one event; the worst outcome wins
(`altered_unresolved`, then `restored_fuzzy`, `restored`, `dropped`). After the
substitutions every placeholder-shaped token still in the text has an event,
whatever its label.
"""

from __future__ import annotations

import re
from difflib import SequenceMatcher

from omissis.contracts import (
    PLACEHOLDER_RE,
    RestoreEvent,
    RestoreOutcome,
    SpanType,
    VaultEntry,
    parse_placeholder,
)
from omissis.vault import Vault

_SEP = r"(?:\\?[ _\-\u2010\u2011])+"
_LABELS = sorted((t.value for t in SpanType), key=len, reverse=True)
_LABEL_ALTERNATIVES = "|".join(label.replace("_", _SEP) for label in _LABELS)
_TOKEN_RE = re.compile(
    rf"(?P<open>\\?\[\s*)?(?<![A-Za-z0-9])(?P<label>{_LABEL_ALTERNATIVES}){_SEP}(?P<n>\d+)"
    rf"(?:{_SEP}(?P<g>[MF]))?(?![A-Za-z0-9])(?P<close>\s*\\?\])?",
    re.IGNORECASE,
)
_BRACKETED_RE = re.compile(r"\\?\[[^\[\]\n]{1,40}\]")
_EDGE_PUNCTUATION = ".,;:!?()«»\"'"
_RANK = {
    RestoreOutcome.DROPPED: 0,
    RestoreOutcome.RESTORED: 1,
    RestoreOutcome.RESTORED_FUZZY: 2,
    RestoreOutcome.ALTERED_UNRESOLVED: 3,
}


def _label(match: re.Match[str]) -> str:
    return re.sub(_SEP, "_", match["label"].upper())


def _normalise(match: re.Match[str]) -> str:
    gender = f"_{match['g'].upper()}" if match["g"] else ""
    return f"[{_label(match)}_{match['n']}{gender}]"


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
        token = _normalise(match)
        has_signal = bool(match["open"] or match["close"] or "_" in raw)
        entry = vault.get(token)
        if entry is not None and (has_signal or match["label"].isupper()):
            out.record(entry.surrogate, RestoreOutcome.RESTORED, None if raw == token else raw)
            return entry.original
        if has_signal:
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
        if raw in out.suspicious or parse_placeholder(clean) is not None:
            return raw  # already reported, or well formed: never mapped to another entry
        near = [e for e in entries if _close(clean, e.surrogate, threshold)]
        if len(near) != 1:
            return raw
        out.record(near[0].surrogate, RestoreOutcome.RESTORED_FUZZY, raw)
        return near[0].original

    return _BRACKETED_RE.sub(substitute, text)


def _restore_forms(text: str, forms: list[tuple[str, str, VaultEntry]], out: _Outcomes) -> str:
    """Steps 1 and 2 for R2: each fake form on whole tokens, the longest first."""
    for fake, original, entry in sorted(forms, key=lambda form: -len(form[0])):
        pattern = r"\s+".join(re.escape(word) for word in fake.split())

        def substitute(match: re.Match[str], fake=fake, original=original, entry=entry) -> str:
            raw = match.group()
            out.record(entry.surrogate, RestoreOutcome.RESTORED, None if raw == fake else raw)
            return original

        text = re.sub(rf"(?<!\w){pattern}(?!\w)", substitute, text, flags=re.IGNORECASE)
    return text


def _restore_fakes(text: str, entries: list[VaultEntry], threshold: float, out: _Outcomes) -> str:
    """Steps 1 to 3 for R2: the whole fakes, their near misses, then their variants."""
    text = _restore_forms(text, [(e.surrogate, e.original, e) for e in entries], out)
    for entry in entries:
        if out.entries[entry.surrogate][0] is not RestoreOutcome.DROPPED:
            continue
        words = list(re.finditer(r"\S+", text))
        size = len(entry.surrogate.split())
        runs = [(words[i].start(), words[i + size - 1].end()) for i in range(len(words) - size + 1)]
        found: dict[str, None] = {}
        for start, end in runs:
            candidate = text[start:end].strip(_EDGE_PUNCTUATION)
            if candidate and _close(candidate, entry.surrogate, threshold):
                found[candidate] = None
        if len(found) == 1:
            (candidate,) = found
            out.record(entry.surrogate, RestoreOutcome.RESTORED_FUZZY, candidate)
            text = re.sub(
                rf"(?<!\w){re.escape(candidate)}(?!\w)", lambda m, e=entry: e.original, text
            )
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

    # No placeholder may remain silently: whatever is still there has an event.
    reported = {form for _, form in out.entries.values()} | set(out.suspicious)
    for match in PLACEHOLDER_RE.finditer(text):
        raw = match.group()
        if raw not in reported and raw not in out.suspicious:
            out.suspicious[raw] = RestoreEvent(raw, RestoreOutcome.HALLUCINATED_TOKEN, raw)
    return text, out.events()
