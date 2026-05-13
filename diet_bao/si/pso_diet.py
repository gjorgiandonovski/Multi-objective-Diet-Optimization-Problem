"""Scalarised PSO baseline (single-objective via weighted sum).

This provides the required swarm-intelligence method using ``inspyred.swarm.PSO``.
"""
from __future__ import annotations

import random
from typing import Any, Sequence

from diet_bao.fitness import fitness_vector_state
from diet_bao.representations import RANDOM_KEY, Representation


def run_pso(
    foods: Sequence[dict],
    edad: int,
    ctarget: float,
    *,
    representation: Representation = RANDOM_KEY,
    pop_size: int = 60,
    max_generations: int = 80,
    w1: float = 1.0,
    w2: float = 1.0,
    seed: int = 1,
) -> dict[str, Any]:
    from inspyred import swarm
    from inspyred.ec import Bounder, terminators

    rng = random.Random(seed)
    state = representation.build(foods, edad)
    trace: dict[str, list[float]] = {"generation": [], "best_scalar": []}

    def generator(random, args):
        return representation.generate(state, random)

    def evaluator(candidates, args):
        vals = []
        for cand in candidates:
            decoded = representation.decode(state, cand)
            f1, f2 = fitness_vector_state(decoded, state, ctarget=ctarget)
            vals.append((w1 * f1) + (w2 * f2))
        return vals

    def observer(population, num_generations, num_evaluations, args):
        best = min(population, key=lambda ind: float(ind.fitness))
        trace["generation"].append(float(num_generations))
        trace["best_scalar"].append(float(best.fitness))

    algo = swarm.PSO(rng)
    algo.terminator = terminators.generation_termination
    algo.observer = observer

    final_pop = algo.evolve(
        generator=generator,
        evaluator=evaluator,
        pop_size=pop_size,
        maximize=False,
        bounder=Bounder(0.0, 1.0),
        max_generations=max_generations,
    )

    best = min(final_pop, key=lambda ind: float(ind.fitness))
    best_decoded = representation.decode(state, best.candidate)
    best_f = fitness_vector_state(best_decoded, state, ctarget=ctarget)

    return {
        "front": [tuple(map(float, best_f))],
        "best_candidate": best_decoded,
        "best_f": tuple(map(float, best_f)),
        "trace": trace,
        "representation": representation.name,
    }
