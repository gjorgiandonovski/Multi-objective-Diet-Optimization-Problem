"""Multi-objective fitness for the diet optimisation problem.

Two objectives, both minimised:
- f1: total daily-calorie deviation across the 7-day plan
- f2: total daily-macro-percentage deviation across the 7-day plan

Both are computed PER DAY and summed, matching the assignment wording
("Adjust DAILY calories...", "Adjust DAILY carbohydrates so their percentage
is 55%...").

The legacy week-aggregate macro fitness is preserved as fitness_vector_weekly
for reproducibility against earlier experiment outputs.
"""
from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Sequence

from diet_bao.encoding import DAYS, GENES_PER_DAY, INDIVIDUAL_LENGTH

if TYPE_CHECKING:
    from diet_bao.representations.base import EncodingState

try:
    from inspyred.ec.emo import Pareto
except Exception:  # pragma: no cover
    Pareto = None  # type: ignore

CARB_TARGET = 55.0
FAT_TARGET = 27.5
PROTEIN_TARGET = 22.5

# Worst-case macro deviation per day, used when a day has zero kcal of macros.
_WORST_DAILY_MACRO_DEV = abs(CARB_TARGET) + abs(FAT_TARGET) + abs(PROTEIN_TARGET)


def _daily_totals(individual: Sequence[int], foods: Sequence[dict]) -> list[dict[str, float]]:
    if len(individual) != INDIVIDUAL_LENGTH:
        raise ValueError("Invalid individual length")

    totals: list[dict[str, float]] = []
    for day in range(DAYS):
        block = individual[day * GENES_PER_DAY : (day + 1) * GENES_PER_DAY]
        acc = {"calorias": 0.0, "proteinas": 0.0, "carbohidratos": 0.0, "grasas": 0.0}
        for idx in block:
            row = foods[int(idx)]
            acc["calorias"] += float(row["calorias"])
            acc["proteinas"] += float(row["proteinas"])
            acc["carbohidratos"] += float(row["carbohidratos"])
            acc["grasas"] += float(row["grasas"])
        totals.append(acc)
    return totals


def _macro_deviation_for_day(day: dict[str, float]) -> float:
    """L1 deviation between actual and target macro percentages for one day."""
    kcal_pro = day["proteinas"] * 4.0
    kcal_carb = day["carbohidratos"] * 4.0
    kcal_fat = day["grasas"] * 9.0
    total = kcal_pro + kcal_carb + kcal_fat

    if total <= 0:
        return _WORST_DAILY_MACRO_DEV

    pct_carb = 100.0 * (kcal_carb / total)
    pct_fat = 100.0 * (kcal_fat / total)
    pct_pro = 100.0 * (kcal_pro / total)
    return (
        abs(pct_carb - CARB_TARGET)
        + abs(pct_fat - FAT_TARGET)
        + abs(pct_pro - PROTEIN_TARGET)
    )


def fitness_vector(
    individual: Sequence[int],
    foods: Sequence[dict],
    ctarget: float,
) -> tuple[float, float]:
    """Per-day fitness, matching the assignment specification.

    f1 = sum over days of |day_kcal - target_kcal|
    f2 = sum over days of (|carb%-55| + |fat%-27.5| + |pro%-22.5|)
    """
    daily = _daily_totals(individual, foods)
    f1 = sum(abs(day["calorias"] - float(ctarget)) for day in daily)
    f2 = sum(_macro_deviation_for_day(day) for day in daily)
    return float(f1), float(f2)


def fitness_vector_from_arrays(
    individual: Sequence[int],
    calories: Sequence[float],
    proteins: Sequence[float],
    carbs: Sequence[float],
    fats: Sequence[float],
    ctarget: float,
) -> tuple[float, float]:
    """Fast per-day fitness using precomputed nutrient arrays.

    This avoids repeated dict lookups in the inner evolutionary loop while
    preserving the public ``fitness_vector`` behaviour.
    """
    if len(individual) != INDIVIDUAL_LENGTH:
        raise ValueError("Invalid individual length")

    target = float(ctarget)
    f1 = 0.0
    f2 = 0.0

    for start in range(0, INDIVIDUAL_LENGTH, GENES_PER_DAY):
        kcal = 0.0
        pro = 0.0
        carb = 0.0
        fat = 0.0

        for pos in range(start, start + GENES_PER_DAY):
            idx = int(individual[pos])
            kcal += calories[idx]
            pro += proteins[idx]
            carb += carbs[idx]
            fat += fats[idx]

        f1 += abs(kcal - target)

        kcal_pro = pro * 4.0
        kcal_carb = carb * 4.0
        kcal_fat = fat * 9.0
        total = kcal_pro + kcal_carb + kcal_fat
        if total <= 0:
            f2 += _WORST_DAILY_MACRO_DEV
        else:
            pct_carb = 100.0 * (kcal_carb / total)
            pct_fat = 100.0 * (kcal_fat / total)
            pct_pro = 100.0 * (kcal_pro / total)
            f2 += (
                abs(pct_carb - CARB_TARGET)
                + abs(pct_fat - FAT_TARGET)
                + abs(pct_pro - PROTEIN_TARGET)
            )

    return float(f1), float(f2)


def fitness_vector_state(
    individual: Sequence[int],
    state: "EncodingState",
    ctarget: float,
) -> tuple[float, float]:
    return fitness_vector_from_arrays(
        individual,
        state.calories,
        state.proteins,
        state.carbs,
        state.fats,
        ctarget,
    )


def fitness_vector_weekly(
    individual: Sequence[int],
    foods: Sequence[dict],
    ctarget: float,
) -> tuple[float, float]:
    """Legacy fitness: macro deviation computed once over the week-aggregate."""
    daily = _daily_totals(individual, foods)
    f1 = sum(abs(day["calorias"] - float(ctarget)) for day in daily)

    week_pro = sum(day["proteinas"] for day in daily)
    week_carb = sum(day["carbohidratos"] for day in daily)
    week_fat = sum(day["grasas"] for day in daily)

    kcal_pro = week_pro * 4.0
    kcal_carb = week_carb * 4.0
    kcal_fat = week_fat * 9.0
    total = kcal_pro + kcal_carb + kcal_fat

    if total <= 0:
        f2 = _WORST_DAILY_MACRO_DEV
    else:
        pct_carb = 100.0 * (kcal_carb / total)
        pct_fat = 100.0 * (kcal_fat / total)
        pct_pro = 100.0 * (kcal_pro / total)
        f2 = (
            abs(pct_carb - CARB_TARGET)
            + abs(pct_fat - FAT_TARGET)
            + abs(pct_pro - PROTEIN_TARGET)
        )

    return float(f1), float(f2)


def evaluate_candidates(candidates: Sequence[Sequence[int]], args: dict):
    """inspyred-compatible evaluator returning Pareto fitness objects."""
    foods = args["foods"]
    ctarget = float(args["ctarget"])
    fitness_fn = args.get("fitness_fn", fitness_vector)
    out = []
    for candidate in candidates:
        f1, f2 = fitness_fn(candidate, foods, ctarget)
        out.append(Pareto([f1, f2]) if Pareto is not None else (f1, f2))
    return out
