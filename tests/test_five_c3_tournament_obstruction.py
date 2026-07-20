from __future__ import annotations

from erdos97.five_c3_tournament_obstruction import build_report


def test_exact_gain_factorizations() -> None:
    report = build_report()
    assert report["gain_quotient_case_count"] == 3**6
    assert report["all_primitive_factorizations_exact"] is True
    assert [
        record["gain_mod_3"] for record in report["primitive_gain_records"]
    ] == [1, 2]
    assert all(
        record["quotient_is_nonzero_constant"]
        for record in report["primitive_gain_records"]
    )
    assert report["parameter_product_is_minus_two"] is True


def test_zero_gain_modulus_reduction() -> None:
    report = build_report()
    assert report["zero_gain_conjugation_factor_exact"] is True
    assert report["radius_inequality_polynomial"] == (
        "(radius - 1)*(radius**2 - 2*radius - 2)"
    )
    assert report["radius_factorization_exact"] is True


def test_scope_preserves_uncovered_rows() -> None:
    report = build_report()
    assert "not a general proof" in report["claim_scope"]
    assert "not a counterexample" in report["claim_scope"]
    assert "four cross-orbit singleton witnesses" in report["excluded_row_shapes"]
    assert "half-step partner-pair rows" in report["excluded_row_shapes"]
