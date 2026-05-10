import math

import pytest

from diet_bao.metrics import (
    delta_spread,
    hypervolume_2d,
    inverted_generational_distance,
    schott_spacing,
)
from diet_bao.metrics.igd import union_reference_front


# ---------------- Hypervolume ----------------


def test_hv_single_point():
    assert hypervolume_2d([(1.0, 1.0)], reference=(10.0, 10.0)) == pytest.approx(81.0)


def test_hv_three_point_known():
    front = [(1.0, 5.0), (3.0, 3.0), (5.0, 1.0)]
    assert hypervolume_2d(front, reference=(6.0, 6.0)) == pytest.approx(13.0)


def test_hv_dominated_point_ignored():
    front_with = [(2.0, 2.0), (3.0, 3.0)]
    front_without = [(2.0, 2.0)]
    r = (10.0, 10.0)
    assert hypervolume_2d(front_with, r) == pytest.approx(hypervolume_2d(front_without, r))


def test_hv_empty_front():
    assert hypervolume_2d([], reference=(1.0, 1.0)) == 0.0


def test_hv_point_outside_reference():
    assert hypervolume_2d([(20.0, 20.0)], reference=(10.0, 10.0)) == 0.0


# ---------------- IGD ----------------


def test_igd_perfect_match():
    pts = [(1.0, 5.0), (3.0, 3.0), (5.0, 1.0)]
    assert inverted_generational_distance(pts, pts) == pytest.approx(0.0)


def test_igd_known_distance():
    assert inverted_generational_distance([(3.0, 4.0)], [(0.0, 0.0)]) == pytest.approx(5.0)


def test_igd_empty_front_is_inf():
    assert math.isinf(inverted_generational_distance([], [(0.0, 0.0)]))


def test_union_reference_front_filters_dominated():
    a = [(1.0, 5.0), (3.0, 3.0)]
    b = [(5.0, 5.0), (5.0, 1.0)]
    ref = union_reference_front(a, b)
    assert (1.0, 5.0) in ref
    assert (3.0, 3.0) in ref
    assert (5.0, 1.0) in ref
    assert (5.0, 5.0) not in ref


# ---------------- Schott's spacing ----------------


def test_schott_spacing_uniform_front_is_zero():
    front = [(0.0, 4.0), (1.0, 3.0), (2.0, 2.0)]
    assert schott_spacing(front) == pytest.approx(0.0, abs=1e-9)


def test_schott_spacing_nonuniform_is_positive():
    front = [(0.0, 10.0), (0.1, 9.9), (5.0, 0.0)]
    assert schott_spacing(front) > 0.0


def test_schott_spacing_single_point_is_zero():
    assert schott_spacing([(1.0, 1.0)]) == 0.0


# ---------------- Delta spread (Deb) ----------------


def test_delta_spread_uniform_front_without_reference_is_zero():
    """With no reference extremes, Delta collapses to the spread component
    sum |d_i - d_bar| / (n * d_bar). For a perfectly uniform front this is 0.
    """
    front = [(0.0, 4.0), (1.0, 3.0), (2.0, 2.0)]
    assert delta_spread(front) == pytest.approx(0.0, abs=1e-9)


def test_delta_spread_nonuniform_is_positive():
    front = [(0.0, 10.0), (0.1, 9.9), (5.0, 0.0)]
    assert delta_spread(front) > 0.0


def test_delta_spread_with_matching_reference_extremes_is_zero_for_uniform():
    """Uniform front whose extremes match the reference -> Delta = 0."""
    front = [(0.0, 4.0), (1.0, 3.0), (2.0, 2.0)]
    reference_extremes = [(0.0, 4.0), (2.0, 2.0)]
    assert delta_spread(front, reference_extremes) == pytest.approx(0.0, abs=1e-9)


def test_delta_spread_with_offset_reference_extremes_is_positive():
    """If the obtained front is uniform but its extremes are far from the
    reference extremes, the extent term pushes Delta above zero.
    """
    front = [(1.0, 3.0), (2.0, 2.0), (3.0, 1.0)]
    reference_extremes = [(0.0, 4.0), (4.0, 0.0)]
    assert delta_spread(front, reference_extremes) > 0.0


def test_delta_spread_single_point_is_zero():
    assert delta_spread([(1.0, 1.0)]) == 0.0


def test_delta_spread_rejects_wrong_reference_size():
    with pytest.raises(ValueError):
        delta_spread([(0.0, 1.0), (1.0, 0.0)], reference_extremes=[(0.0, 0.0)])
