"""Report: what the chart plots and which contrasts are computed without a judge."""

import pytest

from omissis.eval import profiles as planning
from omissis.eval import report


def per_text(config, t3, t1):
    return [
        {
            "text_id": f"t{i}",
            "config": config,
            "t3": t3,
            "t3_parsed": True,
            "judge_parsed": True,
            "t1": t1,
            "utility": t3 if t1 is None else (t3 + t1) / 2,
        }
        for i in range(6)
    ]


def test_chart_plots_t3_for_every_configuration_when_one_has_no_t1():
    # Protocol, section 9: with the judge rejected the chart uses T3 for every configuration.
    judged = report.utility_rows(per_text("REF-none", 0.4, 1.0) + per_text("D4+R1", 0.4, 0.5), 1)
    assert report.chart_metric(judged) == "utility"
    rejected = report.utility_rows(per_text("REF-none", 0.4, 1.0) + per_text("D4+R1", 0.4, None), 1)
    assert report.chart_metric(rejected) == "t3"


def test_chart_names_the_configurations_in_a_legend_not_beside_the_points():
    # On the test split four configurations sit in one corner: names written beside
    # the points covered each other (docs/decisions.md, 22 Nov).
    pytest.importorskip("matplotlib")
    names = ("REF-none", "D1+R1", "D4+R1")
    attack = [
        {"config": c, "n": n, "text_id": f"t{i}", "parsed": True, "top1": i < 3, "top3": True}
        for c in names
        for n in (10, 25)
        for i in range(6)
    ]
    useful = [row for c in names for row in per_text(c, 0.4, None)]
    figure = report.draw(
        {
            "linkage": {"rows": report.attacks.linkage_rows(attack, 1)},
            "utility": {"rows": report.utility_rows(useful, 1)},
        }
    )
    (axes,) = figure.axes
    assert [text.get_text() for text in axes.get_legend().get_texts()] == list(names)
    assert [text.get_text() for text in axes.texts] == ["chance"]
    # One marker per configuration: the chart is read without colour too.
    assert [c.lines[0].get_marker() for c in axes.containers] == list(report.MARKERS[:3])


def test_utility_contrast_needs_t1_on_both_sides():
    # T3 alone against the mean of T3 and T1 is not one scale: no contrast, no finding.
    rows = per_text("REF-none", 0.4, 1.0) + per_text("D4+R1", 0.4, None)
    assert [r["metric"] for r in report.contrast_rows([], rows, [], 1)] == []
    rows = per_text("REF-none", 0.4, 1.0) + per_text("D4+R1", 0.4, 0.5)
    (contrast,) = report.contrast_rows([], rows, [], 1)
    assert contrast["metric"] == "utility" and contrast["difference"] < 0


def test_no_scorecard_when_there_is_no_row(tmp_path):
    # The pilot has the two attacks alone: no table of the scorecard has a row.
    folder = tmp_path / "pilot" / "metrics"
    folder.mkdir(parents=True)
    for name in ("linkage", "attributes"):
        source = report.RESULTS / "pilot" / "metrics" / f"{name}.json"
        (folder / f"{name}.json").write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    metrics = report.rebuild("pilot", tmp_path)
    assert metrics["linkage"]["rows"] and metrics["attributes"]["rows"]
    assert report.scorecard("pilot", metrics) is None
    assert not (tmp_path / "pilot" / "scorecard.md").exists()


def test_scorecard_has_no_utility_without_t1_and_counts_the_replies_not_parsed():
    # Protocol, sections 7 and 8: T3 alone is not the utility score, and an attacker's
    # reply that cannot be read (one cut at the token limit) is a miss counted apart.
    names, ids = ("REF-none", "D4+R1"), [f"t{i}" for i in range(6)]
    cut = ("D4+R1", 25, "t0")
    attack = [
        {"config": c, "n": n, "text_id": t, "parsed": (c, n, t) != cut}
        | dict.fromkeys(("top1", "top3"), (c, n, t) != cut)
        for c in names
        for n in (10, 25)
        for t in ids
    ]
    answers = dict.fromkeys(report.attacks.ATTRIBUTES, "x")
    guessed = [
        {"config": c, "text_id": t, "invalid": [], "truth": answers}
        | {"correct": dict.fromkeys(answers, True)}
        for c in names
        for t in ids
    ]
    restored = [
        {"config": c, "text_id": t, "fully_restored": True, "outcomes": {}, "restored_fakes": 0}
        for c in names
        for t in ids
    ]
    useful = per_text("REF-none", 0.4, 1.0) + per_text("D4+R1", 0.4, None)
    card = report.scorecard(
        "dev",
        {
            "linkage": {"per_text": attack, "rows": report.attacks.linkage_rows(attack, 1)},
            "attributes": {"rows": report.attacks.attribute_rows(guessed, 1)},
            "utility": {"rows": report.utility_rows(useful, 1)},
            "restoration": {"rows": report.restoration_rows(restored, 1)},
            "detection": None,
            "contrasts": None,
            "latency": None,
        },
    )
    table = [
        [cell.strip() for cell in line.strip("|").split("|")]
        for line in card.splitlines()
        if line.startswith(("| Configuration", "| `"))
    ]
    rows = {cells[0]: dict(zip(table[0], cells, strict=True)) for cells in table[1:]}
    assert rows["`REF-none`"]["not parsed"] == "0, 0"
    assert rows["`D4+R1`"]["not parsed"] == "0, 1"
    assert rows["`REF-none`"]["utility"] == "0.70 (no variation)"
    assert rows["`D4+R1`"]["T3"] == "0.40 (no variation)"
    assert rows["`D4+R1`"]["T1"] == rows["`D4+R1`"]["utility"] == "—"


