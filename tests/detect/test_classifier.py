"""D2 ready-made classifier (task 4.2).

The grouping and the stitching of windows are tested on hand-written tokens. The
tests on the real model run only where the dependency group `detect` is installed,
the role `d2` is pinned in `configs/models.yaml` and its weights are in the local
Hugging Face cache: no test downloads a model.
"""

from pathlib import Path

import pytest

from omissis.config import ConfigError, load_config, load_models, with_overrides
from omissis.contracts import DetectorId, SpanType
from omissis.detect import classifier, detect, supported_detectors
from omissis.eval.datasets import load_texts

REPO = Path(__file__).resolve().parents[2]
MODELS_FILE = REPO / "configs" / "models.yaml"
TEXT = "Sono Lidia Caprioli, via dei Tigli 14 a Bergamo."


def tokens(text, *labelled):
    """Tokens for `text`: one per word given as (word, label, score), in order."""
    out, at = [], 0
    for word, label, score in labelled:
        start = text.index(word, at)
        at = start + len(word)
        out.append((start, at, label, score))
    return out


# --- grouping --------------------------------------------------------------------


def test_neighbouring_tokens_of_one_type_become_one_span():
    spans = classifier._group(
        TEXT,
        tokens(
            TEXT,
            ("Sono", "O", 0.99),
            (" Lidia", "I-GIVENNAME", 0.9),  # the token carries its leading space
            (" Capri", "I-SURNAME", 1.0),
            ("oli", "I-SURNAME", 0.8),
            (",", "O", 0.99),
            (" via", "I-STREET", 0.9),
            (" dei", "I-STREET", 0.9),
            (" Tigli", "I-STREET", 0.9),
            (" 14", "I-BUILDINGNUM", 0.9),
            (" a", "O", 0.99),
            (" Bergamo", "I-CITY", 0.7),
        ),
    )
    assert [(s.type, s.text, s.start) for s in spans] == [
        (SpanType.PERSONA, "Lidia Caprioli", 5),
        (SpanType.INDIRIZZO, "via dei Tigli 14", 21),
        (SpanType.CITTA, "Bergamo", 40),
    ]
    assert spans[0].confidence == pytest.approx(0.9)  # mean of 0.9, 1.0, 0.8
    assert all(s.source == "D2" and s.matches(TEXT) for s in spans)


def test_same_type_across_other_text_stays_two_spans():
    text = "Lidia e Bruno"
    found = classifier._group(
        text, tokens(text, ("Lidia", "I-GIVENNAME", 1.0), (" Bruno", "I-GIVENNAME", 1.0))
    )
    assert [s.text for s in found] == ["Lidia", "Bruno"]


def test_label_without_counterpart_is_ignored_and_ends_a_span():
    text = "utente lidia84 segreto99 mario"
    found = classifier._group(
        text,
        tokens(
            text,
            (" lidia84", "I-USERNAME", 1.0),
            (" segreto99", "I-PASSWORD", 1.0),
            (" mario", "I-USERNAME", 1.0),
        ),
    )
    assert [(s.type, s.text) for s in found] == [
        (SpanType.UTENTE, "lidia84"),
        (SpanType.UTENTE, "mario"),
    ]


def test_token_of_white_space_only_gives_no_span():
    assert classifier._group("a  b", [(1, 3, "I-CITY", 1.0)]) == []
    assert classifier._group("", []) == []


def test_every_mapped_type_exists_and_password_is_not_mapped():
    assert "PASSWORD" not in classifier.LABEL_TO_TYPE
    assert all(isinstance(t, SpanType) for t in classifier.LABEL_TO_TYPE.values())


# --- windows ---------------------------------------------------------------------


