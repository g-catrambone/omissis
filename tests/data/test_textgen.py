"""Tagged text, generator and review tools (task 3.2). No test needs the network."""

import json
from pathlib import Path

import pytest
import yaml

from omissis import backends
from omissis.config import ROLES, load_eval_configs
from omissis.contracts import SpanType
from omissis.eval import profiles as planning
from omissis.eval import textgen
from omissis.eval.datasets import load_text, load_texts
from omissis.eval.normalise import parse_amount, parse_date

REPO = Path(__file__).resolve().parents[2]
FIXTURES = load_texts(REPO / "data" / "fixtures")
FILES = planning.build(REPO / "data" / "profiles")
PLAN, BY_ID = FILES["plan.json"], {p["id"]: p for p in FILES["profiles.json"]}

# --- normalisers -------------------------------------------------------------------


@pytest.mark.parametrize(
    ("written", "value"),
    [
        ("€ 320,00", 320.0),
        ("€ 1.200,50", 1200.5),
        ("1.200,50 euro", 1200.5),
        ("1200 euro", 1200.0),
        ("EUR 1.200", 1200.0),
        ("89,90 euro", 89.9),
        ("12.400 euro", 12400.0),
        ("2,5 milioni di euro", 2_500_000.0),
        ("15 mila euro", 15000.0),
        ("milleduecento euro", None),  # amounts in words are not allowed
        ("tra 100 e 200 euro", None),  # two numbers: not one amount
        ("", None),
    ],
)
def test_parse_amount(written, value):
    assert parse_amount(written) == value


@pytest.mark.parametrize(
    ("written", "value"),
    [
        ("16 novembre 2026", "2026-11-16"),
        ("1° marzo 2027", "2027-03-01"),
        ("1 Dicembre 2026", "2026-12-01"),
        ("16/11/2026", "2026-11-16"),
        ("5.12.2026", "2026-12-05"),
        ("2026-11-16", "2026-11-16"),
        ("a dicembre", None),  # no day, no year
        ("dicembre 2026", None),
        ("dal 2019", None),
        ("31 febbraio 2027", None),  # not a date
        ("lunedì prossimo", None),
    ],
)
def test_parse_date(written, value):
    assert parse_date(written) == value


# --- tagged text -------------------------------------------------------------------


def test_tags_are_stripped_and_offsets_computed():
    tagged = "Sono [[PERSONA|Lidia Caprioli]] di [[CITTA|Bergamo]]."
    text, spans = textgen.parse_tagged(tagged)
    assert text == "Sono Lidia Caprioli di Bergamo."
    assert [(s.start, s.end, s.text, s.type) for s in spans] == [
        (5, 19, "Lidia Caprioli", SpanType.PERSONA),
        (23, 30, "Bergamo", SpanType.CITTA),
    ]
    assert all(s.matches(text) and s.source == "GOLD" for s in spans)


def test_adjacent_tags_and_tags_at_the_edges():
    text, spans = textgen.parse_tagged("[[IMPORTO|€ 50]][[DATA|1 marzo 2027]]\n[[CITTA|Lodi]]")
    assert text == "€ 501 marzo 2027\nLodi"
    assert [(s.start, s.end) for s in spans] == [(0, 4), (4, 16), (17, 21)]


def test_single_brackets_and_placeholders_in_the_text_are_left_alone():
    text, spans = textgen.parse_tagged("Vedi [allegato 1] e [IBAN_1], [[CITTA|Lodi]].")
    assert text == "Vedi [allegato 1] e [IBAN_1], Lodi." and len(spans) == 1


@pytest.mark.parametrize(
    "tagged",
    [
        "Sono [[LUOGO|Bergamo]].",  # unknown type
        "Sono [[persona|Lidia]].",  # types are upper case
        "Sono [[CITTA|[[PERSONA|Lidia]] Roma]].",  # a tag inside a tag
        "Sono [[CITTA|Bergamo]] e [[CITTA Roma]].",  # no separator
        "Sono [[CITTA|Bergamo.",  # never closed
        "Sono Bergamo]].",
        "Sono [[CITTA| Bergamo]].",  # white space at the edge of the span
        "Sono [[CITTA|]].",
    ],
)
def test_malformed_tags_are_refused(tagged):
    with pytest.raises(ValueError):
        textgen.parse_tagged(tagged)


@pytest.mark.parametrize("record", FIXTURES, ids=[r.id for r in FIXTURES])
def test_export_then_import_gives_the_record_back(record):
    text, spans, deadline = textgen.parse_file(textgen.write_file(record))
    assert text == record.text
    assert [(s.start, s.end, s.type) for s in spans] == [
        (s.start, s.end, s.type) for s in record.spans
    ]
    assert deadline == record.gold.deadline
    gold = textgen.gold_from(spans, record.scenario, record.gold.requested_action, deadline)
    # The fixtures were annotated by hand: amounts and full dates must come out the same.
    assert sorted(gold["amounts"]) == sorted(record.gold.amounts)
    assert sorted(gold["dates"]) == sorted(record.gold.dates)


