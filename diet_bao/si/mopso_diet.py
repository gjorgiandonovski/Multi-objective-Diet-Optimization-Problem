"""Multi-objective PSO with non-dominated archive (MOPSO).

Recipe (SMPSO-style):

1. Each particle has a position and velocity in [0, 1]^n (random-key encoding).
2. Each particle remembers a personal best (pbest): the best non-dominated
   position it has visited.
3. An external archive holds the global Pareto front so far. New non-dominated
   particles are added; dominated archive entries are removed; the archive is
   pruned to max_archive_size by removing the most-crowded points.
4. At each step, each particle picks a leader from the archive via binary
   tournament on crowding distance.
5. Standard PSO velocity + position update with inertia (w), cognitive (c1),
   and social (c2) coefficients. Velocities and positions are clamped/reflected
   into [0, 1].

Built on the Representation abstraction so it natively supports random_key.
direct_index is rejected because MOPSO's velocity update requires continuous
positions.
"""
from __future__ import annotations

import math
import random
from typing import Any, Sequence

from diet_bao.constraints import REPAIR, ConstraintHandler
from diet_bao.fitness import fitness_vector
from diet_bao.representations import RANDOM_KEY, Representation


def _dominates(a: tuple[float, float], b: tuple[float, float]) -> bool:
    """Strict Pareto dominance for minimisation."""
    return (a[0] <= b[0] and a[1] <= b[1]) and (a[0] < b[0] or a[1] < b[1])


def _crowding_distances(points: list[tuple[float, float]]) -> list[float]:
    """Crowding distance per point (NSGA-II style)."""
    n = len(points)
    if n == 0:
        return []
    if n <= 2:
        return [math.inf] * n

    distances = [0.0] * n
    for m in range(2):  # 2 objectives
        order = sorted(range(n), key=lambda i: points[i][m])
        distances[order[0]] = math.inf
        distances[order[-1]] = math.inf
        f_min = points[order[0]][m]
        f_max = points[order[-1]][m]
        if f_max == f_min:
            continue
        norm = f_max - f_min
        for k in range(1, n - 1):
            prev_f = points[order[k - 1]][m]
            next_f = points[order[k + 1]][m]
            distances[order[k]] += (next_f - prev_f) / norm
    return distances


class _Archive:
    def __init__(self, max_size: int) -> None:
        self.max_size = int(max_size)
        self.positions: list[list[float]] = []
        self.fitnesses: list[tuple[float, float]] = []

    def consider(self, position: list[float], fit: tuple[float, float]) -> None:
        for af in self.fitnesses:
            if _dominates(af, fit):
                return
        keep = [
            i for i, af in enumerate(self.fitnesses)
            if not _dominates(fit, af) and af != fit
        ]
        self.positions = [self.positions[i] for i in keep] + [list(position)]
        self.fitnesses = [self.fitnesses[i] for i in keep] + [tuple(fit)]
        while len(self.fitnesses) > self.max_size:
            distances = _crowding_distances(self.fitnesses)
            worst = min(range(len(distances)), key=lambda i: distances[i])
            self.positions.pop(worst)
            self.fitnesses.pop(worst)

    def select_leader(self, rng: random.Random) -> list[float]:
        """Binary tournament on crowding distance."""
        if not self.positions:
            raise RuntimeError("Empty archive")
        if len(self.positions) == 1:
            return list(self.positions[0])
        i = rng.randrange(len(self.positions))
        j = rng.randrange(len(self.positions))
        while j == i:
            j = rng.randrange(len(self.positions))
        distances = _crowding_distances(self.fitnesses)
        winner = i if distances[i] >= distances[j] else j
        return list(self.positions[winner])


