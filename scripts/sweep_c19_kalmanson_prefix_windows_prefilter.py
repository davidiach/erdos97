#!/usr/bin/env python3
"""Run compact C19 prefix-window sweeps with the fifth-pair prefilter.

The default sweep covers six deterministic 32-prefix windows:

```text
288-319, 320-351, 352-383, 384-415, 416-447, 448-479
```

Each window uses the prefix/fourth/fifth chain from
certify_c19_kalmanson_prefix_window_prefilter.py.  Fifth-pair children first
try the exact two-row Kalmanson prefilter; only prefilter misses call the
ordinary exact Farkas routine.  The sweep artifact stores compact per-window
accounting and survivor lists instead of full closed certificate examples.

This is a bounded sampled-window sweep, not an all-order C19 search.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from certify_c19_kalmanson_prefix_window_prefilter import scan_window_with_prefilter
from pilot_c19_kalmanson_prefix_branches import N, OFFSETS, PATTERN_NAME, label_digest

DEFAULT_START_INDEX = 288
DEFAULT_WINDOW_SIZE = 32
DEFAULT_WINDOW_COUNT = 6
DEFAULT_FALLBACK_EXAMPLE_COUNT = 16


def _as_mapping(value: object, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{label} must be an object")
    return value


def _as_list(value: object, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise TypeError(f"{label} must be a list")
    return value


def compact_window_record(data: Mapping[str, object]) -> dict[str, object]:
    parameters = _as_mapping(data["parameters"], "parameters")
    accounting = _as_mapping(data["branch_accounting"], "branch_accounting")
    direct_unclosed = _as_list(data["direct_unclosed_prefixes"], "direct_unclosed_prefixes")
    fourth_unclosed = _as_list(
        data["unclosed_fourth_pair_child_branches"],
        "unclosed_fourth_pair_child_branches",
    )
    fifth_unclosed = _as_list(
        data["unclosed_fifth_pair_child_branches"],
        "unclosed_fifth_pair_child_branches",
    )
    fallback_examples = _as_list(
        data["fifth_pair_farkas_fallback_examples"],
        "fifth_pair_farkas_fallback_examples",
    )
    start_index = int(parameters["start_index"])
    window_size = int(parameters["window_size"])
    return {
        "start_index": start_index,
        "end_index": start_index + window_size - 1,
        "window_size": window_size,
        "branch_accounting": accounting,
        "forced_row_count_histograms": data["forced_row_count_histograms"],
        "closed_support_size_histograms": data["closed_support_size_histograms"],
        "label_digests": data["label_digests"],
        "direct_survivor_labels": [str(row["label"]) for row in direct_unclosed],
        "fourth_pair_survivor_labels": [str(row["label"]) for row in fourth_unclosed],
        "fifth_pair_survivor_labels": [str(row["label"]) for row in fifth_unclosed],
        "fifth_pair_farkas_fallback_labels": [
            str(row["label"]) for row in fallback_examples
        ],
        "direct_survivors": direct_unclosed,
        "fourth_pair_survivors": fourth_unclosed,
        "fifth_pair_survivors": fifth_unclosed,
    }


def run_sweep(
    *,
    start_index: int,
    window_size: int,
    window_count: int,
    fallback_example_count: int,
    tol: float,
) -> dict[str, object]:
    if start_index < 0:
        raise ValueError("start_index must be nonnegative")
    if window_size < 0:
        raise ValueError("window_size must be nonnegative")
    if window_count < 0:
        raise ValueError("window_count must be nonnegative")
    if fallback_example_count < 0:
        raise ValueError("fallback_example_count must be nonnegative")

    windows: list[dict[str, object]] = []
    for window_offset in range(window_count):
        window_start = start_index + window_offset * window_size
        window_data = scan_window_with_prefilter(
            start_index=window_start,
            window_size=window_size,
            include_certificates=False,
            closed_example_count=fallback_example_count,
            tol=tol,
        )
        windows.append(compact_window_record(window_data))

    prefix_labels: list[str] = []
    total_prefixes = 0
    total_closed = 0
    total_direct_closed = 0
    total_direct_survivors = 0
    total_fourth_children = 0
    total_fourth_closed = 0
    total_fourth_survivors = 0
    total_prefixes_closed_by_fourth = 0
    total_fifth_parents = 0
    total_fifth_children = 0
    total_fifth_closed = 0
    total_fifth_prefilter_closed = 0
    total_fifth_fallback_attempts = 0
    total_fifth_fallback_closed = 0
    total_fifth_survivors = 0
    total_fourth_parents_closed_by_fifth = 0
    total_prefixes_closed_by_fifth = 0
    for window in windows:
        accounting = _as_mapping(window["branch_accounting"], "window branch_accounting")
        total_prefixes += int(accounting["prefix_branch_count"])
        total_closed += int(accounting["prefix_branches_closed_after_chain"])
        total_direct_closed += int(accounting["direct_prefix_certified_count"])
        total_direct_survivors += int(accounting["direct_prefix_unclosed_count"])
        total_fourth_children += int(accounting["fourth_pair_child_branch_count"])
        total_fourth_closed += int(accounting["fourth_pair_child_certified_count"])
        total_fourth_survivors += int(
            accounting["unclosed_fourth_pair_child_branch_count"]
        )
        total_prefixes_closed_by_fourth += int(
            accounting["prefix_parents_closed_by_fourth_refinement"]
        )
        total_fifth_parents += int(accounting["fifth_pair_parent_count"])
        total_fifth_children += int(accounting["fifth_pair_child_branch_count"])
        total_fifth_closed += int(accounting["fifth_pair_child_certified_count"])
        total_fifth_prefilter_closed += int(
            accounting["fifth_pair_prefilter_certified_count"]
        )
        total_fifth_fallback_attempts += int(
            accounting["fifth_pair_farkas_fallback_attempt_count"]
        )
        total_fifth_fallback_closed += int(
            accounting["fifth_pair_farkas_fallback_certified_count"]
        )
        total_fifth_survivors += int(accounting["unclosed_fifth_pair_child_branch_count"])
        total_fourth_parents_closed_by_fifth += int(
            accounting["fourth_pair_parents_closed_by_fifth_refinement"]
        )
        total_prefixes_closed_by_fifth += int(
            accounting["prefix_parents_closed_by_fifth_refinement"]
        )
        prefix_labels.extend(
            f"c19_prefix_branch_{idx:04d}"
            for idx in range(int(window["start_index"]), int(window["end_index"]) + 1)
        )

    return {
        "type": "c19_kalmanson_prefix_window_prefilter_sweep_v1",
        "trust": "EXACT_OBSTRUCTION",
        "pattern": {
            "name": PATTERN_NAME,
            "n": N,
            "circulant_offsets": OFFSETS,
        },
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "This sweep certifies only deterministic C19 three-boundary-prefix windows.",
            "Direct and fourth-pair closures use ordinary prefix-forced Kalmanson/Farkas certificates.",
            "Fifth-pair closures first try exact two-row Kalmanson cancellations; only misses use ordinary Farkas fallback.",
            "Unclosed children, if any, are not counterexamples and are not evidence of realizability.",
            "This is not an exhaustive all-order C19 search.",
        ],
        "parameters": {
            "start_index": start_index,
            "window_size": window_size,
            "window_count": window_count,
            "lp_support_tolerance": tol,
            "anchor_label": 0,
            "fifth_pair_prefilter": "two_row_kalmanson_prefilter",
            "fallback_example_count": fallback_example_count,
        },
        "aggregate_accounting": {
            "prefix_branch_count": total_prefixes,
            "prefix_branches_closed_after_chain": total_closed,
            "prefix_branches_remaining_after_chain": total_prefixes - total_closed,
            "direct_prefix_certified_count": total_direct_closed,
            "direct_prefix_unclosed_count": total_direct_survivors,
            "fourth_pair_child_branch_count": total_fourth_children,
            "fourth_pair_child_certified_count": total_fourth_closed,
            "unclosed_fourth_pair_child_branch_count": total_fourth_survivors,
            "prefix_parents_closed_by_fourth_refinement": total_prefixes_closed_by_fourth,
            "fifth_pair_parent_count": total_fifth_parents,
            "fifth_pair_child_branch_count": total_fifth_children,
            "fifth_pair_child_certified_count": total_fifth_closed,
            "fifth_pair_prefilter_certified_count": total_fifth_prefilter_closed,
            "fifth_pair_farkas_fallback_attempt_count": total_fifth_fallback_attempts,
            "fifth_pair_farkas_fallback_certified_count": total_fifth_fallback_closed,
            "unclosed_fifth_pair_child_branch_count": total_fifth_survivors,
            "fourth_pair_parents_closed_by_fifth_refinement": (
                total_fourth_parents_closed_by_fifth
            ),
            "prefix_parents_closed_by_fifth_refinement": total_prefixes_closed_by_fifth,
            "exhaustive_window_sweep": True,
            "exhaustive_all_orders": False,
        },
        "prefix_label_digest": label_digest(prefix_labels),
        "windows": windows,
    }


def assert_expected(data: Mapping[str, object]) -> None:
    parameters = _as_mapping(data["parameters"], "parameters")
    key = (
        int(parameters["start_index"]),
        int(parameters["window_size"]),
        int(parameters["window_count"]),
        int(parameters["fallback_example_count"]),
    )
    expected_key = (
        DEFAULT_START_INDEX,
        DEFAULT_WINDOW_SIZE,
        DEFAULT_WINDOW_COUNT,
        DEFAULT_FALLBACK_EXAMPLE_COUNT,
    )
    if key != expected_key:
        raise AssertionError(f"no expected counts registered for sweep {key}")

    aggregate = _as_mapping(data["aggregate_accounting"], "aggregate_accounting")
    expected_aggregate = {
        "prefix_branch_count": 192,
        "prefix_branches_closed_after_chain": 192,
        "prefix_branches_remaining_after_chain": 0,
        "direct_prefix_certified_count": 136,
        "direct_prefix_unclosed_count": 56,
        "fourth_pair_child_branch_count": 7392,
        "fourth_pair_child_certified_count": 7277,
        "unclosed_fourth_pair_child_branch_count": 115,
        "prefix_parents_closed_by_fourth_refinement": 17,
        "fifth_pair_parent_count": 115,
        "fifth_pair_child_branch_count": 10350,
        "fifth_pair_child_certified_count": 10350,
        "fifth_pair_prefilter_certified_count": 10342,
        "fifth_pair_farkas_fallback_attempt_count": 8,
        "fifth_pair_farkas_fallback_certified_count": 8,
        "unclosed_fifth_pair_child_branch_count": 0,
        "fourth_pair_parents_closed_by_fifth_refinement": 115,
        "prefix_parents_closed_by_fifth_refinement": 39,
        "exhaustive_window_sweep": True,
        "exhaustive_all_orders": False,
    }
    for key, expected in expected_aggregate.items():
        if aggregate[key] != expected:
            raise AssertionError(f"{key} changed: {aggregate[key]} != {expected}")

    expected_digest = "a2dcbd0eb6d2513dd906346ab9a4e6a273bb7033d5bcd344cf4f52cd622e8648"
    if data["prefix_label_digest"] != expected_digest:
        raise AssertionError("prefix label digest changed")

    windows = data["windows"]
    if not isinstance(windows, list) or len(windows) != 6:
        raise AssertionError("window list changed")
    expected_windows = [
        (288, 319, 32, 0, 0, 0, 0, 0, 0, 0, 0, []),
        (320, 351, 26, 6, 792, 786, 6, 540, 540, 540, 0, []),
        (352, 383, 23, 9, 1188, 1180, 8, 720, 720, 720, 0, []),
        (384, 415, 20, 12, 1584, 1569, 15, 1350, 1350, 1350, 0, []),
        (
            416,
            447,
            19,
            13,
            1716,
            1669,
            47,
            4230,
            4230,
            4223,
            7,
            [
                "c19_window_fifth_child_0430_0081_0011",
                "c19_window_fifth_child_0434_0070_0021",
                "c19_window_fifth_child_0435_0078_0012",
                "c19_window_fifth_child_0435_0078_0085",
                "c19_window_fifth_child_0435_0083_0022",
                "c19_window_fifth_child_0436_0082_0022",
                "c19_window_fifth_child_0436_0083_0022",
            ],
        ),
        (
            448,
            479,
            16,
            16,
            2112,
            2073,
            39,
            3510,
            3510,
            3509,
            1,
            ["c19_window_fifth_child_0456_0059_0041"],
        ),
    ]
    for window, expected in zip(windows, expected_windows):
        (
            start,
            end,
            direct_closed,
            direct_unclosed,
            fourth_count,
            fourth_closed,
            fourth_unclosed,
            fifth_count,
            fifth_closed,
            fifth_prefilter,
            fifth_fallback,
            fallback_labels,
        ) = expected
        accounting = _as_mapping(window["branch_accounting"], "window accounting")
        if window["start_index"] != start or window["end_index"] != end:
            raise AssertionError("window bounds changed")
        checks = {
            "direct_prefix_certified_count": direct_closed,
            "direct_prefix_unclosed_count": direct_unclosed,
            "fourth_pair_child_branch_count": fourth_count,
            "fourth_pair_child_certified_count": fourth_closed,
            "unclosed_fourth_pair_child_branch_count": fourth_unclosed,
            "fifth_pair_child_branch_count": fifth_count,
            "fifth_pair_child_certified_count": fifth_closed,
            "fifth_pair_prefilter_certified_count": fifth_prefilter,
            "fifth_pair_farkas_fallback_certified_count": fifth_fallback,
            "unclosed_fifth_pair_child_branch_count": 0,
            "prefix_branches_closed_after_chain": 32,
            "prefix_branches_remaining_after_chain": 0,
        }
        for key, value in checks.items():
            if accounting[key] != value:
                raise AssertionError(f"window {start} {key} changed")
        if window["fifth_pair_farkas_fallback_labels"] != fallback_labels:
            raise AssertionError(f"window {start} fallback labels changed")


def print_table(data: Mapping[str, object]) -> None:
    aggregate = _as_mapping(data["aggregate_accounting"], "aggregate_accounting")
    print(
        "C19 prefix window prefilter sweep: "
        f"closed={aggregate['prefix_branches_closed_after_chain']} "
        f"remaining={aggregate['prefix_branches_remaining_after_chain']} "
        f"scanned={aggregate['prefix_branch_count']}"
    )
    print(
        "subdivision children: "
        f"fourth={aggregate['fourth_pair_child_certified_count']}/"
        f"{aggregate['fourth_pair_child_branch_count']} "
        f"fifth={aggregate['fifth_pair_child_certified_count']}/"
        f"{aggregate['fifth_pair_child_branch_count']} "
        f"prefilter={aggregate['fifth_pair_prefilter_certified_count']} "
        f"fallback={aggregate['fifth_pair_farkas_fallback_certified_count']}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-index", type=int, default=DEFAULT_START_INDEX)
    parser.add_argument("--window-size", type=int, default=DEFAULT_WINDOW_SIZE)
    parser.add_argument("--window-count", type=int, default=DEFAULT_WINDOW_COUNT)
    parser.add_argument(
        "--fallback-example-count",
        type=int,
        default=DEFAULT_FALLBACK_EXAMPLE_COUNT,
        help="closed fallback examples retained only for compact fallback labels",
    )
    parser.add_argument("--tol", type=float, default=1e-9, help="LP support threshold")
    parser.add_argument("--out", type=Path, help="write JSON payload to this path")
    parser.add_argument("--json", action="store_true", help="print JSON payload")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    data = run_sweep(
        start_index=args.start_index,
        window_size=args.window_size,
        window_count=args.window_count,
        fallback_example_count=args.fallback_example_count,
        tol=args.tol,
    )
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
            print("OK: C19 prefix window prefilter sweep matched expected chain")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
