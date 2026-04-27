#!/usr/bin/env python3
"""Check cyclic-order crossing CSPs for two-overlap patterns."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.cyclic_crossing_csp import (  # noqa: E402
    all_constraints_cross,
    crossing_constraints,
    find_cyclic_crossing_order,
    result_to_json,
)
from erdos97.search import built_in_patterns  # noqa: E402


def assert_sat(row: dict[str, object]) -> None:
    if not row["sat"]:
        raise AssertionError(f"{row['pattern']}: expected SAT")


def assert_unsat(row: dict[str, object]) -> None:
    if row["sat"]:
        raise AssertionError(f"{row['pattern']}: expected UNSAT, got {row['order']}")


def print_table(rows: list[dict[str, object]]) -> None:
    headers = ["pattern", "n", "constraints", "result", "nodes", "max depth", "order"]
    table = []
    for row in rows:
        order = row["order"]
        table.append(
            [
                str(row["pattern"]),
                str(row["n"]),
                str(row["constraint_count"]),
                str(row["result"]),
                str(row["nodes_visited"]),
                str(row["max_depth"]),
                "-" if order is None else str(order),
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print JSON instead of a table")
    parser.add_argument("--pattern", help="limit checks to one built-in pattern")
    parser.add_argument("--assert-sat", action="store_true", help="assert selected pattern is SAT")
    parser.add_argument("--assert-unsat", action="store_true", help="assert selected pattern is UNSAT")
    parser.add_argument("--write-certificate", help="write a JSON certificate/result file")
    args = parser.parse_args()

    patterns = built_in_patterns()
    if args.pattern:
        if args.pattern not in patterns:
            raise SystemExit(f"unknown pattern {args.pattern}; known: {', '.join(patterns)}")
        selected = [patterns[args.pattern]]
    else:
        selected = [patterns["P18_parity_balanced"], patterns["P24_parity_balanced"]]

    rows: list[dict[str, object]] = []
    for pattern in selected:
        result = find_cyclic_crossing_order(pattern.S, pattern.name)
        row = result_to_json(result)
        if result.order is not None:
            constraints = crossing_constraints(pattern.S)
            if not all_constraints_cross(result.order, constraints):
                raise AssertionError(f"{pattern.name}: search returned an invalid order")
        rows.append(row)

    if args.assert_sat:
        for row in rows:
            assert_sat(row)
    if args.assert_unsat:
        for row in rows:
            assert_unsat(row)

    output: object = rows[0] if args.pattern and len(rows) == 1 else rows
    if args.write_certificate:
        path = Path(args.write_certificate)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(output, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    if args.json:
        print(json.dumps(output, indent=2, sort_keys=True))
    else:
        print_table(rows)
        if args.assert_sat or args.assert_unsat:
            print("OK: cyclic crossing CSP expectation verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