def run_mopso(
    foods: Sequence[dict],
    edad: int,
    ctarget: float,
    *,
    representation: Representation = RANDOM_KEY,
    constraint_handler: ConstraintHandler = REPAIR,
    pop_size: int = 60,
    max_generations: int = 80,
    inertia: float = 0.7,
    c1: float = 1.5,
    c2: float = 1.5,
    max_archive_size: int = 100,
    velocity_clamp: float = 0.4,
    seed: int = 1,
) -> dict[str, Any]:
    if representation.name != "random_key":
        raise ValueError("MOPSO requires the random_key representation (continuous positions).")

    rng = random.Random(seed)
    state = representation.build(foods, edad)
    n = state.length

    positions: list[list[float]] = [representation.generate(state, rng) for _ in range(pop_size)]
    velocities: list[list[float]] = [[rng.uniform(-0.1, 0.1) for _ in range(n)] for _ in range(pop_size)]

    def evaluate(position: list[float]) -> tuple[float, float]:
        decoded = representation.decode(state, position)
        f1, f2 = fitness_vector(decoded, state.foods, ctarget=ctarget)
        _, (f1c, f2c) = constraint_handler.process(decoded, state, ctarget, (f1, f2), rng)
        return float(f1c), float(f2c)

    fitnesses: list[tuple[float, float]] = [evaluate(p) for p in positions]
    pbests: list[list[float]] = [list(p) for p in positions]
    pbest_fits: list[tuple[float, float]] = list(fitnesses)

    archive = _Archive(max_archive_size)
    for p, f in zip(positions, fitnesses):
        archive.consider(p, f)

    trace: dict[str, list[float]] = {
        "generation": [],
        "best_scalar": [],
        "front_f1_min": [],
        "front_f2_min": [],
        "front_size": [],
    }

    def _record(gen: int) -> None:
        if archive.fitnesses:
            f1_vals = [f[0] for f in archive.fitnesses]
            f2_vals = [f[1] for f in archive.fitnesses]
        else:
            f1_vals = [f[0] for f in fitnesses]
            f2_vals = [f[1] for f in fitnesses]
        trace["generation"].append(float(gen))
        trace["best_scalar"].append(float(min(a + b for a, b in zip(f1_vals, f2_vals))))
        trace["front_f1_min"].append(float(min(f1_vals)))
        trace["front_f2_min"].append(float(min(f2_vals)))
        trace["front_size"].append(float(len(archive.fitnesses)))

    _record(0)

    for gen in range(1, max_generations + 1):
        for i in range(pop_size):
            leader = archive.select_leader(rng)
            for k in range(n):
                r1 = rng.random()
                r2 = rng.random()
                cognitive = c1 * r1 * (pbests[i][k] - positions[i][k])
                social = c2 * r2 * (leader[k] - positions[i][k])
                v = inertia * velocities[i][k] + cognitive + social
                if v > velocity_clamp:
                    v = velocity_clamp
                elif v < -velocity_clamp:
                    v = -velocity_clamp
                velocities[i][k] = v
                x = positions[i][k] + v
                if x < 0.0:
                    x = -x
                    velocities[i][k] = -velocities[i][k]
                if x > 1.0:
                    x = 2.0 - x
                    velocities[i][k] = -velocities[i][k]
                positions[i][k] = max(0.0, min(1.0, x))

            new_fit = evaluate(positions[i])
            fitnesses[i] = new_fit

            if _dominates(new_fit, pbest_fits[i]):
                pbests[i] = list(positions[i])
                pbest_fits[i] = new_fit
            elif not _dominates(pbest_fits[i], new_fit) and rng.random() < 0.5:
                pbests[i] = list(positions[i])
                pbest_fits[i] = new_fit

            archive.consider(positions[i], new_fit)

        _record(gen)

    front = list(archive.fitnesses)
    if not front:
        front = list(fitnesses)
    best_idx = min(range(len(front)), key=lambda i: front[i][0] + front[i][1])
    best_position = archive.positions[best_idx] if archive.positions else positions[best_idx]
    best_decoded = representation.decode(state, best_position)
    best_f = fitness_vector(best_decoded, state.foods, ctarget=ctarget)

    return {
        "front": front,
        "best_candidate": best_decoded,
        "best_f": best_f,
        "trace": trace,
        "representation": representation.name,
        "constraint_handler": constraint_handler.name,
        "archive_size": len(front),
    }
