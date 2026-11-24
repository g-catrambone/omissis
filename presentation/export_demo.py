"""Export the recorded demo runs (replay mode, no network) to presentation/demo-data.js.

For each synthetic fixture in data/fixtures, every supported detector and R1/R2:
the spans found on the original text, the masked text, the disclosure table, the raw
reply of the cloud model (as it came back, still masked), the restored reply and the
restoration events. Also the feasibility check of the calculation request.
Run from the repository root: uv run --group detect python presentation/export_demo.py
(needs the detect group and the D2 weights; it reads results/cache and writes nothing there)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from omissis.app import REQUESTS, _config, _masked
from omissis.backends import CacheMissError
from omissis.cli import DEFAULT_TASK
from omissis.detect import supported_detectors
from omissis.eval.datasets import load_texts
from omissis.feasibility import check_text
from omissis.pipeline import mask, protect_send_restore

ROOT = Path.cwd()
OUT = ROOT / "presentation" / "demo-data.js"
CALC = REQUESTS[1][0]


def span_dict(s):
    return {
        "start": s.start,
        "end": s.end,
        "text": s.text,
        "type": s.type.value,
        "cls": s.cls.value,
        "source": s.source,
    }


def main() -> int:
    detectors = [d.value for d in supported_detectors()]
    print("detectors:", detectors, file=sys.stderr)
    fixtures = []
    for record in load_texts(ROOT / "data" / "fixtures"):
        runs = {}
        for det in detectors:
            for strat in ("R1", "R2"):
                key = f"{det}+{strat}"
                config = _config(det, strat, "replay")
                try:
                    m = _masked(record.text, config)
                    r = protect_send_restore(record.text, DEFAULT_TASK, config)
                    # the same masking again, to show each surrogate next to its value
                    # (synthetic fixtures only: every value is already in the text)
                    _, vault = mask(record.text, config)
                    values = {e.surrogate: e.original for e in vault}
                except CacheMissError as exc:
                    print(f"{record.id} {key}: cache miss ({exc})", file=sys.stderr)
                    continue
                runs[key] = {
                    "spans": [span_dict(s) for s in m.spans],
                    "masked": r.masked_text,
                    "disclosure": [
                        {
                            "surrogate": d.surrogate,
                            "value": values.get(d.surrogate, ""),
                            "type": d.type.value,
                            "cls": d.cls.value,
                            "source": d.source,
                            "reason": d.reason or "",
                        }
                        for d in r.disclosure
                    ],
                    "raw_reply": r.raw_reply,
                    "restored": r.restored_reply,
                    "events": [
                        {
                            "surrogate": e.surrogate,
                            "outcome": e.outcome.value,
                            "found_as": e.found_as or "",
                        }
                        for e in r.restore_events
                    ],
                    "fully_restored": r.fully_restored,
                    "run_id": r.run_id,
                }
                print(f"{record.id} {key}: ok", file=sys.stderr)
        calc = {}
        for det in detectors:
            blocked = check_text(record.text, CALC, _config(det, "R1", "replay"))
            calc[det] = {k.value: v for k, v in blocked.items()} if blocked else {}
        fixtures.append(
            {
                "id": record.id,
                "domain": record.domain,
                "scenario": record.scenario,
                "text": record.text,
                "runs": runs,
                "calc_blocked": calc,
            }
        )
    data = {"task": DEFAULT_TASK, "calc_task": CALC, "detectors": detectors, "fixtures": fixtures}
    OUT.write_text(
        "window.DEMO = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8"
    )
    print("written", OUT, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
