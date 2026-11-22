"""Profiles, text plan and candidate lists (protocol, sections 1 and 2)."""

import itertools
import json
import re
from collections import Counter
from pathlib import Path

import pytest

from omissis.eval import profiles as P
from omissis.eval.datasets import SCENARIOS, DataError, load_profiles, load_texts
from omissis.replace import fakes

REPO = Path(__file__).resolve().parents[2]
FOLDER = REPO / "data" / "profiles"
FILES = P.build(FOLDER)
PROFILES, PLAN = FILES["profiles.json"], FILES["plan.json"]
BY_ID = {p["id"]: p for p in PROFILES}


def test_committed_files_are_what_the_seed_gives():
    for name, content in FILES.items():
        assert json.loads((FOLDER / name).read_text(encoding="utf-8")) == content, name
    assert P.build(FOLDER) == FILES  # deterministic
    assert P.build(FOLDER, seed=P.SEED + 1)["plan.json"] != PLAN


def test_profiles_load_and_have_the_sizes_of_the_protocol():
    loaded = load_profiles(FOLDER / "profiles.json")
    assert [p.id for p in loaded] == [f"p{i:02d}" for i in range(1, 31)]
    assert Counter(p.cohort for p in loaded) == {f"c{i}": 5 for i in range(1, 7)}
    assert len({p.name for p in loaded}) == 30
    assert all(P.AGES[0] <= p.age <= P.AGES[1] for p in loaded)
    pools = P.load_pools(FOLDER)
    sizes = {k: len(pools[k]) for k in ("cities", "roles", "employers", "banks")}
    assert sizes == {"cities": 6, "roles": 8, "employers": 6, "banks": 4}
    for key, pool in P.POOL_OF.items():
        assert {p[key] for p in PROFILES} <= set(pools[pool])


def test_cohort_rule():
    shared_pairs = []
    for cohort in sorted({p["cohort"] for p in PROFILES}):
        members = [p for p in PROFILES if p["cohort"] == cohort]
        shared = tuple(k for k in P.SHARED if len({m[k] for m in members}) == 1)
        assert len(shared) >= 2, cohort
        shared_pairs.append(shared)
        for a, b in itertools.combinations(members, 2):
            assert any(a[k] != b[k] for k in P.SHARED), (a["id"], b["id"])
    assert len(set(shared_pairs)) == 6  # which attributes are shared varies by cohort


def test_ten_profiles_have_a_special_fact():
    categories = Counter(p["special"]["category"] for p in PROFILES if p["special"])
    assert categories == {"SALUTE": 8, "SINDACATO": 2}


def test_plan_has_the_texts_of_the_protocol():
    assert len(PLAN) == 66
    assert Counter(e["scenario"] for e in PLAN.values()) == P.TEXTS
    domains = Counter(text_id.split("-")[0] for text_id in PLAN)
    assert domains == {"bank": 40, "hr": 26}
    for text_id, entry in PLAN.items():
        domain, actions = SCENARIOS[entry["scenario"]]
        assert text_id.startswith(domain + "-") and re.fullmatch(r"(bank|hr)-\d{4}", text_id)
        assert entry["requested_action"] in actions
        assert set(entry) == {"profile_id", "scenario", "has_special", "requested_action", "pilot"}


def test_special_texts_have_an_author_with_a_matching_fact():
    special = {t: e for t, e in PLAN.items() if e["has_special"]}
    assert len(special) == 20
    for scenario in P.ALWAYS_SPECIAL:
        assert all(e["has_special"] for e in PLAN.values() if e["scenario"] == scenario)
    extra = [e for e in special.values() if e["scenario"] not in P.ALWAYS_SPECIAL]
    assert len(extra) == 7 and {e["scenario"] for e in extra} <= set(P.SOMETIMES_SPECIAL)
    for entry in PLAN.values():
        fact = BY_ID[entry["profile_id"]]["special"]
        if entry["has_special"]:
            wanted = "SINDACATO" if entry["scenario"] == "union_leave" else "SALUTE"
            assert fact and fact["category"] == wanted
        else:
            assert fact is None  # a text without a special span is not by a special profile


def test_every_profile_writes_two_or_three_texts_and_no_scenario_twice():
    texts = Counter(e["profile_id"] for e in PLAN.values())
    assert set(texts) == set(BY_ID) and set(texts.values()) == {2, 3}
    pairs = Counter((e["profile_id"], e["scenario"]) for e in PLAN.values())
    repeated = {scenario for (_, scenario), n in pairs.items() if n > 1}
    assert repeated == {"union_leave"}  # two union members, four texts


def test_pilot_is_ten_texts_one_per_person_of_two_cohorts():
    authors = [e["profile_id"] for e in PLAN.values() if e["pilot"]]
    assert len(authors) == len(set(authors)) == 10
    assert len({BY_ID[a]["cohort"] for a in authors}) == 2


@pytest.mark.parametrize("size", P.LIST_SIZES)
def test_candidate_lists(size):
    lists = FILES[f"candidates_N{size}.json"]
    assert set(lists) == set(PLAN)
    for text_id, candidates in lists.items():
        author = PLAN[text_id]["profile_id"]
        assert len(candidates) == len(set(candidates)) == size
        assert author in candidates
        mates = {p["id"] for p in PROFILES if p["cohort"] == BY_ID[author]["cohort"]}
        assert mates <= set(candidates)
    positions = Counter(lists[t].index(PLAN[t]["profile_id"]) for t in lists)
    assert len(positions) > size // 3  # shuffled: the author is not always in one place


def test_pools_are_disjoint_from_the_r2_fake_lists_and_the_fixtures():
    pools = P.load_pools(FOLDER)
    ours = {
        w.casefold()
        for key in ("names_f", "names_m", "surnames", "cities", "employers", "banks")
        for value in pools[key]
        for w in [value, *value.split()]
    }
    for name in ("nomi_f", "nomi_m", "cognomi", "citta", "aziende", "banche"):
        for value in fakes.load_list(name):
            assert value.casefold() not in ours, value
            if name in ("nomi_f", "nomi_m", "cognomi", "citta"):
                assert not set(value.casefold().split()) & ours, value
    fixtures = load_profiles(REPO / "data" / "fixtures" / "profiles.json")
    for person in fixtures:
        assert person.name.casefold() not in ours and person.city.casefold() not in ours
        assert person.employer.casefold() not in ours and person.bank.casefold() not in ours


def test_load_texts_refuses_a_missing_or_empty_folder(tmp_path):
    with pytest.raises(DataError, match="not a folder"):
        load_texts(tmp_path / "missing")
    (tmp_path / "profiles.json").write_text("[]", encoding="utf-8")
    with pytest.raises(DataError, match="no text files"):
        load_texts(tmp_path)
