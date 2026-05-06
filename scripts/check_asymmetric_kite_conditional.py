#!/usr/bin/env python3
"""Check the review-pending asymmetric-kite algebraic identities.

This is a verifier for a conditional Selection Lemma subcase note, not a
general proof of Erdos Problem #97.  It checks the exact cross-product
factorizations used in the asymmetric-kite memo and runs a deterministic
sign sweep inside the stated parameter box.  The remaining cyclic-order
completeness and mirror-case audit are documented separately.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from typing import Any

import sympy as sp


def left_turn(prev: sp.Matrix, mid: sp.Matrix, succ: sp.Matrix) -> sp.Expr:
    """Return the signed two-dimensional cross product at ``mid``."""
    a = mid - prev
    b = succ - mid
    return sp.simplify(a[0] * b[1] - a[1] * b[0])


def identity_differences() -> dict[str, sp.Expr]:
    """Return raw-minus-factored differences for the four local formulas."""
    c = sp.Symbol("c", positive=True)
    alpha_i = sp.Symbol("alpha_i", positive=True)
    alpha_j = sp.Symbol("alpha_j", positive=True)
    a_angle = sp.Symbol("A", positive=True)
    b_angle = sp.Symbol("B", positive=True)
    b_1 = sp.Symbol("B_1", positive=True)
    b_2 = sp.Symbol("B_2", positive=True)

    r_i = c / sp.sin(alpha_i)
    r_j = c / sp.sin(alpha_j)
    h_i = c * sp.cos(alpha_i) / sp.sin(alpha_i)
    h_j = c * sp.cos(alpha_j) / sp.sin(alpha_j)

    p = sp.Matrix([-c, 0])
    v_j = sp.Matrix([0, -h_j])
    x_left = sp.Matrix([
        -r_i * sp.sin(a_angle),
        h_i - r_i * sp.cos(a_angle),
    ])
    y_left = sp.Matrix([
        -r_j * sp.sin(b_angle),
        -h_j + r_j * sp.cos(b_angle),
    ])
    y_left_1 = sp.Matrix([
        -r_j * sp.sin(b_1),
        -h_j + r_j * sp.cos(b_1),
    ])
    y_left_2 = sp.Matrix([
        -r_j * sp.sin(b_2),
        -h_j + r_j * sp.cos(b_2),
    ])

    lt_x1 = left_turn(x_left, p, y_left)
    lt_x1_factored = (
        -4
        * c**2
        * sp.sin((b_angle - alpha_j) / 2)
        * sp.sin((a_angle - alpha_i) / 2)
        * sp.sin((a_angle + b_angle + alpha_i + alpha_j) / 2)
        / (sp.sin(alpha_i) * sp.sin(alpha_j))
    )

    lt_x2 = left_turn(x_left, p, v_j)
    lt_x2_factored = (
        -2
        * c**2
        * sp.cos((a_angle + alpha_i + 2 * alpha_j) / 2)
        * sp.sin((a_angle - alpha_i) / 2)
        / (sp.sin(alpha_i) * sp.sin(alpha_j))
    )

    lt_x3 = left_turn(y_left_1, p, y_left_2)
    lt_x3_factored = (
        -4
        * c**2
        * sp.sin((b_2 - b_1) / 2)
        * sp.sin((b_2 - alpha_j) / 2)
        * sp.sin((b_1 - alpha_j) / 2)
        / sp.sin(alpha_j) ** 2
    )

    lt_x4 = left_turn(y_left, p, v_j)
    lt_x4_factored = -c**2 * sp.sin(b_angle - alpha_j) / sp.sin(alpha_j) ** 2

    return {
        "LT_X1": sp.simplify(lt_x1 - lt_x1_factored),
        "LT_X2": sp.simplify(lt_x2 - lt_x2_factored),
        "LT_X3": sp.simplify(lt_x3 - lt_x3_factored),
        "LT_X4": sp.simplify(lt_x4 - lt_x4_factored),
    }


def verify_identities() -> dict[str, bool]:
    return {name: diff == 0 for name, diff in identity_differences().items()}


def _lt_values(alpha_i: float, alpha_j: float, a_angle: float, b_angle: float) -> dict[str, float]:
    c = 1.0
    return {
        "LT_X1": (
            -4
            * c**2
            * math.sin((b_angle - alpha_j) / 2)
            * math.sin((a_angle - alpha_i) / 2)
            * math.sin((a_angle + b_angle + alpha_i + alpha_j) / 2)
            / (math.sin(alpha_i) * math.sin(alpha_j))
        ),
        "LT_X2": (
            -2
            * c**2
            * math.cos((a_angle + alpha_i + 2 * alpha_j) / 2)
            * math.sin((a_angle - alpha_i) / 2)
            / (math.sin(alpha_i) * math.sin(alpha_j))
        ),
        "LT_X4": -c**2 * math.sin(b_angle - alpha_j) / math.sin(alpha_j) ** 2,
    }


def sign_sweep() -> dict[str, Any]:
    """Sample the strict interior of the assumed asymmetric-kite box."""
    alpha_pairs = [
        (0.05, 0.04),
        (0.10, 0.05),
        (0.20, 0.10),
        (0.30, 0.20),
        (0.40, 0.20),
        (0.50, 0.10),
        (0.50, 0.49),
        (0.52, 0.01),
    ]
    tested = 0
    violations: list[dict[str, float | str]] = []

    for alpha_i, alpha_j in alpha_pairs:
        if not (0 < alpha_j <= alpha_i < math.pi / 6):
            continue
        a_values = [
            3 * alpha_i + 0.01,
            3 * alpha_i + (math.pi - 6 * alpha_i) / 2,
            math.pi - 3 * alpha_i - 0.01,
        ]
        b_values = [
            3 * alpha_j + 0.01,
            3 * alpha_j + (math.pi - 6 * alpha_j) / 2,
            math.pi - 3 * alpha_j - 0.01,
        ]

        for a_angle, b_angle in itertools.product(a_values, b_values):
            values = _lt_values(alpha_i, alpha_j, a_angle, b_angle)
            tested += len(values)
            for name, value in values.items():
                if value >= 0:
                    violations.append({
                        "formula": name,
                        "alpha_i": alpha_i,
                        "alpha_j": alpha_j,
                        "A": a_angle,
                        "B": b_angle,
                        "value": value,
                    })

        for b_1, b_2 in itertools.product(b_values, b_values):
            if b_2 - b_1 < 2 * alpha_j - 1e-12:
                continue
            value = (
                -4
                * math.sin((b_2 - b_1) / 2)
                * math.sin((b_2 - alpha_j) / 2)
                * math.sin((b_1 - alpha_j) / 2)
                / math.sin(alpha_j) ** 2
            )
            tested += 1
            if value >= 0:
                violations.append({
                    "formula": "LT_X3",
                    "alpha_i": alpha_i,
                    "alpha_j": alpha_j,
                    "B_1": b_1,
                    "B_2": b_2,
                    "value": value,
                })

    return {
        "sampled_formula_evaluations": tested,
        "violations": violations,
    }


def build_summary() -> dict[str, Any]:
    identity_checks = verify_identities()
    sweep = sign_sweep()
    return {
        "status": "CONDITIONAL_REVIEW_PENDING",
        "claim_scope": (
            "Asymmetric-kite algebraic identities and sampled sign guardrails only; "
            "cyclic-order completeness, mirror-case reduction, noncrossing, and the "
            "global Erdos #97 problem remain open."
        ),
        "identity_checks": identity_checks,
        "all_identities_verified": all(identity_checks.values()),
        "sign_sweep": sweep,
        "sign_sweep_has_no_violations": not sweep["violations"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit machine-readable summary")
    args = parser.parse_args()

    summary = build_summary()
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("status:", summary["status"])
        print("identity checks:", summary["identity_checks"])
        print("sampled formula evaluations:", summary["sign_sweep"]["sampled_formula_evaluations"])
        print("sign-sweep violations:", len(summary["sign_sweep"]["violations"]))
        print("claim scope:", summary["claim_scope"])

    if not summary["all_identities_verified"] or not summary["sign_sweep_has_no_violations"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
