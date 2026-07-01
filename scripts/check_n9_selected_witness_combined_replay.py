#!/usr/bin/env python3
"""Combined review-pending n=9 selected-witness replay.

This checker is a narrow companion to ``check_n9_vertex_circle_compact_brancher``.
It reuses that compact independent brancher surface, then emits explicit
per-assignment vertex-circle quotient certificates for the 184 regenerated
frontier assignments.  The output is review infrastructure only: it does not
complete independent review, promote n=9 to a theorem, prove Erdos Problem #97,
or produce a counterexample.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from itertools import combinations
from math import comb
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.check_n9_vertex_circle_compact_brancher import (  # noqa: E402
    EXPECTED_ASSIGNMENT_DIGEST,
    EXPECTED_CENTER_PAIR_INTERSECTION_HISTOGRAM,
    EXPECTED_CLEAN_ASSIGNMENTS,
    EXPECTED_FRONTIER_ASSIGNMENTS,
    EXPECTED_NODES_VISITED,
    EXPECTED_OBSTRUCTION_COUNTS,
    EXPECTED_SELECTED_INDEGREE_VALUE_HISTOGRAM,
    EXPECTED_TWO_OVERLAP_CROSSING_COUNT,
    EXPECTED_WITNESS_PAIR_PROFILE_COUNTS,
    N,
    PAIR_CAP,
    ROW_SIZE,
    Pair,
    angular_order_at_center,
    build_compatibility,
    candidate_rows,
    compatibility_lookup,
    normalized_pair,
)

DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "n9_selected_witness_combined_replay.json"
)
DEFAULT_CERTIFICATES_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "n9_selected_witness_obstruction_certificates.json"
)

SCHEMA = "erdos97.n9_selected_witness_combined_replay.v1"
CERTIFICATE_SCHEMA = "erdos97.n9_selected_witness_obstruction_certificates.v1"
STATUS = "REVIEW_PENDING_N9_SELECTED_WITNESS_COMBINED_REPLAY"
CERTIFICATE_STATUS = "REVIEW_PENDING_N9_SELECTED_WITNESS_OBSTRUCTION_CERTIFICATES"
TRUST = "MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING"
CLAIM_SCOPE = (
    "Combined review-pending replay for the n=9 selected-witness candidate: "
    "localized rich-support counting reduces hypothetical 4-bad nonagons to "
    "the exact-four support frontier, the compact brancher regenerates the "
    "184 exact-four frontier assignments, and explicit vertex-circle quotient "
    "certificates classify all 184 as obstructed. This is audit evidence only: "
    "it does not complete independent review, does not promote n=9 to a "
    "theorem, does not prove Erdos Problem #97, does not produce a "
    "counterexample, and does not update the official/global status."
)
CERTIFICATE_CLAIM_SCOPE = (
    "Per-assignment vertex-circle quotient certificates for the same "
    "review-pending 184 n=9 exact-four frontier assignments. These certificates "
    "are replay data for audit only; they do not complete independent review, "
    "do not prove n=9, do not prove Erdos Problem #97, and do not produce a "
    "counterexample."
)
PROVENANCE = {
    "generator": "scripts/check_n9_selected_witness_combined_replay.py",
    "command": (
        "python scripts/check_n9_selected_witness_combined_replay.py "
        "--write --assert-expected"
    ),
    "derived_from": "scripts/check_n9_vertex_circle_compact_brancher.py",
}

EXPECTED_CERTIFICATE_DIGEST = (
    "f1a58f2155894ae8e1d0a14bd0478c8d8ed6957f6f294f685405e68a6243f790"
)

Row = tuple[int, ...]
Assignment = dict[int, int]


def repo_path(path: Path) -> str:
    """Return a stable repo-relative path for JSON artifacts."""

    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


@dataclass(frozen=True)
class CombinedReplayResult:
    """Generated summary and certificate payloads."""

    summary: dict[str, Any]
    certificates_payload: dict[str, Any]


class UnionFind:
    """Small union-find for selected-distance quotient classes."""

    def __init__(self, size: int):
        self.parents = list(range(size))

    def find(self, value: int) -> int:
        while self.parents[value] != value:
            self.parents[value] = self.parents[self.parents[value]]
            value = self.parents[value]
        return value

    def union(self, left: int, right: int) -> None:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root != right_root:
            self.parents[right_root] = left_root


def pair_to_json(pair: Pair) -> list[int]:
    """Return a pair as a JSON-friendly list."""

    return [int(pair[0]), int(pair[1])]


def strict_vertex_circle_edges_with_intervals(
    ordered_row: Sequence[int],
) -> list[dict[str, Any]]:
    """Return nested-chord strict inequalities with interval provenance."""

    strict_edges: list[dict[str, Any]] = []
    positions = range(len(ordered_row))
    for outer_left, outer_right in combinations(positions, 2):
        outer_pair = normalized_pair(ordered_row[outer_left], ordered_row[outer_right])
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
                strict_edges.append(
                    {
                        "outer_pair": outer_pair,
                        "inner_pair": inner_pair,
                        "outer_interval": [outer_left, outer_right],
                        "inner_interval": [inner_left, inner_right],
                    }
                )
    return strict_edges


def localized_counting_summary(n: int = N) -> dict[str, Any]:
    """Return the localized rich-support counting consequence for n=9."""

    if n < 5:
        raise ValueError("n must be at least 5")
    per_label_budget = 2 * n - 4
    occurrence_cap_if_four_bad = per_label_budget // (ROW_SIZE - 1)
    total_occurrence_cap = n * occurrence_cap_if_four_bad
    baseline_occurrences = ROW_SIZE * n
    exact_forced = total_occurrence_cap == baseline_occurrences
    global_budget = n + 2 * (comb(n, 2) - n)
    global_pair_demand = n * comb(ROW_SIZE, 2)
    return {
        "n": n,
        "lemma": (
            "For each fixed witness label x, "
            "sum_{i: x in R_i} (|R_i|-1) <= 2n-4."
        ),
        "per_label_pair_budget": per_label_budget,
        "occurrence_cap_per_label_for_support_size_at_least_4": (
            occurrence_cap_if_four_bad
        ),
        "total_occurrence_cap": total_occurrence_cap,
        "baseline_occurrences_for_4_bad_polygon": baseline_occurrences,
        "all_centers_forced_exact_four": exact_forced,
        "selected_indegree_forced_regular": exact_forced,
        "global_pair_budget": global_budget,
        "global_pair_demand_exact_four": global_pair_demand,
        "interpretation": (
            "For n=9, every rich support occurrence costs at least three of "
            "the localized pair budget at its witness label. The cap "
            "floor((2n-4)/3)=4 gives at most 36 total occurrences, while a "
            "4-bad nonagon already needs 36. Therefore all chosen rich "
            "supports have size exactly four and every label has selected "
            "indegree exactly four."
        ),
    }


def bfs_equality_path(
    adjacency: Mapping[int, set[int]],
    start: int,
    goal: int,
    all_pairs: Sequence[Pair],
) -> list[list[int]]:
    """Return one equality path between two distance-pair ids."""

    if start == goal:
        return [pair_to_json(all_pairs[start])]
    queue: deque[int] = deque([start])
    parent: dict[int, int | None] = {start: None}
    while queue:
        node = queue.popleft()
        for neighbor in sorted(adjacency.get(node, ())):
            if neighbor in parent:
                continue
            parent[neighbor] = node
            if neighbor == goal:
                path: list[int] = [goal]
                current = goal
                while parent[current] is not None:
                    current = parent[current]  # type: ignore[assignment]
                    path.append(current)
                path.reverse()
                return [pair_to_json(all_pairs[item]) for item in path]
            queue.append(neighbor)
    raise AssertionError("equality path requested inside a class but not found")


def equality_components_json(
    union_find: UnionFind,
    all_pairs: Sequence[Pair],
) -> list[list[list[int]]]:
    """Return nontrivial selected-distance equality classes."""

    classes: dict[int, list[Pair]] = defaultdict(list)
    for pair_id, pair in enumerate(all_pairs):
        classes[union_find.find(pair_id)].append(pair)
    components: list[list[list[int]]] = []
    for pairs in classes.values():
        if len(pairs) >= 2:
            components.append([pair_to_json(pair) for pair in sorted(pairs)])
    components.sort(key=lambda component: (len(component), component))
    return components


def find_directed_cycle(graph: Mapping[int, set[int]]) -> list[int] | None:
    """Return a directed cycle as a root-id list with the first root repeated."""

    state: dict[int, int] = {}
    stack: list[int] = []
    stack_pos: dict[int, int] = {}

    def visit(vertex: int) -> list[int] | None:
        state[vertex] = 1
        stack_pos[vertex] = len(stack)
        stack.append(vertex)
        for neighbor in sorted(graph.get(vertex, ())):
            neighbor_state = state.get(neighbor, 0)
            if neighbor_state == 1:
                start = stack_pos[neighbor]
                return stack[start:] + [neighbor]
            if neighbor_state == 0:
                cycle = visit(neighbor)
                if cycle is not None:
                    return cycle
        stack.pop()
        del stack_pos[vertex]
        state[vertex] = 2
        return None

    for vertex in sorted(graph):
        if state.get(vertex, 0) == 0:
            cycle = visit(vertex)
            if cycle is not None:
                return cycle
    return None


def vertex_circle_certificate(
    assignment: Mapping[int, int],
    rows: Sequence[Sequence[Mapping[str, Any]]],
    all_pairs: Sequence[Pair],
    pair_ids: Mapping[Pair, int],
    *,
    include_components: bool = False,
) -> dict[str, Any]:
    """Classify and explicitly certify one vertex-circle quotient obstruction."""

    union_find = UnionFind(len(all_pairs))
    equality_adjacency: dict[int, set[int]] = defaultdict(set)
    strict_edges: list[dict[str, Any]] = []

    for center in sorted(assignment):
        row_index = assignment[center]
        row_data = rows[center][row_index]
        equality_pairs = list(row_data["equality_pairs"])
        base_id = pair_ids[equality_pairs[0]]
        for pair in equality_pairs[1:]:
            pair_id = pair_ids[pair]
            union_find.union(base_id, pair_id)
            equality_adjacency[base_id].add(pair_id)
            equality_adjacency[pair_id].add(base_id)
        ordered = angular_order_at_center(center, row_data["row"])
        for edge in strict_vertex_circle_edges_with_intervals(ordered):
            strict_edges.append(
                {
                    "center": center,
                    "selected_row": [int(label) for label in row_data["row"]],
                    "angular_order": [int(label) for label in ordered],
                    "outer_pair": edge["outer_pair"],
                    "inner_pair": edge["inner_pair"],
                    "outer_interval": edge["outer_interval"],
                    "inner_interval": edge["inner_interval"],
                }
            )

    quotient_edges: dict[int, set[int]] = defaultdict(set)
    quotient_edge_witness: dict[tuple[int, int], dict[str, Any]] = {}

    for edge in strict_edges:
        outer_id = pair_ids[edge["outer_pair"]]
        inner_id = pair_ids[edge["inner_pair"]]
        outer_class = union_find.find(outer_id)
        inner_class = union_find.find(inner_id)
        if outer_class == inner_class:
            certificate: dict[str, Any] = {
                "kind": "self_edge",
                "meaning": (
                    "A vertex-circle strict inequality has both endpoints in "
                    "the same selected-distance equality class."
                ),
                "strict_edge": {
                    "center": edge["center"],
                    "selected_row": edge["selected_row"],
                    "angular_order": edge["angular_order"],
                    "outer_pair": pair_to_json(edge["outer_pair"]),
                    "inner_pair": pair_to_json(edge["inner_pair"]),
                    "outer_interval": edge["outer_interval"],
                    "inner_interval": edge["inner_interval"],
                },
                "equality_path_outer_to_inner": bfs_equality_path(
                    equality_adjacency,
                    outer_id,
                    inner_id,
                    all_pairs,
                ),
            }
            if include_components:
                certificate["equality_components"] = equality_components_json(
                    union_find,
                    all_pairs,
                )
            return certificate
        quotient_edges[outer_class].add(inner_class)
        quotient_edge_witness.setdefault((outer_class, inner_class), edge)

    cycle = find_directed_cycle(quotient_edges)
    if cycle is not None:
        cycle_edges: list[dict[str, Any]] = []
        for left_class, right_class in zip(cycle, cycle[1:]):
            edge = quotient_edge_witness[(left_class, right_class)]
            cycle_edges.append(
                {
                    "from_class_root_pair": pair_to_json(all_pairs[left_class]),
                    "to_class_root_pair": pair_to_json(all_pairs[right_class]),
                    "center": edge["center"],
                    "selected_row": edge["selected_row"],
                    "angular_order": edge["angular_order"],
                    "outer_pair": pair_to_json(edge["outer_pair"]),
                    "inner_pair": pair_to_json(edge["inner_pair"]),
                    "outer_interval": edge["outer_interval"],
                    "inner_interval": edge["inner_interval"],
                }
            )
        certificate = {
            "kind": "strict_cycle",
            "meaning": (
                "The quotient graph of strict distance inequalities contains "
                "a directed cycle."
            ),
            "cycle_length": len(cycle) - 1,
            "cycle_class_root_pairs": [pair_to_json(all_pairs[root]) for root in cycle],
            "cycle_edges": cycle_edges,
        }
        if include_components:
            certificate["equality_components"] = equality_components_json(
                union_find,
                all_pairs,
            )
        return certificate

    certificate = {
        "kind": "clean",
        "meaning": "No vertex-circle self-edge or strict directed cycle was found.",
    }
    if include_components:
        certificate["equality_components"] = equality_components_json(
            union_find,
            all_pairs,
        )
    return certificate


def counter_profile(counter: Mapping[Any, int]) -> str:
    """Return a compact histogram profile such as 1:18|2:18."""

    histogram = Counter(counter.values())
    return "|".join(f"{key}:{value}" for key, value in sorted(histogram.items()))


def generate_replay(*, include_components: bool = False) -> CombinedReplayResult:
    """Regenerate the frontier and explicit obstruction certificates."""

    rows = candidate_rows()
    compatibility = build_compatibility(rows)
    all_pairs = [normalized_pair(left, right) for left, right in combinations(range(N), 2)]
    pair_ids = {pair: index for index, pair in enumerate(all_pairs)}

    assignment: Assignment = {}
    witness_pair_counts: Counter[Pair] = Counter()
    nodes_visited = 0
    frontier_assignments: list[list[list[int]]] = []
    assignment_certificates: list[dict[str, Any]] = []
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

    def terminal_rows_as_lists() -> list[list[int]]:
        return [
            [int(label) for label in rows[center][assignment[center]]["row"]]
            for center in range(N)
        ]

    def record_terminal_assignment() -> None:
        nonlocal two_overlap_crossing_count
        canonical_rows = terminal_rows_as_lists()
        frontier_assignments.append(canonical_rows)
        certificate = vertex_circle_certificate(
            assignment,
            rows,
            all_pairs,
            pair_ids,
            include_components=include_components,
        )
        obstruction_counts[certificate["kind"]] += 1
        assignment_certificates.append(
            {
                "assignment_index": len(frontier_assignments) - 1,
                "selected_rows": canonical_rows,
                "obstruction": certificate,
            }
        )

        selected_indegrees: Counter[int] = Counter()
        terminal_witness_pair_counts: Counter[Pair] = Counter()
        for row in canonical_rows:
            selected_indegrees.update(row)
            for left, right in combinations(row, 2):
                terminal_witness_pair_counts[normalized_pair(left, right)] += 1
        for vertex in range(N):
            selected_indegree_value_histogram[selected_indegrees[vertex]] += 1
        witness_pair_profile_counts[
            counter_profile({pair: terminal_witness_pair_counts[pair] for pair in all_pairs})
        ] += 1

        for left_center, right_center in combinations(range(N), 2):
            overlap = set(canonical_rows[left_center]) & set(canonical_rows[right_center])
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
    certificate_digest = hashlib.sha256(
        json.dumps(
            assignment_certificates,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    clean_assignments = obstruction_counts.get("clean", 0)

    brancher_summary = {
        "nodes_visited": nodes_visited,
        "candidate_rows_per_center": [len(center_rows) for center_rows in rows],
        "frontier_assignment_count": len(frontier_assignments),
        "assignment_digest_sha256": assignment_digest,
        "obstruction_counts": {
            key: int(obstruction_counts[key]) for key in sorted(obstruction_counts)
        },
        "clean_assignments": clean_assignments,
        "center_pair_intersection_histogram": {
            str(key): int(value) for key, value in sorted(center_pair_intersection_histogram.items())
        },
        "two_overlap_crossing_count": two_overlap_crossing_count,
        "witness_pair_profile_counts": dict(sorted(witness_pair_profile_counts.items())),
        "selected_indegree_value_histogram": {
            str(key): int(value) for key, value in sorted(selected_indegree_value_histogram.items())
        },
    }

    errors = _validation_errors(brancher_summary, certificate_digest)
    summary = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": N,
        "row_size": ROW_SIZE,
        "pair_cap": PAIR_CAP,
        "localized_counting": localized_counting_summary(N),
        "brancher": brancher_summary,
        "certificate_artifact": repo_path(DEFAULT_CERTIFICATES_ARTIFACT),
        "certificate_count": len(assignment_certificates),
        "certificate_digest_sha256": certificate_digest,
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "interpretation": (
            "A passed run checks that the review-pending localized-counting "
            "and exact-four n=9 vertex-circle route has the expected compact "
            "frontier accounting and stores explicit certificates for every "
            "frontier assignment. This is audit evidence only, not completed "
            "review or a status promotion."
        ),
        "provenance": dict(PROVENANCE),
    }
    certificates_payload = {
        "schema": CERTIFICATE_SCHEMA,
        "status": CERTIFICATE_STATUS,
        "trust": TRUST,
        "claim_scope": CERTIFICATE_CLAIM_SCOPE,
        "source_summary_artifact": repo_path(DEFAULT_ARTIFACT),
        "certificate_count": len(assignment_certificates),
        "certificate_digest_sha256": certificate_digest,
        "certificates": assignment_certificates,
        "provenance": dict(PROVENANCE),
    }
    return CombinedReplayResult(summary=summary, certificates_payload=certificates_payload)


def _validation_errors(
    brancher_summary: Mapping[str, Any],
    certificate_digest: str,
) -> list[str]:
    errors: list[str] = []
    _check_equal(errors, "nodes_visited", brancher_summary["nodes_visited"], EXPECTED_NODES_VISITED)
    _check_equal(
        errors,
        "frontier_assignment_count",
        brancher_summary["frontier_assignment_count"],
        EXPECTED_FRONTIER_ASSIGNMENTS,
    )
    _check_equal(
        errors,
        "assignment_digest_sha256",
        brancher_summary["assignment_digest_sha256"],
        EXPECTED_ASSIGNMENT_DIGEST,
    )
    _check_equal(
        errors,
        "obstruction_counts",
        brancher_summary["obstruction_counts"],
        EXPECTED_OBSTRUCTION_COUNTS,
    )
    _check_equal(
        errors,
        "clean_assignments",
        brancher_summary["clean_assignments"],
        EXPECTED_CLEAN_ASSIGNMENTS,
    )
    _check_equal(
        errors,
        "center_pair_intersection_histogram",
        brancher_summary["center_pair_intersection_histogram"],
        EXPECTED_CENTER_PAIR_INTERSECTION_HISTOGRAM,
    )
    _check_equal(
        errors,
        "two_overlap_crossing_count",
        brancher_summary["two_overlap_crossing_count"],
        EXPECTED_TWO_OVERLAP_CROSSING_COUNT,
    )
    _check_equal(
        errors,
        "witness_pair_profile_counts",
        brancher_summary["witness_pair_profile_counts"],
        EXPECTED_WITNESS_PAIR_PROFILE_COUNTS,
    )
    _check_equal(
        errors,
        "selected_indegree_value_histogram",
        brancher_summary["selected_indegree_value_histogram"],
        EXPECTED_SELECTED_INDEGREE_VALUE_HISTOGRAM,
    )
    _check_equal(
        errors,
        "certificate_digest_sha256",
        certificate_digest,
        EXPECTED_CERTIFICATE_DIGEST,
    )
    return errors


def assert_expected_summary(payload: Mapping[str, Any]) -> None:
    """Assert expected summary counts and non-overclaiming metadata."""

    if payload.get("schema") != SCHEMA:
        raise AssertionError(f"schema mismatch: {payload.get('schema')!r}")
    if payload.get("status") != STATUS:
        raise AssertionError(f"status mismatch: {payload.get('status')!r}")
    if payload.get("trust") != TRUST:
        raise AssertionError(f"trust mismatch: {payload.get('trust')!r}")
    if payload.get("claim_scope") != CLAIM_SCOPE:
        raise AssertionError(f"claim_scope mismatch: {payload.get('claim_scope')!r}")
    if payload.get("provenance") != PROVENANCE:
        raise AssertionError(f"provenance mismatch: {payload.get('provenance')!r}")
    for required in (
        "does not complete independent review",
        "does not promote n=9 to a theorem",
        "does not prove Erdos Problem #97",
        "does not produce a counterexample",
        "does not update the official/global status",
    ):
        if required not in CLAIM_SCOPE:
            raise AssertionError(f"claim_scope missing {required!r}")
    if payload.get("validation_status") != "passed":
        raise AssertionError(f"validation errors: {payload.get('validation_errors')!r}")
    brancher = payload.get("brancher")
    if not isinstance(brancher, Mapping):
        raise AssertionError("brancher summary missing")
    errors = _validation_errors(
        brancher,
        str(payload.get("certificate_digest_sha256")),
    )
    if errors:
        raise AssertionError(errors)
    localized = payload.get("localized_counting")
    if not isinstance(localized, Mapping):
        raise AssertionError("localized_counting missing")
    if localized.get("all_centers_forced_exact_four") is not True:
        raise AssertionError("localized_counting did not force exact-four")
    if localized.get("selected_indegree_forced_regular") is not True:
        raise AssertionError("localized_counting did not force regular indegree")


def assert_expected_certificates(payload: Mapping[str, Any]) -> None:
    """Assert expected certificate object metadata and contents."""

    if payload.get("schema") != CERTIFICATE_SCHEMA:
        raise AssertionError(f"certificate schema mismatch: {payload.get('schema')!r}")
    if payload.get("status") != CERTIFICATE_STATUS:
        raise AssertionError(f"certificate status mismatch: {payload.get('status')!r}")
    if payload.get("trust") != TRUST:
        raise AssertionError(f"certificate trust mismatch: {payload.get('trust')!r}")
    if payload.get("claim_scope") != CERTIFICATE_CLAIM_SCOPE:
        raise AssertionError("certificate claim_scope mismatch")
    if payload.get("provenance") != PROVENANCE:
        raise AssertionError("certificate provenance mismatch")
    certificates = payload.get("certificates")
    if not isinstance(certificates, list):
        raise AssertionError("certificates list missing")
    if payload.get("certificate_count") != EXPECTED_FRONTIER_ASSIGNMENTS:
        raise AssertionError("certificate_count mismatch")
    if len(certificates) != EXPECTED_FRONTIER_ASSIGNMENTS:
        raise AssertionError(f"certificates length mismatch: {len(certificates)}")
    digest = hashlib.sha256(
        json.dumps(certificates, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    if digest != EXPECTED_CERTIFICATE_DIGEST:
        raise AssertionError(f"certificate digest mismatch: {digest}")
    if payload.get("certificate_digest_sha256") != EXPECTED_CERTIFICATE_DIGEST:
        raise AssertionError("certificate_digest_sha256 mismatch")
    obstruction_counts = Counter(
        item.get("obstruction", {}).get("kind") for item in certificates
    )
    if dict(sorted(obstruction_counts.items())) != EXPECTED_OBSTRUCTION_COUNTS:
        raise AssertionError(f"certificate obstruction counts mismatch: {obstruction_counts}")
    for index, item in enumerate(certificates):
        if item.get("assignment_index") != index:
            raise AssertionError(f"assignment_index mismatch at {index}")
        selected_rows = item.get("selected_rows")
        if not isinstance(selected_rows, list) or len(selected_rows) != N:
            raise AssertionError(f"selected_rows malformed at {index}")


def load_json(path: Path) -> Any:
    """Load a JSON artifact."""

    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
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
        help="summary artifact path used by --write and --check",
    )
    parser.add_argument(
        "--certificates-artifact",
        type=Path,
        default=DEFAULT_CERTIFICATES_ARTIFACT,
        help="certificate artifact path used by --write and --check",
    )
    parser.add_argument("--write", action="store_true", help="write JSON artifacts")
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare regenerated payloads with the stored artifacts",
    )
    parser.add_argument(
        "--assert-expected",
        action="store_true",
        help="assert expected counts and non-overclaiming metadata",
    )
    parser.add_argument(
        "--include-components",
        action="store_true",
        help=(
            "include full nontrivial equality components in every certificate; "
            "not compatible with the default checked artifact digest"
        ),
    )
    parser.add_argument("--json", action="store_true", help="print summary JSON")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the combined replay."""

    args = parse_args(sys.argv[1:] if argv is None else argv)
    result = generate_replay(include_components=args.include_components)

    if args.assert_expected:
        assert_expected_summary(result.summary)
        assert_expected_certificates(result.certificates_payload)

    if args.write:
        write_json(args.artifact, result.summary)
        write_json(args.certificates_artifact, result.certificates_payload)

    if args.check:
        stored_summary = load_json(args.artifact)
        stored_certificates = load_json(args.certificates_artifact)
        if stored_summary != result.summary:
            raise AssertionError(f"stored summary differs: {args.artifact}")
        if stored_certificates != result.certificates_payload:
            raise AssertionError(
                f"stored certificates differ: {args.certificates_artifact}"
            )

    if args.json:
        print(json.dumps(result.summary, indent=2, sort_keys=True))
    elif not args.write and not args.check:
        brancher = result.summary["brancher"]
        print(
            "n=9 selected-witness combined replay: "
            f"{brancher['frontier_assignment_count']} frontier assignments; "
            f"{brancher['clean_assignments']} clean"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
