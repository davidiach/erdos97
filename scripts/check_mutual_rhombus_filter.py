#!/usr/bin/env python3
"""Check exact crossing-bisector and mutual-rhombus filters on patterns."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.incidence_filters import filter_summary  # noqa: E402
from erdos97.search import PatternInfo, built_in_patterns  # noqa: E402


EXPECTED: dict[str, dict[str, object]] = {
    "B12_3x4_danzer_lift": {
        "midpoint_matrix_rank": 8,
        "forced_equality_classes": [[0, 4, 8], [1, 5, 9], [2, 6, 10], [3, 7, 11]],
    },
    "B20_4x5_FR_lift": {
        "midpoint_matrix_rank": 15,
        "forced_equality_classes": [
            [0, 5, 10, 15],
            [1, 6, 11, 16],
            [2, 7, 12, 17],
            [3, 8, 13, 18],
            [4, 9, 14, 19],
        ],
    },
    "C9_pm_2_4": {
        "forced_equality_classes": [[0, 1, 2, 3, 4, 5, 6, 7, 8]],
    },
    "C13_pm_3_5": {
        "forced_equality_classes": [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]],
    },
    "C16_pm_1_6": {
        "forced_equality_classes": [[0, 2, 4, 6, 8, 10, 12, 14], [1, 3, 5, 7, 9, 11, 13, 15]],
    },
    "C20_pm_4_9": {
        "forced_equality_classes": [
            [0, 4, 8, 12, 16],
            [1, 5, 9, 13, 17],
            [2, 6, 10, 14, 18],
            [3, 7, 11, 15, 19],
        ],
    },
    "C17_skew": {
        "odd_cycle": True,
    },
    "P18_parity_balanced": {
        "adjacent_two_overlap_violations": True,
    },
    "P24_parity_balanced": {
        "adjacent_two_overlap_violations": True,
    },
}


def pattern_status(summary: dict[str, object]) -> str:
    if summary["odd_cycle_length"]:
        return "exactly killed: odd forced-perpendicularity cycle"
    classes = summary["forced_equality_classes"]
    if classes:
        return "exactly killed: mutual-rhombus midpoint equations"
    if summary["adjacent_two_overlap_violations"]:
        return "killed under natural cyclic order; abstract status tracked separately"
    if summary["crossing_bisector_violations"]:
        return "incompatible with natural cyclic order crossing-bisector filter"
    return "not killed by these filters"


def summarize_pattern(pattern: PatternInfo) -> dict[str, object]:
    summary = filter_summary(pattern.S)
    return {
        "name": pattern.name,
        "family": pattern.family,
        "formula": pattern.formula,
        **summary,
        "status": pattern_status(summary),
    }


def compact_classes(classes: object) -> str:
    if not classes:
        return "-"
    text = "; ".join(str(cls) for cls in classes)  # type: ignore[union-attr]
    if len(text) <= 54:
        return text
    return text[:51] + "..."


def print_table(rows: list[dict[str, object]]) -> None:
    headers = [
        "pattern",
        "n",
        "phi",
        "odd",
        "mutual",
        "rank",
        "eq classes",
        "adj",
        "cross",
        "status",
    ]
    table: list[list[str]] = []
    for row in rows:
        table.append(
            [
                str(row["name"]),
                str(row["n"]),
                str(row["phi_edges"]),
                str(row["odd_cycle_length"] or "-"),
                str(row["mutual_phi_2_cycles"]),
                str(row["midpoint_matrix_rank"]),
                compact_classes(row["forced_equality_classes"]),
                str(len(row["adjacent_two_overlap_violations"])),  # type: ignore[arg-type]
                str(len(row["crossing_bisector_violations"])),  # type: ignore[arg-type]
                str(row["status"]),
            ]
        )

    widths = [
        max(len(headers[col]), *(len(row[col]) for row in table))
        for col in range(len(headers))
    ]
    print("  ".join(headers[col].ljust(widths[col]) for col in range(len(headers))))
    print("  ".join("-" * widths[col] for col in range(len(headers))))
    for row in table:
        print("  ".join(row[col].ljust(widths[col]) for col in range(len(headers))))


def assert_expected(rows: list[dict[str, object]], require_all: bool = True) -> None:
    by_name = {str(row["name"]): row for row in rows}
    for name, expected in EXPECTED.items():
        if name not in by_name:
            if require_all:
                raise AssertionError(f"missing built-in pattern {name}")
            continue
        row = by_name[name]
        if "midpoint_matrix_rank" in expected:
            actual_rank = row["midpoint_matrix_rank"]
            expected_rank = expected["midpoint_matrix_rank"]
            if actual_rank != expected_rank:
                raise AssertionError(f"{name}: rank {actual_rank} != {expected_rank}")
        if "forced_equality_classes" in expected:
            actual_classes = row["forced_equality_classes"]
            expected_classes = expected["forced_equality_classes"]
            if actual_classes != expected_classes:
                raise AssertionError(f"{name}: classes {actual_classes} != {expected_classes}")
        if expected.get("odd_cycle") and not row["odd_cycle_length"]:
            raise AssertionError(f"{name}: expected an odd forced-perpendicularity cycle")
        if expected.get("adjacent_two_overlap_violations") and not row[
            "adjacent_two_overlap_violations"
        ]:
            raise AssertionError(f"{name}: expected natural-order adjacent two-overlap violations")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print JSON instead of a table")
    parser.add_argument("--pattern", help="limit checks to one built-in pattern")
    parser.add_argument("--assert-expected", action="store_true", help="assert expected kills")
    args = parser.parse_args()

    patterns = built_in_patterns()
    if args.pattern:
        if args.pattern not in patterns:
            raise SystemExit(f"unknown pattern {args.pattern}; known: {', '.join(patterns)}")
        selected = [patterns[args.pattern]]
    else:
        selected = list(patterns.values())

    rows = [summarize_pattern(pattern) for pattern in selected]
    if args.assert_expected:
        assert_expected(rows, require_all=args.pattern is None)

    if args.json:
        print(json.dumps(rows, indent=2, sort_keys=True))
    else:
        print_table(rows)
        if args.assert_expected:
            print("OK: expected mutual-rhombus and crossing-bisector outcomes verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
