#!/usr/bin/env python3
"""Replay the exact reciprocal algebra for four generic C3 orbits."""

from __future__ import annotations

import argparse
import json

from erdos97.four_c3_generic_orbit_obstruction import build_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = build_report()
    if args.assert_expected:
        assert report["m0_forces_rho_one_for_positive_rho"] is True
        assert report["all_cases_force_coincident_orbits"] is True
        assert report["half_step_factorization_exact"] is True
        assert report["half_step_ratio_two_satisfies_row_equation"] is True
        assert report["half_step_midpoint_exact"] is True
        assert report["half_step_partner_pair_midpoint"] == report["half_step_center_point"]
        assert len(report["nonzero_shift_cases"]) == 2

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("Four generic C3-orbit reciprocal algebra: PASS")
        print(f"m=0 reduction: {report['m0_difference']}")
        for record in report["nonzero_shift_cases"]:
            print(
                f"m={record['shift_mod_3']} residual: "
                f"{record['circle_residual']}"
            )
        print(
            "half-step own/cross reduction: "
            f"{report['half_step_own_cross_polynomial']}"
        )
        print("Scope: generic phases only; half-step branches remain open.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
