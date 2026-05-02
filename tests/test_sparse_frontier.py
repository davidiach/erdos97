from __future__ import annotations

from erdos97.search import built_in_patterns
from erdos97.sparse_frontier import (
    normalize_cyclic_order,
    sample_empty_gap_orders,
    sparse_frontier_summary,
    sparse_row_profiles,
)


FRONTIER_PATTERNS = (
    "C19_skew",
    "C13_sidon_1_2_4_10",
    "C25_sidon_2_5_9_14",
    "C29_sidon_1_3_7_15",
)


def test_frontier_patterns_have_trivial_empty_radius_choice() -> None:
    patterns = built_in_patterns()

    for name in FRONTIER_PATTERNS:
        summary = sparse_frontier_summary(name, patterns[name].S)
        assert summary["trivial_empty_radius_choice_exists"] is True
        assert summary["all_rows_have_uncovered_consecutive_pair"] is True
        assert summary["order_free_blocked_rows"] == []


def test_c13_sidon_all_witness_pairs_have_at_most_one_source() -> None:
    pattern = built_in_patterns()["C13_sidon_1_2_4_10"]

    summary = sparse_frontier_summary(pattern.name, pattern.S)

    assert summary["all_pair_source_count_histogram"] == {"0": 26, "1": 52}
    assert summary["consecutive_pair_source_count_histogram"] == {"0": 13, "1": 26}


def test_sparse_row_profile_records_uncovered_consecutive_pairs() -> None:
    pattern = built_in_patterns()["C19_skew"]

    row0 = sparse_row_profiles(pattern.S)[0]

    assert row0.center == 0
    assert [item.pair for item in row0.consecutive_pairs] == [
        (5, 9),
        (9, 11),
        (11, 16),
    ]
    assert [item.pair for item in row0.uncovered_consecutive_pairs] == [
        (5, 9),
        (9, 11),
    ]


def test_c13_has_sampled_order_without_empty_choice() -> None:
    pattern = built_in_patterns()["C13_sidon_1_2_4_10"]
    order = [1, 10, 9, 5, 11, 2, 3, 7, 8, 4, 0, 12, 6]

    summary = sparse_frontier_summary(pattern.name, pattern.S, order=order)

    assert summary["trivial_empty_radius_choice_exists"] is False
    assert summary["rows_with_uncovered_consecutive_pair"] == [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        9,
        10,
        11,
        12,
    ]


def test_sample_empty_gap_orders_records_counterexamples() -> None:
    pattern = built_in_patterns()["C13_sidon_1_2_4_10"]

    sample = sample_empty_gap_orders(pattern.name, pattern.S, random_samples=20, seed=0)

    assert sample["orders_checked"] == 21
    assert sample["empty_choice_orders"] < sample["orders_checked"]
    assert sample["examples_without_empty_choice"]


def test_normalize_cyclic_order_quotients_rotation_and_reversal() -> None:
    assert normalize_cyclic_order([2, 3, 0, 1]) == [0, 1, 2, 3]
    assert normalize_cyclic_order([2, 1, 0, 3]) == [0, 1, 2, 3]
