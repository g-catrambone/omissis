"""Detection entry point (block 4): one dispatch table from detector id to detector."""

from __future__ import annotations

import logging
from collections.abc import Callable
from importlib.util import find_spec
from typing import NamedTuple

from omissis.backends import CacheMissError
from omissis.config import ConfigError, RunConfig
from omissis.contracts import DetectorId, Span
from omissis.detect import classifier, hybrid, llm, presidio, rules
from omissis.detect.merge import merge

logger = logging.getLogger(__name__)


class _Detector(NamedTuple):
    find: Callable[[str, RunConfig], list[Span]]
    # Top-level modules the detector imports when it runs (dependency group `detect`).
    needs: tuple[str, ...] = ()


def _d0(text: str, config: RunConfig) -> list[Span]:
    return rules.find_all(text)


def _d4(text: str, config: RunConfig) -> list[Span]:
    return hybrid.find(text, config, {d: entry.find for d, entry in _DETECTORS.items()})


# The only place a detector id is tied to code. A detector is built when it is here:
# each task of block 4 added its line. An id with no line never falls through to D0.
_DETECTORS: dict[DetectorId, _Detector] = {
    DetectorId.D0: _Detector(_d0),
    DetectorId.D1: _Detector(presidio.find, presidio.NEEDS),
    DetectorId.D2: _Detector(classifier.find, classifier.NEEDS),
    DetectorId.D3: _Detector(llm.find),
    DetectorId.D4: _Detector(_d4, presidio.NEEDS + classifier.NEEDS),
}


def _missing(detector: _Detector) -> list[str]:
    return [name for name in detector.needs if find_spec(name) is None]


def supported_detectors() -> tuple[DetectorId, ...]:
    """The detectors that can run on this machine: built, and with their libraries installed.

    An import check only: no model is loaded and none is called.
    """
    return tuple(d for d, entry in _DETECTORS.items() if not _missing(entry))


def detect(text: str, detector: DetectorId, config: RunConfig) -> list[Span]:
    """Return the sensitive spans of `text` found by `detector`.

    Spans are sorted by `start` and non-overlapping. Overlaps are resolved inside:
    longer span wins, then higher confidence, then earlier position in
    `config.source_priority`. Every span satisfies `span.matches(text)`.
    Quasi-identifier spans are returned even when `config.mask_quasi` is false.
    Never raises on bad input or on a failing model: a failing detector logs and
    contributes no spans. `CacheMissError` and `ConfigError` (a cache miss in
    replay, a model that is not pinned, a library or a weights file missing on
    this machine) do propagate: returning no spans would send the text unmasked.
    A detector not built yet raises `NotImplementedError`.
    """
    detector = DetectorId(detector)
    entry = _DETECTORS.get(detector)
    if entry is None:
        raise NotImplementedError(f"detector {detector.value} is not built yet (block 4)")
    missing = _missing(entry)
    if missing:
        raise ConfigError(
            f"detector {detector.value} needs {', '.join(missing)}, not installed on this "
            "machine: run `uv sync --locked --group detect`"
        )
    if not isinstance(text, str):
        logger.warning("detect: expected str, got %s; returning no spans", type(text).__name__)
        return []
    try:
        found = entry.find(text, config)
    except (CacheMissError, ConfigError):
        raise
    except ImportError as exc:
        # Installed, but it does not load: as missing, or the text would go out unmasked.
        raise ConfigError(
            f"detector {detector.value} cannot load {exc.name or 'one of its libraries'} on "
            "this machine: run `uv sync --locked --group detect`"
        ) from exc
    except Exception as exc:  # a failing detector contributes no spans
        # Log the error type only: the message could quote the text.
        logger.error("detector %s failed (%s); returning no spans", detector, type(exc).__name__)
        return []
    return merge(found, config.source_priority)
