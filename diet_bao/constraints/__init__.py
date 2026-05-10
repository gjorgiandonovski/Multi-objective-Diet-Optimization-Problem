"""Constraint handling techniques for the diet optimisation problem.

The problem has structural constraints: each gene position must hold a food
of a specific type. Random crossover/mutation can violate this. Three classical
techniques are compared:

- repair: replace any infeasible gene with a random feasible one before fitness.
- penalty: leave the candidate as-is; add a per-violation penalty to each
  objective.
- death_penalty: leave the candidate as-is; assign +infinity fitness to any
  candidate with at least one violation.

All handlers expose process(candidate, state, ctarget, raw_fitness, random)
returning (decoded_indices, adjusted_fitness) so the algorithm body does not
need to care which technique is in use.
"""

from diet_bao.constraints.base import ConstraintHandler
from diet_bao.constraints.death_penalty import DeathPenaltyHandler
from diet_bao.constraints.penalty import PenaltyHandler
from diet_bao.constraints.repair import RepairHandler

REPAIR = RepairHandler()
PENALTY = PenaltyHandler()
DEATH_PENALTY = DeathPenaltyHandler()

ALL_HANDLERS: dict[str, ConstraintHandler] = {
    REPAIR.name: REPAIR,
    PENALTY.name: PENALTY,
    DEATH_PENALTY.name: DEATH_PENALTY,
}

__all__ = [
    "ConstraintHandler",
    "RepairHandler",
    "PenaltyHandler",
    "DeathPenaltyHandler",
    "REPAIR",
    "PENALTY",
    "DEATH_PENALTY",
    "ALL_HANDLERS",
]
