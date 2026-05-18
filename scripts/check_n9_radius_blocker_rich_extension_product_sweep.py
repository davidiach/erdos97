#!/usr/bin/env python3
"""Check the full rich-extension product over all n=9 blocker packets.

This is a finite bridge diagnostic only. It proves no general theorem about
Erdos Problem #97 and supplies no counterexample.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from check_n9_radius_blocker_rich_extension_neighborhood import (  # noqa: E402
    extension_catalog,
    rich_classes_for_blocker,
    rich_rows_from_added_labels,
)
from check_n9_radius_blocker_rich_extension_product_pilot import (  # noqa: E402
    build_source_product_summary,
    iter_full_product_added_label_variants,
    source_product_records,
)
from check_n9_radius_blocker_rich_quotient_sweep import (  # noqa: E402
    DEFAULT_SOURCE,
    N,
    ORDER,
    counter_to_json,
    load_shape_sweep,
    sha256_file,
    source_examples,
)
from erdos97.adaptive_blockers import is_radius_blocker  # noqa: E402
from erdos97.radius_blocker_packets import TRUST  # noqa: E402
from erdos97.vertex_circle_quotient_replay import (  # noqa: E402
    replay_vertex_circle_rich_quotient,
)

SCHEMA = "erdos97.n9_radius_blocker_rich_extension_product_sweep.v1"
STATUS = "N9_RADIUS_BLOCKER_RICH_EXTENSION_PRODUCT_SWEEP_ONLY"
DEFAULT_OUT = (
    ROOT
    / "data"
    / "certificates"
    / "n9_radius_blocker_rich_extension_product_sweep.json"
)
EXPECTED_SUMMARY = {
    "n": 9,
    "source_shape_count": 10,
    "source_packet_count": 20,
    "source_status_counts": {"self_edge": 10, "strict_cycle": 10},
    "source_product_variant_count_total": 2899968,
    "source_product_variant_count_counts": {
        "110592": 8,
        "147456": 7,
        "196608": 5,
    },
    "source_row_option_count_profile": {"3": 43, "4": 137},
    "source_row_alternative_count_profile": {"2": 43, "3": 137},
    "variant_count": 2899968,
    "hamming_distance_counts": {
        "0": 20,
        "1": 497,
        "2": 5479,
        "3": 35167,
        "4": 144819,
        "5": 396765,
        "6": 723141,
        "7": 845397,
        "8": 575181,
        "9": 173502,
    },
    "variant_rich_class_count_total": 26099712,
    "max_rich_class_size": 5,
    "all_variants_radius_blockers": True,
    "quotient_status_counts": {"self_edge": 2899968},
    "all_variants_obstructed": True,
    "total_strict_edge_count": 652492800,
    "total_self_edge_conflict_count": 467149054,
    "min_self_edge_conflict_count": 51,
    "max_self_edge_conflict_count": 225,
    "first_self_edge_row_counts": {"0": 2899968},
    "variant_max_blocker_intersection_size_counts": {
        "2": 6912,
        "3": 1693440,
        "4": 1199616,
    },
}


def build_source_packet_record(
    source: Mapping[str, object],
    product_record: Mapping[str, object],
    *,
    max_variants_per_packet: int | None = None,
) -> dict[str, object]:
    selected_rows = source["source_selected_rows"]
    if not isinstance(selected_rows, list):
        raise AssertionError("source selected rows are missing")
    rows = [[int(label) for label in row] for row in selected_rows]
    blocker = [int(label) for label in source["blocker"]]
    blocker_set = set(blocker)
    baseline, alternatives, catalog_records = extension_catalog(rows, blocker)

    hamming_distance_counts: Counter[int] = Counter()
    quotient_status_counts: Counter[str] = Counter()
    first_self_edge_rows: Counter[int | None] = Counter()
    max_blocker_intersections: Counter[int] = Counter()
    self_edge_counts: list[int] = []
    total_strict_edges = 0
    all_radius_blockers = True
    variant_count = 0
    max_rich_class_size = 0
    seen_variants: set[tuple[int, ...]] = set()

    for distance, added_labels in iter_full_product_added_label_variants(
        baseline, alternatives
    ):
        if (
            max_variants_per_packet is not None
            and variant_count >= max_variants_per_packet
        ):
            break
        if added_labels in seen_variants:
            raise AssertionError("duplicate full-product variant")
        seen_variants.add(added_labels)

        rich_rows = rich_rows_from_added_labels(rows, added_labels)
        all_radius_blockers = all_radius_blockers and is_radius_blocker(
            rich_classes_for_blocker(rich_rows), blocker
        )
        replay = replay_vertex_circle_rich_quotient(N, ORDER, rich_rows)

        hamming_distance_counts[distance] += 1
        quotient_status_counts[str(replay.status)] += 1
        total_strict_edges += int(replay.strict_edge_count)
        self_edge_counts.append(len(replay.self_edge_conflicts))
        first_self_edge_rows[
            int(replay.self_edge_conflicts[0].row)
            if replay.self_edge_conflicts
            else None
        ] += 1
        max_blocker_intersections[
            max(len(set(row.witnesses) & blocker_set) for row in rich_rows)
        ] += 1
        max_rich_class_size = max(
            max_rich_class_size,
            max(len(row.witnesses) for row in rich_rows),
        )
        variant_count += 1

    first_self_edge_json = counter_to_json(first_self_edge_rows)
    first_self_edge_json.pop("None", None)

    return {
        "source_packet_id": str(product_record["source_packet_id"]),
        "source_order_index": int(product_record["source_order_index"]),
        "case_index": int(source["case_index"]),
        "case_name": str(source["case_name"]),
        "blocker": blocker,
        "source_status": str(source["source_status"]),
        "source_example_index": int(source["source_example_index"]),
        "source_selected_rows": rows,
        "row_extension_catalog": catalog_records,
        "row_option_counts": list(product_record["row_option_counts"]),
        "row_alternative_counts": list(product_record["row_alternative_counts"]),
        "product_variant_count": int(product_record["product_variant_count"]),
        "replayed_variant_count": variant_count,
        "truncated": max_variants_per_packet is not None
        and variant_count < int(product_record["product_variant_count"]),
        "hamming_distance_counts": counter_to_json(hamming_distance_counts),
        "all_variants_radius_blockers": all_radius_blockers,
        "quotient_status_counts": counter_to_json(quotient_status_counts),
        "all_variants_obstructed": quotient_status_counts.get("ok", 0) == 0,
        "total_strict_edge_count": total_strict_edges,
        "total_self_edge_conflict_count": sum(self_edge_counts),
        "min_self_edge_conflict_count": min(self_edge_counts),
        "max_self_edge_conflict_count": max(self_edge_counts),
        "first_self_edge_row_counts": first_self_edge_json,
        "variant_max_blocker_intersection_size_counts": counter_to_json(
            max_blocker_intersections
        ),
        "max_rich_class_size": max_rich_class_size,
    }


def build_summary(
    records: Sequence[Mapping[str, object]],
    product_records: Sequence[Mapping[str, object]],
    source_shape_count: int,
) -> dict[str, object]:
    source_product_summary = build_source_product_summary(product_records)
    source_status_counts: Counter[str] = Counter()
    option_count_profile: Counter[int] = Counter()
    alternative_count_profile: Counter[int] = Counter()
    hamming_distance_counts: Counter[str] = Counter()
    quotient_status_counts: Counter[str] = Counter()
    first_self_edge_rows: Counter[str] = Counter()
    max_blocker_intersections: Counter[str] = Counter()
    variant_count = 0
    strict_edge_count = 0
    self_edge_total = 0
    self_edge_min: int | None = None
    self_edge_max = 0
    max_rich_class_size = 0

    for product_record in product_records:
        source_status_counts[str(product_record["source_status"])] += 1
        for count in product_record["row_option_counts"]:
            option_count_profile[int(count)] += 1
        for count in product_record["row_alternative_counts"]:
            alternative_count_profile[int(count)] += 1

    for record in records:
        record_variant_count = int(record["replayed_variant_count"])
        variant_count += record_variant_count
        strict_edge_count += int(record["total_strict_edge_count"])
        self_edge_total += int(record["total_self_edge_conflict_count"])
        record_min = int(record["min_self_edge_conflict_count"])
        record_max = int(record["max_self_edge_conflict_count"])
        self_edge_min = record_min if self_edge_min is None else min(
            self_edge_min, record_min
        )
        self_edge_max = max(self_edge_max, record_max)
        max_rich_class_size = max(
            max_rich_class_size, int(record["max_rich_class_size"])
        )
        for key, value in record["hamming_distance_counts"].items():
            hamming_distance_counts[str(key)] += int(value)
        for key, value in record["quotient_status_counts"].items():
            quotient_status_counts[str(key)] += int(value)
        for key, value in record["first_self_edge_row_counts"].items():
            first_self_edge_rows[str(key)] += int(value)
        for key, value in record["variant_max_blocker_intersection_size_counts"].items():
            max_blocker_intersections[str(key)] += int(value)

    return {
        "n": N,
        "order": ORDER,
        "source_shape_count": source_shape_count,
        "source_packet_count": len(product_records),
        "source_status_counts": counter_to_json(source_status_counts),
        "source_product_variant_count_total": source_product_summary[
            "source_product_variant_count_total"
        ],
        "source_product_variant_count_counts": source_product_summary[
            "source_product_variant_count_counts"
        ],
        "source_row_option_count_profile": counter_to_json(option_count_profile),
        "source_row_alternative_count_profile": counter_to_json(
            alternative_count_profile
        ),
        "variant_count": variant_count,
        "hamming_distance_counts": counter_to_json(hamming_distance_counts),
        "variant_rich_class_count_total": variant_count * N,
        "max_rich_class_size": max_rich_class_size,
        "all_variants_radius_blockers": all(
            bool(record["all_variants_radius_blockers"]) for record in records
        ),
        "quotient_status_counts": counter_to_json(quotient_status_counts),
        "all_variants_obstructed": quotient_status_counts.get("ok", 0) == 0,
        "total_strict_edge_count": strict_edge_count,
        "total_self_edge_conflict_count": self_edge_total,
        "min_self_edge_conflict_count": self_edge_min,
        "max_self_edge_conflict_count": self_edge_max,
        "first_self_edge_row_counts": counter_to_json(first_self_edge_rows),
        "variant_max_blocker_intersection_size_counts": counter_to_json(
            max_blocker_intersections
        ),
    }


def build_payload(
    source: Path = DEFAULT_SOURCE,
    *,
    max_packets: int | None = None,
    max_variants_per_packet: int | None = None,
) -> dict[str, object]:
    shape_sweep = load_shape_sweep(source)
    sources = source_examples(shape_sweep)
    product_records = source_product_records(sources)
    replay_sources = sources if max_packets is None else sources[:max_packets]
    replay_product_records = (
        product_records if max_packets is None else product_records[:max_packets]
    )
    records = [
        build_source_packet_record(
            source_record,
            product_record,
            max_variants_per_packet=max_variants_per_packet,
        )
        for source_record, product_record in zip(
            replay_sources, replay_product_records, strict=True
        )
    ]
    cases = shape_sweep.get("cases")
    if not isinstance(cases, list):
        raise AssertionError("shape sweep artifact has no cases list")

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": (
            "All-packet n=9 full rich-extension product replay over the 20 "
            "generated radius-blocker quotient-sweep source packets. It "
            "replays every radius-blocker-preserving size-five added-label "
            "choice for those generated packets. This is finite generated "
            "packet evidence only: it is not an n=9 proof, not a proof of the "
            "adaptive blocker bridge, and not a counterexample."
        ),
        "summary": build_summary(records, product_records, len(cases)),
        "source_shape_sweep": {
            "path": source.relative_to(ROOT).as_posix(),
            "schema": shape_sweep.get("schema"),
            "status": shape_sweep.get("status"),
            "trust": shape_sweep.get("trust"),
            "sha256": sha256_file(source),
            "summary": shape_sweep.get("summary"),
        },
        "source_product_catalog": build_source_product_summary(product_records),
        "product_rule": {
            "catalogue": (
                "For each row, enumerate every extra label that preserves the "
                "actual radius-blocker condition: inside-blocker centers must "
                "stay below three blocker vertices, while outside-blocker "
                "centers are unconstrained by blocker intersection."
            ),
            "variants": (
                "Replay the full Cartesian product of those row extension "
                "choices for every generated source packet."
            ),
        },
        "debug_limits": {
            "max_packets": max_packets,
            "max_variants_per_packet": max_variants_per_packet,
        },
        "source_packets": records,
        "interpretation_warnings": [
            "This checks only generated size-five packets derived from stored examples.",
            "It does not enumerate arbitrary rich-class catalogues.",
            "It does not prove the adaptive radius-blocker bridge.",
            "No general proof and no counterexample are claimed.",
        ],
        "provenance": {
            "generator": "scripts/check_n9_radius_blocker_rich_extension_product_sweep.py",
            "command": (
                "python scripts/check_n9_radius_blocker_rich_extension_product_sweep.py "
                "--write --assert-expected"
            ),
            "sources": [
                "data/certificates/n9_radius_blocker_shape_sweep.json",
                "scripts/check_n9_radius_blocker_rich_quotient_sweep.py",
                "scripts/check_n9_radius_blocker_rich_extension_neighborhood.py",
                "scripts/check_n9_radius_blocker_rich_extension_product_pilot.py",
                "src/erdos97/adaptive_blockers.py",
                "src/erdos97/vertex_circle_quotient_replay.py",
            ],
        },
    }


def assert_expected_payload(payload: Mapping[str, object]) -> None:
    if payload.get("schema") != SCHEMA:
        raise AssertionError(f"unexpected schema: {payload.get('schema')!r}")
    if payload.get("status") != STATUS:
        raise AssertionError(f"unexpected status: {payload.get('status')!r}")
    if payload.get("debug_limits") != {
        "max_packets": None,
        "max_variants_per_packet": None,
    }:
        raise AssertionError("expected payload must not use debug limits")
    summary = payload.get("summary")
    if not isinstance(summary, Mapping):
        raise AssertionError("summary is missing")
    for key, expected in EXPECTED_SUMMARY.items():
        if summary.get(key) != expected:
            raise AssertionError(
                f"summary[{key!r}] is {summary.get(key)!r}, expected {expected!r}"
            )
    source_packets = payload.get("source_packets")
    if not isinstance(source_packets, list):
        raise AssertionError("source packet records are missing")
    if len(source_packets) != EXPECTED_SUMMARY["source_packet_count"]:
        raise AssertionError("unexpected packet count")
    packet_ids = [packet["source_packet_id"] for packet in source_packets]
    if len(packet_ids) != len(set(packet_ids)):
        raise AssertionError("source packet IDs are not unique")
    if any(packet.get("truncated") for packet in source_packets):
        raise AssertionError("expected payload must not be truncated")


def compare_artifact(payload: Mapping[str, object], path: Path) -> None:
    checked = json.loads(path.read_text(encoding="utf-8"))
    if checked != payload:
        raise AssertionError(f"checked artifact is stale: {path.relative_to(ROOT)}")


def print_summary(payload: Mapping[str, object]) -> None:
    summary = payload["summary"]
    assert isinstance(summary, Mapping)
    print("n=9 radius-blocker rich-extension product sweep")
    print(f"claim scope: {payload['claim_scope']}")
    print(f"source packets: {summary['source_packet_count']}")
    print(f"variants: {summary['variant_count']}")
    print(f"quotient statuses: {summary['quotient_status_counts']}")
    print(f"self-edge conflicts: {summary['total_self_edge_conflict_count']}")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--write", action="store_true", help="write the artifact")
    parser.add_argument("--check", action="store_true", help="compare artifact")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true", help="print full JSON")
    parser.add_argument(
        "--max-packets",
        type=int,
        default=None,
        help="debug/testing packet limit; do not use for checked artifacts",
    )
    parser.add_argument(
        "--max-variants-per-packet",
        type=int,
        default=None,
        help="debug/testing per-packet limit; do not use for checked artifacts",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    payload = build_payload(
        args.source,
        max_packets=args.max_packets,
        max_variants_per_packet=args.max_variants_per_packet,
    )
    if args.assert_expected:
        assert_expected_payload(payload)
    if args.check:
        compare_artifact(payload, args.out)
    if args.write:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_summary(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
