"""Review assignment, agreement and the split (task 3.5), all in a temporary folder."""

import hashlib
import json
import shutil
from collections import Counter
from pathlib import Path

import pytest

from omissis.eval import profiles as planning
from omissis.eval import review, textgen
from omissis.eval import split as splitting
from omissis.eval.datasets import load_texts

REPO = Path(__file__).resolve().parents[2]
FILES = planning.build(REPO / "data" / "profiles")
PLAN = FILES["plan.json"]
PROFILES = {p["id"]: p for p in FILES["profiles.json"]}

# --- assignment --------------------------------------------------------------------


def test_each_member_reviews_22_texts():
    table = review.assign(PLAN)
    assert set(table) == set(PLAN)
    assert Counter(row["reviewer"] for row in table.values()) == dict.fromkeys(review.MEMBERS, 22)
    assert review.assign(PLAN) == table and review.assign(PLAN, seed=1) != table


def test_thirteen_texts_get_a_second_annotator_who_is_not_the_reviewer():
    table = review.assign(PLAN)
    double = {t: row for t, row in table.items() if "second" in row}
    assert len(double) == 13
    assert not any(PLAN[t]["pilot"] for t in double)
    for row in double.values():
        assert row["second"] in review.MEMBERS and row["second"] != row["reviewer"]
    eligible = [t for t, e in PLAN.items() if not e["pilot"]]
    bank = sum(t.startswith("bank-") for t in eligible)
    domains = Counter(t.split("-")[0] for t in double)
    assert domains["bank"] == round(13 * bank / len(eligible)) and sum(domains.values()) == 13


def test_reviewers_file_lists_every_text():
    text = review.reviewers_md(review.assign(PLAN))
    assert text.count("\n| ") == 66 + 1 and "| Text | Reviewer | Second annotator |" in text


# --- agreement ---------------------------------------------------------------------


def spans(tagged):
    return textgen.parse_tagged(tagged)[1]


FIRST = spans(
    "[[PERSONA|Lidia Caprioli]] di [[CITTA|Bergamo]], [[RUOLO|contabile]], [[SALUTE|asma]]."
)
SECOND = spans("[[PERSONA|Lidia]] Caprioli di [[CITTA|Bergamo]], contabile, [[RUOLO|asma]].")


def test_agreement_against_hand_computed_values():
    result = review.agreement({"t": (FIRST, SECOND)})
    exact, overlap, kappa = result["rows"]
    # Exact: only Bergamo. Overlap (same class): Lidia and Bergamo; asma differs in class.
    assert (exact["matched"], exact["first"], exact["second"]) == (1, 4, 3)
    assert exact["f1"] == pytest.approx(2 / 7) and overlap["f1"] == pytest.approx(4 / 7)
    # Pairs whatever the class: direct-direct, quasi-quasi, special-quasi. Observed 2/3;
    # chance (1*1 + 1*2 + 1*0) / 9 = 1/3; kappa = (2/3 - 1/3) / (2/3) = 0.5.
    assert kappa["pairs"] == 3 and kappa["kappa"] == pytest.approx(0.5)
    assert sorted(map(tuple, result["per_text"][0]["class_pairs"])) == [
        ("direct", "direct"),
        ("quasi", "quasi"),
        ("special", "quasi"),
    ]


def test_identical_annotations_agree_fully_and_empty_ones_give_none():
    same = review.agreement({"t": (FIRST, FIRST)})
    assert [r.get("f1", r.get("kappa")) for r in same["rows"]] == [1.0, 1.0, 1.0]
    empty = review.agreement({"t": ([], [])})
    assert [r.get("f1", r.get("kappa")) for r in empty["rows"]] == [None, None, None]


def test_cohen_kappa_textbook_cases():
    assert review.cohen_kappa([("a", "a"), ("b", "b")]) == 1.0
    assert review.cohen_kappa([("a", "b"), ("b", "a")]) == -1.0
    assert review.cohen_kappa([("a", "a"), ("a", "a")]) == 1.0  # one label only
    assert review.cohen_kappa([]) is None


# --- split -------------------------------------------------------------------------


@pytest.fixture
def pool(tmp_path):
    """The 66 planned texts, small and reviewed, in a temporary pool."""
    folder = tmp_path / "pool"
    folder.mkdir()
    for text_id, entry in PLAN.items():
        profile = PROFILES[entry["profile_id"]]
        special = ""
        if entry["has_special"]:
            special = f" [[{profile['special']['category']}|{profile['special']['fact']}]]"
        tagged = f"Sono [[PERSONA|{profile['name']}]] di [[CITTA|{profile['city']}]].{special}\n"
        text, found = textgen.parse_tagged(tagged)
        data = textgen.to_json(text_id, entry, text, found, None) | {"reviewed_by": "MS"}
        textgen.save(folder, data)
    return tmp_path


def digests(folder):
    return {p.stem: hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.glob("*.json")}


def test_split_gives_20_dev_with_the_pilot_and_46_held_out(pool):
    before = digests(pool / "pool")
    manifest = splitting.split(pool / "pool", pool, PLAN, seed=7)
    assert (len(manifest["dev"]), len(manifest["test"])) == (20, 46)
    assert set(manifest["dev"]) >= {t for t, e in PLAN.items() if e["pilot"]}
    assert not set(manifest["dev"]) & set(manifest["test"])
    assert sorted(digests(pool / "dev")) == manifest["dev"]
    assert sorted(digests(pool / "test")) == sorted(manifest["test"])
    assert list((pool / "pool").glob("*.json")) == []  # the pool is emptied
    assert json.loads((pool / "split.json").read_text(encoding="utf-8")) == manifest
    assert manifest["sha256"] == before


