import dataclasses

import pytest

from omissis import backends
from omissis.backends import LLMRequest, LLMResponse, cache_key, register_provider
from omissis.config import ModelSpec

MODEL = ModelSpec("cloud", "some-provider", "model-a", "rev-1")
REQUEST = LLMRequest(role="cloud", prompt="Riassumi: [PERSONA_1_M] chiede…", system="Sii breve.")


@pytest.fixture
def registry(monkeypatch):
    """An empty, private provider registry for each test."""
    fresh = {}
    monkeypatch.setattr(backends, "_PROVIDERS", fresh)
    return fresh


def test_request_defaults_to_temperature_zero():
    assert dict(LLMRequest(role="cloud", prompt="x").params) == {"temperature": 0}


def test_request_default_params_are_not_shared():
    a, b = LLMRequest(role="cloud", prompt="x"), LLMRequest(role="cloud", prompt="y")
    assert a.params is not b.params


def test_request_params_are_read_only_copies():
    params = {"temperature": 0, "max_tokens": 50}
    request = LLMRequest(role="cloud", prompt="x", params=params)
    params["temperature"] = 1
    assert request.params["temperature"] == 0
    with pytest.raises(TypeError):
        request.params["temperature"] = 1


def test_request_and_response_are_frozen():
    with pytest.raises(dataclasses.FrozenInstanceError):
        REQUEST.prompt = "other"
    response = LLMResponse(text="ok", model_id="model-a", revision="rev-1", cached=False)
    with pytest.raises(dataclasses.FrozenInstanceError):
        response.cached = True


def test_cache_key_is_sha256_hex_and_deterministic():
    key = cache_key(MODEL, REQUEST)
    assert len(key) == 64 and int(key, 16) >= 0
    same = LLMRequest(role="cloud", prompt=REQUEST.prompt, system=REQUEST.system)
    assert cache_key(MODEL, same) == key


def test_cache_key_ignores_param_order():
    a = LLMRequest(role="cloud", prompt="x", params={"temperature": 0, "max_tokens": 5})
    b = LLMRequest(role="cloud", prompt="x", params={"max_tokens": 5, "temperature": 0})
    assert cache_key(MODEL, a) == cache_key(MODEL, b)


@pytest.mark.parametrize(
    ("model", "request_"),
    [
        (dataclasses.replace(MODEL, id="model-b"), REQUEST),
        (dataclasses.replace(MODEL, revision="rev-2"), REQUEST),
        (MODEL, dataclasses.replace(REQUEST, system=None)),
        (MODEL, dataclasses.replace(REQUEST, system="Sii lungo.")),
        (MODEL, dataclasses.replace(REQUEST, prompt=REQUEST.prompt + " ")),
        (MODEL, dataclasses.replace(REQUEST, params={"temperature": 0.1})),
        (MODEL, dataclasses.replace(REQUEST, params={"temperature": 0, "max_tokens": 9})),
    ],
)
def test_cache_key_changes_with_each_input(model, request_):
    assert cache_key(model, request_) != cache_key(MODEL, REQUEST)


def test_register_provider(registry):
    def provider(model, request):
        return request.prompt

    register_provider("fake", provider)
    assert registry["fake"] is provider


def test_register_provider_twice_is_an_error(registry):
    register_provider("fake", lambda model, request: "a")
    with pytest.raises(ValueError):
        register_provider("fake", lambda model, request: "b")
