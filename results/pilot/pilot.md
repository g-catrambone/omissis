# Pilot

Both attacks on the 10 pilot texts under the three references. Written by
`python -m omissis.eval.pilot`; the numbers are in `results/pilot/metrics/`.

## Linkage: authors identified (top-1), of 10

| Configuration | N = 10 | N = 25 | top-3, N = 10 | unparseable |
|---|---|---|---|---|
| `REF-none` | 10 | 10 | 10 | 0 |
| `REF-oracle-direct` | 10 | 9 | 10 | 0 |
| `REF-oracle` | 6 | 5 | 9 | 0 |

Chance: 1 of 10 at N = 10, 0.4 of 10 at N = 25.

## Pilot rule (protocol, section 2)

Go when the attacker identifies at least 6 authors under `REF-oracle-direct` at N = 10
and at least 3 fewer under `REF-oracle`. `REF-none` is reported only.

- `REF-oracle-direct`: 10 of 10 (needs 6: met)
- `REF-oracle`: 6 of 10, 4 fewer (needs 3: met)

The decision is the team's and goes in `docs/decisions.md` with these numbers.

## Attribute inference: accuracy

| Attribute | `REF-none` | `REF-oracle-direct` | `REF-oracle` | majority | invalid |
|---|---|---|---|---|---|
| city | 1.00 | 1.00 | 0.10 | 0.60 | 0 |
| role | 0.90 | 0.90 | 0.30 | 0.20 | 0 |
| employer | 1.00 | 1.00 | 0.10 | 1.00 | 0 |
| age_bracket | 0.40 | 0.30 | 0.20 | 0.60 | 0 |
| gender | 0.90 | 1.00 | 1.00 | 0.50 | 0 |
| health | 1.00 | 1.00 | 1.00 | 0.70 | 0 |

Ten texts: every number here is a count to read, not an estimate to report.
