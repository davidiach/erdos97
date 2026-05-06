#!/usr/bin/env python3
"""Generate or check the n=9 row-Ptolemy admissible-order census."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import permutations
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SCRIPTS = ROOT / "scripts"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from erdos97.incidence_filters import (  # noqa: E402
    _selected_distance_pair_classes,
    normalize_chord,
    phi_map,
)
from erdos97.path_display import display_path  # noqa: E402
from erdos97.vertex_circle_quotient_replay import (  # noqa: E402
    parse_selected_rows,
    replay_vertex_circle_quotient,
)
from scripts.check_n9_row_ptolemy_product_cancellations import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_ROW_PTOLEMY_ARTIFACT,
    load_artifact,
    validate_payload as validate_row_ptolemy_payload,
)

DEFAULT_ARTIFACT = (
    ROOT / "data" / "certificates" / "n9_row_ptolemy_order_admissible_census.json"
)
SCHEMA = "erdos97.n9_row_ptolemy_order_admissible_census.v1"
STATUS = "EXPLORATORY_LEDGER_ONLY"
TRUST = "FINITE_BOOKKEEPING_NOT_A_PROOF"
CLAIM_SCOPE = (
    "Derived n=9 row-Ptolemy admissible-order census for the 26 fixed-order "
    "hit assignments; not a proof of n=9, not a counterexample, not an "
    "all-order obstruction, not an orderless abstract-incidence obstruction, "
    "not a geometric realizability count, and not a global status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_row_ptolemy_order_admissible_census.py",
    "command": (
        "python scripts/check_n9_row_ptolemy_order_admissible_census.py "
        "--assert-expected --write"
    ),
}
SOURCE_ARTIFACT = {
    "path": "data/certificates/n9_row_ptolemy_product_cancellations.json",
    "schema": "erdos97.n9_row_ptolemy_product_cancellations.v2",
    "status": "EXPLORATORY_LEDGER_ONLY",
    "trust": "FINITE_BOOKKEEPING_NOT_A_PROOF",
}
EXPECTED_TOP_LEVEL_KEYS = {
    "adjacent_ok_order_count",
    "assignment_order_pair_count",
    "assignment_rows",
    "claim_scope",
    "compatible_certificate_count_histogram",
    "compatible_order_count",
    "compatible_order_count_per_assignment_counts",
    "compatible_vertex_circle_status_counts",
    "compatible_zero_certificate_order_count",
    "family_count",
    "family_rows",
    "filter",
    "interpretation",
    "n",
    "normalized_order_count",
    "normalized_order_rule",
    "provenance",
    "schema",
    "source_artifacts",
    "source_fixed_order",
    "status",
    "trust",
    "witness_size",
}
EXPECTED_FAMILY_ROWS = [
    {
        "all_order_certificate_count_histogram": {
            "0": 594,
            "2": 6516,
            "4": 30294,
            "6": 79128,
            "8": 117630,
            "10": 95796,
            "12": 32922,
        },
        "adjacent_ok_order_count": 990,
        "assignment_count": 18,
        "compatible_certificate_count_histogram": {"6": 18},
        "compatible_order_count": 18,
        "compatible_order_count_per_assignment_counts": {"1": 18},
        "compatible_vertex_circle_status_counts": {"self_edge": 18},
        "compatible_zero_certificate_order_count": 0,
        "family_id": "F02",
        "natural_certificate_count_per_assignment": 6,
    },
    {
        "all_order_certificate_count_histogram": {
            "0": 30,
            "2": 162,
            "4": 1512,
            "6": 5508,
            "8": 13932,
            "10": 24192,
            "12": 28152,
            "14": 25164,
            "16": 16470,
            "18": 5838,
        },
        "adjacent_ok_order_count": 246,
        "assignment_count": 6,
        "compatible_certificate_count_histogram": {"12": 6},
        "compatible_order_count": 6,
        "compatible_order_count_per_assignment_counts": {"1": 6},
        "compatible_vertex_circle_status_counts": {"self_edge": 6},
        "compatible_zero_certificate_order_count": 0,
        "family_id": "F09",
        "natural_certificate_count_per_assignment": 12,
    },
    {
        "all_order_certificate_count_histogram": {
            "0": 10,
            "2": 54,
            "4": 504,
            "6": 1836,
            "8": 4644,
            "10": 8064,
            "12": 9384,
            "14": 8388,
            "16": 5490,
            "18": 1946,
        },
        "adjacent_ok_order_count": 82,
        "assignment_count": 2,
        "compatible_certificate_count_histogram": {"0": 2, "18": 2},
        "compatible_order_count": 4,
        "compatible_order_count_per_assignment_counts": {"2": 2},
        "compatible_vertex_circle_status_counts": {"self_edge": 4},
        "compatible_zero_certificate_order_count": 2,
        "family_id": "F13",
        "natural_certificate_count_per_assignment": 18,
    },
]
EXPECTED_TOTAL_ALL_ORDER_HISTOGRAM = {
    "0": 634,
    "2": 6732,
    "4": 32310,
    "6": 86472,
    "8": 136206,
    "10": 128052,
    "12": 70458,
    "14": 33552,
    "16": 21960,
    "18": 7784,
}
EXPECTED_COMPATIBLE_HISTOGRAM = {"0": 2, "6": 18, "12": 6, "18": 2}
EXPECTED_ZERO_COMPATIBLE_ORDER = [0, 2, 4, 6, 8, 1, 3, 5, 7]
EXPECTED_ZERO_COMPATIBLE_ASSIGNMENTS = [22, 173]


@dataclass(frozen=True)
class NormalizedOrder:
    order: tuple[int, ...]
    positions: tuple[int, ...]
    edges: frozenset[tuple[int, int]]


def write_json(payload: object, path: Path) -> None:
    """Write stable LF-terminated JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def expect_equal(errors: list[str], label: str, actual: Any, expected: Any) -> None:
    """Append a mismatch error when values differ."""

    if actual != expected:
        errors.append(f"{label} mismatch: expected {expected!r}, got {actual!r}")


