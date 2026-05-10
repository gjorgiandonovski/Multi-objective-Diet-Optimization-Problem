"""Random-key representation: each gene is a real number in [0, 1].

Decoding maps each key to an index in the per-position domain by quantizing the
key into one of N equal-width bins, where N is the size of the position's domain.
This gives a continuous search landscape that PSO and other continuous-state
algorithms can navigate, while still respecting the discrete domain structure
when decoded for fitness evaluation.

Repair clamps each gene into [0, 1].
"""
from __future__ import annotations

import random as _random
from typing import Sequence

from diet_bao.representations.base import EncodingState, build_state


class RandomKeyRepresentation:
    name = "random_key"

    def build(self, foods: Sequence[dict], edad: int) -> EncodingState:
        return build_state(foods, edad)

    def generate(self, state: EncodingState, random: _random.Random) -> list[float]:
        return [random.random() for _ in range(state.length)]

    def decode(self, state: EncodingState, candidate) -> list[int]:
        out: list[int] = []
        for x, domain in zip(candidate, state.per_position):
            v = 0.0 if x < 0.0 else 1.0 if x > 1.0 else float(x)
            if not domain:
                raise ValueError("Empty domain at a position")
            if len(domain) == 1:
                out.append(domain[0])
                continue
            # Equal-width bin assignment, with the top edge rounded into the last bin.
            idx = int(v * len(domain))
            if idx >= len(domain):
                idx = len(domain) - 1
            out.append(domain[idx])
        return out

    def repair(self, state: EncodingState, candidate, random: _random.Random) -> list[float]:
        out: list[float] = []
        for x in candidate:
            v = float(x)
            if v < 0.0:
                v = 0.0
            elif v > 1.0:
                v = 1.0
            out.append(v)
        return out
