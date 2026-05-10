"""Inverted Generational Distance (IGD).

IGD measures how well the obtained front A covers a reference set R:

    IGD(A, R) = (1/|R|) * sum over r in R of min_{a in A} ||r - a||

Smaller is better. Requires a reference Pareto front R.

When the true Pareto front is unknown (typical), R is taken as the union of
non-dominated points across all algorithms in the comparison.
"""
from __future__ import annotations

import math
from typing import Sequence


def _euclidean(a: Sequence[float], b: Sequence[float]) -> float:
    return math.sqrt(sum((float(x) - float(y)) ** 2 for x, y in zip(a, b)))


def inverted_generational_distance(
    front: Sequence[Sequence[float]],
    reference: Sequence[Sequence[float]],
) -> float:
    """Compute IGD between an obtained front and a reference Pareto set.

    Args:
        front: iterable of points (f1, f2, ...) produced by an algorithm.
        reference: iterable of reference Pareto-optimal points.

    Returns:
        IGD value (>= 0). Returns +inf when the obtained front is empty.
    """
    if not reference:
        return 0.0
    if not front:
        return float("inf")

    total = 0.0
    for r in reference:
        nearest = min(_euclidean(r, a) for a in front)
        total += nearest
    return float(total / len(reference))


def union_reference_front(*fronts: Sequence[Sequence[float]]) -> list[tuple[float, ...]]:
    """Build a reference Pareto front from the union of several fronts.

    Filters to non-dominated points in the combined set.
    """
    pool: list[tuple[float, ...]] = []
    for f in fronts:
        for p in f:
            pool.append(tuple(float(x) for x in p))

    if not pool:
        return []

    keep: list[tuple[float, ...]] = []
    for p in pool:
        dominated = False
        for q in pool:
            if q is p:
                continue
            if all(qx <= px for qx, px in zip(q, p)) and any(qx < px for qx, px in zip(q, p)):
                dominated = True
                break
        if not dominated:
            keep.append(p)

    # de-duplicate while preserving order
    seen: set[tuple[float, ...]] = set()
    unique: list[tuple[float, ...]] = []
    for p in keep:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    return unique
