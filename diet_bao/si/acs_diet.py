"""Scalarised Ant Colony System baseline via inspyred.

Uses ``inspyred.swarm.ACS`` (an ACO variant) as a discrete, constructive
single-objective baseline. The two objectives (f1, f2) are combined via a
weighted sum and inverted into a positive maximisation fitness.

Because ACS is a discrete constructive method, this implementation currently
operates on the direct-index representation.
"""
from __future__ import annotations

import random
from typing import Any, Sequence

from diet_bao.fitness import fitness_vector_state
from diet_bao.representations import DIRECT_INDEX, Representation


def run_acs(
    foods: Sequence[dict],
    edad: int,
    ctarget: float,
    *,
    representation: Representation = DIRECT_INDEX,
    pop_size: int = 40,
    max_generations: int = 80,
    evaporation_rate: float = 0.1,
    learning_rate: float = 0.1,
    initial_pheromone: float = 1.0,
    w1: float = 1.0,
    w2: float = 1.0,
    seed: int = 1,
) -> dict[str, Any]:
    """Run Ant Colony System (ACS) and return a single best point.

    Parameters mirror the other scalarised baselines (PSO/ACO), with ACS-
    specific pheromone parameters.
    """
    from inspyred import swarm
    from inspyred.ec import terminators
    from inspyred.swarm import TrailComponent

    if representation is not DIRECT_INDEX and getattr(representation, "name", None) != DIRECT_INDEX.name:
        raise ValueError(
            "ACS baseline currently supports only the direct_index representation"
        )

    rng = random.Random(seed)
    state = DIRECT_INDEX.build(foods, edad)

    # One component represents selecting a concrete food id for a concrete slot.
    # Candidate solutions are a list of TrailComponents, one per slot.
    components: list[TrailComponent] = []
    per_slot: list[list[TrailComponent]] = []
    for j, domain in enumerate(state.per_position):
        slot_components: list[TrailComponent] = []
        for food_id in domain:
            c = TrailComponent((j, int(food_id)), value=1.0, maximize=True)
            c.pheromone = float(initial_pheromone)
            slot_components.append(c)
            components.append(c)
        per_slot.append(slot_components)

    trace: dict[str, list[float]] = {"generation": [], "best_scalar": []}

    def _weighted_choice(random_local: random.Random, items: list[TrailComponent]) -> TrailComponent:
        weights = [max(float(c.desirability), 1e-12) for c in items]
        total = sum(weights)
        r = random_local.random() * total
        acc = 0.0
        for c, w in zip(items, weights):
            acc += w
            if r <= acc:
                return c
        return items[-1]

    def generator(random: random.Random, args: dict) -> list[TrailComponent]:
        trail: list[TrailComponent] = []
        for slot_components in per_slot:
            trail.append(_weighted_choice(random, slot_components))
        return trail

    def evaluator(candidates: list[list[TrailComponent]], args: dict) -> list[float]:
        fitnesses: list[float] = []
        for trail in candidates:
            decoded = [int(c.element[1]) for c in trail]
            f1, f2 = fitness_vector_state(decoded, state, ctarget=ctarget)
            scalar = (w1 * float(f1)) + (w2 * float(f2))
            fitnesses.append(1.0 / (scalar + 1e-9))
        return fitnesses

    def observer(population: list, num_generations: int, num_evaluations: int, args: dict) -> None:
        if not population:
            return
        best = max(population, key=lambda ind: float(ind.fitness))
        best_scalar = (1.0 / (float(best.fitness) + 1e-12))
        trace["generation"].append(float(num_generations))
        trace["best_scalar"].append(float(best_scalar))

    algo = swarm.ACS(rng, components)
    algo.terminator = terminators.generation_termination
    algo.observer = observer
    algo.evaporation_rate = float(evaporation_rate)
    algo.learning_rate = float(learning_rate)
    algo.initial_pheromone = float(initial_pheromone)

    final_pop = algo.evolve(
        generator=generator,
        evaluator=evaluator,
        pop_size=pop_size,
        maximize=True,
        max_generations=max_generations,
    )

    best_ind = None
    if getattr(algo, "archive", None):
        best_ind = max(algo.archive, key=lambda ind: float(ind.fitness))
    if best_ind is None and final_pop:
        best_ind = max(final_pop, key=lambda ind: float(ind.fitness))

    if best_ind is None:
        best_f = (0.0, 0.0)
        best_candidate = None
    else:
        best_candidate = [int(c.element[1]) for c in best_ind.candidate]
        best_f_raw = fitness_vector_state(best_candidate, state, ctarget=ctarget)
        best_f = tuple(map(float, best_f_raw))

    return {
        "front": [best_f],
        "best_candidate": best_candidate,
        "best_f": best_f,
        "trace": trace,
        "representation": DIRECT_INDEX.name,
        "constraint_handler": "none",
    }
