"""Base interface for diet representations."""
from __future__ import annotations

import random as _random
from dataclasses import dataclass
from typing import Protocol, Sequence

from diet_bao.encoding import DAYS, GENES_PER_DAY, build_domains


@dataclass(frozen=True)
class EncodingState:
    """Per-position list of valid food indices for a given (foods, edad)."""

    per_position: list[list[int]]
    foods: list[dict]
    edad: int

    @property
    def length(self) -> int:
        return len(self.per_position)


def build_state(foods: Sequence[dict], edad: int) -> EncodingState:
    """Compute the per-position valid-domain mapping for a (foods, edad) pair."""
    d = build_domains(foods, edad)
    per_day = [
        d.snacks,
        d.breakfast_drinks,
        d.breakfast_foods,
        d.breakfast_foods,
        d.lunch_dinner_drinks,
        d.lunch_dinner_foods,
        d.lunch_dinner_foods,
        d.snacks,
        d.lunch_dinner_drinks,
        d.lunch_dinner_foods,
        d.lunch_dinner_foods,
    ]
    per_position: list[list[int]] = []
    for _ in range(DAYS):
        per_position.extend([list(slot) for slot in per_day])
    if len(per_position) != DAYS * GENES_PER_DAY:
        raise RuntimeError("Internal domain mapping error")
    return EncodingState(per_position=per_position, foods=list(foods), edad=int(edad))


class Representation(Protocol):
    """Pluggable encoding strategy.

    Implementations expose a uniform set of operations so that algorithms can
    work with any representation without modification.
    """

    name: str

    def build(self, foods: Sequence[dict], edad: int) -> EncodingState:
        ...

    def generate(self, state: EncodingState, random: _random.Random) -> list:
        """Produce a fresh raw candidate."""
        ...

    def decode(self, state: EncodingState, candidate) -> list[int]:
        """Decode a raw candidate into food indices for fitness evaluation."""
        ...

    def repair(self, state: EncodingState, candidate, random: _random.Random):
        """Return a feasibility-restored copy of `candidate`."""
        ...
