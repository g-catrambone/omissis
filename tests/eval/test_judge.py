"""The judge and its validation (task 3.7), with a fake provider."""

import csv
import json
from pathlib import Path

import pytest
import yaml

from omissis import backends
from omissis.config import ROLES, load_eval_configs
from omissis.eval import judge, utility
from omissis.eval.datasets import load_texts

REPO = Path(__file__).resolve().parents[2]
RECORDS = load_texts(REPO / "data" / "fixtures")

# --- scores ------------------------------------------------------------------------


def test_scores_are_read_and_mapped_to_0_1():
    reply = '{"correctness": 5, "completeness": 3, "italian": 4, "justification": "ok"}'
    scores = judge.parse_scores(reply)
    assert scores == {"correctness": 5, "completeness": 3, "italian": 4}
    assert judge.t1_score(scores) == pytest.approx((1.0 + 0.5 + 0.75) / 3)
    assert judge.t1_score(dict.fromkeys(judge.CRITERIA, 1)) == 0.0
    assert judge.t1_score(dict.fromkeys(judge.CRITERIA, 5)) == 1.0


@pytest.mark.parametrize(
    "reply",
    [
        "ottima risposta",
        '{"correctness": 5, "completeness": 3}',  # one missing
        '{"correctness": 6, "completeness": 3, "italian": 4}',  # out of range
        '{"correctness": 0, "completeness": 3, "italian": 4}',
        '{"correctness": "5", "completeness": 3, "italian": 4}',  # not an integer
        '{"correctness": 4.5, "completeness": 3, "italian": 4}',
    ],
)
def test_unreadable_judge_reply_is_none(reply):
    assert judge.parse_scores(reply) is None


# --- kappa and acceptance ----------------------------------------------------------


def test_quadratic_kappa_against_hand_computed_values():
    assert judge.quadratic_kappa([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]) == 1.0
    # 1,1,5,5 against 1,5,1,5: observed and chance disagreement are both 8.
    assert judge.quadratic_kappa([1, 1, 5, 5], [1, 5, 1, 5]) == 0.0
    assert judge.quadratic_kappa([1, 5], [5, 1]) == -1.0
    # 4,4,5,5 against 4,5,5,5: observed 1/4; chance (2*3 + 2*1) / 16 = 1/2.
    assert judge.quadratic_kappa([4, 4, 5, 5], [4, 5, 5, 5]) == pytest.approx(0.5)
    assert judge.quadratic_kappa([4, 4, 4], [4, 4, 4]) == 1.0  # one score only
    with pytest.raises(ValueError):
        judge.quadratic_kappa([1], [1, 2])


def test_consensus_ending_in_half_is_rounded_up():
    assert [judge.round_half_up(v) for v in (3.5, 4.5, 4.4, 2.0)] == [4, 5, 4, 2]


def sheet(scores):
    return {f"item-{i:03d}": dict.fromkeys(judge.CRITERIA, s) for i, s in enumerate(scores, 1)}


def test_acceptance_over_all_item_criterion_scores():
    judged = sheet([5, 4, 3, 2])
    result = judge.acceptance(judged, [sheet([5, 4, 3, 2]), sheet([5, 5, 4, 2])])
    # Consensus: 5, 4.5 -> 5, 3.5 -> 4, 2. The judge is within one point everywhere.
    assert result["n"] == 12 and result["within_one"] == 1.0 and result["accepted"] is True
    assert set(result["per_criterion"]) == set(judge.CRITERIA)
    assert result["per_criterion"]["italian"]["n"] == 4
    assert result["consensus_distribution"] == {"1": 0, "2": 3, "3": 0, "4": 3, "5": 6}


def test_judge_far_from_the_raters_is_rejected():
    result = judge.acceptance(sheet([1, 5, 1, 5]), [sheet([5, 1, 5, 1]), sheet([5, 1, 5, 1])])
    assert result["kappa"] == -1.0 and result["within_one"] == 0.0 and result["accepted"] is False


def test_acceptance_by_either_condition():
    # Raters always say 4, the judge 4 or 5: kappa is 0 (no variation), within one is 100%.
    by_closeness = judge.acceptance(sheet([4, 5, 4, 5]), [sheet([4] * 4), sheet([4] * 4)])
    assert by_closeness["kappa"] < judge.KAPPA_MIN and by_closeness["accepted"] is True


def test_acceptance_needs_two_sheets_on_the_same_items():
    with pytest.raises(ValueError):
        judge.acceptance(sheet([4, 4]), [sheet([4, 4])])
    with pytest.raises(ValueError):
        judge.acceptance(sheet([4, 4]), [sheet([4, 4]), sheet([4])])


# --- with a provider ---------------------------------------------------------------


