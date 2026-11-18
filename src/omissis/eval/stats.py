"""Statistics of the protocol, section 12. Standard library only.

All comparisons are paired on the same texts: every function takes one value per text,
in the same order for the two configurations compared.
"""

from __future__ import annotations

import math
import random
from collections.abc import Sequence

RESAMPLES = 10_000


def mean(values: Sequence[float]) -> float:
    return sum(values) / len(values)


def _resampled_means(values: Sequence[float], seed: int, resamples: int) -> list[float]:
    rng = random.Random(seed)
    n = len(values)
    return sorted(mean(rng.choices(values, k=n)) for _ in range(resamples))


def _percentile(ordered: Sequence[float], q: float) -> float:
    """Percentile `q` in [0, 1] of sorted values, with linear interpolation."""
    position = q * (len(ordered) - 1)
    low, high = math.floor(position), math.ceil(position)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def bootstrap_ci(
    values: Sequence[float], seed: int, resamples: int = RESAMPLES
) -> tuple[float, float, float]:
    """Mean of `values` and its 95% interval: bootstrap over texts, percentile method."""
    if not values:
        raise ValueError("no values")
    means = _resampled_means(values, seed, resamples)
    return mean(values), _percentile(means, 0.025), _percentile(means, 0.975)


def paired_bootstrap(
    a: Sequence[float], b: Sequence[float], seed: int, resamples: int = RESAMPLES
) -> dict[str, float]:
    """Difference of means a - b over paired texts: estimate, 95% interval, two-sided p.

    p = 2 x min(share of resampled differences <= 0, share >= 0), capped at 1.
    """
    if len(a) != len(b) or not a:
        raise ValueError("paired samples must have the same, non-zero length")
    differences = [x - y for x, y in zip(a, b, strict=True)]
    means = _resampled_means(differences, seed, resamples)
    below = sum(m <= 0 for m in means) / len(means)
    above = sum(m >= 0 for m in means) / len(means)
    return {
        "difference": mean(differences),
        "low": _percentile(means, 0.025),
        "high": _percentile(means, 0.975),
        "p": min(1.0, 2 * min(below, above)),
    }


def mcnemar_exact(a: Sequence[bool], b: Sequence[bool]) -> dict[str, float]:
    """McNemar's exact test, two-sided, for paired binary outcomes.

    Only the discordant pairs count: `a_only` texts where a is true and b false,
    `b_only` the opposite. Under the null they follow a binomial with p = 1/2.
    """
    if len(a) != len(b):
        raise ValueError("paired samples must have the same length")
    a_only = sum(x and not y for x, y in zip(a, b, strict=True))
    b_only = sum(y and not x for x, y in zip(a, b, strict=True))
    n = a_only + b_only
    tail = sum(math.comb(n, k) for k in range(min(a_only, b_only) + 1)) / 2**n
    return {"a_only": a_only, "b_only": b_only, "p": min(1.0, 2 * tail)}


def holm(p_values: Sequence[float]) -> list[float]:
    """Holm-adjusted p-values, in the order given."""
    order = sorted(range(len(p_values)), key=lambda i: p_values[i])
    adjusted, running = [0.0] * len(p_values), 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(p_values) - rank) * p_values[i]))
        adjusted[i] = running
    return adjusted
