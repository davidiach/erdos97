#!/usr/bin/env python3
"""Close the n=10 q=2 four/five rich-support layer by vertex-circle replay.

This review-pending diagnostic extends the n=10 mixed rich-support capacity
catalogue.  The earlier support-level checker closes q=3..7 size-five supports
and records a direct q=2 support-filter survivor.  This checker exhausts q=2
under the same row-pair cap, two-overlap crossing, and witness-pair capacity
filters, while adding monotone partial pruning by the rich-class
vertex-circle quotient gate.

The result is still only finite support/quotient bookkeeping.  It does not
prove n=10, does not prove Erdos Problem #97, and does not give a
counterexample.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]

SCHEMA = "erdos97.n10_q2_rich_vertex_circle.v1"
STATUS = "N10_Q2_RICH_VERTEX_CIRCLE_CLOSURE"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
DEFAULT_OUT = ROOT / "data" / "certificates" / "n10_q2_rich_vertex_circle.json"
N = 10
ORDER = tuple(range(N))
SUPPORT_SIZES = (4, 5)
Q = 2

EXPECTED_REP_SUMMARIES = {
    "0,1": {
        "nodes_visited": 10569,
        "dead_end_count": 3003,
        "vertex_circle_prune_count": 5649,
        "max_depth_reached": 5,
        "vertex_circle_status_counts": {"self_edge": 2332, "strict_cycle": 3317},
    },
    "0,2": {
        "nodes_visited": 34486,
        "dead_end_count": 13406,
        "vertex_circle_prune_count": 12911,
        "max_depth_reached": 6,
        "vertex_circle_status_counts": {"self_edge": 4738, "strict_cycle": 8173},
    },
    "0,3": {
        "nodes_visited": 66565,
        "dead_end_count": 34642,
        "vertex_circle_prune_count": 17162,
        "max_depth_reached": 6,
        "vertex_circle_status_counts": {"self_edge": 7537, "strict_cycle": 9625},
    },
    "0,4": {
        "nodes_visited": 95385,
        "dead_end_count": 50264,
        "vertex_circle_prune_count": 22718,
        "max_depth_reached": 6,
        "vertex_circle_status_counts": {"self_edge": 8276, "strict_cycle": 14442},
    },
    "0,5": {
        "nodes_visited": 113919,
        "dead_end_count": 58559,
        "vertex_circle_prune_count": 27272,
        "max_depth_reached": 6,
        "vertex_circle_status_counts": {"self_edge": 9962, "strict_cycle": 17310},
    },
}
EXPECTED_AGGREGATE = {
    "representatives_checked": 5,
    "complete_assignments_found": 0,
    "total_nodes_visited": 320924,
    "total_dead_end_count": 159874,
    "total_vertex_circle_prune_count": 85712,
    "max_depth_reached": 6,
    "vertex_circle_status_counts": {"self_edge": 32845, "strict_cycle": 52867},
}

Pair = tuple[int, int]
PairId = int

ALL_PAIRS: tuple[Pair, ...] = tuple(combinations(range(N), 2))
PAIR_TO_ID: dict[Pair, PairId] = {pair: idx for idx, pair in enumerate(ALL_PAIRS)}
PAIR_COUNT = len(ALL_PAIRS)


def normalized_pair(left: int, right: int) -> Pair:
    """Return a sorted non-loop pair."""

    if left == right:
        raise ValueError("loop pair")
    return (left, right) if left < right else (right, left)


def pair_id(left: int, right: int) -> PairId:
    """Return the dense id of an unordered pair."""

    return PAIR_TO_ID[normalized_pair(left, right)]


def support_mask(support: Sequence[int]) -> int:
    """Return the bitmask of a support."""

    out = 0
    for label in support:
        out |= 1 << int(label)
    return out


def iter_bits(mask: int) -> Iterable[int]:
    """Yield set-bit indices of a nonnegative integer bitset."""

    while mask:
        low_bit = mask & -mask
        yield low_bit.bit_length() - 1
        mask ^= low_bit


def chords_cross_in_natural_order(first: Pair, second: Pair) -> bool:
    """Return whether two disjoint chords cross in the natural cyclic order."""

    if set(first) & set(second):
        return False
    a, b = normalized_pair(*first)
    c, d = normalized_pair(*second)
    return (a < c < b) != (a < d < b)


def canonical_center_subset(subset: Sequence[int], n: int = N) -> tuple[int, ...]:
    """Return the dihedral canonical representative of a center subset."""

    raw = set(subset)
    variants: list[tuple[int, ...]] = []
    for shift in range(n):
        variants.append(tuple(sorted((label + shift) % n for label in raw)))
        variants.append(tuple(sorted((shift - label) % n for label in raw)))
    return min(variants)


def dihedral_representatives(q: int, n: int = N) -> tuple[tuple[int, ...], ...]:
    """Return dihedral representatives of q-subsets of centers."""

    representatives = {
        canonical_center_subset(subset, n)
        for subset in combinations(range(n), q)
    }
    return tuple(sorted(representatives))


@dataclass(frozen=True)
class StrictEdgeTemplate:
    """A row-local nested-interval strict inequality before quotienting."""

    outer_pair_id: PairId
    inner_pair_id: PairId
    row: int
    witness_order: tuple[int, ...]
    outer_interval: tuple[int, int]
    inner_interval: tuple[int, int]
    outer_pair: Pair
    inner_pair: Pair


@dataclass(frozen=True)
class RowOption:
    """Precomputed support option for one center and support size."""

    witnesses: tuple[int, ...]
    mask: int
    witness_pair_ids: tuple[PairId, ...]
    center_witness_pair_ids: tuple[PairId, ...]
    strict_edges: tuple[StrictEdgeTemplate, ...]


@dataclass(frozen=True)
class PreparedCatalogue:
    options: Mapping[tuple[int, int], tuple[RowOption, ...]]
    pair_option_bits: Mapping[tuple[int, int], tuple[int, ...]]
    compatible_option_bits: Mapping[tuple[int, int, int, int], tuple[int, ...]]
    full_domain: Mapping[tuple[int, int], int]


@dataclass(frozen=True)
class SearchResult:
    found_clean_complete_assignment: bool
    nodes_visited: int
    dead_end_count: int
    vertex_circle_prune_count: int
    max_depth_reached: int
    vertex_circle_status_counts: dict[str, int]
    first_obstruction: dict[str, object] | None


def witness_order_for_row(center: int, witnesses: Sequence[int]) -> tuple[int, ...]:
    """Return witnesses in boundary order around a convex-hull vertex."""

    return tuple(sorted(witnesses, key=lambda witness: (witness - center) % N))


def strict_edges_for_row(
    center: int,
    witnesses: Sequence[int],
) -> tuple[StrictEdgeTemplate, ...]:
    """Generate row-circle nested interval inequalities for a rich support."""

    ordered = witness_order_for_row(center, witnesses)
    out: list[StrictEdgeTemplate] = []
    witness_count = len(ordered)
    for outer_start in range(witness_count):
        for outer_end in range(outer_start + 1, witness_count):
            for inner_start in range(witness_count):
                for inner_end in range(inner_start + 1, witness_count):
                    if (outer_start, outer_end) == (inner_start, inner_end):
                        continue
                    contains = (
                        outer_start <= inner_start
                        and inner_end <= outer_end
                        and (outer_start < inner_start or inner_end < outer_end)
                    )
                    if not contains:
                        continue
                    outer_pair = normalized_pair(
                        ordered[outer_start],
                        ordered[outer_end],
                    )
                    inner_pair = normalized_pair(
                        ordered[inner_start],
                        ordered[inner_end],
                    )
                    out.append(
                        StrictEdgeTemplate(
                            outer_pair_id=PAIR_TO_ID[outer_pair],
                            inner_pair_id=PAIR_TO_ID[inner_pair],
                            row=center,
                            witness_order=ordered,
                            outer_interval=(outer_start, outer_end),
                            inner_interval=(inner_start, inner_end),
                            outer_pair=outer_pair,
                            inner_pair=inner_pair,
                        )
                    )
    return tuple(out)


def prepare_catalogue(n: int = N) -> PreparedCatalogue:
    """Precompute support options and compatibility bitsets."""

    if n != N:
        raise ValueError("this checker is specialized to n=10")

    options: dict[tuple[int, int], tuple[RowOption, ...]] = {}
    pair_option_bits: dict[tuple[int, int], tuple[int, ...]] = {}
    full_domain: dict[tuple[int, int], int] = {}
    compatible_option_bits: dict[tuple[int, int, int, int], tuple[int, ...]] = {}

    for center in range(N):
        labels = tuple(label for label in range(N) if label != center)
        for support_size in SUPPORT_SIZES:
            row_options: list[RowOption] = []
            for row in combinations(labels, support_size):
                witness_pair_ids = tuple(
                    pair_id(left, right) for left, right in combinations(row, 2)
                )
                center_witness_pair_ids = tuple(pair_id(center, witness) for witness in row)
                row_options.append(
                    RowOption(
                        witnesses=tuple(row),
                        mask=support_mask(row),
                        witness_pair_ids=witness_pair_ids,
                        center_witness_pair_ids=center_witness_pair_ids,
                        strict_edges=strict_edges_for_row(center, row),
                    )
                )
            options[(center, support_size)] = tuple(row_options)
            full_domain[(center, support_size)] = (1 << len(row_options)) - 1

            option_bits = [0] * PAIR_COUNT
            for row_index, row_option in enumerate(row_options):
                bit = 1 << row_index
                for witness_pair_id in row_option.witness_pair_ids:
                    option_bits[witness_pair_id] |= bit
            pair_option_bits[(center, support_size)] = tuple(option_bits)

    for left, right in combinations(range(N), 2):
        for left_size in SUPPORT_SIZES:
            for right_size in SUPPORT_SIZES:
                left_to_right: list[int] = []
                right_to_left = [0] * len(options[(right, right_size)])
                for left_index, left_option in enumerate(options[(left, left_size)]):
                    bits = 0
                    for right_index, right_option in enumerate(
                        options[(right, right_size)]
                    ):
                        intersection_mask = left_option.mask & right_option.mask
                        intersection_size = intersection_mask.bit_count()
                        compatible = True
                        if intersection_size > 2:
                            compatible = False
                        elif intersection_size == 2:
                            shared = [
                                label
                                for label in range(N)
                                if (intersection_mask >> label) & 1
                            ]
                            compatible = chords_cross_in_natural_order(
                                (left, right),
                                (shared[0], shared[1]),
                            )
                        if compatible:
                            bits |= 1 << right_index
                            right_to_left[right_index] |= 1 << left_index
                    left_to_right.append(bits)
                compatible_option_bits[(left, left_size, right, right_size)] = tuple(
                    left_to_right
                )
                compatible_option_bits[(right, right_size, left, left_size)] = tuple(
                    right_to_left
                )

    return PreparedCatalogue(
        options=options,
        pair_option_bits=pair_option_bits,
        compatible_option_bits=compatible_option_bits,
        full_domain=full_domain,
    )


class UnionFind:
    """Small deterministic union-find on dense pair ids."""

    def __init__(self, size: int) -> None:
        self.parent = list(range(size))

    def find(self, item: int) -> int:
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def union(self, left: int, right: int) -> None:
        root_left = self.find(left)
        root_right = self.find(right)
        if root_left == root_right:
            return
        if root_right < root_left:
            root_left, root_right = root_right, root_left
        self.parent[root_right] = root_left


def selected_rows_to_json(
    selected: Sequence[tuple[int, int, int, RowOption]],
) -> dict[str, list[int]]:
    """Return a stable JSON object for a partial selected rich-row state."""

    return {
        str(center): list(row_option.witnesses)
        for center, _support_size, _row_index, row_option in sorted(selected)
    }


def strict_edge_to_json(edge: StrictEdgeTemplate, outer_class: int, inner_class: int) -> dict[str, object]:
    """Return a JSON-safe strict edge after quotienting."""

    return {
        "row": edge.row,
        "witness_order": list(edge.witness_order),
        "outer_interval": list(edge.outer_interval),
        "inner_interval": list(edge.inner_interval),
        "outer_pair": list(edge.outer_pair),
        "inner_pair": list(edge.inner_pair),
        "outer_class": list(ALL_PAIRS[outer_class]),
        "inner_class": list(ALL_PAIRS[inner_class]),
    }


def rich_vertex_circle_status(
    selected: Sequence[tuple[int, int, int, RowOption]],
) -> tuple[str, int, dict[str, object] | None]:
    """Replay the rich vertex-circle quotient gate on a partial assignment.

    Returns ``(status, scanned_strict_edges, first_edge)`` where status is one
    of ``ok``, ``self_edge``, or ``strict_cycle``.  The replay is intentionally
    self-contained rather than importing the main quotient helper, so it is a
    small implementation cross-check of the same quotient semantics.
    """

    union_find = UnionFind(PAIR_COUNT)
    for _center, _support_size, _row_index, row_option in selected:
        base = row_option.center_witness_pair_ids[0]
        for pair in row_option.center_witness_pair_ids[1:]:
            union_find.union(base, pair)

    strict_edges: list[tuple[int, int, StrictEdgeTemplate]] = []
    scanned_edges = 0
    for _center, _support_size, _row_index, row_option in selected:
        for edge in row_option.strict_edges:
            scanned_edges += 1
            outer_class = union_find.find(edge.outer_pair_id)
            inner_class = union_find.find(edge.inner_pair_id)
            if outer_class == inner_class:
                return (
                    "self_edge",
                    scanned_edges,
                    strict_edge_to_json(edge, outer_class, inner_class),
                )
            strict_edges.append((outer_class, inner_class, edge))

    graph: dict[int, list[tuple[int, StrictEdgeTemplate]]] = defaultdict(list)
    for outer_class, inner_class, edge in strict_edges:
        graph[outer_class].append((inner_class, edge))
    for source in graph:
        graph[source].sort(key=lambda item: (item[0], item[1].row, item[1].outer_pair, item[1].inner_pair))

    color: dict[int, int] = {}
    parent: dict[int, tuple[int, StrictEdgeTemplate] | None] = {}

    def dfs(node: int) -> dict[str, object] | None:
        color[node] = 1
        for next_node, edge in graph.get(node, []):
            next_color = color.get(next_node, 0)
            if next_color == 0:
                parent[next_node] = (node, edge)
                found = dfs(next_node)
                if found is not None:
                    return found
            elif next_color == 1:
                return strict_edge_to_json(edge, node, next_node)
        color[node] = 2
        return None

    for source in sorted(graph):
        if color.get(source, 0) == 0:
            parent[source] = None
            found_cycle_edge = dfs(source)
            if found_cycle_edge is not None:
                return "strict_cycle", scanned_edges, found_cycle_edge
    return "ok", scanned_edges, None


def search_size_five_subset(
    catalogue: PreparedCatalogue,
    size_five_centers: Sequence[int],
) -> SearchResult:
    """Search one dihedral q=2 center-set representative."""

    size_five_set = set(size_five_centers)
    support_sizes = tuple(5 if center in size_five_set else 4 for center in range(N))
    domains = tuple(
        catalogue.full_domain[(center, support_sizes[center])] for center in range(N)
    )
    pair_counts = [0] * PAIR_COUNT
    assigned: list[int | None] = [None] * N
    selected: list[tuple[int, int, int, RowOption]] = []
    nodes_visited = 0
    dead_end_count = 0
    vertex_circle_prune_count = 0
    max_depth_reached = 0
    status_counts: Counter[str] = Counter()
    first_obstruction: dict[str, object] | None = None

    def recurse(depth: int, assigned_mask: int, current_domains: tuple[int, ...]) -> bool:
        nonlocal dead_end_count
        nonlocal first_obstruction
        nonlocal max_depth_reached
        nonlocal nodes_visited
        nonlocal vertex_circle_prune_count

        max_depth_reached = max(max_depth_reached, depth)
        if depth == N:
            return True

        best_center: int | None = None
        best_count: int | None = None
        for center in range(N):
            if (assigned_mask >> center) & 1:
                continue
            option_count = current_domains[center].bit_count()
            if best_count is None or option_count < best_count:
                best_center = center
                best_count = option_count
            if option_count == 0:
                break

        if best_center is None:
            return True
        if best_count == 0:
            dead_end_count += 1
            return False

        center = best_center
        center_size = support_sizes[center]
        for option_index in iter_bits(current_domains[center]):
            nodes_visited += 1
            row_option = catalogue.options[(center, center_size)][option_index]
            newly_saturated: list[PairId] = []
            for witness_pair_id in row_option.witness_pair_ids:
                old_count = pair_counts[witness_pair_id]
                if old_count >= 2:
                    raise AssertionError("domain allowed an already saturated pair")
                pair_counts[witness_pair_id] = old_count + 1
                if old_count + 1 == 2:
                    newly_saturated.append(witness_pair_id)

            new_domains = list(current_domains)
            new_domains[center] = 1 << option_index
            new_assigned_mask = assigned_mask | (1 << center)
            empty_domain = False
            for other_center in range(N):
                if (new_assigned_mask >> other_center) & 1:
                    continue
                other_size = support_sizes[other_center]
                domain = new_domains[other_center]
                domain &= catalogue.compatible_option_bits[
                    (center, center_size, other_center, other_size)
                ][option_index]
                for pair in newly_saturated:
                    domain &= ~catalogue.pair_option_bits[(other_center, other_size)][pair]
                new_domains[other_center] = domain
                if domain == 0:
                    empty_domain = True
                    break

            assigned[center] = option_index
            selected.append((center, center_size, option_index, row_option))
            if empty_domain:
                dead_end_count += 1
                found = False
            else:
                status, scanned_strict_edges, first_edge = rich_vertex_circle_status(selected)
                if status != "ok":
                    vertex_circle_prune_count += 1
                    status_counts[status] += 1
                    if first_obstruction is None:
                        first_obstruction = {
                            "status": status,
                            "partial_row_count": len(selected),
                            "partial_rows": selected_rows_to_json(selected),
                            "strict_edges_scanned_before_obstruction": scanned_strict_edges,
                            "first_edge": first_edge,
                        }
                    found = False
                else:
                    found = recurse(
                        depth + 1,
                        new_assigned_mask,
                        tuple(new_domains),
                    )
            selected.pop()
            assigned[center] = None
            for witness_pair_id in row_option.witness_pair_ids:
                pair_counts[witness_pair_id] -= 1
            if found:
                return True
        return False

    found_clean = recurse(0, 0, domains)
    return SearchResult(
        found_clean_complete_assignment=found_clean,
        nodes_visited=nodes_visited,
        dead_end_count=dead_end_count,
        vertex_circle_prune_count=vertex_circle_prune_count,
        max_depth_reached=max_depth_reached,
        vertex_circle_status_counts=dict(sorted(status_counts.items())),
        first_obstruction=first_obstruction,
    )


def representative_key(representative: Sequence[int]) -> str:
    """Return a compact stable key for a representative."""

    return ",".join(str(item) for item in representative)


def search_result_to_json(
    representative: Sequence[int],
    result: SearchResult,
) -> dict[str, object]:
    """Return a JSON-safe representative search result."""

    return {
        "size_five_centers": list(representative),
        "found_clean_complete_assignment": result.found_clean_complete_assignment,
        "nodes_visited": result.nodes_visited,
        "dead_end_count": result.dead_end_count,
        "vertex_circle_prune_count": result.vertex_circle_prune_count,
        "max_depth_reached": result.max_depth_reached,
        "vertex_circle_status_counts": result.vertex_circle_status_counts,
        "first_obstruction": result.first_obstruction,
    }


def run_q2_search() -> dict[str, object]:
    """Run the complete q=2 search and return deterministic summaries."""

    catalogue = prepare_catalogue(N)
    representative_results: dict[str, object] = {}
    aggregate_status_counts: Counter[str] = Counter()
    total_nodes = 0
    total_dead_ends = 0
    total_vertex_prunes = 0
    max_depth = 0
    complete_assignments_found = 0

    for representative in dihedral_representatives(Q, N):
        result = search_size_five_subset(catalogue, representative)
        key = representative_key(representative)
        representative_results[key] = search_result_to_json(representative, result)
        total_nodes += result.nodes_visited
        total_dead_ends += result.dead_end_count
        total_vertex_prunes += result.vertex_circle_prune_count
        max_depth = max(max_depth, result.max_depth_reached)
        if result.found_clean_complete_assignment:
            complete_assignments_found += 1
        aggregate_status_counts.update(result.vertex_circle_status_counts)

    return {
        "representative_results": representative_results,
        "summary": {
            "representatives_checked": len(representative_results),
            "complete_assignments_found": complete_assignments_found,
            "total_nodes_visited": total_nodes,
            "total_dead_end_count": total_dead_ends,
            "total_vertex_circle_prune_count": total_vertex_prunes,
            "max_depth_reached": max_depth,
            "vertex_circle_status_counts": dict(sorted(aggregate_status_counts.items())),
        },
    }


def build_payload() -> dict[str, object]:
    """Build the checked artifact payload."""

    search = run_q2_search()
    summary = search["summary"]
    assert isinstance(summary, Mapping)
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": (
            "Generator-independent n=10 q=2 four/five rich-support diagnostic. "
            "It checks all five dihedral center-set representatives with exactly "
            "two size-five supports under the row-pair cap, two-overlap crossing, "
            "witness-pair capacity, and monotone rich vertex-circle quotient "
            "pruning. It finds no clean complete assignment. This does not prove "
            "n=10, does not prove Erdos Problem #97, and is not a counterexample."
        ),
        "summary": {
            "n": N,
            "order": list(ORDER),
            "support_sizes": list(SUPPORT_SIZES),
            "size_five_center_count": Q,
            **summary,
            "max_size_five_centers_surviving_support_plus_vertex_circle_filters": 1,
            "min_exact_four_only_centers_surviving_support_plus_vertex_circle_filters": 9,
        },
        "representative_results": search["representative_results"],
        "filters": [
            {
                "name": "row_pair_cap",
                "meaning": (
                    "Two distinct distance circles can share at most two witness "
                    "vertices."
                ),
            },
            {
                "name": "two_overlap_crossing",
                "meaning": (
                    "When two rich supports share exactly two witnesses, the "
                    "center chord and shared-witness chord must cross in the "
                    "cyclic order."
                ),
            },
            {
                "name": "witness_pair_capacity",
                "meaning": (
                    "Any unordered witness pair can occur together in rich "
                    "supports at at most two centers."
                ),
            },
            {
                "name": "rich_vertex_circle_quotient",
                "meaning": (
                    "For each rich class, union all center-witness distances "
                    "inside the class and add all nested-interval strict "
                    "distance inequalities from the full witness set. A self-edge "
                    "or directed strict cycle is an obstruction."
                ),
            },
        ],
        "support_rule": {
            "rule": (
                "Exactly two centers are represented by size-five same-radius "
                "supports. The other eight centers are represented by exact-four "
                "supports."
            ),
            "dihedral_reduction": (
                "The natural cyclic order fixes labels 0..9. The set of two "
                "size-five centers is reduced by cyclic rotations and reflection; "
                "support choices are still labelled for each representative."
            ),
            "monotonicity_note": (
                "The vertex-circle quotient obstruction is monotone under adding "
                "rows: an existing self-edge or strict cycle remains obstructive, "
                "possibly after quotient classes merge."
            ),
            "combined_consequence_note": (
                "The at-most-one size-five support consequence combines this q=2 "
                "closure with the existing n10_mixed_rich_support_capacity "
                "artifact, which closes q=3..7 under weaker support filters. This "
                "checker itself exhausts exactly the q=2 layer."
            ),
        },
        "interpretation_warnings": [
            "This is a necessary support/quotient diagnostic only.",
            "It does not replay turn inequalities, Kalmanson certificates, or Euclidean realizability.",
            "It leaves the q=0 and q=1 four/five support cases to stronger filters.",
            "No n=10 theorem, general proof, or counterexample is claimed.",
        ],
        "provenance": {
            "generator": "scripts/check_n10_q2_rich_vertex_circle.py",
            "command": (
                "python scripts/check_n10_q2_rich_vertex_circle.py "
                "--write --assert-expected"
            ),
            "related_artifacts": [
                "data/certificates/n10_mixed_rich_support_capacity.json",
                "docs/n10-mixed-rich-support-capacity.md",
                "src/erdos97/vertex_circle_quotient_replay.py",
            ],
        },
    }


def assert_expected_payload(payload: Mapping[str, object]) -> None:
    """Assert stable expected q=2 closure counts."""

    if payload.get("schema") != SCHEMA:
        raise AssertionError(f"unexpected schema: {payload.get('schema')!r}")
    if payload.get("status") != STATUS:
        raise AssertionError(f"unexpected status: {payload.get('status')!r}")
    if payload.get("trust") != TRUST:
        raise AssertionError(f"unexpected trust: {payload.get('trust')!r}")

    summary = payload.get("summary")
    if not isinstance(summary, Mapping):
        raise AssertionError("summary is missing")
    for key, expected in EXPECTED_AGGREGATE.items():
        if summary.get(key) != expected:
            raise AssertionError(
                f"summary[{key!r}] is {summary.get(key)!r}, expected {expected!r}"
            )
    if summary.get("max_size_five_centers_surviving_support_plus_vertex_circle_filters") != 1:
        raise AssertionError("expected at most one surviving size-five center")
    if summary.get("min_exact_four_only_centers_surviving_support_plus_vertex_circle_filters") != 9:
        raise AssertionError("expected at least nine exact-four-only centers")

    representative_results = payload.get("representative_results")
    if not isinstance(representative_results, Mapping):
        raise AssertionError("representative_results is missing")
    for key, expected_items in EXPECTED_REP_SUMMARIES.items():
        item = representative_results.get(key)
        if not isinstance(item, Mapping):
            raise AssertionError(f"missing representative {key}")
        if item.get("found_clean_complete_assignment") is not False:
            raise AssertionError(f"representative {key} unexpectedly has a clean assignment")
        for expected_key, expected in expected_items.items():
            if item.get(expected_key) != expected:
                raise AssertionError(
                    f"representative {key} key {expected_key!r} is "
                    f"{item.get(expected_key)!r}, expected {expected!r}"
                )


def compare_artifact(payload: Mapping[str, object], path: Path) -> None:
    """Compare a checked artifact with a freshly built payload."""

    checked = json.loads(path.read_text(encoding="utf-8"))
    if checked != payload:
        raise AssertionError(f"checked artifact is stale: {path.relative_to(ROOT)}")


def print_summary(payload: Mapping[str, object]) -> None:
    """Print a compact human-readable summary."""

    summary = payload["summary"]
    assert isinstance(summary, Mapping)
    print("n=10 q=2 rich vertex-circle closure diagnostic")
    print(f"claim scope: {payload['claim_scope']}")
    print(f"representatives checked: {summary['representatives_checked']}")
    print(f"clean complete assignments found: {summary['complete_assignments_found']}")
    print(
        "max size-five centers surviving support + vertex-circle filters: "
        f"{summary['max_size_five_centers_surviving_support_plus_vertex_circle_filters']}"
    )
    print(
        "minimum exact-four-only centers after this filter layer: "
        f"{summary['min_exact_four_only_centers_surviving_support_plus_vertex_circle_filters']}"
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--write", action="store_true", help="write the artifact")
    parser.add_argument("--check", action="store_true", help="compare the artifact")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true", help="print full JSON")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    payload = build_payload()
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
