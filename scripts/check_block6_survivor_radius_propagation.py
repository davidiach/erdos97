#!/usr/bin/env python3
"""Check radius-propagation on the fixed block-6 survivor extension."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.fragile_benchmarks import (  # noqa: E402
    block6_two_block_survivor_extension_3_rows,
)
from erdos97.min_radius_filter import (  # noqa: E402
    radius_propagation_order_obstruction,
    radius_result_to_json,
)

PATTERN_NAME = "block6_two_block_survivor_extension_3"


def audit(max_nodes: int | None = None) -> dict[str, object]:
    """Return the fixed-order radius-propagation audit payload."""

    rows = block6_two_block_survivor_extension_3_rows()
    order = list(range(len(rows)))
    result = radius_propagation_order_obstruction(
        rows,
        order=order,
        pattern=PATTERN_NAME,
        max_nodes=max_nodes,
    )
    payload = radius_result_to_json(result)
    return {
        "type": "block6_survivor_radius_propagation_audit",
        "schema": "erdos97.block6_survivor_radius_propagation_audit.v1",
        "claim_strength": (
            "Fixed full selected-row extension and fixed natural cyclic order only."
        ),
        "selected_rows": {str(center): row for center, row in enumerate(rows)},
        "radius_propagation": payload,
        "status": payload["status"],
        "obstructed": payload["obstructed"],
        "acyclic_choice_found": payload["acyclic_choice"] is not None,
        "interpretation": (
            "PASS_RADIUS_PROPAGATION is a negative result for this filter only: "
            "the fixed survivor escapes critical-radius propagation in this "
            "order. It is not a Euclidean realization certificate and not a "
            "counterexample."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--max-nodes", type=int)
    parser.add_argument("--assert-pass", action="store_true")
    args = parser.parse_args()

    payload = audit(max_nodes=args.max_nodes)
    if args.assert_pass:
        if payload["status"] != "PASS_RADIUS_PROPAGATION":
            raise AssertionError(f"expected PASS_RADIUS_PROPAGATION, got {payload['status']}")
        if not payload["acyclic_choice_found"]:
            raise AssertionError("expected an acyclic radius-propagation choice")

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        radius = payload["radius_propagation"]
        print("block6 survivor radius-propagation audit")
        print(f"status: {payload['status']}")
        print(f"nodes visited: {radius['nodes_visited']}")
        print(f"short-gap choices: {radius['short_gap_choice_count']}")
        print(f"acyclic choice found: {payload['acyclic_choice_found']}")
        if args.assert_pass:
            print("OK: radius-propagation pass expectation verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
