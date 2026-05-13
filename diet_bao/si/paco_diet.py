"""Pareto Ant Colony Optimisation for the diet problem.

The construction graph is the 77-slot meal plan.  Each slot has a pheromone
distribution over its admissible foods; ants sample one food per slot, the
external archive keeps non-dominated plans, and pheromone is reinforced from
archive members rather than from a scalar weighted objective.
"""
from __future__ import annotations

import math
import random
from typing import Any, Sequence

from diet_bao.fitness import fitness_vector_state
from diet_bao.representations import DIRECT_INDEX, Representation
from diet_bao.si.pareto_archive import (
    ArchiveEntry,
    best_by_sum,
    crowding_distances,
    update_archive,
)


def _weighted_choice(
    rng: random.Random,
    items: Sequence[int],
    weights: Sequence[float],
) -> int:
    total = sum(weights)
    if total <= 0.0:
        return items[rng.randrange(len(items))]
    target = rng.random() * total
    acc = 0.0
    for item, weight in zip(items, weights):
        acc += weight
        if target <= acc:
            return int(item)
    return int(items[-1])


def run_paco(
    foods: Sequence[dict],
    edad: int,
    ctarget: float,
    *,
    representation: Representation = DIRECT_INDEX,
    pop_size: int = 40,
    max_generations: int = 80,
    max_archive_size: int = 80,
    evaporation_rate: float = 0.1,
    alpha: float = 1.0,
    initial_pheromone: float = 1.0,
    q: float = 1.0,
    tau_min: float = 1e-6,
    tau_max: float = 100.0,
    seed: int = 1,
) -> dict[str, Any]:
    """Run Pareto ACO and return the archive as the final front."""
    if representation.name != DIRECT_INDEX.name:
        raise ValueError("P-ACO currently requires the direct_index representation")

    rng = random.Random(seed)
    state = representation.build(foods, edad)
    tau: list[dict[int, float]] = [
        {int(food_id): float(initial_pheromone) for food_id in domain}
        for domain in state.per_position
    ]

    def construct() -> list[int]:
        solution: list[int] = []
        for j, domain in enumerate(state.per_position):
            weights = [
                max(tau[j][int(food_id)], tau_min) ** alpha
                for food_id in domain
            ]
            solution.append(_weighted_choice(rng, domain, weights))
        return solution

    def evaluate(candidate: list[int]) -> ArchiveEntry:
        decoded = representation.repair(state, candidate, rng)
        f = fitness_vector_state(decoded, state, ctarget=ctarget)
        return {"candidate": list(decoded), "decoded": list(decoded), "fitness": tuple(map(float, f))}

    def evaporate() -> None:
        keep = max(0.0, 1.0 - evaporation_rate)
        for j, domain in enumerate(state.per_position):
            for food_id in domain:
                fid = int(food_id)
                tau[j][fid] = max(tau[j][fid] * keep, tau_min)

    def deposit_from_archive(archive: list[ArchiveEntry]) -> None:
        if not archive:
            return
        distances = crowding_distances(archive)
        finite = [d for d in distances if not math.isinf(d)]
        max_finite = max(finite) if finite else 1.0

        for entry, distance in zip(archive, distances):
            if math.isinf(distance):
                diversity_bonus = 1.0
            elif max_finite <= 0.0:
                diversity_bonus = 0.0
            else:
                diversity_bonus = distance / max_finite
            deposit = (q * (1.0 + diversity_bonus)) / len(archive)
            for j, food_id in enumerate(entry["candidate"]):
                fid = int(food_id)
                tau[j][fid] = min(tau[j][fid] + deposit, tau_max)

    archive: list[ArchiveEntry] = []
    trace: dict[str, list[float]] = {
        "generation": [],
        "best_scalar": [],
        "archive_size": [],
    }

    for gen in range(max_generations + 1):
        colony = [evaluate(construct()) for _ in range(pop_size)]
        archive = update_archive(archive, colony, max_archive_size)
        evaporate()
        deposit_from_archive(archive)

        best = best_by_sum(archive)
        trace["generation"].append(float(gen))
        trace["best_scalar"].append(float(sum(best["fitness"])))
        trace["archive_size"].append(float(len(archive)))

    best = best_by_sum(archive)
    return {
        "front": [tuple(entry["fitness"]) for entry in archive],
        "best_candidate": list(best["candidate"]),
        "best_f": tuple(best["fitness"]),
        "trace": trace,
        "representation": representation.name,
        "constraint_handler": "none",
    }
