"""Provider `groq` and its request rules. The HTTP call is always mocked."""

import http.client
import io
import json
import urllib.error

import pytest
import yaml

from omissis import backends, pipeline
from omissis.backends import LLMRequest, cache_key, complete, groq
from omissis.config import ROLES, ConfigError, ModelSpec, RunConfig

MODEL = ModelSpec("cloud", "groq", "openai/gpt-oss-120b", "2026-11-16")
REQUEST = LLMRequest("cloud", "Riassumi [PERSONA_1_F].", "Breve.", {"max_tokens": 300, "seed": 7})


def reply(text="Fatto.", finish="stop"):
    return {
        "choices": [{"message": {"role": "assistant", "content": text}, "finish_reason": finish}]
    }


@pytest.fixture
def posted(monkeypatch):
    """Replace the HTTP call: record the bodies, answer with the queued replies."""
    state = {"bodies": [], "keys": [], "replies": [reply()]}

    def fake_post(body, keys):
        state["bodies"].append(body)
        state["keys"].append(keys)
        return state["replies"].pop(0)

    monkeypatch.setattr(groq, "_post", fake_post)
    for name in groq.KEY_VARIABLES:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setattr(groq, "_next_key", 0)
    return state


def make_config(tmp_path):
    models = {r: {"provider": "groq", "id": f"{r}-model", "revision": "r1"} for r in ROLES}
    path = tmp_path / "models.yaml"
    path.write_text(yaml.safe_dump(models), encoding="utf-8")
    return RunConfig("NONE", "R1", False, "cloud", 1, 0.9, ["D0"], path, tmp_path / "cache")


# --- the provider ------------------------------------------------------------------


def test_groq_is_registered_on_import():
    assert backends._PROVIDERS["groq"] is groq.groq_provider


def test_request_is_built_from_the_llm_request_and_the_text_returned(posted):
    assert groq.groq_provider(MODEL, REQUEST) == "Fatto."
    assert posted["keys"] == [["test-key"]]
    assert posted["bodies"] == [
        {
            "model": "openai/gpt-oss-120b",
            "messages": [
                {"role": "system", "content": "Breve."},
                {"role": "user", "content": "Riassumi [PERSONA_1_F]."},
            ],
            "temperature": 0,
            "max_completion_tokens": 300,
            "seed": 7,
        }
    ]


def test_no_system_message_when_the_request_has_none(posted):
    groq.groq_provider(MODEL, LLMRequest("cloud", "Ciao"))
    assert posted["bodies"][0]["messages"] == [{"role": "user", "content": "Ciao"}]
    assert posted["bodies"][0]["temperature"] == 0


