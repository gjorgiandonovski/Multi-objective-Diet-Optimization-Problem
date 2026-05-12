"""Hyperparameter tuning sweeps for the diet optimisation experiment.

The tuning protocol is deliberately small but defensible:

* For each algorithm we define a 2--3 dimensional grid that varies the
  hyperparameters with the largest expected effect (population, generations,
  mutation rate, archive size, swarm weights).
* Every configuration in the grid is replicated `n_runs` times (default 5)
  on a small number of representative subjects (default subjects 1 and 4 --
  one large caloric target and one small one).
* The selection metric is the mean hypervolume across the replicates; ties
  are broken by mean runtime (shorter is better).

The output is a tidy DataFrame with one row per (algorithm, hyperparameter
combination, subject, seed) plus a per-algorithm summary that picks the best
setting. The notebook saves the tidy DataFrame to ``experiments/tuning_results.csv``
and feeds the summary into the main grid.
"""
from __future__ import annotations

import itertools
import time
from dataclasses import dataclass
from typing import Any, Sequence

import pandas as pd

from diet_bao.experiment.experiment_loader import (
    AlgorithmConfig,
    BenchmarkPlan,
    _evaluate_run,
)
from diet_bao.metrics.igd import union_reference_front
from diet_bao.types import SubjectProfile


@dataclass(frozen=True)
class TuningGrid:
    """One algorithm's tuning grid: parameter name -> list of candidate values."""
    algorithm: str            # e.g. "NSGA-II"
    representation: str       # e.g. "direct_index"
    constraint_handler: str   # e.g. "repair"
    params: dict[str, list[Any]]
    fixed: dict[str, Any]


def default_tuning_grids() -> list[TuningGrid]:
    """Tuning grids used in the report.

    Each grid is small (8--12 combinations) so the whole tuning phase finishes
    in 10--20 minutes even on a laptop.
    """
    return [
        TuningGrid(
            algorithm="NSGA-II",
            representation="direct_index",
            constraint_handler="repair",
            params={
                "pop_size": [40, 80],
                "max_generations": [40, 80],
                "mutation_rate": [0.05, 0.1, 0.2],
            },
            fixed={},
        ),
        TuningGrid(
            algorithm="PAES",
            representation="direct_index",
            constraint_handler="repair",
            params={
                "max_generations": [400, 800],
                "max_archive_size": [40, 80],
                "mutation_rate": [0.05, 0.1, 0.2],
            },
            fixed={"pop_size": 1},
        ),
        TuningGrid(
            algorithm="PSO-scalar",
            representation="random_key",
            constraint_handler="repair",
            params={
                "pop_size": [30, 60],
                "max_generations": [40, 80],
                # Scalarisation weights (w1 * f1 + w2 * f2). Because f1 dwarfs
                # f2 numerically, weights that favour f2 are explored too.
                "w1w2": [(1.0, 1.0), (1.0, 5.0), (1.0, 10.0)],
            },
            fixed={},
        ),
        TuningGrid(
            algorithm="ACS",
            representation="direct_index",
            constraint_handler="none",
            params={
                "pop_size": [30, 60],
                "max_generations": [40, 80],
                "evaporation_rate": [0.05, 0.1],
                "learning_rate": [0.05, 0.1],
                "w1w2": [(1.0, 5.0)],
            },
            fixed={"initial_pheromone": 1.0},
        ),
    ]


def _expand_grid(grid: TuningGrid) -> list[dict[str, Any]]:
    """Cartesian product of grid.params, with each entry merged with grid.fixed."""
    keys = list(grid.params.keys())
    values = [grid.params[k] for k in keys]
    out = []
    for combo in itertools.product(*values):
        params = dict(zip(keys, combo))
        # c1c2 is a convenience parameter -- expand it into c1 and c2.
        if "c1c2" in params:
            v = params.pop("c1c2")
            params["c1"] = v
            params["c2"] = v
        # w1w2 is a convenience pair -- expand it into w1 and w2.
        if "w1w2" in params:
            w1, w2 = params.pop("w1w2")
            params["w1"] = w1
            params["w2"] = w2
        merged = {**grid.fixed, **params}
        out.append(merged)
    return out


def _config_id(grid: TuningGrid, params: dict[str, Any]) -> str:
    """Build a short, stable id for a tuning configuration."""
    parts = [grid.algorithm.lower().replace("-", "").replace(" ", "")]
    # Force a deterministic ordering for readability.
    for k in (
        "pop_size",
        "max_generations",
        "mutation_rate",
        "inertia",
        "c1",
        "c2",
        "w1",
        "w2",
        "max_archive_size",
        "evaporation_rate",
        "learning_rate",
        "initial_pheromone",
    ):
        if k not in params:
            continue
        v = params[k]
        if k == "max_archive_size":
            parts.append(f"a{v}")
        elif k == "pop_size":
            parts.append(f"p{v}")
        elif k == "max_generations":
            parts.append(f"g{v}")
        elif k == "mutation_rate":
            parts.append(f"m{str(v).replace('.', '')}")
        elif k == "inertia":
            parts.append(f"w{str(v).replace('.', '')}")
        elif k == "c1":
            parts.append(f"c{str(v).replace('.', '')}")
        elif k == "w1":
            parts.append(f"w1-{str(v).replace('.', '')}")
        elif k == "w2":
            parts.append(f"w2-{str(v).replace('.', '')}")
        elif k == "evaporation_rate":
            parts.append(f"rho{str(v).replace('.', '')}")
        elif k == "learning_rate":
            parts.append(f"lr{str(v).replace('.', '')}")
        elif k == "initial_pheromone":
            parts.append(f"t0{str(v).replace('.', '')}")
        # c2 and other already collapsed by c1.
    return "_".join(parts)