def test_text_with_double_brackets_cannot_be_written_as_tagged_text():
    with pytest.raises(ValueError):
        textgen.to_tagged("codice [[x]]", [])


@pytest.mark.parametrize(
    "content",
    [
        "Testo [[CITTA|Lodi]].",  # no separator
        "Testo.\n===\nniente",  # no SCADENZA line
        "Testo.\n===\nSCADENZA: 15/12/2026",  # not ISO
        "Testo.\n===\nSCADENZA: 2026-02-30",  # not a date
    ],
)
def test_bad_tagged_file_is_refused(content):
    with pytest.raises(ValueError):
        textgen.parse_file(content)


def test_model_reasoning_before_the_email_is_dropped():
    content = "<think>\nscrivo [[CITTA|x]]\n</think>\nA [[CITTA|Lodi]].\n===\nSCADENZA: nessuna"
    assert textgen.parse_file(content) == (
        "A Lodi.\n",
        textgen.parse_tagged("A [[CITTA|Lodi]].\n")[1],
        None,
    )


# --- prompt and generation ---------------------------------------------------------


def test_prompt_states_the_profile_the_scenario_and_one_action():
    text_id, entry = next((t, e) for t, e in PLAN.items() if e["has_special"])
    profile = BY_ID[entry["profile_id"]]
    prompt = textgen.build_prompt(profile, entry)
    for value in (profile["name"], profile["city"], profile["employer"], profile["bank"]):
        assert value in prompt
    assert profile["special"]["fact"] in prompt
    assert textgen.ACTION_IT[entry["requested_action"]] in prompt
    other = next(e for e in PLAN.values() if not e["has_special"])
    assert "fatto personale da citare" not in textgen.build_prompt(
        BY_ID[other["profile_id"]], other
    )
    assert "{" not in prompt.replace("[[", "")  # every field of the template was filled


def test_identifiers_are_synthetic_and_stable():
    from omissis.detect import rules

    profile = BY_ID["p01"]
    ids = textgen.identifiers(profile)
    assert ids == textgen.identifiers(profile) != textgen.identifiers(BY_ID["p02"])
    assert rules.iban_is_valid(ids["iban"]) and ids["iban"][5:10] == "00000"
    assert rules.cf_is_valid(ids["cf"]) and ids["cf"][11] == "X"
    assert ids["email"].endswith("@example.com")


REPLY = """Oggetto: richiesta

Buongiorno, sono [[PERSONA|Lidia Caprioli]], [[RUOLO|contabile]] presso
[[AZIENDA|Tessitura Valgrande S.r.l.]] a [[CITTA|Cremona]]. Vi chiedo di aggiornare
l'IBAN [[IBAN|IT89Y0000025613651127989360]] entro il [[DATA|15 dicembre 2026]]: la rata
è di [[IMPORTO|€ 320,00]]. A Cremona resto fino a dicembre.

[[PERSONA|Lidia Caprioli]]
===
SCADENZA: 2026-12-15
"""


@pytest.fixture
def generator(monkeypatch, tmp_path):
    prompts = []

    def fake(model, request):
        prompts.append(request)
        return REPLY

    monkeypatch.setattr(backends, "_PROVIDERS", {"fake": fake})
    models = tmp_path / "models.yaml"
    models.write_text(
        yaml.safe_dump({r: {"provider": "fake", "id": "fake", "revision": "1"} for r in ROLES}),
        encoding="utf-8",
    )
    overrides = {"models_file": str(models), "cache_dir": str(tmp_path / "cache")}
    config = next(iter(load_eval_configs(REPO / "configs" / "eval.yaml", overrides).values()))
    return prompts, config


def test_generated_text_becomes_a_record_the_loader_accepts(generator, tmp_path):
    prompts, config = generator
    text_id, entry = next((t, e) for t, e in PLAN.items() if e["scenario"] == "iban_change")
    data = textgen.generate_one(text_id, entry, BY_ID[entry["profile_id"]], config)
    record = load_text(textgen.save(tmp_path, data))
    assert prompts[0].role == "generator" and dict(prompts[0].params)["temperature"] == 0
    assert (record.id, record.scenario, record.profile_id) == (
        text_id,
        "iban_change",
        entry["profile_id"],
    )
    assert record.gold.requested_action == entry["requested_action"]  # as planned, not the model's
    assert (record.gold.amounts, record.gold.dates, record.gold.deadline) == (
        (320.0,),
        ("2026-12-15",),
        "2026-12-15",
    )
    assert record.reviewed_by is None and "[[" not in record.text


