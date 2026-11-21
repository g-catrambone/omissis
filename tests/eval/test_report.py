"""Report: what the chart plots and which contrasts are computed without a judge."""

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
