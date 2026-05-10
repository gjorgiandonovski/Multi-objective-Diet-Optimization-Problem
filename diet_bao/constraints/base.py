"""Base interface for constraint handling strategies."""
from __future__ import annotations

import random as _random
from typing import Protocol, Sequence

from diet_bao.representations.base import EncodingState


def count_violations(candidate_indices: Sequence[int], state: EncodingState) -> int:
    """Number of gene positions whose decoded index is NOT in the position's domain."""
    bad = 0
    for gene, domain in zip(candidate_indices, state.per_position):
        if int(gene) not in domain:
            bad += 1
    return bad


class ConstraintHandler(Protocol):
    """Pluggable constraint-handling strategy.

    Each handler decides how to combine an evaluated candidate with the
    feasibility check.
    """

    name: str

    def process(
        self,
        candidate_indices: list[int],
        state: EncodingState,
        ctarget: float,
        raw_fitness: tuple[float, float],
        random: _random.Random,
    ) -> tuple[list[int], tuple[float, float]]:
        """Return a (possibly-modified) candidate and (possibly-modified) fitness."""
        ...
