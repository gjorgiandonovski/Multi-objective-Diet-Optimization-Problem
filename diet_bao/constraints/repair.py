"""Repair handler: replace any infeasible gene with a random valid one."""
from __future__ import annotations

import random as _random

from diet_bao.fitness import fitness_vector
from diet_bao.representations.base import EncodingState


class RepairHandler:
    name = "repair"

    def process(
        self,
        candidate_indices: list[int],
        state: EncodingState,
        ctarget: float,
        raw_fitness: tuple[float, float],
        random: _random.Random,
    ) -> tuple[list[int], tuple[float, float]]:
        repaired = list(candidate_indices)
        changed = False
        for i, domain in enumerate(state.per_position):
            if int(repaired[i]) not in domain:
                repaired[i] = domain[random.randrange(len(domain))]
                changed = True
        if not changed:
            return repaired, raw_fitness
        # Re-evaluate after repair so the algorithm sees the corrected fitness.
        f1, f2 = fitness_vector(repaired, state.foods, ctarget=ctarget)
        return repaired, (float(f1), float(f2))
