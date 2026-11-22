"""The command line: what may be written to a committed cache, empty texts, the help."""

import json
import re
from pathlib import Path

import pytest
import yaml

from omissis import cli

REPO = Path(__file__).resolve().parents[2]
FIXTURE = REPO / "data" / "fixtures" / "fx-bank-01.json"


def write_config(tmp_path, cache_dir, backend="cloud"):
    data = yaml.safe_load((REPO / "configs" / "skeleton.yaml").read_text(encoding="utf-8"))
    data.update(
        backend=backend,
        cache_dir=str(cache_dir),
        models_file=str(REPO / "configs" / "models.echo.yaml"),
    )
    path = tmp_path / "config.yaml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return str(path)


def write_record(folder, text=None, name="fx-bank-01"):
    """A copy of a fixture (with another text when given) in `folder`."""
    folder.mkdir(parents=True, exist_ok=True)
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    data["id"] = name
    if text is not None:
        data["text"], data["spans"] = text, []
    target = folder / f"{name}.json"
    target.write_text(json.dumps(data), encoding="utf-8")
    return target


@pytest.fixture
def fake_repo(tmp_path, monkeypatch):
    """A repository root in `tmp_path`, so that a write to its `results/cache` is harmless."""
    root = tmp_path / "repo"
    (root / "results" / "cache").mkdir(parents=True)
    (root / "data" / "fixtures").mkdir(parents=True)
    monkeypatch.setattr(cli, "ROOT", root)
    return root


# --- _is_committed -----------------------------------------------------------------


def test_committed_cache_is_judged_from_the_repository_not_the_current_directory(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    assert cli._is_committed(REPO / "results" / "cache")
    assert cli._is_committed(REPO / "results" / "dev" / "x")
    assert not cli._is_committed(REPO / "results" / "scratch" / "cache")
    assert not cli._is_committed(tmp_path / "cache")
    assert not cli._is_committed(REPO / "data")


# --- what may be written to a committed cache --------------------------------------


def test_json_record_outside_data_is_refused_with_a_committed_cache(fake_repo, tmp_path, capsys):
    record = write_record(tmp_path / "records")
    config = write_config(tmp_path, fake_repo / "results" / "cache")
    assert cli.main(["run", "--config", config, "--input", str(record)]) == 2
    err = capsys.readouterr().err
    assert "results/scratch/" in err and err.count("\n") == 1
    assert list((fake_repo / "results" / "cache").iterdir()) == []


def test_batch_folder_outside_data_is_refused_with_a_committed_cache(fake_repo, tmp_path, capsys):
    record = write_record(tmp_path / "records")
    config = write_config(tmp_path, fake_repo / "results" / "cache")
    assert cli.main(["batch", "--config", config, "--input-dir", str(record.parent)]) == 2
    assert "results/scratch/" in capsys.readouterr().err
    assert list((fake_repo / "results" / "cache").iterdir()) == []


def test_batch_refuses_a_link_inside_data_that_points_outside(fake_repo, tmp_path, capsys):
    outside = write_record(tmp_path / "records")
    (fake_repo / "data" / "fixtures" / "fx-bank-09.json").symlink_to(outside)
    config = write_config(tmp_path, fake_repo / "results" / "cache")
    folder = str(fake_repo / "data" / "fixtures")
    assert cli.main(["batch", "--config", config, "--input-dir", folder]) == 2
    assert "results/scratch/" in capsys.readouterr().err
    assert list((fake_repo / "results" / "cache").iterdir()) == []


def test_mask_refuses_records_outside_data_with_a_committed_cache(fake_repo, tmp_path, capsys):
    record = write_record(tmp_path / "records")
    base = yaml.safe_load(Path(write_config(tmp_path, fake_repo / "results" / "cache")).read_text())
    named = {key: base.pop(key) for key in ("detector", "strategy", "mask_quasi")}
    eval_config = tmp_path / "eval.yaml"
    eval_config.write_text(
        yaml.safe_dump({"base": base, "configurations": [{"name": "one", **named}]}),
        encoding="utf-8",
    )
    out = tmp_path / "masked"
    args = ["mask", "--eval-config", str(eval_config), "--output", str(out)]
    assert cli.main([*args, "--input-dir", str(record.parent)]) == 2
    assert "results/scratch/" in capsys.readouterr().err
    assert not out.exists()
    inside = write_record(fake_repo / "data" / "fixtures")
    assert cli.main([*args, "--input-dir", str(inside.parent)]) == 0
    assert (out / "one" / "fx-bank-01.json").exists()


def test_records_under_data_are_accepted_with_a_committed_cache(fake_repo, tmp_path, capsys):
    record = write_record(fake_repo / "data" / "fixtures")
    config = write_config(tmp_path, fake_repo / "results" / "cache")
    assert cli.main(["run", "--config", config, "--input", str(record)]) == 0
    assert cli.main(["batch", "--config", config, "--input-dir", str(record.parent)]) == 0
    assert "fully restored: True" in capsys.readouterr().out


def test_cache_that_is_not_committed_accepts_a_record_anywhere(fake_repo, tmp_path, capsys):
    record = write_record(tmp_path / "records")
    for cache in (tmp_path / "cache", fake_repo / "results" / "scratch" / "cache"):
        config = write_config(tmp_path, cache)
        assert cli.main(["run", "--config", config, "--input", str(record)]) == 0
        assert cli.main(["batch", "--config", config, "--input-dir", str(record.parent)]) == 0
    assert "fully restored: True" in capsys.readouterr().out


# --- empty text ---------------------------------------------------------------------


@pytest.mark.parametrize("content", ["", "  \n\t\n"])
def test_run_refuses_an_empty_text_before_any_call(tmp_path, capsys, content):
    empty = tmp_path / "empty.txt"
    empty.write_text(content, encoding="utf-8")
    config = write_config(tmp_path, tmp_path / "cache")
    assert cli.main(["run", "--config", config, "--input", str(empty)]) == 2
    captured = capsys.readouterr()
    assert captured.out == "" and captured.err.count("\n") == 1 and "empty" in captured.err
    assert not list((tmp_path / "cache").glob("*")) if (tmp_path / "cache").exists() else True


def test_batch_refuses_an_empty_text_before_any_call(tmp_path, capsys):
    folder = tmp_path / "records"
    write_record(folder, name="fx-bank-01")  # a good text first: nothing is sent for it
    write_record(folder, text="  ", name="fx-bank-02")
    config = write_config(tmp_path, tmp_path / "cache")
    assert cli.main(["batch", "--config", config, "--input-dir", str(folder)]) == 2
    captured = capsys.readouterr()
    assert captured.out == "" and "empty" in captured.err and captured.err.count("\n") == 1
    assert not list((tmp_path / "cache").glob("*")) if (tmp_path / "cache").exists() else True


# --- help ---------------------------------------------------------------------------


def test_help_description_is_a_whole_sentence(capsys):
    with pytest.raises(SystemExit):
        cli.main(["--help"])
    out = capsys.readouterr().out
    description = re.search(r"\n\n(.+?)\n\n", out, re.S).group(1)
    assert description.strip().endswith(".") and "run" in description and "batch" in description