def test_unreadable_reply_is_asked_again_once_with_a_note(generator, monkeypatch):
    prompts, config = generator
    replies = ["Sono [[CODICE FISCALE|X]].\nSCADENZA: nessuna", REPLY]
    monkeypatch.setattr(
        backends, "_PROVIDERS", {"fake": lambda m, r: prompts.append(r) or replies.pop(0)}
    )
    text_id, entry = next((t, e) for t, e in PLAN.items() if e["scenario"] == "iban_change")
    data = textgen.generate_one(text_id, entry, BY_ID[entry["profile_id"]], config)
    assert data["gold"]["deadline"] == "2026-12-15" and len(prompts) == 2
    assert prompts[1].prompt == prompts[0].prompt + textgen.RETRY_NOTE

    replies[:] = ["niente", "ancora niente"]
    other = next(t for t, e in PLAN.items() if e["scenario"] == "card_dispute")
    with pytest.raises(ValueError):
        textgen.generate_one(other, PLAN[other], BY_ID[PLAN[other]["profile_id"]], config)


def test_check_reports_what_breaks_the_requirements(generator, tmp_path):
    _, config = generator
    text_id, entry = next((t, e) for t, e in PLAN.items() if e["scenario"] == "iban_change")
    data = textgen.generate_one(text_id, entry, BY_ID[entry["profile_id"]], config)
    problems = textgen.check(
        load_text(textgen.save(tmp_path, data)), {**entry, "has_special": True}
    )
    assert any("words, outside 120-250" in p for p in problems)
    assert any("plan says has_special=True" in p for p in problems)
    assert any("'Cremona' occurs outside a span" in p for p in problems)
    assert not any("quasi-identifier" in p or "direct identifier" in p for p in problems)


def test_check_with_the_profile_reports_untagged_profile_values_and_d0_findings(tmp_path):
    profile = {**BY_ID["p01"], "name": "Lidia Caprioli", "bank": "Banca Corvalli"}
    tagged = (
        "Gentile Banca Corvalli, sono [[PERSONA|Lidia Caprioli]]. La rata è di € 320,00 e il "
        "mio numero è 347 215 8890. Cordiali saluti, Lidia\n"
    )
    text, spans = textgen.parse_tagged(tagged)
    entry = {"scenario": "iban_change", "profile_id": "p01", "requested_action": "update_details"}
    record = load_text(
        textgen.save(tmp_path, textgen.to_json("bank-0001", entry, text, spans, None))
    )
    problems = textgen.check(record, profile=profile)
    for value in ("Banca Corvalli", "€ 320,00", "347 215 8890", "Lidia"):
        assert any(p.startswith(f"{value!r} occurs outside a span") for p in problems), value


@pytest.mark.parametrize("record", FIXTURES, ids=[r.id for r in FIXTURES])
def test_fixtures_have_no_annotated_string_left_outside_a_span(record):
    assert not [p for p in textgen.check(record) if "outside a span" in p]


def test_export_and_import_commands_keep_reviewed_by_and_recompute_offsets(tmp_path):
    pool, out = tmp_path / "pool", tmp_path / "txt"
    pool.mkdir()
    source = json.loads((REPO / "data" / "fixtures" / "fx-hr-02.json").read_text(encoding="utf-8"))
    source["reviewed_by"] = "MS"
    (pool / "fx-hr-02.json").write_text(json.dumps(source, ensure_ascii=False), encoding="utf-8")
    assert textgen.main(["export", str(pool), str(out)]) == 0
    txt = out / "fx-hr-02.txt"
    edited = txt.read_text(encoding="utf-8").replace("dove lavoro", "dove [[RUOLO|lavoro]]")
    edited = edited.replace("[[CITTA|Rimini]]", "Rimini").replace("2026-12-15", "nessuna")
    txt.write_text(edited, encoding="utf-8")
    assert textgen.main(["import", str(txt), str(pool)]) == 0
    record = load_text(pool / "fx-hr-02.json")
    assert record.reviewed_by == "MS"  # kept, never written by the tool
    assert record.text == source["text"]
    assert "lavoro" in {s.text for s in record.spans}
    assert "Rimini" not in {s.text for s in record.spans}
    assert record.gold.deadline is None and all(s.matches(record.text) for s in record.spans)


def test_generate_asks_before_calling_the_model(generator, tmp_path, monkeypatch, capsys):
    prompts, _ = generator
    monkeypatch.setattr(textgen, "POOL", tmp_path / "pool")
    monkeypatch.setattr("builtins.input", lambda prompt: "n")
    assert textgen.main(["generate", "--pilot"]) == 1
    assert prompts == [] and "10 texts to generate, 10 calls" in capsys.readouterr().out
