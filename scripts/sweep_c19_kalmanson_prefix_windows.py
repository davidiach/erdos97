#!/usr/bin/env python3
"""Run compact C19 prefix-window Kalmanson chain sweeps.

The default sweep covers five deterministic 32-prefix windows:

```text
128-159, 160-191, 192-223, 224-255, 256-287
```

For each window, the underlying checker tries direct three-boundary-prefix
Kalmanson/Farkas certificates, then fourth-pair subdivision, then fifth-pair
subdivision.  The sweep artifact stores compact per-window accounting and
survivor lists instead of full closed certificate examples.

This is a bounded sampled-window sweep, not an all-order C19 search.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Mapping

from certify_c19_kalmanson_prefix_window import scan_window
from pilot_c19_kalmanson_prefix_branches import N, OFFSETS, PATTERN_NAME, label_digest

DEFAULT_START_INDEX = 128
DEFAULT_WINDOW_SIZE = 32
DEFAULT_WINDOW_COUNT = 5


def compact_window_record(data: Mapping[str, object]) -> dict[str, object]:
    parameters = data["parameters"]
    accounting = data["branch_accounting"]
    if not isinstance(parameters, Mapping):
        raise TypeError("parameters must be an object")
    if not isinstance(accounting, Mapping):
        raise TypeError("branch_accounting must be an object")
    direct_unclosed = data["direct_unclosed_prefixes"]
    fourth_unclosed = data["unclosed_fourth_pair_child_branches"]
    fifth_unclosed = data["unclosed_fifth_pair_child_branches"]
    if not isinstance(direct_unclosed, list):
        raise TypeError("direct_unclosed_prefixes must be a list")
    if not isinstance(fourth_unclosed, list):
        raise TypeError("unclosed_fourth_pair_child_branches must be a list")
    if not isinstance(fifth_unclosed, list):
        raise TypeError("unclosed_fifth_pair_child_branches must be a list")
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
        "direct_survivors": direct_unclosed,
        "fourth_pair_survivors": fourth_unclosed,
        "fifth_pair_survivors": fifth_unclosed,
    }


def run_sweep(
    *,
    start_index: int,
    window_size: int,
    window_count: int,
    tol: float,
) -> dict[str, object]:
    if start_index < 0:
        raise ValueError("start_index must be nonnegative")
    if window_size < 0:
        raise ValueError("window_size must be nonnegative")
    if window_count < 0:
        raise ValueError("window_count must be nonnegative")

    windows: list[dict[str, object]] = []
    for window_offset in range(window_count):
        window_start = start_index + window_offset * window_size
        window_data = scan_window(
            start_index=window_start,
            window_size=window_size,
            include_certificates=False,
            closed_example_count=0,
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
    total_fifth_children = 0
    total_fifth_closed = 0
    total_fifth_survivors = 0
    for window in windows:
        accounting = window["branch_accounting"]
        if not isinstance(accounting, Mapping):
            raise TypeError("window branch_accounting must be an object")
        total_prefixes += int(accounting["prefix_branch_count"])
        total_closed += int(accounting["prefix_branches_closed_after_chain"])
        total_direct_closed += int(accounting["direct_prefix_certified_count"])
        total_direct_survivors += int(accounting["direct_prefix_unclosed_count"])
        total_fourth_children += int(accounting["fourth_pair_child_branch_count"])
        total_fourth_closed += int(accounting["fourth_pair_child_certified_count"])
        total_fourth_survivors += int(accounting["unclosed_fourth_pair_child_branch_count"])
        total_fifth_children += int(accounting["fifth_pair_child_branch_count"])
        total_fifth_closed += int(accounting["fifth_pair_child_certified_count"])
        total_fifth_survivors += int(accounting["unclosed_fifth_pair_child_branch_count"])
        prefix_labels.extend(
            f"c19_prefix_branch_{idx:04d}"
            for idx in range(int(window["start_index"]), int(window["end_index"]) + 1)
        )

    return {
        "type": "c19_kalmanson_prefix_window_sweep_v1",
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
            "Closed branches use Kalmanson/Farkas certificates whose order is forced by the recorded boundary prefix.",
            "Unclosed children, if any, are not counterexamples and are not evidence of realizability.",
            "This is not an exhaustive all-order C19 search.",
        ],
        "parameters": {
            "start_index": start_index,
            "window_size": window_size,
            "window_count": window_count,
            "lp_support_tolerance": tol,
            "anchor_label": 0,
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
            "fifth_pair_child_branch_count": total_fifth_children,
            "fifth_pair_child_certified_count": total_fifth_closed,
            "unclosed_fifth_pair_child_branch_count": total_fifth_survivors,
            "exhaustive_window_sweep": True,
            "exhaustive_all_orders": False,
        },
        "prefix_label_digest": label_digest(prefix_labels),
        "windows": windows,
    }


def assert_expected(data: Mapping[str, object]) -> None:
    aggregate = data["aggregate_accounting"]
    if not isinstance(aggregate, Mapping):
        raise AssertionError("aggregate_accounting must be an object")
    expected_aggregate = {
        "prefix_branch_count": 160,
        "prefix_branches_closed_after_chain": 160,
        "prefix_branches_remaining_after_chain": 0,
        "direct_prefix_certified_count": 112,
        "direct_prefix_unclosed_count": 48,
        "fourth_pair_child_branch_count": 6336,
        "fourth_pair_child_certified_count": 6248,
        "unclosed_fourth_pair_child_branch_count": 88,
        "fifth_pair_child_branch_count": 7920,
        "fifth_pair_child_certified_count": 7920,
        "unclosed_fifth_pair_child_branch_count": 0,
        "exhaustive_window_sweep": True,
        "exhaustive_all_orders": False,
    }
    for key, expected in expected_aggregate.items():
        if aggregate[key] != expected:
            raise AssertionError(f"{key} changed: {aggregate[key]} != {expected}")

    expected_digest = "b18984a2ebd95ffcd6eb2af48fd13c6710b29d9234af18e5966895fa23667879"
    if data["prefix_label_digest"] != expected_digest:
        raise AssertionError("prefix label digest changed")

    windows = data["windows"]
    if not isinstance(windows, list) or len(windows) != 5:
        raise AssertionError("window list changed")
    expected_windows = [
        (128, 159, 31, 1, 132, 130, 2, 180, 180, 0),
        (160, 191, 23, 9, 1188, 1181, 7, 630, 630, 0),
        (192, 223, 19, 13, 1716, 1701, 15, 1350, 1350, 0),
        (224, 255, 24, 8, 1056, 1047, 9, 810, 810, 0),
        (256, 287, 15, 17, 2244, 2189, 55, 4950, 4950, 0),
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
            fifth_unclosed,
        ) = expected
        accounting = window["branch_accounting"]
        if not isinstance(accounting, Mapping):
            raise AssertionError("window accounting must be an object")
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
            "unclosed_fifth_pair_child_branch_count": fifth_unclosed,
            "prefix_branches_closed_after_chain": 32,
            "prefix_branches_remaining_after_chain": 0,
        }
        for key, value in checks.items():
            if accounting[key] != value:
                raise AssertionError(f"window {start} {key} changed")


def print_table(data: Mapping[str, object]) -> None:
    aggregate = data["aggregate_accounting"]
    if not isinstance(aggregate, Mapping):
        raise TypeError("aggregate_accounting must be an object")
    print(
        "C19 prefix window sweep: "
        f"closed={aggregate['prefix_branches_closed_after_chain']} "
        f"remaining={aggregate['prefix_branches_remaining_after_chain']} "
        f"scanned={aggregate['prefix_branch_count']}"
    )
    print(
        "subdivision children: "
        f"fourth={aggregate['fourth_pair_child_certified_count']}/"
        f"{aggregate['fourth_pair_child_branch_count']} "
        f"fifth={aggregate['fifth_pair_child_certified_count']}/"
        f"{aggregate['fifth_pair_child_branch_count']}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-index", type=int, default=DEFAULT_START_INDEX)
    parser.add_argument("--window-size", type=int, default=DEFAULT_WINDOW_SIZE)
    parser.add_argument("--window-count", type=int, default=DEFAULT_WINDOW_COUNT)
    parser.add_argument("--tol", type=float, default=1e-9, help="LP support threshold")
    parser.add_argument("--out", type=Path, help="write JSON payload to this path")
    parser.add_argument("--json", action="store_true", help="print JSON payload")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    data = run_sweep(
        start_index=args.start_index,
        window_size=args.window_size,
        window_count=args.window_count,
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
            print("OK: C19 prefix window sweep matched expected sampled chain")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
