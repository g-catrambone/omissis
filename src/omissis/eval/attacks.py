"""The two attacks of the protocol, section 7.

Both read the masked texts written by `omissis mask` and ask the `attacker` model,
through `backends.complete`, at temperature 0. The prompts hold the masked text and
public material only (the candidate profiles, the closed answer lists): never a gold
label, never the name of a configuration.

- **Linkage**: which of N candidate profiles wrote the text. The model returns the
  three most likely candidates in order. A reply that cannot be parsed is a miss.
- **Attribute inference**: one value per attribute from a closed list. A value
  outside its list is wrong, and counted with the unparseable replies.

Each function returns one row per text with everything the estimates are computed
from (`docs/interfaces.md`, section 5: `per_text`), and no text.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from omissis.backends import LLMRequest, TruncatedReplyError, complete
from omissis.config import RunConfig
from omissis.contracts import SpanType
from omissis.eval.datasets import TextRecord
from omissis.eval.normalise import extract_json
from omissis.eval.stats import bootstrap_ci

MAX_TOKENS = 4096  # the attacker reasons at length on the hard cases
AGE_BRACKETS = ("<30", "30-44", "45-59", "60+")
ATTRIBUTES = ("city", "role", "employer", "age_bracket", "gender", "health")
# Rough tokens per call (prompt and reply), for the estimate printed before a batch.
TOKENS = {"linkage_10": 2000, "linkage_25": 3500, "attributes": 1500}

SYSTEM = (
    "Sei un analista che valuta il rischio di re-identificazione di testi pseudonimizzati. "
    "Rispondi solo con JSON valido."
)

LINKAGE_PROMPT = """\
Qui sotto c'è un'email in cui alcuni dati sono stati sostituiti, e un elenco numerato
di {n} persone. Una di loro ha scritto l'email. Indica le tre persone che più
probabilmente l'hanno scritta, dalla più probabile alla meno probabile. Devi sempre
indicarne tre, anche se non sei sicuro.

Email:
---
{text}
---

Persone:
{candidates}

Rispondi solo con questo JSON, con i numeri dell'elenco:
{{"ranking": [numero, numero, numero]}}
"""

ATTRIBUTES_PROMPT = """\
Qui sotto c'è un'email in cui alcuni dati sono stati sostituiti. Per ogni attributo di
chi scrive scegli UN valore dall'elenco indicato. Devi sempre scegliere: non è ammesso
"non so".

Email:
---
{text}
---

Attributi e valori ammessi:
{spaces}

Rispondi solo con questo JSON, usando i valori esattamente come sono scritti:
{{"city": "...", "role": "...", "employer": "...", "age_bracket": "...",
"gender": "...", "health": "..."}}
"""


def load_masked(folder: str | Path) -> dict[str, str]:
    """`text_id -> masked_text` of one configuration folder written by `omissis mask`."""
    files = sorted(Path(folder).glob("*.json"))
    if not files:
        raise FileNotFoundError(f"{folder}: no masked texts; run `omissis mask` first")
    return {
        data["text_id"]: data["masked_text"]
        for data in (json.loads(p.read_text(encoding="utf-8")) for p in files)
    }


def render_profile(profile: dict[str, Any]) -> str:
    """Every field of a profile except `id` and `cohort`, on one line."""
    gender = "donna" if profile["gender"] == "F" else "uomo"
    products = ", ".join(profile["financial"]["products"])
    line = (
        f"{profile['name']}, {gender}, {profile['age']} anni, vive a {profile['city']}; "
        f"{profile['role']} presso {profile['employer']}; banca {profile['bank']}, filiale di "
        f"{profile['branch_city']}; prodotti: {products}"
    )
    if "monthly_installment" in profile["financial"]:
        line += f"; rata mensile {profile['financial']['monthly_installment']:.0f} euro"
    if profile["special"]:
        line += f"; {profile['special']['fact']}"
    return line


def age_bracket(age: int) -> str:
    return AGE_BRACKETS[(age >= 30) + (age >= 45) + (age >= 60)]


def answer_spaces(pools: dict[str, list[str]]) -> dict[str, tuple[str, ...]]:
    """The closed list of every attribute."""
    return {
        "city": tuple(pools["cities"]),
        "role": tuple(pools["roles"]),
        "employer": tuple(pools["employers"]),
        "age_bracket": AGE_BRACKETS,
        "gender": ("M", "F"),
        "health": ("none", "present"),
    }


def truth(profile: dict[str, Any], record: TextRecord) -> dict[str, str]:
    """The correct value of every attribute for a text."""
    health = any(s.type is SpanType.SALUTE for s in record.spans)
    return {
        "city": profile["city"],
        "role": profile["role"],
        "employer": profile["employer"],
        "age_bracket": age_bracket(profile["age"]),
        "gender": profile["gender"],
        "health": "present" if health else "none",
    }


def parse_ranking(reply: str, n: int) -> list[int] | None:
    """Three different positions in 1..n, or None when the reply is not a ranking."""
    data = extract_json(reply)
    ranking = data.get("ranking") if data else None
    if not isinstance(ranking, list) or len(ranking) != 3:
        return None
    if any(isinstance(r, bool) or not isinstance(r, int) or not 1 <= r <= n for r in ranking):
        return None
    return ranking if len(set(ranking)) == 3 else None


def _ask(prompt: str, config: RunConfig) -> str:
    """The attacker's reply; empty, hence unparseable, when it stopped at the token limit."""
    request = LLMRequest("attacker", prompt, SYSTEM, {"max_tokens": MAX_TOKENS})
    try:
        return complete(request, config).text
    except TruncatedReplyError:
        return ""


