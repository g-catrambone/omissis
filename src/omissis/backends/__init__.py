"""LLM request types, cache key, provider registry and `complete` (docs/interfaces.md, section 3).

Every LLM call in the project goes through `complete`. Only functions registered with
`register_provider` talk to a model; a provider does no caching.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from omissis.config import ModelSpec, RunConfig


@dataclass(frozen=True)
class LLMRequest:
    role: str
    prompt: str
    system: str | None = None
    params: Mapping[str, Any] = field(default_factory=lambda: {"temperature": 0})

    def __post_init__(self) -> None:
        # Read-only copy, so a request cannot change after its cache key is computed.
        object.__setattr__(self, "params", MappingProxyType(dict(self.params)))


@dataclass(frozen=True)
class LLMResponse:
    text: str
    model_id: str
    revision: str
    cached: bool


ProviderFn = Callable[[ModelSpec, LLMRequest], str]

_PROVIDERS: dict[str, ProviderFn] = {}


class CacheMissError(RuntimeError):
    """A request is not in the cache and the backend is `replay`."""


def cache_key(model: ModelSpec, request: LLMRequest) -> str:
    """SHA-256 hex digest of the sorted JSON of {id, revision, system, prompt, params}."""
    payload = {
        "id": model.id,
        "revision": model.revision,
        "system": request.system,
        "prompt": request.prompt,
        "params": dict(request.params),
    }
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def register_provider(name: str, fn: ProviderFn) -> None:
    """Register `fn` as the provider called `name`; registering a name twice is an error."""
    if name in _PROVIDERS:
        raise ValueError(f"provider already registered: {name!r}")
    _PROVIDERS[name] = fn


def complete(request: LLMRequest, config: RunConfig) -> LLMResponse:
    """Answer `request` from the cache, or from the provider on a miss.

    Looks the request up in `config.cache_dir` by `cache_key`. Hit: returns the
    stored response with `cached=True`. Miss with `config.backend == "cloud"`: calls
    the provider registered for the model, appends the exchange to the cache
    (`<cache_dir>/<role>.jsonl`), returns it. Miss with `"replay"`: raises
    `CacheMissError` and never touches the network. Refuses a role whose model is
    not pinned.
    """
    raise NotImplementedError("backends.complete is built by task B3")
