"""D0 on the fixture emails: every gold span of a D0 type is found exactly, nothing else."""

from pathlib import Path

import pytest

from omissis.config import load_config
from omissis.contracts import DetectorId, SpanType
from omissis.detect import detect
from omissis.eval.datasets import load_texts

REPO = Path(__file__).resolve().parents[2]
D0_TYPES = {
    SpanType.IBAN,
    SpanType.CF,
    SpanType.PIVA,
    SpanType.TELEFONO,
    SpanType.EMAIL,
    SpanType.IMPORTO,
}
RECORDS = load_texts(REPO / "data" / "fixtures")


@pytest.mark.parametrize("record", RECORDS, ids=[r.id for r in RECORDS])
def test_d0_on_fixture(record):
    config = load_config(REPO / "configs" / "skeleton.yaml")
    found = {(s.start, s.end, s.type) for s in detect(record.text, DetectorId.D0, config)}
    gold = {(s.start, s.end, s.type) for s in record.spans if s.type in D0_TYPES}
    assert found == gold