def _json_counter(counter: Counter[int] | Counter[str]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _make_order_data(order: Sequence[int]) -> NormalizedOrder:
    order_tuple = tuple(int(label) for label in order)
    positions = [0] * len(order_tuple)
    for index, label in enumerate(order_tuple):
        positions[label] = index
    return NormalizedOrder(
        order=order_tuple,
        positions=tuple(positions),
        edges=frozenset(
            normalize_chord(order_tuple[index], order_tuple[(index + 1) % len(order_tuple)])
            for index in range(len(order_tuple))
        ),
    )


def _normalized_orders(n: int) -> list[NormalizedOrder]:
    """Return cyclic orders with label 0 fixed and reversal quotiented."""

    return [
        _make_order_data((0, *suffix))
        for suffix in permutations(range(1, n))
        if suffix[0] < suffix[-1]
    ]


def _chords_cross_with_positions(
    left: tuple[int, int],
    right: tuple[int, int],
    positions: Sequence[int],
) -> bool:
    if set(left) & set(right):
        return False
    a, b = left
    c, d = right
    a_pos = positions[a]
    b_pos = positions[b]
    if a_pos > b_pos:
        a_pos, b_pos = b_pos, a_pos
    c_inside = a_pos < positions[c] < b_pos
    d_inside = a_pos < positions[d] < b_pos
    return c_inside != d_inside


def _order_passes_admissible_filters(
    order: NormalizedOrder,
    phis: dict[tuple[int, int], tuple[int, int]],
) -> bool:
    """Return whether the order passes adjacent two-overlap and crossing filters."""

    if order.edges & set(phis):
        return False
    return _order_passes_crossing_filter(order, phis)


def _order_passes_crossing_filter(
    order: NormalizedOrder,
    phis: dict[tuple[int, int], tuple[int, int]],
) -> bool:
    """Return whether all two-overlap phi edges cross in the supplied order."""

    return all(
        _chords_cross_with_positions(source, target, order.positions)
        for source, target in phis.items()
    )


def _certificate_count_for_order(
    selected_rows: Sequence[Sequence[int]],
    order: NormalizedOrder,
    pair_class: dict[tuple[int, int], int],
) -> int:
    """Return the row-Ptolemy product-cancellation certificate count."""

    count = 0
    variants = (
        (("d02", "d23"), ("d13", "d01")),
        (("d02", "d01"), ("d13", "d23")),
        (("d02", "d12"), ("d13", "d03")),
        (("d02", "d03"), ("d13", "d12")),
    )
    for center, row in enumerate(selected_rows):
        witnesses = sorted(
            row,
            key=lambda witness: (order.positions[witness] - order.positions[center])
            % len(order.order),
        )
        w0, w1, w2, w3 = witnesses
        pairs = {
            "d01": normalize_chord(w0, w1),
            "d02": normalize_chord(w0, w2),
            "d03": normalize_chord(w0, w3),
            "d12": normalize_chord(w1, w2),
            "d13": normalize_chord(w1, w3),
            "d23": normalize_chord(w2, w3),
        }
        classes = {name: pair_class[pair] for name, pair in pairs.items()}
        for equalities in variants:
            if all(classes[left] == classes[right] for left, right in equalities):
                count += 1
    return count


def _source_hit_family_ids(source: dict[str, Any]) -> list[str]:
    hit_summary = source.get("hit_summary", {})
    rows = hit_summary.get("hit_family_counts", [])
    if not isinstance(rows, list):
        return []
    return [
        str(row["family_id"])
        for row in rows
        if isinstance(row, dict) and isinstance(row.get("family_id"), str)
    ]


def _selected_rows(record: dict[str, Any]) -> list[list[int]]:
    rows = record.get("selected_rows")
    if not isinstance(rows, list):
        raise ValueError("source hit record selected_rows must be a list")
    return [[int(label) for label in row] for row in rows]


def _assignment_census_row(
    record: dict[str, Any],
    orders: Sequence[NormalizedOrder],
    natural_order: Sequence[int],
) -> dict[str, Any]:
    selected_rows = _selected_rows(record)
    pair_class, _ = _selected_distance_pair_classes(selected_rows)
    phis = phi_map(selected_rows)
    selected_row_objects = parse_selected_rows(selected_rows)
    natural_order_data = _make_order_data(natural_order)

    all_hist: Counter[int] = Counter()
    compatible_hist: Counter[int] = Counter()
    vertex_status_counts: Counter[str] = Counter()
    compatible_orders = []
    adjacent_ok_order_count = 0
    for order_data in orders:
        certificate_count = _certificate_count_for_order(
            selected_rows,
            order_data,
            pair_class,
        )
        all_hist[certificate_count] += 1
        if order_data.edges & set(phis):
            continue
        adjacent_ok_order_count += 1
        if not _order_passes_crossing_filter(order_data, phis):
            continue
        vertex_status = replay_vertex_circle_quotient(
            len(natural_order),
            order_data.order,
            selected_row_objects,
        ).status
        compatible_hist[certificate_count] += 1
        vertex_status_counts[vertex_status] += 1
        compatible_orders.append(
            {
                "order": [int(label) for label in order_data.order],
                "certificate_count": int(certificate_count),
                "vertex_circle_status": vertex_status,
                "is_natural_order": list(order_data.order) == list(natural_order),
            }
        )

    natural_certificate_count = _certificate_count_for_order(
        selected_rows,
        natural_order_data,
        pair_class,
    )
    return {
        "assignment_index": int(record["assignment_index"]),
        "family_id": str(record["family_id"]),
        "family_orbit_size": int(record["family_orbit_size"]),
        "selected_rows": selected_rows,
        "stored_natural_certificate_count": int(record["certificate_count"]),
        "natural_certificate_count": int(natural_certificate_count),
        "all_order_certificate_count_histogram": _json_counter(all_hist),
        "adjacent_ok_order_count": int(adjacent_ok_order_count),
        "compatible_order_count": sum(compatible_hist.values()),
        "compatible_certificate_count_histogram": _json_counter(compatible_hist),
        "compatible_zero_certificate_order_count": int(compatible_hist[0]),
        "compatible_vertex_circle_status_counts": _json_counter(vertex_status_counts),
        "compatible_orders": compatible_orders,
    }


def _family_rows(assignment_rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    rows_by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in assignment_rows:
        rows_by_family[str(row["family_id"])].append(row)

    family_rows = []
    for family_id in sorted(rows_by_family):
        rows = rows_by_family[family_id]
        natural_counts = {int(row["natural_certificate_count"]) for row in rows}
        all_hist: Counter[int] = Counter()
        adjacent_ok_order_count = 0
        compatible_hist: Counter[int] = Counter()
        compatible_per_assignment: Counter[int] = Counter()
        vertex_status_counts: Counter[str] = Counter()
        for row in rows:
            all_hist.update(
                {
                    int(count): int(value)
                    for count, value in row["all_order_certificate_count_histogram"].items()
                }
            )
            adjacent_ok_order_count += int(row["adjacent_ok_order_count"])
            compatible_hist.update(
                {
                    int(count): int(value)
                    for count, value in row["compatible_certificate_count_histogram"].items()
                }
            )
            compatible_per_assignment[int(row["compatible_order_count"])] += 1
            vertex_status_counts.update(
                {
                    str(status): int(value)
                    for status, value in row["compatible_vertex_circle_status_counts"].items()
                }
            )
        family_rows.append(
            {
                "family_id": family_id,
                "assignment_count": len(rows),
                "natural_certificate_count_per_assignment": (
                    next(iter(natural_counts)) if len(natural_counts) == 1 else None
                ),
                "all_order_certificate_count_histogram": _json_counter(all_hist),
                "adjacent_ok_order_count": int(adjacent_ok_order_count),
                "compatible_order_count": sum(compatible_hist.values()),
                "compatible_order_count_per_assignment_counts": _json_counter(
                    compatible_per_assignment
                ),
                "compatible_certificate_count_histogram": _json_counter(compatible_hist),
                "compatible_zero_certificate_order_count": int(compatible_hist[0]),
                "compatible_vertex_circle_status_counts": _json_counter(
                    vertex_status_counts
                ),
            }
        )
    return family_rows


def admissible_census_payload(source: dict[str, Any]) -> dict[str, Any]:
    """Return the admissible-order row-Ptolemy census payload."""

    source_errors = validate_row_ptolemy_payload(source, recompute=False)
    if source_errors:
        raise ValueError(f"source row-Ptolemy artifact invalid: {source_errors[0]}")
    records = source.get("hit_records")
    if not isinstance(records, list):
        raise ValueError("source row-Ptolemy artifact must contain hit_records")
    natural_order = list(source["cyclic_order"])
    orders = _normalized_orders(int(source["n"]))

    assignment_rows = [
        _assignment_census_row(record, orders, natural_order)
        for record in records
        if isinstance(record, dict)
    ]
    family_rows = _family_rows(assignment_rows)
    all_hist: Counter[int] = Counter()
    adjacent_ok_order_count = 0
    compatible_hist: Counter[int] = Counter()
    compatible_per_assignment: Counter[int] = Counter()
    vertex_status_counts: Counter[str] = Counter()
    for row in assignment_rows:
        all_hist.update(
            {
                int(count): int(value)
                for count, value in row["all_order_certificate_count_histogram"].items()
            }
        )
        adjacent_ok_order_count += int(row["adjacent_ok_order_count"])
        compatible_hist.update(
            {
                int(count): int(value)
                for count, value in row["compatible_certificate_count_histogram"].items()
            }
        )
        compatible_per_assignment[int(row["compatible_order_count"])] += 1
        vertex_status_counts.update(
            {
                str(status): int(value)
                for status, value in row["compatible_vertex_circle_status_counts"].items()
            }
        )

    payload = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": source["n"],
        "witness_size": source["witness_size"],
        "source_fixed_order": {
            "cyclic_order": natural_order,
            "hit_assignment_count": source["hit_summary"]["hit_assignment_count"],
            "hit_certificate_count": source["hit_summary"]["hit_certificate_count"],
            "hit_family_ids": _source_hit_family_ids(source),
        },
        "normalized_order_rule": (
            "Fix label 0 first and quotient reversal by retaining only orders "
            "whose second label is smaller than their last label; no geometric "
            "realizability or cyclic-order completeness claim is made."
        ),
        "filter": {
            "order_filters": [
                "adjacent two-overlap rejection",
                "crossing-bisector rejection for every two-overlap",
            ],
            "row_ptolemy_certificate_scope": (
                "fixed selected-witness pattern plus supplied row order only"
            ),
        },
        "normalized_order_count": len(orders),
        "assignment_order_pair_count": len(orders) * len(assignment_rows),
        "family_count": len(family_rows),
        "adjacent_ok_order_count": int(adjacent_ok_order_count),
        "compatible_order_count": sum(compatible_hist.values()),
        "compatible_order_count_per_assignment_counts": _json_counter(
            compatible_per_assignment
        ),
        "compatible_certificate_count_histogram": _json_counter(compatible_hist),
        "compatible_zero_certificate_order_count": int(compatible_hist[0]),
        "compatible_vertex_circle_status_counts": _json_counter(vertex_status_counts),
        "family_rows": family_rows,
        "assignment_rows": assignment_rows,
        "interpretation": [
            "The census covers normalized supplied cyclic orders for the 26 existing fixed-order row-Ptolemy hit assignments only.",
            "An admissible order here only passes the adjacent two-overlap and crossing-bisector filters for the same selected rows.",
            "Admissible assignment-order records with zero row-Ptolemy certificates are diagnostic gaps for this filter, not realizability evidence.",
            "All recorded admissible assignment-order records remain vertex-circle self-edge obstructed in the replayed quotient diagnostic.",
            "No proof of the n=9 case is claimed.",
        ],
        "source_artifacts": [dict(SOURCE_ARTIFACT)],
        "provenance": PROVENANCE,
    }
    assert_expected_counts(payload)
    return payload


def _zero_compatible_rows(payload: dict[str, Any]) -> list[tuple[int, list[int], str]]:
    rows = []
    for assignment in payload.get("assignment_rows", []):
        if not isinstance(assignment, dict):
            continue
        assignment_index = int(assignment.get("assignment_index", -1))
        for order in assignment.get("compatible_orders", []):
            if not isinstance(order, dict):
                continue
            if order.get("certificate_count") == 0:
                rows.append(
                    (
                        assignment_index,
                        list(order.get("order", [])),
                        str(order.get("vertex_circle_status")),
                    )
                )
    return rows


def assert_expected_counts(payload: dict[str, Any]) -> None:
    """Assert stable expected values for the admissible-order census."""

    if payload["schema"] != SCHEMA:
        raise AssertionError(f"unexpected schema: {payload['schema']}")
    if payload["status"] != STATUS:
        raise AssertionError(f"unexpected status: {payload['status']}")
    if payload["trust"] != TRUST:
        raise AssertionError(f"unexpected trust: {payload['trust']}")
    if payload["claim_scope"] != CLAIM_SCOPE:
        raise AssertionError("claim scope changed")
    if payload["n"] != 9 or payload["witness_size"] != 4:
        raise AssertionError("unexpected n/witness size")
    if payload["normalized_order_count"] != 20160:
        raise AssertionError("unexpected normalized order count")
    if payload["assignment_order_pair_count"] != 524160:
        raise AssertionError("unexpected assignment-order pair count")
    if payload["family_count"] != 3:
        raise AssertionError("unexpected family count")
    if payload["adjacent_ok_order_count"] != 1318:
        raise AssertionError("unexpected adjacent-ok order count")
    if payload["compatible_order_count"] != 28:
        raise AssertionError("unexpected compatible order count")
    if payload["compatible_order_count_per_assignment_counts"] != {"1": 24, "2": 2}:
        raise AssertionError("unexpected compatible-order count distribution")
    if payload["compatible_certificate_count_histogram"] != EXPECTED_COMPATIBLE_HISTOGRAM:
        raise AssertionError("unexpected compatible certificate histogram")
    if payload["compatible_zero_certificate_order_count"] != 2:
        raise AssertionError("unexpected zero-compatible-order count")
    if payload["compatible_vertex_circle_status_counts"] != {"self_edge": 28}:
        raise AssertionError("unexpected compatible vertex-circle statuses")
    if payload["family_rows"] != EXPECTED_FAMILY_ROWS:
        raise AssertionError("unexpected family rows")

    assignment_rows = payload["assignment_rows"]
    if not isinstance(assignment_rows, list) or len(assignment_rows) != 26:
        raise AssertionError("unexpected assignment row count")
    total_all_hist: Counter[int] = Counter()
    for row in assignment_rows:
        if row["stored_natural_certificate_count"] != row["natural_certificate_count"]:
            raise AssertionError("stored and replayed natural counts differ")
        total_all_hist.update(
            {
                int(count): int(value)
                for count, value in row["all_order_certificate_count_histogram"].items()
            }
        )
    adjacent_counts = {
        int(row["assignment_index"]): int(row["adjacent_ok_order_count"])
        for row in assignment_rows
    }
    if set(adjacent_counts.values()) != {41, 55}:
        raise AssertionError("unexpected assignment adjacent-ok counts")
    if Counter(adjacent_counts.values()) != {55: 18, 41: 8}:
        raise AssertionError("unexpected adjacent-ok distribution")
    if _json_counter(total_all_hist) != EXPECTED_TOTAL_ALL_ORDER_HISTOGRAM:
        raise AssertionError("unexpected all-order certificate histogram")
    expected_zero_rows = [
        (assignment, EXPECTED_ZERO_COMPATIBLE_ORDER, "self_edge")
        for assignment in EXPECTED_ZERO_COMPATIBLE_ASSIGNMENTS
    ]
    if _zero_compatible_rows(payload) != expected_zero_rows:
        raise AssertionError("unexpected zero-compatible orders")


def _validate_order(errors: list[str], raw_order: Any, *, label: str, n: int) -> None:
    if not isinstance(raw_order, list) or len(raw_order) != n:
        errors.append(f"{label} must be a list of length {n}")
        return
    if not all(type(item) is int for item in raw_order):
        errors.append(f"{label} must contain integer labels")
        return
    if sorted(raw_order) != list(range(n)):
        errors.append(f"{label} must be a permutation of 0..{n - 1}")
        return
    if raw_order[0] != 0:
        errors.append(f"{label} must fix label 0 first")
    if raw_order[1] >= raw_order[-1]:
        errors.append(f"{label} must satisfy reversal quotient order[1] < order[-1]")


def _validate_assignment_rows(payload: dict[str, Any], errors: list[str]) -> None:
    raw_rows = payload.get("assignment_rows")
    if not isinstance(raw_rows, list):
        errors.append("assignment_rows must be a list")
        return

    compatible_count = 0
    adjacent_ok_count = 0
    compatible_hist: Counter[int] = Counter()
    compatible_per_assignment: Counter[int] = Counter()
    vertex_status_counts: Counter[str] = Counter()
    for row_index, row in enumerate(raw_rows):
        if not isinstance(row, dict):
            errors.append(f"assignment_rows[{row_index}] must be an object")
            continue
        row_label = f"assignment_rows[{row_index}]"
        compatible_orders = row.get("compatible_orders")
        if not isinstance(compatible_orders, list):
            errors.append(f"{row_label}.compatible_orders must be a list")
            continue
        raw_selected_rows = row.get("selected_rows")
        selected_rows: list[list[int]] | None
        if not isinstance(raw_selected_rows, list) or len(raw_selected_rows) != 9:
            errors.append(f"{row_label}.selected_rows must be a list of 9 rows")
            selected_rows = None
        else:
            selected_rows = []
            for selected_index, raw_selected_row in enumerate(raw_selected_rows):
                selected_label = f"{row_label}.selected_rows[{selected_index}]"
                if not isinstance(raw_selected_row, list) or len(raw_selected_row) != 4:
                    errors.append(f"{selected_label} must contain 4 witnesses")
                    selected_rows = None
                    break
                if not all(type(label) is int for label in raw_selected_row):
                    errors.append(f"{selected_label} must contain integer labels")
                    selected_rows = None
                    break
                selected_row = [int(label) for label in raw_selected_row]
                if len(set(selected_row)) != 4:
                    errors.append(f"{selected_label} must not repeat witnesses")
                    selected_rows = None
                    break
                if selected_index in selected_row:
                    errors.append(f"{selected_label} must not select its center")
                    selected_rows = None
                    break
                if any(label < 0 or label >= 9 for label in selected_row):
                    errors.append(f"{selected_label} contains a label outside 0..8")
                    selected_rows = None
                    break
                selected_rows.append(selected_row)

        if row.get("compatible_order_count") != len(compatible_orders):
            errors.append(f"{row_label}.compatible_order_count mismatch")
        if row.get("stored_natural_certificate_count") != row.get(
            "natural_certificate_count"
        ):
            errors.append(f"{row_label} stored/natural certificate counts differ")
        adjacent_count = row.get("adjacent_ok_order_count")
        if type(adjacent_count) is not int:
            errors.append(f"{row_label}.adjacent_ok_order_count must be an integer")
            adjacent_count = 0

        row_hist: Counter[int] = Counter()
        row_vertex_statuses: Counter[str] = Counter()
        pair_class: dict[tuple[int, int], int] | None = None
        selected_row_objects = None
        if selected_rows is not None:
            try:
                pair_class, _ = _selected_distance_pair_classes(selected_rows)
                selected_row_objects = parse_selected_rows(selected_rows)
            except (TypeError, ValueError) as exc:
                errors.append(f"{row_label}.selected_rows replay setup failed: {exc}")
                pair_class = None
                selected_row_objects = None
        for order_index, order_row in enumerate(compatible_orders):
            order_label = f"{row_label}.compatible_orders[{order_index}].order"
            if not isinstance(order_row, dict):
                errors.append(f"{row_label}.compatible_orders[{order_index}] must be an object")
                continue
            raw_order = order_row.get("order")
            before_order_error_count = len(errors)
            _validate_order(errors, raw_order, label=order_label, n=9)
            certificate_count = order_row.get("certificate_count")
            if type(certificate_count) is not int:
                errors.append(f"{order_label} certificate_count must be an integer")
                continue
            status = order_row.get("vertex_circle_status")
            if not isinstance(status, str):
                errors.append(f"{order_label} vertex_circle_status must be a string")
                continue
            row_hist[int(certificate_count)] += 1
            row_vertex_statuses[status] += 1
            if (
                len(errors) == before_order_error_count
                and selected_rows is not None
                and pair_class is not None
                and selected_row_objects is not None
            ):
                order_data = _make_order_data(raw_order)
                if not _order_passes_admissible_filters(order_data, phi_map(selected_rows)):
                    errors.append(f"{order_label} does not pass admissible order filters")
                replayed_certificate_count = _certificate_count_for_order(
                    selected_rows,
                    order_data,
                    pair_class,
                )
                if replayed_certificate_count != certificate_count:
                    errors.append(
                        f"{order_label} certificate_count mismatch: "
                        f"expected {replayed_certificate_count!r}, got {certificate_count!r}"
                    )
                replayed_status = replay_vertex_circle_quotient(
                    9,
                    order_data.order,
                    selected_row_objects,
                ).status
                if replayed_status != status:
                    errors.append(
                        f"{order_label} vertex_circle_status mismatch: "
                        f"expected {replayed_status!r}, got {status!r}"
                    )
        if row.get("compatible_certificate_count_histogram") != _json_counter(row_hist):
            errors.append(f"{row_label}.compatible_certificate_count_histogram mismatch")
        if row.get("compatible_zero_certificate_order_count") != int(row_hist[0]):
            errors.append(f"{row_label}.compatible_zero_certificate_order_count mismatch")
        if row.get("compatible_vertex_circle_status_counts") != _json_counter(
            row_vertex_statuses
        ):
            errors.append(f"{row_label}.compatible_vertex_circle_status_counts mismatch")
        if adjacent_count < len(compatible_orders):
            errors.append(f"{row_label}.adjacent_ok_order_count is below compatible count")
        adjacent_ok_count += int(adjacent_count)
        compatible_count += len(compatible_orders)
        compatible_hist.update(row_hist)
        compatible_per_assignment[len(compatible_orders)] += 1
        vertex_status_counts.update(row_vertex_statuses)

    if payload.get("compatible_order_count") != compatible_count:
        errors.append("compatible_order_count does not match assignment rows")
    if payload.get("adjacent_ok_order_count") != adjacent_ok_count:
        errors.append("adjacent_ok_order_count does not match assignment rows")
    if payload.get("compatible_certificate_count_histogram") != _json_counter(
        compatible_hist
    ):
        errors.append("compatible_certificate_count_histogram does not match assignment rows")
    if payload.get("compatible_order_count_per_assignment_counts") != _json_counter(
        compatible_per_assignment
    ):
        errors.append(
            "compatible_order_count_per_assignment_counts does not match assignment rows"
        )
    if payload.get("compatible_vertex_circle_status_counts") != _json_counter(
        vertex_status_counts
    ):
        errors.append("compatible_vertex_circle_status_counts does not match assignment rows")


def validate_payload(
    payload: Any,
    *,
    source: Any | None = None,
    recompute: bool = True,
) -> list[str]:
    """Return validation errors for a loaded admissible-order census."""

    if not isinstance(payload, dict):
        return ["artifact top level must be a JSON object"]

    errors: list[str] = []
    if set(payload) != EXPECTED_TOP_LEVEL_KEYS:
        errors.append(
            "top-level keys mismatch: "
            f"expected {sorted(EXPECTED_TOP_LEVEL_KEYS)!r}, got {sorted(payload)!r}"
        )
    expected_meta = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": 9,
        "witness_size": 4,
        "source_artifacts": [SOURCE_ARTIFACT],
        "provenance": PROVENANCE,
        "normalized_order_count": 20160,
        "assignment_order_pair_count": 524160,
        "adjacent_ok_order_count": 1318,
    }
    for key, expected in expected_meta.items():
        expect_equal(errors, key, payload.get(key), expected)

    source_fixed_order = payload.get("source_fixed_order")
    if not isinstance(source_fixed_order, dict):
        errors.append("source_fixed_order must be an object")
    else:
        expect_equal(errors, "source fixed cyclic order", source_fixed_order.get("cyclic_order"), list(range(9)))
        expect_equal(errors, "source hit assignments", source_fixed_order.get("hit_assignment_count"), 26)
        expect_equal(errors, "source hit certificates", source_fixed_order.get("hit_certificate_count"), 216)
        expect_equal(errors, "source hit families", source_fixed_order.get("hit_family_ids"), ["F02", "F09", "F13"])

    interpretation = payload.get("interpretation")
    if not isinstance(interpretation, list) or not all(
        isinstance(item, str) for item in interpretation
    ):
        errors.append("interpretation must be a list of strings")
    else:
        required = (
            "Admissible assignment-order records with zero row-Ptolemy certificates are diagnostic gaps for this filter, not realizability evidence.",
            "All recorded admissible assignment-order records remain vertex-circle self-edge obstructed in the replayed quotient diagnostic.",
            "No proof of the n=9 case is claimed.",
        )
        for phrase in required:
            if phrase not in interpretation:
                errors.append(f"interpretation must include {phrase!r}")

    try:
        assert_expected_counts(payload)
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"expected counts failed: {exc}")
    _validate_assignment_rows(payload, errors)

    if recompute:
        if source is None:
            try:
                source = load_artifact(DEFAULT_ROW_PTOLEMY_ARTIFACT)
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"failed to load source row-Ptolemy artifact: {exc}")
                source = None
        if isinstance(source, dict):
            try:
                expected_payload = admissible_census_payload(source)
            except (AssertionError, TypeError, ValueError) as exc:
                errors.append(f"recomputed admissible-order census failed: {exc}")
            else:
                expect_equal(errors, "admissible-order census", payload, expected_payload)
        else:
            errors.append("source row-Ptolemy artifact must be an object")
    return errors


