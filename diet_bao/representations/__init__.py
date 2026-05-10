"""Pluggable representations for the diet optimisation problem.

Two encodings live behind a uniform interface so the same algorithm can compare
both with no code changes:

- direct_index: each gene is the integer index of a chosen food. Native discrete
  encoding; requires per-position domain enforcement.
- random_key: each gene is a real number in [0, 1] decoded by ranking-based
  mapping to a food index from the per-position domain.

Both expose:
    .name -> str
    .build(foods, edad) -> Encoding state object
    .generate(state, random) -> raw candidate
    .decode(state, candidate) -> list[int] of food indices (the canonical form
        consumed by fitness)
    .repair(state, candidate, random) -> raw candidate (in-place safe), restoring
        feasibility with respect to the per-position domains.

Fitness operates on the decoded form. Algorithm operators operate on the raw form.
"""

from diet_bao.representations.base import EncodingState, Representation
from diet_bao.representations.direct_index import DirectIndexRepresentation
from diet_bao.representations.random_key import RandomKeyRepresentation

DIRECT_INDEX = DirectIndexRepresentation()
RANDOM_KEY = RandomKeyRepresentation()

ALL_REPRESENTATIONS: dict[str, Representation] = {
    DIRECT_INDEX.name: DIRECT_INDEX,
    RANDOM_KEY.name: RANDOM_KEY,
}

__all__ = [
    "EncodingState",
    "Representation",
    "DirectIndexRepresentation",
    "RandomKeyRepresentation",
    "DIRECT_INDEX",
    "RANDOM_KEY",
    "ALL_REPRESENTATIONS",
]
