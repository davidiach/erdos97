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
    alternating_decagon_crossing_search,
    alternating_turns,
    alternating_two_radius_family_summary,
    alternating_two_radius_family_to_json,
    concentric_outside_hull_summary,
    concentric_outside_hull_to_json,
    cyclic_crossing_search_to_json,
    linearized_escape_summary,
    linearized_escape_to_json,
    radius_ratio_summary,
    radius_ratio_to_json,
    selected_distance_residuals,
    summary_to_json,
    symmetric_two_orbit_reduction_summary,
    symmetric_two_orbit_reduction_to_json,
    two_orbit_summary,
)


def _is_zero(value: object) -> bool:
    import sympy as sp

    simplified = sp.simplify(value)
    return simplified == 0 or simplified.equals(0) is True


def _is_positive(value: object) -> bool:
    import sympy as sp

    simplified = sp.simplify(value)
    if simplified.is_positive is True:
        return True
    if simplified.is_positive is False:
        return False
    return False


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


def assert_alternating_family(m: int) -> None:
    summary = alternating_two_radius_family_summary(m)
    if summary.status != "exact_family_obstruction_not_general_proof":
        raise AssertionError(f"unexpected alternating-family status for m={m}")
    if not summary.all_gap_certificates_positive:
        raise AssertionError(f"not all adjacent gap certificates are positive for m={m}")


def assert_decagon_crossing() -> None:
    summary = alternating_decagon_crossing_search()
    if summary.status != "NO_CYCLIC_ORDER":
        raise AssertionError(f"unexpected decagon crossing status: {summary.status}")
    if summary.constraint_count != 30:
        raise AssertionError(f"unexpected decagon constraint count: {summary.constraint_count}")
    if summary.normalized_order_count != 181_440:
        raise AssertionError(
            f"unexpected normalized order count: {summary.normalized_order_count}"
        )


def assert_radius_ratio(k: int) -> None:
    summary = radius_ratio_summary(k)
    if summary.status != "exact_necessary_radius_bound_not_general_proof":
        raise AssertionError(f"unexpected radius-ratio status for k={k}")
    if not summary.positive_factor:
        raise AssertionError(f"expected cos(pi/{k}) to be positive")


def assert_symmetric_two_orbit_reduction(k: int) -> None:
    summary = symmetric_two_orbit_reduction_summary(k)
    expected = "exact_reduction_to_alternating_family_obstruction_not_general_proof"
    if summary.status != expected:
        raise AssertionError(f"unexpected symmetric reduction status for k={k}")
    if summary.witness_split != (2, 2):
        raise AssertionError(f"unexpected witness split for k={k}")
    if not summary.reduces_to_alternating_family:
        raise AssertionError(f"expected alternating-family reduction for k={k}")
    if not summary.all_gap_certificates_positive:
        raise AssertionError(f"expected positive gap certificates for k={k}")


def assert_concentric_outside_hull(circle_count: int) -> None:
    summary = concentric_outside_hull_summary(circle_count)
    if circle_count <= 3:
        expected = "exact_exterior_center_obstruction_not_general_proof"
        if summary.status != expected:
            raise AssertionError(
                f"unexpected exterior-center status for {circle_count} circles"
            )
        if not summary.extreme_pair_obstruction:
            raise AssertionError("expected angular-extreme pair obstruction")
    elif summary.status != "not_covered_by_three_circle_pigeonhole":
        raise AssertionError(f"unexpected non-covered status: {summary.status}")


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


def print_alternating_family_summary(m: int, *, m_max: int | None) -> None:
    rows = [
        alternating_two_radius_family_summary(current_m)
        for current_m in range(m, (m_max or m) + 1)
    ]
    print("m  n  status                                      gap certificates")
    for row in rows:
        print(
            f"{row.m}  {row.n}  {row.status:<42}  "
            f"{len(row.gap_certificates)} positive={row.all_gap_certificates_positive}"
        )


