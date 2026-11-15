"""Restoration of original values in the cloud model's reply. Never guesses.

Task B2 builds steps 1 and 2 for R1 placeholders; fuzzy matching and R2 surrogates
come with task B8.

A *placeholder-like token* is a known type label followed by a number and,
optionally, a gender letter, with the parts joined by underscores or spaces, in any
case, with or without brackets: `[PERSONA_1_M]`, `[persona_1_m]`, `[PERSONA 1 M]`,
`PERSONA_1_M`, `[ IBAN_2 ]`. Its normalised form is the canonical placeholder
(`[PERSONA_1_M]`). To avoid touching ordinary Italian ("in data 12 ottobre"), a token
counts only when it shows a placeholder signal: a bracket, an underscore, or (to be
restored, not to be reported) an upper-case label such as `PERSONA 1`.
"""

from __future__ import annotations

import re

from omissis.contracts import (
    RestoreEvent,
    RestoreOutcome,
    SpanType,
    parse_placeholder,
)
from omissis.vault import Vault

_LABELS = sorted((t.value for t in SpanType), key=len, reverse=True)
_LABEL_ALTERNATIVES = "|".join(label.replace("_", "[ _]+") for label in _LABELS)
_TOKEN_RE = re.compile(
    rf"(?P<open>\[\s*)?(?<![A-Za-z0-9])(?P<label>{_LABEL_ALTERNATIVES})[ _]+(?P<n>\d+)"
    r"(?:[ _]+(?P<g>[MF]))?(?![A-Za-z0-9])(?P<close>\s*\])?",
    re.IGNORECASE,
)


def _label(match: re.Match[str]) -> str:
    return re.sub(r"[ _]+", "_", match["label"].upper())


def _normalise(match: re.Match[str]) -> str:
    gender = f"_{match['g'].upper()}" if match["g"] else ""
    return f"[{_label(match)}_{match['n']}{gender}]"


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
    if any(parse_placeholder(e.surrogate) is None for e in entries):
        raise NotImplementedError("restoring R2 surrogates is built by task B8")

    found_as: dict[str, str | None] = {}  # surrogate -> first non-exact form, None if exact
    suspicious: dict[str, RestoreEvent] = {}  # raw token -> event, in order of appearance
    by_type_number = {parse_placeholder(e.surrogate)[:2]: e.surrogate for e in entries}

    def substitute(match: re.Match[str]) -> str:
        raw = match.group()
        token = _normalise(match)
        has_signal = bool(match["open"] or match["close"] or "_" in raw)
        entry = vault.get(token)
        if entry is not None and (has_signal or match["label"].isupper()):
            if raw == entry.surrogate:
                found_as.setdefault(entry.surrogate, None)
            elif found_as.get(entry.surrogate) is None:
                found_as[entry.surrogate] = raw  # first repaired form, shown in the event
            return entry.original
        if has_signal and raw not in suspicious:
            # Same type and number as a vault entry, but a different form (gender suffix,
            # leading zeros): it is ours, altered, and there is no safe way to map it.
            near = by_type_number.get((SpanType(_label(match)), int(match["n"])))
            if near is not None:
                event = RestoreEvent(near, RestoreOutcome.ALTERED_UNRESOLVED, found_as=raw)
            else:
                event = RestoreEvent(token, RestoreOutcome.HALLUCINATED_TOKEN, found_as=raw)
            suspicious[raw] = event
        return raw

    restored = _TOKEN_RE.sub(substitute, reply)

    events = [
        RestoreEvent(e.surrogate, RestoreOutcome.RESTORED, found_as[e.surrogate])
        if e.surrogate in found_as
        else RestoreEvent(e.surrogate, RestoreOutcome.DROPPED)
        for e in entries
    ]
    return restored, events + list(suspicious.values())