@pytest.fixture
def setup(monkeypatch, tmp_path):
    state = {"judge": '{"correctness": 4, "completeness": 5, "italian": 3}', "judged": []}

    def fake(model, request):
        if model.role == "judge":
            state["judged"].append(request.prompt)
            return state["judge"]
        return f"Bozza per: {request.prompt[-60:]}"

    monkeypatch.setattr(backends, "_PROVIDERS", {"fake": fake})
    models = tmp_path / "models.yaml"
    models.write_text(
        yaml.safe_dump({r: {"provider": "fake", "id": f"{r}-m", "revision": "1"} for r in ROLES}),
        encoding="utf-8",
    )
    overrides = {"models_file": str(models), "cache_dir": str(tmp_path / "cache")}
    return state, load_eval_configs(REPO / "configs" / "eval.yaml", overrides)


def test_judge_sees_email_reference_and_reply_never_the_configuration(setup):
    state, configs = setup
    rows = judge.run(RECORDS[:2], "REF-oracle", configs["REF-oracle"], configs["REF-none"])
    assert [r["scores"] for r in rows] == [{"correctness": 4, "completeness": 5, "italian": 3}] * 2
    assert rows[0]["t1"] == pytest.approx((0.75 + 1.0 + 0.5) / 3) and rows[0]["judge_parsed"]
    prompt = state["judged"][0]
    record = RECORDS[0]
    assert record.text in prompt
    assert utility.t1_reply(record, configs["REF-none"]) in prompt
    assert utility.t1_reply(record, configs["REF-oracle"]) in prompt
    for word in ("REF-", "oracle", "GOLD", "R1", "R2", "detector"):
        assert word not in prompt.replace(record.text, "")


def test_reference_is_not_judged_and_scores_1(setup):
    state, configs = setup
    rows = judge.run(RECORDS[:2], "REF-none", configs["REF-none"], configs["REF-none"])
    assert [(r["t1"], r["scores"]) for r in rows] == [(1.0, None)] * 2 and state["judged"] == []


def test_unreadable_judge_scores_1_on_each_criterion_and_is_counted(setup):
    state, configs = setup
    state["judge"] = "non saprei"
    (row,) = judge.run(RECORDS[:1], "REF-oracle", configs["REF-oracle"], configs["REF-none"])
    assert row["scores"] == dict.fromkeys(judge.CRITERIA, 1)
    assert row["t1"] == 0.0 and row["judge_parsed"] is False


def test_sheets_hide_the_strategy_and_the_key_is_apart(setup, tmp_path):
    _, configs = setup
    rated = judge.validation_configs(configs)
    assert [(c.detector, c.strategy, c.mask_quasi) for c in rated.values()] == [
        ("GOLD", "R1", True),
        ("GOLD", "R2", True),
    ]
    items, key = judge.build_items(RECORDS, rated, configs["REF-none"], seed=1)
    assert len(items) == len(key) == 10
    assert sorted((k["text_id"], k["config"]) for k in key.values()) == sorted(
        (r.id, label) for r in RECORDS for label in ("R1", "R2")
    )
    order = [key[i["item"]]["text_id"] for i in items]
    assert order != sorted(order)  # shuffled
    assert judge.build_items(RECORDS, rated, configs["REF-none"], seed=1)[1] == key

    folder = tmp_path / "sheets"
    judge.write_sheets(items, key, folder, ["GC", "MS"])
    with open(folder / "sheet_GC.csv", encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert list(rows[0]) == list(judge.SHEET_COLUMNS) and len(rows) == 10
    assert all(row[c] == "" for row in rows for c in judge.CRITERIA)
    assert (folder / "sheet_MS.csv").read_text("utf-8") == (folder / "sheet_GC.csv").read_text(
        "utf-8"
    )
    sheet_text = (folder / "sheet_GC.csv").read_text("utf-8")
    assert "fx-" not in sheet_text and "R2" not in sheet_text  # no text id, no strategy
    assert json.loads((folder / "key.json").read_text("utf-8")) == key


def test_filled_sheet_is_read_and_an_empty_score_is_an_error(tmp_path):
    path = tmp_path / "sheet_GC.csv"
    lines = [",".join(judge.SHEET_COLUMNS), "item-001,e,r,x,5,4,3", "item-002,e,r,x,2,2,2"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    assert judge.read_sheet(path)["item-001"] == {"correctness": 5, "completeness": 4, "italian": 3}
    path.write_text("\n".join([*lines, "item-003,e,r,x,5,,3"]) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="every score must be filled"):
        judge.read_sheet(path)
    path.write_text("\n".join([*lines, "item-003,e,r,x,5,7,3"]) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="from 1 to 5"):
        judge.read_sheet(path)
