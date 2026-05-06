from __future__ import annotations

import pytest

from erdos97.incidence_filters import row_ptolemy_product_cancellation_certificates
from erdos97.n9_incidence_frontier import (
    DEFAULT_ROW0_WITNESSES,
    N9_RECTANGLE_TRAP_PATTERN,
    classify_pattern,
    mask_bits,
    mask_from_values,
    row_options,
    run_bounded_scan,
)
from scripts.check_n9_incidence_frontier import assert_expected

EXPECTED_FILTER_ORDER = [
    "row_pair_intersection_cap",
    "adjacent_two_overlap",
    "crossing_bisector",
    "column_indegree_upper",
    "column_pair_cap",
    "odd_forced_perpendicular_cycle",
    "mutual_midpoint_collapse",
    "phi4_rectangle_trap",
    "row_ptolemy_product_cancellation",
    "accepted_frontier",
]


ROW_PTOLEMY_FRONTIER_PATTERN = [
    [1, 2, 3, 8],
    [0, 3, 4, 7],
    [1, 3, 5, 6],
    [2, 4, 5, 8],
    [0, 3, 6, 8],
    [2, 4, 6, 7],
    [1, 5, 7, 8],
    [0, 1, 4, 6],
    [0, 2, 5, 7],
]


def test_registered_n9_rectangle_trap_classifies_as_phi4_obstruction() -> None:
    result = classify_pattern(N9_RECTANGLE_TRAP_PATTERN)

    assert result["status"] == "phi4_rectangle_trap"
    assert result["rectangle_trap_4_cycles"] == 1
    assert result["row_ptolemy_product_cancellation_count"] == 0
    assert result["row_pair_intersection_cap_violations"] == []
    assert result["adjacent_two_overlap_violations"] == []
    assert result["crossing_bisector_violations"] == []


def test_row_ptolemy_frontier_pattern_classifies_as_fixed_order_obstruction() -> None:
    result = classify_pattern(ROW_PTOLEMY_FRONTIER_PATTERN)
    certificates = result["row_ptolemy_product_cancellation_certificates"]

    assert result["status"] == "row_ptolemy_product_cancellation"
    assert result["rectangle_trap_4_cycles"] == 0
    assert result["row_ptolemy_product_cancellation_count"] == 6
    assert certificates
    assert certificates == row_ptolemy_product_cancellation_certificates(
        ROW_PTOLEMY_FRONTIER_PATTERN,
    )[: len(certificates)]
    assert certificates[0]["type"] == "row_ptolemy_product_cancellation"
    assert certificates[0]["status"] == "EXACT_OBSTRUCTION_FOR_FIXED_PATTERN_AND_FIXED_ROW_ORDER"
    assert certificates[0]["ptolemy_identity"] == "d02*d13 = d01*d23 + d03*d12"
    assert certificates[0]["witness_order"] == [1, 2, 3, 8]
    assert certificates[0]["zero_product"]["expression"] == "d03*d12"


def test_row_ptolemy_frontier_pattern_is_not_orderless() -> None:
    result = classify_pattern(
        ROW_PTOLEMY_FRONTIER_PATTERN,
        [0, 1, 2, 6, 5, 7, 4, 8, 3],
    )

    assert result["row_ptolemy_product_cancellation_count"] == 0
    assert result["status"] != "row_ptolemy_product_cancellation"


def test_row0_options_use_default_seed_row_and_other_rows_have_all_choices() -> None:
    assert row_options(0) == [mask_from_values(DEFAULT_ROW0_WITNESSES)]
    assert len(row_options(1)) == 70
    assert all(1 not in mask_bits(mask) for mask in row_options(1))


def test_tiny_bounded_scan_without_seed_priority_is_deterministic() -> None:
    payload = run_bounded_scan(
        max_nodes=20,
        max_full_patterns=5,
        max_examples=1,
        preferred_pattern=None,
    )

    assert payload["type"] == "n9_incidence_frontier_bounded_scan_v1"
    assert payload["trust"] == "BOUNDED_INCIDENCE_CSP_DIAGNOSTIC"
    assert payload["truncated"] is True
    assert payload["hit_node_limit"] is True
    assert payload["nodes_visited"] == 21
    assert payload["full_patterns_checked"] == 0
    assert payload["filter_order"] == EXPECTED_FILTER_ORDER
    assert list(payload["full_classification_counts"]) == EXPECTED_FILTER_ORDER
    assert set(payload["full_classification_counts"]) == set(EXPECTED_FILTER_ORDER)
    assert payload["partial_rejection_counts"]["adjacent_two_overlap"] > 0
    assert payload["partial_rejection_counts"]["crossing_bisector"] > 0
    assert payload["seeded_cases"][0]["classification"]["status"] == "phi4_rectangle_trap"


def test_bounded_scan_can_stop_on_full_pattern_limit() -> None:
    payload = run_bounded_scan(max_nodes=100_000, max_full_patterns=1, max_examples=1)

    assert payload["hit_full_pattern_limit"] is True
    assert payload["full_patterns_checked"] == 1
    assert sum(payload["full_classification_counts"].values()) == 1
    assert payload["filter_order"] == EXPECTED_FILTER_ORDER
    assert list(payload["full_classification_counts"]) == EXPECTED_FILTER_ORDER
    assert set(payload["full_classification_counts"]) == set(EXPECTED_FILTER_ORDER)


def test_default_bounded_scan_has_no_remaining_accepted_frontier() -> None:
    payload = run_bounded_scan(max_examples=1)

    assert payload["full_classification_counts"]["phi4_rectangle_trap"] == 1
    assert payload["full_classification_counts"]["odd_forced_perpendicular_cycle"] == 1
    assert payload["full_classification_counts"]["row_ptolemy_product_cancellation"] == 1
    assert payload["accepted_frontier_count"] == 0
    assert payload["full_classification_counts"]["accepted_frontier"] == 0


def test_checker_assert_expected_allows_zero_example_payloads() -> None:
    payload = run_bounded_scan(max_examples=0)

    assert payload["examples"] == {}
    assert_expected(payload)


@pytest.mark.parametrize(
    "row0_witnesses",
    ([0, 1, 2, 3], [1, 2, 3, 9], [-1, 1, 2, 3], [1, 1, 2, 3]),
)
def test_invalid_row0_witnesses_are_rejected(row0_witnesses: list[int]) -> None:
    with pytest.raises(ValueError, match="row0_witnesses"):
        run_bounded_scan(row0_witnesses=row0_witnesses)
