#!/usr/bin/env python3
"""Replay exact arithmetic for advanced radius-level proof candidates."""

from __future__ import annotations

import argparse
import json
from typing import Any

from erdos97.radius_level_advanced_arithmetic import (
    assert_expected_payload,
    payload,
)


def summary_payload(candidate: dict[str, Any]) -> dict[str, Any]:
    """Return the compact reviewer-facing fields."""

    compact = dict(candidate)
    compact.pop("weak_arc_cases", None)
    compact.pop("component_cycle_cases", None)
    return compact


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-cycle-length", type=int, default=128)
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--json", action="store_true")
    output.add_argument("--summary-json", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    candidate = payload(args.max_cycle_length)
    if args.assert_expected:
        assert_expected_payload(candidate)

    if args.summary_json:
        print(json.dumps(summary_payload(candidate), indent=2, sort_keys=True))
    elif args.json:
        print(json.dumps(candidate, indent=2, sort_keys=True))
    else:
        print("advanced radius-level arithmetic replay")
        print(f"weak-arc identity: {candidate['weak_arc_identity']}")
        print(
            "component-cycle first forbidden total path length: "
            f"{candidate['component_cycle_first_forbidden_total_path_length']}"
        )
        print(
            "forced internal path angle: "
            f"{candidate['linear_forest_angle']['forced_angle_radians']}"
        )
        print(
            "triple-fan-in descent factor: "
            f"{candidate['triple_fanin_radius_descent']['positive_threshold']}"
        )
        if args.assert_expected:
            print("OK: advanced radius-level arithmetic matches expected data")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
