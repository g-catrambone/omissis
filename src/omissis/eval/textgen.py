"""Text generator, tagged-text format and review tools (task 3.2; protocol, section 2).

A text is written by the `generator` model from one profile and one line of the plan,
with every sensitive span marked inline as `[[TYPE|text]]`. After the email the model
writes a line `===` and a line `SCADENZA:` with the deadline, or `nessuna`.

The same format, *tagged text*, is what a human reviews: `export` writes a text
record as tagged text, `import` reads the corrected copy back, recomputing the
offsets. Nobody edits offsets in JSON. `amounts` and `dates` of the gold are never
typed by hand: they are read from the IMPORTO and DATA spans (dates with day, month
and year only, as the annotation guide says).

Commands (run with `uv run --env-file .env python -m omissis.eval.textgen ...`):

    generate --pilot | --all      write the planned texts to data/pool/ (asks first)
    check <folder>                report what breaks the requirements of the protocol
    export <folder> <out>         one <text_id>.txt of tagged text per record
    import <txt> <folder>         read a corrected <text_id>.txt back into its record

A file already in `data/pool/` is never overwritten by `generate`; `import` keeps
`reviewed_by` as it is and never writes it: the reviewer adds it by hand.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path
from typing import Any

from omissis.backends import LLMRequest, complete
from omissis.config import RunConfig, load_eval_configs
from omissis.contracts import TYPE_CLASS, Span, SpanClass, SpanType
from omissis.detect import rules
from omissis.eval import profiles as planning
from omissis.eval.datasets import SCENARIOS, TextRecord, load_text, load_texts
from omissis.eval.normalise import parse_amount, parse_date
from omissis.replace.fakes import _cf, _iban, _shape

POOL = Path("data/pool")
EVAL_CONFIG = Path("configs/eval.yaml")
SEPARATOR = "==="
MAX_TOKENS = 4096
WORDS = (120, 250)
TOKENS_PER_TEXT = 2500  # rough: prompt and reply, for the estimate printed before a batch
_TAG = re.compile(r"\[\[([A-Za-z_]+)\|(.+?)\]\]", re.DOTALL)
_THINK = re.compile(r"<think>.*?</think>", re.DOTALL)

SCENARIO_IT = {
    "mortgage_suspension": "chiede alla banca di sospendere o rimodulare le rate del {loan}",
    "card_dispute": "contesta alla banca uno o più addebiti sulla carta che non riconosce",
    "iban_change": "comunica alla banca un nuovo IBAN per un addebito o un accredito",
    "loan_early_repayment": "chiede alla banca notizie o l'estinzione anticipata del {loan}",
    "account_closure": "chiede alla banca di chiudere un conto corrente",
    "fee_complaint": "reclama con la banca per commissioni o spese addebitate",
    "inheritance_unblock": "chiede alla banca di sbloccare il conto di un familiare defunto",
    "sick_leave": "comunica all'ufficio del personale un'assenza per malattia",
    "remote_work_request": "chiede all'ufficio del personale di lavorare da remoto",
    "harassment_complaint": "segnala all'ufficio del personale molestie o vessazioni sul lavoro",
    "medical_reimbursement": "chiede all'ufficio del personale il rimborso di spese mediche",
    "transfer_request": "chiede all'ufficio del personale il trasferimento ad altra sede",
    "union_leave": "chiede all'ufficio del personale un permesso sindacale",
}
ACTION_IT = {
    "suspend_payment": "sospendere i pagamenti",
    "reschedule_payment": "rimodulare il piano dei pagamenti",
    "refund": "rimborsare o stornare una somma",
    "open_investigation": "aprire una pratica di verifica o un'indagine",
    "update_details": "aggiornare i dati registrati",
    "send_information": "inviare informazioni o documenti",
    "close_account": "chiudere il rapporto",
    "release_funds": "sbloccare o trasferire le somme",
    "schedule_meeting": "fissare un incontro o un colloquio",
    "register_absence": "registrare l'assenza",
    "approve_request": "approvare la richiesta",
}

SYSTEM = (
    "Scrivi email italiane realistiche e inventate, per un dataset di ricerca sulla "
    "protezione dei dati personali. Tutte le persone e tutti i dati sono inventati."
)

_TYPES_IT = """\
Identificativi diretti: PERSONA (nome di una persona), IBAN, CF (codice fiscale), PIVA,
TELEFONO, EMAIL, INDIRIZZO (via e numero), DOCUMENTO (numero di un documento),
CONTO (numero di conto, carta o contratto che non è un IBAN), DATA_NASCITA,
UTENTE (matricola, codice cliente, nome utente).
Quasi-identificativi: AZIENDA (organizzazione con un nome: datore di lavoro, banca),
RUOLO (mestiere), CITTA, STRUTTURA (sede con un nome proprio, es. Ospedale Maggiore),
IMPORTO (somma con la valuta), DATA (data diversa dalla nascita), ETA, NAZIONALITA.
Categorie particolari: SALUTE, RELIGIONE, POLITICA, SINDACATO, ORIENTAMENTO, ETNIA,
BIOMETRICO, GIUDIZIARIO."""

PROMPT = """\
Scrivi un'email in italiano, in prima persona, in cui la persona descritta qui sotto
{scenario}. La richiesta è una sola: {action}. Non chiedere altro.

