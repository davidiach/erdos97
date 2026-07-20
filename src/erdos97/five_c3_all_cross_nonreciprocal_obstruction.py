"""Exact algebra replay for the five-C3 all-cross nonreciprocal obstruction."""

from __future__ import annotations

from typing import Any

import sympy as sp


SCHEMA = "erdos97.five_c3_all_cross_nonreciprocal_obstruction.v1"
CLAIM_SCOPE = (
    "Exact obstruction for five distinct concentric C3 orbits with no "
    "half-step pair, four cross-orbit singleton witnesses in every row, and "
    "all ten mutual gain-pairs nonreciprocal; not a reciprocal-gain closure, "
    "not a mixed-row closure, not a general proof, and not a counterexample."
)


def build_report() -> dict[str, Any]:
    """Replay the pair reduction and the exceptional-vector factorizations."""

    u, v = sp.symbols("u v", positive=True)
    row_i, row_j = sp.symbols("row_i row_j", positive=True)
    projection_i = (u + v - row_i) / 2
    projection_j = (u + v - row_j) / 2

    pair_polynomial = sp.factor(
        3 * (u**2 + u * v + v**2)
        - 3 * (u + v) * (row_i + row_j)
        + row_i**2
        + row_i * row_j
        + row_j**2
    )

    projection_records: list[dict[str, Any]] = []
    for gain_sum, imaginary_sign in ((1, 1), (2, -1)):
        imaginary_part = (
            imaginary_sign * (2 * projection_j + projection_i) / sp.sqrt(3)
        )
        modulus_residual = sp.factor(
            projection_i**2 + imaginary_part**2 - u * v
        )
        projection_records.append(
            {
                "gain_sum_mod_3": gain_sum,
                "imaginary_part": str(imaginary_part),
                "modulus_residual": str(modulus_residual),
                "residual_is_pair_polynomial_over_three": sp.simplify(
                    modulus_residual - pair_polynomial / 3
                )
                == 0,
            }
        )

    quadratic_i = 3 * u**2 - 3 * u * row_i + row_i**2
    quadratic_j = 3 * v**2 - 3 * v * row_j + row_j**2
    bilinear_matrix = sp.Matrix(
        (
            (3, -3, 0, 0),
            (-3, 1, 0, 0),
            (0, 0, 0, 1),
            (0, 0, 1, 0),
        )
    )
    vector_i = sp.Matrix((u, row_i, quadratic_i, 1))
    vector_j = sp.Matrix((v, row_j, quadratic_j, 1))
    bilinear_pair = sp.factor((vector_i.T * bilinear_matrix * vector_j)[0])
    diagonal = sp.factor((vector_i.T * bilinear_matrix * vector_i)[0])

    top_block = bilinear_matrix[:2, :2]
    bottom_block = bilinear_matrix[2:, 2:]
    same_type_one = sp.factor(pair_polynomial.subs({row_i: u, row_j: v}))
    same_type_three = sp.factor(
        pair_polynomial.subs({row_i: 3 * u, row_j: 3 * v})
    )

    phase_cosines = {
        "row_equals_orbit_radius": str(sp.simplify((2 * u - u) / (2 * u))),
        "row_equals_three_orbit_radii": str(
            sp.simplify((2 * u - 3 * u) / (2 * u))
        ),
    }

    report = {
        "schema": SCHEMA,
        "trust": "LEMMA_EXACT_ALGEBRA_REPLAY_REVIEW_PENDING",
        "claim_scope": CLAIM_SCOPE,
        "pair_polynomial": str(pair_polynomial),
        "projection_records": projection_records,
        "all_nonreciprocal_projection_reductions_exact": all(
            record["residual_is_pair_polynomial_over_three"]
            for record in projection_records
        ),
        "bilinear_matrix": [
            [str(entry) for entry in row] for row in bilinear_matrix.tolist()
        ],
        "bilinear_pair": str(bilinear_pair),
        "bilinear_pair_is_pair_polynomial": sp.simplify(
            bilinear_pair - pair_polynomial
        )
        == 0,
        "bilinear_determinant": str(sp.factor(bilinear_matrix.det())),
        "top_block_determinant": str(sp.factor(top_block.det())),
        "bottom_block_determinant": str(sp.factor(bottom_block.det())),
        "signature_is_two_two": bool(
            top_block.det() < 0 and bottom_block.det() < 0
        ),
        "diagonal_factorization": "3*(row_i - u)*(row_i - 3*u)",
        "diagonal_factorization_exact": sp.simplify(
            diagonal - 3 * (row_i - u) * (row_i - 3 * u)
        )
        == 0,
        "same_type_row_equals_u": str(same_type_one),
        "same_type_row_equals_three_u": str(same_type_three),
        "same_type_exceptional_factors_exact": (
            sp.simplify(same_type_one - (u - v) ** 2) == 0
            and sp.simplify(same_type_three - 3 * (u - v) ** 2) == 0
        ),
        "exceptional_phase_cosines": phase_cosines,
        "row_u_forces_half_step_cosine": phase_cosines[
            "row_equals_orbit_radius"
        ]
        == "1/2",
        "row_three_u_forces_aligned_cosine": phase_cosines[
            "row_equals_three_orbit_radii"
        ]
        == "-1/2",
        "gain_pair_count_closed": 2**10,
        "remaining_cases": [
            "at least one reciprocal mutual gain-pair",
            "mixed own-pair and four-cross-singleton rows",
            "half-step orbit pairs",
            "arbitrary non-orbit configurations",
        ],
    }

    required = (
        "all_nonreciprocal_projection_reductions_exact",
        "bilinear_pair_is_pair_polynomial",
        "signature_is_two_two",
        "diagonal_factorization_exact",
        "same_type_exceptional_factors_exact",
        "row_u_forces_half_step_cosine",
        "row_three_u_forces_aligned_cosine",
    )
    for field in required:
        if not report[field]:
            raise AssertionError(f"unexpected symbolic identity: {field}")
    return report
