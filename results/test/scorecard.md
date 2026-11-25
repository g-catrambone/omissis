# Scorecard — test

46 texts. Estimates with 95% intervals (paired bootstrap over texts).
Privacy score = 1 − linkage top-1 at N = 25.
Not parsed: the replies of the linkage attack that could not be read, at N = 10 and
at N = 25. Each is counted as a miss; a reply cut at the token limit is one, and it
is asked again at the next launch (protocol, section 7).
Utility = mean of T3 and T1: none where T1 is not reported.

| Configuration | top-1 N=10 | top-3 N=10 | top-1 N=25 | top-3 N=25 | not parsed | city | role | employer | age_bracket | gender | health | T3 | T1 | utility | full restoration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `REF-none` | 1.00 | 1.00 | 1.00 (no variation) | 1.00 | 0, 0 | 1.00 | 1.00 | 1.00 | 0.35 | 0.96 | 1.00 | 0.97 [0.94, 0.99] | 1.00 | 0.98 [0.97, 0.99] | 0.98 [0.93, 1.00] |
| `REF-oracle-direct` | 0.98 | 1.00 | 0.98 [0.93, 1.00] | 1.00 | 0, 0 | 1.00 | 1.00 | 1.00 | 0.35 | 1.00 | 1.00 | 0.96 [0.93, 0.98] | — | — | 0.87 [0.76, 0.96] |
| `REF-oracle` | 0.76 | 0.93 | 0.50 [0.35, 0.65] | 0.72 | 0, 0 | 0.13 | 0.39 | 0.13 | 0.30 | 1.00 | 0.98 | 0.91 [0.87, 0.94] | — | — | 0.83 [0.72, 0.93] |
| `D1+R1` | 0.98 | 1.00 | 0.93 [0.85, 1.00] | 1.00 | 0, 0 | 0.11 | 1.00 | 0.39 | 0.35 | 1.00 | 1.00 | 0.95 [0.92, 0.98] | — | — | 0.87 [0.76, 0.96] |
| `D2+R1` | 0.98 | 1.00 | 1.00 (no variation) | 1.00 | 0, 0 | 0.17 | 1.00 | 1.00 | 0.30 | 1.00 | 1.00 | 0.95 [0.91, 0.97] | — | — | 0.87 [0.76, 0.96] |
| `D4+R1` | 0.70 | 0.93 | 0.59 [0.43, 0.74] | 0.85 | 0, 0 | 0.13 | 0.37 | 0.11 | 0.24 | 1.00 | 0.98 | 0.90 [0.86, 0.93] | 0.62 | 0.76 [0.73, 0.78] | 0.74 [0.61, 0.85] |
| `D4+R2` | 0.67 | 0.91 | 0.41 [0.28, 0.54] | 0.67 | 0, 0 | 0.11 | 0.50 | 0.07 | 0.33 | 1.00 | 1.00 | 0.95 [0.92, 0.97] | — | — | 0.72 [0.59, 0.85] |

Chance: top-1 0.10 at N = 10 and 0.04 at N = 25; top-3 0.30 and 0.12.

## Linkage without the loan texts that contradict the profile

5 texts left out: they are about a loan or a mortgage that the profile of the author
does not hold, so the products of the candidates point away from the author (protocol,
section 7). A control, not a contrast: no test is run on these rows.

| Configuration | texts | top-1 N=25 | top-1 N=25, all texts |
|---|---|---|---|
| `REF-none` | 41 | 1.00 (no variation) | 1.00 |
| `REF-oracle-direct` | 41 | 0.98 [0.93, 1.00] | 0.98 |
| `REF-oracle` | 41 | 0.56 [0.41, 0.71] | 0.50 |
| `D1+R1` | 41 | 0.95 [0.88, 1.00] | 0.93 |
| `D2+R1` | 41 | 1.00 (no variation) | 1.00 |
| `D4+R1` | 41 | 0.63 [0.49, 0.78] | 0.59 |
| `D4+R2` | 41 | 0.44 [0.29, 0.59] | 0.41 |

## Detectors

Recall under overlap matching. Leak rate: share of texts with a direct
identifier not fully covered.

| Detector | recall direct | recall quasi | recall special | precision | leak rate | latency p50 (s) | p95 (s) |
|---|---|---|---|---|---|---|---|
| D0 | 0.48 | 0.13 | 0.00 | 1.00 | 1.00 (no variation) | — | — |
| D1 | 0.72 | 0.43 | 0.00 | 0.87 | 0.87 [0.76, 0.96] | — | — |
| D2 | 0.48 | 0.21 | 0.00 | 0.90 | 1.00 (no variation) | — | — |
| D3 | 0.13 | 0.97 | 0.88 | 0.96 | n/a | — | — |
| D4 | 0.99 | 0.97 | 0.88 | 0.97 | 0.04 [0.00, 0.11] | — | — |

## Primary contrasts

| Contrast | metric | difference | test | p | Holm p | finding |
|---|---|---|---|---|---|---|
| `D4+R1` vs `D1+R1` | linkage_top1_n25 | -0.35 [-0.52, -0.17] | mcnemar_exact | 0.000 | 0.001 | yes |
| `D4+R1` vs `REF-none` | utility | -0.22 [-0.25, -0.20] | paired_bootstrap | 0.000 | 0.000 | yes |
| `D4+R2` vs `D4+R1` | full_restoration | -0.02 [-0.17, 0.13] | mcnemar_exact | 1.000 | 1.000 | not distinguishable with this sample |
