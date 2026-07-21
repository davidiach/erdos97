#!/usr/bin/env python3
"""Replay members of the scalable abstract strict-cycle bridge control."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.scalable_strict_cycle_control import (  # noqa: E402
    assert_expected_structure,
    build_report,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--k",
        action="append",
        type=int,
        help="family parameter; may be repeated and defaults to 8 and 9",
    )
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    parameters = args.k if args.k is not None else [8, 9]
    reports = [build_report(k) for k in parameters]
    if args.assert_expected:
        for report in reports:
            assert_expected_structure(report)

    payload = {
        "status": "EXACT_ABSTRACT_SCALABLE_NEGATIVE_CONTROL",
        "claim_scope": (
            "The checked circulant selected-row systems satisfy the listed "
            "abstract bridge axioms, have no Kalmanson self-edge or primitive "
            "inverse pair, and have shortest vertex-circle strict cycle n. "
            "The first member does have a four-inequality Kalmanson circuit. "
            "The systems are not Euclidean realizations or counterexamples."
        ),
        "reports": [report.to_dict() for report in reports],
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("scalable strict-cycle bridge control")
        for report in reports:
            print(
                f"k={report.k}, n={report.n}: max-intersection="
                f"{report.maximum_row_intersection}, hinges={report.hinge_count}, "
                f"Kalmanson-self-edges={report.kalmanson_self_edge_count}, "
                "primitive-inverse-orbits="
                f"{report.kalmanson_primitive_inverse_orbit_count}, "
                f"shortest-cycle={report.shortest_strict_cycle}"
            )
        if args.assert_expected:
            print("OK: closed-form structure verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
