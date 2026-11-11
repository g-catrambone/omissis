"""Restoration of original values in the cloud model's reply. Never guesses."""

from __future__ import annotations

from omissis.contracts import RestoreEvent
from omissis.vault import Vault


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
    raise NotImplementedError("restore is built by tasks B2 (exact, normalised) and B8 (fuzzy)")
