"""Statistical tests used to compare bioinspired algorithm configurations.

Aligned with BAO chapter 6 ("Comparing Algorithms Output"):

- 1 vs 1 paired comparisons:  wilcoxon_signed_ranks_p_value
- N vs N omnibus:              friedman_aligned_test  (more powerful than plain Friedman)
- N vs N post-hoc:             shaffer_post_hoc       (course-recommended)
- 1 vs N post-hoc:             holm_correction        (Holm-Bonferroni step-down)
- Companion summary:           average_ranks
- Legacy (independent samples): mann_whitney_p_value, friedman_test
"""
from __future__ import annotations

from itertools import combinations
from typing import Sequence

import numpy as np
import pandas as pd
from scipy.stats import friedmanchisquare, mannwhitneyu, norm, wilcoxon


# ---------------------------------------------------------------------------
# 1 vs 1 pairwise tests
# ---------------------------------------------------------------------------

def wilcoxon_signed_ranks_p_value(sample_a: Sequence[float], sample_b: Sequence[float]) -> float:
    """Two-sided Wilcoxon signed-ranks p-value for paired samples.

    Use when the two samples are naturally paired (same seed, same problem
    instance, same subject etc.). For our experiment the two samples to compare
    share the same seed schedule, so they are paired.
    """
    a = np.asarray(sample_a, dtype=float)
    b = np.asarray(sample_b, dtype=float)
    if len(a) != len(b):
        raise ValueError("Wilcoxon signed-ranks requires equal-length paired samples.")
    diffs = a - b
    if np.all(diffs == 0):
        return 1.0  # all pairs identical -> nothing to test
    result = wilcoxon(a, b, alternative="two-sided", zero_method="wilcox")
    return float(result.pvalue)


def mann_whitney_p_value(sample_a: Sequence[float], sample_b: Sequence[float]) -> float:
    """Two-sided Mann-Whitney U p-value (independent samples).

    Kept for legacy comparisons; for our paired experiment use
    wilcoxon_signed_ranks_p_value instead.
    """
    result = mannwhitneyu(sample_a, sample_b, alternative="two-sided")
    return float(result.pvalue)


# ---------------------------------------------------------------------------
# N vs N omnibus tests
# ---------------------------------------------------------------------------

def friedman_test(samples_per_config: dict[str, Sequence[float]]) -> tuple[float, float]:
    """Plain Friedman omnibus: ranks within each block, sums ranks per config."""
    arrays = list(samples_per_config.values())
    if len(arrays) < 3:
        raise ValueError("Friedman test requires at least 3 configurations.")
    if len({len(a) for a in arrays}) != 1:
        raise ValueError("All configurations must have the same number of observations.")
    stat, p = friedmanchisquare(*arrays)
    return float(stat), float(p)


