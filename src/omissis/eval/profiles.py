"""Profiles, text plan and candidate lists (task 3.1; protocol, sections 1 and 2).

Everything is drawn with one seed from the value pools in `data/profiles/pools.json`,
which are disjoint from the R2 fake lists. `python -m omissis.eval.profiles` writes

- `profiles.json`: 30 people in 6 cohorts of 5. The members of a cohort share two of
  role, city, employer and bank, a different pair in each cohort, and no two of them
  share all four. Ten people have a special fact: 8 SALUTE, 2 SINDACATO.
- `plan.json`: the 66 texts to write, each with its author, scenario, `has_special`,
  requested action and whether it is a pilot text. The 20 texts with a special
  category are written by the 10 people with a matching fact, two each; the other
  46 by the other 20 people, two or three each. No one writes a scenario twice,
  except the two union members, who write the four `union_leave` texts.
  The 10 pilot texts are one per person of two cohorts.
- `candidates_N10.json`, `candidates_N25.json`: for every text the true author, the
  other four members of the cohort and people drawn at random, shuffled.
"""

from __future__ import annotations

import itertools
import json
import random
from pathlib import Path
from typing import Any

from omissis.eval.datasets import SCENARIOS

SEED = 20261111
FOLDER = Path("data/profiles")
SHARED = ("role", "city", "employer", "bank")
POOL_OF = {"role": "roles", "city": "cities", "employer": "employers", "bank": "banks"}
LIST_SIZES = (10, 25)
AGES = (24, 67)

# Scenario -> number of texts (protocol, section 2), in the order of the ids.
TEXTS = {
    "mortgage_suspension": 6,
    "card_dispute": 6,
    "iban_change": 6,
    "loan_early_repayment": 6,
    "account_closure": 6,
    "fee_complaint": 5,
    "inheritance_unblock": 5,
    "sick_leave": 5,
    "remote_work_request": 5,
    "harassment_complaint": 4,
    "medical_reimbursement": 4,
    "transfer_request": 4,
    "union_leave": 4,
}
ALWAYS_SPECIAL = {
    "sick_leave": "SALUTE",
    "medical_reimbursement": "SALUTE",
    "union_leave": "SINDACATO",
}
SOMETIMES_SPECIAL = ("mortgage_suspension", "remote_work_request")  # 7 texts by seed, SALUTE
EXTRA_SPECIAL = 7
PILOT_COHORTS = 2


def load_pools(folder: str | Path = FOLDER) -> dict[str, list[str]]:
    return json.loads((Path(folder) / "pools.json").read_text(encoding="utf-8"))


def build_profiles(pools: dict[str, list[str]], seed: int = SEED) -> list[dict[str, Any]]:
    """The 30 profiles, ids p01 to p30, cohorts c1 to c6."""
    rng = random.Random(f"{seed}|profiles")
    names = [(n, "F") for n in pools["names_f"]] + [(n, "M") for n in pools["names_m"]]
    surnames = list(pools["surnames"])
    rng.shuffle(names)
    rng.shuffle(surnames)
    pairs = list(itertools.combinations(SHARED, 2))  # six pairs, one per cohort
    rng.shuffle(pairs)

    profiles = []
    for c, shared in enumerate(pairs, start=1):
        fixed = {key: rng.choice(pools[POOL_OF[key]]) for key in shared}
        free = [key for key in SHARED if key not in shared]
        combos = list(itertools.product(*(pools[POOL_OF[key]] for key in free)))
        for combo in rng.sample(combos, 5):  # five different pairs: no two share all four
            (first, gender), surname = names.pop(), surnames.pop()
            values = {**fixed, **dict(zip(free, combo, strict=True))}
            products = sorted(rng.sample(pools["products"], 2))
            financial: dict[str, Any] = {"products": products}
            if {"mutuo prima casa", "prestito personale"} & set(products):
                financial["monthly_installment"] = float(rng.randrange(180, 951, 10))
            profiles.append(
                {
                    "id": f"p{len(profiles) + 1:02d}",
                    "cohort": f"c{c}",
                    "name": f"{first} {surname}",
                    "gender": gender,
                    "age": rng.randint(*AGES),
                    "city": values["city"],
                    "employer": values["employer"],
                    "role": values["role"],
                    "bank": values["bank"],
                    "branch_city": values["city"],
                    "financial": financial,
                    "special": None,
                }
            )

    chosen = rng.sample(profiles, len(pools["special_salute"]) + len(pools["special_sindacato"]))
    facts = [("SALUTE", f) for f in pools["special_salute"]]
    facts += [("SINDACATO", f) for f in pools["special_sindacato"]]
    for profile, (category, fact) in zip(chosen, facts, strict=True):
        profile["special"] = {"category": category, "fact": fact}
    return profiles


