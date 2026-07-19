from __future__ import annotations

from itertools import combinations

import pytest

from erdos97.period_three_radius_partition import (
    EXPECTED_LARGEST_CLASS_DISTRIBUTION,
    EXPECTED_OCCURRENCE_FREE_PARTITIONS,
    EXPECTED_TOTAL_PARTITIONS,
    PAIR_SLOTS,
    audit_three_reverse_pair_radius_partitions,
    has_complete_pair,
    matches_expected,
    restricted_growth_partitions,
)


def test_partition_census_matches_expected() -> None:
    audit = audit_three_reverse_pair_radius_partitions()
    assert audit.total_partitions == EXPECTED_TOTAL_PARTITIONS
    assert (
        audit.occurrence_free_partitions
        == EXPECTED_OCCURRENCE_FREE_PARTITIONS
    )
    assert (
        audit.largest_class_distribution
        == EXPECTED_LARGEST_CLASS_DISTRIBUTION
    )
    assert matches_expected(audit)


def test_every_four_slots_contain_a_complete_pair() -> None:
    for slots in combinations(range(6), 4):
        assert any(left in slots and right in slots for left, right in PAIR_SLOTS)


def test_three_slot_threshold_is_sharp() -> None:
    slots = {0, 2, 4}
    assert all(
        not (left in slots and right in slots)
        for left, right in PAIR_SLOTS
    )


def test_occurrence_detection() -> None:
    assert has_complete_pair((0, 0, 1, 2, 3, 4))
    assert not has_complete_pair((0, 1, 0, 1, 0, 1))


def test_partition_input_guards() -> None:
    with pytest.raises(ValueError):
        list(restricted_growth_partitions(-1))
    with pytest.raises(ValueError):
        has_complete_pair((0, 1))