def run_tuning_grid(
    grids: Sequence[TuningGrid],
    subjects: list[SubjectProfile],
    foods: list[dict],
    n_runs: int = 5,
    seed0: int = 1000,
) -> pd.DataFrame:
    """Run every tuning combination ``n_runs`` times on every subject in
    ``subjects`` and return the tidy long-form DataFrame.

    Hypervolume is computed against a per-subject reference front built from
    the union of all fronts produced across the entire tuning sweep on that
    subject. This is the same protocol as the main experiment.
    """
    if not subjects:
        return pd.DataFrame()

    # --- 1. Schedule and execute every tuning task. -----------------------
    raw: list[dict[str, Any]] = []
    for subject in subjects:
        per_subject_fronts: list[list[tuple[float, ...]]] = []
        per_subject_runs: list[dict[str, Any]] = []
        for grid in grids:
            for params in _expand_grid(grid):
                # Build an AlgorithmConfig on the fly. We strip parameters
                # consumed by AlgorithmConfig itself from the `extra` dict.
                pop_size = params.pop("pop_size", grid.fixed.get("pop_size", 50))
                max_generations = params.pop("max_generations", 50)
                cfg = AlgorithmConfig(
                    config_id=_config_id(grid, {
                        **params,
                        "pop_size": pop_size,
                        "max_generations": max_generations,
                    }),
                    algorithm=grid.algorithm,
                    representation=grid.representation,
                    constraint_handler=grid.constraint_handler,
                    pop_size=pop_size,
                    max_generations=max_generations,
                    extra=params,
                )
                runner = cfg.runner()
                kwargs = cfg.kwargs()
                for r in range(n_runs):
                    seed = seed0 + r
                    t0 = time.perf_counter()
                    res = runner(foods, subject.edad, subject.calorias, seed=seed, **kwargs)
                    dt = time.perf_counter() - t0
                    front = [tuple(p) for p in res["front"]]
                    per_subject_fronts.append(front)
                    per_subject_runs.append({
                        "subject_id": subject.sujeto_id,
                        "algorithm": grid.algorithm,
                        "representation": grid.representation,
                        "constraint_handler": grid.constraint_handler,
                        "config_id": cfg.config_id,
                        "pop_size": pop_size,
                        "max_generations": max_generations,
                        **{k: v for k, v in params.items() if k != "extra"},
                        "seed": seed,
                        "runtime_s": float(dt),
                        "f1_best": float(res["best_f"][0]),
                        "f2_best": float(res["best_f"][1]),
                        "front": front,
                    })

        # --- 2. Per-subject reference front for HV / IGD. -----------------
        reference_front = union_reference_front(*per_subject_fronts)

        for run in per_subject_runs:
            hv, igd, sp, ds = _evaluate_run(
                {"front": run["front"]}, reference_front,
            )
            run["hypervolume"] = hv
            run["igd"] = igd
            run["spacing"] = sp
            run["delta_spread"] = ds
            run["front_size"] = len(run["front"])
            del run["front"]
            raw.append(run)

    return pd.DataFrame(raw)


def best_configurations(tuning_df: pd.DataFrame) -> pd.DataFrame:
    """Pick the best (algorithm-specific) hyperparameter combination.

    Selection criterion: highest mean hypervolume averaged across subjects.
    Ties (within 1\\% relative hypervolume) are broken by mean runtime.
    """
    if tuning_df.empty:
        return tuning_df

    keep_cols = [
        "algorithm", "config_id", "pop_size", "max_generations",
        "mutation_rate", "inertia", "c1", "c2", "w1", "w2", "max_archive_size",
        "evaporation_rate", "learning_rate", "initial_pheromone",
    ]
    keep_cols = [c for c in keep_cols if c in tuning_df.columns]

    summary = (
        tuning_df.groupby(keep_cols, dropna=False)
                 .agg(hv_mean=("hypervolume", "mean"),
                      hv_std=("hypervolume", "std"),
                      igd_mean=("igd", "mean"),
                      runtime_mean=("runtime_s", "mean"),
                      n=("seed", "count"))
                 .reset_index()
    )

    rows = []
    for algo, group in summary.groupby("algorithm"):
        ranked = group.sort_values(
            by=["hv_mean", "runtime_mean"],
            ascending=[False, True],
        ).reset_index(drop=True)
        ranked["rank"] = ranked.index + 1
        rows.append(ranked)
    return pd.concat(rows, ignore_index=True)
