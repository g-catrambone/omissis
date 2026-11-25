"""Statistics: hand-computed and textbook values."""

import pytest

from omissis.eval import stats


def test_mcnemar_exact_against_hand_computed_values():
    # 1 and 9 discordant pairs: 2 * (C(10,0) + C(10,1)) / 2^10 = 22 / 1024
    a = [True] * 1 + [False] * 9 + [True] * 5 + [False] * 5
    b = [False] * 1 + [True] * 9 + [True] * 5 + [False] * 5
    result = stats.mcnemar_exact(a, b)
    assert (result["a_only"], result["b_only"]) == (1, 9)
    assert result["p"] == pytest.approx(22 / 1024)


def test_mcnemar_exact_edge_cases():
    same = [True, False, True]
    assert stats.mcnemar_exact(same, same)["p"] == 1.0  # no discordant pair
    # 0 and 6: 2 * 1 / 64
    assert stats.mcnemar_exact([True] * 6, [False] * 6)["p"] == pytest.approx(2 / 64)
    # 3 and 3: the two tails overlap, p is capped at 1
    assert stats.mcnemar_exact([True] * 3 + [False] * 3, [False] * 3 + [True] * 3)["p"] == 1.0
    with pytest.raises(ValueError):
        stats.mcnemar_exact([True], [True, False])


def test_holm_against_a_worked_example():
    # Sorted: 0.01 x 3 = 0.03; 0.03 x 2 = 0.06; 0.04 x 1 = 0.04, raised to 0.06.
    assert stats.holm([0.01, 0.04, 0.03]) == pytest.approx([0.03, 0.06, 0.06])
    assert stats.holm([0.5, 0.9, 0.7]) == pytest.approx([1.0, 1.0, 1.0])
    assert stats.holm([0.02]) == [0.02] and stats.holm([]) == []


def test_bootstrap_interval_of_a_constant_has_zero_width():
    assert stats.bootstrap_ci([1.0] * 46, seed=1) == (1.0, 1.0, 1.0)
    assert stats.bootstrap_ci([0.0] * 46, seed=1) == (0.0, 0.0, 0.0)


def test_bootstrap_interval_matches_the_normal_approximation_on_a_proportion():
    values = [1.0] * 23 + [0.0] * 23  # p = 0.5, n = 46: 0.5 +/- 1.96 * sqrt(0.25 / 46)
    estimate, low, high = stats.bootstrap_ci(values, seed=7)
    assert estimate == 0.5
    assert low == pytest.approx(0.5 - 1.96 * (0.25 / 46) ** 0.5, abs=0.02)
    assert high == pytest.approx(0.5 + 1.96 * (0.25 / 46) ** 0.5, abs=0.02)


def test_bootstrap_is_deterministic_for_the_seed():
    values = [0.2, 0.4, 0.9, 1.0, 0.0, 0.6, 0.6, 0.8]
    assert stats.bootstrap_ci(values, seed=3) == stats.bootstrap_ci(values, seed=3)
    assert stats.bootstrap_ci(values, seed=3) != stats.bootstrap_ci(values, seed=4)
    with pytest.raises(ValueError):
        stats.bootstrap_ci([], seed=1)


def test_paired_bootstrap_on_a_clear_and_on_a_null_difference():
    a = [0.8, 0.9, 0.7, 1.0, 0.9, 0.8, 0.9, 1.0, 0.7, 0.8]
    b = [x - 0.3 for x in a]
    clear = stats.paired_bootstrap(a, b, seed=1)
    assert clear["difference"] == pytest.approx(0.3)
    assert clear["low"] == pytest.approx(0.3) and clear["high"] == pytest.approx(0.3)
    assert clear["p"] == 0.0  # no resampled difference is at or below zero
    null = stats.paired_bootstrap(a, a, seed=1)
    assert (null["difference"], null["low"], null["high"], null["p"]) == (0.0, 0.0, 0.0, 1.0)
    mixed = stats.paired_bootstrap([1, 0, 1, 0, 1, 0], [0, 1, 0, 1, 0, 1], seed=1)
    assert mixed["difference"] == 0.0 and mixed["low"] < 0 < mixed["high"] and mixed["p"] > 0.5
    with pytest.raises(ValueError):
        stats.paired_bootstrap([1.0], [1.0, 2.0], seed=1)


def test_percentile_interpolates():
    assert stats._percentile([0.0, 10.0], 0.25) == 2.5
    assert stats._percentile([1.0, 2.0, 3.0], 0.5) == 2.0
