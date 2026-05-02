#!/usr/bin/env python3
"""Sweep exact Altman linear certificates over built-in pattern orders."""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.altman_diagonal_sums import altman_order_linear_certificate  # noqa: E402
from erdos97.search import PatternInfo, built_in_patterns  # noqa: E402

KNOWN_ABSTRACT_ORDERS: dict[str, dict[str, list[int]]] = {
    "C19_skew": {
        "vertex_circle_survivor": [
            18,
            10,
            7,
            17,
            6,
            3,
            5,
            9,
            14,
            11,
            2,
            13,
            4,
            16,
            12,
            15,
            0,
            8,
            1,
        ],
    },
}

EXPECTED_NATURAL_OBSTRUCTIONS = {
    "C13_sidon_1_2_4_10",
    "C19_skew",
    "C25_sidon_2_5_9_14",
    "C29_sidon_1_3_7_15",
}


def sweep_cases(
    patterns: dict[str, PatternInfo],
    include_known_abstract: bool,
    max_denominator: int,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for pattern in patterns.values():
        rows.append(
            _case_row(
                pattern=pattern,
                order_label="natural",
                order=list(range(pattern.n)),
                max_denominator=max_denominator,
            )
        )
        if include_known_abstract:
            for order_label, order in KNOWN_ABSTRACT_ORDERS.get(pattern.name, {}).items():
                rows.append(
                    _case_row(
                        pattern=pattern,
                        order_label=order_label,
                        order=order,
                        max_denominator=max_denominator,
                    )
                )
    return rows


def _case_row(
    pattern: PatternInfo,
    order_label: str,
    order: list[int],
    max_denominator: int,
) -> dict[str, object]:
    result = altman_order_linear_certificate(
        pattern.S,
        order,
        pattern.name,
        max_denominator=max_denominator,
    )
    row = dataclasses.asdict(result)
    return {
        "case": f"{pattern.name}:{order_label}",
        "pattern": pattern.name,
        "order_label": order_label,
        **row,
    }


def sweep_payload(
    rows: list[dict[str, object]],
    max_denominator: int,
) -> dict[str, object]:
    return {
        "type": "altman_linear_certificate_sweep_v1",
        "trust": "FIXED_ORDER_EXACT_WHEN_CERTIFIED",
        "max_denominator": max_denominator,
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "Rows with NO_EXACT_ALTMAN_LINEAR_CERTIFICATE_FOUND are only certificate-search misses.",
        ],
        "cases": rows,
    }


def assert_expected(rows: list[dict[str, object]]) -> None:
    by_case = {str(row["case"]): row for row in rows}
    missing = [
        f"{pattern}:natural"
        for pattern in sorted(EXPECTED_NATURAL_OBSTRUCTIONS)
        if f"{pattern}:natural" not in by_case
    ]
    if missing:
        raise AssertionError(f"missing expected case(s): {', '.join(missing)}")
    for pattern in sorted(EXPECTED_NATURAL_OBSTRUCTIONS):
        row = by_case[f"{pattern}:natural"]
        if row["status"] != "EXACT_ALTMAN_LINEAR_OBSTRUCTION":
            raise AssertionError(f"{pattern}:natural was not certified")
    c19_abstract = by_case.get("C19_skew:vertex_circle_survivor")
    if c19_abstract is None:
        raise AssertionError("missing C19_skew:vertex_circle_survivor")
    if c19_abstract["status"] != "NO_EXACT_ALTMAN_LINEAR_CERTIFICATE_FOUND":
        raise AssertionError("known abstract C19 order unexpectedly certified")


def print_table(rows: list[dict[str, object]]) -> None:
    headers = ["case", "n", "status", "method", "nonzero gaps"]
    table = [
        [
            str(row["case"]),
            str(row["n"]),
            str(row["status"]),
            str(row["certificate_method"]),
            str(row["nonzero_gap_orders"]),
        ]
        for row in rows
    ]
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
    parser.add_argument("--json", action="store_true", help="print JSON")
    parser.add_argument("--out", help="write JSON payload to this path")
    parser.add_argument("--pattern", help="limit sweep to one built-in pattern")
    parser.add_argument(
        "--natural-only",
        action="store_true",
        help="skip registered non-natural abstract orders",
    )
    parser.add_argument(
        "--max-denominator",
        type=int,
        default=1000,
        help="maximum denominator for rationalized LP-dual certificate weights",
    )
    parser.add_argument(
        "--assert-expected",
        action="store_true",
        help="assert currently registered sweep expectations",
    )
    args = parser.parse_args()

    patterns = built_in_patterns()
    if args.pattern:
        if args.pattern not in patterns:
            raise SystemExit(f"unknown pattern {args.pattern}; known: {', '.join(patterns)}")
        patterns = {args.pattern: patterns[args.pattern]}
    rows = sweep_cases(
        patterns=patterns,
        include_known_abstract=not args.natural_only,
        max_denominator=args.max_denominator,
    )
    if args.assert_expected:
        assert_expected(rows)
    payload = sweep_payload(rows, max_denominator=args.max_denominator)
    if args.out:
        with Path(args.out).open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(payload, indent=2) + "\n")
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_table(rows)
        if args.assert_expected:
            print("OK: Altman linear certificate sweep expectations verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
