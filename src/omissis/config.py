"""Run configuration and model pinning (docs/interfaces.md, section 4).

One YAML file defines one run; unknown keys are an error. `run_id` identifies what a
run computes, not where its responses come from: it hashes the evaluated settings and
the resolved models, never `backend`, `cache_dir` or the path of the models file.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from omissis.contracts import DetectorId, Strategy

UNPINNED = "TO_BE_PINNED"
ROLES = ("cloud", "attacker", "judge", "generator", "d3", "d2")
BACKENDS = ("cloud", "replay")


class ConfigError(ValueError):
    """A configuration or models file is invalid."""


@dataclass(frozen=True)
class RunConfig:
    detector: DetectorId
    strategy: Strategy
    mask_quasi: bool
    backend: str
    seed: int
    fuzzy_threshold: float
    source_priority: tuple[DetectorId, ...]
    models_file: Path
    cache_dir: Path

    def __post_init__(self) -> None:
        try:
            object.__setattr__(self, "detector", DetectorId(self.detector))
            object.__setattr__(self, "strategy", Strategy(self.strategy))
            priority = self.source_priority
            if isinstance(priority, str) or not isinstance(priority, list | tuple):
                raise ConfigError("source_priority must be a list of detector ids")
            object.__setattr__(self, "source_priority", tuple(DetectorId(d) for d in priority))
        except ValueError as exc:
            raise ConfigError(str(exc)) from exc
        if len(set(self.source_priority)) != len(self.source_priority):
            raise ConfigError("source_priority contains duplicates")
        if not isinstance(self.mask_quasi, bool):
            raise ConfigError(f"mask_quasi must be a boolean, got {self.mask_quasi!r}")
        if self.backend not in BACKENDS:
            raise ConfigError(f"backend must be one of {BACKENDS}, got {self.backend!r}")
        if isinstance(self.seed, bool) or not isinstance(self.seed, int):
            raise ConfigError(f"seed must be an integer, got {self.seed!r}")
        threshold = self.fuzzy_threshold
        if isinstance(threshold, bool) or not isinstance(threshold, int | float):
            raise ConfigError(f"fuzzy_threshold must be a number, got {threshold!r}")
        if not 0 <= threshold <= 1:
            raise ConfigError(f"fuzzy_threshold must be in [0, 1], got {threshold}")
        object.__setattr__(self, "fuzzy_threshold", float(threshold))
        for name in ("models_file", "cache_dir"):
            value = getattr(self, name)
            if not isinstance(value, str | Path) or not str(value):
                raise ConfigError(f"{name} must be a path, got {value!r}")
            object.__setattr__(self, name, Path(value))


_FIELDS = tuple(f.name for f in dataclasses.fields(RunConfig))


def _build(data: Mapping[str, Any]) -> RunConfig:
    unknown = sorted(set(data) - set(_FIELDS))
    if unknown:
        raise ConfigError(f"unknown configuration keys: {unknown}")
    missing = sorted(set(_FIELDS) - set(data))
    if missing:
        raise ConfigError(f"missing configuration keys: {missing}")
    return RunConfig(**data)


def load_config(path: str | Path, overrides: Mapping[str, Any] | None = None) -> RunConfig:
    """Load a run configuration from YAML, apply `overrides`, validate everything."""
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ConfigError(f"{path}: a run configuration must be a mapping")
    return _build({**data, **(overrides or {})})


def with_overrides(config: RunConfig, **changes: Any) -> RunConfig:
    """Return a copy of `config` with `changes` applied and validated."""
    current = {name: getattr(config, name) for name in _FIELDS}
    return _build({**current, **changes})


@dataclass(frozen=True)
class ModelSpec:
    role: str
    provider: str
    id: str
    revision: str

    @property
    def pinned(self) -> bool:
        return UNPINNED not in (self.provider, self.id, self.revision)


def load_models(path: str | Path) -> dict[str, ModelSpec]:
    """Load the models file: one entry per role, each with provider, id and revision."""
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ConfigError(f"{path}: the models file must be a mapping of roles")
    if set(data) != set(ROLES):
        raise ConfigError(f"{path}: roles must be exactly {list(ROLES)}, got {sorted(data)}")
    models = {}
    for role in ROLES:
        entry = data[role]
        if not isinstance(entry, dict) or set(entry) != {"provider", "id", "revision"}:
            raise ConfigError(f"{path}: role {role!r} needs exactly provider, id and revision")
        for key, value in entry.items():
            if not isinstance(value, str) or not value:
                raise ConfigError(f"{path}: {role}.{key} must be a non-empty string")
        models[role] = ModelSpec(role=role, **entry)
    return models


def require_pinned(models: Mapping[str, ModelSpec], role: str) -> ModelSpec:
    """Return the model for `role`, refusing a role that is missing or not pinned."""
    model = models.get(role)
    if model is None:
        raise ConfigError(f"no model configured for role {role!r}")
    if not model.pinned:
        raise ConfigError(f"model for role {role!r} is not pinned in the models file")
    return model


def run_id(config: RunConfig) -> str:
    """First 12 hex characters of the SHA-256 of the evaluated settings and resolved models."""
    models = load_models(config.models_file)
    resolved = {
        "detector": config.detector.value,
        "strategy": config.strategy.value,
        "mask_quasi": config.mask_quasi,
        "seed": config.seed,
        "fuzzy_threshold": config.fuzzy_threshold,
        "source_priority": [d.value for d in config.source_priority],
        "models": {
            role: {"provider": m.provider, "id": m.id, "revision": m.revision}
            for role, m in models.items()
        },
    }
    payload = json.dumps(resolved, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]
