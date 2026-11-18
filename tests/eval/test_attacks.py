"""The two attacks (task 3.3): prompts and scoring, with a fake provider."""

import json
from pathlib import Path

import pytest
import yaml

from omissis import backends
from omissis.config import ROLES, load_eval_configs, with_overrides
from omissis.eval import attacks
from omissis.eval import profiles as planning
from omissis.eval.datasets import load_texts
from omissis.eval.normalise import extract_json

REPO = Path(__file__).resolve().parents[2]
FILES = planning.build(REPO / "data" / "profiles")
POOLS = planning.load_pools(REPO / "data" / "profiles")
PROFILES = {p["id"]: p for p in FILES["profiles.json"]}
PLAN, CANDIDATES = FILES["plan.json"], FILES["candidates_N10.json"]
TEXT_ID = "bank-0001"
AUTHOR = PLAN[TEXT_ID]["profile_id"]
MASKED = {TEXT_ID: "Gentile [AZIENDA_1], sono [PERSONA_1_M], elettricista a [CITTA_1]."}
# A fixture stands in for the text record: only its spans and profile id are read.
RECORD = load_texts(REPO / "data" / "fixtures")[3]  # fx-hr-01: has SALUTE spans


@pytest.fixture
def attacker(monkeypatch, tmp_path):
    state = {"reply": "{}", "requests": []}

    def fake(model, request):
        state["requests"].append(request)
        return state["reply"]

    monkeypatch.setattr(backends, "_PROVIDERS", {"fake": fake})
    models = tmp_path / "models.yaml"
    models.write_text(
        yaml.safe_dump({r: {"provider": "fake", "id": "fake", "revision": "1"} for r in ROLES}),
        encoding="utf-8",
    )
    overrides = {"models_file": str(models), "cache_dir": str(tmp_path / "cache")}
    config = load_eval_configs(REPO / "configs" / "eval.yaml", overrides)["REF-oracle"]
    return state, config


def fresh(config, state):
    """The same configuration on an empty cache: the same prompt is asked again."""
    return with_overrides(config, cache_dir=config.cache_dir / str(len(state["requests"])))


def run_linkage(state, config, ranking):
    position = {p: i for i, p in enumerate(CANDIDATES[TEXT_ID], 1)}
    state["reply"] = (
        ranking
        if isinstance(ranking, str)
        else json.dumps({"ranking": [position[p] for p in ranking]})
    )
    (row,) = attacks.linkage(MASKED, "X", 10, PLAN, PROFILES, CANDIDATES, fresh(config, state))
    return row


def others(k):
    return [p for p in CANDIDATES[TEXT_ID] if p != AUTHOR][:k]


def test_linkage_scores_top1_and_top3(attacker):
    state, config = attacker
    first = run_linkage(state, config, [AUTHOR, *others(2)])
    assert (first["top1"], first["top3"], first["parsed"]) == (True, True, True)
    assert first["ranking"][0] == AUTHOR and (first["text_id"], first["n"]) == (TEXT_ID, 10)
    third = run_linkage(state, config, [*others(2), AUTHOR])
    assert (third["top1"], third["top3"]) == (False, True)
    absent = run_linkage(state, config, others(3))
    assert (absent["top1"], absent["top3"], absent["parsed"]) == (False, False, True)


@pytest.mark.parametrize(
    "reply",
    [
        "non lo so",
        '{"ranking": [1, 2]}',  # two, not three
        '{"ranking": [1, 1, 2]}',  # a repeated candidate
        '{"ranking": [1, 2, 11]}',  # outside the list
        '{"ranking": [0, 1, 2]}',
        '{"ranking": ["1", "2", "3"]}',  # not numbers
        '{"classifica": [1, 2, 3]}',
    ],
)
def test_unparseable_ranking_is_a_miss_and_is_counted(attacker, reply):
    state, config = attacker
    row = run_linkage(state, config, reply)
    assert (row["parsed"], row["top1"], row["top3"], row["ranking"]) == (False, False, False, None)


def test_linkage_prompt_shows_the_text_and_the_candidates_but_no_id_or_cohort(attacker):
    state, config = attacker
    run_linkage(state, config, [AUTHOR, *others(2)])
    request = state["requests"][-1]
    assert request.role == "attacker" and dict(request.params)["temperature"] == 0
    assert MASKED[TEXT_ID] in request.prompt
    for i, pid in enumerate(CANDIDATES[TEXT_ID], 1):
        assert f"{i}. {PROFILES[pid]['name']}" in request.prompt
        assert pid not in request.prompt and f" {PROFILES[pid]['cohort']}" not in request.prompt
    for word in ("REF-", "GOLD", "oracle", "has_special"):
        assert word not in request.prompt


