"""Small Pareto archive utilities shared by swarm algorithms."""
from __future__ import annotations

import math
from typing import Any, Iterable


ArchiveEntry = dict[str, Any]


def dominates(a: tuple[float, ...], b: tuple[float, ...]) -> bool:
    """Return True when minimisation vector ``a`` Pareto-dominates ``b``."""
    return all(x <= y for x, y in zip(a, b)) and any(x < y for x, y in zip(a, b))


def crowding_distances(entries: list[ArchiveEntry]) -> list[float]:
    """NSGA-II crowding distance for a 2+ objective minimisation archive."""
    n = len(entries)
    if n == 0:
        return []
    if n <= 2:
        return [math.inf] * n

    m = len(entries[0]["fitness"])
    distances = [0.0] * n
    for obj in range(m):
        order = sorted(range(n), key=lambda i: entries[i]["fitness"][obj])
        distances[order[0]] = math.inf
        distances[order[-1]] = math.inf

        lo = float(entries[order[0]]["fitness"][obj])
        hi = float(entries[order[-1]]["fitness"][obj])
        span = hi - lo
        if span <= 0.0:
            continue

        for pos in range(1, n - 1):
            i = order[pos]
            if math.isinf(distances[i]):
                continue
            prev_v = float(entries[order[pos - 1]]["fitness"][obj])
            next_v = float(entries[order[pos + 1]]["fitness"][obj])
            distances[i] += (next_v - prev_v) / span
    return distances


def _entry_key(entry: ArchiveEntry) -> tuple:
    candidate = entry.get("candidate")
    if candidate is None:
        candidate_key = ()
    else:
        candidate_key = tuple(
            round(float(x), 12) if isinstance(x, float) else int(x)
            for x in candidate
        )
    return tuple(round(float(x), 12) for x in entry["fitness"]), candidate_key


def nondominated(entries: Iterable[ArchiveEntry]) -> list[ArchiveEntry]:
    """Return unique non-dominated archive entries."""
    unique: dict[tuple, ArchiveEntry] = {}
    for entry in entries:
        fitness = tuple(float(x) for x in entry["fitness"])
        copied = {**entry, "fitness": fitness, "candidate": list(entry["candidate"])}
        unique[_entry_key(copied)] = copied

    pool = list(unique.values())
    out: list[ArchiveEntry] = []
    for i, entry in enumerate(pool):
        if any(
            i != j and dominates(other["fitness"], entry["fitness"])
            for j, other in enumerate(pool)
        ):
            continue
        out.append(entry)
    return out


def prune_by_crowding(entries: list[ArchiveEntry], max_size: int) -> list[ArchiveEntry]:
    """Keep a bounded, diversity-preserving archive."""
    if max_size <= 0:
        return []
    if len(entries) <= max_size:
        return list(entries)

    distances = crowding_distances(entries)
    order = sorted(
        range(len(entries)),
        key=lambda i: (math.isinf(distances[i]), distances[i]),
        reverse=True,
    )
    return [entries[i] for i in order[:max_size]]


def update_archive(
    archive: list[ArchiveEntry],
    candidates: Iterable[ArchiveEntry],
    max_size: int,
) -> list[ArchiveEntry]:
    """Merge, Pareto-filter, and crowding-prune archive entries."""
    return prune_by_crowding(nondominated([*archive, *candidates]), max_size)


def best_by_sum(entries: list[ArchiveEntry]) -> ArchiveEntry:
    """Convenience representative for APIs that expose a single ``best_f``."""
    if not entries:
        raise ValueError("Cannot choose best entry from an empty archive")
    return min(entries, key=lambda e: sum(float(x) for x in e["fitness"]))
