"""The evaluation runner and the report (task 3.10), with fake providers and detectors."""

import csv
import json
import shutil
from pathlib import Path

import pytest
import yaml

from omissis import backends
from omissis import detect as detect_module
from omissis.config import ROLES
from omissis.contracts import DetectorId
from omissis.detect import rules
from omissis.eval import judge, report, run, textgen, utility
from omissis.eval import profiles as planning

REPO = Path(__file__).resolve().parents[2]
FILES = planning.build(REPO / "data" / "profiles")
PLAN = FILES["plan.json"]
PROFILES = {p["id"]: p for p in FILES["profiles.json"]}
TEXTS = list(PLAN)[:6]
EXTRA = [
    {"name": "D4+R1", "detector": "D0", "strategy": "R1", "mask_quasi": True},
    {"name": "D1+R1", "detector": "D0", "strategy": "R1", "mask_quasi": False},
    {"name": "D4+R2", "detector": "D0", "strategy": "R2", "mask_quasi": True},
]


def tagged(profile):
    fact = ""
    if profile["special"]:
        fact = f" Ho [[{profile['special']['category']}|{profile['special']['fact']}]]."
    return (
        f"Sono [[PERSONA|{profile['name']}]], [[RUOLO|{profile['role']}]] a "
        f"[[CITTA|{profile['city']}]]. Scrivetemi a [[EMAIL|nome.cognome@example.com]] entro il "
        f"[[DATA|15 dicembre 2026]]: la rata è di [[IMPORTO|€ 100,00]].{fact}\n"
    )


def fake(model, request):
    if model.role == "judge":
        return '{"correctness": 4, "completeness": 4, "italian": 5, "justification": "ok"}'
    if model.role == "attacker":
        return '{"ranking": [1, 2, 3]}' if "ranking" in request.prompt else '{"gender": "F"}'
    if request.prompt.startswith(utility.T3_TASK):
        return json.dumps(
            {
                "intent": "x",
                "requested_action": "x",
                "amounts": ["€ 100,00"],
                "dates": ["15 dicembre 2026"],
                "deadline": None,
            }
        )
    return request.prompt  # the reply draft: an echo


@pytest.fixture
def world(monkeypatch, tmp_path):
    data = tmp_path / "data"
    (data / "dev").mkdir(parents=True)
    shutil.copytree(REPO / "data" / "profiles", data / "profiles")
    for text_id in TEXTS:
        entry = PLAN[text_id]
        text, spans = textgen.parse_tagged(tagged(PROFILES[entry["profile_id"]]))
        textgen.save(data / "dev", textgen.to_json(text_id, entry, text, spans, None))

    monkeypatch.setattr(backends, "_PROVIDERS", {"fake": fake})
    monkeypatch.setattr(detect_module, "supported_detectors", lambda: (DetectorId.D0,))
    monkeypatch.setattr(detect_module, "detect", lambda text, d, c: rules.find_all(text))
    models = tmp_path / "models.yaml"
    models.write_text(
        yaml.safe_dump({r: {"provider": "fake", "id": f"{r}-m", "revision": "1"} for r in ROLES}),
        encoding="utf-8",
    )
    settings = yaml.safe_load((REPO / "configs" / "eval.yaml").read_text(encoding="utf-8"))
    settings["base"].update(models_file=str(models), cache_dir=str(tmp_path / "cache"))
    settings["configurations"] += EXTRA
    config = tmp_path / "eval.yaml"
    config.write_text(yaml.safe_dump(settings), encoding="utf-8")

    def evaluate(split="dev", **kw):
        kw.setdefault("confirm", False)
        return run.evaluate(split, config, tmp_path / "results", data, **kw)

    return tmp_path, evaluate


def metrics(tmp, name, split="dev"):
    return json.loads((tmp / "results" / split / "metrics" / f"{name}.json").read_text("utf-8"))


