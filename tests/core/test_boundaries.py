"""The boundary functions keep the exact signatures of docs/interfaces.md, section 3."""

import inspect

import pytest

from omissis import backends, pipeline
from omissis.detect import detect
from omissis.replace import replace
from omissis.resolve import resolve
from omissis.restore import restore

# (function, parameter names in order, parameters with a default of None)
SIGNATURES = [
    (detect, ["text", "detector", "config"], []),
    (resolve, ["spans", "text"], []),
    (replace, ["text", "entities", "strategy", "seed", "vault"], ["vault"]),
    (restore, ["reply", "vault", "fuzzy_threshold"], []),
    (backends.complete, ["request", "config"], []),
    (backends.register_provider, ["name", "fn"], []),
    (pipeline.mask, ["text", "config", "gold_spans", "vault"], ["gold_spans", "vault"]),
    (pipeline.protect_send_restore, ["text", "task", "config"], []),
]


@pytest.mark.parametrize(
    ("fn", "names", "optional"), SIGNATURES, ids=lambda x: getattr(x, "__qualname__", "")
)
def test_signature(fn, names, optional):
    params = inspect.signature(fn).parameters
    assert list(params) == names
    for name, param in params.items():
        if name in optional:
            assert param.default is None
        else:
            assert param.default is inspect.Parameter.empty
    assert fn.__doc__


def test_keep_placeholders_instruction():
    text = pipeline.KEEP_PLACEHOLDERS_INSTRUCTION
    assert "[PERSONA_1_M]" in text and "[IBAN_1]" in text
    assert text.startswith("Il testo contiene segnaposto")
