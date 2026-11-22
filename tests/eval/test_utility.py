"""Utility tasks: T3 scoring and the restoration record, with a fake provider."""

import json
from pathlib import Path

import pytest
import yaml

from omissis import backends
from omissis.cli import DEFAULT_TASK
from omissis.config import ROLES, load_eval_configs, with_overrides
from omissis.eval import utility
from omissis.eval.datasets import Gold, load_texts

REPO = Path(__file__).resolve().parents[2]
FIXTURES = {r.id: r for r in load_texts(REPO / "data" / "fixtures")}
GOLD = Gold(
    intent="iban_change",
    amounts=(320.0, 1200.5),
    dates=("2026-12-01", "2026-11-20"),
    requested_action="update_details",
    deadline="2026-11-20",
)
RIGHT = {
    "intent": "iban_change",
    "requested_action": "update_details",
    "amounts": ["€ 320,00", "1.200,50 euro"],
    "dates": ["1 dicembre 2026", "20/11/2026"],
    "deadline": "20 novembre 2026",
}


def score(**changes):
    return utility.score_t3(json.dumps({**RIGHT, **changes}), GOLD)


def test_all_fields_right_in_the_formats_of_the_texts():
    result = score()
    assert result == {"parsed": True, "fields": dict.fromkeys(utility.FIELDS, True), "score": 1.0}


@pytest.mark.parametrize(
    "changes",
    [
        {"amounts": ["1.200,50 euro", "EUR 320"]},  # another order, another format
        {"amounts": [320, 1200.5]},  # numbers
        {"amounts": ["€ 320,00", "€ 320,00", "1200,5 euro"]},  # a repeat: compared as sets
        {"dates": ["20.11.2026", "2026-12-01"]},
        {"deadline": "2026-11-20"},
        {"deadline": "20/11/2026"},
    ],
)
def test_equal_values_in_different_formats_are_correct(changes):
    assert score(**changes)["score"] == 1.0


@pytest.mark.parametrize(
    ("changes", "wrong"),
    [
        ({"intent": "account_closure"}, "intent"),
        ({"requested_action": "send_information"}, "requested_action"),
        ({"amounts": ["€ 320,00"]}, "amounts"),  # one missing
        ({"amounts": ["€ 320,00", "1.200,50 euro", "€ 5"]}, "amounts"),  # one too many
        ({"amounts": ["trecentoventi euro", "1.200,50 euro"]}, "amounts"),  # unreadable
        ({"amounts": "€ 320,00"}, "amounts"),  # not a list
        ({"dates": ["1 dicembre 2026"]}, "dates"),
        ({"dates": ["1 dicembre 2026", "a novembre"]}, "dates"),
        ({"deadline": None}, "deadline"),
        ({"deadline": "1 dicembre 2026"}, "deadline"),
        ({"deadline": "entro novembre"}, "deadline"),
    ],
)
def test_one_wrong_field_costs_one_fifth(changes, wrong):
    result = score(**changes)
    assert result["score"] == pytest.approx(0.8)
    assert [f for f, ok in result["fields"].items() if not ok] == [wrong]


def test_missing_fields_are_wrong_and_null_deadline_must_be_said():
    no_deadline = Gold("iban_change", (), (), "update_details", None)
    full = {
        "intent": "iban_change",
        "requested_action": "update_details",
        "amounts": [],
        "dates": [],
        "deadline": None,
    }
    assert utility.score_t3(json.dumps(full), no_deadline)["score"] == 1.0
    without = {k: v for k, v in full.items() if k not in ("deadline", "amounts")}
    result = utility.score_t3(json.dumps(without), no_deadline)
    assert result["fields"]["deadline"] is False and result["fields"]["amounts"] is False
    assert result["score"] == pytest.approx(0.6)


@pytest.mark.parametrize("reply", ["non riesco a rispondere", "", "[1, 2]", '{"intent": '])
def test_unparseable_reply_scores_zero(reply):
    result = utility.score_t3(reply, GOLD)
    assert result["score"] == 0.0 and result["parsed"] is False


def test_json_in_a_code_fence_is_read():
    reply = "```json\n" + json.dumps(RIGHT) + "\n```"
    assert utility.score_t3(reply, GOLD)["score"] == 1.0


def test_prompt_lists_the_closed_vocabularies():
    assert len(utility.ACTIONS) == 11
    for word in ("mortgage_suspension", "union_leave", "suspend_payment", "register_absence"):
        assert word in utility.T3_TASK
    assert utility.T1_TASK == DEFAULT_TASK


# --- end to end --------------------------------------------------------------------


@pytest.fixture
def setup(monkeypatch, tmp_path):
    """A provider that extracts by copying placeholders, and drafts by echoing."""
    answers = {}

    def fake(model, request):
        if request.prompt.startswith(utility.T3_TASK):
            return json.dumps(answers["t3"](request.prompt))
        return answers.get("t1", lambda prompt: prompt)(request.prompt)

    monkeypatch.setattr(backends, "_PROVIDERS", {"fake": fake})
    models = tmp_path / "models.yaml"
    models.write_text(
        yaml.safe_dump({r: {"provider": "fake", "id": "fake", "revision": "1"} for r in ROLES}),
        encoding="utf-8",
    )
    overrides = {"models_file": str(models), "cache_dir": str(tmp_path / "cache")}
    return answers, load_eval_configs(REPO / "configs" / "eval.yaml", overrides)


