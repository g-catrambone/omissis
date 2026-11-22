# Scorecard — dev

20 texts. Estimates with 95% intervals (paired bootstrap over texts).
Privacy score = 1 − linkage top-1 at N = 25.
Not parsed: the replies of the linkage attack that could not be read, at N = 10 and
at N = 25. Each is counted as a miss; a reply cut at the token limit is one, and it
is asked again at the next launch (protocol, section 7).
Utility = mean of T3 and T1: none where T1 is not reported.

| Configuration | top-1 N=10 | top-3 N=10 | top-1 N=25 | top-3 N=25 | not parsed | city | role | employer | age_bracket | gender | health | T3 | T1 | utility | full restoration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `REF-none` | 1.00 | 1.00 | 1.00 (no variation) | 1.00 | 0, 0 | 1.00 | 0.95 | 1.00 | 0.35 | 0.90 | 1.00 | 0.98 [0.95, 1.00] | 1.00 | 0.99 [0.97, 1.00] | 1.00 (no variation) |
| `REF-oracle-direct` | 1.00 | 1.00 | 0.95 [0.85, 1.00] | 1.00 | 0, 0 | 1.00 | 0.95 | 1.00 | 0.30 | 1.00 | 1.00 | 0.97 [0.94, 1.00] | — | — | 0.95 [0.85, 1.00] |
| `REF-oracle` | 0.55 | 0.95 | 0.50 [0.30, 0.70] | 0.65 | 0, 0 | 0.15 | 0.30 | 0.25 | 0.20 | 1.00 | 1.00 | 0.89 [0.84, 0.94] | — | — | 0.70 [0.50, 0.90] |
| `D1+R1` | 0.85 | 1.00 | 0.90 [0.75, 1.00] | 1.00 | 0, 0 | 0.15 | 0.95 | 0.30 | 0.20 | 1.00 | 1.00 | 0.98 [0.95, 1.00] | — | — | 0.95 [0.85, 1.00] |
| `D2+R1` | 1.00 | 1.00 | 1.00 (no variation) | 1.00 | 0, 0 | 0.15 | 0.95 | 1.00 | 0.35 | 1.00 | 1.00 | 0.98 [0.95, 1.00] | — | — | 0.95 [0.85, 1.00] |
| `D4+R1` | 0.65 | 0.95 | 0.55 [0.35, 0.75] | 0.80 | 0, 0 | 0.15 | 0.40 | 0.30 | 0.20 | 1.00 | 1.00 | 0.93 [0.88, 0.98] | — | — | 0.85 [0.70, 1.00] |
| `D4+R2` | 0.55 | 0.75 | 0.45 [0.25, 0.65] | 0.65 | 0, 0 | 0.25 | 0.40 | 0.15 | 0.30 | 1.00 | 1.00 | 0.98 [0.95, 1.00] | — | — | 0.75 [0.55, 0.90] |

Chance: top-1 0.10 at N = 10 and 0.04 at N = 25; top-3 0.30 and 0.12.

## Linkage without the loan texts that contradict the profile

2 texts left out: they are about a loan or a mortgage that the profile of the author
does not hold, so the products of the candidates point away from the author (protocol,
section 7). A control, not a contrast: no test is run on these rows.

| Configuration | texts | top-1 N=25 | top-1 N=25, all texts |
|---|---|---|---|
| `REF-none` | 18 | 1.00 (no variation) | 1.00 |
| `REF-oracle-direct` | 18 | 1.00 (no variation) | 0.95 |
| `REF-oracle` | 18 | 0.56 [0.33, 0.78] | 0.50 |
| `D1+R1` | 18 | 0.89 [0.72, 1.00] | 0.90 |
| `D2+R1` | 18 | 1.00 (no variation) | 1.00 |
| `D4+R1` | 18 | 0.56 [0.33, 0.78] | 0.55 |
| `D4+R2` | 18 | 0.50 [0.28, 0.72] | 0.45 |

## Detectors

Recall under overlap matching. Leak rate: share of texts with a direct
identifier not fully covered.

| Detector | recall direct | recall quasi | recall special | precision | leak rate | latency p50 (s) | p95 (s) |
|---|---|---|---|---|---|---|---|
| D0 | 0.49 | 0.14 | 0.00 | 1.00 | 1.00 (no variation) | 0.00 | 0.00 |
| D1 | 0.72 | 0.38 | 0.00 | 0.81 | 0.80 [0.60, 0.95] | 0.01 | 0.01 |
| D2 | 0.45 | 0.16 | 0.00 | 0.92 | 1.00 (no variation) | 0.13 | 0.14 |
| D3 | 0.13 | 0.93 | 1.00 | 0.93 | n/a | 25.00 | 56.77 |
| D4 | 0.99 | 0.93 | 1.00 | 0.96 | 0.05 [0.00, 0.15] | 36.99 | 54.02 |

## Primary contrasts

| Contrast | metric | difference | test | p | Holm p | finding |
|---|---|---|---|---|---|---|
| `D4+R1` vs `D1+R1` | linkage_top1_n25 | -0.35 [-0.55, -0.15] | mcnemar_exact | 0.016 | 0.031 | yes |
| `D4+R2` vs `D4+R1` | full_restoration | -0.10 [-0.35, 0.15] | mcnemar_exact | 0.688 | 0.688 | not distinguishable with this sample |
