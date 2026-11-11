import logging

import pytest

from omissis.contracts import SpanType, VaultEntry
from omissis.vault import Vault

# Synthetic values only.
ORIGINALS = ("Marco Ferri", "Ferri", "IT00X0000000000000000123456")


def entries():
    return [
        VaultEntry(
            "[PERSONA_1_M]",
            ORIGINALS[0],
            SpanType.PERSONA,
            "PERSONA_1",
            original_variants=(ORIGINALS[1],),
        ),
        VaultEntry("[IBAN_1]", ORIGINALS[2], SpanType.IBAN, "IBAN_1"),
    ]


def filled():
    vault = Vault()
    for entry in entries():
        vault.add(entry)
    return vault


def test_add_get_contains_len_iter():
    vault = filled()
    assert len(vault) == 2
    assert "[IBAN_1]" in vault and "[IBAN_2]" not in vault
    assert vault.get("[IBAN_1]").original == ORIGINALS[2]
    assert vault.get("[IBAN_2]") is None
    assert [e.surrogate for e in vault] == ["[PERSONA_1_M]", "[IBAN_1]"]


def test_add_rejects_existing_surrogate():
    vault = filled()
    with pytest.raises(ValueError):
        vault.add(VaultEntry("[IBAN_1]", "IT00", SpanType.IBAN, "IBAN_2"))


def test_surrogate_for():
    vault = filled()
    assert vault.surrogate_for("PERSONA_1") == "[PERSONA_1_M]"
    assert vault.surrogate_for("PERSONA_9") is None


def test_clear():
    vault = filled()
    vault.clear()
    assert len(vault) == 0 and list(vault) == []


def test_repr_and_str_show_count_only():
    vault = filled()
    assert repr(vault) == str(vault) == "Vault(2 entries)"


def test_entry_repr_hides_originals():
    for entry in entries():
        shown = repr(entry) + str(entry) + f"{entry}"
        assert entry.surrogate in shown
        assert not any(original in shown for original in ORIGINALS)


def test_logs_never_show_originals(caplog):
    vault = filled()
    logger = logging.getLogger("omissis.test")
    with caplog.at_level(logging.DEBUG):
        logger.debug("vault %s %r", vault, vault)
        logger.debug("entries %s", list(vault))
        for entry in vault:
            logger.info("entry %s %r", entry, entry)
    assert caplog.text
    assert not any(original in caplog.text for original in ORIGINALS)
