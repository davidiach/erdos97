#!/usr/bin/env python3
"""Check a bounded rich-extension neighborhood for n=9 blocker packets.

This is a finite bridge diagnostic only. It proves no general theorem about
Erdos Problem #97 and supplies no counterexample.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]

from check_n9_radius_blocker_rich_quotient_sweep import (  # noqa: E402
    DEFAULT_SOURCE,
    N,
    ORDER,
    choose_extra_label,
    counter_to_json,
    extra_label_candidates,
    load_shape_sweep,
    sha256_file,
    source_examples,
)
from erdos97.adaptive_blockers import is_radius_blocker  # noqa: E402
from erdos97.radius_blocker_packets import TRUST  # noqa: E402
from erdos97.vertex_circle_quotient_replay import (  # noqa: E402
    RichClassRow,
    replay_vertex_circle_rich_quotient,
)

SCHEMA = "erdos97.n9_radius_blocker_rich_extension_neighborhood.v1"
STATUS = "N9_RADIUS_BLOCKER_RICH_EXTENSION_NEIGHBORHOOD_ONLY"
DEFAULT_OUT = (
    ROOT
    / "data"
    / "certificates"
    / "n9_radius_blocker_rich_extension_neighborhood.json"
)
NEIGHBORHOOD_RADIUS = 2
EXPECTED_SUMMARY = {
    "n": 9,
    "source_shape_count": 10,
    "source_packet_count": 20,
    "neighborhood_radius": 2,
    "variant_count": 5996,
    "source_status_counts": {"self_edge": 10, "strict_cycle": 10},
    "source_variant_count_counts": {"280": 8, "303": 7, "327": 5},
    "hamming_distance_counts": {"0": 20, "1": 497, "2": 5479},
    "source_row_alternative_count_profile": {"2": 43, "3": 137},
    "variant_rich_class_count_total": 53964,
    "max_rich_class_size": 5,
    "all_variants_radius_blockers": True,
    "quotient_status_counts": {"self_edge": 5996},
    "all_variants_obstructed": True,
    "total_strict_edge_count": 1349100,
    "total_self_edge_conflict_count": 1017368,
    "min_self_edge_conflict_count": 82,
    "max_self_edge_conflict_count": 221,
    "first_self_edge_row_counts": {"0": 5996},
    "variant_max_blocker_intersection_size_counts": {
        "2": 128,
        "3": 1559,
        "4": 4309,
    },
}


def rich_classes_for_blocker(
    rows: Sequence[RichClassRow],
) -> tuple[tuple[tuple[int, ...], ...], ...]:
    return tuple((row.witnesses,) for row in rows)


def extension_catalog(
    selected_rows: Sequence[Sequence[int]],
    blocker: Sequence[int],
) -> tuple[list[int], list[list[int]], list[dict[str, object]]]:
    baseline: list[int] = []
    alternatives: list[list[int]] = []
    records: list[dict[str, object]] = []
    blocker_set = set(int(label) for label in blocker)
    for center, row in enumerate(selected_rows):
        row_list = [int(label) for label in row]
        candidates = extra_label_candidates(center, row_list, blocker)
        baseline_label = choose_extra_label(center, row_list, blocker)
        alternative_labels = [label for label in candidates if label != baseline_label]
        baseline.append(baseline_label)
        alternatives.append(alternative_labels)
        baseline_class = tuple(sorted(set(row_list) | {baseline_label}))
        records.append(
            {
                "center": center,
                "source_exact_row": row_list,
                "candidate_added_labels": candidates,
                "baseline_added_label": baseline_label,
                "alternative_added_labels": alternative_labels,
                "baseline_rich_class": list(baseline_class),
                "baseline_blocker_intersection_size": len(
                    set(baseline_class) & blocker_set
                ),
                "inside_blocker_center": center in blocker_set,
            }
        )
    return baseline, alternatives, records


def iter_added_label_variants(
    baseline: Sequence[int],
    alternatives: Sequence[Sequence[int]],
    radius: int = NEIGHBORHOOD_RADIUS,
) -> Iterable[tuple[int, tuple[int, ...], tuple[int, ...]]]:
    """Yield baseline plus all one- and two-row extension changes."""

    baseline_tuple = tuple(int(label) for label in baseline)
    yield 0, (), baseline_tuple
    if radius < 1:
        return
    for center, labels in enumerate(alternatives):
        for label in labels:
            variant = list(baseline_tuple)
            variant[center] = int(label)
            yield 1, (center,), tuple(variant)
    if radius < 2:
        return
    for left, right in combinations(range(N), 2):
        for left_label in alternatives[left]:
            for right_label in alternatives[right]:
                variant = list(baseline_tuple)
                variant[left] = int(left_label)
                variant[right] = int(right_label)
                yield 2, (left, right), tuple(variant)


def rich_rows_from_added_labels(
    selected_rows: Sequence[Sequence[int]],
    added_labels: Sequence[int],
) -> list[RichClassRow]:
    rich_rows: list[RichClassRow] = []
    for center, row in enumerate(selected_rows):
        row_set = set(int(label) for label in row)
        row_set.add(int(added_labels[center]))
        rich_rows.append(RichClassRow(center=center, witnesses=tuple(sorted(row_set))))
    return rich_rows


def build_source_packet_record(source: Mapping[str, object]) -> dict[str, object]:
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
    for distance, _changed_centers, added_labels in iter_added_label_variants(
        baseline, alternatives
    ):
        if added_labels in seen_variants:
            raise AssertionError("duplicate extension-neighborhood variant")
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

    return {
        "source_packet_id": (
            f"{source['case_name']}:{source['source_status']}:"
            f"{source['source_example_index']}"
        ),
        "case_index": source["case_index"],
        "case_name": source["case_name"],
        "blocker": blocker,
        "source_status": source["source_status"],
        "source_example_index": source["source_example_index"],
        "source_selected_rows": rows,
        "row_extension_catalog": catalog_records,
        "alternative_count_profile": counter_to_json(
            Counter(len(labels) for labels in alternatives)
        ),
        "variant_count": variant_count,
        "hamming_distance_counts": counter_to_json(hamming_distance_counts),
        "all_variants_radius_blockers": all_radius_blockers,
        "quotient_status_counts": counter_to_json(quotient_status_counts),
        "all_variants_obstructed": quotient_status_counts.get("ok", 0) == 0,
        "total_strict_edge_count": total_strict_edges,
        "total_self_edge_conflict_count": sum(self_edge_counts),
        "min_self_edge_conflict_count": min(self_edge_counts),
        "max_self_edge_conflict_count": max(self_edge_counts),
        "first_self_edge_row_counts": counter_to_json(first_self_edge_rows),
        "variant_max_blocker_intersection_size_counts": counter_to_json(
            max_blocker_intersections
        ),
        "max_rich_class_size": max_rich_class_size,
    }


def build_summary(
    records: Sequence[Mapping[str, object]],
    source_shape_count: int,
) -> dict[str, object]:
    source_status_counts: Counter[str] = Counter()
    source_variant_count_counts: Counter[int] = Counter()
    hamming_distance_counts: Counter[str] = Counter()
    alternative_count_profile: Counter[str] = Counter()
    quotient_status_counts: Counter[str] = Counter()
    first_self_edge_rows: Counter[str] = Counter()
    max_blocker_intersections: Counter[str] = Counter()
    variant_count = 0
    strict_edge_count = 0
    self_edge_total = 0
    self_edge_min: int | None = None
    self_edge_max = 0
    max_rich_class_size = 0

    for record in records:
        source_status_counts[str(record["source_status"])] += 1
        record_variant_count = int(record["variant_count"])
        source_variant_count_counts[record_variant_count] += 1
        variant_count += record_variant_count
        strict_edge_count += int(record["total_strict_edge_count"])
        self_edge_total += int(record["total_self_edge_conflict_count"])
        record_min = int(record["min_self_edge_conflict_count"])
        record_max = int(record["max_self_edge_conflict_count"])
        self_edge_min = record_min if self_edge_min is None else min(self_edge_min, record_min)
        self_edge_max = max(self_edge_max, record_max)
        max_rich_class_size = max(max_rich_class_size, int(record["max_rich_class_size"]))
        for key, value in record["hamming_distance_counts"].items():
            hamming_distance_counts[str(key)] += int(value)
        for key, value in record["alternative_count_profile"].items():
            alternative_count_profile[str(key)] += int(value)
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
        "source_packet_count": len(records),
        "neighborhood_radius": NEIGHBORHOOD_RADIUS,
        "variant_count": variant_count,
        "source_status_counts": counter_to_json(source_status_counts),
        "source_variant_count_counts": counter_to_json(source_variant_count_counts),
        "hamming_distance_counts": counter_to_json(hamming_distance_counts),
        "source_row_alternative_count_profile": counter_to_json(
            alternative_count_profile
        ),
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


def build_payload(source: Path = DEFAULT_SOURCE) -> dict[str, object]:
    shape_sweep = load_shape_sweep(source)
    sources = source_examples(shape_sweep)
    records = [build_source_packet_record(source_record) for source_record in sources]
    cases = shape_sweep.get("cases")
    if not isinstance(cases, list):
        raise AssertionError("shape sweep artifact has no cases list")

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": (
            "Bounded n=9 rich-extension neighborhood replay. Starting from "
            "the 20 stored shape-sweep obstruction examples, it builds the "
            "baseline synthetic size-five rich classes and replays every "
            "radius-blocker-preserving one-row or two-row added-label change. "
            "This is finite catalogue evidence only: it is not an n=9 proof, "
            "not a proof of the adaptive blocker bridge, and not a "
            "counterexample."
        ),
        "summary": build_summary(records, len(cases)),
        "source_shape_sweep": {
            "path": source.relative_to(ROOT).as_posix(),
            "schema": shape_sweep.get("schema"),
            "status": shape_sweep.get("status"),
            "trust": shape_sweep.get("trust"),
            "sha256": sha256_file(source),
            "summary": shape_sweep.get("summary"),
        },
        "neighborhood_rule": {
            "baseline": (
                "Use the deterministic baseline added label from the generated "
                "rich-class quotient sweep for each exact-four source row."
            ),
            "catalogue": (
                "For each row, enumerate every extra label that preserves the "
                "actual radius-blocker condition: inside-blocker centers must "
                "stay below three blocker vertices, while outside-blocker "
                "centers are unconstrained by blocker intersection."
            ),
            "variants": (
                "Replay the baseline and every Hamming-distance 1 or 2 "
                "replacement of baseline added labels by alternative catalogue "
                "labels. This is not the full Cartesian product of all row "
                "extension choices."
            ),
        },
        "source_packets": records,
        "interpretation_warnings": [
            "This checks only a Hamming-distance <= 2 extension neighborhood.",
            "It does not enumerate the full Cartesian product of size-five extensions.",
            "It does not enumerate arbitrary rich-class catalogues.",
            "It does not prove the adaptive radius-blocker bridge.",
            "No general proof and no counterexample are claimed.",
        ],
        "provenance": {
            "generator": "scripts/check_n9_radius_blocker_rich_extension_neighborhood.py",
            "command": (
                "python scripts/check_n9_radius_blocker_rich_extension_neighborhood.py "
                "--write --assert-expected"
            ),
            "sources": [
                "data/certificates/n9_radius_blocker_shape_sweep.json",
                "scripts/check_n9_radius_blocker_rich_quotient_sweep.py",
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
    source_packets = payload.get("source_packets")
    if not isinstance(source_packets, list):
        raise AssertionError("source packet records are missing")
    packet_ids = [packet["source_packet_id"] for packet in source_packets]
    if len(packet_ids) != len(set(packet_ids)):
        raise AssertionError("source packet IDs are not unique")


def compare_artifact(payload: Mapping[str, object], path: Path) -> None:
    checked = json.loads(path.read_text(encoding="utf-8"))
    if checked != payload:
        raise AssertionError(f"checked artifact is stale: {path.relative_to(ROOT)}")


def print_summary(payload: Mapping[str, object]) -> None:
    summary = payload["summary"]
    assert isinstance(summary, Mapping)
    print("n=9 radius-blocker rich-extension neighborhood")
    print(f"claim scope: {payload['claim_scope']}")
    print(f"variants: {summary['variant_count']}")
    print(f"hamming distances: {summary['hamming_distance_counts']}")
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
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    payload = build_payload(args.source)
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
