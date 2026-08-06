from __future__ import annotations

from erdos97.kalmanson_splice import (
    FIVE_ROLE_SPLICE,
    SIX_ROLE_SPLICE,
    verify_splice_template,
)


def test_five_role_splice_is_exact_and_equality_minimal() -> None:
    replay = verify_splice_template(FIVE_ROLE_SPLICE)
    assert replay["role_count"] == 5
    assert replay["strict_quad_intersection_size"] == 3
    assert replay["direct_cancelled_pair"] == ["a", "d"]
    assert replay["individual_strict_rows_nonzero"] is True
    assert replay["combined_zero_sum_verified"] is True
    assert replay["selected_equality_footprint_inclusion_minimal"] is True


def test_six_role_splice_is_exact_and_equality_minimal() -> None:
    replay = verify_splice_template(SIX_ROLE_SPLICE)
    assert replay["role_count"] == 6
    assert replay["strict_quad_intersection_size"] == 2
    assert replay["direct_cancelled_pair"] == ["c", "e"]
    assert replay["individual_strict_rows_nonzero"] is True
    assert replay["combined_zero_sum_verified"] is True
    assert replay["selected_equality_footprint_inclusion_minimal"] is True
