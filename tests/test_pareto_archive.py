from diet_bao.si.pareto_archive import (
    best_by_sum,
    dominates,
    nondominated,
    update_archive,
)


def test_dominates_minimisation_vectors():
    assert dominates((1.0, 2.0), (1.0, 3.0))
    assert dominates((1.0, 2.0), (2.0, 2.0))
    assert not dominates((1.0, 3.0), (1.0, 2.0))
    assert not dominates((1.0, 2.0), (1.0, 2.0))


def test_nondominated_filters_dominated_entries():
    entries = [
        {"candidate": [0], "fitness": (1.0, 5.0)},
        {"candidate": [1], "fitness": (2.0, 2.0)},
        {"candidate": [2], "fitness": (3.0, 3.0)},
    ]
    front = nondominated(entries)
    assert {tuple(e["fitness"]) for e in front} == {(1.0, 5.0), (2.0, 2.0)}


def test_update_archive_crowding_prunes_to_max_size():
    entries = [
        {"candidate": [i], "fitness": (float(i), float(10 - i))}
        for i in range(10)
    ]
    archive = update_archive([], entries, max_size=4)
    assert len(archive) == 4
    assert (0.0, 10.0) in {tuple(e["fitness"]) for e in archive}
    assert (9.0, 1.0) in {tuple(e["fitness"]) for e in archive}


def test_best_by_sum_returns_representative_point():
    entries = [
        {"candidate": [0], "fitness": (10.0, 1.0)},
        {"candidate": [1], "fitness": (3.0, 4.0)},
    ]
    assert best_by_sum(entries)["candidate"] == [1]
