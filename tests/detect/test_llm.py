"""D3 local LLM, with a fake provider: no test needs a model."""

import json
import logging

import pytest
import yaml

from omissis import backends
from omissis.backends import CacheMissError
from omissis.config import ROLES, ConfigError, RunConfig
from omissis.contracts import TYPE_CLASS, DetectorId, SpanClass, SpanType
from omissis.detect import detect, llm

TEXT = "Lavoro come magazziniere a Nola. A Nola seguo un ciclo di fisioterapia."
GOOD = [
    {"text": "magazziniere", "type": "RUOLO", "reason": "mestiere di chi scrive"},
    {"text": "Nola", "type": "CITTA", "reason": "luogo di lavoro"},
    {"text": "fisioterapia", "type": "SALUTE", "reason": "terapia"},
]


def make_config(tmp_path, backend="cloud", d3_id="d3-model"):
    models = {r: {"provider": "fake", "id": f"{r}-model", "revision": "r1"} for r in ROLES}
    models["d3"]["id"] = d3_id
    path = tmp_path / "models.yaml"
    path.write_text(yaml.safe_dump(models), encoding="utf-8")
    return RunConfig(
        detector="D3",
        strategy="R1",
        mask_quasi=True,
        backend=backend,
        seed=7,
        fuzzy_threshold=0.9,
        source_priority=["D0", "D2", "D1", "D3"],
        models_file=path,
        cache_dir=tmp_path / "cache",
    )


@pytest.fixture
def provider(monkeypatch):
    """A fake provider that answers with the queued replies and records the requests."""
    state = {"replies": [], "requests": []}

    def fake(model, request):
        state["requests"].append(request)
        reply = state["replies"].pop(0)
        if isinstance(reply, Exception):
            raise reply
        return reply if isinstance(reply, str) else json.dumps(reply, ensure_ascii=False)

    monkeypatch.setattr(backends, "_PROVIDERS", {"fake": fake})
    monkeypatch.setattr(llm, "stats", type(llm.stats)())
    return state


def test_valid_json_gives_spans_located_by_search(tmp_path, provider):
    provider["replies"] = [GOOD]
    spans = detect(TEXT, DetectorId.D3, make_config(tmp_path))
    assert [(s.type, s.text, s.start) for s in spans] == [
        (SpanType.RUOLO, "magazziniere", 12),
        (SpanType.CITTA, "Nola", 27),
        (SpanType.CITTA, "Nola", 35),  # repeated text: every occurrence
        (SpanType.SALUTE, "fisioterapia", 58),
    ]
    assert all(s.source == "D3" and s.reason and s.matches(TEXT) for s in spans)
    assert all(s.confidence == llm.CONFIDENCE for s in spans)
    assert llm.stats == {"calls": 1}


def test_request_goes_to_role_d3_with_temperature_0_and_the_seed(tmp_path, provider):
    provider["replies"] = [[]]
    assert detect(TEXT, DetectorId.D3, make_config(tmp_path)) == []
    (request,) = provider["requests"]
    assert request.role == "d3"
    assert dict(request.params) == {
        "temperature": 0,
        "seed": 7,
        "max_tokens": llm.MAX_TOKENS,
        "reasoning_effort": "low",
    }
    assert request.prompt.endswith(TEXT)
    assert request.system == llm.SYSTEM


def test_prompt_asks_for_every_non_direct_type_and_for_utente_only_among_the_direct():
    for type in SpanType:
        asked = f"- {type.value}:" in llm.PROMPT
        wanted = TYPE_CLASS[type] is not SpanClass.DIRECT or type is SpanType.UTENTE
        assert asked == wanted == (type in llm.TYPES)


def test_invalid_json_is_asked_again_with_a_different_prompt(tmp_path, provider):
    provider["replies"] = ["Ecco il risultato: [", GOOD]
    spans = detect(TEXT, DetectorId.D3, make_config(tmp_path))
    assert len(spans) == 4
    first, second = provider["requests"]
    assert first.prompt != second.prompt
    assert second.prompt.startswith(first.prompt)
    assert llm.stats == {"calls": 2, "retries": 1}


