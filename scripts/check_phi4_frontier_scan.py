#!/usr/bin/env python3
"""Run the phi 4-cycle rectangle-trap frontier scan."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.phi4_frontier import (  # noqa: E402
    built_in_natural_order_cases,
    n9_rectangle_trap_case,
    scan_cases,
    scan_payload,
    sparse_order_cases_from_payload,
)
from erdos97.search import built_in_patterns  # noqa: E402

DEFAULT_SPARSE_ORDERS = ROOT / "data" / "certificates" / "sparse_order_survivors.json"
DEFAULT_OUT = ROOT / "data" / "certificates" / "phi4_frontier_scan.json"


def load_sparse_payload(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} should contain a JSON object")
    return payload


def build_rows(args: argparse.Namespace) -> list[dict[str, object]]:
    patterns = built_in_patterns()
    cases = []
    if args.include_n9:
        cases.append(n9_rectangle_trap_case())
    if args.include_builtins:
        cases.extend(built_in_natural_order_cases(patterns))
    if args.include_sparse_orders:
        payload = load_sparse_payload(Path(args.sparse_orders))
        cases.extend(sparse_order_cases_from_payload(payload, patterns))
    return scan_cases(cases)


def assert_expected(rows: list[dict[str, object]]) -> None:
    by_case = {str(row["case"]): row for row in rows}
    n9 = "N9_phi4_rectangle_trap_selected_witness_pattern:natural_order"
    if n9 not in by_case:
        raise AssertionError("missing registered n=9 rectangle-trap case")
    if by_case[n9]["rectangle_trap_4_cycles"] != 1:
        raise AssertionError("registered n=9 case should have one rectangle trap")

    unexpected = [
        row["case"]
        for row in rows
        if row["case"] != n9 and row["obstructed_by_phi4_rectangle_trap"]
    ]
    if unexpected:
        raise AssertionError(f"unexpected phi4 rectangle-trap hit(s): {unexpected}")


def print_table(rows: list[dict[str, object]]) -> None:
    headers = ["case", "n", "phi", "4cycles", "rect4", "status"]
    table = []
    for row in rows:
        status = "OBSTRUCTED" if row["obstructed_by_phi4_rectangle_trap"] else "pass"
        table.append(
            [
                str(row["case"]),
                str(row["n"]),
                str(row["phi_edges"]),
                str(row["directed_phi_4_cycle_count"]),
                str(row["rectangle_trap_4_cycles"]),
                status,
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
    parser.add_argument("--json", action="store_true", help="print full JSON")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="write JSON payload to this path")
    parser.add_argument("--write", action="store_true", help="write --out")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--sparse-orders", default=str(DEFAULT_SPARSE_ORDERS))
    parser.add_argument("--no-n9", dest="include_n9", action="store_false")
    parser.add_argument("--no-builtins", dest="include_builtins", action="store_false")
    parser.add_argument(
        "--no-sparse-orders",
        dest="include_sparse_orders",
        action="store_false",
    )
    parser.set_defaults(include_n9=True, include_builtins=True, include_sparse_orders=True)
    args = parser.parse_args()

    rows = build_rows(args)
    if args.assert_expected:
        assert_expected(rows)
    payload = scan_payload(rows)

    if args.write:
        path = Path(args.out)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_table(rows)
        if args.assert_expected:
            print("OK: phi4 frontier scan expectations verified")
        if args.write:
            print(f"wrote {Path(args.out).relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
