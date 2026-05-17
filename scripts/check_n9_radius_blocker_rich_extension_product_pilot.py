#!/usr/bin/env python3
"""Check a full rich-extension product for one n=9 blocker packet.

This is a finite bridge diagnostic only. It proves no general theorem about
Erdos Problem #97 and supplies no counterexample.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from itertools import product
from pathlib import Path
from typing import Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from check_n9_radius_blocker_rich_extension_neighborhood import (  # noqa: E402
    extension_catalog,
    rich_classes_for_blocker,
    rich_rows_from_added_labels,
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

SCHEMA = "erdos97.n9_radius_blocker_rich_extension_product_pilot.v1"
STATUS = "N9_RADIUS_BLOCKER_RICH_EXTENSION_PRODUCT_PILOT_ONLY"
DEFAULT_OUT = (
    ROOT
    / "data"
    / "certificates"
    / "n9_radius_blocker_rich_extension_product_pilot.json"
)
SELECTION_RULE = "first_maximum_full_extension_product_in_source_order"
EXPECTED_SUMMARY = {
    "n": 9,
    "source_shape_count": 10,
    "source_packet_count": 20,
    "source_product_variant_count_total": 2899968,
    "source_product_variant_count_counts": {
        "110592": 8,
        "147456": 7,
        "196608": 5,
    },
    "selected_packet_id": (
        "n9_full_exact_four_radius_blocker_shape_U0135_natural_order:"
        "self_edge:0"
    ),
    "selected_case_index": 4,
    "selected_case_name": "n9_full_exact_four_radius_blocker_shape_U0135_natural_order",
    "selected_source_status": "self_edge",
    "selected_product_variant_count": 196608,
    "selected_row_option_count_profile": {"3": 1, "4": 8},
    "selected_row_alternative_count_profile": {"2": 1, "3": 8},
    "variant_count": 196608,
    "hamming_distance_counts": {
        "0": 1,
        "1": 26,
        "2": 300,
        "3": 2016,
        "4": 8694,
        "5": 24948,
        "6": 47628,
        "7": 58320,
        "8": 41553,
        "9": 13122,
    },
    "variant_rich_class_count_total": 1769472,
    "max_rich_class_size": 5,
    "all_variants_radius_blockers": True,
    "quotient_status_counts": {"self_edge": 196608},
    "all_variants_obstructed": True,
    "total_strict_edge_count": 44236800,
    "total_self_edge_conflict_count": 33895908,
    "min_self_edge_conflict_count": 69,
    "max_self_edge_conflict_count": 225,
    "first_self_edge_row_counts": {"0": 196608},
    "variant_max_blocker_intersection_size_counts": {"3": 110592, "4": 86016},
}


def packet_id(source: Mapping[str, object]) -> str:
    return (
        f"{source['case_name']}:{source['source_status']}:"
        f"{source['source_example_index']}"
    )


def option_lists(
    baseline: Sequence[int],
    alternatives: Sequence[Sequence[int]],
) -> list[tuple[int, ...]]:
    return [
        (int(base), *(int(label) for label in labels))
        for base, labels in zip(baseline, alternatives, strict=True)
    ]


def product_variant_count(options: Sequence[Sequence[int]]) -> int:
    return math.prod(len(option) for option in options)


def iter_full_product_added_label_variants(
    baseline: Sequence[int],
    alternatives: Sequence[Sequence[int]],
) -> Iterable[tuple[int, tuple[int, ...]]]:
    """Yield every full-product added-label variant and baseline distance."""

    baseline_tuple = tuple(int(label) for label in baseline)
    for added_labels in product(*option_lists(baseline, alternatives)):
        added_tuple = tuple(int(label) for label in added_labels)
        distance = sum(
            1
            for base_label, added_label in zip(
                baseline_tuple, added_tuple, strict=True
            )
            if base_label != added_label
        )
        yield distance, added_tuple


def source_product_records(
    sources: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for index, source in enumerate(sources):
        selected_rows = source["source_selected_rows"]
        if not isinstance(selected_rows, list):
            raise AssertionError("source selected rows are missing")
        baseline, alternatives, _catalog_records = extension_catalog(
            selected_rows, source["blocker"]
        )
        options = option_lists(baseline, alternatives)
        records.append(
            {
                "source_order_index": index,
                "source_packet_id": packet_id(source),
                "case_index": int(source["case_index"]),
                "case_name": str(source["case_name"]),
                "source_status": str(source["source_status"]),
                "source_example_index": int(source["source_example_index"]),
                "blocker": [int(label) for label in source["blocker"]],
                "row_option_counts": [len(option) for option in options],
                "row_alternative_counts": [len(labels) for labels in alternatives],
                "product_variant_count": product_variant_count(options),
            }
        )
    return records


def select_source_record(
    sources: Sequence[Mapping[str, object]],
) -> tuple[Mapping[str, object], dict[str, object]]:
    product_records = source_product_records(sources)
    selected_product = max(
        int(record["product_variant_count"]) for record in product_records
    )
    selected_record = next(
        record
        for record in product_records
        if int(record["product_variant_count"]) == selected_product
    )
    return sources[int(selected_record["source_order_index"])], selected_record


def build_source_product_summary(
    product_records: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    variant_counts: Counter[int] = Counter()
    total = 0
    for record in product_records:
        count = int(record["product_variant_count"])
        variant_counts[count] += 1
        total += count
    return {
        "source_product_variant_count_total": total,
        "source_product_variant_count_counts": counter_to_json(variant_counts),
        "source_product_records": list(product_records),
    }


def build_selected_packet_record(
    source: Mapping[str, object],
    product_record: Mapping[str, object],
    *,
    max_variants: int | None = None,
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
        if max_variants is not None and variant_count >= max_variants:
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
        "selection_rule": SELECTION_RULE,
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
        "truncated": max_variants is not None
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
    product_records: Sequence[Mapping[str, object]],
    selected_packet: Mapping[str, object],
    source_shape_count: int,
) -> dict[str, object]:
    source_product_summary = build_source_product_summary(product_records)
    row_option_profile = Counter(int(count) for count in selected_packet["row_option_counts"])
    row_alternative_profile = Counter(
        int(count) for count in selected_packet["row_alternative_counts"]
    )
    return {
        "n": N,
        "order": ORDER,
        "source_shape_count": source_shape_count,
        "source_packet_count": len(product_records),
        "source_product_variant_count_total": source_product_summary[
            "source_product_variant_count_total"
        ],
        "source_product_variant_count_counts": source_product_summary[
            "source_product_variant_count_counts"
        ],
        "selected_packet_id": selected_packet["source_packet_id"],
        "selected_case_index": selected_packet["case_index"],
        "selected_case_name": selected_packet["case_name"],
        "selected_source_status": selected_packet["source_status"],
        "selected_product_variant_count": selected_packet["product_variant_count"],
        "selected_row_option_count_profile": counter_to_json(row_option_profile),
        "selected_row_alternative_count_profile": counter_to_json(
            row_alternative_profile
        ),
        "variant_count": selected_packet["replayed_variant_count"],
        "hamming_distance_counts": selected_packet["hamming_distance_counts"],
        "variant_rich_class_count_total": selected_packet["replayed_variant_count"]
        * N,
        "max_rich_class_size": selected_packet["max_rich_class_size"],
        "all_variants_radius_blockers": selected_packet[
            "all_variants_radius_blockers"
        ],
        "quotient_status_counts": selected_packet["quotient_status_counts"],
        "all_variants_obstructed": selected_packet["all_variants_obstructed"],
        "total_strict_edge_count": selected_packet["total_strict_edge_count"],
        "total_self_edge_conflict_count": selected_packet[
            "total_self_edge_conflict_count"
        ],
        "min_self_edge_conflict_count": selected_packet[
            "min_self_edge_conflict_count"
        ],
        "max_self_edge_conflict_count": selected_packet[
            "max_self_edge_conflict_count"
        ],
        "first_self_edge_row_counts": selected_packet["first_self_edge_row_counts"],
        "variant_max_blocker_intersection_size_counts": selected_packet[
            "variant_max_blocker_intersection_size_counts"
        ],
    }


def build_payload(
    source: Path = DEFAULT_SOURCE,
    *,
    max_variants: int | None = None,
) -> dict[str, object]:
    shape_sweep = load_shape_sweep(source)
    sources = source_examples(shape_sweep)
    product_records = source_product_records(sources)
    selected_source, selected_product_record = select_source_record(sources)
    selected_packet = build_selected_packet_record(
        selected_source,
        selected_product_record,
        max_variants=max_variants,
    )
    cases = shape_sweep.get("cases")
    if not isinstance(cases, list):
        raise AssertionError("shape sweep artifact has no cases list")

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": (
            "One-packet n=9 full rich-extension product replay. It selects "
            "the first maximum-size source packet from the generated "
            "radius-blocker quotient-sweep packet family and replays every "
            "radius-blocker-preserving size-five added-label choice for that "
            "packet. This is finite packet evidence only: it is not an n=9 "
            "proof, not a proof of the adaptive blocker bridge, and not a "
            "counterexample."
        ),
        "summary": build_summary(product_records, selected_packet, len(cases)),
        "source_shape_sweep": {
            "path": source.relative_to(ROOT).as_posix(),
            "schema": shape_sweep.get("schema"),
            "status": shape_sweep.get("status"),
            "trust": shape_sweep.get("trust"),
            "sha256": sha256_file(source),
            "summary": shape_sweep.get("summary"),
        },
        "source_product_catalog": build_source_product_summary(product_records),
        "selection_rule": {
            "rule": SELECTION_RULE,
            "reason": (
                "The full 20-packet extension product has 2,899,968 variants. "
                "This pilot exhausts one largest product packet first, using "
                "source-artifact order as the stable tie-break."
            ),
        },
        "product_rule": {
            "catalogue": (
                "For each row, enumerate every extra label that preserves the "
                "actual radius-blocker condition: inside-blocker centers must "
                "stay below three blocker vertices, while outside-blocker "
                "centers are unconstrained by blocker intersection."
            ),
            "variants": (
                "Replay the full Cartesian product of those row extension "
                "choices for the selected source packet."
            ),
        },
        "selected_packet": selected_packet,
        "interpretation_warnings": [
            "This checks the full extension product for one selected source packet only.",
            "It does not enumerate the full product for all 20 source packets.",
            "It does not enumerate arbitrary rich-class catalogues.",
            "It does not prove the adaptive radius-blocker bridge.",
            "No general proof and no counterexample are claimed.",
        ],
        "provenance": {
            "generator": "scripts/check_n9_radius_blocker_rich_extension_product_pilot.py",
            "command": (
                "python scripts/check_n9_radius_blocker_rich_extension_product_pilot.py "
                "--write --assert-expected"
            ),
            "sources": [
                "data/certificates/n9_radius_blocker_shape_sweep.json",
                "scripts/check_n9_radius_blocker_rich_quotient_sweep.py",
                "scripts/check_n9_radius_blocker_rich_extension_neighborhood.py",
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
    summary = payload.get("summary")
    if not isinstance(summary, Mapping):
        raise AssertionError("summary is missing")
    for key, expected in EXPECTED_SUMMARY.items():
        if summary.get(key) != expected:
            raise AssertionError(
                f"summary[{key!r}] is {summary.get(key)!r}, expected {expected!r}"
            )
    selected_packet = payload.get("selected_packet")
    if not isinstance(selected_packet, Mapping):
        raise AssertionError("selected packet record is missing")
    if selected_packet.get("truncated"):
        raise AssertionError("expected payload must not be truncated")


def compare_artifact(payload: Mapping[str, object], path: Path) -> None:
    checked = json.loads(path.read_text(encoding="utf-8"))
    if checked != payload:
        raise AssertionError(f"checked artifact is stale: {path.relative_to(ROOT)}")


def print_summary(payload: Mapping[str, object]) -> None:
    summary = payload["summary"]
    assert isinstance(summary, Mapping)
    print("n=9 radius-blocker rich-extension product pilot")
    print(f"claim scope: {payload['claim_scope']}")
    print(f"selected packet: {summary['selected_packet_id']}")
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
        "--max-variants",
        type=int,
        default=None,
        help="debug/testing limit; do not use for checked artifacts",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    payload = build_payload(args.source, max_variants=args.max_variants)
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