def test_invalid_json_twice_logs_counts_and_returns_nothing(tmp_path, provider, caplog):
    provider["replies"] = ["non è JSON", '{"text": "Nola"}']
    with caplog.at_level(logging.ERROR):
        assert detect(TEXT, DetectorId.D3, make_config(tmp_path)) == []
    assert "two invalid replies" in caplog.text
    assert "Nola" not in caplog.text  # never log the text
    assert len(provider["requests"]) == 2
    assert llm.stats == {"calls": 2, "retries": 1, "failures": 1}


@pytest.mark.parametrize(
    "items",
    [
        {"text": "Nola", "type": "CITTA", "reason": "luogo"},  # an object, not an array
        [{"text": "Nola", "type": "CITTA"}],  # reason missing
        [{"text": "Nola", "type": "CITTA", "reason": " "}],  # empty reason
        [{"text": "", "type": "CITTA", "reason": "luogo"}],  # empty text
        [{"text": "Nola", "type": "LUOGO", "reason": "luogo"}],  # unknown type
        [{"text": "Nola", "type": "PERSONA", "reason": "nome"}],  # a direct identifier
        [{"text": "Nola", "type": "CITTA", "reason": "luogo", "start": 27}],  # an offset
        [{"text": 27, "type": "CITTA", "reason": "luogo"}],  # not a string
        ["Nola"],
    ],
)
def test_reply_that_breaks_the_schema_is_invalid(items):
    assert llm._valid(json.dumps(items)) is None


def test_fenced_json_is_invalid():
    assert llm._valid("```json\n[]\n```") is None
    assert llm._valid("[]") == []


def test_hallucinated_text_is_dropped_and_counted(tmp_path, provider):
    invented = {"text": "Pomigliano", "type": "CITTA", "reason": "luogo"}
    provider["replies"] = [[*GOOD, invented]]
    spans = detect(TEXT, DetectorId.D3, make_config(tmp_path))
    assert "Pomigliano" not in {s.text for s in spans}
    assert len(spans) == 4
    assert llm.stats == {"calls": 1, "hallucinated": 1}


def test_a_value_is_found_as_a_whole_token_only(tmp_path, provider):
    text = "Ho 34 anni, vivo a Roma in via Romagnosi 12 e pago 1.340 euro, 34,50 di spese."
    provider["replies"] = [
        [
            {"text": "34", "type": "ETA", "reason": "eta di chi scrive"},
            {"text": "Roma", "type": "CITTA", "reason": "citta"},
            {"text": "magnosi", "type": "CITTA", "reason": "parte di una parola"},
        ]
    ]
    spans = detect(text, DetectorId.D3, make_config(tmp_path))
    assert [(s.text, s.start) for s in spans] == [("34", 3), ("Roma", 19)]
    assert llm.stats == {"calls": 1, "hallucinated": 1}  # found only inside a word


def test_identical_text_is_answered_from_the_cache(tmp_path, provider):
    provider["replies"] = [GOOD]
    config = make_config(tmp_path)
    assert detect(TEXT, DetectorId.D3, config) == detect(TEXT, DetectorId.D3, config)
    assert len(provider["requests"]) == 1


def test_cache_miss_in_replay_propagates(tmp_path, provider):
    with pytest.raises(CacheMissError):
        detect(TEXT, DetectorId.D3, make_config(tmp_path, backend="replay"))


def test_model_not_pinned_propagates(tmp_path, provider):
    with pytest.raises(ConfigError):
        detect(TEXT, DetectorId.D3, make_config(tmp_path, d3_id="TO_BE_PINNED"))


def test_reply_cut_at_the_token_limit_is_an_invalid_reply(tmp_path, provider):
    provider["replies"] = [backends.TruncatedReplyError("cut"), GOOD]
    assert len(detect(TEXT, DetectorId.D3, make_config(tmp_path))) == 4
    assert llm.stats == {"calls": 2, "retries": 1}


def test_failing_provider_stops_the_run(tmp_path, provider):
    # No spans would send the text unmasked: the error of the provider propagates.
    provider["replies"] = [RuntimeError("out of memory")]
    with pytest.raises(RuntimeError, match="out of memory"):
        detect(TEXT, DetectorId.D3, make_config(tmp_path))
    assert llm.stats == {"calls": 1}
