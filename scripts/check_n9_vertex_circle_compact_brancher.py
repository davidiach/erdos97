#!/usr/bin/env python3
"""Compact independent n=9 vertex-circle brancher.

This checker deliberately avoids importing the project n=9 brancher modules. It
regenerates the n=9 selected-witness frontier from first principles using only
row shape, the two-circle row-intersection cap, the two-overlap crossing rule,
and the witness-pair capacity rule. It then applies the row-wise vertex-circle
quotient obstruction to every terminal assignment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any, Mapping, Sequence

from erdos97.json_io import load_json

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "n9_vertex_circle_compact_brancher.json"
)

SCHEMA = "erdos97.n9_vertex_circle_compact_brancher.v1"
STATUS = "REVIEW_PENDING_COMPACT_INDEPENDENT_BRANCHER"
TRUST = "MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING"
CLAIM_SCOPE = (
    "Compact independent regeneration of the review-pending n=9 "
    "selected-witness frontier and vertex-circle quotient obstruction. It "
    "does not import the project n=9 brancher modules and does not read the "
    "stored 184-assignment frontier artifact. It is an audit/replay aid only: "
    "it does not complete independent review of the exhaustive checker, does "
    "not promote n=9 to a theorem, does not prove Erdos Problem #97, does not "
    "produce a counterexample, and does not update the official/global status."
)
PROVENANCE = {
    "generator": "scripts/check_n9_vertex_circle_compact_brancher.py",
    "command": (
        "python scripts/check_n9_vertex_circle_compact_brancher.py "
        "--write --assert-expected"
    ),
}

N = 9
ROW_SIZE = 4
PAIR_CAP = 2
EXPECTED_NODES_VISITED = 100_817
EXPECTED_FRONTIER_ASSIGNMENTS = 184
EXPECTED_OBSTRUCTION_COUNTS = {"self_edge": 158, "strict_cycle": 26}
EXPECTED_CLEAN_ASSIGNMENTS = 0
EXPECTED_ASSIGNMENT_DIGEST = (
    "dc28b32d93e721838a592d1f010f92720869191594dbcc40df2a00f96f213d55"
)
EXPECTED_CENTER_PAIR_INTERSECTION_HISTOGRAM = {"0": 72, "1": 3_168, "2": 3_384}
EXPECTED_TWO_OVERLAP_CROSSING_COUNT = 3_384
EXPECTED_WITNESS_PAIR_PROFILE_COUNTS = {"0:2|1:14|2:20": 36, "1:18|2:18": 148}
EXPECTED_SELECTED_INDEGREE_VALUE_HISTOGRAM = {"4": 1_656}

Pair = tuple[int, int]
Row = tuple[int, ...]
Assignment = dict[int, int]


def normalized_pair(left: int, right: int) -> Pair:
    """Return an unordered pair in canonical order."""

    if left < right:
        return (left, right)
    return (right, left)


def chords_cross_in_natural_order(left: Pair, right: Pair) -> bool:
    """Return whether two disjoint chords cross in cyclic order 0,1,...,8."""

    if len({left[0], left[1], right[0], right[1]}) < 4:
        return False
    a, b = sorted(left)
    c, d = sorted(right)
    return (a < c < b < d) or (c < a < d < b)


def angular_order_at_center(center: int, row: Sequence[int]) -> Row:
    """Return the linear angular order of witnesses in the vertex cone."""

    cone_order = list(range(center + 1, N)) + list(range(center))
    positions = {label: index for index, label in enumerate(cone_order)}
    return tuple(sorted(row, key=positions.__getitem__))


def row_pair_is_compatible(
    left_center: int,
    left_row: Sequence[int],
    right_center: int,
    right_row: Sequence[int],
) -> bool:
    """Check the two-circle cap and two-overlap crossing rule."""

    overlap = sorted(set(left_row) & set(right_row))
    if len(overlap) > 2:
        return False
    if len(overlap) == 2:
        center_chord = normalized_pair(left_center, right_center)
        witness_chord = normalized_pair(overlap[0], overlap[1])
        return chords_cross_in_natural_order(center_chord, witness_chord)
    return True


def candidate_rows() -> list[list[dict[str, Any]]]:
    """Build all 70 four-witness rows at each center with local data."""

    all_rows: list[list[dict[str, Any]]] = []
    for center in range(N):
        center_rows: list[dict[str, Any]] = []
        labels = [label for label in range(N) if label != center]
        for row in combinations(labels, ROW_SIZE):
            ordered = angular_order_at_center(center, row)
            equality_pairs = [normalized_pair(center, witness) for witness in row]
            witness_pairs = [
                normalized_pair(left, right) for left, right in combinations(row, 2)
            ]
            strict_edges = strict_vertex_circle_edges(ordered)
            center_rows.append(
                {
                    "row": tuple(row),
                    "angular_order": ordered,
                    "equality_pairs": tuple(equality_pairs),
                    "witness_pairs": tuple(witness_pairs),
                    "strict_edges": tuple(strict_edges),
                }
            )
        all_rows.append(center_rows)
    return all_rows


def strict_vertex_circle_edges(ordered_row: Sequence[int]) -> list[tuple[Pair, Pair]]:
    """Return nested-chord strict inequalities for one selected row.

    If selected witnesses occur in angular order a,b,c,d around the row center,
    then every chord whose witness interval strictly contains another witness
    interval is longer, since all witnesses lie on one center circle inside a
    strict convex vertex cone of angle less than pi.
    """

    strict_edges: list[tuple[Pair, Pair]] = []
    positions = range(len(ordered_row))
    for outer_left, outer_right in combinations(positions, 2):
        outer_pair = normalized_pair(
            ordered_row[outer_left],
            ordered_row[outer_right],
        )
        for inner_left, inner_right in combinations(positions, 2):
            strictly_contains = (
                outer_left <= inner_left
                and inner_right <= outer_right
                and (outer_left < inner_left or inner_right < outer_right)
            )
            if strictly_contains:
                inner_pair = normalized_pair(
                    ordered_row[inner_left],
                    ordered_row[inner_right],
                )
                strict_edges.append((outer_pair, inner_pair))
    return strict_edges


def build_compatibility(
    rows: Sequence[Sequence[Mapping[str, Any]]],
) -> dict[Pair, list[list[bool]]]:
    """Precompute row-pair compatibility tables for center pairs."""

    compatibility: dict[Pair, list[list[bool]]] = {}
    for left_center, right_center in combinations(range(N), 2):
        table: list[list[bool]] = []
        for left_row in rows[left_center]:
            table_row: list[bool] = []
            for right_row in rows[right_center]:
                table_row.append(
                    row_pair_is_compatible(
                        left_center,
                        left_row["row"],
                        right_center,
                        right_row["row"],
                    )
                )
            table.append(table_row)
        compatibility[(left_center, right_center)] = table
    return compatibility


def compatibility_lookup(
    compatibility: Mapping[Pair, Sequence[Sequence[bool]]],
    left_center: int,
    left_index: int,
    right_center: int,
    right_index: int,
) -> bool:
    """Look up compatibility between two indexed rows."""

    if left_center < right_center:
        return bool(compatibility[(left_center, right_center)][left_index][right_index])
    return bool(compatibility[(right_center, left_center)][right_index][left_index])


def strict_quotient_obstruction_kind(
    assignment: Mapping[int, int],
    rows: Sequence[Sequence[Mapping[str, Any]]],
    all_pairs: Sequence[Pair],
    pair_ids: Mapping[Pair, int],
) -> str | None:
    """Classify a vertex-circle quotient obstruction, if one exists."""

    parents = list(range(len(all_pairs)))

    def find(value: int) -> int:
        while parents[value] != value:
            parents[value] = parents[parents[value]]
            value = parents[value]
        return value

    def union(left: int, right: int) -> None:
        left_root = find(left)
        right_root = find(right)
        if left_root != right_root:
            parents[right_root] = left_root

    strict_edges: list[tuple[Pair, Pair]] = []
    for center, row_index in assignment.items():
        row_data = rows[center][row_index]
        equality_pairs = list(row_data["equality_pairs"])
        base = pair_ids[equality_pairs[0]]
        for pair in equality_pairs[1:]:
            union(base, pair_ids[pair])
        strict_edges.extend(row_data["strict_edges"])

    quotient_edges: dict[int, set[int]] = defaultdict(set)
    for outer_pair, inner_pair in strict_edges:
        outer_class = find(pair_ids[outer_pair])
        inner_class = find(pair_ids[inner_pair])
        if outer_class == inner_class:
            return "self_edge"
        quotient_edges[outer_class].add(inner_class)

    state: dict[int, int] = {}

    def has_directed_cycle(vertex: int) -> bool:
        state[vertex] = 1
        for neighbor in quotient_edges.get(vertex, ()):
            neighbor_state = state.get(neighbor, 0)
            if neighbor_state == 1:
                return True
            if neighbor_state == 0 and has_directed_cycle(neighbor):
                return True
        state[vertex] = 2
        return False

    for vertex in list(quotient_edges):
        if state.get(vertex, 0) == 0 and has_directed_cycle(vertex):
            return "strict_cycle"
    return None


def counter_profile(counter: Mapping[Any, int]) -> str:
    """Return a compact histogram profile such as 1:18|2:18."""

    histogram = Counter(counter.values())
    return "|".join(f"{key}:{value}" for key, value in sorted(histogram.items()))


def compact_brancher_payload() -> dict[str, Any]:
    """Regenerate the compact n=9 frontier and classify vertex-circle status."""

    rows = candidate_rows()
    compatibility = build_compatibility(rows)
    all_pairs = [
        normalized_pair(left, right) for left, right in combinations(range(N), 2)
    ]
    pair_ids = {pair: index for index, pair in enumerate(all_pairs)}

    assignment: Assignment = {}
    witness_pair_counts: Counter[Pair] = Counter()
    nodes_visited = 0
    frontier_assignments: list[list[list[int]]] = []
    obstruction_counts: Counter[str] = Counter()
    center_pair_intersection_histogram: Counter[int] = Counter()
    selected_indegree_value_histogram: Counter[int] = Counter()
    witness_pair_profile_counts: Counter[str] = Counter()
    two_overlap_crossing_count = 0

    def candidate_is_viable(center: int, row_index: int) -> bool:
        for other_center, other_index in assignment.items():
            if not compatibility_lookup(
                compatibility,
                center,
                row_index,
                other_center,
                other_index,
            ):
                return False
        for witness_pair in rows[center][row_index]["witness_pairs"]:
            if witness_pair_counts[witness_pair] >= PAIR_CAP:
                return False
        return True

    def choose_center() -> tuple[int | None, list[int]]:
        best_center: int | None = None
        best_options: list[int] = []
        for center in range(N):
            if center in assignment:
                continue
            options = [
                row_index
                for row_index in range(len(rows[center]))
                if candidate_is_viable(center, row_index)
            ]
            if best_center is None or len(options) < len(best_options):
                best_center = center
                best_options = options
            if not options:
                break
        return best_center, best_options

    def record_terminal_assignment() -> None:
        nonlocal two_overlap_crossing_count
        terminal_rows = {
            center: rows[center][assignment[center]]["row"] for center in range(N)
        }
        canonical_rows = [
            [int(label) for label in terminal_rows[center]] for center in range(N)
        ]
        frontier_assignments.append(canonical_rows)

        obstruction_kind = strict_quotient_obstruction_kind(
            assignment,
            rows,
            all_pairs,
            pair_ids,
        )
        obstruction_counts[obstruction_kind or "clean"] += 1

        selected_indegrees: Counter[int] = Counter()
        terminal_witness_pair_counts: Counter[Pair] = Counter()
        for row in terminal_rows.values():
            selected_indegrees.update(row)
            for left, right in combinations(row, 2):
                terminal_witness_pair_counts[normalized_pair(left, right)] += 1
        for vertex in range(N):
            selected_indegree_value_histogram[selected_indegrees[vertex]] += 1
        witness_pair_profile_counts[
            counter_profile(
                {pair: terminal_witness_pair_counts[pair] for pair in all_pairs}
            )
        ] += 1

        for left_center, right_center in combinations(range(N), 2):
            overlap = set(terminal_rows[left_center]) & set(terminal_rows[right_center])
            center_pair_intersection_histogram[len(overlap)] += 1
            if len(overlap) == 2:
                two_overlap_crossing_count += 1

    def search() -> None:
        nonlocal nodes_visited
        if len(assignment) == N:
            record_terminal_assignment()
            return
        center, options = choose_center()
        if center is None:
            return
        for row_index in options:
            nodes_visited += 1
            assignment[center] = row_index
            for witness_pair in rows[center][row_index]["witness_pairs"]:
                witness_pair_counts[witness_pair] += 1
            search()
            for witness_pair in rows[center][row_index]["witness_pairs"]:
                witness_pair_counts[witness_pair] -= 1
            del assignment[center]

    search()
    sorted_assignments = sorted(frontier_assignments)
    assignment_digest = hashlib.sha256(
        json.dumps(sorted_assignments, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    clean_assignments = obstruction_counts.get("clean", 0)

    summary = {
        "nodes_visited": nodes_visited,
        "candidate_rows_per_center": [len(center_rows) for center_rows in rows],
        "frontier_assignment_count": len(frontier_assignments),
        "assignment_digest_sha256": assignment_digest,
        "vertex_circle_obstruction_counts": dict(sorted(obstruction_counts.items())),
        "vertex_circle_clean_assignments": clean_assignments,
        "center_pair_intersection_histogram": {
            str(key): value
            for key, value in sorted(center_pair_intersection_histogram.items())
        },
        "two_overlap_crossing_count": two_overlap_crossing_count,
        "witness_pair_profile_counts": dict(
            sorted(witness_pair_profile_counts.items())
        ),
        "selected_indegree_value_histogram": {
            str(key): value
            for key, value in sorted(selected_indegree_value_histogram.items())
        },
    }

    errors: list[str] = []
    _check_equal(errors, "nodes_visited", nodes_visited, EXPECTED_NODES_VISITED)
    _check_equal(
        errors,
        "frontier_assignment_count",
        len(frontier_assignments),
        EXPECTED_FRONTIER_ASSIGNMENTS,
    )
    _check_equal(
        errors,
        "assignment_digest_sha256",
        assignment_digest,
        EXPECTED_ASSIGNMENT_DIGEST,
    )
    _check_equal(
        errors,
        "vertex_circle_obstruction_counts",
        {key: obstruction_counts[key] for key in EXPECTED_OBSTRUCTION_COUNTS},
        EXPECTED_OBSTRUCTION_COUNTS,
    )
    _check_equal(
        errors,
        "clean assignments",
        clean_assignments,
        EXPECTED_CLEAN_ASSIGNMENTS,
    )
    _check_equal(
        errors,
        "center_pair_intersection_histogram",
        summary["center_pair_intersection_histogram"],
        EXPECTED_CENTER_PAIR_INTERSECTION_HISTOGRAM,
    )
    _check_equal(
        errors,
        "two_overlap_crossing_count",
        two_overlap_crossing_count,
        EXPECTED_TWO_OVERLAP_CROSSING_COUNT,
    )
    _check_equal(
        errors,
        "witness_pair_profile_counts",
        summary["witness_pair_profile_counts"],
        EXPECTED_WITNESS_PAIR_PROFILE_COUNTS,
    )
    _check_equal(
        errors,
        "selected_indegree_value_histogram",
        summary["selected_indegree_value_histogram"],
        EXPECTED_SELECTED_INDEGREE_VALUE_HISTOGRAM,
    )

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": N,
        "row_size": ROW_SIZE,
        "pair_cap": PAIR_CAP,
        "brancher": summary,
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "interpretation": (
            "A passed run independently regenerates 184 n=9 incidence/count "
            "frontier assignments and classifies all 184 as vertex-circle "
            "quotient obstructed. This is review-pending finite-case audit "
            "evidence only, not a global theorem or counterexample."
        ),
        "provenance": dict(PROVENANCE),
    }


def assert_expected_payload(payload: Mapping[str, Any]) -> None:
    """Assert the expected compact brancher payload."""

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
        "does not import the project n=9 brancher modules",
        "does not read the stored 184-assignment frontier artifact",
        "does not complete independent review",
        "does not promote n=9 to a theorem",
        "does not prove Erdos Problem #97",
        "does not produce a counterexample",
        "does not update the official/global status",
    ):
        if required not in claim_scope:
            raise AssertionError(f"claim_scope missing {required!r}")
    if payload.get("validation_status") != "passed":
        raise AssertionError(f"validation errors: {payload.get('validation_errors')!r}")
    brancher = payload.get("brancher")
    if not isinstance(brancher, Mapping):
        raise AssertionError("brancher summary missing")
    expected = {
        "nodes_visited": EXPECTED_NODES_VISITED,
        "candidate_rows_per_center": [70] * N,
        "frontier_assignment_count": EXPECTED_FRONTIER_ASSIGNMENTS,
        "assignment_digest_sha256": EXPECTED_ASSIGNMENT_DIGEST,
        "vertex_circle_obstruction_counts": EXPECTED_OBSTRUCTION_COUNTS,
        "vertex_circle_clean_assignments": EXPECTED_CLEAN_ASSIGNMENTS,
        "center_pair_intersection_histogram": (
            EXPECTED_CENTER_PAIR_INTERSECTION_HISTOGRAM
        ),
        "two_overlap_crossing_count": EXPECTED_TWO_OVERLAP_CROSSING_COUNT,
        "witness_pair_profile_counts": EXPECTED_WITNESS_PAIR_PROFILE_COUNTS,
        "selected_indegree_value_histogram": EXPECTED_SELECTED_INDEGREE_VALUE_HISTOGRAM,
    }
    for key, value in expected.items():
        if brancher.get(key) != value:
            raise AssertionError(f"{key} mismatch: {brancher.get(key)!r} != {value!r}")


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    """Write JSON with stable formatting."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _check_equal(errors: list[str], label: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        errors.append(f"{label}: expected {expected!r}, got {actual!r}")


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--artifact",
        type=Path,
        default=DEFAULT_ARTIFACT,
        help="artifact path used by --write and --check",
    )
    parser.add_argument("--write", action="store_true", help="write the JSON artifact")
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare regenerated payload with the stored artifact",
    )
    parser.add_argument(
        "--assert-expected",
        action="store_true",
        help="assert the expected counts and non-overclaiming metadata",
    )
    parser.add_argument("--json", action="store_true", help="print JSON output")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the compact brancher audit."""

    args = parse_args(sys.argv[1:] if argv is None else argv)
    payload = compact_brancher_payload()

    if args.assert_expected:
        assert_expected_payload(payload)

    if args.write:
        write_json(args.artifact, payload)

    if args.check:
        stored = load_json(args.artifact)
        if stored != payload:
            raise AssertionError(
                "stored artifact differs from regenerated payload: "
                f"{args.artifact}"
            )

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif not args.write and not args.check:
        brancher = payload["brancher"]
        print(
            "compact n=9 brancher: "
            f"{brancher['frontier_assignment_count']} frontier assignments; "
            f"{brancher['vertex_circle_clean_assignments']} clean"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
