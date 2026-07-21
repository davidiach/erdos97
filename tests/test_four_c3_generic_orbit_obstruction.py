from __future__ import annotations

from erdos97.four_c3_generic_orbit_obstruction import build_report


def test_reciprocal_supplier_elimination() -> None:
    report = build_report()
    assert report["m0_forces_rho_one_for_positive_rho"] is True
    assert report["all_cases_force_coincident_orbits"] is True
    assert [
        record["shift_mod_3"] for record in report["nonzero_shift_cases"]
    ] == [1, 2]
    assert all(
        record["forces_rho_one_for_positive_rho"]
        for record in report["nonzero_shift_cases"]
    )
    assert report["half_step_own_cross_polynomial"] == "(rho - 2)*(rho + 1)"
    assert report["half_step_factorization_exact"] is True
    assert report["half_step_ratio_two_satisfies_row_equation"] is True
    assert report["half_step_midpoint_exact"] is True
    assert report["half_step_partner_pair_midpoint"] == report["half_step_center_point"]


def test_scope_keeps_half_step_branches_open() -> None:
    report = build_report()
    assert "not a general proof" in report["claim_scope"]
    assert "not a counterexample" in report["claim_scope"]
    assert "one half-step orbit pair" in report["remaining_branches"]
    assert "two half-step orbit pairs" in report["remaining_branches"]
