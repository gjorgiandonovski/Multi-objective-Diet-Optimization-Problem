from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Sequence

DAYS = 7
GENES_PER_DAY = 11
INDIVIDUAL_LENGTH = DAYS * GENES_PER_DAY


@dataclass(frozen=True)
class Domains:
    snacks: list[int]
    breakfast_drinks: list[int]
    breakfast_foods: list[int]
    lunch_dinner_drinks: list[int]
    lunch_dinner_foods: list[int]


def _indices(foods: Sequence[dict], prefixes: Sequence[str]) -> list[int]:
    return [
        i
        for i, item in enumerate(foods)
        if any((item.get("grupo") or "").startswith(p) for p in prefixes)
    ]


def build_domains(foods: Sequence[dict], edad: int) -> Domains:
    snacks = _indices(foods, ("F", "S"))
    breakfast_drinks = _indices(foods, ("BA", "BH", "PA", "FE", "FC"))
    breakfast_foods = _indices(foods, ("A", "C", "FA", "MAA"))
    breakfast_foods = [i for i in breakfast_foods if (foods[i].get("grupo") or "") not in {"AC", "AD", "AE"}]

    lunch_dinner_drinks = _indices(foods, ("P", "FC", "FE"))
    lunch_dinner_drinks = [i for i in lunch_dinner_drinks if not (foods[i].get("grupo") or "").startswith("PA")]
    if edad >= 18:
        lunch_dinner_drinks.extend(_indices(foods, ("Q",)))
    lunch_dinner_drinks = sorted(set(lunch_dinner_drinks))

    excluded = ("FC", "FE", "P", "Q", "BA", "BH", "PA", "S", "A")
    allow_a = {"AC", "AD", "AE", "AF"}
    lunch_dinner_foods = []
    for i, item in enumerate(foods):
        group = item.get("grupo") or ""
        if not group.startswith(excluded) or group in allow_a:
            lunch_dinner_foods.append(i)

    return Domains(
        snacks=snacks,
        breakfast_drinks=breakfast_drinks,
        breakfast_foods=breakfast_foods,
        lunch_dinner_drinks=lunch_dinner_drinks,
        lunch_dinner_foods=lunch_dinner_foods,
    )


def _pick(domain: list[int], rng: random.Random) -> int:
    if not domain:
        raise ValueError("Empty domain")
    return domain[rng.randrange(len(domain))]


def create_individual(foods: Sequence[dict], edad: int, rng: random.Random | None = None) -> list[int]:
    rng = rng or random.Random()
    d = build_domains(foods, edad)
    genes: list[int] = []

    for _ in range(DAYS):
        b1 = _pick(d.breakfast_foods, rng)
        l1 = _pick(d.lunch_dinner_foods, rng)
        d1 = _pick(d.lunch_dinner_foods, rng)

        genes.extend(
            [
                _pick(d.snacks, rng),
                _pick(d.breakfast_drinks, rng),
                b1,
                _pick([x for x in d.breakfast_foods if x != b1] or d.breakfast_foods, rng),
                _pick(d.lunch_dinner_drinks, rng),
                l1,
                _pick([x for x in d.lunch_dinner_foods if x != l1] or d.lunch_dinner_foods, rng),
                _pick(d.snacks, rng),
                _pick(d.lunch_dinner_drinks, rng),
                d1,
                _pick([x for x in d.lunch_dinner_foods if x != d1] or d.lunch_dinner_foods, rng),
            ]
        )

    return genes
