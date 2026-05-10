"""Direct-index representation: each gene is an integer food id."""
from __future__ import annotations

import random as _random
from typing import Sequence

from diet_bao.representations.base import EncodingState, build_state


class DirectIndexRepresentation:
    name = "direct_index"

    def build(self, foods: Sequence[dict], edad: int) -> EncodingState:
        return build_state(foods, edad)

    def generate(self, state: EncodingState, random: _random.Random) -> list[int]:
        return [domain[random.randrange(len(domain))] for domain in state.per_position]

    def decode(self, state: EncodingState, candidate) -> list[int]:
        # Direct: candidate IS the list of indices.
        return [int(g) for g in candidate]

    def repair(self, state: EncodingState, candidate, random: _random.Random) -> list[int]:
        out = list(candidate)
        for i, domain in enumerate(state.per_position):
            if out[i] not in domain:
                out[i] = domain[random.randrange(len(domain))]
        return out
