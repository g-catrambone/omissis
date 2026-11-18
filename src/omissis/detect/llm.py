"""D3: an LLM that finds quasi-identifiers and special categories (task 4.3).

It also looks for one direct identifier, UTENTE (employee number, customer code, user
name): it has no fixed shape, so no rule and no ready-made model finds it. On the
pilot texts it was the one identifier left in every text.

The model is asked for a JSON array of items `{"text", "type", "reason"}` and never
for offsets: each `text` is located in the source by string search and every
occurrence as a whole token becomes a span, never a part of a longer word or number
("Roma" is not in "Romagnosi", nor "34" in "1.340"). An item whose text does not occur
so in the source is dropped and counted as hallucinated.

The reply must be the JSON array and nothing else, and every item must pass the
schema (`_valid`): otherwise the whole reply is invalid. An invalid reply is asked
again once, with a different prompt, because the cache answers an identical prompt
with the same reply. After a second invalid reply the failure is logged and counted
and D3 returns no spans.

The call goes through `backends.complete` with role `d3`, temperature 0 and the
seed of the run. `CacheMissError` and `ConfigError` are not caught here.

D3 gives no score: every span gets `CONFIDENCE`. Counts of this process are in
`stats` (`calls`, `retries`, `failures`, `hallucinated`).
"""

from __future__ import annotations

import json
import logging
import re
from collections import Counter

from omissis.backends import LLMRequest, TruncatedReplyError, complete
from omissis.config import RunConfig
from omissis.contracts import TYPE_CLASS, DetectorId, Span, SpanClass, SpanType

logger = logging.getLogger(__name__)

SOURCE = DetectorId.D3.value
CONFIDENCE = 0.8
# Room for the model's reasoning and for the list: without a limit a hosted reasoning
# model stops before it has answered.
MAX_TOKENS = 4096
# At its default effort the pinned model (openai/gpt-oss-20b) loops in its reasoning on
# this task and spends every token without answering; at low effort it answers.
REASONING = {"reasoning_effort": "low"}
TYPES = (
    *(t for t, cls in TYPE_CLASS.items() if cls is not SpanClass.DIRECT),
    SpanType.UTENTE,
)

stats: Counter[str] = Counter()

SYSTEM = (
    "Sei un assistente che individua informazioni personali in testi italiani. "
    "Rispondi solo con JSON valido, senza alcun testo prima o dopo."
)

_TYPE_HELP = {
    SpanType.AZIENDA: "organizzazione con un nome: datore di lavoro, banca, negozio, scuola",
    SpanType.RUOLO: "mestiere o ruolo di una persona precisa",
    SpanType.CITTA: "città, paese o comune",
    SpanType.STRUTTURA: "sede o struttura precisa: ospedale, clinica, filiale, stabilimento",
    SpanType.IMPORTO: "somma di denaro, con la valuta",
    SpanType.DATA: "data di calendario, diversa dalla data di nascita",
    SpanType.ETA: "età",
    SpanType.NAZIONALITA: "nazionalità o cittadinanza",
    SpanType.SALUTE: "salute: diagnosi, malattia, terapia, disabilità, gravidanza",
    SpanType.RELIGIONE: "credo o pratica religiosa",
    SpanType.POLITICA: "opinione politica o iscrizione a un partito",
    SpanType.SINDACATO: "iscrizione o ruolo in un sindacato",
    SpanType.ORIENTAMENTO: "orientamento o vita sessuale",
    SpanType.ETNIA: "origine razziale o etnica",
    SpanType.BIOMETRICO: "dato biometrico o genetico",
    SpanType.GIUDIZIARIO: "condanne penali e reati",
    SpanType.UTENTE: "matricola aziendale, codice cliente, nome utente, numero di badge",
}

PROMPT = (
    "Nel testo qui sotto trova ogni espressione che, da sola o insieme ad altre, "
    "può aiutare a riconoscere chi scrive o le persone di cui parla, oppure rivela "
    "un dato particolare. Usa solo questi tipi:\n\n"
    + "\n".join(f"- {t.value}: {_TYPE_HELP[t]}" for t in TYPES)
    + "\n\nNon cercare nomi di persona, numeri di telefono, email, IBAN o codici "
    "fiscali: se ne occupa un altro strumento.\n\n"
    "Rispondi con un array JSON. Ogni elemento ha tre campi:\n"
    '- "text": l\'espressione copiata dal testo carattere per carattere, la più '
    "breve possibile, senza articoli o preposizioni;\n"
    '- "type": uno dei tipi elencati;\n'
    '- "reason": una frase breve che spiega perché.\n\n'
    "Esempio: "
    '[{"text": "magazziniere", "type": "RUOLO", "reason": "mestiere di chi scrive"}]\n'
    "Se non trovi nulla rispondi [].\n\n"
    "Testo:\n"
)

RETRY_NOTE = (
    "\n\nLa risposta precedente non era un array JSON valido. Rispondi soltanto con "
    'l\'array JSON, senza testo, senza commenti e senza ```. I campi sono "text", '
    '"type" e "reason", tutti stringhe non vuote.'
)


def _valid(reply: str) -> list[dict[str, str]] | None:
    """The items of `reply` when it is a JSON array that passes the schema, else None."""
    try:
        items = json.loads(reply)
    except json.JSONDecodeError:
        return None
    if not isinstance(items, list):
        return None
    allowed = {t.value for t in TYPES}
    for item in items:
        if not isinstance(item, dict) or set(item) != {"text", "type", "reason"}:
            return None
        if not all(isinstance(v, str) and v.strip() for v in item.values()):
            return None
        if item["type"] not in allowed:
            return None
    return items


def _occurrences(text: str, value: str) -> list[int]:
    """Where `value` is in `text` as a whole token: not inside a word or a number."""
    before = r"(?<![^\W_])" + (r"(?<!\d[.,])" if value[:1].isdigit() else "")
    after = r"(?![^\W_])" + (r"(?![.,]\d)" if value[-1:].isdigit() else "")
    return [m.start() for m in re.finditer(before + re.escape(value) + after, text)]


def find(text: str, config: RunConfig) -> list[Span]:
    """Spans found by the local LLM in `text`, possibly overlapping; `detect` merges them."""
    params = {"temperature": 0, "seed": config.seed, "max_tokens": MAX_TOKENS, **REASONING}
    items = None
    for attempt, prompt in enumerate((PROMPT + text, PROMPT + text + RETRY_NOTE)):
        stats["calls"] += 1
        if attempt:
            stats["retries"] += 1
        try:
            reply = complete(LLMRequest("d3", prompt, SYSTEM, params), config).text
        except TruncatedReplyError:  # cut at the token limit: an invalid reply like any other
            reply = ""
        items = _valid(reply)
        if items is not None:
            break
    if items is None:
        stats["failures"] += 1
        logger.error("D3: two invalid replies; returning no spans")
        return []

    spans = []
    for item in items:
        starts = _occurrences(text, item["text"])
        if not starts:
            stats["hallucinated"] += 1
            continue
        end = len(item["text"])
        spans.extend(
            Span(
                s, s + end, item["text"], SpanType(item["type"]), CONFIDENCE, SOURCE, item["reason"]
            )
            for s in starts
        )
    return spans
