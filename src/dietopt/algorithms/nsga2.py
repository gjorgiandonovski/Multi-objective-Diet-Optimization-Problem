from __future__ import annotations

import random
from typing import Any, Dict, List, Sequence, Tuple

from dietopt.decode import build_position_domains
from utils.encoding import create_random_individual
from utils.fitness import evaluate_candidates, fitness_vector


def _constrained_mutation(random: random.Random, candidates: List[List[int]], args: Dict) -> List[List[int]]:
    rate = float(args.get("mutation_rate", 0.1))
    domains = args["position_domains"].per_position

    out: List[List[int]] = []
    for candidate in candidates:
        mutant = list(candidate)
        for i in range(len(mutant)):
            if random.random() < rate:
                domain = domains[i]
                mutant[i] = domain[random.randrange(len(domain))]
        out.append(mutant)
    return out


def run_nsga2(
    comida_bd: Sequence[dict],
    edad: int,
    ctarget: float,
    *,
    pop_size: int = 80,
    max_generations: int = 80,
    mutation_rate: float = 0.1,
    seed: int = 1,
) -> Dict[str, Any]:
    """Run NSGA-II (multi-objective) using a discrete, constraint-respecting encoding."""

    try:
        from inspyred.ec.emo import NSGA2
        from inspyred.ec import terminators, variators
    except Exception as e:  # pragma: no cover
        raise RuntimeError("Missing dependency: inspyred. Install `inspyred`.") from e

    prng = random.Random(seed)
    position_domains = build_position_domains(comida_bd, edad)

    trace: Dict[str, List[float]] = {"generation": [], "best_scalar": []}

    def generator(random: random.Random, args: Dict):
        return create_random_individual(comida_bd=args["comida_bd"], edad=args["edad"], rng=random)

    def observer(population, num_generations, num_evaluations, args):
        # Track a scalarized best just for convergence plotting.
        best = min(
            population,
            key=lambda ind: float(ind.fitness.values[0]) + float(ind.fitness.values[1])
            if hasattr(ind.fitness, "values")
            else float(ind.fitness[0]) + float(ind.fitness[1]),
        )
        if hasattr(best.fitness, "values"):
            f1, f2 = best.fitness.values
        else:
            f1, f2 = best.fitness
        trace["generation"].append(float(num_generations))
        trace["best_scalar"].append(float(f1) + float(f2))

    ea = NSGA2(prng)
    ea.terminator = terminators.generation_termination
    ea.observer = observer
    ea.variator = [variators.n_point_crossover, _constrained_mutation]

    final_pop = ea.evolve(
        generator=generator,
        evaluator=evaluate_candidates,
        pop_size=pop_size,
        maximize=False,
        max_generations=max_generations,
        mutation_rate=mutation_rate,
        comida_bd=list(comida_bd),
        edad=int(edad),
        ctarget=float(ctarget),
        position_domains=position_domains,
    )

    # Extract objective vectors.
    front: List[Tuple[float, float]] = []
    for ind in final_pop:
        if hasattr(ind.fitness, "values"):
            f1, f2 = ind.fitness.values
        else:
            f1, f2 = ind.fitness
        front.append((float(f1), float(f2)))

    # Provide one representative candidate too.
    best_ind = min(final_pop, key=lambda ind: sum(ind.fitness.values) if hasattr(ind.fitness, "values") else sum(ind.fitness))
    best_candidate = list(best_ind.candidate)
    best_f = fitness_vector(best_candidate, list(comida_bd), float(ctarget))

    return {"front": front, "best_candidate": best_candidate, "best_f": best_f, "trace": trace}
