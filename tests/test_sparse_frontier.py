from __future__ import annotations

from erdos97.search import built_in_patterns
from erdos97.sparse_frontier import (
    certify_min_uncovered_consecutive_rows,
    normalize_cyclic_order,
    sample_empty_gap_orders,
    sample_radius_propagation_orders,
    search_adversarial_orders,
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


def test_larger_sparse_frontier_has_order_free_empty_gap_certificate() -> None:
    patterns = built_in_patterns()

    for name in ("C19_skew", "C25_sidon_2_5_9_14", "C29_sidon_1_3_7_15"):
        summary = sparse_frontier_summary(name, patterns[name].S)

        assert summary["all_rows_order_free_empty_gap"] is True
        assert summary["trivial_empty_radius_choice_all_orders"] is True
        assert len(summary["order_free_empty_gap_rows"]) == patterns[name].n


def test_c19_empty_gap_order_bound_is_trivial_from_order_free_certificate() -> None:
    pattern = built_in_patterns()["C19_skew"]

    result = certify_min_uncovered_consecutive_rows(pattern.name, pattern.S)

    assert result["status"] == "CERTIFIED_OPTIMUM"
    assert result["search_complete"] is True
    assert result["certified_min_rows_with_uncovered_consecutive_pair"] == 19
    assert result["certified_max_blocked_rows"] == 0
    assert result["explored_nodes"] == 1


def test_empty_gap_order_bound_matches_all_other_pentagon() -> None:
    S = [[j for j in range(5) if j != i] for i in range(5)]

    result = certify_min_uncovered_consecutive_rows("K5_all_other", S)

    assert result["status"] == "CERTIFIED_OPTIMUM"
    assert result["certified_min_rows_with_uncovered_consecutive_pair"] == 0
    assert result["certified_max_blocked_rows"] == 5
    assert result["best_rows_with_uncovered_consecutive_pair"] == []


def test_c13_sidon_all_witness_pairs_have_at_most_one_source() -> None:
    pattern = built_in_patterns()["C13_sidon_1_2_4_10"]

    summary = sparse_frontier_summary(pattern.name, pattern.S)

    assert summary["all_pair_source_count_histogram"] == {"0": 26, "1": 52}
    assert summary["consecutive_pair_source_count_histogram"] == {"0": 13, "1": 26}
    assert summary["all_rows_order_free_empty_gap"] is False
    assert summary["order_free_empty_gap_rows"] == []


def test_c13_empty_gap_order_bound_certifies_three_rows() -> None:
    pattern = built_in_patterns()["C13_sidon_1_2_4_10"]

    result = certify_min_uncovered_consecutive_rows(pattern.name, pattern.S)

    assert result["status"] == "CERTIFIED_OPTIMUM"
    assert result["search_complete"] is True
    assert result["certified_min_rows_with_uncovered_consecutive_pair"] == 3
    assert result["certified_max_blocked_rows"] == 10
    assert result["best_order"] == [0, 1, 3, 11, 7, 5, 8, 10, 12, 2, 6, 4, 9]
    assert result["best_rows_with_uncovered_consecutive_pair"] == [0, 1, 7]
    assert result["best_radius_propagation"]["status"] == "PASS_ACYCLIC_CHOICE"
    assert result["best_radius_choice_minimization"]["edge_count"] == 10
    assert result["best_radius_choice_minimization"]["optimality_certified"] is True


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
    assert row0.order_free_empty_gap is True
    assert row0.covered_witness_path_orders == []


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


def test_sample_radius_propagation_orders_distinguishes_empty_gap_failures() -> None:
    pattern = built_in_patterns()["C13_sidon_1_2_4_10"]

    sample = sample_radius_propagation_orders(
        pattern.name,
        pattern.S,
        random_samples=20,
        seed=0,
    )

    assert sample["orders_checked"] == 21
    assert sample["empty_choice_orders"] == 3
    assert sample["radius_status_histogram"] == {"PASS_ACYCLIC_CHOICE": 21}
    assert sample["no_empty_choice_radius_status_histogram"] == {
        "PASS_ACYCLIC_CHOICE": 18
    }
    assert sample["examples_without_empty_choice"]
    example = sample["examples_without_empty_choice"][0]
    assert example["trivial_empty_radius_choice_exists"] is False
    assert example["radius_propagation"]["status"] == "PASS_ACYCLIC_CHOICE"


def test_adversarial_order_search_finds_stronger_c13_order() -> None:
    pattern = built_in_patterns()["C13_sidon_1_2_4_10"]

    result = search_adversarial_orders(
        pattern.name,
        pattern.S,
        random_samples=20,
        seed=0,
        restarts=4,
        local_steps=40,
    )

    assert result["orders_evaluated"] == 170
    assert result["min_rows_with_uncovered_consecutive_pair"] == 5
    assert result["radius_status_histogram"] == {"PASS_ACYCLIC_CHOICE": 170}
    best = result["best_examples"][0]
    assert len(best["rows_with_uncovered_consecutive_pair"]) == 5
    assert best["radius_propagation"]["acyclic_edge_count"] == 8
    assert best["radius_choice_minimization"]["edge_count"] == 8
    assert best["radius_choice_minimization"]["optimality_certified"] is True


def test_normalize_cyclic_order_quotients_rotation_and_reversal() -> None:
    assert normalize_cyclic_order([2, 3, 0, 1]) == [0, 1, 2, 3]
    assert normalize_cyclic_order([2, 1, 0, 3]) == [0, 1, 2, 3]