def test_missing_key_is_a_clear_config_error(posted, monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY")
    monkeypatch.setenv("API_KEY", "key-of-another-service")  # not ours: never read, never sent
    with pytest.raises(ConfigError, match="GROQ_API_KEY"):
        groq.groq_provider(MODEL, REQUEST)
    assert posted["bodies"] == []  # nothing was sent
    monkeypatch.setenv("GROQ_API_KEY", "first")
    monkeypatch.setenv("GROQ_API_KEY2", "second")
    monkeypatch.setenv("GROQ_API_KEY3", "first")  # a repeated key counts once
    assert groq.groq_provider(MODEL, REQUEST) == "Fatto."
    assert posted["keys"] == [["first", "second"]]


@pytest.mark.parametrize(
    ("bad", "message"),
    [
        (reply(text="Una risposta a met", finish="length"), "cut at the token limit"),
        (reply(text=""), "is empty"),
        (reply(text="  \n"), "is empty"),
        (reply(text=None), "is empty"),
        ({"choices": []}, "no choices"),
        ({"error": {"message": "boom"}}, "no choices"),
    ],
)
def test_empty_or_cut_reply_raises_and_is_not_cached(posted, tmp_path, bad, message):
    posted["replies"] = [bad]
    config = make_config(tmp_path)
    with pytest.raises(RuntimeError, match=message) as caught:
        complete(REQUEST, config)
    assert isinstance(caught.value, backends.TruncatedReplyError) == ("cut" in message)
    assert not (tmp_path / "cache").exists()


def test_a_real_reply_lands_in_the_cache(posted, tmp_path):
    config = make_config(tmp_path)
    first = complete(REQUEST, config)
    second = complete(REQUEST, config)
    assert (first.text, first.cached, second.cached) == ("Fatto.", False, True)
    assert len(posted["bodies"]) == 1
    assert "test-key" not in (tmp_path / "cache" / "cloud.jsonl").read_text(encoding="utf-8")


# --- HTTP ----------------------------------------------------------------------------


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def http_error(code, headers=None):
    return urllib.error.HTTPError(groq.URL, code, "error", headers or {}, io.BytesIO(b"segreto"))


def test_rate_limit_waits_for_the_time_asked_then_tries_again(monkeypatch):
    answers = [http_error(429, {"retry-after": "2.5"}), http_error(429), reply("Dopo.")]
    waits, requests = [], []

    def fake_urlopen(request, timeout):
        requests.append(request)
        answer = answers.pop(0)
        if isinstance(answer, Exception):
            raise answer
        return FakeResponse(json.dumps(answer).encode("utf-8"))

    monkeypatch.setattr(groq.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(groq.time, "sleep", waits.append)
    monkeypatch.setattr(groq, "_next_key", 0)
    assert groq._post({"model": "m"}, ["test-key"]) == reply("Dopo.")
    assert waits == [2.5, groq.DEFAULT_WAIT_SECONDS]
    assert requests[0].get_header("Authorization") == "Bearer test-key"
    assert json.loads(requests[0].data) == {"model": "m"}


def test_rate_limit_gives_up_after_the_last_attempt(monkeypatch):
    calls = []

    def fake_urlopen(request, timeout):
        calls.append(1)
        raise http_error(429, {"retry-after": "1"})

    monkeypatch.setattr(groq.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(groq.time, "sleep", lambda seconds: None)
    with pytest.raises(RuntimeError, match="HTTP 429"):
        groq._post({"model": "m"}, ["test-key"])
    assert len(calls) == groq.MAX_ATTEMPTS


def test_service_briefly_down_is_tried_again(monkeypatch):
    answers = [http_error(503), reply("Dopo.")]
    waits = []

    def fake_urlopen(request, timeout):
        answer = answers.pop(0)
        if isinstance(answer, Exception):
            raise answer
        return FakeResponse(json.dumps(answer).encode("utf-8"))

    monkeypatch.setattr(groq.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(groq.time, "sleep", waits.append)
    assert groq._post({"model": "m"}, ["test-key"]) == reply("Dopo.")
    assert waits == [groq.DEFAULT_WAIT_SECONDS]


def test_rate_limited_key_is_left_for_the_next_one_before_any_wait(monkeypatch):
    used, waits = [], []

    def fake_urlopen(request, timeout):
        key = request.get_header("Authorization").removeprefix("Bearer ")
        used.append(key)
        if key != "c":
            raise http_error(429, {"retry-after": "30"})
        return FakeResponse(json.dumps(reply("Con la terza.")).encode("utf-8"))

    monkeypatch.setattr(groq.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(groq.time, "sleep", waits.append)
    monkeypatch.setattr(groq, "_next_key", 0)
    assert groq._post({"model": "m"}, ["a", "b", "c"]) == reply("Con la terza.")
    assert used == ["a", "b", "c"] and waits == []
    # The next call starts from the key that worked.
    assert groq._post({"model": "m"}, ["a", "b", "c"]) == reply("Con la terza.")
    assert used == ["a", "b", "c", "c"]


def test_all_keys_rate_limited_waits_once_then_goes_round_again(monkeypatch):
    used, waits = [], []

    def fake_urlopen(request, timeout):
        used.append(request.get_header("Authorization").removeprefix("Bearer "))
        if len(used) <= 2:
            raise http_error(429, {"retry-after": "4"})
        return FakeResponse(json.dumps(reply("Dopo l'attesa.")).encode("utf-8"))

    monkeypatch.setattr(groq.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(groq.time, "sleep", waits.append)
    monkeypatch.setattr(groq, "_next_key", 0)
    assert groq._post({"model": "m"}, ["a", "b"]) == reply("Dopo l'attesa.")
    assert used == ["a", "b", "a"] and waits == [4.0]


def test_daily_limit_stops_at_once_instead_of_sleeping_for_hours(monkeypatch):
    waits = []

    def fake_urlopen(request, timeout):
        raise http_error(429, {"retry-after": "5400"})

    monkeypatch.setattr(groq.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(groq.time, "sleep", waits.append)
    monkeypatch.setattr(groq, "_next_key", 0)
    with pytest.raises(RuntimeError, match="wait 5400 s"):
        groq._post({"model": "m"}, ["a", "b"])
    assert waits == []


def test_no_answer_is_tried_again_then_reported(monkeypatch):
    answers = [TimeoutError("timed out"), reply("Dopo.")]
    waits = []

    def fake_urlopen(request, timeout):
        answer = answers.pop(0) if answers else TimeoutError("timed out")
        if isinstance(answer, Exception):
            raise answer
        return FakeResponse(json.dumps(answer).encode("utf-8"))

    monkeypatch.setattr(groq.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(groq.time, "sleep", waits.append)
    monkeypatch.setattr(groq, "_next_key", 0)
    assert groq._post({"model": "m"}, ["test-key"]) == reply("Dopo.")
    assert waits == [groq.DEFAULT_WAIT_SECONDS]
    with pytest.raises(RuntimeError, match="did not answer \\(TimeoutError\\)"):
        groq._post({"model": "m"}, ["test-key"])


def test_other_http_error_raises_with_the_status_only(monkeypatch):
    def fake_urlopen(request, timeout):
        raise http_error(401)

    monkeypatch.setattr(groq.urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(RuntimeError) as caught:
        groq._post({"model": "m"}, ["test-key"])
    assert str(caught.value) == "Groq API answered HTTP 401"
    assert "test-key" not in str(caught.value) and "segreto" not in str(caught.value)


# --- request rules -------------------------------------------------------------------


def test_temperature_0_is_always_part_of_the_params():
    assert dict(LLMRequest("cloud", "x").params) == {"temperature": 0}
    assert dict(LLMRequest("cloud", "x", params={"seed": 3}).params) == {
        "temperature": 0,
        "seed": 3,
    }
    assert dict(LLMRequest("cloud", "x", params={"temperature": 0.7}).params) == {
        "temperature": 0.7
    }


def test_integral_floats_give_the_same_cache_key():
    a = LLMRequest("cloud", "x", params={"temperature": 0, "max_tokens": 300})
    b = LLMRequest("cloud", "x", params={"temperature": 0.0, "max_tokens": 300.0})
    assert dict(b.params) == {"temperature": 0, "max_tokens": 300}
    assert cache_key(MODEL, a) == cache_key(MODEL, b)
    assert cache_key(MODEL, a) != cache_key(
        MODEL, LLMRequest("cloud", "x", params={"max_tokens": 301})
    )


def test_pipeline_sets_max_tokens_in_the_request(posted, tmp_path):
    pipeline.protect_send_restore("Buongiorno.", "Rispondi.", make_config(tmp_path))
    assert posted["bodies"][0]["max_completion_tokens"] == pipeline.MAX_TOKENS
    assert posted["bodies"][0]["messages"][0]["content"] == pipeline.KEEP_PLACEHOLDERS_INSTRUCTION


def test_cache_writer_repairs_a_file_without_a_final_newline(posted, tmp_path):
    config = make_config(tmp_path)
    complete(REQUEST, config)
    path = tmp_path / "cache" / "cloud.jsonl"
    path.write_bytes(path.read_bytes().rstrip(b"\n"))
    posted["replies"] = [reply("Seconda.")]
    complete(LLMRequest("cloud", "Un'altra domanda"), config)
    lines = path.read_text(encoding="utf-8").splitlines()
    assert [json.loads(line)["response"] for line in lines] == ["Fatto.", "Seconda."]
    assert complete(REQUEST, config).cached


# --- more than one key, and answers that cannot be read ------------------------------


@pytest.mark.parametrize(
    ("keys", "used_after"),
    [
        (["minute", "day"], ["minute", "day", "minute"]),
        (["day", "minute"], ["day", "minute", "day", "minute"]),
    ],
)
def test_a_key_at_its_daily_limit_does_not_stop_the_key_that_asks_a_short_wait(
    monkeypatch, keys, used_after
):
    used, waits = [], []

    def fake_urlopen(request, timeout):
        key = request.get_header("Authorization").removeprefix("Bearer ")
        used.append(key)
        if key == "minute" and waits:  # after the short wait this key has room again
            return FakeResponse(json.dumps(reply("Dopo due secondi.")).encode("utf-8"))
        raise http_error(429, {"retry-after": "2" if key == "minute" else "5400"})

    monkeypatch.setattr(groq.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(groq.time, "sleep", waits.append)
    monkeypatch.setattr(groq, "_next_key", 0)
    assert groq._post({"model": "m"}, keys) == reply("Dopo due secondi.")
    assert used == used_after and waits == [2.0]


def test_rate_limit_on_the_last_attempt_still_tries_the_other_keys(monkeypatch):
    used = []

    def fake_urlopen(request, timeout):
        key = request.get_header("Authorization").removeprefix("Bearer ")
        used.append(key)
        if len(used) < groq.MAX_ATTEMPTS:
            raise http_error(503)
        if key == "a":
            raise http_error(429, {"retry-after": "1"})
        return FakeResponse(json.dumps(reply("Con la seconda.")).encode("utf-8"))

    monkeypatch.setattr(groq.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(groq.time, "sleep", lambda seconds: None)
    monkeypatch.setattr(groq, "_next_key", 0)
    assert groq._post({"model": "m"}, ["a", "b"]) == reply("Con la seconda.")
    assert used[-2:] == ["a", "b"]


@pytest.mark.parametrize(
    "failure",
    [
        http.client.IncompleteRead(b"met", 900),  # the connection dropped in the body
        http.client.BadStatusLine("x"),
        b"<html>Bad gateway</html>",  # an answer that is not JSON
    ],
)
def test_cut_or_unreadable_answer_is_tried_again_then_reported(monkeypatch, failure):
    answers = [failure, reply("Dopo.")]
    waits = []

    def fake_urlopen(request, timeout):
        answer = answers.pop(0) if answers else failure
        if isinstance(answer, Exception):
            raise answer
        body = answer if isinstance(answer, bytes) else json.dumps(answer).encode("utf-8")
        return FakeResponse(body)

    monkeypatch.setattr(groq.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(groq.time, "sleep", waits.append)
    monkeypatch.setattr(groq, "_next_key", 0)
    assert groq._post({"model": "m"}, ["test-key"]) == reply("Dopo.")
    assert waits == [groq.DEFAULT_WAIT_SECONDS]
    with pytest.raises(RuntimeError, match="did not answer"):
        groq._post({"model": "m"}, ["test-key"])


def test_params_cannot_replace_the_pinned_model_or_the_prompt(posted):
    request = LLMRequest("cloud", "Testo.", params={"model": "another/model", "messages": []})
    groq.groq_provider(MODEL, request)
    assert posted["bodies"][0]["model"] == MODEL.id
    assert posted["bodies"][0]["messages"] == [{"role": "user", "content": "Testo."}]
