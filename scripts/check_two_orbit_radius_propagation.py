#!/usr/bin/env python3
"""Check the exact two-orbit radius-propagation obstruction."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.two_orbit_radius_propagation import (  # noqa: E402
    alternating_turns,
    linearized_escape_summary,
    linearized_escape_to_json,
    selected_distance_residuals,
    summary_to_json,
    two_orbit_summary,
)


def _is_zero(value: object) -> bool:
    import sympy as sp

    return sp.simplify(value) == 0


def _is_positive(value: object) -> bool:
    import sympy as sp

    simplified = sp.simplify(value)
    if simplified.is_positive is True:
        return True
    if simplified.is_positive is False:
        return False
    return bool(sp.N(simplified, 80) > 0)


def assert_expected(t: int, *, verify_all_rows: bool) -> None:
    summary = two_orbit_summary(t)
    if not _is_zero(summary.distance_equation):
        raise AssertionError("forced ratio does not satisfy x^2+2x sin(h)-1=0")
    if not _is_zero(summary.a_distance_gap):
        raise AssertionError("A-row selected distances are not equal")
    if not _is_zero(summary.b_distance_gap):
        raise AssertionError("B-row selected distances are not equal")
    if not _is_positive(summary.cos_minus_ratio):
        raise AssertionError("expected forced ratio below cos(h)")
    if not _is_positive(-summary.turn_at_b):
        raise AssertionError("expected B-turn to be negative")
    if not _is_positive(summary.turn_at_a):
        raise AssertionError("expected A-turn to be positive")
    if not summary.forced_concave:
        raise AssertionError("summary should report forced concavity")

    if verify_all_rows:
        for residuals in selected_distance_residuals(t):
            for residual in residuals:
                if not _is_zero(residual):
                    raise AssertionError(
                        f"selected squared-distance residual is nonzero: {residual}"
                    )
        turns = alternating_turns(t)
        if not any(_is_positive(-turn) for turn in turns):
            raise AssertionError("expected at least one negative alternating turn")


def assert_linearized_escape(t: int) -> None:
    summary = linearized_escape_summary(t)
    if summary.status != "LINEARIZED_ESCAPE_FOUND":
        raise AssertionError(f"expected a linearized escape for t={t}")
    if summary.min_concave_turn_derivative is None:
        raise AssertionError("missing turn derivative")
    if summary.min_concave_turn_derivative < summary.derivative_floor - 1e-8:
        raise AssertionError("linearized escape does not meet derivative floor")
    if summary.max_abs_equality_jacobian_residual is None:
        raise AssertionError("missing equality residual")
    if summary.max_abs_equality_jacobian_residual > 1e-8:
        raise AssertionError("linearized escape does not preserve equalities")


def print_summary(t: int) -> None:
    summary = two_orbit_summary(t)
    print("t  m  n  distance_eq  A_gap  B_gap  turn_B<0  turn_A>0  forced_concave")
    print(
        f"{summary.t}  {summary.m}  {summary.n}  "
        f"{summary.distance_equation}  {summary.a_distance_gap}  "
        f"{summary.b_distance_gap}  {_is_positive(-summary.turn_at_b)}  "
        f"{_is_positive(summary.turn_at_a)}  {summary.forced_concave}"
    )
    print(f"S/R = {summary.ratio}")
    print(f"cos(h) - S/R = {summary.cos_minus_ratio}")


def print_linearized_escape_summary(t: int, *, t_max: int | None) -> None:
    rows = [
        linearized_escape_summary(current_t)
        for current_t in range(t, (t_max or t) + 1)
    ]
    print(
        "t  n  status                   rank  kernel  concave turns  min dturn  max |Jv|  l1"
    )
    for row in rows:
        min_derivative = (
            "-"
            if row.min_concave_turn_derivative is None
            else f"{row.min_concave_turn_derivative:.6g}"
        )
        residual = (
            "-"
            if row.max_abs_equality_jacobian_residual is None
            else f"{row.max_abs_equality_jacobian_residual:.3g}"
        )
        l1_norm = "-" if row.l1_norm is None else f"{row.l1_norm:.6g}"
        print(
            f"{row.t}  {row.n}  {row.status:<24}  "
            f"{row.equality_rank}  {row.kernel_dimension}  "
            f"{row.concave_turn_count}  {min_derivative}  {residual}  {l1_norm}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--t", type=int, default=2, help="positive integer with m=4t")
    parser.add_argument("--json", action="store_true", help="print JSON")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument(
        "--linearized-escape",
        action="store_true",
        help="run the numerical first-order escape LP instead of the exact ansatz summary",
    )
    parser.add_argument(
        "--t-max",
        type=int,
        help="with --linearized-escape, scan every t from --t through --t-max",
    )
    parser.add_argument(
        "--include-direction",
        action="store_true",
        help="include the LP direction in --linearized-escape JSON output",
    )
    parser.add_argument(
        "--assert-linearized-escape",
        action="store_true",
        help="assert that the selected t values have a linearized escape",
    )
    parser.add_argument(
        "--verify-all-rows",
        action="store_true",
        help="also verify all selected row distances and alternating turns",
    )
    args = parser.parse_args()

    if args.t_max is not None and args.t_max < args.t:
        raise SystemExit("--t-max must be at least --t")
    if args.assert_linearized_escape and not args.linearized_escape:
        raise SystemExit("--assert-linearized-escape requires --linearized-escape")

    if args.linearized_escape:
        t_values = range(args.t, (args.t_max or args.t) + 1)
        rows = [
            linearized_escape_to_json(
                linearized_escape_summary(
                    current_t,
                    include_direction=args.include_direction,
                )
            )
            for current_t in t_values
        ]
        if args.assert_linearized_escape:
            for current_t in t_values:
                assert_linearized_escape(current_t)
        if args.json:
            output: object = rows[0] if args.t_max is None else rows
            print(json.dumps(output, indent=2, sort_keys=True))
        else:
            print_linearized_escape_summary(args.t, t_max=args.t_max)
            if args.assert_linearized_escape:
                print("OK: linearized escape expectation verified")
        return 0

    if args.assert_expected:
        assert_expected(args.t, verify_all_rows=args.verify_all_rows)

    summary = two_orbit_summary(args.t)
    if args.json:
        print(json.dumps(summary_to_json(summary), indent=2, sort_keys=True))
    else:
        print_summary(args.t)
        if args.assert_expected:
            print("OK: two-orbit obstruction verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
