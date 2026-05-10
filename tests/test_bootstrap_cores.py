from __future__ import annotations

import pytest

from erdos97.adaptive_blockers import singleton_rich_classes_from_pattern
from erdos97.bootstrap_cores import (
    audit_bootstrap_core,
    closure,
    cyclic_capacity_from_runs,
    cyclic_capacity_sum,
    outside_runs,
    search_generating_seed,
    validate_full_rich_classes,
)
from erdos97.bridge_negative_controls import c13_sidon_rows
from scripts.check_bootstrap_core_bridge import all_packets, assert_expected


def test_closure_rank_matches_ear_positive_sanity_case() -> None:
    rich_classes = tuple(
        (tuple(label for label in range(5) if label != center),)
        for center in range(5)
    )

    result = closure([0, 1, 2], rich_classes)
    rank = search_generating_seed(rich_classes, limit=3)

    assert result.generates_all
    assert result.order == [0, 1, 2, 3, 4]
    assert rank.rank_leq_limit
    assert rank.generating_seed == [0, 1, 2]


def test_c13_fixed_row_bootstrap_core_packet() -> None:
    rich_classes = singleton_rich_classes_from_pattern(c13_sidon_rows())

    rank = search_generating_seed(rich_classes, limit=3)
    audit = audit_bootstrap_core([0, 1, 2, 3], rich_classes)

    assert not rank.rank_leq_limit
    assert rank.checked_seed_count == 377
    assert rank.largest_closure_size == 4
    assert audit.core_generates_all
    assert audit.inclusion_minimal
    assert audit.private_halo_requirement_ok
    assert audit.private_pair_lower_bound == 4
    assert audit.private_pair_count == 6
    assert audit.cyclic_capacity_sum == 36
    assert audit.weighted_capacity_ok


def test_cyclic_capacity_matches_outside_run_formula() -> None:
    runs = outside_runs([0, 2, 4], 6)

    assert runs == [[1], [3], [5]]
    assert cyclic_capacity_sum([0, 2, 4], 6) == 6
    assert cyclic_capacity_sum(iter([0, 2, 4]), 6) == 6
    assert cyclic_capacity_from_runs(runs) == 6


def test_cyclic_capacity_requires_nonempty_core() -> None:
    with pytest.raises(ValueError, match="nonempty"):
        outside_runs([], 5)

    with pytest.raises(ValueError, match="nonempty"):
        cyclic_capacity_sum([], 5)


def test_full_rich_classes_reject_overlap_at_same_center() -> None:
    rich_classes = (
        ((1, 2, 3, 4), (4, 5, 6, 7)),
        *((tuple(label for label in range(8) if label != center),) for center in range(1, 8)),
    )

    with pytest.raises(ValueError, match="overlaps"):
        validate_full_rich_classes(rich_classes)


def test_bootstrap_core_checker_packets() -> None:
    assert_expected(all_packets())
