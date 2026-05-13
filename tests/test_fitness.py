import random

import pytest

from diet_bao.encoding import DAYS, GENES_PER_DAY, INDIVIDUAL_LENGTH, create_individual
from diet_bao.fitness import (
    CARB_TARGET,
    FAT_TARGET,
    PROTEIN_TARGET,
    fitness_vector,
    fitness_vector_weekly,
)

from tests.test_encoding import _foods


def test_fitness_vector_returns_nonnegative_pair():
    foods = _foods()
    candidate = create_individual(foods, edad=25, rng=random.Random(1))
    f1, f2 = fitness_vector(candidate, foods, ctarget=2000.0)
    assert isinstance(f1, float)
    assert isinstance(f2, float)
    assert f1 >= 0.0
    assert f2 >= 0.0


def test_fitness_vector_weekly_returns_nonnegative_pair():
    foods = _foods()
    candidate = create_individual(foods, edad=25, rng=random.Random(1))
    f1, f2 = fitness_vector_weekly(candidate, foods, ctarget=2000.0)
    assert f1 >= 0.0
    assert f2 >= 0.0


def test_proportional_macro_split_can_hit_zero_deviation():
    """The corrected assignment macro targets sum to 100%, so f2 can reach 0."""
    pro_g = PROTEIN_TARGET / 4.0
    carb_g = CARB_TARGET / 4.0
    fat_g = FAT_TARGET / 9.0
    proportional = {
        "nombre": "Proportional",
        "grupo": "M1",
        "calorias": 100.0,
        "proteinas": pro_g,
        "carbohidratos": carb_g,
        "grasas": fat_g,
    }
    foods = [proportional] * INDIVIDUAL_LENGTH
    individual = list(range(INDIVIDUAL_LENGTH))
    f1, f2 = fitness_vector(individual, foods, ctarget=11 * 100.0)
    assert f1 == pytest.approx(0.0, abs=1e-6)
    assert f2 == pytest.approx(0.0, abs=1e-6)


def test_per_day_fitness_differs_from_weekly_when_imbalanced():
    """Plans balanced on the weekly aggregate but imbalanced per day score worse on per-day fitness."""
    carb_only = {"nombre": "Sugar", "grupo": "S1", "calorias": 100.0, "proteinas": 0.0, "carbohidratos": 25.0, "grasas": 0.0}
    fat_only = {"nombre": "Lard", "grupo": "M1", "calorias": 100.0, "proteinas": 0.0, "carbohidratos": 0.0, "grasas": 11.1}
    foods = [carb_only, fat_only]
    individual = []
    for day in range(DAYS):
        food_idx = 0 if day % 2 == 0 else 1
        individual.extend([food_idx] * GENES_PER_DAY)

    f1_perday, f2_perday = fitness_vector(individual, foods, ctarget=1100.0)
    f1_week, f2_week = fitness_vector_weekly(individual, foods, ctarget=1100.0)

    assert f1_perday == pytest.approx(f1_week)
    assert f2_perday != pytest.approx(f2_week)
