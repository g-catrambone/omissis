"""Gold spans, the detectors GOLD and NONE, named configurations, `omissis mask` (task 2.2)."""

import json
from pathlib import Path

import pytest
import yaml

from omissis import backends, cli, pipeline
from omissis.config import (
    ROLES,
    ConfigError,
    load_config,
    load_eval_configs,
    run_id,
    with_overrides,
)
from omissis.contracts import Span, SpanClass, SpanType
from omissis.eval.datasets import load_texts

REPO = Path(__file__).resolve().parents[2]
FIXTURE_DIR = REPO / "data" / "fixtures"
FIXTURES = load_texts(FIXTURE_DIR)
TASK = "Scrivi una bozza di risposta a questa email."
EVAL = REPO / "configs" / "eval.yaml"


@pytest.fixture
def sent(monkeypatch, tmp_path):
    """Every role pinned to a fake provider that records the prompts and echoes them."""
    prompts = []

    def fake(model, request):
        prompts.append(request.prompt)
        return request.prompt

    monkeypatch.setattr(backends, "_PROVIDERS", {"fake": fake})
    models = {r: {"provider": "fake", "id": "fake", "revision": "1"} for r in ROLES}
    path = tmp_path / "models.yaml"
    path.write_text(yaml.safe_dump(models), encoding="utf-8")
    return prompts, {"models_file": str(path), "cache_dir": str(tmp_path / "cache")}


@pytest.fixture
def configs(sent):
    return load_eval_configs(EVAL, sent[1])


# --- configuration -----------------------------------------------------------------


def test_eval_file_names_the_three_references_in_order(configs):
    assert list(configs) == ["REF-none", "REF-oracle-direct", "REF-oracle"]
    assert [(c.detector, c.mask_quasi) for c in configs.values()] == [
        ("NONE", False),
        ("GOLD", False),
        ("GOLD", True),
    ]
    assert all(c.seed == 20261111 and c.backend == "cloud" for c in configs.values())


def test_overrides_apply_to_every_configuration():
    configs = load_eval_configs(EVAL, {"backend": "replay"})
    assert {c.backend for c in configs.values()} == {"replay"}
    assert {str(c.models_file) for c in configs.values()} == {"configs/models.yaml"}


def test_configurations_that_differ_only_in_detector_have_different_run_ids(configs):
    gold = configs["REF-oracle-direct"]
    ids = {run_id(with_overrides(gold, detector=d)) for d in ("GOLD", "NONE", "D0", "D4")}
    assert len(ids) == 4
    assert len({run_id(c) for c in configs.values()}) == 3


@pytest.mark.parametrize("changes", [{"strategy": "R2"}, {"mask_quasi": True}])
def test_detector_none_has_one_spelling(configs, changes):
    with pytest.raises(ConfigError, match="NONE"):
        with_overrides(configs["REF-none"], **changes)


def test_unknown_detector_is_refused(configs):
    with pytest.raises(ConfigError):
        with_overrides(configs["REF-none"], detector="ORACLE")


BASE = yaml.safe_load(EVAL.read_text(encoding="utf-8"))["base"]
REF = {"name": "A", "detector": "GOLD", "strategy": "R1", "mask_quasi": True}


@pytest.mark.parametrize(
    "content",
    [
        yaml.safe_dump({"base": BASE, "configurations": [REF, REF]}),  # a name twice
        yaml.safe_dump({"base": BASE, "configurations": [{**REF, "colour": "red"}]}),
        yaml.safe_dump({"base": BASE, "configurations": [{k: REF[k] for k in REF if k != "name"}]}),
        yaml.safe_dump({"base": BASE, "configurations": []}),
        yaml.safe_dump({"base": BASE, "configurations": [REF], "extra": 1}),
        yaml.safe_dump({"configurations": [REF]}),
        "base: [unclosed",  # not YAML
    ],
)
def test_bad_eval_file_is_a_config_error(tmp_path, content):
    path = tmp_path / "eval.yaml"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ConfigError):
        load_eval_configs(path)


def test_yaml_syntax_error_in_a_run_configuration_is_a_config_error(tmp_path):
    path = tmp_path / "run.yaml"
    path.write_text("detector: [D0", encoding="utf-8")
    with pytest.raises(ConfigError, match="not valid YAML"):
        load_config(path)


# --- mask and protect_send_restore ---------------------------------------------------


@pytest.mark.parametrize("record", FIXTURES, ids=[r.id for r in FIXTURES])
def test_gold_with_mask_quasi_sends_no_gold_span_text(record, configs, sent):
    result = pipeline.protect_send_restore(record.text, TASK, configs["REF-oracle"], record.spans)
    (prompt,) = sent[0]
    assert prompt == f"{TASK}\n\n{result.masked_text}"
    assert all(span.text not in prompt for span in record.spans)
    assert result.restored_reply == f"{TASK}\n\n{record.text}"
    assert result.fully_restored
    assert {item.source for item in result.disclosure} == {"GOLD"}


