"""Gradio demo (task 2.7): one text through `pipeline.protect_send_restore`.

The page shows the masked text exactly as it is sent, with the surrogates
highlighted, the restored reply and the disclosure list with any restoration
problem. It starts in replay mode: no network, answers from `results/cache`. With
backend `cloud` it reads and writes `results/scratch/app`, never `results/cache`.

The request sent before the text is the field *Richiesta*, the default task unless the
user writes another. A request for a calculation on masked amounts, dates or ages is not
sent: `feasibility.check_text` stops it and the page says why.

Run it with `make demo`. For backend `cloud` the key must be in the environment:
`uv run --env-file .env python -m omissis.app`.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from omissis.backends import CacheMissError
from omissis.cli import DEFAULT_TASK
from omissis.config import ConfigError, load_config
from omissis.contracts import PipelineResult, RestoreOutcome, SpanType
from omissis.detect import supported_detectors
from omissis.eval.datasets import load_texts
from omissis.feasibility import check_text
from omissis.pipeline import protect_send_restore

ROOT = Path(__file__).resolve().parents[2]
CONFIG_FILE = ROOT / "configs" / "app.yaml"
EXAMPLES_DIR = ROOT / "data" / "fixtures"
SCRATCH_CACHE = Path("results/scratch/app")
HEADERS = ["Surrogate", "Class", "Type", "Detector", "Reason", "Restoration"]
# The requests offered under the field: the default task, and one the check stops.
REQUESTS = [[DEFAULT_TASK], ["Calcola il totale degli importi indicati nell'email."]]

Segments = list[tuple[str, str | None]]


def segments(result: PipelineResult) -> Segments:
    """The masked text cut into pieces, each surrogate labelled with its type."""
    labels = {item.surrogate: item.type.value for item in result.disclosure}
    if not labels:
        return [(result.masked_text, None)]
    pattern = "|".join(re.escape(s) for s in sorted(labels, key=len, reverse=True))
    pieces = re.split(f"({pattern})", result.masked_text)
    return [(piece, labels.get(piece)) for piece in pieces if piece]


def rows(result: PipelineResult) -> list[list[str]]:
    """One row per disclosed surrogate, then one per token restoration could not place."""
    problems = {
        event.surrogate: event
        for event in result.restore_events
        if event.outcome is not RestoreOutcome.RESTORED
    }
    table = []
    for item in result.disclosure:
        event = problems.pop(item.surrogate, None)
        note = "" if event is None else event.outcome.value
        if event is not None and event.found_as:
            note += f" ({event.found_as})"
        table.append(
            [item.surrogate, item.cls.value, item.type.value, item.source, item.reason or "", note]
        )
    for event in problems.values():
        table.append([event.found_as or event.surrogate, "", "", "", "", event.outcome.value])
    return table


def refusal(blocked: dict[SpanType, int]) -> str:
    """Why a request is not sent: the masked types and their counts, never a value."""
    kinds = ", ".join(f"{count} {kind.value}" for kind, count in blocked.items())
    return (
        "Richiesta non inviata: chiede un calcolo, ma nel testo sono mascherati valori "
        f"che il modello cloud non vede ({kinds}). Con i segnaposto non avrebbe numeri; "
        "con i valori fittizi calcolerebbe un risultato sbagliato, che non si può "
        "ripristinare. Questa richiesta si può soddisfare solo in locale."
    )


def process(
    text: str, detector: str, strategy: str, backend: str, task: str = DEFAULT_TASK
) -> tuple[Segments, str, list[list[str]], str]:
    """Run one text with the request `task`: masked pieces, restored reply, disclosure
    rows, a message. A request that the feasibility check stops is not sent."""
    if not text or not text.strip():
        return [], "", [], "Scrivi o scegli un testo."
    task = task.strip() if task and task.strip() else DEFAULT_TASK
    cache = {"cache_dir": str(SCRATCH_CACHE)} if backend == "cloud" else {}
    try:
        config = load_config(
            CONFIG_FILE, {"detector": detector, "strategy": strategy, "backend": backend, **cache}
        )
        blocked = check_text(text, task, config)
        if blocked:
            return [], "", [], refusal(blocked)
        result = protect_send_restore(text, task, config)
    except CacheMissError:
        return (
            [],
            "",
            [],
            (
                "Questo testo non è nella cache con questa combinazione: la modalità replay "
                "non usa la rete. Scegli un esempio registrato oppure il backend cloud."
            ),
        )
    except NotImplementedError as exc:
        return [], "", [], f"Non ancora disponibile: {exc}"
    except ConfigError as exc:
        return [], "", [], f"Configurazione non valida: {exc}"
    except RuntimeError as exc:
        return [], "", [], f"La chiamata al modello non è riuscita: {exc}"
    status = (
        "Ripristino completo." if result.fully_restored else "Ripristino incompleto: vedi tabella."
    )
    return segments(result), result.restored_reply, rows(result), f"{status} Run {result.run_id}."


def build():
    """The Gradio page."""
    import gradio as gr

    detectors = [d.value for d in supported_detectors()]
    examples = [[record.text] for record in load_texts(EXAMPLES_DIR)]
    with gr.Blocks(title="Omissis") as page:
        gr.Markdown(
            "# Omissis\nIl testo viene pseudonimizzato prima di essere inviato al modello; "
            "nella risposta i valori reali vengono ripristinati. La pseudonimizzazione "
            "riduce il rischio di re-identificazione, non lo elimina.\n\n"
            "Con i detector D3 e D4 il testo intero, non ancora pseudonimizzato, viene prima "
            "letto dal modello del ruolo `d3`: se quel modello è ospitato da un servizio "
            "esterno, in quel passaggio il testo lascia questa macchina.\n\n"
            "Una richiesta di calcolo su importi, date o età mascherati non viene inviata: "
            "il modello non vedrebbe i valori reali."
        )
        with gr.Row():
            detector = gr.Dropdown(detectors, value=detectors[0], label="Detector")
            strategy = gr.Dropdown(["R1", "R2"], value="R1", label="Sostituzione")
            backend = gr.Dropdown(["replay", "cloud"], value="replay", label="Backend")
        text = gr.Textbox(lines=12, label="Testo")
        gr.Examples(examples, inputs=text, label="Esempi (testi sintetici)")
        task = gr.Textbox(lines=2, value=DEFAULT_TASK, label="Richiesta")
        gr.Examples(REQUESTS, inputs=task, label="Richieste di esempio")
        button = gr.Button("Proteggi e invia", variant="primary")
        message = gr.Markdown()
        masked = gr.HighlightedText(label="Testo inviato al modello", combine_adjacent=False)
        reply = gr.Textbox(lines=12, label="Risposta con i valori ripristinati")
        table = gr.Dataframe(headers=HEADERS, label="Che cosa è stato sostituito", wrap=True)
        button.click(
            process,
            [text, detector, strategy, backend, task],
            [masked, reply, table, message],
        )
    return page


def main() -> None:
    os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")  # no network at start-up
    build().launch()


if __name__ == "__main__":
    main()
