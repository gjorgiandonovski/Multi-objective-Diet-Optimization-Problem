"""End-to-end smoke tests for every (algorithm, representation, constraint) combo
that's supposed to be supported. Uses a tiny synthetic food list and small
pop/gen counts so they run in seconds.
"""
import pytest

from diet_bao.constraints import DEATH_PENALTY, PENALTY, REPAIR
from diet_bao.representations import DIRECT_INDEX, RANDOM_KEY


def _foods():
    catalog = []
    for i in range(10):
        catalog.append({"nombre": f"Snack{i}", "grupo": "F", "calorias": 80.0 + i, "proteinas": 1.0, "carbohidratos": 18.0, "grasas": 0.5})
    for i in range(10):
        catalog.append({"nombre": f"BD{i}", "grupo": "BA" if i % 2 == 0 else "BH", "calorias": 60.0 + i, "proteinas": 3.0, "carbohidratos": 5.0, "grasas": 3.0})
    for i in range(10):
        catalog.append({"nombre": f"BF{i}", "grupo": "FA" if i % 2 == 0 else "C", "calorias": 110.0 + i, "proteinas": 6.0, "carbohidratos": 22.0, "grasas": 5.0})
    for i in range(10):
        catalog.append({"nombre": f"LD{i}", "grupo": "P" if i % 2 == 0 else "FC", "calorias": 30.0 + i, "proteinas": 0.0, "carbohidratos": 8.0, "grasas": 0.0})
    for i in range(20):
        catalog.append({"nombre": f"M{i}", "grupo": "MR" if i % 3 else "DR", "calorias": 150.0 + i, "proteinas": 18.0, "carbohidratos": 8.0, "grasas": 6.0})
    return catalog


def _assert_result(res, has_front: bool = True):
    assert "best_f" in res
    assert isinstance(res["best_f"], tuple) or isinstance(res["best_f"], list)
    assert len(res["best_f"]) == 2
    f1, f2 = res["best_f"]
    assert f1 >= 0.0
    assert f2 >= 0.0
    if has_front:
        assert "front" in res
        assert len(res["front"]) >= 1
    assert "trace" in res


@pytest.mark.parametrize("rep", [DIRECT_INDEX, RANDOM_KEY])
@pytest.mark.parametrize("handler", [REPAIR, PENALTY, DEATH_PENALTY])
def test_nsga2_runs_for_every_combo(rep, handler):
    from diet_bao.ea.nsga2_diet import run_nsga2

    res = run_nsga2(
        _foods(), edad=25, ctarget=2200.0,
        representation=rep, constraint_handler=handler,
        pop_size=15, max_generations=8, seed=42,
    )
    _assert_result(res)


@pytest.mark.parametrize("rep", [DIRECT_INDEX, RANDOM_KEY])
@pytest.mark.parametrize("handler", [REPAIR, PENALTY])  # DEATH_PENALTY can starve PAES
def test_paes_runs_for_every_combo(rep, handler):
    from diet_bao.ea.paes_diet import run_paes

    res = run_paes(
        _foods(), edad=25, ctarget=2200.0,
        representation=rep, constraint_handler=handler,
        max_generations=30, max_archive_size=20, seed=42,
    )
    _assert_result(res)


@pytest.mark.parametrize("rep", [DIRECT_INDEX, RANDOM_KEY])
def test_pso_scalarized_runs(rep):
    from diet_bao.si.pso_diet import run_pso

    res = run_pso(
        _foods(), edad=25, ctarget=2200.0,
        representation=rep, pop_size=15, max_generations=8, seed=42,
    )
    _assert_result(res, has_front=False)
