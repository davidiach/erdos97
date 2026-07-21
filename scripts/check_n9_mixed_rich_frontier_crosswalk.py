#!/usr/bin/env python3
"""Crosswalk the n=9 mixed rich-support reduction to the exact-four frontier.

This is a finite support/frontier diagnostic only. It proves no general
theorem about Erdos Problem #97 and supplies no counterexample.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from erdos97.json_io import load_json  # noqa: E402
from erdos97.path_display import display_path  # noqa: E402

import check_n9_mixed_rich_support_reduction as mixed  # noqa: E402

SCHEMA = "erdos97.n9_mixed_rich_frontier_crosswalk.v1"
STATUS = "REVIEW_PENDING_MIXED_RICH_FRONTIER_CROSSWALK"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
DEFAULT_OUT = ROOT / "data" / "certificates" / "n9_mixed_rich_frontier_crosswalk.json"
DEFAULT_MIXED = ROOT / "data" / "certificates" / "n9_mixed_rich_support_reduction.json"
DEFAULT_FRONTIER = (
    ROOT
    / "data"
    / "certificates"
    / "n9_vertex_circle_frontier_motif_classification.json"
)
CLAIM_SCOPE = (
    "Crosswalk from the generator-independent n=9 mixed four/five rich-support "
    "reduction to the stored exact-four vertex-circle frontier. It reruns the "
    "mixed support search, collects the 184 all-exact-four terminal support "
    "assignments, and checks that their labelled row set is exactly the stored "
    "184 pre-vertex-circle frontier assignments. It does not prove the "
    "exact-four vertex-circle exhaustive checker, does not prove filter "
    "soundness, strict-edge geometry, selected-distance quotient soundness, "
    "n=9, Erdos Problem #97, a counterexample, or any official/global status "
    "update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_mixed_rich_frontier_crosswalk.py",
    "command": (
        "python scripts/check_n9_mixed_rich_frontier_crosswalk.py "
        "--write --assert-expected"
    ),
    "sources": [
        "data/certificates/n9_mixed_rich_support_reduction.json",
        "data/certificates/n9_vertex_circle_frontier_motif_classification.json",
        "scripts/check_n9_mixed_rich_support_reduction.py",
    ],
}

EXPECTED_SUMMARY = {
    "n": 9,
    "support_sizes": [4, 5],
    "search_nodes_visited": 108018,
    "search_dead_end_count": 58791,
    "mixed_source_assignment_count": 184,
    "collected_mixed_assignment_count": 184,
    "frontier_assignment_count": 184,
    "mixed_unique_assignment_count": 184,
    "frontier_unique_assignment_count": 184,
    "all_collected_supports_exact_four": True,
    "mixed_source_counts_match_collected": True,
    "sequence_matches": False,
    "sequence_mismatch_count": 6,
    "set_matches": True,
    "missing_from_frontier_count": 0,
    "extra_in_frontier_count": 0,
    "matched_frontier_status_counts": {"self_edge": 158, "strict_cycle": 26},
    "mixed_sequence_rows_sha256": "42df5855afd69904a94408342d6f4194cc36732ee79df67349da4c7e1b67faa2",
    "frontier_sequence_rows_sha256": "d7807b69b9de27da17fa851b3325b1e26cfa0b6d86277abeda4bc4e3454b8e01",
    "mixed_sorted_rows_sha256": "dc28b32d93e721838a592d1f010f92720869191594dbcc40df2a00f96f213d55",
    "frontier_sorted_rows_sha256": "dc28b32d93e721838a592d1f010f92720869191594dbcc40df2a00f96f213d55",
    "sequence_mismatch_positions_sample": [106, 107, 108, 109, 134, 135],
}

Rows = tuple[tuple[int, ...], ...]


@dataclass(frozen=True)
class CollectedMixedFrontier:
    rows: tuple[Rows, ...]
    nodes_visited: int
    dead_end_count: int
    center_choice_counts: Mapping[int, int]
    node_depth_counts: Mapping[int, int]


def mixed_frontier_crosswalk_payload(
    *,
    mixed_path: Path = DEFAULT_MIXED,
    frontier_path: Path = DEFAULT_FRONTIER,
) -> dict[str, Any]:
    """Return the mixed-rich-to-exact-four-frontier crosswalk payload."""

    errors: list[str] = []
    mixed_source = load_json(mixed_path)
    frontier_source = load_json(frontier_path)
    collected = collect_mixed_terminal_rows()
    stored = stored_frontier_rows(frontier_source)
    summary = crosswalk_summary(mixed_source, collected, stored)
    audit_summary(summary, errors)

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": mixed.N,
        "support_sizes": list(mixed.SUPPORT_SIZES),
        "mixed_rich_frontier_crosswalk": summary,
        "source_artifacts": {
            "mixed_support_reduction": source_metadata(mixed_path, mixed_source),
            "frontier_motif_classification": source_metadata(
                frontier_path,
                frontier_source,
            ),
        },
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "interpretation": (
            "A passed crosswalk says the 184 terminal assignments from the "
            "mixed four/five rich-support reduction are exactly the stored "
            "184 exact-four pre-vertex-circle frontier assignments as a "
            "labelled set. This is a support-to-frontier landing check only."
        ),
        "provenance": dict(PROVENANCE),
    }


def collect_mixed_terminal_rows() -> CollectedMixedFrontier:
    """Collect all terminal row systems from the mixed support search."""

    catalogue = mixed.prepare_support_catalogue(mixed.N, mixed.ORDER)
    n = len(catalogue.options)
    assigned: dict[int, int] = {}
    pair_counts = [0] * len(mixed.pair_indices(n))
    terminal_rows: list[Rows] = []
    center_choice_counts: Counter[int] = Counter()
    node_depth_counts: Counter[int] = Counter()
    nodes_visited = 0
    dead_end_count = 0

    def add_support(center: int, support_index: int) -> None:
        for pair_id in catalogue.pair_ids[center][support_index]:
            pair_counts[pair_id] += 1

    def remove_support(center: int, support_index: int) -> None:
        for pair_id in catalogue.pair_ids[center][support_index]:
            pair_counts[pair_id] -= 1

    def choose_center() -> tuple[int | None, list[int]]:
        best_center: int | None = None
        best_options: list[int] = []
        for center in range(n):
            if center in assigned:
                continue
            viable, _rejections = mixed.viable_support_indices(
                catalogue,
                assigned,
                pair_counts,
                center,
            )
            if best_center is None or len(viable) < len(best_options):
                best_center = center
                best_options = viable
            if not viable:
                break
        return best_center, best_options

    def search() -> None:
        nonlocal dead_end_count
        nonlocal nodes_visited

        depth = len(assigned)
        if depth == n:
            terminal_rows.append(
                tuple(catalogue.options[center][assigned[center]] for center in range(n))
            )
            return
        center, center_options = choose_center()
        if center is None:
            return
        if not center_options:
            dead_end_count += 1
            return

        center_choice_counts[center] += 1
        node_depth_counts[depth] += len(center_options)
        for support_index in center_options:
            nodes_visited += 1
            assigned[center] = support_index
            add_support(center, support_index)
            search()
            remove_support(center, support_index)
            del assigned[center]

    search()
    return CollectedMixedFrontier(
        rows=tuple(terminal_rows),
        nodes_visited=nodes_visited,
        dead_end_count=dead_end_count,
        center_choice_counts=dict(sorted(center_choice_counts.items())),
        node_depth_counts=dict(sorted(node_depth_counts.items())),
    )


def stored_frontier_rows(frontier_source: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return stored frontier rows and status labels."""

    assignments = frontier_source.get("assignments")
    if not isinstance(assignments, list):
        raise ValueError("frontier artifact must contain an assignments list")
    out: list[dict[str, Any]] = []
    for index, assignment in enumerate(assignments, start=1):
        if not isinstance(assignment, Mapping):
            raise ValueError(f"frontier assignment {index} is not an object")
        out.append(
            {
                "assignment_id": str(assignment.get("assignment_id", f"A{index:03d}")),
                "rows": rows_from_selected_rows(assignment.get("selected_rows")),
                "status": str(assignment.get("status")),
            }
        )
    return out