def test_run_writes_every_metrics_file_scorecard_and_masked_texts(world, capsys):
    tmp, evaluate = world
    assert evaluate() == 0
    assert "6 texts x 6 configurations: 210 calls" in capsys.readouterr().out
    for name in (
        "linkage",
        "attributes",
        "utility",
        "restoration",
        "contrasts",
        "cost",
        "detection",
    ):
        data = metrics(tmp, name)
        runs = 1 if name == "detection" else 6  # detection does not depend on the run
        assert data["split"] == "dev" and len(data["generated_from"]) == runs, name
        assert all("text" not in row for row in data["per_text"]), name
    names = ["REF-none", "REF-oracle-direct", "REF-oracle", "D4+R1", "D1+R1", "D4+R2"]
    assert [r["config"] for r in metrics(tmp, "utility")["rows"]] == names
    assert len(metrics(tmp, "linkage")["per_text"]) == 6 * 6 * 2
    assert sorted(p.name for p in (tmp / "results" / "dev" / "masked").iterdir()) == sorted(names)
    card = (tmp / "results" / "dev" / "scorecard.md").read_text(encoding="utf-8")
    for heading in ("# Scorecard — dev", "## Detectors", "## Primary contrasts", "`D4+R2`"):
        assert heading in card


def test_reference_is_not_judged_and_utility_is_the_mean_of_t3_and_t1(world):
    tmp, evaluate = world
    evaluate()
    rows = {r["config"]: r for r in metrics(tmp, "utility")["rows"]}
    assert rows["REF-none"]["t1"] == 1.0
    judged = (0.75 + 0.75 + 1.0) / 3  # scores 4, 4, 5
    assert rows["REF-oracle"]["t1"] == pytest.approx(judged)
    # T3: amounts and dates right, intent and action wrong; the deadline is null in the gold.
    assert rows["REF-oracle"]["t3"] == pytest.approx(0.6)
    assert rows["REF-oracle"]["utility"] == pytest.approx((0.6 + judged) / 2)
    restoration = {r["config"]: r for r in metrics(tmp, "restoration")["rows"]}
    assert restoration["REF-oracle"]["full_restoration"] == 1.0
    assert restoration["D4+R2"]["restored_fakes_per_reply"] > 0
    assert restoration["D4+R1"]["restored_fakes_per_reply"] == 0


def test_contrasts_are_computed_for_the_configurations_present(world):
    tmp, evaluate = world
    evaluate()
    rows = metrics(tmp, "contrasts")["rows"]
    assert [(r["a"], r["b"], r["metric"]) for r in rows] == list(report.CONTRASTS)
    assert [r["test"] for r in rows] == ["mcnemar_exact", "paired_bootstrap", "mcnemar_exact"]
    assert all(0 <= r["p"] <= r["p_holm"] <= 1 and r["texts"] == 6 for r in rows)
    assert all(isinstance(r["finding"], bool) for r in rows)


def test_rows_are_rebuilt_from_per_text_alone(world, monkeypatch):
    tmp, evaluate = world
    evaluate()
    names = ("linkage", "attributes", "utility", "restoration", "contrasts", "detection")
    first = {n: metrics(tmp, n) for n in names}
    card = (tmp / "results" / "dev" / "scorecard.md").read_text(encoding="utf-8")
    folder = tmp / "results" / "dev" / "metrics"
    for name in names:
        report.write(folder, name, first[name] | {"rows": []})
    monkeypatch.setattr(backends, "_PROVIDERS", {})  # no model
    monkeypatch.setattr(detect_module, "detect", None)  # no detector
    shutil.rmtree(tmp / "data")  # no text
    report.rebuild("dev", tmp / "results")
    assert {n: metrics(tmp, n) for n in names} == first
    assert (tmp / "results" / "dev" / "scorecard.md").read_text(encoding="utf-8") == card


def test_second_launch_makes_no_new_call(world, monkeypatch):
    tmp, evaluate = world
    evaluate()
    first = {n: metrics(tmp, n) for n in ("linkage", "utility")}
    monkeypatch.setattr(backends, "_PROVIDERS", {})
    assert evaluate(backend="replay") == 0
    assert {n: metrics(tmp, n) for n in ("linkage", "utility")} == first


