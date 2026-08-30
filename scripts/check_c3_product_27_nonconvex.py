#!/usr/bin/env python3
"""Exact checker for a 27-point C3 product negative control.

The checked configuration gives every point four named equidistant partners,
but only 18 of the 27 points are convex-hull vertices. It is therefore not a
counterexample to Erdos Problem #97.
"""

from __future__ import annotations

import argparse
import json
from itertools import product
from pathlib import Path
from typing import Any, Iterable

import sympy as sp

SCHEMA = "erdos97.c3_product_27_nonconvex.v1"
STATUS = "EXACT_NONCONVEX_NEGATIVE_CONTROL"
TRUST = "EXACT_CERTIFICATE_DIAGNOSTIC"
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT = ROOT / "data" / "certificates" / "c3_product_27_nonconvex.json"
CLAIM_SCOPE = (
    "Exact verification of one 27-point C3 product configuration in which "
    "every point has four named partners at one common center-dependent "
    "distance. Exactly 18 points are convex-hull vertices, so the object is "
    "not a counterexample to Erdos Problem #97. The checker does not classify "
    "other projective multiplier cycles or prove an obstruction to convexifying "
    "the product template."
)

SQRT3 = sp.sqrt(3)
RADICAND_A = -519 + 348 * SQRT3
RADICAND_B = -761 + 488 * SQRT3
RADICAL_A = sp.sqrt(RADICAND_A)
RADICAL_B = sp.sqrt(RADICAND_B)

# Lower real roots of the displayed projective-cycle quadratics.
U_A_EXPR = (18 - 6 * SQRT3 - 2 * RADICAL_A) / (2 * (-75 + 44 * SQRT3))
U_B_EXPR = (32 - 16 * SQRT3 - 4 * RADICAL_B) / (2 * (-162 + 96 * SQRT3))

FIELD = sp.QQ.algebraic_field(
    SQRT3,
    RADICAL_A,
    RADICAL_B,
    alias="alpha",
)

Scalar = Any
Point = tuple[Scalar, Scalar]
CycleLabel = tuple[int, int]
ProductLabel = tuple[int, int, int]

ZERO = FIELD.zero
ONE = FIELD.one
THREE = FIELD.convert(3)
HALF = FIELD.convert(sp.Rational(1, 2))
SQRT3_K = FIELD.from_sympy(SQRT3)
OMEGA: Point = (-HALF, SQRT3_K * HALF)
UNIT: Point = (ONE, ZERO)

FACTOR_A_HULL: tuple[CycleLabel, ...] = (
    (1, 1),
    (0, 2),
    (2, 0),
    (1, 2),
    (0, 0),
    (2, 1),
    (1, 0),
    (0, 1),
    (2, 2),
)
FACTOR_B_HULL: tuple[CycleLabel, ...] = (
    (2, 2),
    (1, 1),
    (0, 2),
    (2, 0),
    (1, 2),
    (0, 0),
    (2, 1),
    (1, 0),
    (0, 1),
)
PRODUCT_HULL: tuple[ProductLabel, ...] = (
    (1, 1, 0),
    (1, 0, 1),
    (0, 1, 1),
    (2, 2, 0),
    (2, 1, 2),
    (1, 2, 2),
    (1, 1, 1),
    (1, 0, 2),
    (0, 1, 2),
    (2, 2, 1),
    (2, 1, 0),
    (1, 2, 0),
    (1, 1, 2),
    (1, 0, 0),
    (0, 1, 0),
    (2, 2, 2),
    (2, 1, 1),
    (1, 2, 1),
)


def add(left: Point, right: Point) -> Point:
    return (left[0] + right[0], left[1] + right[1])


def subtract(left: Point, right: Point) -> Point:
    return (left[0] - right[0], left[1] - right[1])


