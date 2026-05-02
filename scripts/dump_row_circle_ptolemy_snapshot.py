#!/usr/bin/env python3
"""Dump a row-circle Ptolemy active-set snapshot for exactification."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.row_circle_ptolemy_nlp import (  # noqa: E402
    row_circle_ptolemy_nlp_diagnostic,
    solution_snapshot_to_json,
)
from erdos97.search import built_in_patterns  # noqa: E402

C19_VERTEX_CIRCLE_SURVIVOR = [
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
]


def parse_order(raw: str) -> list[int]:
    try:
        return [int(item.strip()) for item in raw.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid comma-separated order: {raw}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pattern", default="C19_skew", help="built-in pattern name")
    parser.add_argument(
        "--order",
        type=parse_order,
        help="comma-separated cyclic order; defaults to the registered C19 survivor",
    )
    parser.add_argument("--order-label", default="vertex_circle_survivor")
    parser.add_argument("--out", required=True, help="write JSON snapshot to this path")
    parser.add_argument("--tolerance", type=float, default=1e-8)
    parser.add_argument("--tight-tolerance", type=float, default=None)
    parser.add_argument("--maxiter", type=int, default=3000)
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    patterns = built_in_patterns()
    if args.pattern not in patterns:
        raise SystemExit(f"unknown pattern {args.pattern}; known: {', '.join(patterns)}")
    order = args.order
    if order is None:
        if args.pattern != "C19_skew":
            raise SystemExit("--order is required unless --pattern C19_skew is used")
        order = C19_VERTEX_CIRCLE_SURVIVOR

    pattern = patterns[args.pattern]
    result = row_circle_ptolemy_nlp_diagnostic(
        pattern.S,
        order=order,
        pattern=pattern.name,
        tolerance=args.tolerance,
        maxiter=args.maxiter,
        include_solution=True,
    )
    snapshot = solution_snapshot_to_json(
        result,
        tight_tolerance=args.tight_tolerance,
    )
    snapshot["case"] = f"{pattern.name}:{args.order_label}"
    snapshot["order_label"] = args.order_label

    if args.assert_expected:
        assert_expected(snapshot)

    with Path(args.out).open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(snapshot, indent=2, sort_keys=True) + "\n")
    print(
        f"{snapshot['case']} {snapshot['status']} "
        f"gamma={snapshot['gamma']:.6g} "
        f"tight_linear={snapshot['counts']['tight_linear_rows']} "
        f"tight_ptolemy={snapshot['counts']['tight_ptolemy_rows']}"
    )
    if args.assert_expected:
        print("OK: row-circle Ptolemy snapshot expectations verified")
    return 0


def assert_expected(snapshot: dict[str, object]) -> None:
    if snapshot["case"] != "C19_skew:vertex_circle_survivor":
        raise AssertionError(f"unexpected snapshot case: {snapshot['case']}")
    if snapshot["status"] != "ROW_CIRCLE_PTOLEMY_NLP_NUMERICAL_OBSTRUCTION":
        raise AssertionError(f"unexpected C19 status: {snapshot['status']}")
    gamma = snapshot["gamma"]
    if not isinstance(gamma, float) or gamma >= -1e-4:
        raise AssertionError(f"C19 gamma is not negative enough: {gamma}")
    counts = snapshot["counts"]
    if not isinstance(counts, dict):
        raise AssertionError("snapshot counts missing")
    if counts.get("distance_classes") != 114:
        raise AssertionError(f"unexpected distance-class count: {counts}")
    if counts.get("tight_linear_rows") != 22:
        raise AssertionError(f"unexpected tight-linear count: {counts}")
    if counts.get("tight_ptolemy_rows") != 74:
        raise AssertionError(f"unexpected tight-Ptolemy count: {counts}")
    residual = snapshot["row_ptolemy_max_abs_residual"]
    if not isinstance(residual, float) or residual > 1e-12:
        raise AssertionError(f"row-Ptolemy residual too large: {residual}")


if __name__ == "__main__":
    raise SystemExit(main())
