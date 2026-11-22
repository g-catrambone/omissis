"""The feasibility check before sending: the cues, the masked types that block a
request, and what `omissis run` does with a blocked one. No test needs the network."""

from pathlib import Path

import pytest
import yaml

from omissis import backends, cli, feasibility
from omissis.config import ROLES, load_config, with_overrides
from omissis.contracts import Entity, Span, SpanType, VaultEntry
from omissis.eval.datasets import load_texts
from omissis.vault import Vault

REPO = Path(__file__).resolve().parents[2]
FIXTURE_DIR = REPO / "data" / "fixtures"
FIXTURES = load_texts(FIXTURE_DIR)
TWO_AMOUNTS = next(r for r in FIXTURES if r.id == "fx-bank-02")
SUM = "Calcola il totale dei due importi"
AMOUNTS = ("89,90", "245,00")  # the original amounts of the fixture: never in a message

CALCULATIONS = [
    SUM,
    "Somma le rate indicate nell'email.",
    "Qual è la differenza tra i due importi?",
    "Che percentuale della rata è la commissione?",
    "QUANTO DEVO PAGARE IN TUTTO?",
    "Qual è la media delle rate?",
    "Quanti giorni mancano alla scadenza?",
    "Quanto resta da pagare dopo la prima rata?",
    "Ricalcola l'importo complessivo.",
    "Sottrai l'acconto dal saldo.",
    "Sommali.",
    "Sommate le rate e ditemi il risultato.",
    "Prendi i due importi e prova a sommarli.",
]
NO_CALCULATION = [
    cli.DEFAULT_TASK,
    "Riassumi questa email in tre punti.",
    "Traduci l'email in inglese.",
    "Riscrivi la risposta in tono formale.",
    "Quali documenti chiede il cliente?",
    "Fai un sommario dell'email.",
    "Tutto sommato, rispondi in modo cortese.",
    "",
]


def entity(kind: SpanType, n: int = 1) -> Entity:
    return Entity(f"{kind.value}_{n}", kind, "x", (Span(0, 1, "x", kind, 1.0, "D0"),))


@pytest.fixture
def config(tmp_path):
    """The defaults of the demo: detector D0, placeholders, quasi-identifiers masked."""
    return with_overrides(load_config(REPO / "configs" / "app.yaml"), cache_dir=tmp_path)


# --- the cues ------------------------------------------------------------------------------


@pytest.mark.parametrize("task", CALCULATIONS)
def test_a_request_with_a_calculation_cue_is_recognised(task):
    assert feasibility.asks_calculation(task)


@pytest.mark.parametrize("task", NO_CALCULATION)
def test_a_request_without_a_cue_is_not(task):
    assert not feasibility.asks_calculation(task)


# --- what blocks ---------------------------------------------------------------------------


def test_masked_amounts_dates_and_ages_block_a_calculation_with_their_counts():
    entities = [
        entity(SpanType.IMPORTO, 1),
        entity(SpanType.PERSONA),
        entity(SpanType.IMPORTO, 2),
        entity(SpanType.ETA),
        entity(SpanType.DATA),
        entity(SpanType.DATA_NASCITA),
    ]
    assert feasibility.check(SUM, entities) == {
        SpanType.IMPORTO: 2,
        SpanType.DATA: 1,
        SpanType.ETA: 1,
        SpanType.DATA_NASCITA: 1,
    }


def test_nothing_blocks_without_a_cue_or_without_a_masked_value_to_compute_on():
    amount = [entity(SpanType.IMPORTO)]
    assert feasibility.check(cli.DEFAULT_TASK, amount) == {}
    assert feasibility.check(SUM, [entity(SpanType.PERSONA), entity(SpanType.IBAN)]) == {}
    assert feasibility.check(SUM, []) == {}


def test_the_text_is_masked_as_the_run_would_mask_it(config):
    assert feasibility.check_text(TWO_AMOUNTS.text, SUM, config) == {SpanType.IMPORTO: 2}
    # An amount that stays visible can be computed on: nothing blocks.
    visible = with_overrides(config, mask_quasi=False)
    assert feasibility.check_text(TWO_AMOUNTS.text, SUM, visible) == {}
    unmasked = with_overrides(config, detector="NONE", mask_quasi=False)
    assert feasibility.check_text(TWO_AMOUNTS.text, SUM, unmasked) == {}


