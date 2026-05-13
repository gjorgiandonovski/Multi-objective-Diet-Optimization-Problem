"""End-to-end smoke test: load the real dataset, run a tiny benchmark across all
algorithms, print summary metrics and a Friedman significance test.

Tiny pop / few generations -- the goal is to confirm wiring, not produce
report-quality results. Should finish in under a minute.

Usage (from the project root with the venv active):
    python smoke_test.py
"""
from __future__ import annotations

import sys
import time


def main() -> int:
    print("Loading real dataset from MySQL...")
    try:
        from diet_bao.experiment.experiment_loader import (
            AlgorithmConfig,
            BenchmarkPlan,
            load_real_dataset,
            run_all_subjects,
        )
        from stac.stat_tests import friedman_test, average_ranks
    except Exception as exc:
        print(f"[FAIL] Imports failed: {exc}")
        return 1

    foods, subjects = load_real_dataset()
    print(f"  foods={len(foods)}  subjects={len(subjects)}")

    plan = BenchmarkPlan(
        configs=[
            AlgorithmConfig("nsga2_di_repair", "NSGA-II", "direct_index", "repair", 30, 15),
            AlgorithmConfig("nsga2_rk_repair", "NSGA-II", "random_key", "repair", 30, 15),
            AlgorithmConfig("paes_di_repair", "PAES", "direct_index", "repair", 1, 100, extra={"max_archive_size": 30}),
            AlgorithmConfig("mopso_rk", "MOPSO", "random_key", "none", 30, 15, extra={"max_archive_size": 30}),
            AlgorithmConfig("paco_di", "P-ACO", "direct_index", "none", 30, 15, extra={"max_archive_size": 30}),
        ],
        n_runs=3,
        seed0=0,
    )
    target_subject = [subjects[0]]

    t0 = time.perf_counter()
    df = run_all_subjects(target_subject, foods, plan)
    elapsed = time.perf_counter() - t0
    print(f"\nRan {len(df)} configurations x replicates in {elapsed:.2f}s")

    summary = df.groupby(["config_id", "algorithm"])[["hypervolume", "igd", "spacing", "front_size", "runtime_s"]].mean().round(3)
    print("\nMean metrics per configuration:")
    print(summary.to_string())

    samples_hv = {cfg: df[df.config_id == cfg].hypervolume.tolist() for cfg in df.config_id.unique()}
    if all(len(v) >= 1 for v in samples_hv.values()) and len(samples_hv) >= 3:
        try:
            stat, p = friedman_test(samples_hv)
            print(f"\nFriedman on hypervolume: stat={stat:.3f}  p={p:.4g}")
            print("Average ranks (best HV first):")
            print(average_ranks(samples_hv, lower_is_better=False).to_string())
        except Exception as exc:
            print(f"[INFO] Friedman skipped: {exc}")

    print("\n[OK] All algorithms ran end-to-end on the real dataset.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
