"""Discrete integer encoding utilities for weekly diet plans.

Encoding model:
- Individual length L = 77 (7 days * 11 genes/day)
- Each gene is an integer index pointing to an item in `comida_bd`
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Sequence


DAYS = 7
GENES_PER_DAY = 11
INDIVIDUAL_LENGTH = DAYS * GENES_PER_DAY

DAILY_GENE_NAMES = (
    "gsnack1",
    "gdrinkB",
    "gfoodB1",
    "gfoodB2",
    "gdrinkL",
    "gfoodL1",
    "gfoodL2",
    "gsnack2",
    "gdrinkD",
    "gfoodD1",
    "gfoodD2",
)


@dataclass(frozen=True)
class GeneDomains:
    snacks: List[int]
    breakfast_drinks: List[int]
    breakfast_foods: List[int]
    lunch_dinner_drinks: List[int]
    lunch_dinner_foods: List[int]


def _indices_by_prefix(comida_bd: Sequence[dict], prefixes: Sequence[str]) -> List[int]:
    return [
        i
        for i, item in enumerate(comida_bd)
        if any((item.get("grupo") or "").startswith(p) for p in prefixes)
    ]


def build_gene_domains(comida_bd: Sequence[dict], edad: int) -> GeneDomains:
    """Build valid gene domains using the project meal constraints."""
    snacks = _indices_by_prefix(comida_bd, ("F", "S"))

    breakfast_drinks = _indices_by_prefix(comida_bd, ("BA", "BH", "PA", "FE", "FC"))
    breakfast_foods = _indices_by_prefix(comida_bd, ("A", "C", "FA", "MAA"))
    breakfast_foods = [i for i in breakfast_foods if (comida_bd[i].get("grupo") or "") not in {"AC", "AD", "AE"}]

    lunch_dinner_drinks = _indices_by_prefix(comida_bd, ("P", "FC", "FE"))
    lunch_dinner_drinks = [i for i in lunch_dinner_drinks if not (comida_bd[i].get("grupo") or "").startswith("PA")]
    if edad >= 18:
        lunch_dinner_drinks.extend(_indices_by_prefix(comida_bd, ("Q",)))
    lunch_dinner_drinks = sorted(set(lunch_dinner_drinks))

    excluded_prefixes = ("FC", "FE", "P", "Q", "BA", "BH", "PA", "S", "A")
    allowed_a_groups = {"AC", "AD", "AE", "AF"}
    lunch_dinner_foods = []
    for i, item in enumerate(comida_bd):
        group = item.get("grupo") or ""
        if not group.startswith(excluded_prefixes) or group in allowed_a_groups:
            lunch_dinner_foods.append(i)

    return GeneDomains(
        snacks=snacks,
        breakfast_drinks=breakfast_drinks,
        breakfast_foods=breakfast_foods,
        lunch_dinner_drinks=lunch_dinner_drinks,
        lunch_dinner_foods=lunch_dinner_foods,
    )


def _pick(domain: Sequence[int], rng: random.Random) -> int:
    if not domain:
        raise ValueError("Empty domain found while sampling genes.")
    return domain[rng.randrange(len(domain))]


def create_random_individual(
    comida_bd: Sequence[dict],
    edad: int,
    rng: random.Random | None = None,
    unique_pairs: bool = True,
) -> List[int]:
    """Create one random valid individual (length 77)."""
    rng = rng or random.Random()
    d = build_gene_domains(comida_bd, edad)

    individual: List[int] = []
    for _ in range(DAYS):
        gsnack1 = _pick(d.snacks, rng)
        gdrinkB = _pick(d.breakfast_drinks, rng)
        gfoodB1 = _pick(d.breakfast_foods, rng)
        gfoodB2 = _pick([x for x in d.breakfast_foods if not unique_pairs or x != gfoodB1] or d.breakfast_foods, rng)
        gdrinkL = _pick(d.lunch_dinner_drinks, rng)
        gfoodL1 = _pick(d.lunch_dinner_foods, rng)
        gfoodL2 = _pick([x for x in d.lunch_dinner_foods if not unique_pairs or x != gfoodL1] or d.lunch_dinner_foods, rng)
        gsnack2 = _pick(d.snacks, rng)
        gdrinkD = _pick(d.lunch_dinner_drinks, rng)
        gfoodD1 = _pick(d.lunch_dinner_foods, rng)
        gfoodD2 = _pick([x for x in d.lunch_dinner_foods if not unique_pairs or x != gfoodD1] or d.lunch_dinner_foods, rng)

        individual.extend(
            [
                gsnack1,
                gdrinkB,
                gfoodB1,
                gfoodB2,
                gdrinkL,
                gfoodL1,
                gfoodL2,
                gsnack2,
                gdrinkD,
                gfoodD1,
                gfoodD2,
            ]
        )

    return individual


def split_daily_blocks(individual: Sequence[int]) -> Dict[str, Dict[str, int]]:
    """Return the vector as D1..D7 blocks with named genes."""
    if len(individual) != INDIVIDUAL_LENGTH:
        raise ValueError(f"Expected length {INDIVIDUAL_LENGTH}, got {len(individual)}")

    blocks: Dict[str, Dict[str, int]] = {}
    for day in range(DAYS):
        start = day * GENES_PER_DAY
        day_values = individual[start : start + GENES_PER_DAY]
        blocks[f"D{day + 1}"] = dict(zip(DAILY_GENE_NAMES, day_values))
    return blocks


def validate_individual(individual: Sequence[int], comida_bd: Sequence[dict], edad: int) -> List[str]:
    """Return a list of constraint violations. Empty list means valid."""
    errors: List[str] = []
    if len(individual) != INDIVIDUAL_LENGTH:
        errors.append(f"Invalid length: {len(individual)} != {INDIVIDUAL_LENGTH}")
        return errors

    d = build_gene_domains(comida_bd, edad)
    domains = (
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
    )

    for day in range(DAYS):
        start = day * GENES_PER_DAY
        day_genes = individual[start : start + GENES_PER_DAY]
        for gene_name, value, domain in zip(DAILY_GENE_NAMES, day_genes, domains):
            if value not in domain:
                errors.append(f"D{day + 1}.{gene_name} -> index {value} outside domain")
    return errors
