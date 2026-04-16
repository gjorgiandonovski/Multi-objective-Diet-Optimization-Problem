"""Multi-objective fitness functions for weekly diet plans.

Objectives (to minimize):
1) f1: Caloric accuracy = sum of absolute daily deviations from target calories
2) f2: Macronutrient adjustment = absolute deviation from the target macro split
   across the whole weekly solution

Designed for use with `inspyred`.
"""

from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

from src.utilidades.encoding import DAYS, GENES_PER_DAY, INDIVIDUAL_LENGTH

try:
    from inspyred.ec.emo import Pareto
except Exception:  # pragma: no cover
    Pareto = None  # type: ignore


CARB_TARGET_PCT = 55.0
FAT_TARGET_PCT = 27.5
PROTEIN_TARGET_PCT = 22.5


def _daily_totals(individual: Sequence[int], comida_bd: Sequence[dict]) -> List[Dict[str, float]]:
    if len(individual) != INDIVIDUAL_LENGTH:
        raise ValueError(f"Expected individual length {INDIVIDUAL_LENGTH}, got {len(individual)}")

    totals: List[Dict[str, float]] = []
    for day in range(DAYS):
        start = day * GENES_PER_DAY
        genes = individual[start : start + GENES_PER_DAY]

        cal = pro = carb = fat = 0.0
        for idx in genes:
            item = comida_bd[int(idx)]
            cal += float(item["calorias"])
            pro += float(item["proteinas"])
            carb += float(item["carbohidratos"])
            fat += float(item["grasas"])

        totals.append({"calorias": cal, "proteinas": pro, "carbohidratos": carb, "grasas": fat})
    return totals


def _weekly_totals(individual: Sequence[int], comida_bd: Sequence[dict]) -> Dict[str, float]:
    daily_totals = _daily_totals(individual, comida_bd)
    return {
        "calorias": sum(day["calorias"] for day in daily_totals),
        "proteinas": sum(day["proteinas"] for day in daily_totals),
        "carbohidratos": sum(day["carbohidratos"] for day in daily_totals),
        "grasas": sum(day["grasas"] for day in daily_totals),
    }


def caloric_accuracy_f1(individual: Sequence[int], comida_bd: Sequence[dict], ctarget: float) -> float:
    """Minimize total absolute deviation from daily target calories."""
    totals = _daily_totals(individual, comida_bd)
    return sum(abs(day["calorias"] - float(ctarget)) for day in totals)


def macronutrient_adjustment_f2(
    individual: Sequence[int],
    comida_bd: Sequence[dict],
    carb_target_pct: float = CARB_TARGET_PCT,
    fat_target_pct: float = FAT_TARGET_PCT,
    protein_target_pct: float = PROTEIN_TARGET_PCT,
) -> float:
    """Minimize weekly macro percentage deviation from the target distribution."""
    totals = _weekly_totals(individual, comida_bd)

    cal_pro = totals["proteinas"] * 4.0
    cal_carb = totals["carbohidratos"] * 4.0
    cal_fat = totals["grasas"] * 9.0
    macro_cal_total = cal_pro + cal_carb + cal_fat

    if macro_cal_total <= 0:
        # Maximal penalty for an impossible/no-nutrient solution.
        return abs(carb_target_pct) + abs(fat_target_pct) + abs(protein_target_pct)

    carb_pct = (cal_carb / macro_cal_total) * 100.0
    fat_pct = (cal_fat / macro_cal_total) * 100.0
    protein_pct = (cal_pro / macro_cal_total) * 100.0

    return (
        abs(carb_pct - carb_target_pct)
        + abs(fat_pct - fat_target_pct)
        + abs(protein_pct - protein_target_pct)
    )


def fitness_vector(individual: Sequence[int], comida_bd: Sequence[dict], ctarget: float) -> Tuple[float, float]:
    """Return (f1, f2) for one candidate."""
    f1 = caloric_accuracy_f1(individual, comida_bd, ctarget)
    f2 = macronutrient_adjustment_f2(individual, comida_bd)
    return f1, f2


def evaluate_candidates(candidates: Sequence[Sequence[int]], args: dict):
    """inspyred evaluator: returns list of Pareto fitness values.

    Required args:
    - `comida_bd`: list of foods from DB
    - `ctarget`: target daily calories for the selected user
    """
    comida_bd = args["comida_bd"]
    ctarget = args["ctarget"]

    out = []
    for candidate in candidates:
        f1, f2 = fitness_vector(candidate, comida_bd, ctarget)
        if Pareto is not None:
            out.append(Pareto([f1, f2]))
        else:
            out.append((f1, f2))
    return out
