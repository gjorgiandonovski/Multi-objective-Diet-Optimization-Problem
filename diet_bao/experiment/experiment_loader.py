"""Experiment runner for the diet optimisation problem.

Composes (algorithm x representation x constraint_handler) configurations,
runs N replicates per configuration per subject, and records fitness, runtime,
Pareto front size, hypervolume, IGD, Schott's spacing and Delta Spread.
"""
from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any, Callable

import pandas as pd

from diet_bao.constraints import ALL_HANDLERS
from diet_bao.data import load_foods_from_db, load_subjects_from_db
from diet_bao.ea.nsga2_diet import run_nsga2
from diet_bao.ea.paes_diet import run_paes
from diet_bao.metrics import (
    delta_spread,
    hypervolume_2d,
    inverted_generational_distance,
    schott_spacing,
)
from diet_bao.metrics.igd import union_reference_front
from diet_bao.representations import ALL_REPRESENTATIONS
from diet_bao.si.mopso_diet import run_mopso
from diet_bao.si.pso_diet import run_pso
from diet_bao.types import SubjectProfile


ALGORITHM_RUNNERS: dict[str, Callable[..., dict[str, Any]]] = {
    "NSGA-II": run_nsga2,
    "PAES": run_paes,
    "PSO-scalar": run_pso,
    "MOPSO": run_mopso,
}


@dataclass(frozen=True)
class AlgorithmConfig:
    """One concrete (algorithm, representation, constraint handler) configuration."""
    config_id: str
    algorithm: str
    representation: str
    constraint_handler: str
    pop_size: int = 50
    max_generations: int = 50
    extra: dict[str, Any] = field(default_factory=dict)

    def kwargs(self) -> dict[str, Any]:
        kw: dict[str, Any] = {
            "representation": ALL_REPRESENTATIONS[self.representation],
            "pop_size": self.pop_size,
            "max_generations": self.max_generations,
        }
        if self.algorithm in {"NSGA-II", "PAES", "MOPSO"}:
            kw["constraint_handler"] = ALL_HANDLERS[self.constraint_handler]
        kw.update(self.extra)
        return kw

    def runner(self) -> Callable[..., dict[str, Any]]:
        return ALGORITHM_RUNNERS[self.algorithm]


@dataclass(frozen=True)
class BenchmarkPlan:
    """A list of configurations and the number of stochastic replicates per configuration."""
    configs: list[AlgorithmConfig]
    n_runs: int = 30
    seed0: int = 100


@dataclass(frozen=True)
class RunResult:
    subject_id: int
    config_id: str
    algorithm: str
    representation: str
    constraint_handler: str
    seed: int
    runtime_s: float
    f1_best: float
    f2_best: float
    front_size: int
    hypervolume: float
    igd: float
    spacing: float
    delta_spread: float


def load_real_dataset() -> tuple[list[dict], list[SubjectProfile]]:
    return load_foods_from_db(), load_subjects_from_db()


def default_plan(n_runs: int = 30, seed0: int = 100) -> BenchmarkPlan:
    """Reference benchmark plan touching every algorithm and constraint handler."""
    configs = [
        AlgorithmConfig("nsga2_di_repair", "NSGA-II", "direct_index", "repair", 80, 80),
        AlgorithmConfig("nsga2_rk_repair", "NSGA-II", "random_key", "repair", 80, 80),
        AlgorithmConfig("nsga2_di_penalty", "NSGA-II", "direct_index", "penalty", 80, 80),
        AlgorithmConfig("paes_di_repair", "PAES", "direct_index", "repair", 1, 800,
                        extra={"max_archive_size": 80, "mutation_rate": 0.1}),
        AlgorithmConfig("pso_scalar_rk", "PSO-scalar", "random_key", "repair", 60, 80),
        AlgorithmConfig("mopso_rk_repair", "MOPSO", "random_key", "repair", 60, 80,
                        extra={"max_archive_size": 80}),
    ]
    return BenchmarkPlan(configs=configs, n_runs=n_runs, seed0=seed0)


def _hv_reference(front: list[tuple[float, float]], pad: float = 1.1) -> tuple[float, float]:
    if not front:
        return (1.0, 1.0)
    return (max(p[0] for p in front) * pad + 1.0, max(p[1] for p in front) * pad + 1.0)