@pytest.mark.parametrize("record", FIXTURES, ids=[r.id for r in FIXTURES])
def test_gold_without_mask_quasi_sends_the_quasi_identifiers_only(record, configs, sent):
    config = configs["REF-oracle-direct"]
    pipeline.protect_send_restore(record.text, TASK, config, record.spans)
    (prompt,) = sent[0]
    for span in record.spans:
        assert (span.text in prompt) == (span.cls is SpanClass.QUASI), span


def test_mask_result_with_gold_holds_every_span_and_only_masked_entities(configs):
    record = FIXTURES[0]
    result, vault = pipeline.mask(record.text, configs["REF-oracle-direct"], record.spans)
    assert result.spans == record.spans
    assert all(e.cls is not SpanClass.QUASI for e in result.entities)
    assert len(result.disclosure) == len(result.entities) == len(vault)


def test_detector_none_sends_the_text_unchanged(configs, sent):
    record = FIXTURES[0]
    result = pipeline.protect_send_restore(record.text, TASK, configs["REF-none"])
    assert sent[0] == [f"{TASK}\n\n{record.text}"]
    assert result.masked_text == record.text
    assert result.disclosure == () and result.restore_events == ()
    masked, vault = pipeline.mask(record.text, configs["REF-none"])
    assert (masked.masked_text, masked.spans, masked.entities) == (record.text, (), ())
    assert len(vault) == 0


def test_wrong_combinations_of_detector_and_gold_spans_raise(configs):
    record = FIXTURES[0]
    d0 = with_overrides(configs["REF-oracle"], detector="D0")
    with pytest.raises(ValueError, match="requires gold_spans"):
        pipeline.mask(record.text, configs["REF-oracle"])
    with pytest.raises(ValueError, match="only allowed with detector GOLD"):
        pipeline.mask(record.text, d0, record.spans)
    with pytest.raises(ValueError, match="only allowed with detector GOLD"):
        pipeline.mask(record.text, configs["REF-none"], record.spans)
    with pytest.raises(ValueError, match="requires gold_spans"):
        pipeline.protect_send_restore(record.text, TASK, configs["REF-oracle"])
    with pytest.raises(ValueError, match="does not match"):
        pipeline.mask("un altro testo " * 100, configs["REF-oracle"], record.spans)


def test_gold_with_an_empty_list_masks_nothing(configs):
    result, vault = pipeline.mask("Buongiorno.", configs["REF-oracle"], [])
    assert result.masked_text == "Buongiorno." and len(vault) == 0


def test_reason_that_quotes_a_masked_value_is_rewritten_or_dropped(configs, monkeypatch):
    text = "Lavoro a Nola come magazziniere dopo l'ernia."

    def span(value, type, reason):
        start = text.index(value)
        return Span(start, start + len(value), value, type, 0.8, "D3", reason)

    found = [
        span("Nola", SpanType.CITTA, "Nola è il luogo di lavoro"),
        span("magazziniere", SpanType.RUOLO, "mestiere di chi scrive"),
        span("ernia", SpanType.SALUTE, "ERNIA: una diagnosi"),
    ]
    monkeypatch.setattr(pipeline, "detect", lambda text, detector, config: found)
    config = with_overrides(configs["REF-oracle"], detector="D3")
    result, _ = pipeline.mask(text, config)
    assert [item.reason for item in result.disclosure] == [
        "[CITTA_1] è il luogo di lavoro",
        "mestiere di chi scrive",
        None,  # the value is quoted in another case: dropped
    ]


def test_vault_is_erased_when_the_provider_raises(configs, monkeypatch):
    created = []

    class SpyVault(pipeline.Vault):
        def __init__(self):
            super().__init__()
            created.append(self)

    def broken(model, request):
        raise RuntimeError("the provider is down")

    monkeypatch.setattr(pipeline, "Vault", SpyVault)
    monkeypatch.setattr(backends, "_PROVIDERS", {"fake": broken})
    record = FIXTURES[0]
    with pytest.raises(RuntimeError, match="down"):
        pipeline.protect_send_restore(record.text, TASK, configs["REF-oracle"], record.spans)
    assert len(created) == 1 and len(created[0]) == 0


# --- command line --------------------------------------------------------------------


@pytest.fixture
def eval_file(sent, tmp_path):
    data = yaml.safe_load(EVAL.read_text(encoding="utf-8"))
    data["base"].update(sent[1])
    path = tmp_path / "eval.yaml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