def test_values_extracted_as_placeholders_are_scored_after_restoration(setup):
    answers, configs = setup
    record = FIXTURES["fx-hr-02"]
    answers["t3"] = lambda prompt: {
        "intent": "transfer_request",
        "requested_action": "approve_request",
        "amounts": [],
        "dates": ["[DATA_1]", "[DATA_2]"],  # the masked text holds placeholders
        "deadline": "[DATA_2]",
    }
    (row,) = utility.run([record], "REF-oracle", configs["REF-oracle"])
    assert row["t3"] == 1.0 and row["t3_parsed"] and all(row["t3_fields"].values())
    assert (row["text_id"], row["config"]) == ("fx-hr-02", "REF-oracle")
    assert row["fully_restored"] is True and row["outcomes"] == {"restored": 12}
    assert row["restored_fakes"] == 0 and "text" not in row


def test_unmasked_reference_is_scored_like_any_other(setup):
    answers, configs = setup
    record = FIXTURES["fx-hr-02"]
    answers["t3"] = lambda prompt: {
        "intent": "transfer_request",
        "requested_action": "schedule_meeting",  # wrong
        "amounts": [],
        "dates": ["1 marzo 2027", "15 dicembre 2026"],
        "deadline": "15 dicembre 2026",
    }
    (row,) = utility.run([record], "REF-none", configs["REF-none"])
    assert row["t3"] == pytest.approx(0.8) and row["outcomes"] == {}


def test_restoration_of_the_draft_is_recorded_and_fakes_are_counted(setup):
    answers, configs = setup
    record = FIXTURES["fx-bank-01"]
    answers["t3"] = lambda prompt: {}
    r2 = with_overrides(configs["REF-oracle"], strategy="R2")
    (row,) = utility.run([record], "X", r2)
    assert row["fully_restored"] and row["t3"] == 0.0 and row["t3_parsed"]
    # The role keeps its placeholder under R2: every other restored surrogate is a fake.
    assert row["restored_fakes"] == row["outcomes"]["restored"] - 1

    answers["t1"] = lambda prompt: "Gentile [PERSONA_1_M], vedi [CITTA_9]."
    (row,) = utility.run([record], "Y", with_overrides(configs["REF-oracle"], seed=5))
    assert row["fully_restored"] is False
    assert row["outcomes"]["altered_unresolved"] == 1 and row["outcomes"]["hallucinated_token"] == 1


def test_t1_reply_comes_from_the_cache_after_the_run(setup, monkeypatch):
    answers, configs = setup
    record = FIXTURES["fx-bank-01"]
    answers["t3"] = lambda prompt: {}
    utility.run([record], "REF-oracle", configs["REF-oracle"])
    monkeypatch.setattr(backends, "_PROVIDERS", {})  # no provider: only the cache can answer
    replay = with_overrides(configs["REF-oracle"], backend="replay")
    assert record.text in utility.t1_reply(record, replay)


@pytest.mark.parametrize(
    "answer", ["", "entro fine mese", "15 dicembre", "31/02/2026", 0, "nessuna"]
)
def test_answer_that_is_not_a_date_is_wrong_when_the_text_has_no_deadline(answer):
    # Only null says "no deadline": an answer that cannot be read as a date is not null.
    no_deadline = Gold("iban_change", (), (), "update_details", None)
    reply = {
        "intent": "iban_change",
        "requested_action": "update_details",
        "amounts": [],
        "dates": [],
        "deadline": answer,
    }
    result = utility.score_t3(json.dumps(reply), no_deadline)
    assert result["fields"]["deadline"] is False
    assert result["score"] == pytest.approx(0.8)


@pytest.mark.parametrize(
    "reply",
    [
        '{"intent": "iban_change"}\nNota: i campi {mancanti} sono omessi.',
        'Ecco {la risposta}: {"intent": "iban_change"} (vedi sopra).',
        '```json\n{"intent": "iban_change", "extra": {"a": 1}}\n```\n{fine}',
    ],
)
def test_braces_in_the_words_around_the_object_do_not_hide_it(reply):
    assert utility.extract_json(reply)["intent"] == "iban_change"


@pytest.mark.parametrize(
    "reply",
    [
        '{"intent": "iban_change", "meta": {"k": 1}, oops}',  # broken, with an object inside
        '{"intent": "iban_change", "meta": {"k": 1}, "deadline": "1',  # cut off
        '{"amounts": [{"importo": "10"}], "deadline": None}',  # not JSON
    ],
)
def test_object_inside_a_broken_reply_is_not_taken_for_the_reply(reply):
    assert utility.extract_json(reply) is None
    assert utility.score_t3(reply, GOLD)["parsed"] is False