def _assign(
    rng: random.Random, slots: list[int], scenarios: list[str], people: list[str], each: int
):
    """Give every slot an author: `each` texts per person, the rest one more to some.

    Drawn again until no one has the same scenario twice. Where the slots hold one
    scenario only (the four `union_leave` texts of the two union members) that
    cannot be, and is not asked.
    """
    one_scenario = len({scenarios[s] for s in slots}) == 1
    for _ in range(10_000):
        extra = rng.sample(people, len(slots) - each * len(people))
        authors = people * each + extra
        rng.shuffle(authors)
        seen = set(zip(authors, (scenarios[s] for s in slots), strict=True))
        if one_scenario or len(seen) == len(slots):
            return dict(zip(slots, authors, strict=True))
    raise RuntimeError("no assignment of authors without a repeated scenario")


def build_plan(profiles: list[dict[str, Any]], seed: int = SEED) -> dict[str, dict[str, Any]]:
    """The 66 texts: author, scenario, `has_special`, requested action, pilot flag."""
    rng = random.Random(f"{seed}|plan")
    scenarios = [name for name, count in TEXTS.items() for _ in range(count)]
    sometimes = [i for i, s in enumerate(scenarios) if s in SOMETIMES_SPECIAL]
    special = {i: ALWAYS_SPECIAL[s] for i, s in enumerate(scenarios) if s in ALWAYS_SPECIAL}
    special.update(dict.fromkeys(rng.sample(sometimes, EXTRA_SPECIAL), "SALUTE"))

    by_category: dict[str | None, list[str]] = {}
    for p in profiles:
        by_category.setdefault(p["special"] and p["special"]["category"], []).append(p["id"])
    author: dict[int, str] = {}
    for category, people in by_category.items():
        slots = [i for i in range(len(scenarios)) if special.get(i) == category]
        author.update(_assign(rng, slots, scenarios, people, each=2))

    cohort = {p["id"]: p["cohort"] for p in profiles}
    pilot_cohorts = set(rng.sample(sorted(set(cohort.values())), PILOT_COHORTS))
    pilot: set[int] = set()
    for person in sorted(p for p, c in cohort.items() if c in pilot_cohorts):
        pilot.add(rng.choice([i for i, a in author.items() if a == person]))

    plan, counters = {}, {"bank": 0, "hr": 0}
    for i, scenario in enumerate(scenarios):
        domain, actions = SCENARIOS[scenario]
        counters[domain] += 1
        plan[f"{domain}-{counters[domain]:04d}"] = {
            "profile_id": author[i],
            "scenario": scenario,
            "has_special": i in special,
            "requested_action": rng.choice(actions),
            "pilot": i in pilot,
        }
    return plan


def build_candidates(
    profiles: list[dict[str, Any]], plan: dict[str, dict[str, Any]], size: int, seed: int = SEED
) -> dict[str, list[str]]:
    """For every text: the author, the rest of the cohort, random others; shuffled."""
    cohort = {p["id"]: p["cohort"] for p in profiles}
    lists = {}
    for text_id, entry in plan.items():
        rng = random.Random(f"{seed}|candidates|{size}|{text_id}")
        author = entry["profile_id"]
        mates = [p for p in cohort if cohort[p] == cohort[author]]
        others = rng.sample([p for p in cohort if p not in mates], size - len(mates))
        candidates = mates + others
        rng.shuffle(candidates)
        lists[text_id] = candidates
    return lists


def build(folder: str | Path = FOLDER, seed: int = SEED) -> dict[str, Any]:
    """Every file of `data/profiles/` except the pools, by file name."""
    profiles = build_profiles(load_pools(folder), seed)
    plan = build_plan(profiles, seed)
    files: dict[str, Any] = {"profiles.json": profiles, "plan.json": plan}
    for size in LIST_SIZES:
        files[f"candidates_N{size}.json"] = build_candidates(profiles, plan, size, seed)
    return files


def main() -> None:
    for name, content in build().items():
        path = FOLDER / name
        path.write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {path} ({len(content)} entries)")


if __name__ == "__main__":
    main()
