"""Detection metrics and latency (task 3.9): hand-computed toy cases, fake detectors."""

import json
import shutil
from pathlib import Path

import pytest

from omissis import detect as detect_module
from omissis.config import load_eval_configs
from omissis.contracts import DetectorId, Span, SpanType
from omissis.eval import detection

REPO = Path(__file__).resolve().parents[2]
TEXT = "Lidia Caprioli di Bergamo, 347 215 8890, contabile, € 320,00, asma."
#       0123456789...


def span(value, type, source="GOLD"):
    start = TEXT.index(value)
    return Span(start, start + len(value), value, SpanType(type), 1.0, source)


GOLD = [
    span("Lidia Caprioli", "PERSONA"),
    span("Bergamo", "CITTA"),
    span("347 215 8890", "TELEFONO"),
    span("contabile", "RUOLO"),
    span("asma", "SALUTE"),
]
PREDICTED = [
    span("Caprioli", "PERSONA", "D1"),  # overlaps the name: overlap match, not exact; a leak
    span("Bergamo", "CITTA", "D1"),  # exact
    span("347 215 8890", "CONTO", "D1"),  # same class (direct), another type
    span("€ 320,00", "IMPORTO", "D1"),  # spurious
]


def test_exact_and_overlap_matching():
    assert detection.match(GOLD, PREDICTED, "exact") == [(1, 1)]
    assert sorted(detection.match(GOLD, PREDICTED, "overlap")) == [(0, 0), (1, 1), (2, 2)]


def test_overlap_matching_is_one_to_one_longest_overlap_first():
    gold = [span("Lidia Caprioli", "PERSONA")]
    predicted = [span("Lidia", "PERSONA", "D1"), span("Caprioli", "PERSONA", "D1")]
    assert detection.match(gold, predicted, "overlap") == [(0, 1)]  # 8 characters against 5
    # A quasi-identifier never matches a direct one, even on the same characters.
    assert (
        detection.match([span("Bergamo", "CITTA")], [span("Bergamo", "PERSONA", "D1")], "overlap")
        == []
    )


def test_counts_per_type_of_one_text():
    counts = detection.text_counts(GOLD, PREDICTED)
    assert counts["leak"] is True  # "Lidia " is not covered
    assert counts["exact"]["CITTA"] == {"matched_gold": 1, "missed": 0, "matched_predicted": 1}
    assert counts["exact"]["PERSONA"] == {"matched_gold": 0, "missed": 1, "spurious": 1}
    # Overlap: the phone is found (recall, under TELEFONO) by a span counted under CONTO.
    assert counts["overlap"]["TELEFONO"] == {"matched_gold": 1, "missed": 0}
    assert counts["overlap"]["CONTO"] == {"matched_predicted": 1}
    assert counts["overlap"]["IMPORTO"] == {"spurious": 1}
    assert counts["overlap"]["SALUTE"] == {"matched_gold": 0, "missed": 1}


def row(rows, detector="D1", **wanted):
    (found,) = [
        r
        for r in rows
        if r["detector"] == detector and all(r.get(k) == v for k, v in wanted.items())
    ]
    return found


def test_precision_recall_f1_against_hand_computed_values():
    per = [{"text_id": "t", "detector": "D1"} | detection.text_counts(GOLD, PREDICTED)]
    rows = detection.rows(per, seed=1)
    exact = row(rows, matching="exact", level="all")
    assert (exact["gold"], exact["predicted"]) == (5, 4)
    assert exact["recall"] == pytest.approx(1 / 5) and exact["precision"] == pytest.approx(1 / 4)
    assert exact["f1"] == pytest.approx(2 * 0.2 * 0.25 / 0.45)
    overlap = row(rows, matching="overlap", level="all")
    assert overlap["recall"] == pytest.approx(3 / 5) and overlap["precision"] == pytest.approx(
        3 / 4
    )
    direct = row(rows, matching="overlap", level="class", name="direct")
    assert (direct["recall"], direct["precision"]) == (1.0, 1.0)  # 2 of 2 gold, 2 of 2 predicted
    quasi = row(rows, matching="overlap", level="class", name="quasi")
    assert quasi["recall"] == pytest.approx(1 / 2) and quasi["precision"] == pytest.approx(1 / 2)
    special = row(rows, matching="overlap", level="class", name="special")
    assert special["recall"] == 0.0 and special["precision"] is None and special["f1"] is None
    phone = row(rows, matching="overlap", level="type", name="TELEFONO")
    assert phone["recall"] == 1.0 and phone["precision"] is None  # nothing predicted as TELEFONO
    assert row(rows, level="leak_rate")["leak_rate"] == 1.0


