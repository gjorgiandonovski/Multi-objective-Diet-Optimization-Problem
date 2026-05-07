from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple


def dominates(a: Sequence[float], b: Sequence[float]) -> bool:
    """True if a Pareto-dominates b (minimization)."""
    return all(x <= y for x, y in zip(a, b)) and any(x < y for x, y in zip(a, b))


def pareto_front(points: Iterable[Sequence[float]]) -> List[Tuple[float, ...]]:
    pts = [tuple(map(float, p)) for p in points]
    front: List[Tuple[float, ...]] = []
    for p in pts:
        if any(dominates(q, p) for q in pts if q is not p):
            continue
        front.append(p)
    # Deduplicate
    return sorted(set(front))


def knee_point(front: Sequence[Sequence[float]], w1: float = 1.0, w2: float = 1.0) -> Tuple[float, ...]:
    """Pick a single representative solution from a Pareto front via weighted sum."""
    if not front:
        raise ValueError("Empty front")
    best = min(front, key=lambda p: (w1 * float(p[0]) + w2 * float(p[1])))
    return tuple(map(float, best))
