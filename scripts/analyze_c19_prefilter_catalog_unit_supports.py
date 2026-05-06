#!/usr/bin/env python3
"""Verify cataloged three-row C19 fallback prefilter supports.

The exhaustive small-unit search records one support witness for each sampled
C19 fifth-pair fallback child where a unit-weight cancellation of size <= 3
exists.  This analyzer turns those recorded witnesses into a compact catalog
and replays them as cheap exact prefilter rules over the same fallback states.

The scope is only the recorded fallback children from the compact C19
prefilter-window sweep.  This is not an all-order C19 search and does not
settle Erdos Problem #97.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from analyze_c19_fifth_pair_two_row_prefilter import two_row_certificate_for_state
from analyze_c19_prefilter_fallback_supports import (
    _as_list,
    _as_mapping,
    _fallback_states,
    _histogram,
    _relative_path,
)
from check_kalmanson_certificate import build_distance_classes
from pilot_c19_kalmanson_prefix_branches import (
    N,
    OFFSETS,
    PATTERN_NAME,
    BoundaryState,
    label_digest,
    prefix_kalmanson_rows,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = (
    ROOT
    / "data"
    / "certificates"
    / "c19_kalmanson_prefix_window_prefilter_sweep_288_479.json"
)
DEFAULT_SUPPORTS = ROOT / "reports" / "c19_prefilter_small_unit_support_search.json"
DEFAULT_OUT = ROOT / "reports" / "c19_prefilter_catalog_unit_supports.json"


def _support_line(support: Sequence[Mapping[str, object]]) -> str:
    parts = []
    for item in support:
        quad = ",".join(str(value) for value in _as_list(item["quad"], "quad"))
        parts.append(f"{int(item['weight'])}:{item['kind']}:{quad}")
    return ";".join(parts)


def _digest(lines: Sequence[str]) -> str:
    payload = "".join(f"{line}\n" for line in lines)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _vector_sum(vectors: Sequence[tuple[int, ...]]) -> tuple[int, ...]:
    if not vectors:
        return ()
    width = len(vectors[0])
    values = [0] * width
    for vector in vectors:
        if len(vector) != width:
            raise AssertionError("incompatible vector widths")
        for idx, value in enumerate(vector):
            values[idx] += value
    return tuple(values)


def _load_catalog(support_payload: Mapping[str, Any]) -> list[dict[str, object]]:
    if support_payload["type"] != "c19_prefilter_small_unit_support_search_v1":
        raise ValueError("expected C19 small-unit support search artifact")

    catalog: list[dict[str, object]] = []
    seen: set[str] = set()
    for row in _as_list(support_payload["fallback_records"], "fallback_records"):
        record = _as_mapping(row, "fallback_record")
        if not bool(record["unit_support_at_most_three_found"]):
            continue
        support = [
            dict(_as_mapping(item, "support item"))
            for item in _as_list(record["unit_support"], "unit_support")
        ]
        line = _support_line(support)
        if line in seen:
            continue
        seen.add(line)
        catalog.append(
            {
                "catalog_id": f"unit_support_{len(catalog):03d}",
                "support": support,
                "support_line": line,
            }
        )
    return catalog


def _catalog_certificate_for_state(
    state: BoundaryState,
    classes: Mapping[tuple[int, int], int],
    catalog: Sequence[Mapping[str, object]],
) -> dict[str, object] | None:
    rows = prefix_kalmanson_rows(state, classes)
    by_key = {(row.kind, tuple(row.quad)): row for row in rows}
    for item in catalog:
        support = [
            _as_mapping(row, "catalog support row")
            for row in _as_list(item["support"], "catalog support")
        ]
        vectors: list[tuple[int, ...]] = []
        missing = False
        for support_row in support:
            if int(support_row["weight"]) != 1:
                raise AssertionError("catalog support is expected to be unit weight")
            quad = tuple(int(value) for value in _as_list(support_row["quad"], "quad"))
            row = by_key.get((str(support_row["kind"]), quad))
            if row is None:
                missing = True
                break
            vectors.append(row.vector)
        if missing:
            continue
        if any(_vector_sum(vectors)):
            raise AssertionError("catalog support rows do not sum to zero")
        return {
            "catalog_id": item["catalog_id"],
            "positive_inequalities": len(support),
            "forced_inequalities_available": len(rows),
            "inequalities": support,
        }
    return None


def analyze_catalog_unit_supports(
    source: Mapping[str, Any],
    support_payload: Mapping[str, Any],
    *,
    source_artifact: str,
    support_artifact: str,
) -> dict[str, Any]:
    if source["type"] != "c19_kalmanson_prefix_window_prefilter_sweep_v1":
        raise ValueError("expected compact C19 prefilter sweep artifact")

    classes = build_distance_classes(N, OFFSETS)
    catalog = _load_catalog(support_payload)
    records: list[dict[str, Any]] = []
    fallback_labels: list[str] = []
    certified_labels: list[str] = []
    input_support_labels: list[str] = []
    catalog_usage: Counter[str] = Counter()
    two_row_miss_count = 0
    catalog_certified_count = 0

    support_records = _as_list(support_payload["fallback_records"], "fallback_records")
    for row in support_records:
        support_record = _as_mapping(row, "support fallback record")
        if bool(support_record["unit_support_at_most_three_found"]):
            input_support_labels.append(str(support_record["label"]))

    for item in _fallback_states(source):
        state = item.pop("state")
        if not isinstance(state, BoundaryState):
            raise TypeError("internal fallback state reconstruction failed")
        label = str(item["label"])
        fallback_labels.append(label)
        _, two_row = two_row_certificate_for_state(state, classes)
        if two_row:
            raise AssertionError(f"fallback label now has a two-row certificate: {label}")
        two_row_miss_count += 1

        certificate = _catalog_certificate_for_state(state, classes, catalog)
        if certificate is None:
            catalog_usage["none"] += 1
        else:
            catalog_certified_count += 1
            certified_labels.append(label)
            catalog_usage[str(certificate["catalog_id"])] += 1
        records.append(
            {
                **item,
                "catalog_unit_support_found": certificate is not None,
                "catalog_certificate": certificate,
            }
        )

    expected_count = int(
        _as_mapping(source["aggregate_accounting"], "aggregate_accounting")[
            "fifth_pair_farkas_fallback_certified_count"
        ]
    )
    if len(records) != expected_count:
        raise AssertionError(f"reconstructed {len(records)} fallback children, expected {expected_count}")
    if sorted(certified_labels) != sorted(input_support_labels):
        raise AssertionError("catalog replay does not match the small-unit support artifact")

    support_lines = [str(item["support_line"]) for item in catalog]
    return {
        "type": "c19_prefilter_catalog_unit_supports_v1",
        "trust": "EXACT_OBSTRUCTION",
        "source_artifact": source_artifact,
        "support_artifact": support_artifact,
        "source_prefix_label_digest": source["prefix_label_digest"],
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "This replays cataloged three-row unit Kalmanson supports over recorded C19 fallback children only.",
            "Each catalog hit is rechecked by exact vector summation after selected-distance quotienting.",
            "This does not certify branches beyond the recorded sampled windows and is not an all-order C19 obstruction.",
        ],
        "parameters": {
            "catalog_source": "nonempty supports from c19_prefilter_small_unit_support_search_v1",
            "fifth_pair_prefilter_chain": "two_row_then_cataloged_three_row_unit_support",
        },
        "pattern": {
            "name": PATTERN_NAME,
            "n": N,
            "circulant_offsets": OFFSETS,
        },
        "aggregate": {
            "fallback_child_count": len(records),
            "two_row_prefilter_miss_count": two_row_miss_count,
            "catalog_support_count": len(catalog),
            "input_support_record_count": len(input_support_labels),
            "catalog_certified_count": catalog_certified_count,
            "catalog_miss_count": len(records) - catalog_certified_count,
            "fallback_label_digest": label_digest(fallback_labels),
            "catalog_certified_label_digest": label_digest(certified_labels),
            "catalog_support_digest": _digest(support_lines),
        },
        "histograms": {
            "catalog_usage": _histogram(catalog_usage),
        },
        "catalog": [
            {
                "catalog_id": str(item["catalog_id"]),
                "support": item["support"],
            }
            for item in catalog
        ],
        "fallback_records": records,
    }


def assert_expected(data: Mapping[str, Any]) -> None:
    aggregate = _as_mapping(data["aggregate"], "aggregate")
    expected_aggregate = {
        "fallback_child_count": 8,
        "two_row_prefilter_miss_count": 8,
        "catalog_support_count": 2,
        "input_support_record_count": 7,
        "catalog_certified_count": 7,
        "catalog_miss_count": 1,
        "fallback_label_digest": "2dc4965b208144017b7aba73dba920c8c8f8f1eea93a2f84650eb4f5f484f0c8",
        "catalog_certified_label_digest": "03412b1e4da3c1de13345b052773aef2ae944f06028529f6c0f0d0a39e2a8ea6",
        "catalog_support_digest": "b4110d03ca090444ce9585c24d89ca8a71be87d1e7df55507cbc47ef41a5aee5",
    }
    for key, expected in expected_aggregate.items():
        if aggregate[key] != expected:
            raise AssertionError(f"{key} changed: {aggregate[key]} != {expected}")
    histograms = _as_mapping(data["histograms"], "histograms")
    if histograms["catalog_usage"] != {
        "none": 1,
        "unit_support_000": 6,
        "unit_support_001": 1,
    }:
        raise AssertionError("catalog usage histogram changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--supports", type=Path, default=DEFAULT_SUPPORTS)
    parser.add_argument("--out", type=Path, help="write JSON payload to this path")
    parser.add_argument("--json", action="store_true", help="print JSON payload")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    source = _as_mapping(json.loads(args.source.read_text(encoding="utf-8")), "source")
    support_payload = _as_mapping(
        json.loads(args.supports.read_text(encoding="utf-8")),
        "support payload",
    )
    data = analyze_catalog_unit_supports(
        source,
        support_payload,
        source_artifact=_relative_path(args.source),
        support_artifact=_relative_path(args.supports),
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
            "C19 catalog unit supports: "
            f"certified={aggregate['catalog_certified_count']} "
            f"missing={aggregate['catalog_miss_count']} "
            f"catalog={aggregate['catalog_support_count']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
