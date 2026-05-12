"""Post-processing helpers: per-subject summary tables and statistical tests.

Reads a tidy ``all_runs.csv`` produced by ``run_all_subjects`` and emits:

* ``summary.csv`` -- per (config, subject) descriptive statistics for every
  metric (mean, std, min, max).
* ``pairwise_hv.csv`` -- Wilcoxon signed-ranks p-values with Holm correction
  on hypervolume.
* ``pairwise_hv_shaffer.csv`` -- same raw p-values with Shaffer's static
  correction (course-recommended).
* ``friedman_aligned.csv`` -- Friedman Aligned Ranks omnibus per metric.
"""
from __future__ import annotations

from itertools import combinations

import numpy as np
import pandas as pd

from stac.stat_tests import (
    average_ranks,
    friedman_aligned_test,
    holm_correction,
    shaffer_post_hoc,
    wilcoxon_signed_ranks_p_value,
)


METRIC_COLS = ("f1_best", "f2_best", "runtime_s", "hypervolume",
               "igd", "spacing", "delta_spread", "front_size")


def per_subject_summary(runs: pd.DataFrame) -> pd.DataFrame:
    """Per (config, subject) mean/std/min/max for every metric column."""
    if runs.empty:
        return runs
    grouped = runs.groupby(["config_id", "subject_id", "algorithm"])
    return grouped[list(METRIC_COLS)].agg(["mean", "std", "min", "max"]).round(4)


def _wide_table(runs: pd.DataFrame, metric: str) -> pd.DataFrame:
    """Wide table indexed by (subject_id, seed), columns are config_ids."""
    return runs.pivot_table(
        index=["subject_id", "seed"],
        columns="config_id",
        values=metric,
        aggfunc="first",
    ).dropna(axis=0, how="any")


def pairwise_table(
    runs: pd.DataFrame,
    metric: str = "hypervolume",
    higher_is_better: bool = True,
) -> dict[str, pd.DataFrame]:
    """Run pairwise Wilcoxon signed-ranks tests on ``metric`` and return
    both Holm- and Shaffer-corrected p-value tables.
    """
    wt = _wide_table(runs, metric)
    if wt.empty:
        return {"holm": pd.DataFrame(), "shaffer": pd.DataFrame()}

    configs = list(wt.columns)
    samples = {c: wt[c].to_numpy() for c in configs}

    # Wilcoxon raw p-values for every pair.
    raw = []
    for a, b in combinations(configs, 2):
        p = wilcoxon_signed_ranks_p_value(samples[a], samples[b])
        raw.append({"config_a": a, "config_b": b, "p_raw": float(p)})
    df_raw = pd.DataFrame(raw)

    # Holm correction.
    holm = df_raw.copy()
    holm["p_adj"] = holm_correction(holm["p_raw"].tolist())
    holm = holm.sort_values("p_adj").reset_index(drop=True)

    # Shaffer correction.
    shaffer = shaffer_post_hoc(samples, pair_p_values=list(
        (r.config_a, r.config_b, r.p_raw) for r in df_raw.itertuples()
    )).sort_values("p_adj").reset_index(drop=True)

    return {"holm": holm, "shaffer": shaffer}


def friedman_aligned_table(runs: pd.DataFrame) -> pd.DataFrame:
    """Friedman Aligned Ranks omnibus on hypervolume, IGD, runtime and Delta Spread."""
    out_rows = []
    for metric, hib in [
        ("hypervolume", True),
        ("igd", False),
        ("runtime_s", False),
        ("delta_spread", False),
        ("spacing", False),
    ]:
        wt = _wide_table(runs, metric)
        if wt.empty:
            continue
        configs = list(wt.columns)
        samples = {c: wt[c].to_numpy() for c in configs}
        T, p, ranks = friedman_aligned_test(samples, lower_is_better=(not hib))
        row = {"metric": metric, "higher_is_better": hib, "statistic": T, "p_value": p}
        for c, r in ranks.items():
            row[f"rank_{c}"] = r
        out_rows.append(row)
    return pd.DataFrame(out_rows)


def regenerate_all(
    runs: pd.DataFrame,
    outdir: str,
) -> dict[str, str]:
    """Regenerate ``summary.csv``, pairwise tests and Friedman omnibus.

    Returns a dict mapping artefact name to the file path written.
    """
    import os
    os.makedirs(outdir, exist_ok=True)
    written: dict[str, str] = {}

    summ = per_subject_summary(runs)
    p = os.path.join(outdir, "summary.csv")
    summ.to_csv(p)
    written["summary"] = p

    pair = pairwise_table(runs, "hypervolume", higher_is_better=True)
    p_holm = os.path.join(outdir, "pairwise_hv.csv")
    p_shaffer = os.path.join(outdir, "pairwise_hv_shaffer.csv")
    pair["holm"].to_csv(p_holm, index=False)
    pair["shaffer"].to_csv(p_shaffer, index=False)
    written["pairwise_hv"] = p_holm
    written["pairwise_hv_shaffer"] = p_shaffer

    fa = friedman_aligned_table(runs)
    p_fa = os.path.join(outdir, "friedman_aligned.csv")
    fa.to_csv(p_fa, index=False)
    written["friedman_aligned"] = p_fa

    return written
