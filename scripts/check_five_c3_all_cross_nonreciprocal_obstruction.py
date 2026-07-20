#!/usr/bin/env python3
"""Replay the exact five-C3 all-cross nonreciprocal obstruction."""

from __future__ import annotations

import argparse
import json

from erdos97.five_c3_all_cross_nonreciprocal_obstruction import build_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = build_report()
    if args.assert_expected:
        assert report["all_nonreciprocal_projection_reductions_exact"] is True
        assert report["bilinear_pair_is_pair_polynomial"] is True
        assert report["signature_is_two_two"] is True
        assert report["diagonal_factorization_exact"] is True
        assert report["same_type_exceptional_factors_exact"] is True
        assert report["gain_pair_count_closed"] == 1024

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("Five-C3 all-cross nonreciprocal obstruction: PASS")
        print(f"gain-pair patterns closed: {report['gain_pair_count_closed']}")
        print(f"pair polynomial: {report['pair_polynomial']}")
        print(f"bilinear determinant: {report['bilinear_determinant']}")
        print(f"diagonal: {report['diagonal_factorization']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