Chi scrive:
- nome: {name}
- età: {age} anni
- città: {city}
- lavoro: {role} presso {employer}
- banca: {bank}, filiale di {branch_city}
- prodotti bancari: {products}
{special}
Dati da usare quando servono un identificativo o un contatto (non inventarne altri
dello stesso tipo):
- IBAN: {iban}
- codice fiscale: {cf}
- telefono: {phone}
- email: {email}
- matricola aziendale: {badge}

Regole:
1. Da {min_words} a {max_words} parole. Oggetto, saluto, testo, firma. Tono di una
   persona comune, non di un modulo.
2. L'email contiene il nome di chi scrive, almeno un altro identificativo diretto e
   almeno quattro quasi-identificativi (lavoro, datore di lavoro, città, banca,
   importi, date), distribuiti nel testo: nessuna frase da sola deve bastare a
   riconoscere la persona.
3. Almeno un importo oppure una data. Importi come "€ 1.200,50" o "1.200 euro"; date
   complete come "16 novembre 2026" o "16/11/2026". Niente importi in lettere, niente
   "lunedì prossimo". Le date sono tra novembre 2026 e giugno 2027.
4. Marca OGNI dato personale così: [[TIPO|testo]]. Il testo dentro il marcatore è il
   più breve possibile: il nome senza il titolo, l'importo con la valuta, la data
   senza il giorno della settimana, senza articoli o preposizioni. Marca anche le
   ripetizioni, l'oggetto e la firma. Il nome della banca e quello del datore di lavoro
   si marcano come AZIENDA ogni volta, anche nel saluto ("Gentile [[AZIENDA|Banca
   Corvalli]]"); ogni importo come IMPORTO. Una struttura indicata con un nome comune e una città
   ("filiale di Cremona") si marca solo come città. Enti che tutti conoscono (INPS,
   Agenzia delle Entrate) non si marcano.
{special_rule}
Tipi ammessi:
{types}

Esempio di frase marcata:
sono [[PERSONA|Davide Sorrentino]], [[RUOLO|magazziniere]] nello stabilimento di
[[CITTA|Nola]], e dal [[DATA|16 novembre 2026]] sarò assente.

