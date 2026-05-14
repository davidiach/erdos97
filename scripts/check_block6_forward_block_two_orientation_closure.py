#!/usr/bin/env python3
"""Check the first-block-forward two-orientation block-6 crosswalk."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.check_block6_reversed_block_two_stage_closure import (  # noqa: E402
    OUT as REVERSED_TWO_STAGE_OUT,
    assert_expected as assert_reversed_expected,
    check_artifact as check_reversed_artifact,
)
from scripts.check_block6_shuffle_order_vertex_circle_sweep import (  # noqa: E402
    OUT as FORWARD_VERTEX_CIRCLE_OUT,
    assert_expected as assert_forward_expected,
)
from scripts.check_block6_terminal_crossing_vertex_circle_sample import (  # noqa: E402
    write_json,
)

OUT = (
    ROOT
    / "data"
    / "certificates"
    / "block6_forward_block_two_orientation_closure.json"
)
SCHEMA = "erdos97.block6_forward_block_two_orientation_closure.v1"
STATUS = "BOUNDED_FIXED_ORDER_TWO_ORIENTATION_CLOSURE_DIAGNOSTIC"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
PROVENANCE = {
    "generator": "scripts/check_block6_forward_block_two_orientation_closure.py",
    "command": (
        "python scripts/check_block6_forward_block_two_orientation_closure.py "
        "--write --assert-expected"
    ),
}
CLAIM_SCOPE = (
    "Cross-artifact fixed-order-family diagnostic for the 924 normalized "
    "block-6 shuffle orders with the first six-label block kept in forward "
    "orientation and the second block allowed in forward or reversed "
    "orientation. It combines 462 vertex-circle closures from the "
    "forward-second-block packet with the 462-order reversed-second-block "
    "two-stage closure packet. This does not include first-block-reversed "
    "orientations, arbitrary cyclic orders, all selected-row systems, the "
    "fragile bridge, a proof of Erdos Problem #97, or a counterexample."
)

EXPECTED_SUMMARY = {
    "first_block_orientation": "forward",
    "second_block_orientation_count": 2,
    "forward_second_block_order_count": 462,
    "reversed_second_block_order_count": 462,
    "total_family_order_count": 924,
    "forward_second_block_closed_order_count": 462,
    "reversed_second_block_closed_order_count": 462,
    "combined_closed_order_count": 924,
    "combined_closure_complete": True,
    "vertex_circle_closed_order_count": 908,
    "kalmanson_after_vertex_circle_escape_count": 16,
    "reversed_clean_escape_order_count": 16,
    "method_counts": {
        "forward_second_block_vertex_circle": 462,
        "reversed_second_block_vertex_circle": 446,
        "reversed_second_block_kalmanson_after_vertex_circle_escape": 16,
    },
}


def _load_forward_vertex_circle() -> dict[str, Any]:
    data = json.loads(FORWARD_VERTEX_CIRCLE_OUT.read_text(encoding="utf-8"))
    assert_forward_expected(data)
    return data


def _family_summary(
    *,
    name: str,
    orientation: str,
    artifact_path: Path,
    data: Mapping[str, Any],
    closure_methods: Mapping[str, int],
) -> dict[str, object]:
    summary = data["summary"]
    return {
        "name": name,
        "second_block_orientation": orientation,
        "path": artifact_path.relative_to(ROOT).as_posix(),
        "schema": data["schema"],
        "status": data["status"],
        "order_count": int(
            summary.get("shuffle_order_count", summary.get("family_order_count", 0))
        ),
        "closed_order_count": int(
            summary.get("closed_order_count", summary.get("combined_closed_order_count", 0))
        ),
        "closure_methods": dict(closure_methods),
    }


def payload() -> dict[str, object]:
    forward = _load_forward_vertex_circle()
    reversed_two_stage = check_reversed_artifact()
    assert_reversed_expected(reversed_two_stage)

    forward_summary = forward["summary"]
    reversed_summary = reversed_two_stage["summary"]

    forward_order_count = int(forward_summary["shuffle_order_count"])
    reversed_order_count = int(reversed_summary["family_order_count"])
    forward_closed = int(forward_summary["closed_order_count"])
    reversed_closed = int(reversed_summary["combined_closed_order_count"])
    reversed_vc_closed = int(reversed_summary["vertex_circle_closed_order_count"])
    reversed_kalmanson_closed = int(
        reversed_summary["kalmanson_obstructed_clean_order_count"]
    )
    summary = {
        "first_block_orientation": "forward",
        "second_block_orientation_count": 2,
        "forward_second_block_order_count": forward_order_count,
        "reversed_second_block_order_count": reversed_order_count,
        "total_family_order_count": forward_order_count + reversed_order_count,
        "forward_second_block_closed_order_count": forward_closed,
        "reversed_second_block_closed_order_count": reversed_closed,
        "combined_closed_order_count": forward_closed + reversed_closed,
        "combined_closure_complete": (
            forward_closed == forward_order_count
            and reversed_closed == reversed_order_count
        ),
        "vertex_circle_closed_order_count": forward_closed + reversed_vc_closed,
        "kalmanson_after_vertex_circle_escape_count": reversed_kalmanson_closed,
        "reversed_clean_escape_order_count": int(
            reversed_summary["vertex_circle_clean_order_count"]
        ),
        "method_counts": {
            "forward_second_block_vertex_circle": forward_closed,
            "reversed_second_block_vertex_circle": reversed_vc_closed,
            "reversed_second_block_kalmanson_after_vertex_circle_escape": (
                reversed_kalmanson_closed
            ),
        },
    }
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "source_artifacts": {
            "forward_second_block_vertex_circle": {
                "path": FORWARD_VERTEX_CIRCLE_OUT.relative_to(ROOT).as_posix(),
                "schema": forward["schema"],
                "status": forward["status"],
            },
            "reversed_second_block_two_stage": {
                "path": REVERSED_TWO_STAGE_OUT.relative_to(ROOT).as_posix(),
                "schema": reversed_two_stage["schema"],
                "status": reversed_two_stage["status"],
            },
        },
        "summary": summary,
        "family_crosswalk": [
            _family_summary(
                name="forward_second_block",
                orientation="forward",
                artifact_path=FORWARD_VERTEX_CIRCLE_OUT,
                data=forward,
                closure_methods={"vertex_circle_quotient": forward_closed},
            ),
            _family_summary(
                name="reversed_second_block",
                orientation="reversed",
                artifact_path=REVERSED_TWO_STAGE_OUT,
                data=reversed_two_stage,
                closure_methods={
                    "vertex_circle_quotient": reversed_vc_closed,
                    "kalmanson_after_vertex_circle_escape": reversed_kalmanson_closed,
                },
            ),
        ],
        "provenance": PROVENANCE,
        "interpretation": (
            "For the two block-preserving shuffle families with first block in "
            "forward orientation, the forward-second-block packet closes all "
            "462 orders by vertex-circle quotient pruning. The reversed-second-"
            "block packet closes 446 orders by vertex-circle pruning and the "
            "remaining 16 stored clean escape rows by fixed-order Kalmanson "
            "certificates. The aggregate 924-order count is a convenience "
            "crosswalk only and does not widen to first-block-reversed or "
            "arbitrary cyclic orders."
        ),
    }


def check_artifact() -> dict[str, object]:
    data = json.loads(OUT.read_text(encoding="utf-8"))
    expected = payload()
    if data != expected:
        raise AssertionError("stored two-orientation closure artifact differs")
    return data


def assert_expected(data: Mapping[str, object]) -> None:
    if data["summary"] != EXPECTED_SUMMARY:
        raise AssertionError("unexpected two-orientation closure summary")
    if data["provenance"] != PROVENANCE:
        raise AssertionError("unexpected provenance")
    claim_scope = str(data["claim_scope"])
    for guard in (
        "does not include first-block-reversed",
        "arbitrary cyclic orders",
        "proof of Erdos Problem #97",
        "counterexample",
    ):
        if guard not in claim_scope:
            raise AssertionError(f"claim scope lost guard: {guard}")
    records = data["family_crosswalk"]
    if not isinstance(records, list) or len(records) != 2:
        raise AssertionError("expected two family crosswalk records")


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
        print("block6 first-block-forward two-orientation closure crosswalk")
        print(f"total family orders: {summary['total_family_order_count']}")
        print(
            "combined closed: "
            f"{summary['combined_closed_order_count']} "
            f"(complete={summary['combined_closure_complete']})"
        )
        print(f"method counts: {summary['method_counts']}")
        if args.assert_expected:
            print("OK: expected two-orientation closure crosswalk verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
