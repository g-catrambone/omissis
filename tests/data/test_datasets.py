"""Text and profile loaders and the fixture emails."""

import copy
import json
from pathlib import Path

import pytest

from omissis.contracts import GOLD_SOURCE, SpanClass
from omissis.eval.datasets import DataError, load_profiles, load_text, load_texts

FIXTURES = Path(__file__).resolve().parents[2] / "data" / "fixtures"


# --- the fixtures ------------------------------------------------------------------


@pytest.fixture(scope="module")
def records():
    return load_texts(FIXTURES)


def test_five_fixture_emails(records):
    assert len(records) == 5
    assert [r.domain for r in records].count("bank") == 3
    assert [r.domain for r in records].count("hr") == 2


def test_exactly_one_fixture_has_special_category_data(records):
    assert sum(r.has_special for r in records) == 1


def test_every_span_matches_its_text(records):
    for record in records:
        assert record.spans
        assert all(s.matches(record.text) for s in record.spans)
        assert all(s.source == GOLD_SOURCE and s.confidence == 1.0 for s in record.spans)


def test_every_fixture_has_a_direct_identifier(records):
    for record in records:
        assert any(s.cls is SpanClass.DIRECT for s in record.spans), record.id


def test_fixtures_are_not_marked_as_reviewed(records):
    # reviewed_by is set by a human reviewer only.
    assert all(r.reviewed_by is None for r in records)


def test_fixture_authors_are_in_the_fixture_profiles(records):
    profiles = {p.id: p for p in load_profiles(FIXTURES / "profiles.json")}
    for record in records:
        profile = profiles[record.profile_id]
        assert profile.name in record.text
        assert (profile.special is not None) == record.has_special


def test_fixture_emails_use_reserved_domains(records):
    for record in records:
        for span in record.spans:
            if span.type == "EMAIL":
                assert span.text.split("@")[1] in {"example.com", "example.net", "example.org"}


# --- validation of texts -------------------------------------------------------------

VALID = {
    "id": "t-0001",
    "domain": "bank",
    "scenario": "card_dispute",
    "profile_id": "p01",
    "has_special": False,
    "text": "Sono Ada Neri, rimborso di 50 euro.",
    "spans": [
        {"start": 5, "end": 13, "text": "Ada Neri", "type": "PERSONA"},
        {"start": 27, "end": 34, "text": "50 euro", "type": "IMPORTO"},
    ],
    "gold": {
        "intent": "card_dispute",
        "amounts": [50.0],
        "dates": [],
        "requested_action": "refund",
        "deadline": None,
    },
}


def write(tmp_path, data, name=None):
    path = tmp_path / f"{name or data.get('id', 'x')}.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


def test_valid_record_loads(tmp_path):
    record = load_text(write(tmp_path, VALID))
    assert record.gold.amounts == (50.0,)
    assert [s.text for s in record.spans] == ["Ada Neri", "50 euro"]


def test_reviewed_by_is_optional_and_loaded(tmp_path):
    record = load_text(write(tmp_path, {**VALID, "reviewed_by": "MS"}))
    assert record.reviewed_by == "MS"


def mutate(change):
    data = copy.deepcopy(VALID)
    change(data)
    return data


