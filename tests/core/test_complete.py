"""`backends.complete`: JSONL cache, replay, echo (block 1). No test needs the network."""

import json
from datetime import datetime
from pathlib import Path

import pytest
import yaml

from omissis import backends
from omissis.backends import CacheMissError, LLMRequest, cache_key, complete
from omissis.config import ROLES, ConfigError, ModelSpec, RunConfig, load_config, load_models

REPO = Path(__file__).resolve().parents[2]


def write_models(path, provider="fake", unpinned=()):
    data = {
        role: {
            "provider": provider,
            "id": "TO_BE_PINNED" if role in unpinned else f"{role}-model",
            "revision": "r1",
        }
        for role in ROLES
    }
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


def make_config(tmp_path, backend="cloud", **models_kw):
    return RunConfig(
        detector="D0",
        strategy="R1",
        mask_quasi=False,
        backend=backend,
        seed=1,
        fuzzy_threshold=0.9,
        source_priority=["D0"],
        models_file=write_models(tmp_path / "models.yaml", **models_kw),
        cache_dir=tmp_path / "cache",
    )


@pytest.fixture
def calls(monkeypatch):
    """A fresh registry with a fake provider that records every call."""
    log = []

    def fake(model, request):
        log.append((model.id, request.prompt))
        return f"risposta a: {request.prompt}"

    monkeypatch.setattr(backends, "_PROVIDERS", {"fake": fake})
    return log


REQUEST = LLMRequest(role="cloud", prompt="Riassumi [PERSONA_1_F] è qui", system="Breve.")


def test_miss_calls_provider_once_then_hit_from_cache(tmp_path, calls):
    config = make_config(tmp_path)
    first = complete(REQUEST, config)
    second = complete(REQUEST, config)
    assert calls == [("cloud-model", REQUEST.prompt)]
    assert first.text == second.text == f"risposta a: {REQUEST.prompt}"
    assert (first.cached, second.cached) == (False, True)
    assert (second.model_id, second.revision) == ("cloud-model", "r1")


def test_cache_record_format(tmp_path, calls):
    config = make_config(tmp_path)
    complete(REQUEST, config)
    lines = (tmp_path / "cache" / "cloud.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert "è" in lines[0]  # ensure_ascii=False
    record = json.loads(lines[0])
    assert set(record) == {
        "key",
        "role",
        "model_id",
        "revision",
        "system",
        "prompt",
        "params",
        "response",
        "created_at",
    }
    model = load_models(config.models_file)["cloud"]
    assert record["key"] == cache_key(model, REQUEST)
    assert record["params"] == {"temperature": 0}
    assert datetime.fromisoformat(record["created_at"]).utcoffset().total_seconds() == 0


def test_different_request_is_a_new_miss(tmp_path, calls):
    config = make_config(tmp_path)
    complete(REQUEST, config)
    complete(LLMRequest(role="cloud", prompt="altro"), config)
    complete(LLMRequest(role="judge", prompt="altro"), config)
    assert len(calls) == 3
    assert (tmp_path / "cache" / "judge.jsonl").exists()


def test_replay_miss_raises_and_does_not_call_provider(tmp_path, calls):
    config = make_config(tmp_path, backend="replay")
    with pytest.raises(CacheMissError):
        complete(REQUEST, config)
    assert calls == []
    assert issubclass(CacheMissError, RuntimeError)


def test_replay_serves_what_cloud_cached(tmp_path, calls):
    complete(REQUEST, make_config(tmp_path))
    replayed = complete(REQUEST, make_config(tmp_path, backend="replay"))
    assert replayed.cached and len(calls) == 1


def test_unpinned_role_is_refused(tmp_path, calls):
    config = make_config(tmp_path, unpinned=("cloud",))
    with pytest.raises(ConfigError, match="not pinned"):
        complete(REQUEST, config)
    assert calls == []


def test_unknown_provider_is_an_error(tmp_path, calls):
    with pytest.raises(ConfigError, match="no provider registered"):
        complete(REQUEST, make_config(tmp_path, provider="nobody"))


def test_provider_must_return_text(tmp_path, monkeypatch):
    monkeypatch.setattr(backends, "_PROVIDERS", {"fake": lambda model, request: None})
    with pytest.raises(TypeError):
        complete(REQUEST, make_config(tmp_path))
    assert not (tmp_path / "cache" / "cloud.jsonl").exists()


def test_corrupt_cache_line_is_reported(tmp_path, calls):
    config = make_config(tmp_path)
    (tmp_path / "cache").mkdir()
    (tmp_path / "cache" / "cloud.jsonl").write_text("{not json\n", encoding="utf-8")
    with pytest.raises(ValueError, match="line 1"):
        complete(REQUEST, config)


def test_echo_is_built_in_and_returns_the_prompt(tmp_path):
    assert "echo" in backends._PROVIDERS
    config = make_config(tmp_path, provider="echo")
    response = complete(REQUEST, config)
    assert response.text == REQUEST.prompt and not response.cached


def test_echo_models_file_pins_every_role():
    models = load_models(REPO / "configs" / "models.echo.yaml")
    assert set(models) == set(ROLES)
    assert all(m == ModelSpec(m.role, "echo", "echo", "1") and m.pinned for m in models.values())


def test_skeleton_config():
    config = load_config(REPO / "configs" / "skeleton.yaml")
    assert (config.detector, config.strategy, config.backend) == ("D0", "R1", "cloud")
    assert config.models_file == Path("configs/models.echo.yaml")


@pytest.mark.parametrize("line", ["null", "[]", "42", '"testo"'])
def test_cache_line_that_is_not_a_record_is_reported_with_its_place(tmp_path, calls, line):
    config = make_config(tmp_path)
    path = tmp_path / "cache" / "cloud.jsonl"
    path.parent.mkdir()
    path.write_text(line + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match=r"cloud\.jsonl, line 1"):
        complete(REQUEST, config)
    assert calls == []


def test_cache_record_without_its_reply_is_reported_with_its_place(tmp_path, calls):
    config = make_config(tmp_path)
    key = cache_key(load_models(config.models_file)["cloud"], REQUEST)
    path = tmp_path / "cache" / "cloud.jsonl"
    path.parent.mkdir()
    path.write_text(json.dumps({"key": key, "model_id": "cloud-model"}) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match=r"cloud\.jsonl, line 1"):
        complete(REQUEST, config)
    assert calls == []
