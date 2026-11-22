"""The pilot command, end to end with a fake attacker."""

import json
from pathlib import Path

import pytest
import yaml

from omissis import backends
from omissis.config import ROLES
from omissis.eval import pilot, textgen
from omissis.eval import profiles as planning

REPO = Path(__file__).resolve().parents[2]
FILES = planning.build(REPO / "data" / "profiles")
PLAN = FILES["plan.json"]
PROFILES = {p["id"]: p for p in FILES["profiles.json"]}
PILOT = [t for t, e in PLAN.items() if e["pilot"]]


def tagged(profile):
    """A small email by `profile`, tagged; the health fact only when it has one."""
    fact = f" Soffro di [[SALUTE|{profile['special']['fact']}]]." if profile["special"] else ""
    if profile["special"] and profile["special"]["category"] != "SALUTE":
        fact = f" Sono [[SINDACATO|{profile['special']['fact']}]]."
    return (
        f"Sono [[PERSONA|{profile['name']}]], [[RUOLO|{profile['role']}]] presso "
        f"[[AZIENDA|{profile['employer']}]] a [[CITTA|{profile['city']}]]. Il "
        f"[[DATA|15 dicembre 2026]] pago [[IMPORTO|€ 100,00]].{fact}\n"
    )


@pytest.fixture
def world(monkeypatch, tmp_path):
    """Ten pilot texts in a temporary pool and an attacker that reads names in clear."""
    pool = tmp_path / "pool"
    pool.mkdir()
    for text_id in PILOT:
        entry = PLAN[text_id]
        text, spans = textgen.parse_tagged(tagged(PROFILES[entry["profile_id"]]))
        textgen.save(pool, textgen.to_json(text_id, entry, text, spans, None))

    def fake(model, request):
        if "ranking" not in request.prompt:
            return json.dumps({"city": "Cremona", "gender": "F", "health": "none"})
        # The attacker finds the author when a quasi-identifier is visible: it picks the
        # first candidate whose employer and role are both written in the email.
        email, _, people = request.prompt.partition("Persone:")
        for line in people.splitlines():
            number, _, rest = line.partition(". ")
            if number.isdigit() and any(
                p["name"] in rest and p["employer"] in email and p["role"] in email
                for p in PROFILES.values()
            ):
                return json.dumps({"ranking": [int(number), 1 if number != "1" else 2, 3]})
        return json.dumps({"ranking": [1, 2, 3]})

    monkeypatch.setattr(backends, "_PROVIDERS", {"fake": fake})
    models = tmp_path / "models.yaml"
    models.write_text(
        yaml.safe_dump({r: {"provider": "fake", "id": "fake", "revision": "1"} for r in ROLES}),
        encoding="utf-8",
    )
    data = yaml.safe_load((REPO / "configs" / "eval.yaml").read_text(encoding="utf-8"))
    data["base"].update(models_file=str(models), cache_dir=str(tmp_path / "cache"))
    config = tmp_path / "eval.yaml"
    config.write_text(yaml.safe_dump(data), encoding="utf-8")
    monkeypatch.setattr(pilot, "POOL", pool)
    monkeypatch.setattr(pilot, "OUT", tmp_path / "results")
    monkeypatch.setattr(pilot, "EVAL_CONFIG", config)
    return tmp_path


def test_pilot_writes_masked_texts_metrics_and_the_note(world, capsys):
    assert pilot.main(["--yes"]) == 0
    assert "10 texts x 3 configurations: 90 calls" in capsys.readouterr().out
    out = world / "results"
    assert sorted(p.name for p in (out / "masked").iterdir()) == sorted(pilot.REFERENCES)
    assert len(list((out / "masked" / "REF-oracle").glob("*.json"))) == 10

    linkage = json.loads((out / "metrics" / "linkage.json").read_text(encoding="utf-8"))
    assert linkage["split"] == "pilot" and len(linkage["generated_from"]) == 3
    assert len(linkage["per_text"]) == 10 * 3 * 2 and len(linkage["rows"]) == 3 * 2
    assert all("text" not in row and "ranking" in row for row in linkage["per_text"])
    top1 = {(r["config"], r["n"]): r["top1"] for r in linkage["rows"]}
    # Role and employer are visible unless quasi-identifiers are masked.
    assert top1[("REF-none", 10)] > top1[("REF-oracle", 10)]
    assert top1[("REF-oracle-direct", 10)] > top1[("REF-oracle", 10)]

    attributes = json.loads((out / "metrics" / "attributes.json").read_text(encoding="utf-8"))
    assert len(attributes["per_text"]) == 30 and len(attributes["rows"]) == 3 * 6
    role = next(r for r in attributes["rows"] if r["attribute"] == "role")
    assert role["accuracy"] == 0.0 and role["invalid"] == 10  # the fake never answers it

    text = (out / "pilot.md").read_text(encoding="utf-8")
    assert "## Pilot rule" in text and "`REF-oracle-direct`" in text
    assert "The decision is the team's" in text


def test_rows_can_be_rebuilt_from_per_text_and_seed(world):
    from omissis.eval import attacks

    pilot.main(["--yes"])
    for name, rebuild in (
        ("linkage", attacks.linkage_rows),
        ("attributes", attacks.attribute_rows),
    ):
        data = json.loads((world / "results" / "metrics" / f"{name}.json").read_text("utf-8"))
        assert rebuild(data["per_text"], data["seed"]) == data["rows"]


def test_pilot_asks_first_and_stops_on_no(world, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt: "n")
    assert pilot.main([]) == 1
    assert not (world / "results").exists()


def test_pilot_stops_when_a_pilot_text_is_missing(world, capsys):
    (world / "pool" / f"{PILOT[0]}.json").unlink()
    assert pilot.main(["--yes"]) == 2
    assert PILOT[0] in capsys.readouterr().err
