#!/usr/bin/env python3
"""Reduce duplicate row/global Ptolemy multipliers in a snapshot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

PT_LABELS = ("ac", "bd", "ab", "cd", "bc", "ad")


def ptolemy_key(row: dict[str, Any]) -> tuple[tuple[int, int], tuple[tuple[int, int], tuple[int, int]]]:
    classes = row["classes"]
    values = {label: int(classes[label]["class_index"]) for label in PT_LABELS}
    negative = tuple(sorted((values["ac"], values["bd"])))
    positive = tuple(
        sorted(
            (
                tuple(sorted((values["ab"], values["cd"]))),
                tuple(sorted((values["bc"], values["ad"]))),
            )
        )
    )
    return negative, positive


def reduce_snapshot(snapshot: dict[str, Any], source: str) -> dict[str, Any]:
    by_key: dict[object, list[dict[str, Any]]] = {}
    for row in snapshot["tight_ptolemy_rows"]:
        by_key.setdefault(ptolemy_key(row), []).append(row)

    reductions = []
    unmatched = []
    for row in snapshot["row_ptolemy_rows"]:
        matches = by_key.get(ptolemy_key(row), [])
        if len(matches) != 1:
            unmatched.append(
                {
                    "center": row["center"],
                    "witnesses": row["witnesses"],
                    "match_count": len(matches),
                }
            )
            continue
        match = matches[0]
        row_multiplier = float(row.get("multiplier", 0.0))
        ptolemy_multiplier = float(match.get("multiplier", 0.0))
        reductions.append(
            {
                "center": row["center"],
                "row_witnesses": row["witnesses"],
                "global_ptolemy_index": match["index"],
                "global_vertices": match["vertices"],
                "row_multiplier": row_multiplier,
                "global_ptolemy_multiplier": ptolemy_multiplier,
                "combined_multiplier": row_multiplier + ptolemy_multiplier,
                "row_residual": row["residual"],
                "global_slack": match["slack"],
            }
        )

    combined = [abs(row["combined_multiplier"]) for row in reductions]
    original_row = [abs(row["row_multiplier"]) for row in reductions]
    original_global = [abs(row["global_ptolemy_multiplier"]) for row in reductions]
    return {
        "type": "row_circle_ptolemy_multiplier_reduction_v1",
        "trust": "NUMERICAL_NONLINEAR_DIAGNOSTIC",
        "source_snapshot": source,
        "pattern": snapshot["pattern"],
        "case": snapshot["case"],
        "status": snapshot["status"],
        "row_global_duplicate_count": len(reductions),
        "unmatched_rows": unmatched,
        "max_abs_original_row_multiplier": max(original_row) if original_row else None,
        "max_abs_original_global_multiplier": max(original_global) if original_global else None,
        "max_abs_combined_multiplier": max(combined) if combined else None,
        "reductions": reductions,
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "This file only reduces numerical SLSQP multiplier bookkeeping.",
            "Large row-circle equality multipliers often cancel against the matching global Ptolemy inequality multiplier.",
        ],
    }


def assert_expected(payload: dict[str, Any]) -> None:
    if payload["case"] != "C19_skew:vertex_circle_survivor":
        raise AssertionError(f"unexpected case: {payload['case']}")
    if payload["row_global_duplicate_count"] != 19:
        raise AssertionError("expected all 19 row equalities to match a global Ptolemy row")
    if payload["unmatched_rows"]:
        raise AssertionError(f"unexpected unmatched rows: {payload['unmatched_rows']}")
    max_combined = payload["max_abs_combined_multiplier"]
    if not isinstance(max_combined, float) or max_combined > 25:
        raise AssertionError(f"unexpected reduced multiplier scale: {max_combined}")
    max_original = payload["max_abs_original_row_multiplier"]
    if not isinstance(max_original, float) or max_original < 1e16:
        raise AssertionError(f"expected large original multipliers: {max_original}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--snapshot",
        default="data/certificates/c19_row_circle_ptolemy_active_set.json",
        help="input row-circle Ptolemy snapshot JSON",
    )
    parser.add_argument("--out", required=True, help="write reduced JSON payload")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    snapshot_path = Path(args.snapshot)
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    payload = reduce_snapshot(snapshot, args.snapshot)
    if args.assert_expected:
        assert_expected(payload)
    with Path(args.out).open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(
        f"{payload['case']} row-global duplicates={payload['row_global_duplicate_count']} "
        f"max_combined={payload['max_abs_combined_multiplier']:.6g}"
    )
    if args.assert_expected:
        print("OK: row-circle multiplier reduction expectations verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