def test_not_parsed_counts_the_replies_and_refuses_a_split_with_no_results(tmp_path, capsys):
    # Protocol, section 7: a split is launched again while this count is above zero.
    folder = tmp_path / "dev" / "metrics"
    answers = dict.fromkeys(report.attacks.ATTRIBUTES, "x")
    rows = [{"parsed": True}, {"parsed": False}, {"parsed": False}]
    report.write(folder, "linkage", {"per_text": rows})
    guessed = [{"invalid": []}, {"invalid": ["city"]}, {"invalid": list(answers)}]
    report.write(folder, "attributes", {"per_text": guessed})
    before = {p.name: p.read_bytes() for p in folder.iterdir()}
    assert report.not_parsed("dev", tmp_path) == {"linkage": 2, "attributes": 1}
    assert {p.name: p.read_bytes() for p in folder.iterdir()} == before  # nothing is written
    # The command, on the committed pilot and on a split that has no results yet.
    assert report.main(["--split", "pilot", "--not-parsed"]) == 0
    assert "pilot: replies of the attacker not parsed: linkage" in capsys.readouterr().out
    assert report.main(["--split", "no-such-split", "--not-parsed"]) == 2


def linkage(text_ids, hit):
    return [
        {"config": "D4+R1", "n": n, "text_id": t, "parsed": True, "top1": hit(t), "top3": True}
        for n in (10, 25)
        for t in text_ids
    ]


def test_loan_mismatch_is_what_the_rule_of_the_decision_gives():
    # docs/decisions.md, 21 Nov: a text about a loan or a mortgage whose author holds
    # neither in the profile. The ids are written in the report so that it reads no plan.
    files = planning.build()
    holds = {p["id"]: set(p["financial"]["products"]) for p in files["profiles.json"]}
    by_rule = {
        text_id
        for text_id, entry in files["plan.json"].items()
        if entry["scenario"] in ("mortgage_suspension", "loan_early_repayment")
        and not holds[entry["profile_id"]] & {"mutuo prima casa", "prestito personale"}
    }
    assert by_rule == report.LOAN_MISMATCH
    assert len(by_rule) == 7


def test_linkage_control_rows_leave_out_the_loan_mismatch_texts():
    # The attacker misses the two mismatch texts and no other: 4 of 6, and 4 of 4 without.
    left_out = sorted(report.LOAN_MISMATCH)[:2]
    per_text = linkage(
        [*left_out, "bank-0004", "bank-0006", "hr-0001", "hr-0003"], hit=lambda t: t not in left_out
    )
    control = report.linkage_control(per_text, seed=1)
    assert control["control_excluded"] == left_out
    assert [(r["n"], r["texts"], r["top1"]) for r in control["control_rows"]] == [
        (10, 4, 1.0),
        (25, 4, 1.0),
    ]
    (full,) = [r for r in report.attacks.linkage_rows(per_text, 1) if r["n"] == 25]
    assert full["top1"] == 4 / 6


def test_no_linkage_control_rows_when_the_split_holds_no_mismatch_text():
    per_text = linkage(["bank-0004", "hr-0001"], hit=lambda t: True)
    assert report.linkage_control(per_text, seed=1) == {"control_excluded": [], "control_rows": []}
    assert report.control_table({"rows": [], "control_excluded": [], "control_rows": []}) == []
    assert report.control_table({"rows": []}) == []  # a file written before the control rows


def test_control_table_sets_the_row_without_the_texts_beside_the_one_with_all():
    left_out = sorted(report.LOAN_MISMATCH)[:2]
    per_text = linkage(
        [*left_out, "bank-0004", "bank-0006", "hr-0001", "hr-0003"], hit=lambda t: t not in left_out
    )
    data = {"rows": report.attacks.linkage_rows(per_text, 1)} | report.linkage_control(per_text, 1)
    table = report.control_table(data)
    assert "2 texts" in table[2]
    (row,) = [line for line in table if line.startswith("| `D4+R1`")]
    assert row == "| `D4+R1` | 4 | 1.00 (no variation) | 0.67 |"


def test_rebuild_writes_the_control_rows_of_the_pilot(tmp_path):
    folder = tmp_path / "pilot" / "metrics"
    folder.mkdir(parents=True)
    source = report.RESULTS / "pilot" / "metrics" / "linkage.json"
    (folder / "linkage.json").write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    data = report.rebuild("pilot", tmp_path)["linkage"]
    assert data["control_excluded"] == ["bank-0002", "bank-0024"]
    assert {r["texts"] for r in data["control_rows"]} == {8}
    assert report.read(folder, "linkage") == data
