#!/usr/bin/env python3
"""Analyze exact branch costs in the compact C19 Kalmanson sweep artifact.

This script is a deterministic diagnostic over a checked sweep artifact.  It
does not run LPs and does not produce new obstruction certificates.  Its purpose
is to identify where later exact C19 prefix scans are paying subdivision cost.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "data" / "certificates" / "c19_kalmanson_prefix_window_sweep_128_287.json"
DEFAULT_OUT = ROOT / "reports" / "c19_kalmanson_sweep_cost_diagnostic.json"


def _as_mapping(value: object, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{label} must be an object")
    return value


def _as_list(value: object, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise TypeError(f"{label} must be a list")
    return value


def _branch_index(label: str) -> int:
    return int(label.rsplit("_", 1)[1])


def _histogram(counter: Counter[int]) -> dict[str, int]:
    return {str(key): counter[key] for key in sorted(counter)}


def analyze_sweep_costs(payload: Mapping[str, Any], *, source_artifact: str) -> dict[str, Any]:
    aggregate = _as_mapping(payload["aggregate_accounting"], "aggregate_accounting")
    windows = _as_list(payload["windows"], "windows")

    per_prefix: list[dict[str, Any]] = []
    per_window: list[dict[str, Any]] = []
    fifth_by_prefix_histogram: Counter[int] = Counter()
    fourth_survivor_histogram: Counter[int] = Counter()
    window_total_histogram: Counter[int] = Counter()
    direct_survivors_requiring_fifth = 0

    for window in windows:
        window_map = _as_mapping(window, "window")
        accounting = _as_mapping(window_map["branch_accounting"], "window branch_accounting")
        direct_survivors = _as_list(window_map["direct_survivors"], "direct_survivors")
        fourth_survivors = _as_list(window_map["fourth_pair_survivors"], "fourth_pair_survivors")
        fourth_by_prefix: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
        for row in fourth_survivors:
            row_map = _as_mapping(row, "fourth survivor")
            fourth_by_prefix[str(row_map["prefix_parent_label"])].append(row_map)

        direct_attempts = int(accounting["prefix_branch_count"])
        fourth_attempts = int(accounting["fourth_pair_child_branch_count"])
        fifth_attempts = int(accounting["fifth_pair_child_branch_count"])
        total_attempts = direct_attempts + fourth_attempts + fifth_attempts
        window_total_histogram[total_attempts] += 1
        per_window.append(
            {
                "start_index": int(window_map["start_index"]),
                "end_index": int(window_map["end_index"]),
                "direct_prefix_attempt_count": direct_attempts,
                "direct_prefix_unclosed_count": int(accounting["direct_prefix_unclosed_count"]),
                "fourth_pair_child_attempt_count": fourth_attempts,
                "fourth_pair_child_survivor_count": int(
                    accounting["unclosed_fourth_pair_child_branch_count"]
                ),
                "fifth_pair_child_attempt_count": fifth_attempts,
                "fifth_pair_child_survivor_count": int(
                    accounting["unclosed_fifth_pair_child_branch_count"]
                ),
                "total_branch_attempt_count": total_attempts,
            }
        )

        for row in direct_survivors:
            row_map = _as_mapping(row, "direct survivor")
            label = str(row_map["label"])
            middle_label_count = int(row_map["middle_label_count"])
            fourth_attempt_count = middle_label_count * (middle_label_count - 1)
            fifth_attempt_per_fourth_survivor = (middle_label_count - 2) * (middle_label_count - 3)
            fourth_survivor_count = len(fourth_by_prefix.get(label, []))
            fifth_attempt_count = fourth_survivor_count * fifth_attempt_per_fourth_survivor
            if fourth_survivor_count:
                direct_survivors_requiring_fifth += 1
            fifth_by_prefix_histogram[fifth_attempt_count] += 1
            fourth_survivor_histogram[fourth_survivor_count] += 1
            per_prefix.append(
                {
                    "label": label,
                    "branch_index": _branch_index(label),
                    "window_start_index": int(window_map["start_index"]),
                    "window_end_index": int(window_map["end_index"]),
                    "boundary_left": row_map["boundary_left"],
                    "boundary_right_reflection_side": row_map["boundary_right_reflection_side"],
                    "middle_label_count": middle_label_count,
                    "fourth_pair_child_attempt_count": fourth_attempt_count,
                    "fourth_pair_child_survivor_count": fourth_survivor_count,
                    "fifth_pair_child_attempt_count": fifth_attempt_count,
                    "total_descendant_attempt_count": fourth_attempt_count + fifth_attempt_count,
                }
            )

    per_window.sort(key=lambda row: (row["start_index"], row["end_index"]))
    per_prefix.sort(key=lambda row: row["branch_index"])
    total_attempts = (
        int(aggregate["prefix_branch_count"])
        + int(aggregate["fourth_pair_child_branch_count"])
        + int(aggregate["fifth_pair_child_branch_count"])
    )
    max_window = max(per_window, key=lambda row: (row["total_branch_attempt_count"], row["start_index"]))
    max_prefix = max(
        per_prefix,
        key=lambda row: (
            row["fifth_pair_child_attempt_count"],
            row["fourth_pair_child_survivor_count"],
            -row["branch_index"],
        ),
    )
    top_prefixes = sorted(
        per_prefix,
        key=lambda row: (
            -row["fifth_pair_child_attempt_count"],
            -row["fourth_pair_child_survivor_count"],
            row["branch_index"],
        ),
    )[:12]

    return {
        "type": "c19_kalmanson_sweep_cost_diagnostic_v1",
        "trust": "EXACT_CERTIFICATE_DIAGNOSTIC",
        "source_artifact": source_artifact,
        "source_type": payload["type"],
        "source_prefix_label_digest": payload["prefix_label_digest"],
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "This is an exact workload diagnostic over the recorded sweep artifact.",
            "The counts are branch/certificate attempts implied by the artifact, not runtime measurements.",
            "The diagnostic does not certify any branch beyond the source artifact.",
        ],
        "aggregate": {
            "window_count": len(windows),
            "prefix_branch_count": int(aggregate["prefix_branch_count"]),
            "prefix_branches_closed_after_chain": int(
                aggregate["prefix_branches_closed_after_chain"]
            ),
            "prefix_branches_remaining_after_chain": int(
                aggregate["prefix_branches_remaining_after_chain"]
            ),
            "direct_prefix_attempt_count": int(aggregate["prefix_branch_count"]),
            "direct_prefix_unclosed_count": int(aggregate["direct_prefix_unclosed_count"]),
            "fourth_pair_child_attempt_count": int(aggregate["fourth_pair_child_branch_count"]),
            "fourth_pair_child_survivor_count": int(
                aggregate["unclosed_fourth_pair_child_branch_count"]
            ),
            "fifth_pair_child_attempt_count": int(aggregate["fifth_pair_child_branch_count"]),
            "fifth_pair_child_survivor_count": int(
                aggregate["unclosed_fifth_pair_child_branch_count"]
            ),
            "total_branch_attempt_count": total_attempts,
            "direct_survivor_count": len(per_prefix),
            "direct_survivors_requiring_fifth_pair_count": direct_survivors_requiring_fifth,
            "direct_survivors_closed_by_fourth_pair_only_count": len(per_prefix)
            - direct_survivors_requiring_fifth,
        },
        "histograms": {
            "fifth_pair_child_attempts_per_direct_survivor": _histogram(
                fifth_by_prefix_histogram
            ),
            "fourth_pair_survivors_per_direct_survivor": _histogram(
                fourth_survivor_histogram
            ),
            "window_total_branch_attempts": _histogram(window_total_histogram),
        },
        "maxima": {
            "max_window_by_total_branch_attempts": max_window,
            "max_prefix_by_fifth_pair_child_attempts": max_prefix,
        },
        "per_window": per_window,
        "top_prefix_frontiers_by_fifth_pair_child_attempts": top_prefixes,
        "per_prefix_frontier": per_prefix,
    }


def assert_expected(data: Mapping[str, Any]) -> None:
    expected_digest = "b18984a2ebd95ffcd6eb2af48fd13c6710b29d9234af18e5966895fa23667879"
    if data["source_prefix_label_digest"] != expected_digest:
        raise AssertionError("source digest changed")
    aggregate = _as_mapping(data["aggregate"], "aggregate")
    expected_aggregate = {
        "window_count": 5,
        "prefix_branch_count": 160,
        "prefix_branches_closed_after_chain": 160,
        "prefix_branches_remaining_after_chain": 0,
        "direct_prefix_attempt_count": 160,
        "direct_prefix_unclosed_count": 48,
        "fourth_pair_child_attempt_count": 6336,
        "fourth_pair_child_survivor_count": 88,
        "fifth_pair_child_attempt_count": 7920,
        "fifth_pair_child_survivor_count": 0,
        "total_branch_attempt_count": 14416,
        "direct_survivor_count": 48,
        "direct_survivors_requiring_fifth_pair_count": 33,
        "direct_survivors_closed_by_fourth_pair_only_count": 15,
    }
    for key, expected in expected_aggregate.items():
        if aggregate[key] != expected:
            raise AssertionError(f"{key} changed: {aggregate[key]} != {expected}")

    histograms = _as_mapping(data["histograms"], "histograms")
    expected_fifth_histogram = {
        "0": 15,
        "90": 13,
        "180": 7,
        "270": 3,
        "360": 4,
        "450": 4,
        "630": 1,
        "810": 1,
    }
    if histograms["fifth_pair_child_attempts_per_direct_survivor"] != expected_fifth_histogram:
        raise AssertionError("fifth-pair child histogram changed")

    maxima = _as_mapping(data["maxima"], "maxima")
    max_window = _as_mapping(maxima["max_window_by_total_branch_attempts"], "max window")
    if (max_window["start_index"], max_window["end_index"], max_window["total_branch_attempt_count"]) != (
        256,
        287,
        7226,
    ):
        raise AssertionError("max-cost window changed")
    max_prefix = _as_mapping(maxima["max_prefix_by_fifth_pair_child_attempts"], "max prefix")
    if (
        max_prefix["label"],
        max_prefix["fifth_pair_child_attempt_count"],
        max_prefix["fourth_pair_child_survivor_count"],
    ) != ("c19_prefix_branch_0269", 810, 9):
        raise AssertionError("max-cost prefix changed")


def print_table(data: Mapping[str, Any]) -> None:
    aggregate = _as_mapping(data["aggregate"], "aggregate")
    maxima = _as_mapping(data["maxima"], "maxima")
    max_window = _as_mapping(maxima["max_window_by_total_branch_attempts"], "max window")
    max_prefix = _as_mapping(maxima["max_prefix_by_fifth_pair_child_attempts"], "max prefix")
    print(
        "C19 sweep cost diagnostic: "
        f"attempts={aggregate['total_branch_attempt_count']} "
        f"prefixes={aggregate['prefix_branch_count']} "
        f"fifth_pair={aggregate['fifth_pair_child_attempt_count']}"
    )
    print(
        "max window: "
        f"{max_window['start_index']}-{max_window['end_index']} "
        f"attempts={max_window['total_branch_attempt_count']}"
    )
    print(
        "max prefix: "
        f"{max_prefix['label']} "
        f"fifth_children={max_prefix['fifth_pair_child_attempt_count']}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, help="write JSON payload to this path")
    parser.add_argument("--json", action="store_true", help="print JSON payload")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    payload = json.loads(args.source.read_text(encoding="utf-8"))
    try:
        source_artifact = str(args.source.resolve().relative_to(ROOT))
    except ValueError:
        source_artifact = str(args.source)
    data = analyze_sweep_costs(payload, source_artifact=source_artifact)
    if args.assert_expected:
        assert_expected(data)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print_table(data)
        if args.assert_expected:
            print("OK: C19 sweep cost diagnostic matched expected accounting")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