BROKEN = {
    "missing key": mutate(lambda d: d.pop("gold")),
    "unknown key": mutate(lambda d: d.update(extra=1)),
    "empty reviewer": mutate(lambda d: d.update(reviewed_by=" ")),
    "unknown scenario": mutate(lambda d: d.update(scenario="pizza")),
    "wrong domain": mutate(lambda d: d.update(domain="hr")),
    "has_special not bool": mutate(lambda d: d.update(has_special="no")),
    "has_special without span": mutate(lambda d: d.update(has_special=True)),
    "span offsets": mutate(lambda d: d["spans"][0].update(start=4, end=12)),
    "span length": mutate(lambda d: d["spans"][0].update(end=14)),
    "span type": mutate(lambda d: d["spans"][0].update(type="NOME")),
    "span extra key": mutate(lambda d: d["spans"][0].update(confidence=0.5)),
    "span overlap": mutate(
        lambda d: d["spans"].insert(1, {"start": 9, "end": 13, "text": "Neri", "type": "PERSONA"})
    ),
    "spans unsorted": mutate(lambda d: d["spans"].reverse()),
    "intent": mutate(lambda d: d["gold"].update(intent="iban_change")),
    "action": mutate(lambda d: d["gold"].update(requested_action="close_account")),
    "amount": mutate(lambda d: d["gold"].update(amounts=["50"])),
    "date": mutate(lambda d: d["gold"].update(dates=["03/11/2026"])),
    "deadline": mutate(lambda d: d["gold"].update(deadline="2026-02-30")),
    # ISO has other ten-character dates; the scorer compares YYYY-MM-DD strings only
    "date as a week": mutate(lambda d: d["gold"].update(dates=["2026-W47-3"])),
    "deadline as a week": mutate(lambda d: d["gold"].update(deadline="2026-W47-3")),
    "amount not a number": mutate(lambda d: d["gold"].update(amounts=[float("nan")])),
    "amount infinite": mutate(lambda d: d["gold"].update(amounts=[float("inf")])),
    "span offset a float": mutate(lambda d: d["spans"][0].update(start=5.0)),
    "span offset a bool": mutate(
        lambda d: d["spans"].__setitem__(
            0, {"start": True, "end": 4, "text": "ono", "type": "PERSONA"}
        )
    ),
    "span type a list": mutate(lambda d: d["spans"][0].update(type=["PERSONA"])),
    "span text a number": mutate(lambda d: d["spans"][0].update(text=5)),
}


@pytest.mark.parametrize("data", BROKEN.values(), ids=BROKEN.keys())
def test_broken_record_is_rejected(tmp_path, data):
    with pytest.raises(DataError):
        load_text(write(tmp_path, data, name=VALID["id"]))


def test_id_must_match_file_name(tmp_path):
    with pytest.raises(DataError, match="file name"):
        load_text(write(tmp_path, VALID, name="other"))


def test_invalid_json_is_reported(tmp_path):
    path = tmp_path / "t-0001.json"
    path.write_text("{", encoding="utf-8")
    with pytest.raises(DataError, match="not valid JSON"):
        load_text(path)


# --- validation of profiles ----------------------------------------------------------

PROFILE = {
    "id": "p01",
    "cohort": "c1",
    "name": "Ada Neri",
    "gender": "F",
    "age": 30,
    "city": "Lecce",
    "employer": "Esempio S.r.l.",
    "role": "contabile",
    "bank": "Banca Esempio",
    "branch_city": "Lecce",
    "financial": {},
    "special": {"category": "SALUTE", "fact": "diabete"},
}


def write_profiles(tmp_path, items):
    path = tmp_path / "profiles.json"
    path.write_text(json.dumps(items), encoding="utf-8")
    return path


def test_valid_profiles_load(tmp_path):
    (profile,) = load_profiles(write_profiles(tmp_path, [PROFILE]))
    assert profile.gender == "F" and profile.special["category"] == "SALUTE"


@pytest.mark.parametrize(
    "change",
    [
        {"gender": "X"},
        {"age": "30"},
        {"age": 12},
        {"name": ""},
        {"financial": []},
        {"special": {"category": "CITTA", "fact": "x"}},
        {"special": {"category": "SALUTE"}},
        {"extra": 1},
    ],
)
def test_broken_profile_is_rejected(tmp_path, change):
    with pytest.raises(DataError):
        load_profiles(write_profiles(tmp_path, [{**PROFILE, **change}]))


def test_duplicate_profile_id_is_rejected(tmp_path):
    with pytest.raises(DataError, match="duplicate"):
        load_profiles(write_profiles(tmp_path, [PROFILE, PROFILE]))