def test_split_is_stratified_and_deterministic(pool):
    records = load_texts(pool / "pool")
    dev = splitting.choose_dev(records, PLAN, seed=7)
    assert dev == splitting.choose_dev(records, PLAN, seed=7)
    assert dev != splitting.choose_dev(records, PLAN, seed=8)
    by_id = {r.id: r for r in records}
    drawn = [t for t in dev if not PLAN[t]["pilot"]]
    rest = [r for r in records if not PLAN[r.id]["pilot"]]
    for key in {(r.domain, r.has_special) for r in rest}:
        share = 10 * sum((r.domain, r.has_special) == key for r in rest) / len(rest)
        got = sum((by_id[t].domain, by_id[t].has_special) == key for t in drawn)
        assert abs(got - share) < 1, key


def test_split_refuses_unreviewed_texts_a_short_pool_and_a_second_run(pool):
    path = pool / "pool" / "bank-0001.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    del data["reviewed_by"]
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(RuntimeError, match="without reviewed_by.*bank-0001"):
        splitting.split(pool / "pool", pool, PLAN, seed=7)
    assert not (pool / "dev").exists() and not (pool / "split.json").exists()

    path.unlink()
    with pytest.raises(RuntimeError, match="exactly the 66 planned texts"):
        splitting.split(pool / "pool", pool, PLAN, seed=7)

    data["reviewed_by"] = "MS"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    splitting.split(pool / "pool", pool, PLAN, seed=7)
    with pytest.raises(RuntimeError, match="made once"):
        splitting.split(pool / "pool", pool, PLAN, seed=7)


def test_split_that_fails_half_way_leaves_the_pool_whole_and_can_run_again(pool, monkeypatch):
    before = digests(pool / "pool")
    calls = []

    def fails_on_the_30th(*args, **kwargs):
        calls.append(args)
        if len(calls) >= 30:
            raise OSError("disk full")
        raise AssertionError("the real function is called below")

    # Whatever the split uses to put a file in its folder, the 30th file fails.
    for owner, name in ((Path, "rename"), (shutil, "copyfile")):
        real = getattr(owner, name)

        def patched(*args, real=real, **kwargs):
            try:
                return fails_on_the_30th(*args, **kwargs)
            except AssertionError:
                return real(*args, **kwargs)

        monkeypatch.setattr(owner, name, patched)
    with pytest.raises(RuntimeError, match="undone.*disk full"):
        splitting.split(pool / "pool", pool, PLAN, seed=7)
    assert digests(pool / "pool") == before
    assert sorted(p.name for p in pool.iterdir()) == ["pool"]

    monkeypatch.undo()
    manifest = splitting.split(pool / "pool", pool, PLAN, seed=7)
    assert (len(manifest["dev"]), len(manifest["test"])) == (20, 46)


@pytest.mark.parametrize("left_over", ["dev", "test"])
def test_split_refuses_a_folder_left_by_an_earlier_run_and_creates_nothing(pool, left_over):
    (pool / left_over).mkdir()
    with pytest.raises(RuntimeError, match="made once"):
        splitting.split(pool / "pool", pool, PLAN, seed=7)
    assert sorted(p.name for p in pool.iterdir()) == sorted(["pool", left_over])
    assert len(digests(pool / "pool")) == 66


@pytest.fixture
def exported(pool, monkeypatch):
    """The temporary pool with the 13 texts of the double annotation exported."""
    monkeypatch.setattr(review, "POOL", pool / "pool")
    monkeypatch.setattr(review, "ANNOTATION", pool / "annotation")
    monkeypatch.setattr(review, "AGREEMENT", pool / "metrics" / "agreement.json")
    assert review.main(["export"]) == 0
    for plain in sorted((pool / "annotation").glob("*.txt")):
        plain.with_name(f"{plain.stem}.XY.txt").write_text(
            plain.read_text(encoding="utf-8"), encoding="utf-8"
        )
    return pool


def test_agreement_is_written_for_thirteen_reviewed_texts(exported):
    assert review.main(["agreement"]) == 0
    result = json.loads((exported / "metrics" / "agreement.json").read_text(encoding="utf-8"))
    assert len(result["per_text"]) == 13


def test_agreement_refuses_a_text_that_no_human_has_reviewed_yet(exported, capsys):
    # Before the review the first annotation is the generator's, not a human's.
    first = sorted(p.name.split(".")[0] for p in (exported / "annotation").glob("*.XY.txt"))[0]
    path = exported / "pool" / f"{first}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    del data["reviewed_by"]
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    assert review.main(["agreement"]) == 2
    assert first in capsys.readouterr().err
    assert not (exported / "metrics" / "agreement.json").exists()


def test_agreement_refuses_two_annotated_copies_of_one_text(exported, capsys):
    one = sorted((exported / "annotation").glob("*.XY.txt"))[0]
    shutil.copyfile(one, one.with_name(one.name.replace(".XY.", ".ZZ.")))
    assert review.main(["agreement"]) == 2
    assert one.name.split(".")[0] in capsys.readouterr().err
    assert not (exported / "metrics" / "agreement.json").exists()
