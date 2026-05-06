#!/usr/bin/env python3
"""Run the C19 prefix-window sweep with cataloged fallback prefilter supports.

This is the same deterministic 288-479 C19 sampled-prefix range as
sweep_c19_kalmanson_prefix_windows_prefilter.py, but fifth-pair children use a
two-stage exact prefilter:

1. the existing two-row Kalmanson cancellation lookup;
2. the cataloged unit supports from
   reports/c19_prefilter_catalog_unit_supports.json.

Only misses for both exact prefilters call the ordinary Kalmanson/Farkas
routine.  This is a bounded sampled-window sweep, not an all-order C19 search.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from analyze_c19_prefilter_catalog_unit_supports import catalog_unit_support_catalog
from sweep_c19_kalmanson_prefix_windows_prefilter import (
    DEFAULT_FALLBACK_EXAMPLE_COUNT,
    DEFAULT_START_INDEX,
    DEFAULT_WINDOW_COUNT,
    DEFAULT_WINDOW_SIZE,
    _as_mapping,
    print_table,
    run_sweep,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = (
    ROOT
    / "data"
    / "certificates"
    / "c19_kalmanson_prefix_window_catalog_prefilter_sweep_288_479.json"
)


def assert_expected(data: Mapping[str, Any]) -> None:
    parameters = _as_mapping(data["parameters"], "parameters")
    key = (
        int(parameters["start_index"]),
        int(parameters["window_size"]),
        int(parameters["window_count"]),
        int(parameters["fallback_example_count"]),
        int(parameters["catalog_unit_support_count"]),
    )
    expected_key = (
        DEFAULT_START_INDEX,
        DEFAULT_WINDOW_SIZE,
        DEFAULT_WINDOW_COUNT,
        DEFAULT_FALLBACK_EXAMPLE_COUNT,
        3,
    )
    if key != expected_key:
        raise AssertionError(f"no expected counts registered for catalog sweep {key}")
    if data["type"] != "c19_kalmanson_prefix_window_catalog_prefilter_sweep_v1":
        raise AssertionError("catalog sweep artifact type changed")

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
        "fifth_pair_prefilter_certified_count": 10350,
        "fifth_pair_two_row_prefilter_certified_count": 10342,
        "fifth_pair_catalog_prefilter_certified_count": 8,
        "fifth_pair_farkas_fallback_attempt_count": 0,
        "fifth_pair_farkas_fallback_certified_count": 0,
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
        (288, 319, 0, 0, 0, []),
        (320, 351, 540, 0, 0, []),
        (352, 383, 720, 0, 0, []),
        (384, 415, 1350, 0, 0, []),
        (416, 447, 4230, 7, 0, []),
        (448, 479, 3510, 1, 0, []),
    ]
    for window, expected in zip(windows, expected_windows):
        start, end, prefilter_count, catalog_count, fallback_count, fallback_labels = expected
        if window["start_index"] != start or window["end_index"] != end:
            raise AssertionError("window bounds changed")
        accounting = _as_mapping(window["branch_accounting"], "window accounting")
        checks = {
            "fifth_pair_prefilter_certified_count": prefilter_count,
            "fifth_pair_catalog_prefilter_certified_count": catalog_count,
            "fifth_pair_farkas_fallback_certified_count": fallback_count,
            "unclosed_fifth_pair_child_branch_count": 0,
            "prefix_branches_closed_after_chain": 32,
            "prefix_branches_remaining_after_chain": 0,
        }
        for name, value in checks.items():
            if accounting.get(name) != value:
                raise AssertionError(f"window {start} {name} changed")
        if window["fifth_pair_farkas_fallback_labels"] != fallback_labels:
            raise AssertionError(f"window {start} fallback labels changed")


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
        catalog_unit_supports=catalog_unit_support_catalog(),
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
            print("OK: C19 catalog prefilter sweep matched expected chain")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
