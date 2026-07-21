#!/usr/bin/env python3
"""Check centered cap-cut and squared-chord constraints for a fixed pattern."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from erdos97.cap_cut_constraints import cap_cut_report
from erdos97.search import built_in_patterns

def parse_order(raw: str) -> list[int]:
    try:
        return [int(item.strip()) for item in raw.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid comma-separated order: {raw}") from exc


def print_summary(report: dict[str, object]) -> None:
    unit = report["unit_chain_superadditivity"]
    outer = report["outer_dominance"]
    print("cap-cut / squared-chord constraint report")
    print(f"n: {report['n']}")
    print(f"selected rows: {report['selected_row_count']}")
    print(f"selected triple inequalities: {report['selected_superadditivity_row_count']}")
    print(f"chain inequalities: {report['chain_superadditivity_row_count']}")
    print(f"cap-cut inequalities: {report['cap_cut_row_count']}")
    print(f"unit-chain status: {unit['status']}")
    print(f"outer-dominant pairs: {outer['outer_dominant_pair_count']}")
    print(
        "pair-cap-compatible outer-dominant types: "
        f"{outer['pair_cap_compatible_outer_dominant_types']}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pattern", required=True, help="built-in pattern name")
    parser.add_argument(
        "--order",
        type=parse_order,
        help="comma-separated cyclic order; defaults to natural label order",
    )
    parser.add_argument(
        "--no-cap-cuts",
        action="store_true",
        help="omit general nonselected cap-cut inequalities from the report",
    )
    parser.add_argument("--json", action="store_true", help="print JSON")
    parser.add_argument("--write-certificate", help="write JSON report to this path")
    parser.add_argument(
        "--assert-unit-obstructed",
        action="store_true",
        help="assert that unit chain-superadditivity already obstructs the pattern",
    )
    args = parser.parse_args()

    patterns = built_in_patterns()
    if args.pattern not in patterns:
        raise SystemExit(f"unknown pattern {args.pattern}; known: {', '.join(patterns)}")
    pattern = patterns[args.pattern]
    report = cap_cut_report(
        pattern.S,
        args.order,
        include_cap_cuts=not args.no_cap_cuts,
    )

    if args.assert_unit_obstructed:
        unit = report["unit_chain_superadditivity"]
        if unit["obstructed"] is not True:
            raise AssertionError("expected unit chain-superadditivity obstruction")

    if args.write_certificate:
        path = Path(args.write_certificate)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_summary(report)
        if args.assert_unit_obstructed:
            print("OK: unit obstruction expectation verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
