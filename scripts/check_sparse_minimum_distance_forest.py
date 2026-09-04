#!/usr/bin/env python3
"""Replay exact arithmetic for the boundary-detour forest and fan-in lemmas."""

from __future__ import annotations

import argparse
import json
from typing import Any

from erdos97.sparse_minimum_distance_forest import (
    assert_expected_payload,
    arithmetic_payload,
)


def summary_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a compact reviewer-facing summary."""

    compact = dict(payload)
    compact.pop("long_cycle_cases", None)
    compact.pop("fan_in_cases", None)
    compact.pop("export_cases", None)
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
    payload = arithmetic_payload(args.max_cycle_length)
    if args.assert_expected:
        assert_expected_payload(payload)

    if args.summary_json:
        print(json.dumps(summary_payload(payload), indent=2, sort_keys=True))
    elif args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("boundary-detour forest and fan-in arithmetic replay")
        print(
            "triangle normalized lower sum: "
            f"{payload['triangle_case']['normalized_internal_turn_lower_sum']}"
        )
        start, end = payload["checked_cycle_length_range"]
        print(f"checked long-cycle range: {start}..{end}")
        print(
            "all checked long cycles close: "
            f"{payload['all_checked_long_cycles_close']}"
        )
        print(f"long-cycle identity: {payload['long_cycle_identity']}")
        print(f"common-target fan-in cap: {payload['fan_in_cap']}")
        print(f"export identity: {payload['export_identity']}")
        if args.assert_expected:
            print("OK: forest, fan-in, and export arithmetic matches expected data")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
