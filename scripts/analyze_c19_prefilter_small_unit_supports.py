#!/usr/bin/env python3
"""Search small unit-weight Kalmanson cancellations for C19 fallback children.

The two-row prefilter finds one forced row that is zero after quotienting, or
two forced rows that are exact opposites.  This diagnostic asks the next exact
question on the recorded fallback children: does any fallback child have a
unit-weight cancellation using at most three forced Kalmanson rows?

The search is exhaustive for support size <= 3 over the recorded fallback
children only.  It is not an all-order C19 search and not a proof of Erdos
Problem #97.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

from check_kalmanson_certificate import build_distance_classes
from pilot_c19_kalmanson_prefix_branches import (
    N,
    OFFSETS,
    PATTERN_NAME,
    BoundaryState,
    label_digest,
    prefix_kalmanson_rows,
)
from analyze_c19_fifth_pair_two_row_prefilter import two_row_certificate_for_state
from analyze_c19_prefilter_fallback_supports import (
    _as_list,
    _as_mapping,
    _fallback_states,
    _relative_path,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = (
    ROOT
    / "data"
    / "certificates"
    / "c19_kalmanson_prefix_window_prefilter_sweep_288_479.json"
)
DEFAULT_OUT = ROOT / "reports" / "c19_prefilter_small_unit_support_search.json"

SparseVector = tuple[tuple[int, int], ...]


def _sparse(vector: tuple[int, ...]) -> SparseVector:
    return tuple((idx, value) for idx, value in enumerate(vector) if value)


def _neg(vector: SparseVector) -> SparseVector:
    return tuple((idx, -value) for idx, value in vector)


def _add(left: SparseVector, right: SparseVector) -> SparseVector:
    values: dict[int, int] = {}
    for idx, value in left:
        values[idx] = values.get(idx, 0) + value
    for idx, value in right:
        values[idx] = values.get(idx, 0) + value
    return tuple((idx, value) for idx, value in sorted(values.items()) if value)


def _row_payload(row: Any) -> dict[str, object]:
    return {
        "weight": 1,
        "kind": row.kind,
        "quad": list(row.quad),
    }


def unit_support_at_most_three(
    state: BoundaryState,
    classes: Mapping[tuple[int, int], int],
) -> tuple[int, list[dict[str, object]], int]:
    rows = prefix_kalmanson_rows(state, classes)
    sparse_rows = [_sparse(row.vector) for row in rows]
    by_vector: dict[SparseVector, list[int]] = {}
    for idx, vector in enumerate(sparse_rows):
        by_vector.setdefault(vector, []).append(idx)

    for idx, vector in enumerate(sparse_rows):
        if not vector:
            return len(rows), [_row_payload(rows[idx])], 0

    pair_count = 0
    for i, left in enumerate(sparse_rows):
        for j in range(i + 1, len(sparse_rows)):
            right = sparse_rows[j]
            pair_count += 1
            if not _add(left, right):
                return len(rows), [_row_payload(rows[i]), _row_payload(rows[j])], pair_count
            target = _neg(_add(left, right))
            for k in by_vector.get(target, []):
                if k != i and k != j:
                    if _add(_add(left, right), sparse_rows[k]):
                        raise AssertionError("three-row lookup produced a nonzero sum")
                    support = sorted([i, j, k])
                    return len(rows), [_row_payload(rows[idx]) for idx in support], pair_count

    return len(rows), [], pair_count


def analyze_small_unit_supports(
    source: Mapping[str, Any],
    *,
    source_artifact: str,
) -> dict[str, Any]:
    if source["type"] != "c19_kalmanson_prefix_window_prefilter_sweep_v1":
        raise ValueError("expected compact C19 prefilter sweep artifact")

    classes = build_distance_classes(N, OFFSETS)
    records: list[dict[str, Any]] = []
    labels: list[str] = []
    support_histogram: Counter[str] = Counter()
    row_count_histogram: Counter[int] = Counter()
    pair_count_histogram: Counter[int] = Counter()
    total_pairs_checked = 0
    found_count = 0
    two_row_miss_count = 0

    for item in _fallback_states(source):
        state = item.pop("state")
        if not isinstance(state, BoundaryState):
            raise TypeError("internal fallback state reconstruction failed")
        label = str(item["label"])
        labels.append(label)
        row_count, two_row = two_row_certificate_for_state(state, classes)
        if two_row:
            raise AssertionError(f"fallback label now has a two-row certificate: {label}")
        two_row_miss_count += 1
        search_row_count, support, pair_count = unit_support_at_most_three(state, classes)
        if search_row_count != row_count:
            raise AssertionError("row count changed between prefilter and unit search")
        row_count_histogram[row_count] += 1
        pair_count_histogram[pair_count] += 1
        total_pairs_checked += pair_count
        if support:
            found_count += 1
            support_histogram[str(len(support))] += 1
        else:
            support_histogram["none"] += 1
        records.append(
            {
                **item,
                "forced_inequalities_available": row_count,
                "pair_sums_checked": pair_count,
                "unit_support_at_most_three_found": bool(support),
                "unit_support": support,
            }
        )

    expected_count = int(
        _as_mapping(source["aggregate_accounting"], "aggregate_accounting")[
            "fifth_pair_farkas_fallback_certified_count"
        ]
    )
    if len(records) != expected_count:
        raise AssertionError(f"reconstructed {len(records)} fallback children, expected {expected_count}")

    return {
        "type": "c19_prefilter_small_unit_support_search_v1",
        "trust": "EXACT_OBSTRUCTION",
        "source_artifact": source_artifact,
        "source_prefix_label_digest": source["prefix_label_digest"],
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "This is an exact small-support diagnostic over recorded C19 fallback children only.",
            "The search is exhaustive for unit-weight cancellations using at most three forced Kalmanson rows.",
            "A missing small unit support does not rule out larger supports, non-unit weights, or other exact prefilters.",
            "This does not certify branches beyond the recorded sampled windows and is not an all-order C19 obstruction.",
        ],
        "parameters": {
            "max_unit_support_size": 3,
            "fifth_pair_prefilter": "two_row_kalmanson_prefilter",
        },
        "pattern": {
            "name": PATTERN_NAME,
            "n": N,
            "circulant_offsets": OFFSETS,
        },
        "aggregate": {
            "fallback_child_count": len(records),
            "two_row_prefilter_miss_count": two_row_miss_count,
            "unit_support_at_most_three_found_count": found_count,
            "unit_support_at_most_three_missing_count": len(records) - found_count,
            "total_pair_sums_checked": total_pairs_checked,
            "fallback_label_digest": label_digest(labels),
            "exhaustive_unit_support_bound": 3,
        },
        "histograms": {
            "forced_row_count": {str(k): row_count_histogram[k] for k in sorted(row_count_histogram)},
            "unit_support_result": dict(sorted(support_histogram.items())),
            "pair_sums_checked": {
                str(k): pair_count_histogram[k] for k in sorted(pair_count_histogram)
            },
        },
        "fallback_records": records,
    }


def assert_expected(data: Mapping[str, Any]) -> None:
    aggregate = _as_mapping(data["aggregate"], "aggregate")
    expected_aggregate = {
        "fallback_child_count": 8,
        "two_row_prefilter_miss_count": 8,
        "unit_support_at_most_three_found_count": 7,
        "unit_support_at_most_three_missing_count": 1,
        "total_pair_sums_checked": 15428396,
        "fallback_label_digest": "2dc4965b208144017b7aba73dba920c8c8f8f1eea93a2f84650eb4f5f484f0c8",
        "exhaustive_unit_support_bound": 3,
    }
    for key, expected in expected_aggregate.items():
        if aggregate[key] != expected:
            raise AssertionError(f"{key} changed: {aggregate[key]} != {expected}")
    histograms = _as_mapping(data["histograms"], "histograms")
    if histograms["forced_row_count"] != {"3300": 8}:
        raise AssertionError("forced row-count histogram changed")
    if histograms["unit_support_result"] != {"3": 7, "none": 1}:
        raise AssertionError("unit-support result histogram changed")
    records = _as_list(data["fallback_records"], "fallback_records")
    missing = [row["label"] for row in records if not row["unit_support_at_most_three_found"]]
    if missing != ["c19_window_fifth_child_0430_0081_0011"]:
        raise AssertionError("small-unit missing label list changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, help="write JSON payload to this path")
    parser.add_argument("--json", action="store_true", help="print JSON payload")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    source = _as_mapping(json.loads(args.source.read_text(encoding="utf-8")), "source")
    data = analyze_small_unit_supports(
        source,
        source_artifact=_relative_path(args.source),
    )
    if args.assert_expected:
        assert_expected(data)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        aggregate = _as_mapping(data["aggregate"], "aggregate")
        print(
            "C19 fallback small unit supports: "
            f"found={aggregate['unit_support_at_most_three_found_count']} "
            f"missing={aggregate['unit_support_at_most_three_missing_count']} "
            f"pairs={aggregate['total_pair_sums_checked']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
