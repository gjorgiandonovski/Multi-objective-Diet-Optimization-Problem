import random

from utils.encoding import create_random_individual
from utils.fitness import fitness_vector

from tests.test_encoding import _sample_foods


def test_fitness_vector_returns_two_nonnegative_values():
    foods = _sample_foods()
    rng = random.Random(1)
    ind = create_random_individual(foods, edad=25, rng=rng)

    f1, f2 = fitness_vector(ind, foods, ctarget=2000.0)
    assert isinstance(f1, float)
    assert isinstance(f2, float)
    assert f1 >= 0.0
    assert f2 >= 0.0
