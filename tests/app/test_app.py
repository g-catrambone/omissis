"""The demo app: the functions behind the two buttons, and the page itself."""

import dataclasses
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


def run(text, detector="D0", strategy="R1", backend="cloud", task=app.DEFAULT_TASK):
    """Both steps on the same inputs: the preview and the result of sending it."""
    *shown, preview = app.protect(text, detector, strategy, backend, task)
    assert preview is not None, shown
    return tuple(shown), app.send(text, detector, strategy, backend, task, preview)


def test_protect_shows_the_masked_text_and_sends_nothing(setup):
    prompts, tmp_path = setup
    masked, reply, table, message, preview = app.protect(RECORD.text, "D0", "R1", "cloud")
    assert prompts == []  # no call to the role cloud
    assert not (tmp_path / "scratch").exists() and not (tmp_path / "cache").exists()
    assert ("[IBAN_1]", "IBAN") in masked and ("[EMAIL_1]", "EMAIL") in masked
    assert "".join(piece for piece, _ in masked) == preview.masked_text
    assert "IT89Y0000025613651127989360" not in preview.masked_text
    assert reply == "" and message == app.PREVIEWED
    assert ["[IBAN_1]", "direct", "IBAN", "D0", "", ""] in table  # restoration column empty
    assert all(len(row) == len(app.HEADERS) and row[-1] == "" for row in table)


def test_full_run_shows_masked_text_reply_and_disclosure(setup):
    prompts, _ = setup
    (masked, _, _, _), (shown, reply, table, message) = run(RECORD.text)
    sent = "".join(piece for piece, _ in shown)
    assert prompts == [f"{app.DEFAULT_TASK}\n\n{sent}"]  # the page shows what was sent
    assert shown == masked  # and it is what the preview showed
    assert "IT89Y0000025613651127989360" not in sent
    assert "IT89Y0000025613651127989360" in reply
    assert ["[IBAN_1]", "direct", "IBAN", "D0", "", ""] in table
    assert all(len(row) == len(app.HEADERS) for row in table)
    assert message.startswith("Fully restored. Run ")


def test_what_is_sent_is_what_was_previewed(setup):
    prompts, _ = setup
    for strategy in ("R1", "R2"):
        prompts.clear()
        (_, _, _, _), _ = run(RECORD.text, strategy=strategy)
        *_, preview = app.protect(RECORD.text, "D0", strategy, "cloud")
        assert prompts == [f"{app.DEFAULT_TASK}\n\n{preview.masked_text}"]


def test_send_without_a_preview_is_refused(setup):
    prompts, tmp_path = setup
    result = app.send(RECORD.text, "D0", "R1", "cloud", app.DEFAULT_TASK, None)
    assert result == ([], "", [], "Nothing to send: press Protect first.")
    assert prompts == [] and not (tmp_path / "scratch").exists()


@pytest.mark.parametrize(
    "change",
    [
        {"text": RECORD.text + " "},
        {"detector": "D1"},
        {"strategy": "R2"},
        {"backend": "replay"},
        {"task": "Riassumi questa email in tre punti."},
    ],
)
def test_send_after_any_input_changed_is_refused(setup, change):
    prompts, tmp_path = setup
    *_, preview = app.protect(RECORD.text, "D0", "R1", "cloud")
    inputs = dict(
        text=RECORD.text, detector="D0", strategy="R1", backend="cloud", task=app.DEFAULT_TASK
    )
    inputs.update(change)
    masked, reply, table, message = app.send(**inputs, preview=preview)
    assert (masked, reply, table) == ([], "", [])
    assert "Press Protect again" in message
    assert prompts == [] and not (tmp_path / "scratch").exists()


def test_an_empty_request_in_the_send_step_is_the_default_one(setup):
    prompts, _ = setup
    *_, preview = app.protect(RECORD.text, "D0", "R1", "cloud", "  ")
    app.send(RECORD.text, "D0", "R1", "cloud", "", preview)
    assert len(prompts) == 1 and prompts[0].startswith(f"{app.DEFAULT_TASK}\n\n")


def test_a_masked_text_that_differs_from_the_preview_is_not_sent(setup, monkeypatch):
    prompts, _ = setup
    *_, preview = app.protect(RECORD.text, "D0", "R1", "cloud")
    real = app.mask

    def different(text, config, gold_spans=None, vault=None):
        result, vault = real(text, config, gold_spans, vault)
        return dataclasses.replace(result, masked_text=result.masked_text + "!"), vault

    monkeypatch.setattr(app, "mask", different)
    masked, reply, table, message = app.send(
        RECORD.text, "D0", "R1", "cloud", app.DEFAULT_TASK, preview
    )
    assert (masked, reply, table) == ([], "", [])
    assert "not the one that was previewed" in message
    assert prompts == []


