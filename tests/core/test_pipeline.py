"""Pipeline and CLI (block 1); the resolver has its own tests. No test needs the network."""

import json
from pathlib import Path

import pytest
import yaml

from omissis import backends, cli, pipeline
from omissis.config import ROLES, load_config, with_overrides
from omissis.contracts import GOLD_SOURCE, RestoreOutcome, Span, SpanClass, SpanType
from omissis.eval.datasets import load_texts
from omissis.resolve import resolve

REPO = Path(__file__).resolve().parents[2]
FIXTURES = load_texts(REPO / "data" / "fixtures")
TASK = "Scrivi una bozza di risposta a questa email."
DETECTED_BY_D0 = {SpanType.IBAN, SpanType.CF, SpanType.PIVA, SpanType.TELEFONO, SpanType.EMAIL}


@pytest.fixture
def config(tmp_path):
    return with_overrides(load_config(REPO / "configs" / "skeleton.yaml"), cache_dir=tmp_path)


@pytest.fixture
def sent(monkeypatch, tmp_path):
    """Pin every role to a fake provider that records the prompts and echoes them."""
    prompts = []

    def fake(model, request):
        prompts.append((request.system, request.prompt))
        return request.prompt

    monkeypatch.setattr(backends, "_PROVIDERS", {"fake": fake})
    models = {r: {"provider": "fake", "id": "fake", "revision": "1"} for r in ROLES}
    path = tmp_path / "models.yaml"
    path.write_text(yaml.safe_dump(models), encoding="utf-8")
    return prompts, path


# --- resolver, order and ids --------------------------------------------------------------


def test_resolver_one_entity_per_distinct_text():
    text = "Ada, Bea, Ada, Roma"
    spans = [
        Span(0, 3, "Ada", SpanType.PERSONA, 1.0, GOLD_SOURCE),
        Span(5, 8, "Bea", SpanType.PERSONA, 1.0, GOLD_SOURCE),
        Span(10, 13, "Ada", SpanType.PERSONA, 1.0, GOLD_SOURCE),
        Span(15, 19, "Roma", SpanType.CITTA, 1.0, GOLD_SOURCE),
    ]
    entities = resolve(list(reversed(spans)), text)
    assert [(e.entity_id, e.canonical, len(e.mentions)) for e in entities] == [
        ("PERSONA_1", "Ada", 2),
        ("PERSONA_2", "Bea", 1),
        ("CITTA_1", "Roma", 1),
    ]
    assert sum(len(e.mentions) for e in entities) == len(spans)


# --- pipeline ----------------------------------------------------------------------


@pytest.mark.parametrize("record", FIXTURES, ids=[r.id for r in FIXTURES])
def test_fixture_end_to_end_with_fake_provider(record, config, sent):
    prompts, models_file = sent
    config = with_overrides(config, models_file=models_file)
    result = pipeline.protect_send_restore(record.text, TASK, config)

    ((system, prompt),) = prompts
    assert system == pipeline.KEEP_PLACEHOLDERS_INSTRUCTION
    assert prompt == f"{TASK}\n\n{result.masked_text}"
    masked, _ = pipeline.mask(record.text, config)
    assert result.masked_text == masked.masked_text
    masked_values = [m.text for e in masked.entities for m in e.mentions]
    assert masked_values
    for value in masked_values:  # no masked value reaches the provider
        assert value not in prompt
    for span in record.spans:  # in particular no gold direct identifier that D0 covers
        if span.cls is SpanClass.DIRECT and span.type in DETECTED_BY_D0:
            assert span.text not in prompt
    # The provider echoes, so restoring must give back exactly the original text.
    assert result.restored_reply == f"{TASK}\n\n{record.text}"
    assert result.fully_restored
    assert {e.outcome for e in result.restore_events} == {RestoreOutcome.RESTORED}
    assert len(result.disclosure) == len(masked.entities) > 0


def test_mask_never_calls_a_model(config, sent):
    prompts, models_file = sent
    pipeline.mask(FIXTURES[0].text, with_overrides(config, models_file=models_file))
    assert prompts == []


def test_quasi_identifiers_masked_only_with_mask_quasi(config):
    text = "Rimborso di 50 euro sull'IBAN IT89Y0000025613651127989360."
    off, _ = pipeline.mask(text, config)
    on, _ = pipeline.mask(text, with_overrides(config, mask_quasi=True))
    assert "50 euro" in off.masked_text and "[IMPORTO_1]" in on.masked_text
    assert "[IBAN_1]" in off.masked_text and "[IBAN_1]" in on.masked_text
    assert any(s.cls is SpanClass.QUASI for s in off.spans)  # reported, not masked
    assert all(e.cls is not SpanClass.QUASI for e in off.entities)


def test_disclosure_never_contains_original_values(config):
    result, _ = pipeline.mask(FIXTURES[0].text, config)
    shown = json.dumps([str(item) for item in result.disclosure])
    for span in result.spans:
        assert span.text not in shown


def test_vault_is_erased_before_returning(config, monkeypatch):
    created = []

    class SpyVault(pipeline.Vault):
        def __init__(self):
            super().__init__()
            created.append(self)

    monkeypatch.setattr(pipeline, "Vault", SpyVault)
    pipeline.protect_send_restore(FIXTURES[0].text, TASK, config)
    assert len(created) == 1 and len(created[0]) == 0


# --- CLI ---------------------------------------------------------------------------


def write_config(tmp_path, backend):
    data = yaml.safe_load((REPO / "configs" / "skeleton.yaml").read_text(encoding="utf-8"))
    data.update(
        backend=backend,
        cache_dir=str(tmp_path / "cache"),
        models_file=str(REPO / "configs" / "models.echo.yaml"),
    )
    path = tmp_path / f"{backend}.yaml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


def fixture_path(record):
    return str(REPO / "data" / "fixtures" / f"{record.id}.json")


def run(tmp_path, backend, *args):
    return cli.main([args[0], "--config", str(write_config(tmp_path, backend)), *args[1:]])


@pytest.mark.parametrize("record", FIXTURES, ids=[r.id for r in FIXTURES])
def test_cli_run_then_replay_gives_the_same_result(record, tmp_path, capsys):
    assert run(tmp_path, "cloud", "run", "--input", fixture_path(record)) == 0
    first = capsys.readouterr().out
    assert run(tmp_path, "replay", "run", "--input", fixture_path(record)) == 0
    second = capsys.readouterr().out
    assert first == second
    assert "fully restored: True" in first


def test_cli_replay_without_cache_fails_cleanly(tmp_path, capsys):
    assert run(tmp_path, "replay", "run", "--input", fixture_path(FIXTURES[0])) == 2
    assert "no cached response" in capsys.readouterr().err


def test_cli_backend_override(tmp_path, capsys):
    path = fixture_path(FIXTURES[0])
    assert run(tmp_path, "cloud", "run", "--input", path, "--backend", "replay") == 2


def test_cli_batch(tmp_path, capsys):
    assert run(tmp_path, "cloud", "batch", "--input-dir", str(REPO / "data" / "fixtures")) == 0
    lines = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert [line["text_id"] for line in lines] == [r.id for r in FIXTURES]
    assert all(line["fully_restored"] for line in lines)
    assert len({line["run_id"] for line in lines}) == 1


def test_cli_plain_text_input(tmp_path, capsys):
    source = tmp_path / "email.txt"
    source.write_text("Il mio IBAN è IT89Y0000025613651127989360.", encoding="utf-8")
    assert run(tmp_path, "cloud", "run", "--input", str(source)) == 0
    out = capsys.readouterr().out
    assert "Il mio IBAN è [IBAN_1]." in out