def friedman_aligned_test(
    samples_per_config: dict[str, Sequence[float]],
    lower_is_better: bool = True,
) -> tuple[float, float, dict[str, float]]:
    """Friedman Aligned Ranks Test (Hodges-Lehmann variant).

    Compared to the plain Friedman test, the Aligned Ranks variant first
    subtracts a per-block location estimator (here, the per-block mean) from
    every observation, then ranks ALL aligned observations together across
    blocks. This is more powerful when the number of treatments K is small.

    Args:
        samples_per_config: dict {config_id: [obs_block_0, obs_block_1, ...]}.
            All sequences must have the same length n (number of blocks).
        lower_is_better: if True, smaller observations get smaller (better)
            ranks; if False, the convention is inverted.

    Returns:
        (statistic, p_value, average_aligned_rank_per_config)
    """
    keys = list(samples_per_config.keys())
    K = len(keys)
    if K < 3:
        raise ValueError("Friedman aligned ranks requires at least 3 configurations.")

    matrix = np.asarray([list(samples_per_config[k]) for k in keys], dtype=float)  # shape (K, n)
    if matrix.shape[1] < 2:
        raise ValueError("Need at least 2 blocks (observations per configuration).")
    n = matrix.shape[1]

    # 1) Align each observation by subtracting its block mean.
    block_means = matrix.mean(axis=0, keepdims=True)
    aligned = matrix - block_means
    if not lower_is_better:
        aligned = -aligned

    # 2) Rank all K*n aligned observations together (average ranks for ties).
    flat = aligned.flatten()
    ranks_flat = pd.Series(flat).rank(method="average").to_numpy()
    R = ranks_flat.reshape(K, n)

    # 3) Per-treatment rank totals R_i and per-block rank totals R_hat_j.
    R_i = R.sum(axis=1)            # length K
    R_hat_j = R.sum(axis=0)        # length n

    # 4) Aligned ranks statistic (Hodges-Lehmann / Garcia-Herrera 2010).
    sum_R_hat_sq = float(np.sum(R_hat_j ** 2))
    sum_R_i_sq = float(np.sum(R_i ** 2))
    numerator = (K - 1) * (sum_R_i_sq - (K * n ** 2 / 4.0) * (K * n + 1) ** 2)
    denom = (K * n * (K * n + 1) * (2 * K * n + 1) / 6.0) - (1.0 / K) * sum_R_hat_sq
    if denom == 0:
        # Degenerate (all observations identical after alignment).
        return 0.0, 1.0, {k: float(R_i[i] / n) for i, k in enumerate(keys)}

    T = numerator / denom
    # Approximated by a chi-square with K - 1 degrees of freedom.
    from scipy.stats import chi2
    p = float(1.0 - chi2.cdf(T, df=K - 1))
    avg_rank = {k: float(R_i[i] / n) for i, k in enumerate(keys)}
    return float(T), p, avg_rank


# ---------------------------------------------------------------------------
# N vs N post-hoc procedures
# ---------------------------------------------------------------------------

def _shaffer_max_hypotheses(K: int) -> list[int]:
    """Maximum number of hypotheses that can be simultaneously true given K
    treatments, sorted in decreasing order. Used by Shaffer's static
    procedure (Shaffer 1986).

    s(0) = 0, s(K) = max over j in {1..K} of C(j,2) + s(K-j)
    """
    cache: dict[int, list[int]] = {0: [0], 1: [0]}

    def t(k: int) -> int:
        return k * (k - 1) // 2

    def s_set(k: int) -> set[int]:
        if k in cache:
            return set(cache[k])
        result: set[int] = set()
        for j in range(1, k + 1):
            for v in s_set(k - j):
                result.add(t(j) + v)
        cache[k] = sorted(result, reverse=True)
        return set(cache[k])

    s_set(K)
    return cache[K]


def shaffer_post_hoc(
    samples_per_config: dict[str, Sequence[float]],
    pair_p_values: list[tuple[str, str, float]] | None = None,
) -> pd.DataFrame:
    """Shaffer's static post-hoc procedure for N vs N pairwise comparisons.

    For K configurations there are m = K*(K-1)/2 pairwise comparisons. After
    sorting the raw p-values from smallest to largest, the i-th hypothesis is
    rejected at level alpha if its raw p-value is below alpha / t_i, where
    t_i is the i-th element of Shaffer's set of maximum simultaneously-true
    hypotheses (which is bounded by m - i + 1 and never larger than that, so
    Shaffer is at least as powerful as Bonferroni-Holm).

    Args:
        samples_per_config: dict of paired samples per configuration.
        pair_p_values: optional pre-computed list of (config_a, config_b, p_raw)
            tuples (e.g. from Wilcoxon). If None, Wilcoxon signed-ranks is used
            for every pair.

    Returns:
        Long-form DataFrame with columns config_a, config_b, p_raw, p_adj.
    """
    keys = list(samples_per_config.keys())
    K = len(keys)
    if K < 3:
        raise ValueError("Shaffer post-hoc requires at least 3 configurations.")

    if pair_p_values is None:
        pair_p_values = []
        for i, j in combinations(range(K), 2):
            p = wilcoxon_signed_ranks_p_value(samples_per_config[keys[i]], samples_per_config[keys[j]])
            pair_p_values.append((keys[i], keys[j], p))

    rows = [{"config_a": a, "config_b": b, "p_raw": float(p)} for a, b, p in pair_p_values]
    rows.sort(key=lambda r: r["p_raw"])

    shaffer_set = _shaffer_max_hypotheses(K)
    # Pad with 1s in case the cache returned fewer entries (shouldn't happen).
    m = len(rows)
    if len(shaffer_set) < m:
        shaffer_set = shaffer_set + [1] * (m - len(shaffer_set))

    running_max = 0.0
    for i, row in enumerate(rows):
        t_i = shaffer_set[i] if i < len(shaffer_set) else 1
        adj = min(1.0, row["p_raw"] * max(t_i, 1))
        adj = max(adj, running_max)  # enforce monotonicity
        running_max = adj
        row["p_adj"] = adj

    return pd.DataFrame(rows)