def test_token_in_two_windows_keeps_the_prediction_farther_from_the_edge():
    # Six tokens of two characters; two windows of four tokens share tokens 2 and 3.
    first = [(0, 2, "O", 1.0), (2, 4, "O", 1.0), (4, 6, "I-CITY", 0.6), (6, 8, "O", 0.9)]
    second = [(4, 6, "O", 0.9), (6, 8, "I-CITY", 0.7), (8, 10, "O", 1.0), (10, 12, "O", 1.0)]
    stitched = classifier._stitch([first, second])
    assert [t[:2] for t in stitched] == [(0, 2), (2, 4), (4, 6), (6, 8), (8, 10), (10, 12)]
    # Token (4, 6) is third of four in the first window and first in the second.
    assert stitched[2] == (4, 6, "I-CITY", 0.6)
    assert stitched[3] == (6, 8, "I-CITY", 0.7)


def test_single_window_is_returned_unchanged():
    window = [(0, 2, "O", 1.0), (3, 5, "I-CITY", 0.8)]
    assert classifier._stitch([window]) == window
    assert classifier._stitch([]) == []


# --- configuration ---------------------------------------------------------------


def test_unpinned_d2_is_a_config_error(tmp_path):
    config = with_overrides(load_config(REPO / "configs" / "skeleton.yaml"))
    unpinned = tmp_path / "models.yaml"
    echo = (REPO / "configs" / "models.echo.yaml").read_text(encoding="utf-8")
    head, _, _ = echo.partition("d2:")
    unpinned.write_text(
        head + "d2:\n  provider: TO_BE_PINNED\n  id: TO_BE_PINNED\n  revision: TO_BE_PINNED\n",
        encoding="utf-8",
    )
    with pytest.raises(ConfigError, match="d2"):
        classifier.find(TEXT, with_overrides(config, models_file=unpinned))


def test_weights_not_on_disk_are_a_config_error_not_a_download():
    pytest.importorskip("transformers")
    pytest.importorskip("torch")
    with pytest.raises(ConfigError, match="hf download"):
        classifier._load("omissis/no-such-model", "0" * 40)


# --- the real model --------------------------------------------------------------


@pytest.fixture(scope="module")
def config():
    pytest.importorskip("transformers")
    pytest.importorskip("torch")
    model = load_models(MODELS_FILE)["d2"]
    if not model.pinned:
        pytest.skip("role d2 is not pinned in configs/models.yaml")
    try:
        classifier._load(model.id, model.revision)
    except ConfigError:
        pytest.skip("the weights of d2 are not on this machine")
    return load_config(REPO / "configs" / "skeleton.yaml", {"models_file": str(MODELS_FILE)})


def test_d2_and_d4_are_supported_here(config):
    assert {DetectorId.D2, DetectorId.D4} <= set(supported_detectors())


def test_italian_name_and_city_are_found(config):
    spans = detect("Mi chiamo Lidia Caprioli e abito a Bergamo.", DetectorId.D2, config)
    assert [(s.type, s.text) for s in spans] == [
        (SpanType.PERSONA, "Lidia Caprioli"),
        (SpanType.CITTA, "Bergamo"),
    ]


def test_text_longer_than_one_window_has_correct_offsets_across_the_border(config):
    records = load_texts(REPO / "data" / "fixtures")
    text = "\n\n".join(r.text for r in records)
    model = load_models(MODELS_FILE)["d2"]
    windows = classifier._windows(text, model.id, model.revision)
    assert len(windows) > 1
    first_end, second_start = windows[0][-1][1], windows[1][0][0]
    assert second_start < first_end  # the windows overlap

    spans = detect(text, DetectorId.D2, config)
    assert all(s.matches(text) for s in spans)
    found = {(s.type, s.text, s.start) for s in spans}
    # The signature of the first email lies in the stretch shared by two windows,
    # the sender of the second email lies beyond the first window.
    signature = text.index("Lidia Caprioli", second_start)
    assert second_start <= signature < first_end
    assert (SpanType.PERSONA, "Lidia Caprioli", signature) in found
    sender = text.index("Bruno Ferraguti")
    assert sender > first_end
    assert (SpanType.PERSONA, "Bruno Ferraguti", sender) in found


@pytest.mark.parametrize("text", ["", " ", "\n\t", "🙂" * 20])
def test_odd_text_gives_no_error(config, text):
    assert all(s.matches(text) for s in detect(text, DetectorId.D2, config))
