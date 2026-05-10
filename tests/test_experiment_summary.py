import pandas as pd

from diet_bao.experiment.experiment_loader import summarize_results


def test_summarize_results_has_expected_index_levels():
    frame = pd.DataFrame(
        [
            {"config_id": "c1", "subject_id": 1, "algorithm": "NSGA-II", "f1_best": 1.0, "f2_best": 2.0, "runtime_s": 3.0},
            {"config_id": "c1", "subject_id": 1, "algorithm": "NSGA-II", "f1_best": 1.5, "f2_best": 2.5, "runtime_s": 3.5},
            {"config_id": "c1", "subject_id": 1, "algorithm": "PSO", "f1_best": 2.0, "f2_best": 3.0, "runtime_s": 4.0},
            {"config_id": "c1", "subject_id": 1, "algorithm": "PSO", "f1_best": 2.5, "f2_best": 3.5, "runtime_s": 4.5},
        ]
    )

    summary = summarize_results(frame)

    assert not summary.empty
    assert set(summary.index.names) == {"config_id", "subject_id", "algorithm"}
    assert ("f1_best", "mean") in summary.columns
    assert ("runtime_s", "mean") in summary.columns
