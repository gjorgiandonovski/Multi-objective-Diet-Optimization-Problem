"""NSGA-II for the diet problem.

Consumes a Representation (direct_index | random_key) and a ConstraintHandler
(repair | penalty | death_penalty). The algorithm body itself is the inspyred
NSGA-II default; only the variator (mutation), evaluator and observer are wired
through the representation/constraint abstractions.
"""
from __future__ import annotations

import random
from typing import Any, Sequence

from diet_bao.constraints import REPAIR, ConstraintHandler
from diet_bao.fitness import fitness_vector
from diet_bao.representations import DIRECT_INDEX, Representation


def _make_evaluator(
    representation: Representation,
    state,
    ctarget: float,
    handler: ConstraintHandler,
    rng: random.Random,
):
    """Build an inspyred-compatible evaluator (decode -> fitness -> handler)."""
    from inspyred.ec.emo import Pareto

    def evaluator(candidates, args):
        out = []
        for raw in candidates:
            decoded = representation.decode(state, raw)
            f1, f2 = fitness_vector(decoded, state.foods, ctarget=ctarget)
            _, (f1c, f2c) = handler.process(decoded, state, ctarget, (f1, f2), rng)
            out.append(Pareto([float(f1c), float(f2c)]))
        return out

    return evaluator


def _make_mutation(representation: Representation, state, rate_key: str = "mutation_rate"):
    """Per-gene re-randomisation that respects the representation's repair semantics."""

    def variator(random, candidates, args):
        rate = float(args.get(rate_key, 0.1))
        out = []
        for cand in candidates:
            mutant = list(cand)
            if representation.name == "direct_index":
                for i, domain in enumerate(state.per_position):
                    if mutant[i] not in domain or random.random() < rate:
                        mutant[i] = domain[random.randrange(len(domain))]
            else:
                for i in range(len(mutant)):
                    if random.random() < rate:
                        delta = random.gauss(0.0, 0.1)
                        v = float(mutant[i]) + delta
                        if v < 0.0:
                            v = -v
                        if v > 1.0:
                            v = 2.0 - v
                        v = max(0.0, min(1.0, v))
                        mutant[i] = v
            mutant = representation.repair(state, mutant, random)
            out.append(mutant)
        return out

    return variator


def run_nsga2(
    foods: Sequence[dict],
    edad: int,
    ctarget: float,
    *,
    representation: Representation = DIRECT_INDEX,
    constraint_handler: ConstraintHandler = REPAIR,
    pop_size: int = 80,
    max_generations: int = 80,
    mutation_rate: float = 0.1,
    seed: int = 1,
) -> dict[str, Any]:
    from inspyred.ec import terminators, variators
    from inspyred.ec.emo import NSGA2

    rng = random.Random(seed)
    state = representation.build(foods, edad)

    trace: dict[str, list[float]] = {
        "generation": [],
        "best_scalar": [],
        "front_f1_min": [],
        "front_f2_min": [],
        "front_size": [],
    }

    def generator(random, args):
        return representation.generate(state, random)

    def observer(population, num_generations, num_evaluations, args):
        f1_vals = [float(ind.fitness.values[0]) for ind in population]
        f2_vals = [float(ind.fitness.values[1]) for ind in population]
        scalars = [a + b for a, b in zip(f1_vals, f2_vals)]
        trace["generation"].append(float(num_generations))
        trace["best_scalar"].append(float(min(scalars)))
        trace["front_f1_min"].append(float(min(f1_vals)))
        trace["front_f2_min"].append(float(min(f2_vals)))
        trace["front_size"].append(float(len(population)))

    algo = NSGA2(rng)
    algo.terminator = terminators.generation_termination
    algo.observer = observer
    algo.variator = [
        variators.n_point_crossover,
        _make_mutation(representation, state),
    ]

    final_pop = algo.evolve(
        generator=generator,
        evaluator=_make_evaluator(representation, state, ctarget, constraint_handler, rng),
        pop_size=pop_size,
        maximize=False,
        max_generations=max_generations,
        mutation_rate=mutation_rate,
    )

    front: list[tuple[float, float]] = []
    for ind in final_pop:
        f1, f2 = ind.fitness.values
        front.append((float(f1), float(f2)))

    best = min(final_pop, key=lambda ind: float(ind.fitness.values[0]) + float(ind.fitness.values[1]))
    best_decoded = representation.decode(state, best.candidate)
    best_f = fitness_vector(best_decoded, state.foods, ctarget=ctarget)

    return {
        "front": front,
        "best_candidate": best_decoded,
        "best_f": best_f,
        "trace": trace,
        "representation": representation.name,
        "constraint_handler": constraint_handler.name,
    }