def test_gold_spans_are_used_with_detector_gold(config):
    gold = with_overrides(config, detector="GOLD")
    blocked = feasibility.check_text(TWO_AMOUNTS.text, SUM, gold, TWO_AMOUNTS.spans)
    # D0 has no rule for an age: only the annotation finds it.
    assert blocked[SpanType.IMPORTO] == 2 and blocked[SpanType.ETA] == 1


def test_an_ordinary_request_is_not_masked_twice(config, monkeypatch):
    def never(*args, **kwargs):
        raise AssertionError("a request without a cue needs no masking")

    monkeypatch.setattr(feasibility, "mask", never)
    assert feasibility.check_text(TWO_AMOUNTS.text, cli.DEFAULT_TASK, config) == {}


def test_the_vault_of_the_check_is_erased_also_when_masking_fails(config, monkeypatch):
    vaults = []

    class Recorded(Vault):
        def __init__(self):
            super().__init__()
            vaults.append(self)

    monkeypatch.setattr(feasibility, "Vault", Recorded)
    assert feasibility.check_text(TWO_AMOUNTS.text, SUM, config)
    assert len(vaults) == 1 and len(vaults[0]) == 0

    def failing(text, config, gold_spans, vault):
        vault.add(VaultEntry("[IMPORTO_1]", "89,90 euro", SpanType.IMPORTO, "IMPORTO_1"))
        raise RuntimeError("the detector failed")

    monkeypatch.setattr(feasibility, "mask", failing)
    with pytest.raises(RuntimeError, match="the detector failed"):
        feasibility.check_text(TWO_AMOUNTS.text, SUM, config)
    assert len(vaults) == 2 and len(vaults[1]) == 0


# --- the command line ----------------------------------------------------------------------


@pytest.fixture
def sent(monkeypatch, tmp_path):
    """Every role pinned to a fake provider that records the prompts and echoes them."""
    prompts = []

    def fake(model, request):
        prompts.append(request.prompt)
        return request.prompt

    monkeypatch.setattr(backends, "_PROVIDERS", {"fake": fake})
    models = tmp_path / "models.yaml"
    models.write_text(
        yaml.safe_dump({r: {"provider": "fake", "id": "fake", "revision": "1"} for r in ROLES}),
        encoding="utf-8",
    )
    return prompts, models


def run_config(tmp_path, models, **changes):
    settings = yaml.safe_load((REPO / "configs" / "app.yaml").read_text(encoding="utf-8"))
    settings.update(models_file=str(models), cache_dir=str(tmp_path / "cache"), backend="cloud")
    settings.update(changes)
    path = tmp_path / "run.yaml"
    path.write_text(yaml.safe_dump(settings), encoding="utf-8")
    return str(path)


def test_run_does_not_send_a_calculation_on_masked_amounts(sent, tmp_path, capsys):
    prompts, models = sent
    fixture = str(FIXTURE_DIR / "fx-bank-02.json")
    args = ["run", "--config", run_config(tmp_path, models), "--input", fixture]
    assert cli.main([*args, "--task", SUM]) == 2
    captured = capsys.readouterr()
    assert prompts == [] and captured.out == ""
    assert captured.err.count("\n") == 1  # one line, as every error of the command
    assert "not sent" in captured.err and "IMPORTO: 2" in captured.err
    assert not any(amount in captured.err for amount in AMOUNTS)
    # The default request on the same text is sent as before.
    assert cli.main(args) == 0
    assert len(prompts) == 1 and prompts[0].startswith(cli.DEFAULT_TASK)


def test_run_checks_the_gold_spans_of_a_record(sent, tmp_path, capsys):
    prompts, models = sent
    config = run_config(tmp_path, models, detector="GOLD")
    fixture = str(FIXTURE_DIR / "fx-bank-02.json")
    assert cli.main(["run", "--config", config, "--input", fixture, "--task", SUM]) == 2
    assert prompts == [] and "ETA: 1" in capsys.readouterr().err


def test_batch_is_not_checked(sent, tmp_path, capsys):
    prompts, models = sent
    args = ["batch", "--config", run_config(tmp_path, models), "--input-dir", str(FIXTURE_DIR)]
    assert cli.main([*args, "--task", SUM]) == 0
    assert len(prompts) == len(FIXTURES)
