#!/usr/bin/env python3
"""Crosswalk the block-6 fragile survivor through current exact filters."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.fragile_benchmarks import (  # noqa: E402
    block6_two_block_survivor_extension_3_rows,
)
from erdos97.incidence_filters import (  # noqa: E402
    row_ptolemy_product_cancellation_certificates,
)
from erdos97.vertex_circle_order_filter import (  # noqa: E402
    vertex_circle_order_obstruction,
)
from scripts.check_block6_fragile_vertex_circle_extension import (  # noqa: E402
    audit_payload as vertex_circle_extension_audit,
)
from scripts.check_block6_row_ptolemy_extensions import (  # noqa: E402
    audit as row_ptolemy_extension_audit,
)
from scripts.check_block6_survivor_crossing_kalmanson import (  # noqa: E402
    audit as crossing_kalmanson_audit,
)
from scripts.check_block6_survivor_ptolemy_feasibility import (  # noqa: E402
    audit as quotient_ptolemy_audit,
)
from scripts.check_block6_survivor_radius_propagation import (  # noqa: E402
    audit as radius_propagation_audit,
)

PATTERN_NAME = "block6_two_block_survivor_extension_3"
EXPECTED_SUMMARY = {
    "row_ptolemy_extension_index": 3,
    "row_ptolemy_product_cancellation_count": 0,
    "quotient_ptolemy_distance_classes": 33,
    "radius_propagation_status": "PASS_RADIUS_PROPAGATION",
    "radius_propagation_nodes": 13,
    "natural_order_vertex_circle_status": "self_edge",
    "natural_order_vertex_circle_self_edges": 15,
    "natural_order_vertex_circle_strict_edges": 108,
    "crossing_order_count": 4,
    "crossing_kalmanson_obstructed_order_count": 4,
    "all_extension_pruned_result": "closed",
    "all_extension_pruned_nodes": 1752,
    "all_extension_pruned_solutions": 0,
}


def _rows_by_center(rows: list[list[int]]) -> dict[str, list[int]]:
    return {str(center): list(row) for center, row in enumerate(rows)}


def _survivor_rows_from_ptolemy_frontier(
    frontier: Mapping[str, object],
) -> dict[str, list[int]]:
    survivor = frontier.get("survivor")
    if not isinstance(survivor, Mapping):
        raise AssertionError("row-Ptolemy frontier did not report a survivor")
    rows = survivor.get("rows")
    if not isinstance(rows, Mapping):
        raise AssertionError("row-Ptolemy survivor did not include selected rows")
    return {str(center): [int(label) for label in row] for center, row in rows.items()}  # type: ignore[union-attr]


def _vertex_circle_status(rows: list[list[int]]) -> dict[str, object]:
    result = vertex_circle_order_obstruction(
        rows,
        list(range(len(rows))),
        PATTERN_NAME,
    )
    status = (
        "self_edge"
        if result.self_edge_conflicts
        else "strict_cycle"
        if result.cycle_edges
        else "ok"
    )
    first_self_edge = result.self_edge_conflicts[0] if result.self_edge_conflicts else None
    return {
        "status": status,
        "strict_edge_count": result.strict_edge_count,
        "self_edge_count": len(result.self_edge_conflicts),
        "cycle_edge_count": len(result.cycle_edges),
        "first_self_edge": {
            "row": first_self_edge.row,
            "witness_order": first_self_edge.witness_order,
            "outer_pair": list(first_self_edge.outer_pair),
            "inner_pair": list(first_self_edge.inner_pair),
            "quotient_class": list(first_self_edge.outer_class),
        }
        if first_self_edge is not None
        else None,
    }


def audit(*, include_terminal: bool = False) -> dict[str, Any]:
    """Return a compact crosswalk across the current block-6 filters."""

    rows = block6_two_block_survivor_extension_3_rows()
    order = list(range(len(rows)))
    rows_by_center = _rows_by_center(rows)

    row_ptolemy_frontier = row_ptolemy_extension_audit(
        blocks=2,
        max_extensions=3,
        max_nodes=100_000,
    )
    if _survivor_rows_from_ptolemy_frontier(row_ptolemy_frontier) != rows_by_center:
        raise AssertionError("shared block-6 survivor changed")
    survivor_record = row_ptolemy_frontier["survivor"]
    if not isinstance(survivor_record, Mapping):
        raise AssertionError("row-Ptolemy survivor record is missing")

    product_cancellations = row_ptolemy_product_cancellation_certificates(rows, order)
    quotient_ptolemy = quotient_ptolemy_audit()
    radius = radius_propagation_audit()
    natural_vc = _vertex_circle_status(rows)
    crossing = crossing_kalmanson_audit()
    all_extension_vc = vertex_circle_extension_audit(
        include_terminal=include_terminal,
    )

    summary = {
        "row_ptolemy_extension_index": int(survivor_record["extension_index"]),
        "row_ptolemy_product_cancellation_count": len(product_cancellations),
        "quotient_ptolemy_distance_classes": int(
            quotient_ptolemy["distance_class_count"]
        ),
        "radius_propagation_status": str(radius["status"]),
        "radius_propagation_nodes": int(
            radius["radius_propagation"]["nodes_visited"]  # type: ignore[index]
        ),
        "natural_order_vertex_circle_status": str(natural_vc["status"]),
        "natural_order_vertex_circle_self_edges": int(natural_vc["self_edge_count"]),
        "natural_order_vertex_circle_strict_edges": int(natural_vc["strict_edge_count"]),
        "crossing_order_count": int(crossing["crossing_order_count"]),
        "crossing_kalmanson_obstructed_order_count": int(
            crossing["obstructed_order_count"]
        ),
        "all_extension_pruned_result": str(
            all_extension_vc["pruned_search"]["result"]  # type: ignore[index]
        ),
        "all_extension_pruned_nodes": int(
            all_extension_vc["pruned_search"]["nodes"]  # type: ignore[index]
        ),
        "all_extension_pruned_solutions": int(
            all_extension_vc["pruned_search"]["solutions"]  # type: ignore[index]
        ),
    }

    return {
        "schema": "erdos97.block6_fragile_filter_crosswalk.v1",
        "status": "REVIEW_PENDING_DIAGNOSTIC_ONLY",
        "claim_scope": (
            "Filter-layer crosswalk for one fixed two-block block-6 full "
            "selected-row survivor and the existing natural-order all-extension "
            "vertex-circle audit. This is not a proof of Erdos Problem #97 and "
            "not a counterexample."
        ),
        "pattern": {
            "name": PATTERN_NAME,
            "n": len(rows),
            "selected_rows": rows_by_center,
        },
        "summary": summary,
        "fixed_survivor_layers": {
            "row_ptolemy_frontier": {
                "extensions_examined": row_ptolemy_frontier["extensions_examined"],
                "extensions_killed_by_product_cancellation": row_ptolemy_frontier[
                    "extensions_killed_by_row_ptolemy_product_cancellation"
                ],
                "survivor_extension_index": survivor_record["extension_index"],
            },
            "quotient_ptolemy": {
                "distance_classes": quotient_ptolemy["distance_class_count"],
                "row_ptolemy_equations_verified": quotient_ptolemy[
                    "row_ptolemy_equations_verified"
                ],
                "positive_assignment": quotient_ptolemy["positive_assignment"],
            },
            "radius_propagation": {
                "status": radius["status"],
                "nodes_visited": radius["radius_propagation"]["nodes_visited"],  # type: ignore[index]
                "short_gap_choice_count": radius["radius_propagation"][
                    "short_gap_choice_count"
                ],
                "acyclic_choice_found": radius["acyclic_choice_found"],
            },
            "natural_order_vertex_circle": natural_vc,
            "crossing_kalmanson": {
                "crossing_order_count": crossing["crossing_order_count"],
                "obstructed_order_count": crossing["obstructed_order_count"],
                "strict_rows": [
                    item["strict_rows"] for item in crossing["order_summaries"]
                ],
                "weight_sums": [
                    item["weight_sum"] for item in crossing["order_summaries"]
                ],
            },
        },
        "all_extension_natural_order_vertex_circle": {
            "pruned_search": all_extension_vc["pruned_search"],
            "terminal_classification": all_extension_vc.get("terminal_classification"),
        },
        "remaining_gap": (
            "The natural-order all-extension vertex-circle audit closes this "
            "block-6 family only in the fixed natural cyclic order. The crossing "
            "Kalmanson layer closes only the fixed survivor across its crossing "
            "orders. The open bridge target is still all full extensions across "
            "all compatible cyclic orders, or a genuine minimal/rich-class "
            "geometric reduction."
        ),
    }


def assert_expected(payload: Mapping[str, Any]) -> None:
    if payload["status"] != "REVIEW_PENDING_DIAGNOSTIC_ONLY":
        raise AssertionError("unexpected status")
    if "not a proof" not in payload["claim_scope"]:
        raise AssertionError("claim scope lost no-proof note")
    if payload["summary"] != EXPECTED_SUMMARY:
        raise AssertionError(f"unexpected crosswalk summary: {payload['summary']!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print full JSON payload")
    parser.add_argument(
        "--terminal",
        action="store_true",
        help="include the slower all-terminal vertex-circle classification",
    )
    parser.add_argument(
        "--assert-expected",
        action="store_true",
        help="assert the current expected crosswalk counts",
    )
    args = parser.parse_args()

    payload = audit(include_terminal=args.terminal)
    if args.assert_expected:
        assert_expected(payload)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        summary = payload["summary"]
        print("block6 fragile filter-layer crosswalk")
        print(f"row-Ptolemy survivor index: {summary['row_ptolemy_extension_index']}")
        print(
            "natural-order vertex-circle: "
            f"{summary['natural_order_vertex_circle_status']} "
            f"self_edges={summary['natural_order_vertex_circle_self_edges']}"
        )
        print(
            "crossing Kalmanson: "
            f"{summary['crossing_kalmanson_obstructed_order_count']}/"
            f"{summary['crossing_order_count']} orders obstructed"
        )
        print(
            "all-extension natural-order VC: "
            f"{summary['all_extension_pruned_result']} "
            f"solutions={summary['all_extension_pruned_solutions']}"
        )
        if args.assert_expected:
            print("OK: block6 fragile filter crosswalk matched expected counts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
