#!/usr/bin/env python3
"""Run the Ptolemy-strengthened fixed-order nonlinear diagnostic."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.ptolemy_order_nlp import (  # noqa: E402
    ptolemy_order_nlp_diagnostic,
    result_to_json,
)
from erdos97.search import PatternInfo, built_in_patterns  # noqa: E402

REGISTERED_ORDERS: dict[str, dict[str, list[int]]] = {
    "C13_sidon_1_2_4_10": {
        "sample_full_filter_survivor": [5, 0, 10, 8, 9, 7, 4, 6, 2, 11, 12, 3, 1],
    },
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


def parse_order(raw: str) -> list[int]:
    try:
        return [int(item.strip()) for item in raw.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid comma-separated order: {raw}") from exc


def evaluate_order(
    pattern: PatternInfo,
    order: list[int],
    order_label: str,
    *,
    tolerance: float,
    maxiter: int,
) -> dict[str, object]:
    result = ptolemy_order_nlp_diagnostic(
        pattern.S,
        order=order,
        pattern=pattern.name,
        tolerance=tolerance,
        maxiter=maxiter,
    )
    row = result_to_json(result)
    row["case"] = f"{pattern.name}:{order_label}"
    row["order_label"] = order_label
    return row


def registered_rows(
    patterns: dict[str, PatternInfo],
    *,
    tolerance: float = 1e-8,
    maxiter: int = 1500,
) -> list[dict[str, object]]:
    rows = []
    for pattern_name, orders in REGISTERED_ORDERS.items():
        pattern = patterns[pattern_name]
        for order_label, order in orders.items():
            rows.append(
                evaluate_order(
                    pattern,
                    order,
                    order_label,
                    tolerance=tolerance,
                    maxiter=maxiter,
                )
            )
    return rows


def assert_expected(rows: list[dict[str, object]]) -> None:
    by_case = {str(row["case"]): row for row in rows}
    expected = {
        "C13_sidon_1_2_4_10:sample_full_filter_survivor",
        "C19_skew:vertex_circle_survivor",
    }
    missing = sorted(expected - set(by_case))
    if missing:
        raise AssertionError(f"missing expected case(s): {', '.join(missing)}")
    for case in sorted(expected):
        row = by_case[case]
        if row["status"] != "PASS_PTOLEMY_ORDER_NLP_RELAXATION":
            raise AssertionError(f"{case} did not pass the Ptolemy-order NLP")
        margin = row["max_margin"]
        if not isinstance(margin, float) or margin <= 5e-4:
            raise AssertionError(f"{case} has an unexpectedly small margin: {margin}")


def payload(rows: list[dict[str, object]]) -> dict[str, object]:
    return {
        "type": "ptolemy_order_nlp_registered_survivor_sweep_v1",
        "trust": "NUMERICAL_NONLINEAR_DIAGNOSTIC",
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "Passing this nonlinear relaxation is not evidence of geometric realizability.",
            "An obstruction from this diagnostic would require exactification before use.",
        ],
        "cases": rows,
    }


def print_table(rows: list[dict[str, object]]) -> None:
    headers = [
        "case",
        "n",
        "status",
        "margin",
        "linear",
        "ptolemy",
    ]
    table = [
        [
            str(row["case"]),
            str(row["n"]),
            str(row["status"]),
            f"{row['max_margin']:.6g}" if isinstance(row["max_margin"], float) else "-",
            str(row["linear_inequality_count"]),
            str(row["ptolemy_inequality_count"]),
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
    parser.add_argument("--pattern", help="built-in pattern name for a supplied --order")
    parser.add_argument("--order", type=parse_order, help="comma-separated cyclic order")
    parser.add_argument("--order-label", default="supplied", help="label for --order")
    parser.add_argument("--tolerance", type=float, default=1e-8)
    parser.add_argument("--maxiter", type=int, default=1500)
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    patterns = built_in_patterns()
    if args.order is not None:
        if not args.pattern:
            raise SystemExit("--pattern is required with --order")
        if args.pattern not in patterns:
            raise SystemExit(f"unknown pattern {args.pattern}; known: {', '.join(patterns)}")
        rows = [
            evaluate_order(
                patterns[args.pattern],
                args.order,
                args.order_label,
                tolerance=args.tolerance,
                maxiter=args.maxiter,
            )
        ]
    else:
        if args.pattern:
            raise SystemExit("--pattern requires --order")
        rows = registered_rows(
            patterns,
            tolerance=args.tolerance,
            maxiter=args.maxiter,
        )

    if args.assert_expected:
        assert_expected(rows)
    data = payload(rows)
    if args.out:
        with Path(args.out).open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(data, indent=2, sort_keys=True) + "\n")
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print_table(rows)
        if args.assert_expected:
            print("OK: Ptolemy-order NLP expectations verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
