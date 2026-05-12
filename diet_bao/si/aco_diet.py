"""Scalarised Ant Colony Optimisation baseline (Ant System variant).

Like the PSO baseline this is a single-objective method (weighted sum of f1
and f2), so it returns a front of cardinality 1.  It is included as a second
swarm-intelligence algorithm alongside PSO, providing a direct comparison
between velocity-based (PSO) and pheromone-guided (ACO) search on the same
problem.

Implementation notes
--------------------
* Each ant constructs a complete 77-slot diet plan by sampling each slot
  independently from the pheromone distribution over that slot's admissible
  food set.  This treats the 77 slots as independent construction steps, which
  is the natural formulation for problems without inter-slot path dependencies.
* Pheromone update follows the classic Ant System (AS) rule [1]:

      tau_{j,i} <- (1 - rho) * tau_{j,i}  +  sum_k  Q / scalar_k

  where rho is the evaporation rate and Q / scalar_k is the deposit of ant k.
  Better solutions (lower scalar) therefore leave stronger traces.
* A pheromone floor ``tau_min`` prevents stagnation when one food monopolises
  a slot in later generations.
* The ``inspyred.ec.EvolutionaryComputation`` class provides the outer loop,
  reproducible seeding, and the observer hook used for pheromone updates.
  The variator discards parent candidates and constructs a fresh colony each
  generation, which matches the constructive nature of ACO.

References
----------
[1] Dorigo, M., Maniezzo, V., & Colorni, A. (1996).
    Ant system: optimization by a colony of cooperating agents.
    IEEE Transactions on Systems, Man, and Cybernetics -- Part B, 26(1), 29-41.
"""
from __future__ import annotations

import random
from typing import Any, Sequence

from diet_bao.fitness import fitness_vector
from diet_bao.representations import DIRECT_INDEX, Representation


def run_aco(
    foods: Sequence[dict],
    edad: int,
    ctarget: float,
    *,
    representation: Representation = DIRECT_INDEX,
    pop_size: int = 40,
    max_generations: int = 80,
    evaporation_rate: float = 0.1,
    alpha: float = 1.0,
    q: float = 1000.0,
    w1: float = 1.0,
    w2: float = 1.0,
    seed: int = 1,
) -> dict[str, Any]:
    """Run Ant System on the diet problem and return a single best point.

    Parameters
    ----------
    foods:
        Full food catalogue as loaded from the database.
    edad:
        User age (used to filter admissible foods per slot).
    ctarget:
        Daily caloric target for the user profile.
    representation:
        Encoding to use; defaults to direct_index.  The pheromone matrix is
        built over the admissible set D_j for each slot, so it aligns
        naturally with the direct-index encoding.
    pop_size:
        Colony size -- number of ants constructing solutions per generation.
    max_generations:
        Number of construction-and-update cycles.
    evaporation_rate:
        Fraction of pheromone that evaporates each cycle (rho in AS).
        Larger values lead to faster forgetting and more exploration.
    alpha:
        Pheromone influence exponent.  Higher values concentrate
        selection on the currently best food choices.
    q:
        Pheromone deposit constant.  Each ant deposits Q / scalar on its
        path, so solutions with a lower weighted objective leave stronger
        traces.
    w1, w2:
        Scalarisation weights for the two objectives: w1*f1 + w2*f2.
    seed:
        Random seed for full reproducibility.
    """
    from inspyred.ec import EvolutionaryComputation, replacers, selectors, terminators

    rng = random.Random(seed)
    state = representation.build(foods, edad)

    # ------------------------------------------------------------------
    # Pheromone matrix: one dict per slot mapping food_id -> pheromone.
    # Uniform initialisation so the first generation is essentially random.
    # ------------------------------------------------------------------
    tau: list[dict[int, float]] = [
        {food_id: 1.0 for food_id in domain}
        for domain in state.per_position
    ]
    tau_min: float = 1e-6  # floor to prevent fully degenerate distributions

    trace: dict[str, list[float]] = {"generation": [], "best_scalar": []}

    # Global best tracked across all generations (elitism at reporting level).
    _best: dict[str, Any] = {
        "scalar": float("inf"),
        "candidate": None,
        "f": (0.0, 0.0),
    }

    # ------------------------------------------------------------------
    # Inner helper: construct one ant solution from current pheromone state.
    # ------------------------------------------------------------------
    def _construct(rng_local: random.Random) -> list[int]:
        solution: list[int] = []
        for j, domain in enumerate(state.per_position):
            weights = [tau[j][fid] ** alpha for fid in domain]
            total = sum(weights)
            r = rng_local.random() * total
            cumulative = 0.0
            chosen = domain[-1]  # fallback to last element
            for fid, w in zip(domain, weights):
                cumulative += w
                if r <= cumulative:
                    chosen = fid
                    break
            solution.append(chosen)
        return solution

    # ------------------------------------------------------------------
    # inspyred callbacks
    # ------------------------------------------------------------------
    def generator(rng_local: random.Random, args: dict) -> list[int]:
        return _construct(rng_local)

    def evaluator(candidates: list, args: dict) -> list[float]:
        scores: list[float] = []
        for cand in candidates:
            f1, f2 = fitness_vector(cand, state.foods, ctarget=ctarget)
            scores.append(w1 * float(f1) + w2 * float(f2))
        return scores

    def variator(rng_local: random.Random, candidates: list, args: dict) -> list[list[int]]:
        """Construct a fresh colony each generation.

        Parent candidates are intentionally ignored: ants always rebuild
        solutions from scratch using the current pheromone state, which is
        the defining characteristic of constructive ACO.
        """
        return [_construct(rng_local) for _ in candidates]

    def observer(
        population: list,
        num_generations: int,
        num_evaluations: int,
        args: dict,
    ) -> None:
        """AS pheromone update: global evaporation then proportional deposit."""
        # Evaporation
        for j, domain in enumerate(state.per_position):
            for fid in domain:
                tau[j][fid] = max(tau[j][fid] * (1.0 - evaporation_rate), tau_min)

        # Deposit: every ant contributes Q / scalar to the slots it visited
        for ind in population:
            scalar = float(ind.fitness)
            deposit = q / (scalar + 1e-9)
            for j, fid in enumerate(ind.candidate):
                tau[j][fid] += deposit

            # Update global best
            if scalar < _best["scalar"]:
                _best["scalar"] = scalar
                _best["candidate"] = list(ind.candidate)
                _best["f"] = fitness_vector(
                    ind.candidate, state.foods, ctarget=ctarget
                )

        best_this_gen = min(float(ind.fitness) for ind in population)
        trace["generation"].append(float(num_generations))
        trace["best_scalar"].append(float(best_this_gen))

    # ------------------------------------------------------------------
    # Run via inspyred EC (provides seeding, termination, observer hook)
    # ------------------------------------------------------------------
    ec = EvolutionaryComputation(rng)
    ec.selector = selectors.truncation_selection
    ec.variator = [variator]
    ec.replacer = replacers.generational_replacement
    ec.terminator = terminators.generation_termination
    ec.observer = observer

    ec.evolve(
        generator=generator,
        evaluator=evaluator,
        pop_size=pop_size,
        maximize=False,
        max_generations=max_generations,
        num_selected=pop_size,
    )

    # Return global best (elitist) rather than arbitrary final-population best.
    if _best["candidate"] is None:
        _best["f"] = (0.0, 0.0)
    best_f = tuple(map(float, _best["f"]))

    return {
        "front": [best_f],
        "best_candidate": _best["candidate"],
        "best_f": best_f,
        "trace": trace,
        "representation": representation.name,
        "constraint_handler": "none",
    }
