from __future__ import annotations

import random
from typing import Any, Dict, List, Sequence, Tuple

from dietopt.decode import build_position_domains, decode_continuous
from utils.fitness import fitness_vector


def run_pso_scalarized(
    comida_bd: Sequence[dict],
    edad: int,
    ctarget: float,
    *,
    pop_size: int = 60,
    max_generations: int = 80,
    w1: float = 1.0,
    w2: float = 1.0,
    seed: int = 1,
) -> Dict[str, Any]:
    """Run PSO (swarm) on a continuous encoding, decoded to valid discrete plans.

    PSO in inspyred is single-objective, so we scalarize the 2 objectives:
    scalar = w1*f1 + w2*f2.
    """

    try:
        from inspyred import swarm
        from inspyred.ec import Bounder, terminators
    except Exception as e:  # pragma: no cover
        raise RuntimeError("Missing dependency: inspyred. Install `inspyred`.") from e

    prng = random.Random(seed)
    position_domains = build_position_domains(comida_bd, edad)

    trace: Dict[str, List[float]] = {"generation": [], "best_scalar": []}

    def generator(random: random.Random, args: Dict):
        # candidate in [0,1]
        return [random.random() for _ in range(len(position_domains.per_position))]

    def evaluator(candidates: Sequence[Sequence[float]], args: Dict):
        out = []
        for cand in candidates:
            ind = decode_continuous(cand, position_domains)
            f1, f2 = fitness_vector(ind, list(comida_bd), float(ctarget))
            out.append((w1 * float(f1)) + (w2 * float(f2)))
        return out

    def observer(population, num_generations, num_evaluations, args):
        best = min(population, key=lambda ind: float(ind.fitness))
        trace["generation"].append(float(num_generations))
        trace["best_scalar"].append(float(best.fitness))

    pso = swarm.PSO(prng)
    pso.terminator = terminators.generation_termination
    pso.observer = observer

    bounder = Bounder(0.0, 1.0)
    final_pop = pso.evolve(
        generator=generator,
        evaluator=evaluator,
        pop_size=pop_size,
        maximize=False,
        bounder=bounder,
        max_generations=max_generations,
    )

    best = min(final_pop, key=lambda ind: float(ind.fitness))
    best_candidate_cont = list(best.candidate)
    best_candidate = decode_continuous(best_candidate_cont, position_domains)
    best_f = fitness_vector(best_candidate, list(comida_bd), float(ctarget))

    # For comparison plots, expose a "front" with just the best point.
    front: List[Tuple[float, float]] = [(float(best_f[0]), float(best_f[1]))]

    return {"front": front, "best_candidate": best_candidate, "best_f": best_f, "trace": trace}
