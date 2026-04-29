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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--t", type=int, default=2, help="positive integer with m=4t")
    parser.add_argument("--json", action="store_true", help="print JSON")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument(
        "--verify-all-rows",
        action="store_true",
        help="also verify all selected row distances and alternating turns",
    )
    args = parser.parse_args()

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
