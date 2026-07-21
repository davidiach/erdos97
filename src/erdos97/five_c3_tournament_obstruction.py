"""Exact algebra replay for the five-C3 regular-tournament obstruction."""

from __future__ import annotations

from typing import Any

import sympy as sp


SCHEMA = "erdos97.five_c3_tournament_obstruction.v1"
CLAIM_SCOPE = (
    "Exact obstruction for five distinct concentric C3 orbits with own-pair "
    "rows and the reciprocal-free regular-tournament supplier pattern; not a "
    "general proof, not a counterexample, and not a four-singleton-row "
    "obstruction."
)


def build_report() -> dict[str, Any]:
    """Replay the exact circle-product identities used in the proof."""

    t, u, radius = sp.symbols("t u radius", real=True)
    x, z = sp.symbols("x z")
    imaginary = sp.I
    root3 = sp.sqrt(3)
    parameter_a = 2 + root3
    omega = (-1 + imaginary * root3) / 2

    def circle_parameter(value: sp.Expr) -> sp.Expr:
        return 1 + root3 * (1 + imaginary * value) / (1 - imaginary * value)

    xt = circle_parameter(t)
    xu = circle_parameter(u)

    primitive_records: list[dict[str, Any]] = []
    primitive_inputs = (
        (1, omega, (t + parameter_a) * (u + parameter_a) * (t * u - parameter_a)),
        (2, omega**2, (t - parameter_a) * (u - parameter_a) * (t * u - parameter_a)),
    )
    for gain, eta, expected_factor in primitive_inputs:
        product = sp.factor(eta * xt * xu, extension=[imaginary, root3])
        residual = sp.together(
            product * sp.conjugate(product)
            - product
            - sp.conjugate(product)
            - 2
        )
        numerator, denominator = residual.as_numer_denom()
        numerator = sp.factor(numerator, extension=[imaginary, root3])
        quotient = sp.factor(
            sp.cancel(numerator / expected_factor), extension=[imaginary, root3]
        )
        primitive_records.append(
            {
                "gain_mod_3": gain,
                "numerator_factorization": str(numerator),
                "denominator": str(
                    sp.factor(denominator, extension=[imaginary, root3])
                ),
                "expected_parameter_factor": str(expected_factor),
                "factor_quotient": str(quotient),
                "quotient_is_nonzero_constant": not quotient.free_symbols
                and quotient != 0,
            }
        )

    conjugation_numerator = sp.factor(
        (x * z + 2) * (x - 1) * (z - 1)
        - (x * z - 1) * (x + 2) * (z + 2)
    )
    expected_conjugation = -3 * (x * z * (x + z) - 2)

    radius_polynomial = sp.factor(radius**3 - 3 * radius**2 + 2)

    report = {
        "schema": SCHEMA,
        "trust": "LEMMA_EXACT_ALGEBRA_REPLAY_REVIEW_PENDING",
        "claim_scope": CLAIM_SCOPE,
        "circle_parameter": str(xt),
        "parameter_a": str(parameter_a),
        "x_at_positive_a_is_omega": sp.simplify(
            circle_parameter(parameter_a) - omega
        )
        == 0,
        "x_at_negative_a_is_omega_squared": sp.simplify(
            circle_parameter(-parameter_a) - omega**2
        )
        == 0,
        "parameter_product_is_minus_two": sp.simplify(
            circle_parameter(t) * circle_parameter(parameter_a / t) + 2
        )
        == 0,
        "primitive_gain_records": primitive_records,
        "all_primitive_factorizations_exact": all(
            record["quotient_is_nonzero_constant"] for record in primitive_records
        ),
        "zero_gain_conjugation_numerator": str(conjugation_numerator),
        "zero_gain_conjugation_factor_exact": sp.simplify(
            conjugation_numerator - expected_conjugation
        )
        == 0,
        "radius_inequality_polynomial": str(radius_polynomial),
        "radius_factorization_exact": sp.simplify(
            radius_polynomial - (radius - 1) * (radius**2 - 2 * radius - 2)
        )
        == 0,
        "gain_quotient_case_count": 3**6,
        "case_count_closed_by_one_product_argument": True,
        "excluded_row_shapes": [
            "four cross-orbit singleton witnesses",
            "half-step partner-pair rows",
            "non-tournament supplier patterns",
        ],
    }

    required = (
        "x_at_positive_a_is_omega",
        "x_at_negative_a_is_omega_squared",
        "parameter_product_is_minus_two",
        "all_primitive_factorizations_exact",
        "zero_gain_conjugation_factor_exact",
        "radius_factorization_exact",
    )
    for field in required:
        if not report[field]:
            raise AssertionError(f"unexpected symbolic identity: {field}")
    return report