def linkage(
    masked: dict[str, str],
    name: str,
    size: int,
    plan: dict[str, dict[str, Any]],
    profiles: dict[str, dict[str, Any]],
    candidates: dict[str, list[str]],
    config: RunConfig,
) -> list[dict[str, Any]]:
    """One row per text: the ranking given and whether the author is first, or in it."""
    rows = []
    for text_id, text in masked.items():
        ids = candidates[text_id]
        listed = "\n".join(f"{i}. {render_profile(profiles[p])}" for i, p in enumerate(ids, 1))
        reply = _ask(LINKAGE_PROMPT.format(n=size, text=text, candidates=listed), config)
        positions = parse_ranking(reply, len(ids))
        ranking = [ids[p - 1] for p in positions] if positions else None
        author = plan[text_id]["profile_id"]
        rows.append(
            {
                "text_id": text_id,
                "config": name,
                "n": size,
                "ranking": ranking,
                "parsed": ranking is not None,
                "top1": bool(ranking) and ranking[0] == author,
                "top3": bool(ranking) and author in ranking,
            }
        )
    return rows


def attributes(
    masked: dict[str, str],
    name: str,
    records: dict[str, TextRecord],
    profiles: dict[str, dict[str, Any]],
    pools: dict[str, list[str]],
    config: RunConfig,
) -> list[dict[str, Any]]:
    """One row per text: the answers, the true values, and what was right."""
    spaces = answer_spaces(pools)
    listed = "\n".join(f"- {attr}: {' | '.join(values)}" for attr, values in spaces.items())
    rows = []
    for text_id, text in masked.items():
        data = extract_json(_ask(ATTRIBUTES_PROMPT.format(text=text, spaces=listed), config)) or {}
        answers = {a: data.get(a) for a in ATTRIBUTES}
        true = truth(profiles[records[text_id].profile_id], records[text_id])
        rows.append(
            {
                "text_id": text_id,
                "config": name,
                "answers": answers,
                "truth": true,
                # An answer outside its list is wrong and counted as invalid.
                "invalid": [a for a in ATTRIBUTES if answers[a] not in spaces[a]],
                "correct": {a: answers[a] == true[a] for a in ATTRIBUTES},
            }
        )
    return rows


def linkage_rows(per_text: list[dict[str, Any]], seed: int) -> list[dict[str, Any]]:
    """One row per configuration and N: top-1 and top-3 accuracy with 95% intervals."""
    rows = []
    for name, size in dict.fromkeys((r["config"], r["n"]) for r in per_text):
        group = [r for r in per_text if (r["config"], r["n"]) == (name, size)]
        row: dict[str, Any] = {"config": name, "n": size, "texts": len(group)}
        for metric in ("top1", "top3"):
            estimate, low, high = bootstrap_ci([float(r[metric]) for r in group], seed)
            row |= {metric: estimate, f"{metric}_ci_low": low, f"{metric}_ci_high": high}
        row["unparseable"] = sum(not r["parsed"] for r in group)
        row["chance_top1"], row["chance_top3"] = 1 / size, 3 / size
        rows.append(row)
    return rows


def attribute_rows(per_text: list[dict[str, Any]], seed: int) -> list[dict[str, Any]]:
    """One row per configuration and attribute: accuracy, interval, majority baseline."""
    rows = []
    for name in dict.fromkeys(r["config"] for r in per_text):
        group = [r for r in per_text if r["config"] == name]
        for attribute in ATTRIBUTES:
            estimate, low, high = bootstrap_ci(
                [float(r["correct"][attribute]) for r in group], seed
            )
            values = [r["truth"][attribute] for r in group]
            rows.append(
                {
                    "config": name,
                    "attribute": attribute,
                    "texts": len(group),
                    "accuracy": estimate,
                    "ci_low": low,
                    "ci_high": high,
                    "invalid": sum(attribute in r["invalid"] for r in group),
                    "majority_baseline": max(values.count(v) for v in set(values)) / len(values),
                }
            )
    return rows


def count_calls(texts: int, configurations: int, sizes: tuple[int, ...] = (10, 25)) -> dict:
    """Calls and rough tokens of both attacks, printed before any real batch."""
    per_text = {f"linkage_{n}": 1 for n in sizes} | {"attributes": 1}
    calls = texts * configurations * len(per_text)
    tokens = texts * configurations * sum(TOKENS[kind] for kind in per_text)
    return {"calls": calls, "tokens": tokens}
