import pandas as pd

from diet_bao.experiment.experiment_loader import (
    AlgorithmConfig,
    BenchmarkPlan,
    default_plan,
    run_all_subjects,
)
from diet_bao.types import SubjectProfile


def test_run_all_subjects_empty():
    plan = BenchmarkPlan(configs=[], n_runs=1)
    df = run_all_subjects([], [], plan)
    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_subject_dataclass():
    subject = SubjectProfile(1, 25, 2200.0, [], [], [])
    assert subject.sujeto_id == 1
    assert subject.calorias == 2200.0


def test_default_plan_has_at_least_one_config_per_algorithm():
    plan = default_plan(n_runs=2, seed0=0)
    algorithms = {c.algorithm for c in plan.configs}
    assert "NSGA-II" in algorithms
    assert "PAES" in algorithms
    assert "MOPSO" in algorithms


def test_algorithm_config_kwargs_for_pso_drops_constraint_handler():
    cfg = AlgorithmConfig("test_pso", "PSO-scalar", "random_key", "repair", 10, 5)
    kwargs = cfg.kwargs()
    assert "constraint_handler" not in kwargs
    assert kwargs["pop_size"] == 10
    assert kwargs["max_generations"] == 5


def test_algorithm_config_kwargs_for_nsga2_includes_constraint_handler():
    cfg = AlgorithmConfig("test_nsga2", "NSGA-II", "direct_index", "penalty", 20, 10)
    kwargs = cfg.kwargs()
    assert "constraint_handler" in kwargs
    assert kwargs["constraint_handler"].name == "penalty"
