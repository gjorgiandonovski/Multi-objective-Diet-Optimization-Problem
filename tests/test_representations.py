import random

from diet_bao.encoding import INDIVIDUAL_LENGTH
from diet_bao.representations import DIRECT_INDEX, RANDOM_KEY

from tests.test_encoding import _foods


def test_direct_index_generate_decode_round_trip():
    state = DIRECT_INDEX.build(_foods(), edad=25)
    candidate = DIRECT_INDEX.generate(state, random.Random(0))
    assert len(candidate) == INDIVIDUAL_LENGTH
    decoded = DIRECT_INDEX.decode(state, candidate)
    # Direct-index decode is identity.
    assert decoded == [int(g) for g in candidate]
    # Every gene must lie in its position's domain.
    for gene, domain in zip(decoded, state.per_position):
        assert gene in domain


def test_direct_index_repair_fixes_invalid_genes():
    state = DIRECT_INDEX.build(_foods(), edad=25)
    candidate = DIRECT_INDEX.generate(state, random.Random(0))
    # Corrupt a gene with an out-of-domain value.
    candidate[0] = 999_999  # not a valid food index
    repaired = DIRECT_INDEX.repair(state, candidate, random.Random(1))
    assert repaired[0] in state.per_position[0]
    # Other positions remain unchanged.
    assert repaired[1:] == candidate[1:]


def test_random_key_generate_in_unit_interval():
    state = RANDOM_KEY.build(_foods(), edad=25)
    candidate = RANDOM_KEY.generate(state, random.Random(0))
    assert len(candidate) == INDIVIDUAL_LENGTH
    for x in candidate:
        assert 0.0 <= x <= 1.0


def test_random_key_decodes_into_valid_food_indices():
    state = RANDOM_KEY.build(_foods(), edad=25)
    candidate = RANDOM_KEY.generate(state, random.Random(0))
    decoded = RANDOM_KEY.decode(state, candidate)
    assert len(decoded) == INDIVIDUAL_LENGTH
    for gene, domain in zip(decoded, state.per_position):
        assert gene in domain


def test_random_key_decode_is_deterministic_per_key():
    state = RANDOM_KEY.build(_foods(), edad=25)
    keys = [0.0] * INDIVIDUAL_LENGTH
    decoded_a = RANDOM_KEY.decode(state, keys)
    decoded_b = RANDOM_KEY.decode(state, keys)
    assert decoded_a == decoded_b
    # Key 0.0 should pick the first (index 0) element of each domain.
    expected = [domain[0] for domain in state.per_position]
    assert decoded_a == expected


def test_random_key_repair_clamps_out_of_range():
    state = RANDOM_KEY.build(_foods(), edad=25)
    candidate = [-0.5, 1.5, 0.3, 2.0] + [0.5] * (INDIVIDUAL_LENGTH - 4)
    repaired = RANDOM_KEY.repair(state, candidate, random.Random(0))
    assert repaired[0] == 0.0
    assert repaired[1] == 1.0
    assert repaired[2] == 0.3
    assert repaired[3] == 1.0
