from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from dietopt.metrics import knee_point, pareto_front


@dataclass(frozen=True)
class RunResult:
    algorithm: str
    seed: int
    runtime_s: float
    # Representative objective values (f1, f2)
    f1: float
    f2: float
    # Optional traces for plotting
    trace: Optional[Dict[str, Any]] = None


def run_replicates(
    algorithm_name: str,
    run_fn: Callable[..., Dict[str, Any]],
    n_runs: int,
    seed0: int,
    **kwargs,
) -> List[RunResult]:
    results: List[RunResult] = []

    for i in range(n_runs):
        seed = seed0 + i
        t0 = time.perf_counter()
        out = run_fn(seed=seed, **kwargs)
        dt = time.perf_counter() - t0

        # Expect `front` as list of (f1, f2).
        front = pareto_front(out["front"]) if "front" in out else []
        if not front:
            # fallback to single objective point
            f1, f2 = out.get("best_f", (float("inf"), float("inf")))
        else:
            f1, f2 = knee_point(front)

        results.append(
            RunResult(
                algorithm=algorithm_name,
                seed=seed,
                runtime_s=dt,
                f1=float(f1),
                f2=float(f2),
                trace=out.get("trace"),
            )
        )

    return results


def mann_whitney_u_p_value(a: Sequence[float], b: Sequence[float]) -> float:
    """Two-sided Mann-Whitney U test p-value (requires SciPy)."""
    try:
        from scipy.stats import mannwhitneyu
    except Exception as e:  # pragma: no cover
        raise RuntimeError("SciPy is required for statistical tests. Install `scipy`.") from e

    res = mannwhitneyu(a, b, alternative="two-sided")
    return float(res.pvalue)