def test_configuration_with_a_detector_that_cannot_run_stops_before_any_call(
    world, monkeypatch, capsys
):
    tmp, evaluate = world
    monkeypatch.setattr(detect_module, "supported_detectors", lambda: ())
    assert evaluate() == 2
    assert "D4+R1" in capsys.readouterr().err
    assert not (tmp / "results").exists() and not (tmp / "cache").exists()


def test_run_asks_first(world, monkeypatch):
    tmp, evaluate = world
    monkeypatch.setattr("builtins.input", lambda prompt: "n")
    assert evaluate(confirm=True) == 1 and not (tmp / "results").exists()


def test_cache_miss_stops_the_command_with_status_2(world, monkeypatch, capsys):
    tmp, _ = world
    monkeypatch.setattr(
        run, "evaluate", lambda *a, **k: (_ for _ in ()).throw(backends.CacheMissError("x"))
    )
    assert run.main(["--split", "dev", "--yes"]) == 2
    assert "evaluation stopped" in capsys.readouterr().err


def test_held_out_split_is_evaluated_once_and_every_launch_is_logged(world, monkeypatch, capsys):
    tmp, evaluate = world
    monkeypatch.setattr(run, "HELD_OUT", "holdout")
    (tmp / "data" / "dev").rename(tmp / "data" / "holdout")
    assert evaluate("holdout") == 0
    assert evaluate("holdout") == 2
    assert "second run is refused" in capsys.readouterr().err
    log = (tmp / "data" / "holdout_access.log").read_text(encoding="utf-8").splitlines()
    assert len(log) == 2 and all(line.endswith("launch") for line in log)


def reject_judge(tmp):
    report.write(tmp / "results" / "dev" / "metrics", "judge_validation", {"accepted": False})


def test_rejected_judge_leaves_t1_unscored_and_utility_on_t3(world):
    tmp, evaluate = world
    reject_judge(tmp)
    evaluate()
    rows = {r["config"]: r for r in metrics(tmp, "utility")["rows"]}
    assert rows["REF-none"]["t1"] == 1.0
    assert rows["REF-oracle"]["t1"] is None and rows["REF-oracle"]["utility"] == pytest.approx(0.6)
    assert "—" in (tmp / "results" / "dev" / "scorecard.md").read_text(encoding="utf-8")


def test_rejected_judge_on_the_held_out_split_waits_for_the_human_sheets(
    world, monkeypatch, capsys
):
    tmp, evaluate = world
    reject_judge(tmp)
    monkeypatch.setattr(run, "HELD_OUT", "holdout")
    (tmp / "data" / "dev").rename(tmp / "data" / "holdout")
    assert evaluate("holdout") == 0
    out = tmp / "results" / "holdout"
    assert "not complete yet" in capsys.readouterr().out
    assert not (out / "metrics" / "contrasts.json").exists()  # the run does not count yet
    sheets = sorted((out / "judge_fallback").glob("sheet_*.csv"))
    assert len(sheets) == 3

    assert evaluate("holdout") == 0  # sheets still empty: still waiting, not refused
    assert not (out / "metrics" / "contrasts.json").exists()

    for path in sheets:  # the three members fill their sheets
        with open(path, encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh))
        with open(path, "w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=judge.SHEET_COLUMNS)
            writer.writeheader()
            writer.writerows({**row, **dict.fromkeys(judge.CRITERIA, "5")} for row in rows)
    assert evaluate("holdout") == 0
    rows = {r["config"]: r for r in metrics(tmp, "utility", "holdout")["rows"]}
    assert rows["D4+R1"]["t1"] == 1.0 and rows["D4+R2"]["t1"] is None
    assert (out / "metrics" / "contrasts.json").exists()
    assert evaluate("holdout") == 2  # now it counts as run
