import math

import numpy as np
import pytest

from stac.stat_tests import (
    average_ranks,
    friedman_aligned_test,
    friedman_test,
    holm_correction,
    mann_whitney_p_value,
    pairwise_post_hoc,
    shaffer_post_hoc,
    wilcoxon_signed_ranks_p_value,
)


# ---------- 1 vs 1 paired tests ----------


def test_wilcoxon_returns_float_in_unit_interval():
    a = [1.0, 2.0, 3.0, 4.0, 5.0]
    b = [1.5, 2.4, 3.2, 4.1, 5.5]
    p = wilcoxon_signed_ranks_p_value(a, b)
    assert 0.0 <= p <= 1.0


def test_wilcoxon_rejects_unequal_lengths():
    with pytest.raises(ValueError):
        wilcoxon_signed_ranks_p_value([1, 2, 3], [1, 2])


def test_wilcoxon_identical_samples_returns_one():
    a = [1.0, 2.0, 3.0, 4.0]
    assert wilcoxon_signed_ranks_p_value(a, a) == 1.0


def test_mann_whitney_returns_float():
    p = mann_whitney_p_value([1, 2, 3, 4, 5], [10, 11, 12, 13, 14])
    assert 0.0 <= p <= 1.0


# ---------- N vs N omnibus tests ----------


def test_friedman_requires_three_groups():
    with pytest.raises(ValueError):
        friedman_test({"a": [1, 2, 3], "b": [4, 5, 6]})


def test_friedman_detects_difference():
    samples = {
        "fast": [1.0, 1.1, 0.9, 1.2, 1.0],
        "medium": [3.0, 3.1, 2.9, 3.2, 3.0],
        "slow": [10.0, 10.1, 9.9, 10.2, 10.0],
    }
    stat, p = friedman_test(samples)
    assert stat > 0
    assert p < 0.05


def test_friedman_aligned_requires_three_groups():
    with pytest.raises(ValueError):
        friedman_aligned_test({"a": [1, 2, 3], "b": [4, 5, 6]})


def test_friedman_aligned_detects_difference_and_returns_ranks():
    np.random.seed(0)
    samples = {
        "fast": np.random.normal(1.0, 0.5, 30).tolist(),
        "mid": np.random.normal(3.0, 0.5, 30).tolist(),
        "slow": np.random.normal(10.0, 0.5, 30).tolist(),
    }
    stat, p, ranks = friedman_aligned_test(samples, lower_is_better=True)
    assert stat > 0
    assert p < 0.001
    # 'fast' should have the smallest aligned rank (best on lower-is-better).
    assert min(ranks, key=ranks.get) == "fast"
    assert max(ranks, key=ranks.get) == "slow"


# ---------- Holm correction ----------


def test_holm_correction_monotone_and_bounded():
    p_values = [0.001, 0.04, 0.03, 0.5]
    adj = holm_correction(p_values)
    assert all(0.0 <= a <= 1.0 for a in adj)
    assert adj[0] == pytest.approx(0.004)


# ---------- Shaffer post-hoc ----------


def test_shaffer_post_hoc_shapes_and_monotonicity():
    np.random.seed(0)
    samples = {
        "a": np.random.normal(1.0, 0.5, 30).tolist(),
        "b": np.random.normal(3.0, 0.5, 30).tolist(),
        "c": np.random.normal(5.0, 0.5, 30).tolist(),
    }
    df = shaffer_post_hoc(samples)
    assert len(df) == 3  # K*(K-1)/2 pairs
    assert set(df.columns) == {"config_a", "config_b", "p_raw", "p_adj"}
    # Adjusted p-values must be non-decreasing along the sorted order.
    sorted_padj = df.sort_values("p_raw")["p_adj"].tolist()
    assert all(sorted_padj[i] <= sorted_padj[i + 1] + 1e-12 for i in range(len(sorted_padj) - 1))


def test_shaffer_post_hoc_rejects_below_three_configs():
    with pytest.raises(ValueError):
        shaffer_post_hoc({"a": [1, 2, 3], "b": [4, 5, 6]})


# ---------- pairwise_post_hoc dispatcher ----------


def test_pairwise_post_hoc_uses_wilcoxon_by_default():
    np.random.seed(1)
    samples = {
        "a": np.random.normal(1.0, 0.5, 30).tolist(),
        "b": np.random.normal(2.0, 0.5, 30).tolist(),
        "c": np.random.normal(3.0, 0.5, 30).tolist(),
    }
    df = pairwise_post_hoc(samples)
    assert len(df) == 3
    assert "p_adj" in df.columns


def test_pairwise_post_hoc_supports_shaffer():
    np.random.seed(1)
    samples = {
        "a": np.random.normal(1.0, 0.5, 30).tolist(),
        "b": np.random.normal(2.0, 0.5, 30).tolist(),
        "c": np.random.normal(3.0, 0.5, 30).tolist(),
    }
    df = pairwise_post_hoc(samples, correction="shaffer")
    assert len(df) == 3
    assert "p_adj" in df.columns


def test_pairwise_post_hoc_supports_legacy_mann_whitney():
    samples = {
        "a": [1.0, 2.0, 3.0, 4.0, 5.0],
        "b": [10.0, 11.0, 12.0, 13.0, 14.0],
        "c": [20.0, 21.0, 22.0, 23.0, 24.0],
    }
    df = pairwise_post_hoc(samples, test="mann_whitney")
    assert len(df) == 3


def test_pairwise_post_hoc_rejects_unknown_test():
    with pytest.raises(ValueError):
        pairwise_post_hoc({"a": [1, 2, 3], "b": [1, 2, 3]}, test="bogus")


# ---------- average_ranks ----------


def test_average_ranks_lower_is_better_orders_correctly():
    samples = {
        "best": [1.0, 1.0, 1.0],
        "mid": [5.0, 5.0, 5.0],
        "worst": [10.0, 10.0, 10.0],
    }
    ranks = average_ranks(samples, lower_is_better=True)
    assert ranks.index[0] == "best"
    assert ranks.index[-1] == "worst"
