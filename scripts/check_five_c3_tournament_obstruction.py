#!/usr/bin/env python3
"""Replay the exact five-C3 tournament product obstruction."""

from __future__ import annotations

import argparse
import json

from erdos97.five_c3_tournament_obstruction import build_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = build_report()
    if args.assert_expected:
        assert report["gain_quotient_case_count"] == 729
        assert report["all_primitive_factorizations_exact"] is True
        assert report["zero_gain_conjugation_factor_exact"] is True
        assert report["radius_factorization_exact"] is True
        assert report["case_count_closed_by_one_product_argument"] is True

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("Five-C3 regular-tournament product obstruction: PASS")
        print(f"gain quotient cases: {report['gain_quotient_case_count']}")
        for record in report["primitive_gain_records"]:
            print(
                f"gain {record['gain_mod_3']} factor: "
                f"{record['expected_parameter_factor']}"
            )
        print(f"zero-gain factor: {report['zero_gain_conjugation_numerator']}")
        print(f"radius factor: {report['radius_inequality_polynomial']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