def test_the_vault_of_each_masking_is_erased(setup, monkeypatch):
    vaults = []
    real = app.mask

    def spy(text, config, gold_spans=None, vault=None):
        result, vault = real(text, config, gold_spans, vault)
        vaults.append(vault)
        assert len(vault) > 0  # it held the originals while masking
        return result, vault

    monkeypatch.setattr(app, "mask", spy)
    run(RECORD.text)
    assert len(vaults) == 2 and all(len(v) == 0 for v in vaults)


def test_cloud_writes_the_scratch_cache_and_replay_reads_the_committed_one(setup):
    _, tmp_path = setup
    run(RECORD.text)
    assert (tmp_path / "scratch" / "cloud.jsonl").exists()
    assert not (tmp_path / "cache").exists()
    *_, preview = app.protect(RECORD.text, "D0", "R1", "replay")
    masked, reply, table, message = app.send(
        RECORD.text, "D0", "R1", "replay", app.DEFAULT_TASK, preview
    )
    assert (masked, reply, table) == ([], "", [])
    assert "cache" in message and "replay" in message  # a readable cache miss


def test_replay_shows_a_run_recorded_in_the_cache(setup, monkeypatch):
    _, tmp_path = setup
    monkeypatch.setattr(app, "SCRATCH_CACHE", tmp_path / "cache")  # record where replay reads
    _, recorded = run(RECORD.text)
    monkeypatch.setattr(backends, "_PROVIDERS", {})  # replay needs no provider
    _, replayed = run(RECORD.text, backend="replay")
    assert replayed == recorded


def test_detector_not_built_yet_shows_a_readable_message(setup, monkeypatch):
    def not_built(text, detector, config):
        raise NotImplementedError("detector D9 is not built yet")

    monkeypatch.setattr("omissis.pipeline.detect", not_built)
    monkeypatch.setattr(app, "supported_detectors", lambda: (DetectorId.D0,))
    masked, reply, table, message, preview = app.protect(RECORD.text, "D0", "R1", "cloud")
    assert (masked, reply, table, preview) == ([], "", [], None)
    assert message == "Not available yet: detector D9 is not built yet"


def test_a_configuration_error_shows_a_readable_message(setup):
    *shown, message, preview = app.protect(RECORD.text, "D9", "R1", "cloud")
    assert preview is None and message.startswith("Invalid configuration: ")


def test_a_provider_that_fails_shows_a_readable_message(setup, monkeypatch):
    def failing(model, request):
        raise RuntimeError("quota exceeded")

    monkeypatch.setattr(backends, "_PROVIDERS", {"fake": failing})
    *_, preview = app.protect(RECORD.text, "D0", "R1", "cloud")
    assert preview is not None  # step 1 makes no call to the model
    *shown, message = app.send(RECORD.text, "D0", "R1", "cloud", app.DEFAULT_TASK, preview)
    assert message == "The call to the model failed: quota exceeded"


@pytest.mark.parametrize("error", [ValueError("broken cache line"), OSError("disk full")])
def test_value_and_os_errors_are_handled_in_both_steps(setup, monkeypatch, error):
    def failing(text, detector, config):
        raise error

    *_, preview = app.protect(RECORD.text, "D0", "R1", "cloud")
    monkeypatch.setattr("omissis.pipeline.detect", failing)
    *shown, message, none = app.protect(RECORD.text, "D0", "R1", "cloud")
    assert none is None and message == f"The run failed: {error}"
    *shown, message = app.send(RECORD.text, "D0", "R1", "cloud", app.DEFAULT_TASK, preview)
    assert message == f"The run failed: {error}"


def test_restoration_problems_are_listed(setup, monkeypatch):
    def altering(model, request):
        return request.prompt.replace("[IBAN_1]", "[IBAN_01]") + " Vedi anche [CITTA_9]."

    monkeypatch.setattr(backends, "_PROVIDERS", {"fake": altering})
    _, (_, _, table, message) = run(RECORD.text)
    assert ["[IBAN_1]", "direct", "IBAN", "D0", "", "altered_unresolved ([IBAN_01])"] in table
    assert ["[CITTA_9]", "", "", "", "", "hallucinated_token"] in table
    assert message.startswith("Not fully restored: see the table. Run ")


def test_every_invented_form_of_a_token_has_its_own_row(setup, monkeypatch):
    def inventing(model, request):
        return request.prompt + " [IBAN_7] e poi IBAN_7 e [iban_7]"

    monkeypatch.setattr(backends, "_PROVIDERS", {"fake": inventing})
    _, (_, _, table, _) = run(RECORD.text)
    extra = [row for row in table if row[0] != "[IBAN_1]" and row[-1]]
    assert len(extra) >= 2 and all(row[-1] == "hallucinated_token" for row in extra)
    assert len({row[0] for row in extra}) == len(extra)  # distinct forms, distinct rows


