from __future__ import annotations

import pytest

from erdos97.n9_incidence_frontier import (
    DEFAULT_ROW0_WITNESSES,
    N9_RECTANGLE_TRAP_PATTERN,
    classify_pattern,
    mask_bits,
    mask_from_values,
    row_options,
    run_bounded_scan,
)


def test_registered_n9_rectangle_trap_classifies_as_phi4_obstruction() -> None:
    result = classify_pattern(N9_RECTANGLE_TRAP_PATTERN)

    assert result["status"] == "phi4_rectangle_trap"
    assert result["rectangle_trap_4_cycles"] == 1
    assert result["row_pair_intersection_cap_violations"] == []
    assert result["adjacent_two_overlap_violations"] == []
    assert result["crossing_bisector_violations"] == []


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
    assert payload["partial_rejection_counts"]["adjacent_two_overlap"] > 0
    assert payload["partial_rejection_counts"]["crossing_bisector"] > 0
    assert payload["seeded_cases"][0]["classification"]["status"] == "phi4_rectangle_trap"


def test_bounded_scan_can_stop_on_full_pattern_limit() -> None:
    payload = run_bounded_scan(max_nodes=100_000, max_full_patterns=1, max_examples=1)

    assert payload["hit_full_pattern_limit"] is True
    assert payload["full_patterns_checked"] == 1
    assert sum(payload["full_classification_counts"].values()) == 1


@pytest.mark.parametrize(
    "row0_witnesses",
    ([0, 1, 2, 3], [1, 2, 3, 9], [-1, 1, 2, 3], [1, 1, 2, 3]),
)
def test_invalid_row0_witnesses_are_rejected(row0_witnesses: list[int]) -> None:
    with pytest.raises(ValueError, match="row0_witnesses"):
        run_bounded_scan(row0_witnesses=row0_witnesses)
