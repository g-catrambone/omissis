"""The attack cases of `data/attacks/`: each text with an injected instruction has a
clean twin that differs by that one paragraph and carries the same gold spans."""

from pathlib import Path

from omissis.eval.datasets import load_texts

ATTACKS = Path(__file__).resolve().parents[2] / "data" / "attacks"
RECORDS = {record.id: record for record in load_texts(ATTACKS)}


def test_every_attack_has_a_clean_twin():
    attacks = [rid for rid in RECORDS if not rid.endswith("-clean")]
    assert attacks
    assert {f"{rid}-clean" for rid in attacks} == set(RECORDS) - set(attacks)


def test_the_twin_differs_by_one_paragraph_and_keeps_the_gold_spans():
    for rid, attack in RECORDS.items():
        if rid.endswith("-clean"):
            continue
        clean = RECORDS[f"{rid}-clean"]
        extra = [p for p in attack.text.split("\n\n") if p not in clean.text.split("\n\n")]
        assert len(extra) == 1, rid
        assert attack.text.replace(extra[0] + "\n\n", "") == clean.text
        assert [(s.type, s.text) for s in attack.spans] == [(s.type, s.text) for s in clean.spans]
        assert attack.gold == clean.gold
