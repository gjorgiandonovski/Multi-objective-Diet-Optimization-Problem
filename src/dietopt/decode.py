from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from utils.encoding import DAYS, GENES_PER_DAY, GeneDomains, build_gene_domains


@dataclass(frozen=True)
class PositionDomains:
    per_position: List[List[int]]


def build_position_domains(comida_bd: Sequence[dict], edad: int) -> PositionDomains:
    d: GeneDomains = build_gene_domains(comida_bd, edad)

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

    per_position: List[List[int]] = []
    for _ in range(DAYS):
        per_position.extend([list(x) for x in per_day])

    if len(per_position) != DAYS * GENES_PER_DAY:
        raise RuntimeError("Internal error building position domains")

    return PositionDomains(per_position=per_position)


def decode_continuous(candidate: Sequence[float], domains: PositionDomains) -> List[int]:
    """Map a [0,1] float vector to a valid discrete meal-plan individual."""
    if len(candidate) != len(domains.per_position):
        raise ValueError("Candidate length mismatch")

    out: List[int] = []
    for x, domain in zip(candidate, domains.per_position):
        if not domain:
            raise ValueError("Empty domain")
        # Clamp into [0, 1] then map.
        x = 0.0 if x < 0.0 else 1.0 if x > 1.0 else float(x)
        idx = int(x * (len(domain) - 1)) if len(domain) > 1 else 0
        out.append(domain[idx])
    return out