def multiply(left: Point, right: Point) -> Point:
    return (
        left[0] * right[0] - left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def reciprocal(value: Point) -> Point:
    denominator = norm_squared(value)
    return (value[0] / denominator, -value[1] / denominator)


def norm_squared(value: Point) -> Scalar:
    return value[0] * value[0] + value[1] * value[1]


def squared_distance(left: Point, right: Point) -> Scalar:
    return norm_squared(subtract(left, right))


def orientation(a: Point, b: Point, c: Point) -> Scalar:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (
        c[0] - a[0]
    )


def is_positive(value: Scalar) -> bool:
    """Return the exact sign in the radicals' selected real embedding."""

    return FIELD.to_sympy(value).is_positive is True


def omega_power(power: int) -> Point:
    result = UNIT
    for _ in range(power % 3):
        result = multiply(result, OMEGA)
    return result


def circle_multiplier(parameter: Scalar) -> Point:
    """Parametrize the circle ``|lambda - 1|^2 = 3`` exactly."""

    denominator = ONE + parameter * parameter
    return (
        ONE + SQRT3_K * (ONE - parameter * parameter) / denominator,
        2 * SQRT3_K * parameter / denominator,
    )


def projective_cycle(
    first_parameter: int,
    second_parameter_expr: sp.Expr,
) -> tuple[tuple[Point, Point, Point], tuple[Point, Point, Point]]:
    """Return representatives and multipliers with monodromy ``omega``."""

    first = circle_multiplier(FIELD.convert(first_parameter))
    second = circle_multiplier(FIELD.from_sympy(second_parameter_expr))
    representatives = (UNIT, first, multiply(first, second))
    third = multiply(OMEGA, reciprocal(representatives[2]))
    return representatives, (first, second, third)


def lifted_cycle_points(
    representatives: tuple[Point, Point, Point],
) -> dict[CycleLabel, Point]:
    return {
        (orbit, phase): multiply(representatives[orbit], omega_power(phase))
        for orbit, phase in product(range(3), repeat=2)
    }


def product_points(
    first: tuple[Point, Point, Point],
    second: tuple[Point, Point, Point],
) -> dict[ProductLabel, Point]:
    return {
        (i, j, phase): multiply(
            multiply(first[i], second[j]),
            omega_power(phase),
        )
        for i, j, phase in product(range(3), repeat=3)
    }


def product_witnesses(label: ProductLabel) -> tuple[ProductLabel, ...]:
    i, j, phase = label
    first_successor = (
        (i + 1, j, phase) if i < 2 else (0, j, (phase + 1) % 3)
    )
    second_successor = (
        (i, j + 1, phase) if j < 2 else (i, 0, (phase + 1) % 3)
    )
    return (
        (i, j, (phase + 1) % 3),
        (i, j, (phase + 2) % 3),
        first_successor,
        second_successor,
    )


def cycle_witnesses(label: CycleLabel) -> tuple[CycleLabel, ...]:
    orbit, phase = label
    successor = (
        (orbit + 1, phase) if orbit < 2 else (0, (phase + 1) % 3)
    )
    return (
        (orbit, (phase + 1) % 3),
        (orbit, (phase + 2) % 3),
        successor,
    )


def strict_hull_errors(
    points: dict[Any, Point],
    hull: Iterable[Any],
    name: str,
) -> list[str]:
    """Check an asserted counterclockwise strict hull in exact arithmetic."""

    hull_labels = tuple(hull)
    errors: list[str] = []
    if len(set(hull_labels)) != len(hull_labels):
        errors.append(f"{name}: repeated hull label")
        return errors
    for index, left_label in enumerate(hull_labels):
        right_label = hull_labels[(index + 1) % len(hull_labels)]
        left = points[left_label]
        right = points[right_label]
        for label, point in points.items():
            if label in {left_label, right_label}:
                continue
            turn = orientation(left, right, point)
            if not is_positive(turn):
                errors.append(
                    f"{name}: {label!r} is not strictly left of edge "
                    f"{left_label!r}->{right_label!r}"
                )
    return errors


def _float(value: Scalar) -> float:
    return float(sp.N(FIELD.to_sympy(value), 17))


def build_payload() -> dict[str, Any]:
    """Build and exactly validate the construction summary."""

    errors: list[str] = []
    first_representatives, first_multipliers = projective_cycle(2, U_A_EXPR)
    second_representatives, second_multipliers = projective_cycle(3, U_B_EXPR)

    parameter_checks = (
        (-75 + 44 * SQRT3) * U_A_EXPR**2
        + (-18 + 6 * SQRT3) * U_A_EXPR
        - 33
        - 14 * SQRT3,
        (-162 + 96 * SQRT3) * U_B_EXPR**2
        + (-32 + 16 * SQRT3) * U_B_EXPR
        - 50
        - 16 * SQRT3,
    )
    for index, expression in enumerate(parameter_checks):
        if FIELD.from_sympy(sp.expand(expression)) != ZERO:
            errors.append(f"cycle parameter {index} fails its defining quadratic")

    for cycle_index, multipliers in enumerate(
        (first_multipliers, second_multipliers)
    ):
        multiplier_product = UNIT
        for multiplier in multipliers:
            circle_residual = squared_distance(multiplier, UNIT) - THREE
            if circle_residual != ZERO:
                errors.append(
                    f"cycle {cycle_index}: multiplier is not on |lambda-1|^2=3"
                )
            multiplier_product = multiply(multiplier_product, multiplier)
        if multiplier_product != OMEGA:
            errors.append(f"cycle {cycle_index}: monodromy is not omega")

    factor_a_points = lifted_cycle_points(first_representatives)
    factor_b_points = lifted_cycle_points(second_representatives)
    for name, factor_points in (
        ("factor A", factor_a_points),
        ("factor B", factor_b_points),
    ):
        for center_label, center in factor_points.items():
            radius = THREE * norm_squared(center)
            witnesses = cycle_witnesses(center_label)
            if any(
                squared_distance(center, factor_points[witness]) != radius
                for witness in witnesses
            ):
                errors.append(f"{name}: bad three-witness row at {center_label!r}")

    errors.extend(strict_hull_errors(factor_a_points, FACTOR_A_HULL, "factor A"))
    errors.extend(strict_hull_errors(factor_b_points, FACTOR_B_HULL, "factor B"))

    points = product_points(first_representatives, second_representatives)
    orbit_moduli = [
        norm_squared(multiply(first_representatives[i], second_representatives[j]))
        for i, j in product(range(3), repeat=2)
    ]
    if len(set(orbit_moduli)) != 9:
        errors.append("the nine product C3 orbits do not have distinct moduli")
    if not all(is_positive(value) for value in orbit_moduli):
        errors.append("a product orbit has nonpositive squared modulus")

    named_equalities = 0
    for center_label, center in points.items():
        witnesses = product_witnesses(center_label)
        if len(set(witnesses)) != 4 or center_label in witnesses:
            errors.append(f"invalid witness labels at {center_label!r}")
            continue
        radius = THREE * norm_squared(center)
        for witness in witnesses:
            named_equalities += 1
            if squared_distance(center, points[witness]) != radius:
                errors.append(
                    f"selected distance mismatch at {center_label!r}->{witness!r}"
                )

    errors.extend(strict_hull_errors(points, PRODUCT_HULL, "27-point product"))
    interior_labels = sorted(set(points) - set(PRODUCT_HULL))

    summary = {
        "factor_cycle_count": 2,
        "factor_point_counts": [len(factor_a_points), len(factor_b_points)],
        "factor_hull_vertex_counts": [len(FACTOR_A_HULL), len(FACTOR_B_HULL)],
        "factor_named_witness_count_per_center": 3,
        "cycle_monodromies": ["omega", "omega"],
        "product_point_count": len(points),
        "distinct_product_point_count": 27 if len(set(orbit_moduli)) == 9 else None,
        "product_named_witness_count_per_center": 4,
        "product_named_equality_count": named_equalities,
        "product_hull_vertex_count": len(PRODUCT_HULL),
        "product_hull_labels": [list(label) for label in PRODUCT_HULL],
        "product_interior_point_count": len(interior_labels),
        "product_interior_labels": [list(label) for label in interior_labels],
        "factor_hull_labels": {
            "A": [list(label) for label in FACTOR_A_HULL],
            "B": [list(label) for label in FACTOR_B_HULL],
        },
        "cycle_parameters_approx": {
            "A": [2.0, _float(FIELD.from_sympy(U_A_EXPR))],
            "B": [3.0, _float(FIELD.from_sympy(U_B_EXPR))],
        },
    }
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "provenance": {
            "generator": "scripts/check_c3_product_27_nonconvex.py",
            "command": (
                "python scripts/check_c3_product_27_nonconvex.py "
                "--write-artifact --assert-expected"
            ),
            "arithmetic": (
                "exact SymPy algebraic-number-field equality and selected-real-"
                "embedding sign checks"
            ),
        },
        "validation_status": "passed" if not errors else "failed",
        "errors": errors,
        "defining_quadratics": {
            "A": "(-75+44*sqrt(3))*u^2+(-18+6*sqrt(3))*u-33-14*sqrt(3)",
            "B": "(-162+96*sqrt(3))*u^2+(-32+16*sqrt(3))*u-50-16*sqrt(3)",
            "root_choice": "lower real root in both cases",
        },
        "summary": summary,
    }