def run_config(tmp_path, eval_file, name, **changes):
    data = yaml.safe_load(eval_file.read_text(encoding="utf-8"))
    entry = next(c for c in data["configurations"] if c["name"] == name)
    settings = {**data["base"], **{k: v for k, v in entry.items() if k != "name"}, **changes}
    path = tmp_path / f"{name}.yaml"
    path.write_text(yaml.safe_dump(settings), encoding="utf-8")
    return path


def test_mask_writes_what_protect_send_restore_sends(eval_file, tmp_path, capsys):
    out = tmp_path / "masked"
    args = ["mask", "--eval-config", str(eval_file), "--input-dir", str(FIXTURE_DIR)]
    assert cli.main([*args, "--output", str(out)]) == 0
    configs = load_eval_configs(eval_file)
    assert sorted(p.name for p in out.iterdir()) == sorted(configs)
    for name, config in configs.items():
        for record in FIXTURES:
            data = json.loads((out / name / f"{record.id}.json").read_text(encoding="utf-8"))
            gold = record.spans if config.detector == "GOLD" else None
            sent = pipeline.protect_send_restore(record.text, TASK, config, gold)
            assert data["masked_text"] == sent.masked_text
            assert (data["text_id"], data["config_name"]) == (record.id, name)
            assert data["run_id"] == sent.run_id == run_id(config)
            assert [set(d) for d in data["disclosure"]] == [
                {"surrogate", "type", "class", "source", "reason"}
            ] * len(sent.disclosure)
            assert [d["surrogate"] for d in data["disclosure"]] == [
                d.surrogate for d in sent.disclosure
            ]


def test_mask_never_calls_the_cloud_role(eval_file, tmp_path, sent):
    args = ["mask", "--eval-config", str(eval_file), "--input-dir", str(FIXTURE_DIR)]
    assert cli.main([*args, "--output", str(tmp_path / "masked"), "--names", "REF-oracle"]) == 0
    assert sent[0] == []
    assert [p.name for p in (tmp_path / "masked").iterdir()] == ["REF-oracle"]


def test_mask_with_an_unknown_name_fails_cleanly(eval_file, tmp_path, capsys):
    args = ["mask", "--eval-config", str(eval_file), "--input-dir", str(FIXTURE_DIR)]
    assert cli.main([*args, "--output", str(tmp_path / "m"), "--names", "REF-oracle,D9+R1"]) == 2
    assert "D9+R1" in capsys.readouterr().err
    assert not (tmp_path / "m").exists()


def test_run_and_batch_take_gold_spans_from_the_record(eval_file, tmp_path, capsys):
    config = str(run_config(tmp_path, eval_file, "REF-oracle"))
    record = FIXTURES[0]
    assert (
        cli.main(["run", "--config", config, "--input", str(FIXTURE_DIR / "fx-bank-01.json")]) == 0
    )
    out = capsys.readouterr().out
    assert "[PERSONA_1_F]" in out and "fully restored: True" in out
    assert cli.main(["batch", "--config", config, "--input-dir", str(FIXTURE_DIR)]) == 0
    lines = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert [line["text_id"] for line in lines] == [r.id for r in FIXTURES]
    assert all(span.text not in lines[0]["masked_text"] for span in record.spans)


def test_plain_text_with_detector_gold_fails_cleanly(eval_file, tmp_path, capsys):
    config = str(run_config(tmp_path, eval_file, "REF-oracle"))
    plain = tmp_path / "email.txt"
    plain.write_text("Buongiorno.", encoding="utf-8")
    assert cli.main(["run", "--config", config, "--input", str(plain)]) == 2
    assert "GOLD" in capsys.readouterr().err


def test_errors_exit_with_status_2(eval_file, tmp_path, capsys, monkeypatch):
    fixture = str(FIXTURE_DIR / "fx-bank-01.json")
    oracle = str(run_config(tmp_path, eval_file, "REF-oracle"))

    def not_built(*args):
        raise NotImplementedError("detector D9 is not built yet")

    with monkeypatch.context() as patch:
        patch.setattr(cli, "protect_send_restore", not_built)
        assert cli.main(["run", "--config", oracle, "--input", fixture]) == 2
    broken = tmp_path / "broken.yaml"
    broken.write_text("detector: [D0", encoding="utf-8")
    assert cli.main(["run", "--config", str(broken), "--input", fixture]) == 2
    binary = tmp_path / "email.txt"
    binary.write_bytes(b"\xff\xfe\x00caff\xe8")
    none = str(run_config(tmp_path, eval_file, "REF-none"))
    assert cli.main(["run", "--config", none, "--input", str(binary)]) == 2
    assert capsys.readouterr().err.count("omissis: error:") == 3
