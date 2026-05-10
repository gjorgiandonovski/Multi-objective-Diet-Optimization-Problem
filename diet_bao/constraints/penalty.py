"""Penalty handler: add a per-violation penalty to each objective.

Per-violation penalties are large enough to dominate small fitness differences
without overwhelming candidates that are close to feasibility:

- f1 penalty: 1000 kcal per violation
- f2 penalty: 10 % per violation
"""
from __future__ import annotations

import random as _random

from diet_bao.constraints.base import count_violations
from diet_bao.representations.base import EncodingState


class PenaltyHandler:
    name = "penalty"

    def __init__(self, f1_per_violation: float = 1000.0, f2_per_violation: float = 10.0) -> None:
        self.f1_per_violation = float(f1_per_violation)
        self.f2_per_violation = float(f2_per_violation)

    def process(
        self,
        candidate_indices: list[int],
        state: EncodingState,
        ctarget: float,
        raw_fitness: tuple[float, float],
        random: _random.Random,
    ) -> tuple[list[int], tuple[float, float]]:
        violations = count_violations(candidate_indices, state)
        if violations == 0:
            return candidate_indices, raw_fitness
        f1, f2 = raw_fitness
        return candidate_indices, (
            float(f1 + violations * self.f1_per_violation),
            float(f2 + violations * self.f2_per_violation),
        )