def print_decagon_crossing_summary() -> None:
    summary = alternating_decagon_crossing_search()
    print("alternating concave decagon crossing search")
    print(f"constraints: {summary.constraint_count}")
    print(f"normalized orders checked: {summary.normalized_order_count}")
    print(f"status: {summary.status}")


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


def print_radius_ratio_summary(k: int, *, k_max: int | None) -> None:
    rows = [radius_ratio_summary(current_k) for current_k in range(k, (k_max or k) + 1)]
    print("k  status                                           inradius factor")
    for row in rows:
        print(f"{row.k}  {row.status:<48}  {row.inradius_factor}")


def print_symmetric_two_orbit_reduction_summary(
    k: int,
    *,
    k_max: int | None,
) -> None:
    rows = [
        symmetric_two_orbit_reduction_summary(current_k)
        for current_k in range(k, (k_max or k) + 1)
    ]
    print("k  n  status                                                     small-k")
    for row in rows:
        print(
            f"{row.k}  {row.n}  {row.status:<58}  "
            f"{row.small_k_boundary_case}"
        )


def print_concentric_outside_hull_summary(circle_count: int) -> None:
    summary = concentric_outside_hull_summary(circle_count)
    print("concentric exterior-center obstruction")
    print(f"circle count: {summary.circle_count}")
    print(f"covered by lemma: {summary.covered_by_lemma}")
    print(f"status: {summary.status}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--t", type=int, default=2, help="positive integer with m=4t")
    parser.add_argument("--m", type=int, default=5, help="integer m >= 4 for alternating-family checks")
    parser.add_argument("--k", type=int, default=3, help="integer k >= 3 for C_k reduction checks")
    parser.add_argument("--circle-count", type=int, default=3, help="number of concentric circles")
    parser.add_argument("--json", action="store_true", help="print JSON")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument(
        "--alternating-family",
        action="store_true",
        help="check the broader alternating two-radius regular 2m-gon family",
    )
    parser.add_argument(
        "--m-max",
        type=int,
        help="with --alternating-family, scan every m from --m through --m-max",
    )
    parser.add_argument(
        "--assert-alternating-family",
        action="store_true",
        help="assert that selected alternating-family m values have positive gap certificates",
    )
    parser.add_argument(
        "--decagon-crossing",
        action="store_true",
        help="check cyclic-order crossings for the fixed concave alternating decagon pattern",
    )
    parser.add_argument(
        "--assert-decagon-crossing",
        action="store_true",
        help="assert the fixed concave decagon pattern has no cyclic order",
    )
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
        "--radius-ratio",
        action="store_true",
        help="check the regular-orbit radius-ratio necessary bound",
    )
    parser.add_argument(
        "--k-max",
        type=int,
        help="with --radius-ratio or --two-orbit-reduction, scan --k through --k-max",
    )
    parser.add_argument(
        "--assert-radius-ratio",
        action="store_true",
        help="assert the selected k values satisfy the radius-ratio certificate",
    )
    parser.add_argument(
        "--two-orbit-reduction",
        action="store_true",
        help="check the restricted C_k two-orbit reduction",
    )
    parser.add_argument(
        "--assert-two-orbit-reduction",
        action="store_true",
        help="assert the selected k values pass the two-orbit reduction check",
    )
    parser.add_argument(
        "--concentric-outside",
        action="store_true",
        help="check the at-most-three-circles exterior-center obstruction",
    )
    parser.add_argument(
        "--assert-concentric-outside",
        action="store_true",
        help="assert the exterior-center obstruction for --circle-count",
    )
    parser.add_argument(
        "--verify-all-rows",
        action="store_true",
        help="also verify all selected row distances and alternating turns",
    )
    args = parser.parse_args()

    if args.t_max is not None and args.t_max < args.t:
        raise SystemExit("--t-max must be at least --t")
    if args.m_max is not None and args.m_max < args.m:
        raise SystemExit("--m-max must be at least --m")
    if args.k_max is not None and args.k_max < args.k:
        raise SystemExit("--k-max must be at least --k")
    if args.assert_linearized_escape and not args.linearized_escape:
        raise SystemExit("--assert-linearized-escape requires --linearized-escape")
    if args.assert_alternating_family and not args.alternating_family:
        raise SystemExit("--assert-alternating-family requires --alternating-family")
    if args.assert_decagon_crossing and not args.decagon_crossing:
        raise SystemExit("--assert-decagon-crossing requires --decagon-crossing")
    if args.assert_radius_ratio and not args.radius_ratio:
        raise SystemExit("--assert-radius-ratio requires --radius-ratio")
    if args.assert_two_orbit_reduction and not args.two_orbit_reduction:
        raise SystemExit("--assert-two-orbit-reduction requires --two-orbit-reduction")
    if args.assert_concentric_outside and not args.concentric_outside:
        raise SystemExit("--assert-concentric-outside requires --concentric-outside")
    modes = [
        args.linearized_escape,
        args.alternating_family,
        args.decagon_crossing,
        args.radius_ratio,
        args.two_orbit_reduction,
        args.concentric_outside,
    ]
    if sum(bool(mode) for mode in modes) > 1:
        raise SystemExit("choose only one special mode")

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

    if args.alternating_family:
        m_values = range(args.m, (args.m_max or args.m) + 1)
        rows = [
            alternating_two_radius_family_to_json(
                alternating_two_radius_family_summary(current_m)
            )
            for current_m in m_values
        ]
        if args.assert_alternating_family:
            for current_m in m_values:
                assert_alternating_family(current_m)
        if args.json:
            output: object = rows[0] if args.m_max is None else rows
            print(json.dumps(output, indent=2, sort_keys=True))
        else:
            print_alternating_family_summary(args.m, m_max=args.m_max)
            if args.assert_alternating_family:
                print("OK: alternating-family expectation verified")
        return 0

    if args.radius_ratio:
        k_values = range(args.k, (args.k_max or args.k) + 1)
        rows = [radius_ratio_to_json(radius_ratio_summary(current_k)) for current_k in k_values]
        if args.assert_radius_ratio:
            for current_k in k_values:
                assert_radius_ratio(current_k)
        if args.json:
            output = rows[0] if args.k_max is None else rows
            print(json.dumps(output, indent=2, sort_keys=True))
        else:
            print_radius_ratio_summary(args.k, k_max=args.k_max)
            if args.assert_radius_ratio:
                print("OK: radius-ratio expectation verified")
        return 0

    if args.two_orbit_reduction:
        k_values = range(args.k, (args.k_max or args.k) + 1)
        rows = [
            symmetric_two_orbit_reduction_to_json(
                symmetric_two_orbit_reduction_summary(current_k)
            )
            for current_k in k_values
        ]
        if args.assert_two_orbit_reduction:
            for current_k in k_values:
                assert_symmetric_two_orbit_reduction(current_k)
        if args.json:
            output = rows[0] if args.k_max is None else rows
            print(json.dumps(output, indent=2, sort_keys=True))
        else:
            print_symmetric_two_orbit_reduction_summary(args.k, k_max=args.k_max)
            if args.assert_two_orbit_reduction:
                print("OK: two-orbit reduction expectation verified")
        return 0

    if args.concentric_outside:
        summary = concentric_outside_hull_summary(args.circle_count)
        if args.assert_concentric_outside:
            assert_concentric_outside_hull(args.circle_count)
        if args.json:
            print(
                json.dumps(
                    concentric_outside_hull_to_json(summary),
                    indent=2,
                    sort_keys=True,
                )
            )
        else:
            print_concentric_outside_hull_summary(args.circle_count)
            if args.assert_concentric_outside:
                print("OK: concentric exterior-center expectation verified")
        return 0

    if args.decagon_crossing:
        summary = alternating_decagon_crossing_search()
        if args.assert_decagon_crossing:
            assert_decagon_crossing()
        if args.json:
            print(json.dumps(cyclic_crossing_search_to_json(summary), indent=2, sort_keys=True))
        else:
            print_decagon_crossing_summary()
            if args.assert_decagon_crossing:
                print("OK: decagon crossing expectation verified")
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