def summary_payload(path: Path, payload: Any, errors: Sequence[str]) -> dict[str, Any]:
    """Return a compact checker summary."""

    object_payload = payload if isinstance(payload, dict) else {}
    return {
        "ok": not errors,
        "artifact": display_path(path, ROOT),
        "schema": object_payload.get("schema"),
        "status": object_payload.get("status"),
        "trust": object_payload.get("trust"),
        "normalized_order_count": object_payload.get("normalized_order_count"),
        "assignment_order_pair_count": object_payload.get("assignment_order_pair_count"),
        "adjacent_ok_order_count": object_payload.get("adjacent_ok_order_count"),
        "compatible_order_count": object_payload.get("compatible_order_count"),
        "compatible_certificate_count_histogram": object_payload.get(
            "compatible_certificate_count_histogram"
        ),
        "compatible_zero_certificate_order_count": object_payload.get(
            "compatible_zero_certificate_order_count"
        ),
        "family_ids": [
            row.get("family_id")
            for row in object_payload.get("family_rows", [])
            if isinstance(row, dict)
        ],
        "validation_errors": list(errors),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--source", type=Path, default=DEFAULT_ROW_PTOLEMY_ARTIFACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--write", action="store_true", help="write generated census")
    parser.add_argument("--check", action="store_true", help="validate an existing census")
    parser.add_argument("--json", action="store_true", help="print stable JSON summary")
    parser.add_argument("--assert-expected", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    artifact = args.artifact if args.artifact.is_absolute() else ROOT / args.artifact
    source_path = args.source if args.source.is_absolute() else ROOT / args.source
    out = args.out if args.out.is_absolute() else ROOT / args.out

    try:
        source = load_artifact(source_path)
    except (OSError, json.JSONDecodeError) as exc:
        source = {}
        source_errors = [str(exc)]
    else:
        source_errors = validate_row_ptolemy_payload(source, recompute=False)

    if args.write:
        if source_errors:
            for error in source_errors:
                print(f"source artifact invalid: {error}", file=sys.stderr)
            return 1
        payload = admissible_census_payload(source)
        if args.assert_expected:
            assert_expected_counts(payload)
        write_json(payload, out)
        if not args.check:
            if args.json:
                print(json.dumps(summary_payload(out, payload, []), indent=2, sort_keys=True))
            else:
                print(f"wrote {display_path(out, ROOT)}")
            return 0

    try:
        payload = load_artifact(artifact)
        errors = validate_payload(
            payload,
            source=source,
            recompute=args.check or args.assert_expected,
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        payload = {}
        errors = [str(exc)]
    if source_errors:
        errors.extend(f"source artifact invalid: {error}" for error in source_errors)

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    elif errors:
        print(f"FAILED: {display_path(artifact, ROOT)}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
    else:
        print("n=9 row-Ptolemy admissible-order census")
        print(f"artifact: {summary['artifact']}")
        print(f"normalized orders: {summary['normalized_order_count']}")
        print(f"assignment-order pairs: {summary['assignment_order_pair_count']}")
        print(f"adjacent-ok orders: {summary['adjacent_ok_order_count']}")
        print(f"admissible assignment-order records: {summary['compatible_order_count']}")
        print(
            "zero-certificate admissible records: "
            f"{summary['compatible_zero_certificate_order_count']}"
        )
        if args.check or args.assert_expected:
            print("OK: row-Ptolemy admissible-order census checks passed")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
