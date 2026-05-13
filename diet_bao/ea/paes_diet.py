"""PAES (Pareto Archived Evolution Strategy) wrapper for the diet problem.

PAES is a (1+1)-ES with an adaptive grid archive. Compared to NSGA-II
(dominance + crowding selection from a population), PAES uses an external
archive to select the parent for the next generation.

Wrapped on top of inspyred.ec.emo.PAES; the only change from default PAES is the
mutation variator, which is replaced so that it respects the active representation.
"""
from __future__ import annotations

import random
from typing import Any, Sequence

from diet_bao.constraints import REPAIR, ConstraintHandler
from diet_bao.fitness import fitness_vector_state
from diet_bao.representations import DIRECT_INDEX, Representation


def _make_evaluator(representation, state, ctarget, handler, rng):
    from inspyred.ec.emo import Pareto

    def evaluator(candidates, args):
        out = []
        for raw in candidates:
            decoded = representation.decode(state, raw)
            f1, f2 = fitness_vector_state(decoded, state, ctarget=ctarget)
            _, (f1c, f2c) = handler.process(decoded, state, ctarget, (f1, f2), rng)
            out.append(Pareto([float(f1c), float(f2c)]))
        return out

    return evaluator


def _make_mutation(representation, state, rate_key="mutation_rate"):
    """Per-gene re-randomisation with repair, identical to the NSGA-II mutator."""

    def variator(random, candidates, args):
        rate = float(args.get(rate_key, 0.1))
        out = []
        for cand in candidates:
            mutant = list(cand)
            if representation.name == "direct_index":
                for i, (domain, domain_set) in enumerate(zip(state.per_position, state.per_position_sets)):
                    if int(mutant[i]) not in domain_set or random.random() < rate:
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


def run_paes(
    foods: Sequence[dict],
    edad: int,
    ctarget: float,
    *,
    representation: Representation = DIRECT_INDEX,
    constraint_handler: ConstraintHandler = REPAIR,
    pop_size: int = 1,
    max_generations: int = 200,
    mutation_rate: float = 0.1,
    max_archive_size: int = 100,
    grid_divisions: int = 8,
    seed: int = 1,
) -> dict[str, Any]:
    from inspyred.ec import terminators
    from inspyred.ec.emo import PAES

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
        archive = args.get("_ec").archive if hasattr(args.get("_ec", None), "archive") else population
        if not archive:
            archive = population
        f1_vals = [float(ind.fitness.values[0]) for ind in archive]
        f2_vals = [float(ind.fitness.values[1]) for ind in archive]
        scalars = [a + b for a, b in zip(f1_vals, f2_vals)]
        trace["generation"].append(float(num_generations))
        trace["best_scalar"].append(float(min(scalars)))
        trace["front_f1_min"].append(float(min(f1_vals)))
        trace["front_f2_min"].append(float(min(f2_vals)))
        trace["front_size"].append(float(len(archive)))

    algo = PAES(rng)
    algo.terminator = terminators.generation_termination
    algo.observer = observer
    algo.variator = _make_mutation(representation, state)

    final_pop = algo.evolve(
        generator=generator,
        evaluator=_make_evaluator(representation, state, ctarget, constraint_handler, rng),
        pop_size=pop_size,
        maximize=False,
        max_generations=max_generations,
        mutation_rate=mutation_rate,
        max_archive_size=max_archive_size,
        num_grid_divisions=grid_divisions,
    )

    archive = list(getattr(algo, "archive", final_pop)) or list(final_pop)
    front: list[tuple[float, float]] = [
        (float(ind.fitness.values[0]), float(ind.fitness.values[1])) for ind in archive
    ]

    best = min(archive, key=lambda ind: float(ind.fitness.values[0]) + float(ind.fitness.values[1]))
    best_decoded = representation.decode(state, best.candidate)
    best_f = fitness_vector_state(best_decoded, state, ctarget=ctarget)

    return {
        "front": front,
        "best_candidate": best_decoded,
        "best_f": best_f,
        "trace": trace,
        "representation": representation.name,
        "constraint_handler": constraint_handler.name,
    }
