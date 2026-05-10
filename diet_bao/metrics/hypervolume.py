"""2D hypervolume (a.k.a. S-metric) for minimization problems.

For a 2-objective minimization problem, the hypervolume of a front F relative
to a reference point r is the area of the union of rectangles
    { (x, y) | f1 <= x <= r1, f2 <= y <= r2 }
for each non-dominated point (f1, f2) in F.

For 2D, this can be computed in O(n log n) by:
1. Filter to non-dominated points (relative to the reference).
2. Sort by f1 ascending.
3. Sweep across, summing the strip area (r1 - f1) * (prev_f2 - f2).

Larger HV is better.
"""
from __future__ import annotations

from typing import Iterable, Sequence


def _is_dominated_or_outside(p: tuple[float, float], r: tuple[float, float], front: Iterable[tuple[float, float]]) -> bool:
    if p[0] >= r[0] or p[1] >= r[1]:
        return True
    for q in front:
        if q is p:
            continue
        if q[0] <= p[0] and q[1] <= p[1] and (q[0] < p[0] or q[1] < p[1]):
            return True
    return False


def hypervolume_2d(
    front: Sequence[Sequence[float]],
    reference: Sequence[float],
) -> float:
    """Compute 2D hypervolume for a minimization Pareto front.

    Args:
        front: iterable of (f1, f2) points.
        reference: (r1, r2) reference point that dominates the worst-case point.
            Must satisfy r_i > max f_i over the front, otherwise points outside
            are clipped (return 0 contribution).

    Returns:
        Hypervolume value (>= 0).
    """
    r = (float(reference[0]), float(reference[1]))
    pts: list[tuple[float, float]] = [(float(p[0]), float(p[1])) for p in front]
    if not pts:
        return 0.0

    keep = [p for p in pts if not _is_dominated_or_outside(p, r, pts)]
    if not keep:
        return 0.0

    keep.sort(key=lambda p: (p[0], p[1]))

    hv = 0.0
    prev_f2 = r[1]
    for f1, f2 in keep:
        if f2 >= prev_f2:
            # Dominated by an earlier (lower-f1) point in the sweep.
            continue
        width = r[0] - f1
        height = prev_f2 - f2
        hv += width * height
        prev_f2 = f2
    return float(hv)
