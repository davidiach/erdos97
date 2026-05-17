#!/usr/bin/env python3
"""Check a bounded n=9 radius-blocker richer-class projection pilot.

This is a finite bridge diagnostic only. It proves no general theorem about
Erdos Problem #97 and supplies no counterexample.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.radius_blocker_packets import (  # noqa: E402
    TRUST,
    PacketConfig,
    analyze_radius_blocker_projection_packet,
    exact_four_rich_classes_from_rows,
    four_subset_options_from_rich_classes,
    result_to_packet_json,
)

SCHEMA = "erdos97.n9_radius_blocker_rich_projection_pilot.v1"
STATUS = "N9_RADIUS_BLOCKER_RICH_PROJECTION_PILOT_ONLY"
DEFAULT_SHAPE_SWEEP = (
    ROOT / "data" / "certificates" / "n9_radius_blocker_shape_sweep.json"
)
DEFAULT_OUT = (
    ROOT / "data" / "certificates" / "n9_radius_blocker_rich_projection_pilot.json"
)
N = 9
ORDER = list(range(N))
SOURCE_BLOCKER = (0, 1, 2, 3)
EXPECTED_SUMMARY = {
    "n": 9,
    "blocker": [0, 1, 2, 3],
    "expanded_center_count": 9,
    "max_rich_class_size": 5,
    "projected_row_option_counts": [5, 5, 5, 5, 5, 5, 5, 5, 5],
    "projected_raw_selection_upper_bound": 1_953_125,
    "radius_blocker_ok": True,
    "all_projected_incidence_survivors_obstructed": True,
    "nodes_visited": 20,
    "incidence_survivors": 1,
    "vertex_circle_status_counts": {"self_edge": 1},
    "rejection_counts": {
        "column_pair_cap": 13,
        "row_pair_cap": 68,
        "two_overlap_crossing": 137,
    },
}
EXPECTED_EXPANSIONS = [
    {
        "center": 0,
        "source_exact_row": [1, 2, 4, 6],
        "added_label": 5,
        "rich_class": [1, 2, 4, 5, 6],
    },
    {
        "center": 1,
        "source_exact_row": [2, 5, 7, 8],
        "added_label": 0,
        "rich_class": [0, 2, 5, 7, 8],
    },
    {
        "center": 2,
        "source_exact_row": [1, 3, 4, 8],
        "added_label": 5,
        "rich_class": [1, 3, 4, 5, 8],
    },
    {
        "center": 3,
        "source_exact_row": [0, 2, 4, 7],
        "added_label": 5,
        "rich_class": [0, 2, 4, 5, 7],
    },
    {
        "center": 4,
        "source_exact_row": [0, 1, 5, 6],
        "added_label": 7,
        "rich_class": [0, 1, 5, 6, 7],
    },
    {
        "center": 5,
        "source_exact_row": [2, 3, 6, 8],
        "added_label": 4,
        "rich_class": [2, 3, 4, 6, 8],
    },
    {
        "center": 6,
        "source_exact_row": [1, 3, 5, 7],
        "added_label": 4,
        "rich_class": [1, 3, 4, 5, 7],
    },
    {
        "center": 7,
        "source_exact_row": [0, 4, 5, 8],
        "added_label": 1,
        "rich_class": [0, 1, 4, 5, 8],
    },
    {
        "center": 8,
        "source_exact_row": [0, 3, 6, 7],
        "added_label": 4,
        "rich_class": [0, 3, 4, 6, 7],
    },
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_shape_sweep(path: Path) -> Mapping[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise AssertionError("shape sweep artifact is not an object")
    return payload


def source_case(payload: Mapping[str, object]) -> Mapping[str, object]:
    cases = payload.get("cases")
    if not isinstance(cases, list):
        raise AssertionError("shape sweep artifact has no cases list")
    for case in cases:
        if not isinstance(case, Mapping):
            raise AssertionError(f"shape sweep case is not an object: {case!r}")
        if tuple(int(label) for label in case["blocker"]) == SOURCE_BLOCKER:
            return case
    raise AssertionError(f"missing source blocker case: {SOURCE_BLOCKER}")


def source_selected_rows(case: Mapping[str, object]) -> list[list[int]]:
    examples = case.get("obstruction_examples")
    if not isinstance(examples, Mapping):
        raise AssertionError("source case has no obstruction examples")
    self_edge_examples = examples.get("self_edge")
    if not isinstance(self_edge_examples, list) or not self_edge_examples:
        raise AssertionError("source case has no self-edge example")
    first = self_edge_examples[0]
    if not isinstance(first, Mapping):
        raise AssertionError("source self-edge example is not an object")
    rows = first.get("selected_rows")
    if not isinstance(rows, list):
        raise AssertionError("source self-edge example has no selected rows")
    return [[int(label) for label in row] for row in rows]


def safe_extra_label(center: int, row: Sequence[int], blocker: Sequence[int]) -> int:
    row_set = set(int(label) for label in row)
    blocker_set = set(int(label) for label in blocker)
    for label in range(N):
        if label == center or label in row_set:
            continue
        if len((row_set | {label}) & blocker_set) <= 2:
            return label
    raise AssertionError(f"no safe size-five extension for center {center}")


def build_projected_rich_classes(
    rows: Sequence[Sequence[int]],
    blocker: Sequence[int],
) -> tuple[tuple[tuple[int, ...], ...], ...]:
    rich_classes = [list(classes) for classes in exact_four_rich_classes_from_rows(rows)]
    for center, row in enumerate(rows):
        extra = safe_extra_label(center, row, blocker)
        rich_classes[center] = (tuple(sorted(set(row) | {extra})),)
    return tuple(tuple(classes) for classes in rich_classes)


def expansion_records(
    rows: Sequence[Sequence[int]],
    rich_classes: Sequence[Sequence[Sequence[int]]],
    blocker: Sequence[int],
) -> list[dict[str, object]]:
    options = four_subset_options_from_rich_classes(rich_classes)
    records: list[dict[str, object]] = []
    for center, row in enumerate(rows):
        rich_class = list(rich_classes[center][0])
        records.append(
            {
                "center": center,
                "source_exact_row": [int(label) for label in row],
                "added_label": safe_extra_label(center, row, blocker),
                "rich_class": rich_class,
                "projected_four_rows": [list(option) for option in options[center]],
            }
        )
    return records


def build_payload(shape_sweep_path: Path = DEFAULT_SHAPE_SWEEP) -> dict[str, object]:
    """Build the deterministic richer-class projection pilot payload."""

    source = load_shape_sweep(shape_sweep_path)
    case = source_case(source)
    rows = source_selected_rows(case)
    rich_classes = build_projected_rich_classes(rows, SOURCE_BLOCKER)
    result = analyze_radius_blocker_projection_packet(
        "n9_radius_blocker_size_five_projection_pilot_U0123_natural_order",
        rich_classes,
        SOURCE_BLOCKER,
        ORDER,
        PacketConfig(
            max_nodes=100_000,
            max_survivor_examples=1,
            max_obstruction_examples_per_status=1,
        ),
    )

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": (
            "Bounded n=9 radius-blocker projection pilot. Each center has "
            "one synthetic size-five rich class obtained from a checked "
            "exact-four obstructed source row by adding one label while "
            "preserving blocker compatibility. The replay expands each "
            "larger class to its exact four-subsets and checks only the "
            "projected selected-row packet; this is not a proof of n=9, not "
            "a proof of the adaptive blocker bridge, and not a counterexample."
        ),
        "summary": {
            "n": N,
            "order": ORDER,
            "blocker": list(SOURCE_BLOCKER),
            "expanded_center_count": len(rich_classes),
            "max_rich_class_size": max(
                len(rich_class)
                for center_classes in rich_classes
                for rich_class in center_classes
            ),
            "projected_row_option_counts": list(result.row_option_counts),
            "projected_raw_selection_upper_bound": result.raw_selection_upper_bound,
            "radius_blocker_ok": result.radius_blocker_ok,
            "all_projected_incidence_survivors_obstructed": (
                result.all_incidence_survivors_obstructed
            ),
            "nodes_visited": result.nodes_visited,
            "incidence_survivors": result.incidence_survivors,
            "vertex_circle_status_counts": dict(result.vertex_circle_status_counts),
            "rejection_counts": dict(result.rejection_counts),
        },
        "source_shape_sweep": {
            "path": shape_sweep_path.relative_to(ROOT).as_posix(),
            "schema": source.get("schema"),
            "status": source.get("status"),
            "trust": source.get("trust"),
            "sha256": sha256_file(shape_sweep_path),
            "source_blocker": list(SOURCE_BLOCKER),
            "source_case_name": case.get("name"),
            "source_case_vertex_circle_status_counts": dict(
                case["vertex_circle_status_counts"]
            ),
        },
        "source_selected_rows": rows,
        "projected_rich_classes": [
            [list(rich_class) for rich_class in center_classes]
            for center_classes in rich_classes
        ],
        "expanded_centers": expansion_records(rows, rich_classes, SOURCE_BLOCKER),
        "projection_rule": {
            "rule": (
                "Each rich class contributes every exact four-subset as a "
                "candidate selected row for the existing finite packet replay."
            ),
            "forgetful_boundary": (
                "The projection forgets equality constraints involving the "
                "vertices omitted from a chosen four-subset."
            ),
            "why_blocker_is_preserved": (
                "For centers in the blocker, the synthetic size-five class "
                "still intersects the blocker in at most two vertices."
            ),
        },
        "result": result_to_packet_json(result),
        "interpretation_warnings": [
            "This is one bounded synthetic size-five rich-class packet only.",
            "The replay checks the exact four-subset projection, not the full rich-class quotient.",
            "The result does not classify arbitrary n=9 rich-class systems.",
            "No general proof and no counterexample are claimed.",
        ],
        "provenance": {
            "generator": "scripts/check_n9_radius_blocker_rich_projection_pilot.py",
            "command": (
                "python scripts/check_n9_radius_blocker_rich_projection_pilot.py "
                "--write --assert-expected"
            ),
            "sources": [
                "data/certificates/n9_radius_blocker_shape_sweep.json",
                "src/erdos97/radius_blocker_packets.py",
                "src/erdos97/adaptive_blockers.py",
                "src/erdos97/vertex_circle_quotient_replay.py",
            ],
        },
    }


def compact_expansions(records: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "center": int(record["center"]),
            "source_exact_row": list(record["source_exact_row"]),
            "added_label": int(record["added_label"]),
            "rich_class": list(record["rich_class"]),
        }
        for record in records
    ]


def assert_expected_payload(payload: Mapping[str, object]) -> None:
    """Assert the stable richer-class projection pilot counts."""

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

    records = payload.get("expanded_centers")
    if not isinstance(records, list):
        raise AssertionError("expanded center records are missing")
    if compact_expansions(records) != EXPECTED_EXPANSIONS:
        raise AssertionError("expanded center records changed")


def compare_artifact(payload: Mapping[str, object], path: Path) -> None:
    checked = json.loads(path.read_text(encoding="utf-8"))
    if checked != payload:
        raise AssertionError(f"checked artifact is stale: {path.relative_to(ROOT)}")


def print_summary(payload: Mapping[str, object]) -> None:
    summary = payload["summary"]
    assert isinstance(summary, Mapping)
    print("n=9 radius-blocker richer-class projection pilot")
    print(f"claim scope: {payload['claim_scope']}")
    print(f"expanded centers: {summary['expanded_center_count']}")
    print(f"row option counts: {summary['projected_row_option_counts']}")
    print(f"raw projected selections: {summary['projected_raw_selection_upper_bound']}")
    print(f"nodes visited: {summary['nodes_visited']}")
    print(f"incidence survivors: {summary['incidence_survivors']}")
    print(
        "all projected incidence survivors obstructed: "
        f"{summary['all_projected_incidence_survivors_obstructed']}"
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SHAPE_SWEEP)
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
