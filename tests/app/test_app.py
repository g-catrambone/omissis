"""The demo app (task 2.7): the function behind the button, and the page itself."""

from pathlib import Path

import pytest
import yaml

from omissis import app, backends
from omissis.config import ROLES
from omissis.contracts import DetectorId, Span, SpanType
from omissis.eval.datasets import load_texts

REPO = Path(__file__).resolve().parents[2]
RECORD = load_texts(REPO / "data" / "fixtures")[0]


@pytest.fixture
def setup(monkeypatch, tmp_path):
    """The app on a copy of its configuration, with a fake provider that echoes."""
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
    settings = yaml.safe_load(app.CONFIG_FILE.read_text(encoding="utf-8"))
    settings.update(models_file=str(models), cache_dir=str(tmp_path / "cache"))
    config = tmp_path / "app.yaml"
    config.write_text(yaml.safe_dump(settings), encoding="utf-8")
    monkeypatch.setattr(app, "CONFIG_FILE", config)
    monkeypatch.setattr(app, "SCRATCH_CACHE", tmp_path / "scratch")
    return prompts, tmp_path


def test_full_run_shows_masked_text_reply_and_disclosure(setup):
    prompts, _ = setup
    masked, reply, table, message = app.process(RECORD.text, "D0", "R1", "cloud")
    sent = "".join(piece for piece, _ in masked)
    assert prompts == [f"{app.DEFAULT_TASK}\n\n{sent}"]  # the page shows what was sent
    assert ("[IBAN_1]", "IBAN") in masked and ("[EMAIL_1]", "EMAIL") in masked
    assert "IT89Y0000025613651127989360" not in sent
    assert "IT89Y0000025613651127989360" in reply
    assert ["[IBAN_1]", "direct", "IBAN", "D0", "", ""] in table
    assert all(len(row) == len(app.HEADERS) for row in table)
    assert "Ripristino completo" in message


def test_cloud_writes_the_scratch_cache_and_replay_reads_the_committed_one(setup):
    _, tmp_path = setup
    app.process(RECORD.text, "D0", "R1", "cloud")
    assert (tmp_path / "scratch" / "cloud.jsonl").exists()
    assert not (tmp_path / "cache").exists()
    masked, reply, table, message = app.process(RECORD.text, "D0", "R1", "replay")
    assert (masked, reply, table) == ([], "", [])
    assert "cache" in message and "replay" in message  # a readable cache miss


def test_replay_shows_a_run_recorded_in_the_cache(setup, monkeypatch):
    _, tmp_path = setup
    monkeypatch.setattr(app, "SCRATCH_CACHE", tmp_path / "cache")  # record where replay reads
    recorded = app.process(RECORD.text, "D0", "R1", "cloud")
    monkeypatch.setattr(backends, "_PROVIDERS", {})  # replay needs no provider
    assert app.process(RECORD.text, "D0", "R1", "replay") == recorded


def test_detector_not_built_yet_shows_a_readable_message(setup, monkeypatch):
    def not_built(text, detector, config):
        raise NotImplementedError("detector D9 is not built yet")

    monkeypatch.setattr("omissis.pipeline.detect", not_built)
    monkeypatch.setattr(app, "supported_detectors", lambda: (DetectorId.D0,))
    masked, reply, table, message = app.process(RECORD.text, "D0", "R1", "cloud")
    assert (masked, reply, table) == ([], "", [])
    assert message == "Non ancora disponibile: detector D9 is not built yet"


def test_restoration_problems_are_listed(setup, monkeypatch):
    def altering(model, request):
        return request.prompt.replace("[IBAN_1]", "[IBAN_01]") + " Vedi anche [CITTA_9]."

    monkeypatch.setattr(backends, "_PROVIDERS", {"fake": altering})
    _, _, table, message = app.process(RECORD.text, "D0", "R1", "cloud")
    assert ["[IBAN_1]", "direct", "IBAN", "D0", "", "altered_unresolved ([IBAN_01])"] in table
    assert ["[CITTA_9]", "", "", "", "", "hallucinated_token"] in table
    assert "Ripristino incompleto" in message


def test_r2_fakes_are_highlighted_and_restored(setup):
    masked, reply, table, _ = app.process(RECORD.text, "D0", "R2", "cloud")
    labelled = [piece for piece, label in masked if label == "IBAN"]
    assert len(labelled) == 2 and all(p.startswith("IT") and "00000" in p for p in labelled)
    assert "IT89Y0000025613651127989360" in reply


def test_d3_reason_is_shown(setup, monkeypatch):
    value = "impiegata amministrativa"
    start = RECORD.text.index(value)
    found = [Span(start, start + len(value), value, SpanType.RUOLO, 0.8, "D3", "mestiere")]
    monkeypatch.setattr("omissis.pipeline.detect", lambda text, detector, config: found)
    _, _, table, _ = app.process(RECORD.text, "D3", "R1", "cloud")
    assert table == [["[RUOLO_1]", "quasi", "RUOLO", "D3", "mestiere", ""]]


def test_empty_text_asks_for_a_text(setup):
    assert app.process("  ", "D0", "R1", "replay") == ([], "", [], "Scrivi o scegli un testo.")


def test_page_builds_with_the_supported_detectors(setup, monkeypatch):
    pytest.importorskip("gradio")
    monkeypatch.setattr(app, "supported_detectors", lambda: (DetectorId.D0, DetectorId.D1))
    page = app.build()
    dropdowns = [b for b in page.blocks.values() if type(b).__name__ == "Dropdown"]
    assert [choice[0] for choice in dropdowns[0].choices] == ["D0", "D1"]