def holm_correction(p_values: list[float]) -> list[float]:
    """Holm-Bonferroni step-down adjustment for an arbitrary list of p-values."""
    n = len(p_values)
    indexed = sorted(enumerate(p_values), key=lambda kv: kv[1])
    adjusted = [0.0] * n
    running_max = 0.0
    for rank, (orig_idx, p) in enumerate(indexed):
        adj = min(1.0, p * (n - rank))
        adj = max(adj, running_max)
        running_max = adj
        adjusted[orig_idx] = adj
    return adjusted


def pairwise_post_hoc(
    samples_per_config: dict[str, Sequence[float]],
    test: str = "wilcoxon",
    correction: str = "holm",
) -> pd.DataFrame:
    """Pairwise comparison across all config pairs, with multi-test correction.

    Args:
        samples_per_config: dict of samples per configuration. For Wilcoxon,
            samples must be paired and equal-length.
        test: "wilcoxon" (course-recommended for paired data) or "mann_whitney"
            (legacy, for independent data).
        correction: "holm" (default), "shaffer" or "none".

    Returns:
        DataFrame with columns config_a, config_b, p_raw, p_adj.
    """
    if test == "wilcoxon":
        pair_test = wilcoxon_signed_ranks_p_value
    elif test == "mann_whitney":
        pair_test = mann_whitney_p_value
    else:
        raise ValueError(f"Unknown test: {test}")

    keys = list(samples_per_config.keys())
    rows = []
    raw_pvals = []
    for i, j in combinations(range(len(keys)), 2):
        a = samples_per_config[keys[i]]
        b = samples_per_config[keys[j]]
        p = pair_test(a, b)
        rows.append({"config_a": keys[i], "config_b": keys[j], "p_raw": float(p)})
        raw_pvals.append(float(p))

    if correction == "holm":
        adjusted = holm_correction(raw_pvals)
        for row, p in zip(rows, adjusted):
            row["p_adj"] = p
        return pd.DataFrame(rows)

    if correction == "shaffer":
        # Reuse the Shaffer routine with already-computed raw p-values.
        triples = [(r["config_a"], r["config_b"], r["p_raw"]) for r in rows]
        return shaffer_post_hoc(samples_per_config, pair_p_values=triples)

    if correction == "none":
        for row, p in zip(rows, raw_pvals):
            row["p_adj"] = p
        return pd.DataFrame(rows)

    raise ValueError(f"Unknown correction method: {correction}")


# ---------------------------------------------------------------------------
# Companion summaries
# ---------------------------------------------------------------------------

def average_ranks(samples_per_config: dict[str, Sequence[float]], lower_is_better: bool = True) -> pd.Series:
    """Average within-block ranks per configuration (rows = blocks, cols = configs)."""
    df = pd.DataFrame(samples_per_config)
    if lower_is_better:
        ranks = df.rank(axis=1, method="average")
    else:
        ranks = (-df).rank(axis=1, method="average")
    return ranks.mean(axis=0).sort_values()