def test_text_with_no_gold_spans_and_detector_with_no_predictions():
    nothing = detection.text_counts([], [])
    assert nothing == {"leak": False, "exact": {}, "overlap": {}}
    silent = detection.text_counts(GOLD, [])
    assert silent["leak"] is True and silent["exact"]["PERSONA"] == {"matched_gold": 0, "missed": 1}
    noisy = detection.text_counts([], PREDICTED)
    assert noisy["leak"] is False and noisy["overlap"]["CITTA"] == {"spurious": 1}
    per = [
        {"text_id": "a", "detector": "D9"} | nothing,
        {"text_id": "b", "detector": "D9"} | silent,
    ]
    rows = detection.rows(per, seed=1)
    total = row(rows, detector="D9", matching="exact", level="all")
    assert total["recall"] == 0.0 and total["precision"] is None and total["predicted"] == 0
    assert row(rows, detector="D9", level="leak_rate")["leak_rate"] == 0.5


def test_leak_is_about_coverage_whatever_the_type():
    name = [span("Lidia Caprioli", "PERSONA")]
    assert not detection.leaks(name, [span("Lidia Caprioli di Bergamo", "CITTA", "D1")])
    assert not detection.leaks(
        name, [span("Lidia", "CITTA", "D1"), span(" Caprioli", "RUOLO", "D1")]
    )
    assert detection.leaks(name, [span("Lidia", "PERSONA", "D1")])
    assert not detection.leaks([span("Bergamo", "CITTA")], [])  # only direct identifiers count


def test_d3_gets_no_leak_rate():
    per = [{"text_id": "t", "detector": "D3"} | detection.text_counts(GOLD, PREDICTED)]
    assert not [r for r in detection.rows(per, seed=1) if r["level"] == "leak_rate"]


# --- files, with fake detectors ----------------------------------------------------


@pytest.fixture
def world(monkeypatch, tmp_path):
    """Two fixtures as a split, and two fake detectors."""
    split = tmp_path / "data" / "dev"
    split.mkdir(parents=True)
    for name in ("fx-bank-01.json", "fx-hr-01.json"):
        shutil.copy(REPO / "data" / "fixtures" / name, split / name)

    def fake_detect(text, detector, config):
        from omissis.detect import rules

        found = rules.find_all(text)
        return found if detector is DetectorId.D0 else found[:1]

    monkeypatch.setattr(detect_module, "detect", fake_detect)
    monkeypatch.setattr(
        detect_module, "supported_detectors", lambda: (DetectorId.D0, DetectorId.D1)
    )
    config = next(iter(load_eval_configs(REPO / "configs" / "eval.yaml").values()))
    return tmp_path, config


def test_run_writes_detected_spans_and_metrics(world):
    tmp, config = world
    path = detection.run("dev", config, results=tmp / "results", data=tmp / "data")
    detected = tmp / "results" / "dev" / "detected"
    assert sorted(p.name for p in detected.iterdir()) == ["D0", "D1"]
    one = json.loads((detected / "D0" / "fx-bank-01.json").read_text(encoding="utf-8"))
    assert set(one) == {"text_id", "detector", "spans", "seconds"}
    assert set(one["spans"][0]) == {
        "start",
        "end",
        "text",
        "type",
        "confidence",
        "source",
        "reason",
    }
    metrics = json.loads(path.read_text(encoding="utf-8"))
    assert metrics["split"] == "dev" and len(metrics["per_text"]) == 4
    assert all("text" not in r for r in metrics["per_text"])
    recall = {
        r["detector"]: r["recall"]
        for r in metrics["rows"]
        if r.get("matching") == "exact" and r["level"] == "class" and r["name"] == "direct"
    }
    assert recall["D0"] > recall["D1"] > 0


def test_metrics_are_recomputed_from_the_files_without_a_detector(world, monkeypatch):
    tmp, config = world
    path = detection.run("dev", config, results=tmp / "results", data=tmp / "data")
    first = json.loads(path.read_text(encoding="utf-8"))

    def no_detector(*args):
        raise AssertionError("no detector may run")

    monkeypatch.setattr(detect_module, "detect", no_detector)
    from omissis.eval.datasets import load_texts

    records = load_texts(tmp / "data" / "dev")
    counts = detection.per_text(records, tmp / "results" / "dev" / "detected")
    assert counts == first["per_text"]
    assert detection.rows(counts, first["seed"]) == first["rows"]


