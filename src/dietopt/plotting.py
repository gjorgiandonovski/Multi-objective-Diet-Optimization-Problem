from __future__ import annotations

from typing import Dict, Iterable, List, Sequence, Tuple


def extract_front_xy(front: Iterable[Sequence[float]]) -> Tuple[List[float], List[float]]:
    x: List[float] = []
    y: List[float] = []
    for p in front:
        x.append(float(p[0]))
        y.append(float(p[1]))
    return x, y


def plot_convergence(trace: Dict, ax, label: str):
    gens = trace.get("generation", [])
    best = trace.get("best_scalar", [])
    ax.plot(gens, best, label=label)
    ax.set_xlabel("Generation")
    ax.set_ylabel("Best scalar objective")


def plot_pareto(front: Sequence[Sequence[float]], ax, label: str):
    xs, ys = extract_front_xy(front)
    ax.scatter(xs, ys, s=20, alpha=0.8, label=label)
    ax.set_xlabel("f1 (calorie deviation)")
    ax.set_ylabel("f2 (macro deviation)")
