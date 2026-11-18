"""LLM request types, cache key, provider registry and `complete` (docs/interfaces.md, section 3).

Every LLM call in the project goes through `complete`. Only functions registered with
`register_provider` talk to a model; a provider does no caching.
"""

from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from types import MappingProxyType
from typing import Any

from omissis.config import ConfigError, ModelSpec, RunConfig, load_models, require_pinned


@dataclass(frozen=True)
class LLMRequest:
    role: str
    prompt: str
    system: str | None = None
    params: Mapping[str, Any] = field(default_factory=lambda: {"temperature": 0})

    def __post_init__(self) -> None:
        # `temperature: 0` is always there: what the caller passes is merged over it.
        # Integral floats become integers, so that 0 and 0.0 give one cache key.
        params = {"temperature": 0, **copy.deepcopy(dict(self.params))}
        for name, value in params.items():
            if isinstance(value, float) and value.is_integer():
                params[name] = int(value)
        # A read-only copy, nested values included, so that a request cannot change
        # after its cache key is computed.
        object.__setattr__(self, "params", MappingProxyType(params))


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


class TruncatedReplyError(RuntimeError):
    """The model stopped at the token limit: the reply is incomplete and is not cached."""


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
    model = require_pinned(load_models(config.models_file), request.role)
    key = cache_key(model, request)
    path = Path(config.cache_dir) / f"{request.role}.jsonl"

    stored = _lookup(path, key)
    if stored is not None:
        return LLMResponse(stored["response"], stored["model_id"], stored["revision"], cached=True)
    if config.backend == "replay":
        raise CacheMissError(
            f"no cached response for role {request.role!r} (key {key[:12]}…) in {path}; "
            "run once with backend: cloud to fill the cache"
        )

    provider = _PROVIDERS.get(model.provider)
    if provider is None:
        raise ConfigError(f"no provider registered under {model.provider!r} (role {model.role!r})")
    text = provider(model, request)
    if not isinstance(text, str):
        raise TypeError(f"provider {model.provider!r} returned {type(text).__name__}, not str")

    record = {
        "key": key,
        "role": request.role,
        "model_id": model.id,
        "revision": model.revision,
        "system": request.system,
        "prompt": request.prompt,
        "params": dict(request.params),
        "response": text,
        "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    # A file that does not end with a newline (a merge, an editor) gets one first.
    broken = path.exists() and path.stat().st_size > 0 and not path.read_bytes().endswith(b"\n")
    with open(path, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(("\n" if broken else "") + json.dumps(record, ensure_ascii=False) + "\n")
    return LLMResponse(text, model.id, model.revision, cached=False)


_ANSWER_FIELDS = ("response", "model_id", "revision")  # what a cache hit returns


def _lookup(path: Path, key: str) -> dict[str, Any] | None:
    """The first cache record with `key` in `path`, or None.

    A line that is not a record, or the record found without its reply, is an error
    that names the file and the line.
    """
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as fh:
        for number, line in enumerate(fh, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}, line {number}: not valid JSON") from exc
            if not isinstance(record, dict):
                raise ValueError(f"{path}, line {number}: not a cache record")
            if record.get("key") == key:
                if not all(isinstance(record.get(f), str) for f in _ANSWER_FIELDS):
                    raise ValueError(f"{path}, line {number}: cache record without its reply")
                return record
    return None


def _echo(model: ModelSpec, request: LLMRequest) -> str:
    """Built-in provider: returns the prompt unchanged. For the skeleton, tests, debugging."""
    return request.prompt


register_provider("echo", _echo)

# Imported here, after the names it needs exist; the provider is registered on import.
from omissis.backends.groq import groq_provider  # noqa: E402

register_provider("groq", groq_provider)

from omissis.backends.local import local_provider  # noqa: E402

register_provider("local", local_provider)