Dopo l'email scrivi una riga con solo {separator} e poi una riga:
SCADENZA: la data entro cui il destinatario deve agire, nel formato AAAA-MM-GG,
oppure "nessuna" se l'email non ne indica una.
Non scrivere nient'altro.
"""


# --- tagged text -------------------------------------------------------------------


def parse_tagged(tagged: str) -> tuple[str, list[Span]]:
    """Strip the `[[TYPE|text]]` tags of `tagged`: the plain text and its gold spans."""
    parts, spans, at, length = [], [], 0, 0
    for match in _TAG.finditer(tagged):
        label, value = match.group(1), match.group(2)
        if label not in SpanType.__members__:
            raise ValueError(f"unknown type {label!r} in tag {match.group()!r}")
        if "[[" in value or "]]" in value or not value.strip() or value != value.strip():
            raise ValueError(f"malformed tag {match.group()!r}")
        before = tagged[at : match.start()]
        parts += [before, value]
        start = length + len(before)
        spans.append(Span(start, start + len(value), value, SpanType(label), 1.0, "GOLD"))
        length = start + len(value)
        at = match.end()
    parts.append(tagged[at:])
    text = "".join(parts)
    if "[[" in text or "]]" in text:
        where = text.index("[[") if "[[" in text else text.index("]]")
        raise ValueError(f"brackets left after the tags: {text[max(0, where - 20) : where + 30]!r}")
    return text, spans


def to_tagged(text: str, spans: list[Span] | tuple[Span, ...]) -> str:
    """The inverse of `parse_tagged`."""
    if "[[" in text or "]]" in text:
        raise ValueError("the text holds double brackets and cannot be written as tagged text")
    out, at = [], 0
    for span in sorted(spans, key=lambda s: s.start):
        out += [text[at : span.start], f"[[{span.type.value}|{span.text}]]"]
        at = span.end
    return "".join(out) + text[at:]


def parse_file(content: str) -> tuple[str, list[Span], str | None]:
    """A tagged-text file: the text, its spans and the deadline (None for `nessuna`)."""
    content = _THINK.sub("", content).strip()
    body, separator, tail = content.rpartition(f"\n{SEPARATOR}")
    if not separator:
        raise ValueError(f"no line {SEPARATOR!r} after the email")
    line = re.search(r"SCADENZA:\s*(\S+)", tail)
    if line is None:
        raise ValueError("no line SCADENZA: after the separator")
    deadline = None if line.group(1).lower().startswith("nessun") else line.group(1)
    if deadline is not None and parse_date(deadline) != deadline:
        raise ValueError(f"SCADENZA must be AAAA-MM-GG or nessuna, got {deadline!r}")
    text, spans = parse_tagged(body.strip() + "\n")
    return text, spans, deadline


def write_file(record: TextRecord) -> str:
    """A text record as a tagged-text file."""
    deadline = record.gold.deadline or "nessuna"
    return f"{to_tagged(record.text, record.spans)}\n{SEPARATOR}\nSCADENZA: {deadline}\n"


def gold_from(spans: list[Span] | tuple[Span, ...], scenario: str, action: str, deadline):
    """The gold fields: amounts and full dates read from the spans, in order, no repeats."""
    amounts = [parse_amount(s.text) for s in spans if s.type is SpanType.IMPORTO]
    dates = [parse_date(s.text) for s in spans if s.type is SpanType.DATA]
    return {
        "intent": scenario,
        "amounts": list(dict.fromkeys(a for a in amounts if a is not None)),
        "dates": list(dict.fromkeys(d for d in dates if d is not None)),
        "requested_action": action,
        "deadline": deadline,
    }


def to_json(
    text_id: str, entry: dict[str, Any], text: str, spans: list[Span], deadline: str | None
) -> dict[str, Any]:
    """The text-record object of `docs/interfaces.md`, section 5 (without `reviewed_by`)."""
    return {
        "id": text_id,
        "domain": SCENARIOS[entry["scenario"]][0],
        "scenario": entry["scenario"],
        "profile_id": entry["profile_id"],
        "has_special": any(TYPE_CLASS[s.type] is SpanClass.SPECIAL for s in spans),
        "text": text,
        "spans": [
            {"start": s.start, "end": s.end, "text": s.text, "type": s.type.value} for s in spans
        ],
        "gold": gold_from(spans, entry["scenario"], entry["requested_action"], deadline),
    }


def save(folder: Path, data: dict[str, Any]) -> Path:
    path = folder / f"{data['id']}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    load_text(path)  # the loader is the judge of the format
    return path


# --- generation --------------------------------------------------------------------


def identifiers(profile: dict[str, Any], seed: int = planning.SEED) -> dict[str, str]:
    """Synthetic identifiers of a profile, the same in every text it writes."""
    rng = random.Random(f"{seed}|identifiers|{profile['id']}")
    first, surname = profile["name"].lower().split()
    return {
        "iban": _iban(rng),
        "cf": _cf(rng),
        "phone": _shape(rng, "3xx 000 0000".replace("x", "0"), keep=1),
        "email": f"{first}.{surname}@example.com",
        "badge": _shape(rng, "AA-00000"),
    }


def build_prompt(profile: dict[str, Any], entry: dict[str, Any]) -> str:
    special = special_rule = ""
    if entry["has_special"]:
        fact = profile["special"]
        special = f"- fatto personale da citare nell'email: {fact['fact']} ({fact['category']})\n"
        special_rule = (
            f"5. L'email cita il fatto personale indicato sopra e lo marca come "
            f"{fact['category']}.\n"
        )
    else:
        special_rule = (
            "5. L'email non contiene dati sulla salute, sul sindacato o altre categorie "
            "particolari.\n"
        )
    products = profile["financial"]["products"]
    loan = next(
        (name for name in ("mutuo prima casa", "prestito personale") if name in products),
        "finanziamento",
    )
    return PROMPT.format(
        scenario=SCENARIO_IT[entry["scenario"]].format(loan=loan),
        action=ACTION_IT[entry["requested_action"]],
        products=", ".join(products),
        special=special,
        special_rule=special_rule,
        types=_TYPES_IT,
        separator=SEPARATOR,
        min_words=WORDS[0] + 20,  # a margin inside the limits of the protocol
        max_words=WORDS[1] - 30,
        **{
            k: profile[k]
            for k in ("name", "age", "city", "role", "employer", "bank", "branch_city")
        },
        **identifiers(profile),
    )


def generate_one(
    text_id: str, entry: dict[str, Any], profile: dict[str, Any], config: RunConfig
) -> dict[str, Any]:
    """Ask the generator for one text and return its text-record object."""
    request = LLMRequest(
        "generator", build_prompt(profile, entry), SYSTEM, {"max_tokens": MAX_TOKENS}
    )
    text, spans, deadline = parse_file(complete(request, config).text)
    return to_json(text_id, entry, text, spans, deadline)


# --- checks ------------------------------------------------------------------------


def _outside(record: TextRecord, value: str) -> list[str]:
    """The contexts where `value` occurs in the text outside every span."""
    covered = [(s.start, s.end) for s in record.spans]
    found = []
    for match in re.finditer(rf"(?<!\w){re.escape(value)}(?!\w)", record.text):
        if not any(a <= match.start() and match.end() <= b for a, b in covered):
            found.append(record.text[max(0, match.start() - 25) : match.end() + 15])
    return found


def check(
    record: TextRecord, entry: dict[str, Any] | None = None, profile: dict[str, Any] | None = None
) -> list[str]:
    """What in `record` breaks the text requirements of the protocol, section 2.

    With the `profile` of the author it also reports the values of the profile, and
    whatever the D0 rules find, that the text holds outside every span: the reviewer
    tags them or accepts them.
    """
    problems = []
    words = len(record.text.split())
    if not WORDS[0] <= words <= WORDS[1]:
        problems.append(f"{words} words, outside {WORDS[0]}-{WORDS[1]}")
    classes = [s.cls for s in record.spans]
    if classes.count(SpanClass.DIRECT) < 1:
        problems.append("no direct identifier")
    if classes.count(SpanClass.QUASI) < 4:
        problems.append(f"{classes.count(SpanClass.QUASI)} quasi-identifier spans, fewer than 4")
    if not any(s.type in (SpanType.IMPORTO, SpanType.DATA) for s in record.spans):
        problems.append("no amount and no date")
    if entry is not None and entry["has_special"] != record.has_special:
        problems.append(f"plan says has_special={entry['has_special']}, the spans say otherwise")
    for span in record.spans:
        if span.type is SpanType.IMPORTO and parse_amount(span.text) is None:
            problems.append(f"amount {span.text!r} is not in an allowed format")
    if record.gold.deadline is not None and record.gold.deadline not in record.gold.dates:
        problems.append(f"deadline {record.gold.deadline} is not one of the dates of the text")
    values = [s.text for s in record.spans]
    if profile is not None:
        values += [profile[k] for k in ("name", "city", "employer", "role", "bank", "branch_city")]
        values += profile["name"].split() + list(identifiers(profile).values())
        values += [s.text for s in rules.find_all(record.text)]
    for value in dict.fromkeys(values):
        for context in _outside(record, value):
            problems.append(f"{value!r} occurs outside a span: ...{context!r}...")
    return problems


# --- commands ----------------------------------------------------------------------


def _generate(args: argparse.Namespace) -> int:
    files = planning.build()
    by_id = {p["id"]: p for p in files["profiles.json"]}
    wanted = {
        t: e
        for t, e in files["plan.json"].items()
        if (e["pilot"] or args.all) and not (POOL / f"{t}.json").exists()
    }
    print(
        f"{len(wanted)} texts to generate, {len(wanted)} calls to the generator, "
        f"about {len(wanted) * TOKENS_PER_TEXT:,} tokens (free tier: no charge)."
    )
    if not wanted:
        return 0
    if not args.yes and input("Proceed? [y/N] ").strip().lower() != "y":
        return 1
    config = next(iter(load_eval_configs(EVAL_CONFIG).values()))
    POOL.mkdir(parents=True, exist_ok=True)
    failed = 0
    for text_id, entry in wanted.items():
        try:
            path = save(POOL, generate_one(text_id, entry, by_id[entry["profile_id"]], config))
        except (ValueError, RuntimeError) as exc:  # unparseable reply, refused record, API down
            failed += 1
            (POOL / f"{text_id}.json").unlink(missing_ok=True)
            print(f"{text_id}: NOT WRITTEN: {exc}")
            continue
        problems = check(load_text(path), entry, by_id[entry["profile_id"]])
        print(f"{text_id}: written" + "".join(f"\n    - {p}" for p in problems))
    return 1 if failed else 0


def _check(args: argparse.Namespace) -> int:
    files = planning.build()
    plan, by_id = files["plan.json"], {p["id"]: p for p in files["profiles.json"]}
    found = 0
    for record in load_texts(args.folder):
        problems = check(record, plan.get(record.id), by_id.get(record.profile_id))
        found += len(problems)
        print(
            f"{record.id}: " + ("ok" if not problems else "".join(f"\n    - {p}" for p in problems))
        )
    return 1 if found else 0


def _export(args: argparse.Namespace) -> int:
    args.out.mkdir(parents=True, exist_ok=True)
    for record in load_texts(args.folder):
        (args.out / f"{record.id}.txt").write_text(write_file(record), encoding="utf-8")
    return 0


def _import(args: argparse.Namespace) -> int:
    path = args.folder / f"{args.txt.stem}.json"
    old = json.loads(path.read_text(encoding="utf-8"))
    text, spans, deadline = parse_file(args.txt.read_text(encoding="utf-8"))
    entry = {k: old[k] for k in ("scenario", "profile_id")}
    entry["requested_action"] = old["gold"]["requested_action"]
    new = to_json(old["id"], entry, text, spans, deadline)
    if "reviewed_by" in old:
        new["reviewed_by"] = old["reviewed_by"]
    save(args.folder, new)
    for problem in check(load_text(path)):
        print(f"    - {problem}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m omissis.eval.textgen")
    commands = parser.add_subparsers(dest="command", required=True)
    sub = commands.add_parser("generate")
    sub.add_argument("--all", action="store_true", help="every planned text, not only the pilot")
    sub.add_argument("--pilot", action="store_true", help="the 10 pilot texts (the default)")
    sub.add_argument("--yes", action="store_true", help="do not ask before calling the model")
    sub.set_defaults(run=_generate)
    sub = commands.add_parser("check")
    sub.add_argument("folder", type=Path)
    sub.set_defaults(run=_check)
    sub = commands.add_parser("export")
    sub.add_argument("folder", type=Path)
    sub.add_argument("out", type=Path)
    sub.set_defaults(run=_export)
    sub = commands.add_parser("import")
    sub.add_argument("txt", type=Path)
    sub.add_argument("folder", type=Path)
    sub.set_defaults(run=_import)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    sys.exit(main())
