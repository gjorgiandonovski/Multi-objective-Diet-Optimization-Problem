"""Death-penalty handler: any infeasible candidate is set to +infinity fitness."""
from __future__ import annotations

import math
import random as _random

from diet_bao.constraints.base import count_violations
from diet_bao.representations.base import EncodingState


class DeathPenaltyHandler:
    name = "death_penalty"

    def process(
        self,
        candidate_indices: list[int],
        state: EncodingState,
        ctarget: float,
        raw_fitness: tuple[float, float],
        random: _random.Random,
    ) -> tuple[list[int], tuple[float, float]]:
        if count_violations(candidate_indices, state) == 0:
            return candidate_indices, raw_fitness
        return candidate_indices, (math.inf, math.inf)
