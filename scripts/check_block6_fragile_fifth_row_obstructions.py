#!/usr/bin/env python3
"""Catalog one-row vertex-circle obstructions for the block-6 fragile audit."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.check_block6_fragile_vertex_circle_extension import (  # noqa: E402
    _add_row,
    _initial_state,
    _options,
    _partial_vertex_circle_status,
    _remove_row,
    _valid_options,
)

EXPECTED_CENTER_COUNTS = {
    "1": {"valid": 38, "ok": 21, "self_edge": 7, "strict_cycle": 10},
    "2": {"valid": 64, "ok": 41, "self_edge": 13, "strict_cycle": 10},
    "4": {"valid": 38, "ok": 7, "self_edge": 14, "strict_cycle": 17},
    "5": {"valid": 31, "ok": 14, "self_edge": 7, "strict_cycle": 10},
    "7": {"valid": 38, "ok": 21, "self_edge": 7, "strict_cycle": 10},
    "8": {"valid": 64, "ok": 41, "self_edge": 13, "strict_cycle": 10},
    "10": {"valid": 38, "ok": 7, "self_edge": 14, "strict_cycle": 17},
    "11": {"valid": 31, "ok": 14, "self_edge": 7, "strict_cycle": 10},
}
EXPECTED_TOTALS = {
    "valid": 342,
    "ok": 166,
    "self_edge": 82,
    "strict_cycle": 94,
}
STATUSES = ("ok", "self_edge", "strict_cycle")


def _json_counter(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def catalog_payload(*, include_rows: bool = False) -> dict[str, Any]:
    """Classify every legal one-row extension of the fixed block-6 rows."""

    assigned, pair_counts, indegrees = _initial_state()
    options = _options()
    fixed_centers = sorted(assigned)
    center_payload: dict[str, dict[str, Any]] = {}
    totals: Counter[str] = Counter()

    for center in range(len(options)):
        if center in assigned:
            continue
        valid_rows = _valid_options(
            center,
            options,
            assigned,
            pair_counts,
            indegrees,
        )
        status_counts: Counter[str] = Counter()
        edge_counts: Counter[int] = Counter()
        examples: dict[str, list[int]] = {}
        row_records: list[dict[str, Any]] = []

        for row in valid_rows:
            _add_row(assigned, pair_counts, indegrees, center, row)
            status, edge_count = _partial_vertex_circle_status(assigned)
            _remove_row(assigned, pair_counts, indegrees, center, row)

            status_counts[status] += 1
            edge_counts[edge_count] += 1
            examples.setdefault(status, list(row))
            if include_rows:
                row_records.append(
                    {
                        "row": list(row),
                        "vertex_circle_status": status,
                        "strict_edge_count": edge_count,
                    }
                )

        center_record: dict[str, Any] = {
            "valid": len(valid_rows),
            "ok": int(status_counts["ok"]),
            "self_edge": int(status_counts["self_edge"]),
            "strict_cycle": int(status_counts["strict_cycle"]),
            "strict_edge_count_histogram": _json_counter(edge_counts),
            "first_examples": examples,
        }
        if include_rows:
            center_record["rows"] = row_records
        center_payload[str(center)] = center_record
        totals.update({"valid": len(valid_rows)})
        for status in STATUSES:
            totals.update({status: status_counts[status]})

    return {
        "schema": "erdos97.block6_fragile_fifth_row_obstruction_catalog.v1",
        "status": "REVIEW_PENDING_DIAGNOSTIC_ONLY",
        "claim_scope": (
            "Legal one-row extensions of the two-block block-6 fragile rows "
            "in the natural cyclic order; not a proof of Erdos Problem #97 "
            "and not a counterexample."
        ),
        "fixed_centers": fixed_centers,
        "fixed_rows": {str(center): list(assigned[center]) for center in fixed_centers},
        "center_counts": center_payload,
        "totals": {key: int(totals[key]) for key in ("valid", *STATUSES)},
    }


def assert_expected(payload: Mapping[str, Any]) -> None:
    if payload["status"] != "REVIEW_PENDING_DIAGNOSTIC_ONLY":
        raise AssertionError("unexpected status")
    if "not a proof" not in payload["claim_scope"]:
        raise AssertionError("claim scope lost no-proof note")
    if payload["totals"] != EXPECTED_TOTALS:
        raise AssertionError(f"unexpected totals: {payload['totals']!r}")
    actual_centers = {
        center: {
            key: record[key]
            for key in ("valid", "ok", "self_edge", "strict_cycle")
        }
        for center, record in payload["center_counts"].items()
    }
    if actual_centers != EXPECTED_CENTER_COUNTS:
        raise AssertionError(f"unexpected center counts: {actual_centers!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print full JSON payload")
    parser.add_argument(
        "--include-rows",
        action="store_true",
        help="include every legal fifth-row classification in the JSON payload",
    )
    parser.add_argument(
        "--assert-expected",
        action="store_true",
        help="assert the current expected catalog counts",
    )
    args = parser.parse_args()

    payload = catalog_payload(include_rows=args.include_rows)
    if args.assert_expected:
        assert_expected(payload)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        totals = payload["totals"]
        print("block6 fragile fifth-row obstruction catalog")
        print(f"fixed centers: {payload['fixed_centers']}")
        print(
            "totals: "
            f"valid={totals['valid']} ok={totals['ok']} "
            f"self_edge={totals['self_edge']} "
            f"strict_cycle={totals['strict_cycle']}"
        )
        if args.assert_expected:
            print("OK: block6 fifth-row catalog matched expected counts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
