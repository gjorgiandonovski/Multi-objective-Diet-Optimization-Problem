"""Plotting helpers for the diet optimization experiments.

All plotting functions take a matplotlib Axes so the caller controls layout.
"""
from __future__ import annotations

from typing import Sequence


def plot_convergence(trace: dict, ax, label: str) -> None:
    """Best scalar (f1+f2) of the population over generations."""
    ax.plot(trace.get("generation", []), trace.get("best_scalar", []), label=label)
    ax.set_xlabel("Generation")
    ax.set_ylabel("Best scalar objective (f1 + f2)")


def plot_objective_min_over_time(trace: dict, ax, label: str) -> None:
    """Track f1_min and f2_min separately to show convergence per objective."""
    gens = trace.get("generation", [])
    f1 = trace.get("front_f1_min", [])
    f2 = trace.get("front_f2_min", [])
    if f1:
        ax.plot(gens, f1, label=f"{label} f1 min", linestyle="-")
    if f2:
        ax.plot(gens, f2, label=f"{label} f2 min", linestyle="--")
    ax.set_xlabel("Generation")
    ax.set_ylabel("Min objective value")


def plot_front_size_over_time(trace: dict, ax, label: str) -> None:
    """Diversity proxy: size of the Pareto front (or archive) over generations."""
    ax.plot(trace.get("generation", []), trace.get("front_size", []), label=label)
    ax.set_xlabel("Generation")
    ax.set_ylabel("Pareto front / archive size")


def plot_pareto(front: Sequence[Sequence[float]], ax, label: str, marker: str = "o") -> None:
    """Scatter plot of a Pareto front in objective space."""
    x = [float(p[0]) for p in front]
    y = [float(p[1]) for p in front]
    ax.scatter(x, y, s=20, alpha=0.7, label=label, marker=marker)
    ax.set_xlabel("f1 (calorie deviation)")
    ax.set_ylabel("f2 (macro deviation)")


def plot_reference_front(front: Sequence[Sequence[float]], ax, label: str = "Reference") -> None:
    """Plot a reference Pareto front as a dashed line connecting sorted points."""
    pts = sorted([(float(p[0]), float(p[1])) for p in front], key=lambda p: p[0])
    if not pts:
        return
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ax.plot(xs, ys, linestyle="--", marker="x", label=label, alpha=0.8)


def plot_metric_box(df, metric: str, group_by: str, ax, title: str | None = None) -> None:
    """Boxplot of a metric across a grouping column (e.g., algorithm or config_id)."""
    df.boxplot(column=metric, by=group_by, ax=ax)
    ax.set_title(title or metric)
    ax.set_xlabel(group_by)
    ax.set_ylabel(metric)
