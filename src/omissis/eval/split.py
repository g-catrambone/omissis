"""`make split` (task 3.5; protocol, section 4). HUMANS ONLY: it is run once.

20 texts go to dev and 46 to test. The pilot texts go to dev; the others are split by
seed, stratified by `domain` x `has_special`, so that dev reaches 20. Every text must
have been reviewed (`reviewed_by`). The command writes the dev and the test folder
under `data/` and `data/split.json` with the checksum of every file, and empties
`data/pool/`.

After it has run, no agent opens the test folder.
"""

from __future__ import annotations

import hashlib
import json
import random
import sys
from pathlib import Path
from typing import Any

from omissis.eval import profiles as planning
from omissis.eval.datasets import TextRecord, load_texts

DEV = 20
TOTAL = 66


def choose_dev(
    records: list[TextRecord], plan: dict[str, dict[str, Any]], seed: int, dev: int = DEV
) -> list[str]:
    """The ids of the dev texts: every pilot text, then a stratified draw of the others."""
    pilot = sorted(r.id for r in records if plan[r.id]["pilot"])
    rest = [r for r in records if not plan[r.id]["pilot"]]
    need = dev - len(pilot)
    if need < 0:
        raise ValueError(f"{len(pilot)} pilot texts, more than the {dev} of dev")
    strata: dict[tuple[str, bool], list[str]] = {}
    for record in rest:
        strata.setdefault((record.domain, record.has_special), []).append(record.id)
    # Largest remainders: each stratum gives its share of the texts still needed.
    shares = {key: need * len(ids) / len(rest) for key, ids in strata.items()}
    take = {key: int(share) for key, share in shares.items()}
    by_remainder = sorted(strata, key=lambda key: (-(shares[key] - take[key]), key))
    for key in by_remainder[: need - sum(take.values())]:
        take[key] += 1
    rng = random.Random(f"{seed}|split")
    chosen = [t for key in sorted(strata) for t in rng.sample(sorted(strata[key]), take[key])]
    return sorted(pilot + chosen)


def split(pool: Path, data: Path, plan: dict[str, dict[str, Any]], seed: int) -> dict[str, Any]:
    """Move the pool into the dev and test folders of `data` and write `split.json`."""
    if (data / "split.json").exists():
        raise RuntimeError(f"{data / 'split.json'} exists: the split is made once")
    records = load_texts(pool)
    if len(records) != TOTAL or {r.id for r in records} != set(plan):
        raise RuntimeError(
            f"{pool} must hold exactly the {TOTAL} planned texts, found {len(records)}"
        )
    unreviewed = [r.id for r in records if not r.reviewed_by]
    if unreviewed:
        raise RuntimeError(f"texts without reviewed_by cannot enter the split: {unreviewed}")
    dev = choose_dev(records, plan, seed)
    manifest: dict[str, Any] = {"seed": seed, "dev": dev, "test": [], "sha256": {}}
    for name in ("dev", "test"):
        (data / name).mkdir(parents=True, exist_ok=False)
    for record in records:
        source = pool / f"{record.id}.json"
        target = "dev" if record.id in dev else "test"
        if target == "test":
            manifest["test"].append(record.id)
        manifest["sha256"][record.id] = hashlib.sha256(source.read_bytes()).hexdigest()
        source.rename(data / target / source.name)
    (data / "split.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    plan = planning.build()["plan.json"]
    try:
        manifest = split(Path("data/pool"), Path("data"), plan, planning.SEED)
    except RuntimeError as exc:
        print(f"split: {exc}", file=sys.stderr)
        return 2
    print(f"dev: {len(manifest['dev'])} texts, test: {len(manifest['test'])} texts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
