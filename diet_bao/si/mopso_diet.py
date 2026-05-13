"""Multi-objective PSO for the diet optimisation problem.

This is a Pareto-based MOPSO: particles move in random-key space, an external
archive stores non-dominated solutions, leaders are selected from that archive,
and crowding-distance pruning keeps the archive bounded and diverse.
"""
from __future__ import annotations

import random
from typing import Any, Sequence

from diet_bao.fitness import fitness_vector_state
from diet_bao.representations import RANDOM_KEY, Representation
from diet_bao.si.pareto_archive import (
    ArchiveEntry,
    best_by_sum,
    dominates,
    update_archive,
)


def _sigma_2d(fitness: tuple[float, float]) -> float:
    """Mostaghim-Teich sigma value for two objectives."""
    f1, f2 = float(fitness[0]), float(fitness[1])
    denom = (f1 * f1) + (f2 * f2)
    if denom <= 0.0:
        return 0.0
    return ((f1 * f1) - (f2 * f2)) / denom


def _select_leader(
    archive: list[ArchiveEntry],
    particle_fitness: tuple[float, float],
    rng: random.Random,
    method: str,
) -> ArchiveEntry:
    if not archive:
        raise ValueError("Cannot select a leader from an empty archive")
    if method == "random":
        return archive[rng.randrange(len(archive))]
    if method != "sigma":
        raise ValueError("leader_method must be 'sigma' or 'random'")

    sigma = _sigma_2d(particle_fitness)
    return min(archive, key=lambda entry: abs(_sigma_2d(entry["fitness"]) - sigma))


def _evaluate(position: list[float], state, representation: Representation, ctarget: float) -> tuple[list[int], tuple[float, float]]:
    decoded = representation.decode(state, position)
    f = fitness_vector_state(decoded, state, ctarget=ctarget)
    return decoded, tuple(map(float, f))


def run_mopso(
    foods: Sequence[dict],
    edad: int,
    ctarget: float,
    *,
    representation: Representation = RANDOM_KEY,
    pop_size: int = 60,
    max_generations: int = 80,
    max_archive_size: int = 80,
    inertia: float = 0.4,
    c1: float = 1.5,
    c2: float = 1.5,
    velocity_clamp: float = 0.2,
    leader_method: str = "sigma",
    seed: int = 1,
) -> dict[str, Any]:
    """Run MOPSO and return the non-dominated archive as the final front."""
    if representation.name != RANDOM_KEY.name:
        raise ValueError("MOPSO currently requires the random_key representation")

    rng = random.Random(seed)
    state = representation.build(foods, edad)

    positions = [representation.generate(state, rng) for _ in range(pop_size)]
    velocities = [
        [rng.uniform(-velocity_clamp, velocity_clamp) for _ in range(state.length)]
        for _ in range(pop_size)
    ]

    pbest: list[ArchiveEntry] = []
    initial_entries: list[ArchiveEntry] = []
    for position in positions:
        decoded, fitness = _evaluate(position, state, representation, ctarget)
        entry = {"candidate": list(position), "decoded": decoded, "fitness": fitness}
        pbest.append(entry)
        initial_entries.append(entry)

    archive = update_archive([], initial_entries, max_archive_size)
    trace: dict[str, list[float]] = {
        "generation": [0.0],
        "best_scalar": [float(sum(best_by_sum(archive)["fitness"]))],
        "archive_size": [float(len(archive))],
    }

    for gen in range(1, max_generations + 1):
        current_entries: list[ArchiveEntry] = []
        for i in range(pop_size):
            leader = _select_leader(archive, pbest[i]["fitness"], rng, leader_method)
            leader_position = leader["candidate"]
            pbest_position = pbest[i]["candidate"]

            for j in range(state.length):
                r1 = rng.random()
                r2 = rng.random()
                velocities[i][j] = (
                    (inertia * velocities[i][j])
                    + (c1 * r1 * (pbest_position[j] - positions[i][j]))
                    + (c2 * r2 * (leader_position[j] - positions[i][j]))
                )
                if velocities[i][j] > velocity_clamp:
                    velocities[i][j] = velocity_clamp
                elif velocities[i][j] < -velocity_clamp:
                    velocities[i][j] = -velocity_clamp

                positions[i][j] += velocities[i][j]
                if positions[i][j] < 0.0:
                    positions[i][j] = 0.0
                    velocities[i][j] *= -0.5
                elif positions[i][j] > 1.0:
                    positions[i][j] = 1.0
                    velocities[i][j] *= -0.5

            decoded, fitness = _evaluate(positions[i], state, representation, ctarget)
            current = {"candidate": list(positions[i]), "decoded": decoded, "fitness": fitness}
            current_entries.append(current)

            old_f = pbest[i]["fitness"]
            if dominates(fitness, old_f):
                pbest[i] = current
            elif not dominates(old_f, fitness) and rng.random() < 0.5:
                pbest[i] = current

        archive = update_archive(archive, current_entries, max_archive_size)
        best = best_by_sum(archive)
        trace["generation"].append(float(gen))
        trace["best_scalar"].append(float(sum(best["fitness"])))
        trace["archive_size"].append(float(len(archive)))

    best = best_by_sum(archive)
    return {
        "front": [tuple(entry["fitness"]) for entry in archive],
        "best_candidate": list(best["decoded"]),
        "best_f": tuple(best["fitness"]),
        "trace": trace,
        "representation": representation.name,
        "constraint_handler": "none",
        "leader_method": leader_method,
    }
