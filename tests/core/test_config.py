from pathlib import Path

import pytest
import yaml

from omissis.config import (
    ROLES,
    ConfigError,
    ModelSpec,
    RunConfig,
    load_config,
    load_models,
    require_pinned,
    run_id,
    with_overrides,
)
from omissis.contracts import DetectorId, Strategy

REPO = Path(__file__).resolve().parents[2]


def pinned_models(**changes):
    models = {role: {"provider": "echo", "id": "echo", "revision": "1"} for role in ROLES}
    models.update(changes)
    return models


def write(path, data):
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


@pytest.fixture
def base(tmp_path):
    models = write(tmp_path / "models.yaml", pinned_models())
    return {
        "detector": "D0",
        "strategy": "R1",
        "mask_quasi": False,
        "backend": "replay",
        "seed": 13,
        "fuzzy_threshold": 0.9,
        "source_priority": ["D0", "D1"],
        "models_file": str(models),
        "cache_dir": str(tmp_path / "cache"),
    }


def test_load_config(tmp_path, base):
    config = load_config(write(tmp_path / "run.yaml", base))
    assert config.detector is DetectorId.D0
    assert config.strategy is Strategy.R1
    assert config.source_priority == (DetectorId.D0, DetectorId.D1)
    assert config.models_file == Path(base["models_file"])
    assert isinstance(config.fuzzy_threshold, float)


def test_example_config_loads():
    config = load_config(REPO / "configs" / "example.yaml")
    assert isinstance(config, RunConfig)


def test_load_config_overrides(tmp_path, base):
    config = load_config(write(tmp_path / "run.yaml", base), {"detector": "D4", "seed": 1})
    assert config.detector is DetectorId.D4 and config.seed == 1


def test_unknown_key_is_an_error(tmp_path, base):
    with pytest.raises(ConfigError, match="unknown"):
        load_config(write(tmp_path / "run.yaml", {**base, "detectr": "D0"}))
    with pytest.raises(ConfigError, match="unknown"):
        load_config(write(tmp_path / "run.yaml", base), {"temperature": 0})


def test_missing_key_is_an_error(tmp_path, base):
    del base["seed"]
    with pytest.raises(ConfigError, match="missing"):
        load_config(write(tmp_path / "run.yaml", base))


def test_non_mapping_file_is_an_error(tmp_path):
    with pytest.raises(ConfigError):
        load_config(write(tmp_path / "run.yaml", ["D0"]))


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("detector", "D5"),
        ("strategy", "R3"),
        ("mask_quasi", "yes"),
        ("mask_quasi", 1),
        ("backend", "local"),
        ("seed", "13"),
        ("seed", 1.5),
        ("seed", True),
        ("fuzzy_threshold", 1.5),
        ("fuzzy_threshold", -0.1),
        ("fuzzy_threshold", "0.9"),
        ("source_priority", "D0"),
        ("source_priority", ["D0", "D9"]),
        ("source_priority", ["D0", "D0"]),
        ("models_file", ""),
        ("cache_dir", None),
    ],
)
def test_invalid_values(tmp_path, base, key, value):
    with pytest.raises(ConfigError):
        load_config(write(tmp_path / "run.yaml", {**base, key: value}))


def test_with_overrides_validates(tmp_path, base):
    config = load_config(write(tmp_path / "run.yaml", base))
    changed = with_overrides(config, strategy="R2", fuzzy_threshold=1)
    assert changed.strategy is Strategy.R2 and changed.fuzzy_threshold == 1.0
    assert config.strategy is Strategy.R1
    with pytest.raises(ConfigError):
        with_overrides(config, backend="network")
    with pytest.raises(ConfigError):
        with_overrides(config, colour="blue")


# --- models ---


