"""Print LaTeX-ready table rows for report.tex.

After running ``main.ipynb`` end-to-end (so that ``experiments/all_runs.csv``,
``experiments/summary.csv`` and ``experiments/tuning_best.csv`` exist), run
this script and paste the printed rows into the corresponding tables in
``report.tex``::

    python experiments/emit_latex.py

The script reads from the standard files in ``experiments/`` and writes
nothing -- it only prints.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from stac.stat_tests import (  # noqa: E402
    friedman_aligned_test,
    wilcoxon_signed_ranks_p_value,
    shaffer_post_hoc,
)


def _fmt(v: float, kind: str = "default") -> str:
    if pd.isna(v):
        return "--"
    if kind == "int":
        return f"{int(round(v)):,}".replace(",", "{,}")
    if kind == "big":
        return f"{int(round(v)):,}".replace(",", "{,}")
    if kind == "money":
        return f"{v:,.2f}".replace(",", "{,}")
    if kind == "decimal":
        return f"{v:.2f}"
    if kind == "small":
        return f"{v:.3f}"
    return f"{v:.3f}"


def main() -> int:
    exp = ROOT / "experiments"
    runs = pd.read_csv(exp / "all_runs.csv")
    print(f"% Source: {len(runs)} rows, "
          f"{runs.config_id.nunique()} configs, {runs.subject_id.nunique()} subjects")
    print()

    # ---- Table tab:summary --------------------------------------------------
    print("% --- Table tab:summary (paste between \\midrule and \\bottomrule) ---")
    agg = runs.groupby("config_id").agg(
        hv=("hypervolume", "mean"),
        igd=("igd", "mean"),
        spacing=("spacing", "mean"),
        delta=("delta_spread", "mean"),
        f1=("f1_best", "mean"),
        f2=("f2_best", "mean"),
        rt=("runtime_s", "mean"),
        front=("front_size", "mean"),
    )
    pretty = {
        "nsga2_rk_repair":   "\\texttt{nsga2\\_rk\\_repair}",
        "nsga2_di_repair":   "\\texttt{nsga2\\_di\\_repair}",
        "nsga2_di_penalty":  "\\texttt{nsga2\\_di\\_penalty}",
        "nsga2_di_death":    "\\texttt{nsga2\\_di\\_death}",
        "paes_di_repair":    "\\texttt{paes\\_di\\_repair}",
        "mopso_rk":          "\\texttt{mopso\\_rk}",
        "paco_di":           "\\texttt{paco\\_di}",
    }
    order = ["nsga2_rk_repair", "nsga2_di_repair", "nsga2_di_penalty", "nsga2_di_death",
             "paes_di_repair", "mopso_rk", "paco_di"]
    for cid in order:
        if cid not in agg.index:
            continue
        r = agg.loc[cid]
        print(
            f"{pretty[cid]:34s} & {_fmt(r['hv'], 'big')} & {_fmt(r['igd'], 'decimal')} "
            f"& {_fmt(r['spacing'], 'decimal')} & {_fmt(r['delta'], 'small')} "
            f"& {_fmt(r['f1'], 'decimal')} & {_fmt(r['f2'], 'decimal')} "
            f"& {_fmt(r['rt'], 'decimal')} & {_fmt(r['front'], 'decimal')} \\\\"
        )
    print()

    # ---- Friedman Aligned Ranks per metric ----------------------------------
    print("% --- Friedman Aligned Ranks (paste into Table tab:ranks paragraph) ---")
    wide = lambda metric: runs.pivot_table(
        index=["subject_id", "seed"], columns="config_id",
        values=metric, aggfunc="first",
    ).dropna(axis=0, how="any")
    for metric, hib in [("hypervolume", True), ("igd", False), ("runtime_s", False)]:
        wt = wide(metric)
        if wt.empty:
            continue
        samples = {c: wt[c].to_numpy() for c in wt.columns}
        T, p, ranks = friedman_aligned_test(samples, lower_is_better=(not hib))
        print(f"%   {metric:11s}: T = {T:.2f}, p = {p:.2e}")
        for c in sorted(ranks, key=ranks.get):
            print(f"%     {c:25s} rank = {ranks[c]:.2f}")
    print()

    # ---- Wilcoxon + Shaffer hypervolume -------------------------------------
    print("% --- Wilcoxon+Shaffer pairwise hypervolume (cite p_adj into the bullets) ---")
    wt = wide("hypervolume")
    samples = {c: wt[c].to_numpy() for c in wt.columns}
    df = shaffer_post_hoc(samples).sort_values("p_adj")
    for _, r in df.iterrows():
        print(f"%   {r['config_a']:25s} vs {r['config_b']:25s}  "
              f"p_raw = {r['p_raw']:.2e}  p_adj = {r['p_adj']:.2e}")
    print()

    # ---- Tuning winners table -----------------------------------------------
    tb = exp / "tuning_best.csv"
    if tb.exists():
        print("% --- tab:tuning_winners ---")
        best = pd.read_csv(tb)
        first = best.groupby("algorithm").head(1).set_index("algorithm")
        algo_order = ["NSGA-II", "PAES", "MOPSO", "P-ACO"]
        for algo in [a for a in algo_order if a in first.index]:
            r = first.loc[algo]
            cells = []
            if "pop_size" in r and pd.notna(r["pop_size"]):
                cells.append(f"pop={int(r['pop_size'])}")
            if "max_generations" in r and pd.notna(r["max_generations"]):
                cells.append(f"gen={int(r['max_generations'])}")
            if "max_archive_size" in r and pd.notna(r["max_archive_size"]):
                cells.append(f"archive={int(r['max_archive_size'])}")
            if "mutation_rate" in r and pd.notna(r["mutation_rate"]):
                cells.append(f"mut={r['mutation_rate']}")
            if "inertia" in r and pd.notna(r["inertia"]):
                cells.append(f"$w={r['inertia']}$")
            if (
                "c1" in r and "c2" in r
                and pd.notna(r["c1"]) and pd.notna(r["c2"])
                and float(r["c1"]) == float(r["c2"])
            ):
                cells.append(f"$c_1=c_2={r['c1']}$")
            elif "c1" in r and pd.notna(r["c1"]):
                cells.append(f"$c_1={r['c1']}$")
            if "c2" in r and pd.notna(r["c2"]) and not (
                "c1" in r and pd.notna(r["c1"]) and float(r["c1"]) == float(r["c2"])
            ):
                cells.append(f"$c_2={r['c2']}$")
            if "w1" in r and pd.notna(r["w1"]):
                cells.append(f"$w_1={r['w1']}$")
            if "w2" in r and pd.notna(r["w2"]):
                cells.append(f"$w_2={r['w2']}$")
            if "evaporation_rate" in r and pd.notna(r["evaporation_rate"]):
                cells.append(f"$\\rho={r['evaporation_rate']}$")
            if "alpha" in r and pd.notna(r["alpha"]):
                cells.append(f"$\\alpha={r['alpha']}$")
            if "initial_pheromone" in r and pd.notna(r["initial_pheromone"]):
                cells.append(f"$\\tau_0={r['initial_pheromone']}$")
            note = ", ".join(cells)
            print(f"{algo:10s} & {note} & tuning winner & "
                  f"{_fmt(r['hv_mean'], 'big')} & {_fmt(r['runtime_mean'], 'decimal')} \\\\")
    return 0


if __name__ == "__main__":
    sys.exit(main())
