#!/usr/bin/env python3
"""Check a Kalmanson quotient-cone certificate for the block-6 survivor."""

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
from erdos97.quotient_cone import check_quotient_cone_certificate  # noqa: E402


SURVIVOR_ROWS: list[list[int]] = block6_two_block_survivor_extension_3_rows()

STRICT_ROWS: list[dict[str, object]] = [
    {"source": "kalmanson", "kind": "K1_diag_gt_sides", "quad": [0, 1, 3, 9], "weight": 402},
    {"source": "kalmanson", "kind": "K1_diag_gt_sides", "quad": [0, 1, 7, 10], "weight": 100},
    {"source": "kalmanson", "kind": "K1_diag_gt_sides", "quad": [0, 2, 3, 11], "weight": 146},
    {"source": "kalmanson", "kind": "K1_diag_gt_sides", "quad": [0, 2, 5, 9], "weight": 105},
    {"source": "kalmanson", "kind": "K2_diag_gt_other", "quad": [0, 2, 6, 10], "weight": 5},
    {"source": "kalmanson", "kind": "K1_diag_gt_sides", "quad": [0, 4, 6, 7], "weight": 96},
    {"source": "kalmanson", "kind": "K2_diag_gt_other", "quad": [0, 4, 7, 9], "weight": 48},
    {"source": "kalmanson", "kind": "K1_diag_gt_sides", "quad": [0, 6, 7, 8], "weight": 101},
    {"source": "kalmanson", "kind": "K1_diag_gt_sides", "quad": [0, 7, 8, 10], "weight": 249},
    {"source": "kalmanson", "kind": "K2_diag_gt_other", "quad": [0, 7, 9, 11], "weight": 48},
    {"source": "kalmanson", "kind": "K1_diag_gt_sides", "quad": [0, 8, 10, 11], "weight": 5},
    {"source": "kalmanson", "kind": "K2_diag_gt_other", "quad": [1, 2, 7, 10], "weight": 246},
    {"source": "kalmanson", "kind": "K1_diag_gt_sides", "quad": [1, 3, 4, 9], "weight": 284},
    {"source": "kalmanson", "kind": "K2_diag_gt_other", "quad": [1, 3, 10, 11], "weight": 146},
    {"source": "kalmanson", "kind": "K1_diag_gt_sides", "quad": [1, 4, 5, 11], "weight": 256},
    {"source": "kalmanson", "kind": "K2_diag_gt_other", "quad": [1, 4, 6, 8], "weight": 28},
    {"source": "kalmanson", "kind": "K1_diag_gt_sides", "quad": [1, 4, 8, 11], "weight": 28},
    {"source": "kalmanson", "kind": "K1_diag_gt_sides", "quad": [2, 3, 4, 10], "weight": 264},
    {"source": "kalmanson", "kind": "K2_diag_gt_other", "quad": [2, 3, 7, 11], "weight": 97},
    {"source": "kalmanson", "kind": "K1_diag_gt_sides", "quad": [2, 4, 5, 6], "weight": 264},
    {"source": "kalmanson", "kind": "K2_diag_gt_other", "quad": [2, 4, 6, 9], "weight": 236},
    {"source": "kalmanson", "kind": "K1_diag_gt_sides", "quad": [2, 6, 7, 10], "weight": 149},
    {"source": "kalmanson", "kind": "K1_diag_gt_sides", "quad": [2, 6, 8, 11], "weight": 82},
    {"source": "kalmanson", "kind": "K2_diag_gt_other", "quad": [2, 7, 8, 11], "weight": 49},
    {"source": "kalmanson", "kind": "K1_diag_gt_sides", "quad": [2, 8, 9, 10], "weight": 131},
    {"source": "kalmanson", "kind": "K2_diag_gt_other", "quad": [3, 5, 6, 11], "weight": 97},
    {"source": "kalmanson", "kind": "K1_diag_gt_sides", "quad": [3, 6, 7, 11], "weight": 97},
    {"source": "kalmanson", "kind": "K2_diag_gt_other", "quad": [3, 8, 9, 10], "weight": 118},
    {"source": "kalmanson", "kind": "K2_diag_gt_other", "quad": [4, 5, 10, 11], "weight": 264},
    {"source": "kalmanson", "kind": "K1_diag_gt_sides", "quad": [4, 7, 8, 9], "weight": 48},
    {"source": "kalmanson", "kind": "K2_diag_gt_other", "quad": [5, 8, 9, 11], "weight": 105},
]

CERTIFICATE: dict[str, object] = {
    "type": "block6_survivor_kalmanson_quotient_cone_certificate",
    "schema": "erdos97.block6_survivor_kalmanson_quotient_cone_certificate.v1",
    "status": "EXACT_OBSTRUCTION_FOR_FIXED_SURVIVOR_AND_FIXED_CYCLIC_ORDER",
    "claim_strength": (
        "Exact obstruction for the fixed two-block block-6 survivor extension "
        "and natural cyclic order only."
    ),
    "pattern": {
        "name": "block6_two_block_survivor_extension_3",
        "n": 12,
        "selected_rows": SURVIVOR_ROWS,
    },
    "cyclic_order": list(range(12)),
    "strict_rows": STRICT_ROWS,
    "num_inequalities": 31,
    "weight_sum": 4294,
}


def audit() -> dict[str, object]:
    result = check_quotient_cone_certificate(CERTIFICATE)
    return {
        "type": CERTIFICATE["type"],
        "schema": CERTIFICATE["schema"],
        "status": result.status,
        "claim_strength": result.claim_strength,
        "pattern": result.pattern,
        "n": result.n,
        "cyclic_order": CERTIFICATE["cyclic_order"],
        "strict_rows": result.strict_rows,
        "distance_classes": result.distance_classes,
        "weight_sum": result.weight_sum,
        "max_weight": result.max_weight,
        "zero_sum_verified": result.zero_sum_verified,
        "nonpositive_sum_verified": result.nonpositive_sum_verified,
        "combined_nonzero_coefficient_count": result.combined_nonzero_coefficient_count,
        "coefficient_positive_count": result.coefficient_positive_count,
        "coefficient_negative_count": result.coefficient_negative_count,
        "coefficient_zero_count": result.coefficient_zero_count,
        "certificate": CERTIFICATE,
        "interpretation": (
            "The listed positive integer combination of strict Kalmanson "
            "inequalities reduces to the zero vector after selected-distance "
            "quotienting. Summing the strict inequalities gives 0 > 0 for this "
            "fixed survivor/order."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    payload = audit()
    if args.assert_expected:
        if payload["strict_rows"] != 31:
            raise AssertionError("unexpected strict-row count")
        if payload["distance_classes"] != 33:
            raise AssertionError("unexpected distance-class count")
        if payload["weight_sum"] != 4294:
            raise AssertionError("unexpected weight sum")
        if payload["max_weight"] != 402:
            raise AssertionError("unexpected max weight")
        if not payload["zero_sum_verified"]:
            raise AssertionError("expected zero-sum certificate")
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("block6 survivor Kalmanson quotient-cone certificate")
        print(f"strict rows: {payload['strict_rows']}")
        print(f"distance classes: {payload['distance_classes']}")
        print(f"weight sum: {payload['weight_sum']}")
        print(f"max weight: {payload['max_weight']}")
        print(f"zero sum verified: {payload['zero_sum_verified']}")
        if args.assert_expected:
            print("OK: expected Kalmanson certificate verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
