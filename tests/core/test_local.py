"""Provider `local`: a model served on this machine. The HTTP call is always mocked."""

import io
import json
import urllib.error

import pytest

from omissis import backends
from omissis.backends import LLMRequest, TruncatedReplyError, local
from omissis.config import ConfigError, ModelSpec

MODEL = ModelSpec("d3", "local", "gpt-oss:20b", "2026-11-18")
PARAMS = {"temperature": 0, "seed": 7, "max_tokens": 4096, "reasoning_effort": "low"}
REQUEST = LLMRequest("d3", "Sono Ada Neri di Nola.", "Rispondi in JSON.", PARAMS)


def reply(text="[]", finish="stop"):
    return {
        "choices": [{"message": {"role": "assistant", "content": text}, "finish_reason": finish}]
    }


def http_error(code, body=b"{}"):
    return urllib.error.HTTPError("http://localhost", code, "error", None, io.BytesIO(body))


@pytest.fixture
def opened(monkeypatch):
    """Replace the HTTP call: record the requests, answer with the queued replies."""
    state = {"requests": [], "replies": [reply()]}

    def fake_urlopen(request, timeout=None):
        state["requests"].append(request)
        answer = state["replies"].pop(0)
        if isinstance(answer, Exception):
            raise answer
        data = answer if isinstance(answer, bytes) else json.dumps(answer).encode("utf-8")
        return io.BytesIO(data)

    monkeypatch.setattr(local.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.delenv(local.URL_VARIABLE, raising=False)
    return state


def test_local_is_registered_on_import():
    assert backends._PROVIDERS["local"] is local.local_provider


def test_request_goes_to_this_machine_with_the_pinned_model_and_no_key(opened):
    assert local.local_provider(MODEL, REQUEST) == "[]"
    (request,) = opened["requests"]
    assert request.full_url == "http://localhost:11434/v1/chat/completions"
    assert request.get_header("Authorization") is None
    body = json.loads(request.data.decode("utf-8"))
    assert body == PARAMS | {
        "model": "gpt-oss:20b",
        "messages": [
            {"role": "system", "content": "Rispondi in JSON."},
            {"role": "user", "content": "Sono Ada Neri di Nola."},
        ],
    }


def test_params_cannot_replace_the_pinned_model_or_the_prompt(opened):
    request = LLMRequest("d3", "testo", None, {"model": "altro", "messages": []})
    local.local_provider(MODEL, request)
    body = json.loads(opened["requests"][0].data.decode("utf-8"))
    assert body["model"] == "gpt-oss:20b"
    assert body["messages"] == [{"role": "user", "content": "testo"}]


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com/v1/chat/completions",
        "https://api.groq.com/openai/v1/chat/completions",
        "http://localhost.example.com:11434/v1/chat/completions",
        "http://192.168.1.10:11434/v1/chat/completions",
        "ftp://localhost/v1/chat/completions",
        "localhost:11434",
    ],
)
def test_address_that_is_not_this_machine_is_refused_before_any_call(opened, monkeypatch, url):
    # What D3 reads is the original text: this provider must never send it elsewhere.
    monkeypatch.setenv(local.URL_VARIABLE, url)
    with pytest.raises(ConfigError, match="this machine"):
        local.local_provider(MODEL, REQUEST)
    assert opened["requests"] == []


@pytest.mark.parametrize(
    "url",
    ["http://127.0.0.1:8080/v1/chat/completions", "http://[::1]:1234/v1/chat/completions"],
)
def test_another_port_of_this_machine_is_accepted(opened, monkeypatch, url):
    monkeypatch.setenv(local.URL_VARIABLE, url)
    assert local.local_provider(MODEL, REQUEST) == "[]"
    assert opened["requests"][0].full_url == url


def test_server_that_does_not_answer_is_a_config_error(opened):
    # Not "no spans": D3 and D4 must stop, or the text would go on without them.
    opened["replies"] = [urllib.error.URLError(ConnectionRefusedError(61, "refused"))]
    with pytest.raises(ConfigError, match="ollama serve"):
        local.local_provider(MODEL, REQUEST)


def test_model_that_is_not_on_the_server_is_a_config_error(opened):
    opened["replies"] = [http_error(404)]
    with pytest.raises(ConfigError, match=r"gpt-oss:20b"):
        local.local_provider(MODEL, REQUEST)


def test_other_http_error_raises_with_the_status_only(opened):
    opened["replies"] = [http_error(500, b'{"error": "Sono Ada Neri di Nola."}')]
    with pytest.raises(RuntimeError, match="HTTP 500") as caught:
        local.local_provider(MODEL, REQUEST)
    assert "Ada Neri" not in str(caught.value)


def test_reply_cut_at_the_token_limit_and_empty_reply_are_errors(opened):
    opened["replies"] = [reply("[", finish="length"), reply("  "), b"not json", {"choices": []}]
    with pytest.raises(TruncatedReplyError):
        local.local_provider(MODEL, REQUEST)
    for _ in range(3):
        with pytest.raises(RuntimeError):
            local.local_provider(MODEL, REQUEST)
