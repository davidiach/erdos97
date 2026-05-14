#!/usr/bin/env python3
"""Check Kalmanson certificates for reversed-block VC-clean rows.

This is a fixed-order diagnostic for the 16 vertex-circle-clean abstract row
systems recorded by
``check_block6_reversed_block_shuffle_vertex_circle_escape.py``.  Each stored
certificate obstructs only one selected-row assignment in one cyclic order.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from itertools import combinations
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np
import sympy as sp
from scipy.optimize import linprog

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from erdos97.quotient_cone import (  # noqa: E402
    check_quotient_cone_certificate,
    kalmanson_row,
    selected_distance_quotient,
)
from scripts.check_block6_reversed_block_shuffle_vertex_circle_escape import (  # noqa: E402
    EXPECTED_CLEAN_INDICES,
    OUT as SOURCE_OUT,
    assert_expected as assert_source_expected,
)
from scripts.check_block6_terminal_crossing_vertex_circle_sample import (  # noqa: E402
    write_json,
)

OUT = ROOT / "data" / "certificates" / "block6_reversed_block_clean_kalmanson.json"
PROVENANCE = {
    "generator": "scripts/check_block6_reversed_block_clean_kalmanson.py",
    "command": (
        "python scripts/check_block6_reversed_block_clean_kalmanson.py "
        "--write --assert-expected"
    ),
}
SCHEMA = "erdos97.block6_reversed_block_clean_kalmanson.v1"
STATUS = "EXACT_FIXED_ORDER_OBSTRUCTIONS_FOR_REVERSED_BLOCK_VC_CLEAN_ROWS"
TRUST = "EXACT_CERTIFICATE_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Exact Kalmanson quotient-cone certificates for the 16 vertex-circle-clean "
    "fixed-order selected-row assignments recorded by the reversed-second-block "
    "shuffle negative-control packet. Each certificate applies only to its "
    "encoded selected-row assignment and encoded cyclic order. This is not "
    "all-order closure, not a fragile-bridge proof, not a proof of Erdos "
    "Problem #97, and not a counterexample."
)

EXPECTED_SUMMARY = {
    "source_clean_order_count": 16,
    "obstructed_clean_order_count": 16,
    "strict_rows_total": 394,
    "strict_rows_min": 7,
    "strict_rows_max": 31,
    "weight_sum_total": 16850,
    "weight_sum_min": 8,
    "weight_sum_max": 4002,
    "max_weight_overall": 375,
    "distance_classes_min": 31,
    "distance_classes_max": 36,
    "kind_counts": {"K1_diag_gt_sides": 169, "K2_diag_gt_other": 225},
}

Rows = list[list[int]]


def _parse_indices(raw: str) -> list[int]:
    try:
        return [int(item.strip()) for item in raw.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"invalid comma-separated index list: {raw}"
        ) from exc


def _source_payload() -> dict[str, Any]:
    data = json.loads(SOURCE_OUT.read_text(encoding="utf-8"))
    assert_source_expected(data)
    return data


def _clean_records(indices: Iterable[int] | None = None) -> list[dict[str, Any]]:
    data = _source_payload()
    records = list(data["clean_order_records"])
    if indices is None:
        return records
    selected = set(indices)
    known = {int(record["index"]) for record in records}
    unknown = selected - known
    if unknown:
        raise ValueError(f"unknown clean reversed-block order indices: {sorted(unknown)}")
    return [record for record in records if int(record["index"]) in selected]


def _lp_support(vectors: Sequence[Sequence[int]], tol: float = 1e-9) -> list[int]:
    matrix = np.array(vectors, dtype=float)
    class_count = matrix.shape[1]
    a_eq = np.vstack([matrix.T, np.ones((1, len(vectors)))])
    b_eq = np.zeros(class_count + 1)
    b_eq[-1] = 1.0
    result = linprog(
        np.zeros(len(vectors)),
        A_eq=a_eq,
        b_eq=b_eq,
        bounds=(0, None),
        method="highs",
    )
    if not result.success:
        raise AssertionError(f"no Kalmanson quotient-cone LP support: {result.message}")
    return [idx for idx, weight in enumerate(result.x) if weight > tol]


def _exact_positive_weights(
    vectors: Sequence[Sequence[int]],
    support: Sequence[int],
) -> list[int]:
    if not support:
        raise AssertionError("LP support is empty")
    matrix = sp.Matrix(
        [[vectors[idx][col] for idx in support] for col in range(len(vectors[0]))]
    )
    nullspace = matrix.nullspace()
    if len(nullspace) != 1:
        raise AssertionError(f"expected one-dimensional nullspace, got {len(nullspace)}")
    vector = nullspace[0]
    if all(value < 0 for value in vector):
        vector = -vector
    if not all(value > 0 for value in vector):
        raise AssertionError("exact null vector is not strictly positive")

    denominator_lcm = 1
    for value in vector:
        denominator_lcm = int(sp.lcm(denominator_lcm, value.q))
    weights = [int(value * denominator_lcm) for value in vector]
    divisor = 0
    for weight in weights:
        divisor = math.gcd(divisor, abs(weight))
    return [weight // divisor for weight in weights]


def _certificate_for_record(record: dict[str, Any]) -> dict[str, object]:
    index = int(record["index"])
    order = [int(label) for label in record["order"]]
    rows: Rows = [
        [int(label) for label in row]
        for row in record["pruned_search"]["first_clean_rows"]
    ]
    quotient = selected_distance_quotient(rows)
    candidates = []
    for quad in combinations(order, 4):
        for kind in ("K1_diag_gt_sides", "K2_diag_gt_other"):
            row = kalmanson_row(quotient, kind, quad)
            candidates.append((kind, tuple(int(label) for label in quad), row.vector))

    support = _lp_support([item[2] for item in candidates])
    weights = _exact_positive_weights([item[2] for item in candidates], support)
    strict_rows = [
        {
            "source": "kalmanson",
            "kind": candidates[idx][0],
            "quad": list(candidates[idx][1]),
            "weight": int(weight),
        }
        for idx, weight in zip(support, weights, strict=True)
    ]
    certificate: dict[str, object] = {
        "type": "block6_reversed_block_clean_kalmanson_certificate",
        "schema": SCHEMA,
        "status": "EXACT_OBSTRUCTION_FOR_FIXED_CLEAN_ROW_AND_FIXED_CYCLIC_ORDER",
        "claim_strength": (
            "Exact Kalmanson obstruction for this fixed vertex-circle-clean "
            "reversed-block selected-row assignment and fixed cyclic order "
            "only; not all-order closure, not a fragile-bridge proof, not an "
            "Erdos97 proof, and not a counterexample."
        ),
        "pattern": {
            "name": f"block6_reversed_block_clean_order_{index}",
            "n": len(rows),
            "selected_rows": rows,
        },
        "cyclic_order": order,
        "source_clean_order_index": index,
        "strict_rows": strict_rows,
        "num_inequalities": len(strict_rows),
        "weight_sum": int(sum(weights)),
    }
    check_quotient_cone_certificate(certificate)
    return certificate


def _record_summary(certificate: dict[str, object]) -> dict[str, object]:
    check = check_quotient_cone_certificate(certificate)
    return {
        "index": int(certificate["source_clean_order_index"]),
        "cyclic_order": certificate["cyclic_order"],
        "selected_rows": certificate["pattern"]["selected_rows"],  # type: ignore[index]
        "strict_rows": check.strict_rows,
        "distance_classes": check.distance_classes,
        "weight_sum": check.weight_sum,
        "max_weight": check.max_weight,
        "zero_sum_verified": check.zero_sum_verified,
        "nonpositive_sum_verified": check.nonpositive_sum_verified,
        "combined_nonzero_coefficient_count": (
            check.combined_nonzero_coefficient_count
        ),
        "certificate": certificate,
    }


def _summary(records: Sequence[dict[str, object]]) -> dict[str, object]:
    kind_counts: dict[str, int] = {}
    for record in records:
        certificate = record["certificate"]
        for row in certificate["strict_rows"]:  # type: ignore[index]
            kind = str(row["kind"])
            kind_counts[kind] = kind_counts.get(kind, 0) + 1
    strict_rows = [int(record["strict_rows"]) for record in records]
    distance_classes = [int(record["distance_classes"]) for record in records]
    weight_sums = [int(record["weight_sum"]) for record in records]
    max_weights = [int(record["max_weight"]) for record in records]
    return {
        "source_clean_order_count": len(records),
        "obstructed_clean_order_count": sum(
            1 for record in records if record["zero_sum_verified"] is True
        ),
        "clean_order_indices": [int(record["index"]) for record in records],
        "strict_rows_total": sum(strict_rows),
        "strict_rows_min": min(strict_rows, default=0),
        "strict_rows_max": max(strict_rows, default=0),
        "weight_sum_total": sum(weight_sums),
        "weight_sum_min": min(weight_sums, default=0),
        "weight_sum_max": max(weight_sums, default=0),
        "max_weight_overall": max(max_weights, default=0),
        "distance_classes_min": min(distance_classes, default=0),
        "distance_classes_max": max(distance_classes, default=0),
        "kind_counts": dict(sorted(kind_counts.items())),
    }


def payload(*, indices: Iterable[int] | None = None) -> dict[str, object]:
    certificates = [_certificate_for_record(record) for record in _clean_records(indices)]
    records = [_record_summary(certificate) for certificate in certificates]
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "source_artifact": {
            "path": SOURCE_OUT.relative_to(ROOT).as_posix(),
            "schema": "erdos97.block6_reversed_block_shuffle_vertex_circle_escape.v1",
            "clean_order_indices": EXPECTED_CLEAN_INDICES,
        },
        "summary": _summary(records),
        "certificate_records": records,
        "provenance": PROVENANCE,
        "interpretation": (
            "The reversed-second-block vertex-circle negative-control packet "
            "left 16 fixed-order abstract selected-row assignments clean under "
            "that gate. This artifact replays exact Kalmanson quotient-cone "
            "certificates for those same 16 assignment/order pairs, closing "
            "that bounded escape set only."
        ),
    }


def _check_loaded_artifact(data: dict[str, Any]) -> dict[str, object]:
    if data.get("schema") != SCHEMA:
        raise AssertionError("unexpected schema")
    if data.get("status") != STATUS:
        raise AssertionError("unexpected status")
    if data.get("trust") != TRUST:
        raise AssertionError("unexpected trust label")
    if data.get("claim_scope") != CLAIM_SCOPE:
        raise AssertionError("unexpected claim scope")

    source = _source_payload()
    source_by_index = {
        int(record["index"]): record for record in source["clean_order_records"]
    }
    records = data.get("certificate_records")
    if not isinstance(records, list):
        raise AssertionError("certificate_records must be a list")
    checked_records = []
    for record in records:
        if not isinstance(record, dict):
            raise AssertionError("certificate record must be an object")
        index = int(record["index"])
        source_record = source_by_index[index]
        certificate = record["certificate"]
        if certificate["cyclic_order"] != source_record["order"]:
            raise AssertionError(f"order mismatch for clean order {index}")
        source_rows = source_record["pruned_search"]["first_clean_rows"]
        if certificate["pattern"]["selected_rows"] != source_rows:
            raise AssertionError(f"selected rows mismatch for clean order {index}")
        checked_records.append(_record_summary(certificate))

    checked_summary = _summary(checked_records)
    if data.get("summary") != checked_summary:
        raise AssertionError("stored summary does not match checked certificates")
    checked = dict(data)
    checked["certificate_records"] = checked_records
    return checked


def check_artifact() -> dict[str, object]:
    data = json.loads(OUT.read_text(encoding="utf-8"))
    return _check_loaded_artifact(data)


def assert_expected(data: dict[str, object]) -> None:
    if data["summary"] != {
        **EXPECTED_SUMMARY,
        "clean_order_indices": EXPECTED_CLEAN_INDICES,
    }:
        raise AssertionError("unexpected summary")
    records = data["certificate_records"]
    if not isinstance(records, list):
        raise AssertionError("certificate_records must be a list")
    if [record["index"] for record in records] != EXPECTED_CLEAN_INDICES:
        raise AssertionError("unexpected clean order indices")
    if not all(record["zero_sum_verified"] for record in records):
        raise AssertionError("expected every record to verify zero-sum")
    if not all(
        record["combined_nonzero_coefficient_count"] == 0 for record in records
    ):
        raise AssertionError("expected every certificate sum to vanish")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument(
        "--indices",
        type=_parse_indices,
        help="Optional comma-separated clean order indices for partial discovery.",
    )
    args = parser.parse_args()

    data = check_artifact() if args.check else payload(indices=args.indices)
    if args.assert_expected and args.indices is None:
        assert_expected(data)
    if args.write:
        write_json(data, OUT)

    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        summary = data["summary"]
        print("block6 reversed-block clean-row Kalmanson certificates")
        print(f"source clean orders: {summary['source_clean_order_count']}")
        print(f"obstructed clean orders: {summary['obstructed_clean_order_count']}")
        print(f"strict rows total: {summary['strict_rows_total']}")
        print(f"weight sum total: {summary['weight_sum_total']}")
        if args.assert_expected and args.indices is None:
            print("OK: expected reversed-block clean-row certificates verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