def rows_from_selected_rows(raw_rows: Any) -> Rows:
    """Return witness rows ordered by center from compact selected rows."""

    if not isinstance(raw_rows, list):
        raise ValueError("selected_rows must be a list")
    rows: list[tuple[int, ...] | None] = [None] * mixed.N
    for raw_row in raw_rows:
        if not isinstance(raw_row, list) or len(raw_row) != 5:
            raise ValueError(f"bad selected row: {raw_row!r}")
        center = int(raw_row[0])
        witnesses = tuple(int(label) for label in raw_row[1:])
        if center < 0 or center >= mixed.N:
            raise ValueError(f"bad row center: {center!r}")
        if len(witnesses) != 4 or len(set(witnesses)) != 4 or center in witnesses:
            raise ValueError(f"bad witness row for center {center}: {witnesses!r}")
        rows[center] = witnesses
    if any(row is None for row in rows):
        raise ValueError("stored assignment does not cover every center")
    return tuple(row for row in rows if row is not None)


def crosswalk_summary(
    mixed_source: Mapping[str, Any],
    collected: CollectedMixedFrontier,
    stored: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Return the stable crosswalk summary."""

    mixed_rows = list(collected.rows)
    frontier_rows = [record["rows"] for record in stored]
    mixed_set = set(mixed_rows)
    frontier_set = set(frontier_rows)
    missing = sorted(mixed_set - frontier_set)
    extra = sorted(frontier_set - mixed_set)
    sequence_mismatches = [
        index
        for index, (left, right) in enumerate(zip(mixed_rows, frontier_rows), start=1)
        if left != right
    ]
    status_by_rows = {record["rows"]: str(record["status"]) for record in stored}
    matched_status_counts = Counter(status_by_rows[rows] for rows in mixed_set & frontier_set)
    source_summary = mixed_source.get("summary", {})
    if not isinstance(source_summary, Mapping):
        source_summary = {}

    return {
        "n": mixed.N,
        "support_sizes": list(mixed.SUPPORT_SIZES),
        "search_rule": "mixed_support_minimum_remaining_options",
        "search_nodes_visited": int(collected.nodes_visited),
        "search_dead_end_count": int(collected.dead_end_count),
        "search_center_choice_counts": mixed.counter_to_json(
            collected.center_choice_counts,
        ),
        "search_node_depth_counts": mixed.counter_to_json(collected.node_depth_counts),
        "mixed_source_assignment_count": source_summary.get(
            "search_complete_assignments",
        ),
        "collected_mixed_assignment_count": len(mixed_rows),
        "frontier_assignment_count": len(frontier_rows),
        "mixed_unique_assignment_count": len(mixed_set),
        "frontier_unique_assignment_count": len(frontier_set),
        "all_collected_supports_exact_four": all(
            len(row) == 4 for rows in mixed_rows for row in rows
        ),
        "mixed_source_counts_match_collected": (
            source_summary.get("search_complete_assignments") == len(mixed_rows)
            and source_summary.get("search_nodes_visited") == collected.nodes_visited
            and source_summary.get("search_dead_end_count") == collected.dead_end_count
        ),
        "sequence_matches": mixed_rows == frontier_rows,
        "sequence_mismatch_count": len(sequence_mismatches),
        "set_matches": mixed_set == frontier_set,
        "missing_from_frontier_count": len(missing),
        "extra_in_frontier_count": len(extra),
        "matched_frontier_status_counts": dict(sorted(matched_status_counts.items())),
        "mixed_sequence_rows_sha256": rows_digest(mixed_rows),
        "frontier_sequence_rows_sha256": rows_digest(frontier_rows),
        "mixed_sorted_rows_sha256": rows_digest(sorted(mixed_rows)),
        "frontier_sorted_rows_sha256": rows_digest(sorted(frontier_rows)),
        "sequence_mismatch_positions_sample": sequence_mismatches[:10],
        "example_mismatches": example_mismatches(missing, extra),
    }


def rows_digest(rows_list: Sequence[Rows]) -> str:
    """Return the stable digest convention used by frontier crosswalks."""

    payload = [[list(row) for row in rows] for rows in rows_list]
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def example_mismatches(
    missing: Sequence[Rows],
    extra: Sequence[Rows],
) -> list[dict[str, Any]]:
    """Return a small mismatch sample for failed crosswalks."""

    examples: list[dict[str, Any]] = []
    for kind, rows_list in (
        ("missing_from_frontier", missing),
        ("extra_in_frontier", extra),
    ):
        for rows in rows_list[:3]:
            examples.append({"kind": kind, "rows": [list(row) for row in rows]})
    return examples


def audit_summary(summary: Mapping[str, Any], errors: list[str]) -> None:
    """Collect validation errors from the crosswalk summary."""

    for key, expected in EXPECTED_SUMMARY.items():
        if summary.get(key) != expected:
            errors.append(f"{key}: {summary.get(key)!r} != {expected!r}")
    if summary.get("example_mismatches") != []:
        errors.append(f"unexpected mismatch examples: {summary.get('example_mismatches')!r}")


def assert_expected_payload(payload: Mapping[str, Any]) -> None:
    """Assert the expected mixed-rich-to-frontier crosswalk."""

    if payload.get("schema") != SCHEMA:
        raise AssertionError(f"schema mismatch: {payload.get('schema')!r}")
    if payload.get("status") != STATUS:
        raise AssertionError(f"status mismatch: {payload.get('status')!r}")
    if payload.get("trust") != TRUST:
        raise AssertionError(f"trust mismatch: {payload.get('trust')!r}")
    if payload.get("provenance") != PROVENANCE:
        raise AssertionError(f"provenance mismatch: {payload.get('provenance')!r}")
    if payload.get("claim_scope") != CLAIM_SCOPE:
        raise AssertionError(f"claim_scope mismatch: {payload.get('claim_scope')!r}")
    claim_scope = CLAIM_SCOPE
    for required in (
        "does not prove the exact-four vertex-circle exhaustive checker",
        "does not prove filter soundness",
        "strict-edge geometry",
        "selected-distance quotient soundness",
        "n=9",
        "Erdos Problem #97",
        "counterexample",
        "official/global status update",
    ):
        if required not in claim_scope:
            raise AssertionError(f"claim_scope missing {required!r}")
    if payload.get("validation_status") != "passed":
        raise AssertionError(f"validation errors: {payload.get('validation_errors')!r}")
    summary = payload.get("mixed_rich_frontier_crosswalk")
    if not isinstance(summary, Mapping):
        raise AssertionError("mixed_rich_frontier_crosswalk missing")
    for key, expected in EXPECTED_SUMMARY.items():
        if summary.get(key) != expected:
            raise AssertionError(f"{key} mismatch: {summary.get(key)!r} != {expected!r}")
    if summary.get("example_mismatches") != []:
        raise AssertionError(f"unexpected mismatch examples: {summary['example_mismatches']!r}")


def source_metadata(path: Path, payload: Mapping[str, Any]) -> dict[str, Any]:
    """Return compact metadata for a source artifact."""

    return {
        "path": display_path(path, ROOT),
        "schema": payload.get("schema"),
        "type": payload.get("type"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
    }


def compare_artifact(payload: Mapping[str, Any], path: Path) -> None:
    checked = load_json(path)
    if checked != payload:
        raise AssertionError(f"checked artifact is stale: {display_path(path, ROOT)}")


def print_summary(payload: Mapping[str, Any]) -> None:
    summary = payload["mixed_rich_frontier_crosswalk"]
    assert isinstance(summary, Mapping)
    print("n=9 mixed rich-support to frontier crosswalk")
    print(f"claim scope: {payload['claim_scope']}")
    print(f"mixed terminals: {summary['collected_mixed_assignment_count']}")
    print(f"frontier assignments: {summary['frontier_assignment_count']}")
    print(f"set matches: {summary['set_matches']}")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--mixed", type=Path, default=DEFAULT_MIXED)
    parser.add_argument("--frontier", type=Path, default=DEFAULT_FRONTIER)
    parser.add_argument("--write", action="store_true", help="write the artifact")
    parser.add_argument("--check", action="store_true", help="compare artifact")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true", help="print full JSON")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    payload = mixed_frontier_crosswalk_payload(
        mixed_path=args.mixed,
        frontier_path=args.frontier,
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