def test_load_models_and_pinning(tmp_path):
    path = write(
        tmp_path / "m.yaml",
        pinned_models(judge={"provider": "x", "id": "TO_BE_PINNED", "revision": "1"}),
    )
    models = load_models(path)
    assert models["cloud"] == ModelSpec("cloud", "echo", "echo", "1")
    assert models["cloud"].pinned
    assert not models["judge"].pinned
    assert require_pinned(models, "cloud") is models["cloud"]


def test_require_pinned_refuses_unpinned_and_missing(tmp_path):
    unpinned = {"provider": "TO_BE_PINNED", "id": "TO_BE_PINNED", "revision": "TO_BE_PINNED"}
    path = write(tmp_path / "m.yaml", pinned_models(**{role: unpinned for role in ROLES}))
    models = load_models(path)
    assert not any(m.pinned for m in models.values())
    with pytest.raises(ConfigError, match="not pinned"):
        require_pinned(models, "cloud")
    with pytest.raises(ConfigError):
        require_pinned(models, "summariser")


@pytest.mark.parametrize(
    "data",
    [
        {k: v for k, v in pinned_models().items() if k != "d2"},  # missing role
        pinned_models(extra={"provider": "a", "id": "b", "revision": "c"}),  # unknown role
        pinned_models(cloud={"provider": "a", "id": "b"}),  # missing field
        pinned_models(cloud={"provider": "a", "id": "b", "revision": "c", "x": 1}),
        pinned_models(cloud={"provider": "a", "id": "b", "revision": 1}),  # not a string
        pinned_models(cloud="echo"),
    ],
)
def test_invalid_models_file(tmp_path, data):
    with pytest.raises(ConfigError):
        load_models(write(tmp_path / "m.yaml", data))


# --- run_id ---


def test_run_id_is_12_hex_and_stable(tmp_path, base):
    config = load_config(write(tmp_path / "run.yaml", base))
    rid = run_id(config)
    assert len(rid) == 12 and int(rid, 16) >= 0
    assert run_id(load_config(write(tmp_path / "again.yaml", base))) == rid


def test_run_id_ignores_where_responses_come_from(tmp_path, base):
    config = load_config(write(tmp_path / "run.yaml", base))
    copy = write(tmp_path / "other_models.yaml", pinned_models())
    same = with_overrides(
        config, backend="cloud", cache_dir=tmp_path / "elsewhere", models_file=copy
    )
    assert run_id(same) == run_id(config)


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("detector", "D1"),
        ("strategy", "R2"),
        ("mask_quasi", True),
        ("seed", 14),
        ("fuzzy_threshold", 0.8),
        ("source_priority", ["D1", "D0"]),
    ],
)
def test_run_id_changes_with_evaluated_settings(tmp_path, base, key, value):
    config = load_config(write(tmp_path / "run.yaml", base))
    assert run_id(with_overrides(config, **{key: value})) != run_id(config)


def test_run_id_changes_with_models(tmp_path, base):
    config = load_config(write(tmp_path / "run.yaml", base))
    other = write(
        tmp_path / "m2.yaml",
        pinned_models(cloud={"provider": "echo", "id": "echo", "revision": "2"}),
    )
    assert run_id(with_overrides(config, models_file=other)) != run_id(config)


def test_run_id_is_the_formula_the_committed_results_were_named_with(tmp_path):
    """A change here renames every committed result: it must be a decision."""
    models = {role: {"provider": "echo", "id": f"{role}-model", "revision": "1"} for role in ROLES}
    path = write(tmp_path / "m.yaml", models)
    settings = ("GOLD", "R2", True, "cloud", 20261111, 0.9, ["D0", "D2", "D1", "D3"])
    config = RunConfig(*settings, path, tmp_path / "cache")
    assert run_id(config) == "b02f8872b48d"
    for role in ROLES:  # every pinned role is part of what a run computes
        other = {**models, role: {"provider": "echo", "id": f"{role}-model", "revision": "2"}}
        again = RunConfig(*settings, write(tmp_path / f"{role}.yaml", other), tmp_path / "cache")
        assert run_id(again) != "b02f8872b48d", role
