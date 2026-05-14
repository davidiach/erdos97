#!/usr/bin/env python3
"""Check the two-stage closure crosswalk for reversed-block shuffles."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.check_block6_reversed_block_clean_kalmanson import (  # noqa: E402
    OUT as KALMANSON_OUT,
    assert_expected as assert_kalmanson_expected,
    check_artifact as check_kalmanson_artifact,
)
from scripts.check_block6_reversed_block_shuffle_vertex_circle_escape import (  # noqa: E402
    EXPECTED_CLEAN_INDICES,
    OUT as VERTEX_CIRCLE_OUT,
    assert_expected as assert_vertex_circle_expected,
)
from scripts.check_block6_terminal_crossing_vertex_circle_sample import (  # noqa: E402
    write_json,
)

OUT = ROOT / "data" / "certificates" / "block6_reversed_block_two_stage_closure.json"
SCHEMA = "erdos97.block6_reversed_block_two_stage_closure.v1"
STATUS = "BOUNDED_FIXED_ORDER_FAMILY_TWO_STAGE_CLOSURE_DIAGNOSTIC"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
PROVENANCE = {
    "generator": "scripts/check_block6_reversed_block_two_stage_closure.py",
    "command": (
        "python scripts/check_block6_reversed_block_two_stage_closure.py "
        "--write --assert-expected"
    ),
}
CLAIM_SCOPE = (
    "Two-stage fixed-order-family crosswalk for the 462 reversed-second-block "
    "shuffle orders only. It combines vertex-circle quotient closure for 446 "
    "orders with exact fixed-order Kalmanson certificates for the 16 stored "
    "vertex-circle-clean escape rows. This is not all-order closure, not a "
    "fragile-bridge proof, not a proof of Erdos Problem #97, and not a "
    "counterexample."
)

EXPECTED_SUMMARY = {
    "family_order_count": 462,
    "vertex_circle_closed_order_count": 446,
    "vertex_circle_clean_order_count": 16,
    "kalmanson_obstructed_clean_order_count": 16,
    "combined_closed_order_count": 462,
    "combined_closure_complete": True,
    "kalmanson_strict_rows_total": 394,
    "kalmanson_weight_sum_total": 16850,
    "method_counts": {
        "vertex_circle_quotient": 446,
        "kalmanson_after_vertex_circle_escape": 16,
    },
}


def _load_vertex_circle() -> dict[str, Any]:
    data = json.loads(VERTEX_CIRCLE_OUT.read_text(encoding="utf-8"))
    assert_vertex_circle_expected(data)
    return data


def _clean_order_summary(record: Mapping[str, Any]) -> dict[str, object]:
    return {
        "index": int(record["index"]),
        "cyclic_order": record["cyclic_order"],
        "strict_rows": int(record["strict_rows"]),
        "distance_classes": int(record["distance_classes"]),
        "weight_sum": int(record["weight_sum"]),
        "max_weight": int(record["max_weight"]),
        "zero_sum_verified": bool(record["zero_sum_verified"]),
    }


def payload() -> dict[str, object]:
    vc = _load_vertex_circle()
    kalmanson = check_kalmanson_artifact()
    assert_kalmanson_expected(kalmanson)

    vc_summary = vc["summary"]
    kal_summary = kalmanson["summary"]
    vc_clean_indices = [int(record["index"]) for record in vc["clean_order_records"]]
    kal_records = list(kalmanson["certificate_records"])  # type: ignore[index]
    kal_indices = [int(record["index"]) for record in kal_records]
    source_clean_indices_match = (
        vc_clean_indices == kal_indices == list(EXPECTED_CLEAN_INDICES)
    )
    combined_closed = int(vc_summary["closed_order_count"]) + int(
        kal_summary["obstructed_clean_order_count"]
    )
    summary = {
        "family_order_count": int(vc_summary["shuffle_order_count"]),
        "vertex_circle_closed_order_count": int(vc_summary["closed_order_count"]),
        "vertex_circle_clean_order_count": int(
            vc_summary["orders_with_clean_pruned_solution"]
        ),
        "kalmanson_obstructed_clean_order_count": int(
            kal_summary["obstructed_clean_order_count"]
        ),
        "combined_closed_order_count": combined_closed,
        "combined_closure_complete": (
            combined_closed == int(vc_summary["shuffle_order_count"])
            and source_clean_indices_match
        ),
        "source_clean_indices_match": source_clean_indices_match,
        "clean_order_indices": kal_indices,
        "kalmanson_strict_rows_total": int(kal_summary["strict_rows_total"]),
        "kalmanson_weight_sum_total": int(kal_summary["weight_sum_total"]),
        "method_counts": {
            "vertex_circle_quotient": int(vc_summary["closed_order_count"]),
            "kalmanson_after_vertex_circle_escape": int(
                kal_summary["obstructed_clean_order_count"]
            ),
        },
    }
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "source_artifacts": {
            "vertex_circle_escape": {
                "path": VERTEX_CIRCLE_OUT.relative_to(ROOT).as_posix(),
                "schema": vc["schema"],
                "status": vc["status"],
            },
            "clean_kalmanson": {
                "path": KALMANSON_OUT.relative_to(ROOT).as_posix(),
                "schema": kalmanson["schema"],
                "status": kalmanson["status"],
            },
        },
        "summary": summary,
        "clean_order_crosswalk": [
            _clean_order_summary(record) for record in kal_records
        ],
        "provenance": PROVENANCE,
        "interpretation": (
            "Within the reversed-second-block shuffle family, the vertex-circle "
            "gate closes 446 fixed orders and leaves 16 clean assignment/order "
            "pairs. The clean set is exactly the set certified by the "
            "fixed-order Kalmanson packet, so the combined two-stage gate "
            "closes this bounded 462-order family."
        ),
    }


def check_artifact() -> dict[str, object]:
    data = json.loads(OUT.read_text(encoding="utf-8"))
    expected = payload()
    if data != expected:
        raise AssertionError("stored two-stage closure artifact differs")
    return data


def assert_expected(data: Mapping[str, object]) -> None:
    expected = {
        **EXPECTED_SUMMARY,
        "source_clean_indices_match": True,
        "clean_order_indices": EXPECTED_CLEAN_INDICES,
    }
    if data["summary"] != expected:
        raise AssertionError("unexpected two-stage closure summary")
    if "not a counterexample" not in str(data["claim_scope"]):
        raise AssertionError("claim scope lost counterexample guard")
    records = data["clean_order_crosswalk"]
    if not isinstance(records, list) or len(records) != 16:
        raise AssertionError("unexpected clean-order crosswalk")
    if not all(record["zero_sum_verified"] for record in records):
        raise AssertionError("expected every clean-order certificate to verify")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    data = check_artifact() if args.check else payload()
    if args.assert_expected:
        assert_expected(data)
    if args.write:
        write_json(data, OUT)

    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        summary = data["summary"]
        print("block6 reversed-block two-stage closure crosswalk")
        print(f"family orders: {summary['family_order_count']}")
        print(f"vertex-circle closed: {summary['vertex_circle_closed_order_count']}")
        print(
            "Kalmanson-clean closures: "
            f"{summary['kalmanson_obstructed_clean_order_count']}"
        )
        print(f"combined closed: {summary['combined_closed_order_count']}")
        if args.assert_expected:
            print("OK: expected two-stage closure crosswalk verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
