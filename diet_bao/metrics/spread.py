"""Diversity metrics for a 2D Pareto front.

Two formulas are exposed:

- delta_spread (Deb): the diversity metric taught in the BAO course
  (chapter 6.2). Combines the extent of the front (distance from the
  obtained extreme points to a reference set of extreme points) with
  the uniformity of the spacing between consecutive solutions.

      Delta = (sum_j d_j^e + sum_i |d_i - d_bar|)
            / (sum_j d_j^e + |S| * d_bar)

  Lower is better; Delta = 0 corresponds to a perfectly uniform front
  whose extremes coincide with the reference extremes.

- schott_spacing: the simpler standard-deviation-of-spacing metric.
  Kept as an internal helper because it is one of the components
  inside delta_spread.
"""
from __future__ import annotations

import math
from typing import Sequence


def _euclidean(a: Sequence[float], b: Sequence[float]) -> float:
    return math.sqrt(sum((float(x) - float(y)) ** 2 for x, y in zip(a, b)))


def schott_spacing(front: Sequence[Sequence[float]]) -> float:
    """Standard deviation of consecutive Euclidean distances along a 2D front.

    Smaller is more uniform; returns 0.0 for fronts with fewer than 2 points.
    """
    pts = [tuple(float(x) for x in p) for p in front]
    if len(pts) < 2:
        return 0.0
    pts.sort(key=lambda p: p[0])
    distances = [_euclidean(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    dbar = sum(distances) / len(distances)
    variance = sum((d - dbar) ** 2 for d in distances) / max(len(distances) - 1, 1)
    return float(math.sqrt(variance))


def delta_spread(
    front: Sequence[Sequence[float]],
    reference_extremes: Sequence[Sequence[float]] | None = None,
) -> float:
    """Deb's Delta diversity metric (course-syllabus formula, 2D version).

    Args:
        front: iterable of (f1, f2) points produced by an algorithm.
        reference_extremes: optional iterable of two points giving the true
            extremes of the Pareto front (one minimising each objective). When
            omitted (the typical case where the true front is unknown), the
            extremes of the obtained front itself are used and Delta only
            measures the uniformity of internal spacing.

    Returns:
        Delta value in [0, +inf). Lower is better. Returns 0.0 for fronts with
        fewer than 2 points.
    """
    pts = sorted([tuple(float(x) for x in p) for p in front], key=lambda p: p[0])
    n = len(pts)
    if n < 2:
        return 0.0

    distances = [_euclidean(pts[i], pts[i + 1]) for i in range(n - 1)]
    dbar = sum(distances) / len(distances)

    # Extent term: distance from each "boundary" of the obtained front to the
    # corresponding extreme point of the reference set.
    if reference_extremes is None:
        # No reference set known -> set extent contribution to zero so Delta
        # collapses to the spread component.
        extent_sum = 0.0
    else:
        ref_pts = [tuple(float(x) for x in p) for p in reference_extremes]
        if len(ref_pts) != 2:
            raise ValueError("reference_extremes must contain exactly 2 extreme points for a 2D front")
        # Match each reference extreme to the obtained extreme on its dominant axis.
        ref_min_f1 = min(ref_pts, key=lambda p: p[0])
        ref_min_f2 = min(ref_pts, key=lambda p: p[1])
        obt_min_f1 = pts[0]                   # smallest f1 -> first after sort by f1
        obt_min_f2 = min(pts, key=lambda p: p[1])
        d1e = _euclidean(ref_min_f1, obt_min_f1)
        d2e = _euclidean(ref_min_f2, obt_min_f2)
        extent_sum = d1e + d2e

    spacing_sum = sum(abs(d - dbar) for d in distances)
    numerator = extent_sum + spacing_sum
    denominator = extent_sum + n * dbar
    if denominator == 0:
        return 0.0
    return float(numerator / denominator)