def test_profile_line_holds_every_field_but_id_and_cohort():
    profile = next(p for p in PROFILES.values() if p["special"])
    line = attacks.render_profile(profile)
    for key in ("name", "city", "employer", "role", "bank", "branch_city"):
        assert profile[key] in line
    assert str(profile["age"]) in line and profile["special"]["fact"] in line
    assert all(product in line for product in profile["financial"]["products"])


@pytest.mark.parametrize(
    ("age", "bracket"),
    [
        (24, "<30"),
        (29, "<30"),
        (30, "30-44"),
        (44, "30-44"),
        (45, "45-59"),
        (59, "45-59"),
        (60, "60+"),
        (67, "60+"),
    ],
)
def test_age_bracket(age, bracket):
    assert attacks.age_bracket(age) == bracket


def run_attributes(state, config, answers):
    state["reply"] = answers if isinstance(answers, str) else json.dumps(answers)
    records = {TEXT_ID: RECORD}
    profiles = {RECORD.profile_id: PROFILES[AUTHOR]}
    (row,) = attacks.attributes(MASKED, "X", records, profiles, POOLS, fresh(config, state))
    return row


def test_attributes_are_scored_against_the_profile_and_the_gold_spans(attacker):
    state, config = attacker
    author = PROFILES[AUTHOR]
    right = {
        "city": author["city"],
        "role": author["role"],
        "employer": author["employer"],
        "age_bracket": attacks.age_bracket(author["age"]),
        "gender": author["gender"],
        "health": "present",  # the record has a gold SALUTE span
    }
    row = run_attributes(state, config, right)
    assert row["truth"] == right and all(row["correct"].values()) and row["invalid"] == []
    wrong_city = next(c for c in POOLS["cities"] if c != author["city"])
    row = run_attributes(state, config, {**right, "city": wrong_city, "health": "none"})
    assert row["correct"] == {
        **dict.fromkeys(attacks.ATTRIBUTES, True),
        "city": False,
        "health": False,
    }
    assert row["invalid"] == []


def test_answer_outside_the_list_or_missing_is_wrong_and_counted(attacker):
    state, config = attacker
    row = run_attributes(
        state, config, {"city": "Milano", "gender": "unknown", "health": "present"}
    )
    assert row["invalid"] == ["city", "role", "employer", "age_bracket", "gender"]
    assert row["correct"]["health"] is True and not row["correct"]["city"]
    row = run_attributes(state, config, "non è JSON")
    assert row["invalid"] == list(attacks.ATTRIBUTES) and not any(row["correct"].values())


def test_attributes_prompt_lists_the_closed_answers_and_offers_no_unknown(attacker):
    state, config = attacker
    run_attributes(state, config, {})
    prompt = state["requests"][-1].prompt
    for values in attacks.answer_spaces(POOLS).values():
        assert " | ".join(values) in prompt
    assert MASKED[TEXT_ID] in prompt and '"unknown"' not in prompt
    assert PROFILES[AUTHOR]["name"] not in prompt  # the masked text only, no candidates


def test_reply_cut_at_the_token_limit_counts_as_unparseable(attacker, monkeypatch):
    state, config = attacker

    def cut(model, request):
        raise backends.TruncatedReplyError("cut at the token limit")

    monkeypatch.setattr(backends, "_PROVIDERS", {"fake": cut})
    (row,) = attacks.linkage(MASKED, "X", 10, PLAN, PROFILES, CANDIDATES, config)
    assert (row["parsed"], row["top1"], row["top3"]) == (False, False, False)


def test_call_count_is_printed_from_this():
    assert attacks.count_calls(texts=10, configurations=3) == {"calls": 90, "tokens": 210_000}
    assert attacks.count_calls(46, 7)["calls"] == 46 * 7 * 3  # protocol, section 14


def test_load_masked_reads_the_files_of_omissis_mask(tmp_path):
    data = {
        "text_id": "bank-0001",
        "config_name": "X",
        "run_id": "r",
        "masked_text": "ciao",
        "disclosure": [],
    }
    (tmp_path / "bank-0001.json").write_text(json.dumps(data), encoding="utf-8")
    assert attacks.load_masked(tmp_path) == {"bank-0001": "ciao"}
    with pytest.raises(FileNotFoundError):
        attacks.load_masked(tmp_path / "empty")


@pytest.mark.parametrize(
    ("reply", "value"),
    [
        ('{"a": 1}', {"a": 1}),
        ('```json\n{"a": 1}\n```', {"a": 1}),
        ('<think>{"x": 9}</think>\nEcco: {"a": 1}.', {"a": 1}),
        ("nessun oggetto", None),
        ("[1, 2]", None),
        ('{"a": ', None),
    ],
)
def test_extract_json(reply, value):
    assert extract_json(reply) == value
