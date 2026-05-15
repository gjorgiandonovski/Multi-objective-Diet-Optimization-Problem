from diet_bao.experiment.experiment_loader import _evaluate_run, _hv_reference


def test_hv_reference_uses_all_points_across_fronts():
    fronts = [
        [(1.0, 100.0), (4.0, 80.0)],
        [(50.0, 2.0)],
    ]

    assert _hv_reference(fronts) == (56.00000000000001, 111.00000000000001)


def test_evaluate_run_accepts_common_hv_reference_point():
    result = {"front": [(1.0, 5.0)]}
    reference_front = [(1.0, 5.0), (5.0, 1.0)]

    hv, igd, spacing, delta = _evaluate_run(
        result,
        reference_front,
        hv_reference=(6.0, 6.0),
    )

    assert hv == 5.0
    assert igd > 0.0
    assert spacing == 0.0
    assert delta == 0.0
