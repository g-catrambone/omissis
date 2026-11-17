"""D4: the hybrid detector (task 4.4). Composition only, no detection logic.

Direct identifiers come from D0, D1 and D2; quasi-identifiers, special categories and
the one direct type D3 is asked for (`llm.TYPES`: UTENTE) come from D3. A span outside
the share of its detector is dropped. D1 was added after the first run on
the pilot texts: D2 alone missed 7 person names of 26, D1 none. The spans keep the source of the
detector that found them, and `detect` resolves the overlaps with `merge`.

A sub-detector that fails is logged and contributes no spans; the spans of the
others are still returned. `CacheMissError` and `ConfigError` propagate, as in
`detect`.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Mapping

from omissis.backends import CacheMissError
from omissis.config import ConfigError, RunConfig
from omissis.contracts import DetectorId, Span, SpanClass
from omissis.detect import llm

logger = logging.getLogger(__name__)

Find = Callable[[str, RunConfig], list[Span]]

# Detector -> whether it supplies the direct identifiers (True) or the types of D3.
ROUTES = (
    (DetectorId.D0, True),
    (DetectorId.D1, True),
    (DetectorId.D2, True),
    (DetectorId.D3, False),
)


def find(text: str, config: RunConfig, detectors: Mapping[DetectorId, Find]) -> list[Span]:
    """The spans of D0, D1, D2 and D3 routed by class, possibly overlapping."""
    parts = [(d, detectors[d], direct) for d, direct in ROUTES]
    spans: list[Span] = []
    for detector, find_one, direct in parts:
        try:
            found = find_one(text, config)
        except (CacheMissError, ConfigError):
            raise
        except Exception as exc:
            # Log the error type only: the message could quote the text.
            logger.error("D4: detector %s failed (%s)", detector, type(exc).__name__)
            continue
        if direct:
            spans.extend(s for s in found if s.cls is SpanClass.DIRECT)
        else:
            spans.extend(s for s in found if s.type in llm.TYPES)
    return spans