def test_rows_gives_each_event_that_is_not_restored_a_row():
    from omissis.contracts import DisclosureItem, RestoreEvent, RestoreOutcome

    events = tuple(
        RestoreEvent("[IBAN_7]", RestoreOutcome.HALLUCINATED_TOKEN, form)
        for form in ("[IBAN_7]", "IBAN_7", "[iban_7]")
    ) + (RestoreEvent("[IBAN_1]", RestoreOutcome.RESTORED, "[IBAN_1]"),)
    item = DisclosureItem("[IBAN_1]", SpanType.IBAN, "D0")
    result = app.PipelineResult("r", "m", "x", "y", (item,), events)
    table = app.rows(result)
    assert [row[0] for row in table] == ["[IBAN_1]", "[IBAN_7]", "IBAN_7", "[iban_7]"]


def test_r2_fakes_are_highlighted_and_restored(setup):
    (masked, _, _, _), (_, reply, _, _) = run(RECORD.text, strategy="R2")
    labelled = [piece for piece, label in masked if label == "IBAN"]
    assert len(labelled) == 2 and all(p.startswith("IT") and "00000" in p for p in labelled)
    assert "IT89Y0000025613651127989360" in reply


def test_d3_reason_is_shown(setup, monkeypatch):
    value = "impiegata amministrativa"
    start = RECORD.text.index(value)
    found = [Span(start, start + len(value), value, SpanType.RUOLO, 0.8, "D3", "mestiere")]
    monkeypatch.setattr("omissis.pipeline.detect", lambda text, detector, config: found)
    (_, _, table, _), (_, _, table_sent, _) = run(RECORD.text, "D3")
    assert table == table_sent == [["[RUOLO_1]", "quasi", "RUOLO", "D3", "mestiere", ""]]


def test_empty_text_asks_for_a_text(setup):
    assert app.protect("  ", "D0", "R1", "replay") == ([], "", [], "Write or choose a text.", None)


def test_page_builds_with_the_supported_detectors(setup, monkeypatch):
    pytest.importorskip("gradio")
    monkeypatch.setattr(app, "supported_detectors", lambda: (DetectorId.D0, DetectorId.D1))
    page = app.build()
    dropdowns = [b for b in page.blocks.values() if type(b).__name__ == "Dropdown"]
    assert [choice[0] for choice in dropdowns[0].choices] == ["D0", "D1"]


def test_page_has_two_buttons_and_send_is_not_interactive_until_a_preview(setup):
    pytest.importorskip("gradio")
    page = app.build()
    buttons = {b.value: b for b in page.blocks.values() if type(b).__name__ == "Button"}
    assert set(buttons) == {"1 · Protect", "2 · Send"}
    assert buttons["2 · Send"].interactive is False and buttons["1 · Protect"].interactive


def test_page_says_that_d3_and_d4_read_the_whole_text_before_it_is_masked(setup):
    # The detector D3, alone or inside D4, is itself a model that receives the original text.
    pytest.importorskip("gradio")
    page = app.build()
    header = next(b for b in page.blocks.values() if type(b).__name__ == "Markdown").value
    assert "D3 and D4" in header and "not yet pseudonymised" in header
    assert "anonym" not in header.lower()


# --- the request and its feasibility check (step B5) ---------------------------------------

SUM = "Calcola il totale degli importi indicati"


def test_a_calculation_on_masked_amounts_is_not_sent_nor_previewed(setup):
    prompts, tmp_path = setup
    masked, reply, table, message, preview = app.protect(RECORD.text, "D0", "R1", "cloud", SUM)
    assert (masked, reply, table, preview) == ([], "", [], None)
    assert prompts == [] and not (tmp_path / "scratch").exists()  # nothing left the machine
    assert message.startswith("Request not sent") and "1 IMPORTO" in message
    assert "320,00" not in message  # the reason names types and counts, never a value


def test_a_request_without_a_calculation_is_sent_as_written(setup):
    prompts, _ = setup
    task = "Riassumi questa email in tre punti."
    (_, _, _, _), (masked, _, _, message) = run(RECORD.text, task=task)
    sent = "".join(piece for piece, _ in masked)
    assert prompts == [f"{task}\n\n{sent}"] and message.startswith("Fully restored.")


def test_a_detector_that_fails_during_the_check_shows_its_message(setup, monkeypatch):
    def not_built(text, detector, config):
        raise NotImplementedError("detector D9 is not built yet")

    monkeypatch.setattr("omissis.pipeline.detect", not_built)
    *_, message, preview = app.protect(RECORD.text, "D0", "R1", "cloud", SUM)
    assert message == "Not available yet: detector D9 is not built yet" and preview is None


def test_page_has_a_field_for_the_request_with_the_default_task(setup):
    pytest.importorskip("gradio")
    page = app.build()
    boxes = [b for b in page.blocks.values() if type(b).__name__ == "Textbox"]
    request = [b for b in boxes if b.label == "Request"]
    assert [b.value for b in request] == [app.DEFAULT_TASK]
    assert "not masked" in request[0].info
