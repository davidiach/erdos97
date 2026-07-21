from __future__ import annotations

from erdos97.five_c3_all_cross_nonreciprocal_obstruction import build_report


def test_pair_projection_and_bilinear_reductions() -> None:
    report = build_report()
    assert [
        record["gain_sum_mod_3"] for record in report["projection_records"]
    ] == [1, 2]
    assert report["all_nonreciprocal_projection_reductions_exact"] is True
    assert report["bilinear_pair_is_pair_polynomial"] is True
    assert report["bilinear_determinant"] == "6"
    assert report["signature_is_two_two"] is True


def test_exceptional_vectors_are_exactly_aligned_or_half_step() -> None:
    report = build_report()
    assert report["diagonal_factorization"] == (
        "3*(row_i - u)*(row_i - 3*u)"
    )
    assert report["same_type_row_equals_u"] == "(u - v)**2"
    assert report["same_type_row_equals_three_u"] == "3*(u - v)**2"
    assert report["row_u_forces_half_step_cosine"] is True
    assert report["row_three_u_forces_aligned_cosine"] is True


def test_scope_preserves_reciprocal_and_mixed_cases() -> None:
    report = build_report()
    assert "not a general proof" in report["claim_scope"]
    assert "not a counterexample" in report["claim_scope"]
    assert "at least one reciprocal mutual gain-pair" in report["remaining_cases"]
    assert "mixed own-pair and four-cross-singleton rows" in report[
        "remaining_cases"
    ]