def test_stored_spans_that_do_not_match_the_text_are_refused(world):
    # A file left from an earlier version of a text must not be scored in silence.
    tmp, config = world
    detection.run("dev", config, results=tmp / "results", data=tmp / "data")
    from omissis.eval.datasets import load_texts

    records = load_texts(tmp / "data" / "dev")
    folder = tmp / "results" / "dev" / "detected"
    path = sorted((folder / "D0").glob("*.json"))[0]
    data = json.loads(path.read_text(encoding="utf-8"))
    data["spans"][0]["start"] += 1
    data["spans"][0]["end"] += 1
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(ValueError, match="does not match the text"):
        detection.per_text(records, folder)


def test_files_of_a_detector_not_run_here_are_kept_and_counted(world, monkeypatch):
    tmp, config = world
    detection.run("dev", config, results=tmp / "results", data=tmp / "data")
    monkeypatch.setattr(detect_module, "supported_detectors", lambda: (DetectorId.D0,))
    path = detection.run("dev", config, results=tmp / "results", data=tmp / "data")
    assert (tmp / "results" / "dev" / "detected" / "D1" / "fx-hr-01.json").exists()
    detectors = {r["detector"] for r in json.loads(path.read_text(encoding="utf-8"))["per_text"]}
    assert detectors == {"D0", "D1"}


def test_timing_pass_uses_an_empty_cache_under_scratch(world, monkeypatch):
    tmp, config = world
    seen = []
    original = detect_module.detect

    def recording(text, detector, config):
        seen.append((detector, config.cache_dir, config.backend, text == ""))
        return original(text, detector, config)

    monkeypatch.setattr(detect_module, "detect", recording)
    path = detection.time_detectors("dev", config, results=tmp / "results", data=tmp / "data")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert [r["detector"] for r in data["rows"]] == ["D0", "D1"] and data["machine"]
    assert all(r["texts"] == 2 and 0 <= r["p50"] <= r["p95"] for r in data["rows"])
    assert len(data["per_text"]) == 4
    assert all("scratch" in str(cache) and backend == "cloud" for _, cache, backend, _ in seen)
    assert [warm for d, _, _, warm in seen if d is DetectorId.D0] == [True, False, False]
    assert len({cache for _, cache, _, _ in seen}) == 2  # one cache per detector


def test_percentiles():
    assert detection.percentile([1.0], 95) == 1.0
    assert detection.percentile([1.0, 2.0, 3.0, 4.0, 5.0], 50) == 3.0


@pytest.mark.parametrize("command", ["run", "time"])
def test_held_out_split_is_refused_once_it_was_evaluated(command, tmp_path, monkeypatch, capsys):
    # As the runner: the test texts are read once; a second run is refused, nothing is read.
    metrics = tmp_path / "results" / "test" / "metrics"
    metrics.mkdir(parents=True)
    (metrics / "contrasts.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(detection, "RESULTS", tmp_path / "results")

    def not_reached(*args, **kwargs):
        raise AssertionError("no text may be read")

    for name in ("load_texts", "run", "time_detectors", "load_eval_configs"):
        monkeypatch.setattr(detection, name, not_reached)
    assert detection.main([command, "--split", "test"]) == 2
    err = capsys.readouterr().err
    assert err == "test was already evaluated: a second run is refused.\n"
    assert sorted(p.name for p in (tmp_path / "results" / "test").rglob("*")) == [
        "contrasts.json",
        "metrics",
    ]


@pytest.mark.parametrize("command", ["run", "time"])
def test_held_out_split_works_before_it_is_evaluated(command, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(detection, "RESULTS", tmp_path / "results")
    calls = []
    monkeypatch.setattr(detection, "run", lambda *a, **k: calls.append(("run", a, k)) or Path("r"))
    monkeypatch.setattr(
        detection, "time_detectors", lambda *a, **k: calls.append(("time", a, k)) or Path("t")
    )
    assert detection.main([command, "--split", "test"]) == 0
    assert calls[0][0] == command and calls[0][1][0] == "test"
    assert calls[0][2]["results"] == tmp_path / "results"
