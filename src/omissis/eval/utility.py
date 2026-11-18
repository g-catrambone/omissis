"""The two utility tasks of the protocol, section 8 (task 3.6).

Both run through `pipeline.protect_send_restore` for every configuration, `REF-none`
included, and are scored after restoration.

- **T3, extraction.** The model returns JSON with `intent`, `requested_action`,
  `amounts`, `dates`, `deadline`. The prompt asks for amounts and dates copied as they
  are written: the scorer normalises them (`eval/normalise.py`), not the model. The
  score of a text is the share of the five fields that equal the gold; a reply that
  is not JSON scores 0.
- **T1, reply draft.** The reply itself is scored by the judge (`eval/judge.py`).
  Here its restoration is recorded: the outcome of every restore event, whether the
  reply is fully restored, and for R2 the number of restored fakes.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from omissis.config import GOLD_DETECTOR, RunConfig
from omissis.contracts import PipelineResult, RestoreOutcome, parse_placeholder
from omissis.eval.datasets import SCENARIOS, Gold, TextRecord
from omissis.eval.normalise import extract_json, parse_amount, parse_date
from omissis.pipeline import protect_send_restore

T1_TASK = "Scrivi una bozza di risposta a questa email."
FIELDS = ("intent", "requested_action", "amounts", "dates", "deadline")
ACTIONS = tuple(dict.fromkeys(a for _, actions in SCENARIOS.values() for a in actions))

T3_TASK = (
    "Leggi l'email qui sotto ed estrai queste informazioni. Rispondi solo con un oggetto "
    "JSON con questi campi:\n"
    f'- "intent": lo scopo dell\'email, uno tra: {", ".join(SCENARIOS)};\n'
    f'- "requested_action": l\'azione richiesta al destinatario, una tra: {", ".join(ACTIONS)};\n'
    '- "amounts": la lista di tutti gli importi di denaro, ciascuno copiato esattamente '
    "come è scritto nell'email;\n"
    '- "dates": la lista di tutte le date complete (giorno, mese e anno), escluse le date '
    "di nascita, ciascuna copiata esattamente come è scritta;\n"
    '- "deadline": la data entro cui il destinatario deve agire, copiata come è scritta, '
    "oppure null se l'email non ne indica una.\n"
    "Non aggiungere altro testo."
)


def _amount(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return round(float(value), 2)
    return parse_amount(value) if isinstance(value, str) else None


def _date(value: Any) -> str | None:
    return parse_date(value) if isinstance(value, str) else None


def _as_set(values: Any, convert) -> set | None:
    """The normalised values of a list; None when it is not a list or an item is unreadable."""
    if not isinstance(values, list):
        return None
    converted = [convert(v) for v in values]
    return None if any(c is None for c in converted) else set(converted)


def score_t3(reply: str, gold: Gold) -> dict[str, Any]:
    """Which of the five fields of `reply` equal the gold after normalisation."""
    data = extract_json(reply)
    if data is None:
        return {"parsed": False, "fields": dict.fromkeys(FIELDS, False), "score": 0.0}
    deadline = data.get("deadline")
    fields = {
        "intent": data.get("intent") == gold.intent,
        "requested_action": data.get("requested_action") == gold.requested_action,
        "amounts": _as_set(data.get("amounts"), _amount) == {round(a, 2) for a in gold.amounts},
        "dates": _as_set(data.get("dates"), _date) == set(gold.dates),
        "deadline": (deadline is None and "deadline" in data and gold.deadline is None)
        or (deadline is not None and _date(deadline) == gold.deadline),
    }
    return {"parsed": True, "fields": fields, "score": sum(fields.values()) / len(FIELDS)}


def restoration(result: PipelineResult) -> dict[str, Any]:
    """The restoration of one reply: outcome counts, full restoration, restored fakes."""
    outcomes = Counter(event.outcome.value for event in result.restore_events)
    restored = (RestoreOutcome.RESTORED, RestoreOutcome.RESTORED_FUZZY)
    fakes = sum(
        event.outcome in restored and parse_placeholder(event.surrogate) is None
        for event in result.restore_events
    )
    return {
        "fully_restored": result.fully_restored,
        "outcomes": dict(sorted(outcomes.items())),
        "restored_fakes": fakes,
    }


def run(records: list[TextRecord], name: str, config: RunConfig) -> list[dict[str, Any]]:
    """One row per text: the T3 score and fields, and the restoration of the T1 reply."""
    rows = []
    for record in records:
        gold = record.spans if config.detector == GOLD_DETECTOR else None
        extraction = protect_send_restore(record.text, T3_TASK, config, gold)
        draft = protect_send_restore(record.text, T1_TASK, config, gold)
        t3 = score_t3(extraction.restored_reply, record.gold)
        rows.append(
            {
                "text_id": record.id,
                "config": name,
                "t3": t3["score"],
                "t3_parsed": t3["parsed"],
                "t3_fields": t3["fields"],
                **restoration(draft),
            }
        )
    return rows


def t1_reply(record: TextRecord, config: RunConfig) -> str:
    """The restored T1 reply of a text: from the cache once `run` has made the call."""
    gold = record.spans if config.detector == GOLD_DETECTOR else None
    return protect_send_restore(record.text, T1_TASK, config, gold).restored_reply
