"""Loaders for texts with gold and for profiles (block 1; formats in docs/interfaces.md, section 5).

Every check here is a rule of the file format or of docs/evaluation_protocol.md,
sections 2 and 3. A file that breaks one raises `DataError` naming the file.
Loaded spans get `confidence=1.0` and `source="GOLD"`.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from omissis.contracts import GOLD_SOURCE, TYPE_CLASS, Gender, Span, SpanClass, SpanType

# Scenario (= intent) -> (domain, allowed requested_action), protocol section 2.
SCENARIOS: dict[str, tuple[str, tuple[str, ...]]] = {
    "mortgage_suspension": ("bank", ("suspend_payment", "reschedule_payment")),
    "card_dispute": ("bank", ("refund", "open_investigation")),
    "iban_change": ("bank", ("update_details", "send_information")),
    "loan_early_repayment": ("bank", ("send_information", "close_account")),
    "account_closure": ("bank", ("close_account", "release_funds")),
    "fee_complaint": ("bank", ("refund", "schedule_meeting")),
    "inheritance_unblock": ("bank", ("release_funds", "send_information")),
    "sick_leave": ("hr", ("register_absence", "approve_request")),
    "remote_work_request": ("hr", ("approve_request", "schedule_meeting")),
    "harassment_complaint": ("hr", ("open_investigation", "schedule_meeting")),
    "medical_reimbursement": ("hr", ("refund", "send_information")),
    "transfer_request": ("hr", ("approve_request", "schedule_meeting")),
    "union_leave": ("hr", ("approve_request", "register_absence")),
}

_TEXT_KEYS = {"id", "domain", "scenario", "profile_id", "has_special", "text", "spans", "gold"}
_SPAN_KEYS = {"start", "end", "text", "type"}
_GOLD_KEYS = {"intent", "amounts", "dates", "requested_action", "deadline"}
_PROFILE_KEYS = {
    "id",
    "cohort",
    "name",
    "gender",
    "age",
    "city",
    "employer",
    "role",
    "bank",
    "branch_city",
    "financial",
    "special",
}


class DataError(ValueError):
    """A text or profile file breaks the format."""


@dataclass(frozen=True)
class Gold:
    intent: str
    amounts: tuple[float, ...]
    dates: tuple[str, ...]
    requested_action: str
    deadline: str | None


@dataclass(frozen=True)
class TextRecord:
    id: str
    domain: str
    scenario: str
    profile_id: str
    has_special: bool
    text: str
    spans: tuple[Span, ...]
    gold: Gold
    reviewed_by: str | None = None


@dataclass(frozen=True)
class Profile:
    id: str
    cohort: str
    name: str
    gender: Gender
    age: int
    city: str
    employer: str
    role: str
    bank: str
    branch_city: str
    financial: dict[str, Any]
    special: dict[str, str] | None


def load_text(path: str | Path) -> TextRecord:
    """Load and validate one text file `<text_id>.json`."""
    path = Path(path)
    data = _read_json(path)

    def fail(message: str) -> DataError:
        return DataError(f"{path}: {message}")

    if not isinstance(data, dict):
        raise fail("a text file must be a JSON object")
    keys = set(data)
    if missing := sorted(_TEXT_KEYS - keys):
        raise fail(f"missing keys {missing}")
    if unknown := sorted(keys - _TEXT_KEYS - {"reviewed_by"}):
        raise fail(f"unknown keys {unknown}")
    for key in ("id", "domain", "scenario", "profile_id", "text"):
        if not isinstance(data[key], str) or not data[key]:
            raise fail(f"{key} must be a non-empty string")
    if data["id"] != path.stem:
        raise fail(f"id {data['id']!r} does not match the file name")
    if data["scenario"] not in SCENARIOS:
        raise fail(f"unknown scenario {data['scenario']!r}")
    domain, actions = SCENARIOS[data["scenario"]]
    if data["domain"] != domain:
        raise fail(f"scenario {data['scenario']!r} belongs to domain {domain!r}")
    if not isinstance(data["has_special"], bool):
        raise fail("has_special must be a boolean")
    reviewed_by = data.get("reviewed_by")
    if "reviewed_by" in data and (not isinstance(reviewed_by, str) or not reviewed_by.strip()):
        raise fail("reviewed_by, when present, must hold the reviewer's initials")

    text = data["text"]
    spans = _load_spans(data["spans"], text, fail)
    if data["has_special"] != any(s.cls is SpanClass.SPECIAL for s in spans):
        raise fail("has_special must be true exactly when a special-category span is tagged")
    gold = _load_gold(data["gold"], data["scenario"], actions, fail)
    return TextRecord(
        id=data["id"],
        domain=domain,
        scenario=data["scenario"],
        profile_id=data["profile_id"],
        has_special=data["has_special"],
        text=text,
        spans=spans,
        gold=gold,
        reviewed_by=reviewed_by,
    )


def load_texts(folder: str | Path) -> list[TextRecord]:
    """Load every `*.json` text in `folder` except `profiles.json`, sorted by id.

    A folder that is missing or holds no text raises `DataError`: an evaluation on
    nothing would report numbers.
    """
    if not Path(folder).is_dir():
        raise DataError(f"{folder}: not a folder")
    paths = sorted(p for p in Path(folder).glob("*.json") if p.name != "profiles.json")
    if not paths:
        raise DataError(f"{folder}: no text files")
    return [load_text(p) for p in paths]


def load_profiles(path: str | Path) -> list[Profile]:
    """Load and validate a profiles file (a JSON list of profile objects)."""
    path = Path(path)
    data = _read_json(path)
    if not isinstance(data, list):
        raise DataError(f"{path}: a profiles file must be a JSON list")
    profiles, seen = [], set()
    for i, item in enumerate(data):

        def fail(message: str, i: int = i) -> DataError:
            return DataError(f"{path}, profile {i}: {message}")

        if not isinstance(item, dict):
            raise fail("must be a JSON object")
        if set(item) != _PROFILE_KEYS:
            raise fail(f"keys must be exactly {sorted(_PROFILE_KEYS)}")
        for key in ("id", "cohort", "name", "city", "employer", "role", "bank", "branch_city"):
            if not isinstance(item[key], str) or not item[key]:
                raise fail(f"{key} must be a non-empty string")
        if item["id"] in seen:
            raise fail(f"duplicate id {item['id']!r}")
        seen.add(item["id"])
        if item["gender"] not in ("M", "F"):
            raise fail("gender must be M or F")
        if isinstance(item["age"], bool) or not isinstance(item["age"], int) or item["age"] < 18:
            raise fail("age must be an integer of at least 18")
        if not isinstance(item["financial"], dict):
            raise fail("financial must be an object")
        special = item["special"]
        if special is not None:
            if not isinstance(special, dict) or set(special) != {"category", "fact"}:
                raise fail("special must be null or an object with category and fact")
            if TYPE_CLASS.get(special["category"]) is not SpanClass.SPECIAL:
                raise fail(f"special.category {special['category']!r} is not a special category")
            if not isinstance(special["fact"], str) or not special["fact"]:
                raise fail("special.fact must be a non-empty string")
        profiles.append(Profile(**{**item, "gender": Gender(item["gender"])}))
    return profiles


# --- helpers ---------------------------------------------------------------------


def _read_json(path: Path) -> Any:
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as exc:
        raise DataError(f"{path}: not valid JSON ({exc.msg}, line {exc.lineno})") from exc


def _load_spans(items: Any, text: str, fail) -> tuple[Span, ...]:
    if not isinstance(items, list):
        raise fail("spans must be a list")
    spans = []
    for i, item in enumerate(items):
        if not isinstance(item, dict) or set(item) != _SPAN_KEYS:
            raise fail(f"span {i} must have exactly {sorted(_SPAN_KEYS)}")
        if not isinstance(item["type"], str) or item["type"] not in SpanType.__members__:
            raise fail(f"span {i} has unknown type {item['type']!r}")
        if any(isinstance(item[k], bool) or not isinstance(item[k], int) for k in ("start", "end")):
            raise fail(f"span {i}: start and end must be integers")
        if not isinstance(item["text"], str):
            raise fail(f"span {i}: text must be a string")
        try:
            span = Span(item["start"], item["end"], item["text"], item["type"], 1.0, GOLD_SOURCE)
        except (TypeError, ValueError) as exc:
            raise fail(f"span {i}: {exc}") from exc
        if not span.matches(text):
            raise fail(f"span {i} ({span.text!r}) does not match the text at its offsets")
        spans.append(span)
    for a, b in zip(spans, spans[1:], strict=False):
        if b.start < a.end:
            raise fail(f"spans must be sorted and non-overlapping ({a.text!r}, {b.text!r})")
    return tuple(spans)


def _load_gold(item: Any, scenario: str, actions: tuple[str, ...], fail) -> Gold:
    if not isinstance(item, dict) or set(item) != _GOLD_KEYS:
        raise fail(f"gold must have exactly {sorted(_GOLD_KEYS)}")
    if item["intent"] != scenario:
        raise fail("gold.intent must equal scenario")
    if item["requested_action"] not in actions:
        raise fail(f"gold.requested_action must be one of {list(actions)}")
    amounts = item["amounts"]
    if not isinstance(amounts, list) or any(
        isinstance(a, bool) or not isinstance(a, int | float) or not math.isfinite(a)
        for a in amounts
    ):
        raise fail("gold.amounts must be a list of finite numbers")
    dates = item["dates"]
    if not isinstance(dates, list) or not all(_is_iso_date(d) for d in dates):
        raise fail("gold.dates must be a list of YYYY-MM-DD dates")
    if item["deadline"] is not None and not _is_iso_date(item["deadline"]):
        raise fail("gold.deadline must be null or a YYYY-MM-DD date")
    return Gold(
        intent=item["intent"],
        amounts=tuple(float(a) for a in amounts),
        dates=tuple(dates),
        requested_action=item["requested_action"],
        deadline=item["deadline"],
    )


def _is_iso_date(value: Any) -> bool:
    # `date.fromisoformat` also reads week dates ("2026-W47-3"): only YYYY-MM-DD is ours.
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True