def _reference_extremes(reference_front: list[tuple[float, ...]]) -> list[tuple[float, ...]] | None:
    """Pick the two extremes of the per-subject reference front for Delta Spread."""
    if not reference_front or len(reference_front) < 2:
        return None
    pts = [tuple(float(x) for x in p) for p in reference_front]
    min_f1 = min(pts, key=lambda p: p[0])
    min_f2 = min(pts, key=lambda p: p[1])
    if min_f1 == min_f2:
        return None
    return [min_f1, min_f2]


def _evaluate_run(result: dict[str, Any], reference_front: list[tuple[float, ...]]) -> tuple[float, float, float, float]:
    front = [tuple(p) for p in result["front"]]
    if not front:
        return 0.0, float("inf"), 0.0, 0.0
    ref_point = _hv_reference(front)
    hv = hypervolume_2d(front, reference=ref_point)
    igd = inverted_generational_distance(front, reference_front) if reference_front else 0.0
    sp = schott_spacing(front)
    extremes = _reference_extremes(reference_front)
    ds = delta_spread(front, reference_extremes=extremes)
    return float(hv), float(igd), float(sp), float(ds)


def evaluate_single_run(cfg: AlgorithmConfig, subject: SubjectProfile, foods: list[dict], seed: int) -> tuple:
    runner = cfg.runner()
    kwargs = cfg.kwargs()
    t0 = time.perf_counter()
    res = runner(foods, subject.edad, subject.calorias, seed=seed, **kwargs)
    dt = time.perf_counter() - t0
    return subject.sujeto_id, cfg, seed, res, dt


def run_subject(subject: SubjectProfile, foods: list[dict], plan: BenchmarkPlan, raw_results: list | None = None) -> pd.DataFrame:
    if raw_results is None:
        raw_results = []
        for cfg in plan.configs:
            for r in range(plan.n_runs):
                seed = plan.seed0 + r
                # Strip subject_id from return value for backwards compatibility within this func
                _, cfg_out, seed_out, res_out, dt_out = evaluate_single_run(cfg, subject, foods, seed)
                raw_results.append((cfg_out, seed_out, res_out, dt_out))

    all_fronts = [[tuple(p) for p in res["front"]] for _, _, res, _ in raw_results]
    reference_front = union_reference_front(*all_fronts)

    rows = []
    for cfg, seed, res, dt in raw_results:
        front = [tuple(p) for p in res["front"]]
        f1_best, f2_best = res["best_f"]
        hv, igd, sp, ds = _evaluate_run(res, reference_front)
        rows.append(asdict(RunResult(
            subject_id=subject.sujeto_id,
            config_id=cfg.config_id,
            algorithm=cfg.algorithm,
            representation=cfg.representation,
            constraint_handler=cfg.constraint_handler,
            seed=seed,
            runtime_s=float(dt),
            f1_best=float(f1_best),
            f2_best=float(f2_best),
            front_size=len(front),
            hypervolume=hv,
            igd=igd,
            spacing=sp,
            delta_spread=ds,
        )))
    return pd.DataFrame(rows)


def run_all_subjects(subjects: list[SubjectProfile], foods: list[dict], plan: BenchmarkPlan, parallel: bool = True) -> pd.DataFrame:
    import concurrent.futures
    import multiprocessing

    if not parallel:
        frames = [run_subject(s, foods, plan) for s in subjects]
    else:
        max_workers = min(multiprocessing.cpu_count(), 32)
        print(f"Parallel evaluation across {max_workers} processes...")
        raw_results_by_sub = {s.sujeto_id: [] for s in subjects}
        
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for s in subjects:
                for cfg in plan.configs:
                    for r in range(plan.n_runs):
                        seed = plan.seed0 + r
                        futures.append(executor.submit(evaluate_single_run, cfg, s, foods, seed))
            
            for future in concurrent.futures.as_completed(futures):
                subj_id, cfg, seed, res, dt = future.result()
                raw_results_by_sub[subj_id].append((cfg, seed, res, dt))
                
        # Reconstruct frames post-parallelism
        frames = []
        for s in subjects:
            if raw_results_by_sub[s.sujeto_id]:
                frames.append(run_subject(s, foods, plan, raw_results=raw_results_by_sub[s.sujeto_id]))
                
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def summarize_results(results: pd.DataFrame) -> pd.DataFrame:
    if results.empty:
        return pd.DataFrame()
    metric_cols = [c for c in [
        "f1_best", "f2_best", "runtime_s",
        "hypervolume", "igd", "spacing", "delta_spread", "front_size",
    ] if c in results.columns]
    return (
        results.groupby(["config_id", "subject_id", "algorithm"])[metric_cols]
        .agg(["mean", "std", "min", "max"])
        .sort_index()
    )