def validate_payload(payload: dict[str, Any]) -> list[str]:
    errors = list(payload.get("errors", []))
    summary = payload.get("summary", {})
    expected = {
        "factor_point_counts": [9, 9],
        "factor_hull_vertex_counts": [9, 9],
        "factor_named_witness_count_per_center": 3,
        "cycle_monodromies": ["omega", "omega"],
        "product_point_count": 27,
        "distinct_product_point_count": 27,
        "product_named_witness_count_per_center": 4,
        "product_named_equality_count": 108,
        "product_hull_vertex_count": 18,
        "product_interior_point_count": 9,
    }
    for key, expected_value in expected.items():
        if summary.get(key) != expected_value:
            errors.append(
                f"summary[{key!r}]={summary.get(key)!r}, expected {expected_value!r}"
            )
    if "not a counterexample" not in payload.get("claim_scope", ""):
        errors.append("claim scope must retain the non-counterexample warning")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print JSON output")
    parser.add_argument(
        "--artifact",
        type=Path,
        default=DEFAULT_ARTIFACT,
        help="stored JSON certificate path",
    )
    parser.add_argument(
        "--write-artifact",
        action="store_true",
        help="write the regenerated exact certificate",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare the stored certificate with exact regeneration",
    )
    parser.add_argument(
        "--assert-expected",
        action="store_true",
        help="fail unless all exact checks and pinned summary values pass",
    )
    args = parser.parse_args()

    payload = build_payload()
    errors = validate_payload(payload)
    artifact_path = args.artifact
    if not artifact_path.is_absolute():
        artifact_path = ROOT / artifact_path
    if args.write_artifact:
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if args.check:
        if not artifact_path.exists():
            errors.append(f"missing artifact: {artifact_path}")
        else:
            stored = json.loads(artifact_path.read_text(encoding="utf-8"))
            if stored != payload:
                errors.append(f"stored artifact differs from regeneration: {artifact_path}")
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        summary = payload["summary"]
        print(f"validation: {payload['validation_status']}")
        print(f"points: {summary['product_point_count']}")
        print(f"hull vertices: {summary['product_hull_vertex_count']}")
        print(f"interior points: {summary['product_interior_point_count']}")
    if errors:
        for error in errors:
            print(error)
        return 1
    if args.assert_expected and payload["validation_status"] != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
