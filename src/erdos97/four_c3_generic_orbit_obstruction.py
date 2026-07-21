"""Exact algebra replay for the four-generic-C3-orbit obstruction.

The mathematical statement and proof are in
``docs/four-c3-generic-orbit-obstruction.md``.  This module verifies the three
reciprocal-supplier elimination cases and one half-step midpoint degeneration.
It is not a general solver for Erdos Problem #97 and does not close the
remaining half-step branches.
"""

from __future__ import annotations

from typing import Any

import sympy as sp


SCHEMA = "erdos97.four_c3_generic_orbit_obstruction.v1"
CLAIM_SCOPE = (
    "Exact symbolic replay of the reciprocal-supplier lemma for four distinct "
    "concentric C3 orbits with no aligned or half-step phase pair; not a "
    "general proof, not a counterexample, and not a half-step-branch closure."
)


def build_report() -> dict[str, Any]:
    """Return an exact symbolic report for shifts m=0,1,2."""

    rho = sp.symbols("rho", positive=True)
    base_radius = sp.symbols("base_radius", positive=True)
    cosine = (rho**2 - 2) / (2 * rho)
    half_step_own_cross = sp.factor(rho**2 - rho - 2)
    half_step_midpoint = (
        sp.simplify(
            (
                2 * base_radius * sp.cos(sp.pi / 3)
                + 2 * base_radius * sp.cos(-sp.pi / 3)
            )
            / 2
        ),
        sp.simplify(
            (
                2 * base_radius * sp.sin(sp.pi / 3)
                + 2 * base_radius * sp.sin(-sp.pi / 3)
            )
            / 2
        ),
    )
    half_step_center = (base_radius, sp.Integer(0))

    # For m=0, equality of the two cosine terms gives
    # rho^2 - 2 = 1 - 2 rho^2.
    m0_difference = sp.factor((rho**2 - 2) - (1 - 2 * rho**2))
    m0_forces_rho_one = (
        sp.simplify(m0_difference - 3 * (rho - 1) * (rho + 1)) == 0
    )

    records: list[dict[str, Any]] = []
    for shift, sine_sign in ((1, -1), (2, 1)):
        sine = sine_sign * sp.sqrt(3) * rho / 2
        circle_residual = sp.factor(cosine**2 + sine**2 - 1)
        numerator, denominator = sp.fraction(circle_residual)
        records.append(
            {
                "shift_mod_3": shift,
                "cosine": str(cosine),
                "sine": str(sine),
                "circle_residual": str(circle_residual),
                "residual_numerator": str(sp.factor(numerator)),
                "residual_denominator": str(sp.factor(denominator)),
                "forces_rho_one_for_positive_rho": sp.simplify(
                    numerator - (rho - 1) ** 2 * (rho + 1) ** 2
                )
                == 0,
            }
        )

    report = {
        "schema": SCHEMA,
        "trust": "LEMMA_EXACT_ALGEBRA_REPLAY_REVIEW_PENDING",
        "claim_scope": CLAIM_SCOPE,
        "m0_difference": str(m0_difference),
        "m0_forces_rho_one_for_positive_rho": m0_forces_rho_one,
        "nonzero_shift_cases": records,
        "all_cases_force_coincident_orbits": m0_forces_rho_one
        and all(
            record["forces_rho_one_for_positive_rho"] for record in records
        ),
        "half_step_own_cross_polynomial": str(half_step_own_cross),
        "half_step_factorization_exact": sp.simplify(
            half_step_own_cross - (rho - 2) * (rho + 1)
        )
        == 0,
        "half_step_positive_ratio": "2",
        "half_step_ratio_two_satisfies_row_equation": sp.simplify(
            half_step_own_cross.subs(rho, 2)
        )
        == 0,
        "half_step_partner_pair_midpoint": [
            str(coordinate) for coordinate in half_step_midpoint
        ],
        "half_step_center_point": [str(coordinate) for coordinate in half_step_center],
        "half_step_midpoint_exact": all(
            sp.simplify(left - right) == 0
            for left, right in zip(half_step_midpoint, half_step_center, strict=True)
        ),
        "remaining_branches": [
            "one half-step orbit pair",
            "two half-step orbit pairs",
            "arbitrary non-orbit configurations",
        ],
    }
    if not report["m0_forces_rho_one_for_positive_rho"]:
        raise AssertionError("unexpected m=0 elimination")
    if not report["all_cases_force_coincident_orbits"]:
        raise AssertionError("unexpected nonzero-shift elimination")
    if not report["half_step_factorization_exact"]:
        raise AssertionError("unexpected half-step factorization")
    if not report["half_step_ratio_two_satisfies_row_equation"]:
        raise AssertionError("unexpected half-step positive root")
    if not report["half_step_midpoint_exact"]:
        raise AssertionError("unexpected half-step midpoint reduction")
    return report
