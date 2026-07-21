#!/usr/bin/env python3
"""Check the reciprocal-radial middle-witness budget packet."""

from __future__ import annotations

import argparse
import json

from erdos97.reciprocal_radial_budget import smoke_report

def assert_expected(report: dict[str, object], tolerance: float) -> None:
    pentagon = report["pentagon_tight_example"]
    if not isinstance(pentagon, dict):
        raise AssertionError("malformed pentagon section")
    max_abs_margin = float(pentagon["max_abs_margin"])
    if max_abs_margin > tolerance:
        raise AssertionError(
            f"pentagon tightness drifted: {max_abs_margin} > {tolerance}"
        )

    jump = report["jump_formula_affine_circle"]
    if not isinstance(jump, dict):
        raise AssertionError("malformed jump-formula section")
    max_abs_error = float(jump["max_abs_error"])
    if max_abs_error > tolerance:
        raise AssertionError(
            f"jump formula error too large: {max_abs_error} > {tolerance}"
        )
    if float(jump["min_visible_denominator"]) <= 0:
        raise AssertionError("expected positive visible denominators")
    if float(jump["min_exterior_turn_cross"]) <= 0:
        raise AssertionError("expected positive exterior turns")
    if float(jump["min_convex_left_turn"]) <= 0:
        raise AssertionError("affine-circle control is not strictly convex")


def print_summary(report: dict[str, object]) -> None:
    pentagon = report["pentagon_tight_example"]
    jump = report["jump_formula_affine_circle"]
    if not isinstance(pentagon, dict) or not isinstance(jump, dict):
        raise TypeError("malformed reciprocal-radial smoke report")

    print("reciprocal-radial budget smoke check")
    print(f"trust: {report['trust']}")
    print(f"scope: {report['claim_scope']}")
    print(
        "pentagon tight example max |rhs-lhs|: "
        f"{float(pentagon['max_abs_margin']):.3e}"
    )
    print(
        "jump formula affine-circle max error: "
        f"{float(jump['max_abs_error']):.3e}"
    )
    print(
        "minimum visible denominator / turn: "
        f"{float(jump['min_visible_denominator']):.3e} / "
        f"{float(jump['min_exterior_turn_cross']):.3e}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print JSON output")
    parser.add_argument(
        "--assert-expected",
        action="store_true",
        help="assert the deterministic smoke checks match expectations",
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=1e-11,
        help="floating tolerance for deterministic smoke checks",
    )
    args = parser.parse_args()

    report = smoke_report()
    if args.assert_expected:
        assert_expected(report, args.tolerance)

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_summary(report)
        if args.assert_expected:
            print("OK: reciprocal-radial budget smoke checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
