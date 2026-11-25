"""Gradio demo: one text in two steps, so the user sees what is sent before it is sent.

Step 1, Protect: the request is checked (`feasibility.check_text`) and the text is
masked with `pipeline.mask`, with no call to the role `cloud`. The page shows the masked
text exactly as it would be sent, with the surrogates highlighted, and the table of what
was replaced. Step 2, Send: only if the text, the detector, the replacement, the backend
and the request are the ones that were previewed, and the text masks to the same result,
the text goes through `pipeline.protect_send_restore`; the page then shows the restored
reply and any restoration problem. It starts in replay mode: no network, answers from
`results/cache`. With backend `cloud` it reads and writes `results/scratch/app`, never
`results/cache`.

The request sent before the text is the field *Request*, the default task unless the
user writes another. A request for a calculation on masked amounts, dates or ages is not
sent: `feasibility.check_text` stops it and the page says why.

Run it with `make demo`. For backend `cloud` the key must be in the environment:
`uv run --env-file .env python -m omissis.app`.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

from omissis.backends import CacheMissError
from omissis.cli import DEFAULT_TASK
from omissis.config import ConfigError, RunConfig, load_config
from omissis.contracts import MaskResult, PipelineResult, RestoreOutcome, SpanType
from omissis.detect import supported_detectors
from omissis.eval.datasets import load_texts
from omissis.feasibility import check_text
from omissis.pipeline import mask, protect_send_restore
from omissis.vault import Vault

ROOT = Path(__file__).resolve().parents[2]
CONFIG_FILE = ROOT / "configs" / "app.yaml"
EXAMPLES_DIR = ROOT / "data" / "fixtures"
SCRATCH_CACHE = Path("results/scratch/app")
HEADERS = ["Surrogate", "Class", "Type", "Detector", "Reason", "Restoration"]
# The requests offered under the field: the default task, and one the check stops. They are
# prompts sent to the model, in Italian, and part of the cache keys.
REQUESTS = [[DEFAULT_TASK], ["Calcola il totale degli importi indicati nell'email."]]

PREVIEWED = "Nothing has been sent yet. Check the masked text, then press Send."

Segments = list[tuple[str, str | None]]


@dataclass(frozen=True)
class Preview:
    """What step 1 showed: the inputs it was run on and the masked text."""

    text: str
    detector: str
    strategy: str
    backend: str
    task: str
    masked_text: str


def segments(result: PipelineResult | MaskResult) -> Segments:
    """The masked text cut into pieces, each surrogate labelled with its type."""
    labels = {item.surrogate: item.type.value for item in result.disclosure}
    if not labels:
        return [(result.masked_text, None)]
    pattern = "|".join(re.escape(s) for s in sorted(labels, key=len, reverse=True))
    pieces = re.split(f"({pattern})", result.masked_text)
    return [(piece, labels.get(piece)) for piece in pieces if piece]


def rows(result: PipelineResult | MaskResult) -> list[list[str]]:
    """One row per disclosed surrogate, then one per token restoration could not place.

    Every event that is not `RESTORED` has its own row: the first one of a surrogate is
    shown on the row of that surrogate, the others (and the tokens that are not in the
    disclosure) in rows of their own.
    """
    problems: dict[str, list] = {}
    for event in getattr(result, "restore_events", ()):
        if event.outcome is not RestoreOutcome.RESTORED:
            problems.setdefault(event.surrogate, []).append(event)
    table = []
    for item in result.disclosure:
        events = problems.get(item.surrogate, [])
        event = events.pop(0) if events else None
        note = "" if event is None else event.outcome.value
        if event is not None and event.found_as:
            note += f" ({event.found_as})"
        table.append(
            [item.surrogate, item.cls.value, item.type.value, item.source, item.reason or "", note]
        )
    for events in problems.values():
        for event in events:
            table.append([event.found_as or event.surrogate, "", "", "", "", event.outcome.value])
    return table


def refusal(blocked: dict[SpanType, int]) -> str:
    """Why a request is not sent: the masked types and their counts, never a value."""
    kinds = ", ".join(f"{count} {kind.value}" for kind, count in blocked.items())
    return (
        "Request not sent: it asks for a calculation, but the text holds masked values that "
        f"the cloud model does not see ({kinds}). With placeholders it would have no numbers; "
        "with fake values it would compute a wrong result that cannot be restored. This "
        "request can only be answered locally."
    )


def _failure(exc: Exception) -> str:
    """The message for an error of a step. `ConfigError` is a `ValueError`; a cache miss and
    `NotImplementedError` are `RuntimeError`s: the order of the tests matters."""
    if isinstance(exc, CacheMissError):
        return (
            "This text is not in the cache with this combination: replay mode does not use "
            "the network. Choose a recorded example, or the cloud backend."
        )
    if isinstance(exc, NotImplementedError):
        return f"Not available yet: {exc}"
    if isinstance(exc, ConfigError):
        return f"Invalid configuration: {exc}"
    if isinstance(exc, RuntimeError):
        return f"The call to the model failed: {exc}"
    return f"The run failed: {exc}"


def _config(detector: str, strategy: str, backend: str) -> RunConfig:
    cache = {"cache_dir": str(SCRATCH_CACHE)} if backend == "cloud" else {}
    overrides = {"detector": detector, "strategy": strategy, "backend": backend, **cache}
    return load_config(CONFIG_FILE, overrides)


def _task(task: str | None) -> str:
    return task.strip() if task and task.strip() else DEFAULT_TASK


def _masked(text: str, config: RunConfig) -> MaskResult:
    """`pipeline.mask` with no call to the role `cloud`; its vault is erased at once."""
    vault = Vault()
    try:
        result, _ = mask(text, config, None, vault)
    finally:
        vault.clear()
    return result


def protect(
    text: str, detector: str, strategy: str, backend: str, task: str = DEFAULT_TASK
) -> tuple[Segments, str, list[list[str]], str, Preview | None]:
    """Step 1: check the request, mask the text and show it. Nothing is sent.

    Returns the masked pieces, an empty reply, the table (restoration column empty), a
    message and the preview to keep in the page state (None when there is nothing to send).
    """
    if not text or not text.strip():
        return [], "", [], "Write or choose a text.", None
    task = _task(task)
    try:
        config = _config(detector, strategy, backend)
        blocked = check_text(text, task, config)
        if blocked:
            return [], "", [], refusal(blocked), None
        result = _masked(text, config)
    except (RuntimeError, ValueError, OSError) as exc:
        return [], "", [], _failure(exc), None
    preview = Preview(text, detector, strategy, backend, task, result.masked_text)
    return segments(result), "", rows(result), PREVIEWED, preview


def send(
    text: str,
    detector: str,
    strategy: str,
    backend: str,
    task: str = DEFAULT_TASK,
    preview: Preview | None = None,
) -> tuple[Segments, str, list[list[str]], str]:
    """Step 2: send what step 1 showed, through `pipeline.protect_send_restore`.

    Refused when there is no preview or when any input differs from the previewed one.
    The text is masked again and compared with the preview: if it differs, nothing is
    sent. Returns the masked pieces, the restored reply, the table and a message.
    """
    if preview is None:
        return [], "", [], "Nothing to send: press Protect first."
    task = _task(task)
    if (text, detector, strategy, backend, task) != (
        preview.text,
        preview.detector,
        preview.strategy,
        preview.backend,
        preview.task,
    ):
        return (
            [],
            "",
            [],
            (
                "Nothing sent: the text, the detector, the replacement, the backend or the "
                "request changed after the preview. Press Protect again."
            ),
        )
    try:
        config = _config(detector, strategy, backend)
        if _masked(text, config).masked_text != preview.masked_text:
            return (
                [],
                "",
                [],
                (
                    "Nothing sent: the masked text is not the one that was previewed. "
                    "Press Protect again."
                ),
            )
        result = protect_send_restore(text, task, config)
    except (RuntimeError, ValueError, OSError) as exc:
        return [], "", [], _failure(exc)
    status = "Fully restored." if result.fully_restored else "Not fully restored: see the table."
    return segments(result), result.restored_reply, rows(result), f"{status} Run {result.run_id}."


def build():
    """The Gradio page."""
    import gradio as gr

    detectors = [d.value for d in supported_detectors()]
    examples = [[record.text] for record in load_texts(EXAMPLES_DIR)]
    with gr.Blocks(title="Omissis") as page:
        gr.Markdown(
            "# Omissis\nThe text is pseudonymised before it is sent to the model; the real "
            "values are restored in the reply. Pseudonymisation lowers the re-identification "
            "risk, it does not remove it.\n\n"
            "With detectors D3 and D4 the whole text, not yet pseudonymised, is first read by "
            "the model of role `d3`: if that model is hosted by an external service, the text "
            "leaves this machine at that step.\n\n"
            "A request for a calculation on masked amounts, dates or ages is not sent: the "
            "model would not see the real values."
        )
        with gr.Row():
            detector = gr.Dropdown(detectors, value=detectors[0], label="Detector")
            strategy = gr.Dropdown(["R1", "R2"], value="R1", label="Replacement")
            backend = gr.Dropdown(["replay", "cloud"], value="replay", label="Backend")
        text = gr.Textbox(lines=12, label="Text")
        gr.Examples(examples, inputs=text, label="Examples (synthetic texts)")
        task = gr.Textbox(
            lines=2,
            value=DEFAULT_TASK,
            label="Request",
            info="Sent as written, before the text. It is not masked: do not write personal "
            "data here.",
        )
        gr.Examples(REQUESTS, inputs=task, label="Example requests")
        with gr.Row():
            protect_button = gr.Button("1 · Protect", variant="primary")
            send_button = gr.Button("2 · Send", interactive=False)
        state = gr.State(None)
        message = gr.Markdown()
        masked = gr.HighlightedText(
            label="Text that will be sent to the model", combine_adjacent=False
        )
        reply = gr.Textbox(lines=12, label="Reply with the real values restored")
        table = gr.Dataframe(headers=HEADERS, label="What was replaced", wrap=True)

        def on_protect(*args):
            *shown, preview = protect(*args)
            return *shown, preview, gr.update(interactive=preview is not None)

        protect_button.click(
            on_protect,
            [text, detector, strategy, backend, task],
            [masked, reply, table, message, state, send_button],
        )
        send_button.click(
            send,
            [text, detector, strategy, backend, task, state],
            [masked, reply, table, message],
        )
    return page


def main() -> None:
    os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")  # no network at start-up
    build().launch()


if __name__ == "__main__":
    main()
