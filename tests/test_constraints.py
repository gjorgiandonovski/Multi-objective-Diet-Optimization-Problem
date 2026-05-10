import math
import random

import pytest

from diet_bao.constraints import DEATH_PENALTY, PENALTY, REPAIR
from diet_bao.constraints.base import count_violations
from diet_bao.representations import DIRECT_INDEX

from tests.test_encoding import _foods


def _state():
    return DIRECT_INDEX.build(_foods(), edad=25)


def test_count_violations_clean_candidate():
    state = _state()
    candidate = DIRECT_INDEX.generate(state, random.Random(0))
    assert count_violations(candidate, state) == 0


def test_count_violations_corrupted():
    state = _state()
    candidate = DIRECT_INDEX.generate(state, random.Random(0))
    candidate[0] = 999_999
    candidate[3] = 888_888
    assert count_violations(candidate, state) == 2


def test_repair_handler_fixes_violations_and_reevaluates():
    state = _state()
    candidate = DIRECT_INDEX.generate(state, random.Random(0))
    candidate[0] = 999_999
    repaired, fit = REPAIR.process(
        candidate, state, ctarget=2000.0, raw_fitness=(1.0, 1.0), random=random.Random(1)
    )
    assert count_violations(repaired, state) == 0
    # Repair re-evaluates fitness, so it should not be (1, 1) anymore.
    assert fit != (1.0, 1.0)


def test_repair_passthrough_when_no_violations():
    state = _state()
    candidate = DIRECT_INDEX.generate(state, random.Random(0))
    repaired, fit = REPAIR.process(
        candidate, state, ctarget=2000.0, raw_fitness=(123.0, 4.5), random=random.Random(1)
    )
    assert repaired == candidate
    assert fit == (123.0, 4.5)


def test_penalty_handler_adds_per_violation_cost():
    state = _state()
    candidate = DIRECT_INDEX.generate(state, random.Random(0))
    candidate[0] = 999_999
    candidate[1] = 888_888
    _, (f1, f2) = PENALTY.process(
        candidate, state, ctarget=2000.0, raw_fitness=(0.0, 0.0), random=random.Random(0)
    )
    # 2 violations × default penalties (1000, 10).
    assert f1 == pytest.approx(2000.0)
    assert f2 == pytest.approx(20.0)


def test_penalty_handler_passthrough_when_no_violations():
    state = _state()
    candidate = DIRECT_INDEX.generate(state, random.Random(0))
    _, fit = PENALTY.process(
        candidate, state, ctarget=2000.0, raw_fitness=(50.0, 1.5), random=random.Random(0)
    )
    assert fit == (50.0, 1.5)


def test_death_penalty_zeroes_out_infeasibles():
    state = _state()
    candidate = DIRECT_INDEX.generate(state, random.Random(0))
    candidate[0] = 999_999
    _, (f1, f2) = DEATH_PENALTY.process(
        candidate, state, ctarget=2000.0, raw_fitness=(50.0, 1.5), random=random.Random(0)
    )
    assert math.isinf(f1)
    assert math.isinf(f2)


def test_death_penalty_passthrough_when_feasible():
    state = _state()
    candidate = DIRECT_INDEX.generate(state, random.Random(0))
    _, fit = DEATH_PENALTY.process(
        candidate, state, ctarget=2000.0, raw_fitness=(50.0, 1.5), random=random.Random(0)
    )
    assert fit == (50.0, 1.5)
