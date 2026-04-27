"""Exact vertex-circle cyclic-order filter for selected-witness patterns."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Sequence

from erdos97.cyclic_crossing_csp import crossing_constraints
from erdos97.incidence_filters import Chord, chords_cross_in_order

Pair = tuple[int, int]
StrictEdge = tuple[Pair, Pair]
Constraint = tuple[Chord, Chord]


def pair(u: int, v: int) -> Pair:
    """Return a normalized unordered pair. Reject loops."""
    if u == v:
        raise ValueError(f"loop pair is not allowed: ({u}, {v})")
    return (u, v) if u < v else (v, u)


class UnionFind:
    """Small deterministic union-find over unordered vertex pairs."""

    def __init__(self, items: Sequence[Pair]) -> None:
        self.parent = {item: item for item in items}

    def find(self, item: Pair) -> Pair:
        if item not in self.parent:
            self.parent[item] = item
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def union(self, a: Pair, b: Pair) -> None:
        root_a = self.find(a)
        root_b = self.find(b)
        if root_a == root_b:
            return
        if root_b < root_a:
            root_a, root_b = root_b, root_a
        self.parent[root_b] = root_a


@dataclass(frozen=True)
class StrictInequality:
    row: int
    witness_order: list[int]
    outer_interval: list[int]
    inner_interval: list[int]
    outer_pair: Pair
    inner_pair: Pair
    outer_class: Pair
    inner_class: Pair


@dataclass(frozen=True)
class VertexCircleOrderResult:
    pattern: str
    n: int
    order: list[int]
    row_count_completed: int
    strict_edge_count: int
    self_edge_conflicts: list[StrictInequality]
    cycle_edges: list[StrictInequality]
    obstructed: bool


@dataclass(frozen=True)
class VertexCircleSearchResult:
    pattern: str
    n: int
    crossing_constraints: list[Constraint]
    symmetry_normalization: list[list[int]]
    sat: bool
    order: list[int] | None
    nodes_visited: int
    max_depth: int
    crossing_prunes: int
    vertex_circle_prunes: int
    terminal_conflicts: list[dict[str, object]]
    terminal_conflicts_truncated: bool


def _all_pairs(n: int) -> list[Pair]:
    return [(u, v) for u in range(n) for v in range(u + 1, n)]


def _validate_order(order: Sequence[int], n: int, require_full: bool) -> None:
    seen: set[int] = set()
    for label in order:
        if label in seen:
            raise ValueError(f"cyclic order is not a permutation: repeated label {label}")
        if label < 0 or label >= n:
            raise ValueError(f"cyclic order label out of range: {label}")
        seen.add(label)
    if require_full and seen != set(range(n)):
        missing = sorted(set(range(n)) - seen)
        extra = sorted(seen - set(range(n)))
        raise ValueError(f"cyclic order is not complete; missing={missing}, extra={extra}")


def _distance_class_union_find(S: Sequence[Sequence[int]]) -> UnionFind:
    n = len(S)
    uf = UnionFind(_all_pairs(n))
    for center, row in enumerate(S):
        if len(row) != 4:
            raise ValueError(f"row {center} has length {len(row)}, expected 4")
        base = pair(center, row[0])
        for witness in row[1:]:
            uf.union(base, pair(center, witness))
    return uf


def angular_witness_order(
    order: Sequence[int],
    center: int,
    witnesses: Sequence[int],
) -> list[int]:
    """Return witnesses in angular order around a convex-hull vertex center.

    For a strict convex polygon, the angular order around a hull vertex is the
    cyclic boundary order with the center removed, up to reversal. Reversal
    preserves interval-containment relations.
    """
    n = len(order)
    positions = {label: idx for idx, label in enumerate(order)}
    if center not in positions:
        raise ValueError(f"center {center} is missing from cyclic order")
    missing = [witness for witness in witnesses if witness not in positions]
    if missing:
        raise ValueError(f"witness {missing[0]} is missing from cyclic order")
    center_pos = positions[center]
    return sorted(witnesses, key=lambda witness: (positions[witness] - center_pos) % n)


def vertex_circle_strict_inequalities(
    S: Sequence[Sequence[int]],
    order: Sequence[int],
    placed: set[int] | None = None,
) -> tuple[list[StrictInequality], int]:
    """Return strict distance-class inequalities from completed rows.

    If ``placed`` is supplied, only rows whose center and four witnesses are in
    ``placed`` are considered. This is the safe pruning condition used by the
    insertion search.
    """
    n = len(S)
    _validate_order(order, n, require_full=placed is None)
    if placed is None:
        placed = set(order)

    uf = _distance_class_union_find(S)
    strict_edges: list[StrictInequality] = []
    completed_rows = 0
    for center, row in enumerate(S):
        row_labels = set(row) | {center}
        if not row_labels <= placed:
            continue
        completed_rows += 1
        witnesses = angular_witness_order(order, center, row)
        for outer_start in range(4):
            for outer_end in range(outer_start + 1, 4):
                for inner_start in range(4):
                    for inner_end in range(inner_start + 1, 4):
                        if (outer_start, outer_end) == (inner_start, inner_end):
                            continue
                        contains = (
                            outer_start <= inner_start
                            and inner_end <= outer_end
                            and (outer_start < inner_start or inner_end < outer_end)
                        )
                        if not contains:
                            continue
                        outer_pair = pair(witnesses[outer_start], witnesses[outer_end])
                        inner_pair = pair(witnesses[inner_start], witnesses[inner_end])
                        strict_edges.append(
                            StrictInequality(
                                row=center,
                                witness_order=list(witnesses),
                                outer_interval=[outer_start, outer_end],
                                inner_interval=[inner_start, inner_end],
                                outer_pair=outer_pair,
                                inner_pair=inner_pair,
                                outer_class=uf.find(outer_pair),
                                inner_class=uf.find(inner_pair),
                            )
                        )
    return strict_edges, completed_rows


def _find_strict_cycle(edges: Sequence[StrictInequality]) -> list[StrictInequality]:
    graph: dict[Pair, list[StrictInequality]] = defaultdict(list)
    for edge in edges:
        if edge.outer_class != edge.inner_class:
            graph[edge.outer_class].append(edge)
    for source in graph:
        graph[source].sort(key=lambda edge: (edge.inner_class, edge.row, edge.outer_pair, edge.inner_pair))

    color: dict[Pair, int] = {}
    parent: dict[Pair, tuple[Pair, StrictInequality] | None] = {}

    def dfs(node: Pair) -> list[StrictInequality]:
        color[node] = 1
        for edge in graph.get(node, []):
            nxt = edge.inner_class
            nxt_color = color.get(nxt, 0)
            if nxt_color == 0:
                parent[nxt] = (node, edge)
                found = dfs(nxt)
                if found:
                    return found
            elif nxt_color == 1:
                path_edges: list[StrictInequality] = []
                cur = node
                while cur != nxt:
                    parent_item = parent[cur]
                    if parent_item is None:  # pragma: no cover - defensive
                        break
                    prev, parent_edge = parent_item
                    path_edges.append(parent_edge)
                    cur = prev
                return list(reversed(path_edges)) + [edge]
        color[node] = 2
        return []

    for node in sorted(graph):
        if color.get(node, 0) == 0:
            parent[node] = None
            found = dfs(node)
            if found:
                return found
    return []


def _partial_vertex_circle_result(
    S: Sequence[Sequence[int]],
    order: Sequence[int],
    placed: set[int],
) -> tuple[bool, list[StrictInequality], list[StrictInequality], int, int]:
    edges, completed_rows = vertex_circle_strict_inequalities(S, order, placed)
    self_edges = [edge for edge in edges if edge.outer_class == edge.inner_class]
    cycle_edges = [] if self_edges else _find_strict_cycle(edges)
    return bool(self_edges or cycle_edges), self_edges, cycle_edges, len(edges), completed_rows


def vertex_circle_order_obstruction(
    S: Sequence[Sequence[int]],
    order: Sequence[int],
    pattern: str = "",
) -> VertexCircleOrderResult:
    """Check whether one full cyclic order is killed by the vertex-circle filter."""
    n = len(S)
    _validate_order(order, n, require_full=True)
    placed = set(order)
    obstructed, self_edges, cycle_edges, edge_count, completed_rows = _partial_vertex_circle_result(
        S,
        order,
        placed,
    )
    return VertexCircleOrderResult(
        pattern=pattern,
        n=n,
        order=list(order),
        row_count_completed=completed_rows,
        strict_edge_count=edge_count,
        self_edge_conflicts=self_edges,
        cycle_edges=cycle_edges,
        obstructed=obstructed,
    )


def _constraint_labels(constraint: Constraint) -> set[int]:
    return set(constraint[0]) | set(constraint[1])


def _initial_orders(constraints: Sequence[Constraint], n: int) -> list[list[int]]:
    if not constraints:
        return [[0] if n else []]
    source, target = constraints[0]
    return [
        [source[0], target[0], source[1], target[1]],
        [source[0], target[1], source[1], target[0]],
    ]


def find_cyclic_order_with_vertex_circle_filter(
    S: Sequence[Sequence[int]],
    pattern: str = "",
    max_terminal_conflicts: int | None = 128,
) -> VertexCircleSearchResult:
    """Search for a cyclic order satisfying crossing and vertex-circle filters."""
    n = len(S)
    if max_terminal_conflicts is not None and max_terminal_conflicts < 0:
        raise ValueError("max_terminal_conflicts must be nonnegative or None")

    constraints = crossing_constraints(S)
    labels = set(range(n))
    constraint_label_sets = [_constraint_labels(constraint) for constraint in constraints]
    label_to_constraints: dict[int, list[int]] = {label: [] for label in labels}
    for idx, labels_for_constraint in enumerate(constraint_label_sets):
        for label in labels_for_constraint:
            label_to_constraints[label].append(idx)

    row_label_sets = [set(row) | {center} for center, row in enumerate(S)]
    label_to_rows: dict[int, list[int]] = {label: [] for label in labels}
    for row_idx, labels_for_row in enumerate(row_label_sets):
        for label in labels_for_row:
            label_to_rows[label].append(row_idx)

    nodes_visited = 0
    max_depth = 0
    crossing_prunes = 0
    vertex_circle_prunes = 0
    terminal_conflicts: list[dict[str, object]] = []
    terminal_conflicts_truncated = False

    def completed_crossing_failure(
        order: Sequence[int],
        placed: set[int],
        affected_labels: set[int] | None = None,
    ) -> int | None:
        if affected_labels is None:
            candidate_idxs = range(len(constraints))
        else:
            idxs: set[int] = set()
            for label in affected_labels:
                idxs.update(label_to_constraints[label])
            candidate_idxs = sorted(idxs)
        for idx in candidate_idxs:
            if constraint_label_sets[idx] <= placed:
                source, target = constraints[idx]
                if not chords_cross_in_order(source, target, order):
                    return idx
        return None

    def vertex_circle_failure(
        order: Sequence[int],
        placed: set[int],
    ) -> dict[str, object] | None:
        obstructed, self_edges, cycle_edges, edge_count, completed_rows = _partial_vertex_circle_result(
            S,
            order,
            placed,
        )
        if not obstructed:
            return None
        reason_edges = self_edges if self_edges else cycle_edges
        return {
            "completed_rows": completed_rows,
            "strict_edge_count": edge_count,
            "self_edge_conflicts": [_json_inequality(edge) for edge in self_edges],
            "cycle_edges": [_json_inequality(edge) for edge in reason_edges],
        }

    def choose_label(placed: set[int]) -> int:
        def score(label: int) -> tuple[int, int, int, int, int, int]:
            crossing_touches = [
                len(constraint_label_sets[idx] & placed)
                for idx in label_to_constraints[label]
            ]
            row_touches = [
                len(row_label_sets[idx] & placed)
                for idx in label_to_rows[label]
            ]
            return (
                sum(count == 3 for count in crossing_touches),
                sum(count == 4 for count in row_touches),
                sum(count == 2 for count in crossing_touches),
                sum(count == 3 for count in row_touches),
                len(label_to_constraints[label]) + len(label_to_rows[label]),
                -label,
            )

        return max(labels - placed, key=score)

    def search(order: list[int], placed: set[int]) -> list[int] | None:
        nonlocal nodes_visited
        nonlocal max_depth
        nonlocal crossing_prunes
        nonlocal vertex_circle_prunes
        nonlocal terminal_conflicts_truncated
        nodes_visited += 1
        max_depth = max(max_depth, len(placed))
        if len(placed) == n:
            if completed_crossing_failure(order, placed) is not None:
                return None
            return order if vertex_circle_failure(order, placed) is None else None

        label = choose_label(placed)
        gap_conflicts: list[dict[str, object]] = []
        tried_valid_child = False
        for position in range(1, len(order) + 1):
            candidate_order = order[:position] + [label] + order[position:]
            candidate_placed = placed | {label}
            failed_idx = completed_crossing_failure(candidate_order, candidate_placed, {label})
            if failed_idx is not None:
                crossing_prunes += 1
                gap_conflicts.append(
                    {
                        "insert_position": position,
                        "gap_after": int(candidate_order[position - 1]),
                        "type": "crossing",
                        "constraint": _json_constraint(constraints[failed_idx]),
                    }
                )
                continue

            vertex_reason = vertex_circle_failure(candidate_order, candidate_placed)
            if vertex_reason is not None:
                vertex_circle_prunes += 1
                gap_conflicts.append(
                    {
                        "insert_position": position,
                        "gap_after": int(candidate_order[position - 1]),
                        "type": "vertex_circle",
                        "reason": vertex_reason,
                    }
                )
                continue

            tried_valid_child = True
            found = search(candidate_order, candidate_placed)
            if found is not None:
                return found

        if not tried_valid_child:
            if (
                max_terminal_conflicts is not None
                and len(terminal_conflicts) >= max_terminal_conflicts
            ):
                terminal_conflicts_truncated = True
                return None
            terminal_conflicts.append(
                {
                    "partial_order": [int(label) for label in order],
                    "blocked_label": int(label),
                    "reasons": gap_conflicts,
                }
            )
        return None

    normalizations = _initial_orders(constraints, n)
    for initial_order in normalizations:
        found = search(initial_order, set(initial_order))
        if found is not None:
            return VertexCircleSearchResult(
                pattern=pattern,
                n=n,
                crossing_constraints=constraints,
                symmetry_normalization=normalizations,
                sat=True,
                order=found,
                nodes_visited=nodes_visited,
                max_depth=max_depth,
                crossing_prunes=crossing_prunes,
                vertex_circle_prunes=vertex_circle_prunes,
                terminal_conflicts=[],
                terminal_conflicts_truncated=False,
            )

    return VertexCircleSearchResult(
        pattern=pattern,
        n=n,
        crossing_constraints=constraints,
        symmetry_normalization=normalizations,
        sat=False,
        order=None,
        nodes_visited=nodes_visited,
        max_depth=max_depth,
        crossing_prunes=crossing_prunes,
        vertex_circle_prunes=vertex_circle_prunes,
        terminal_conflicts=terminal_conflicts,
        terminal_conflicts_truncated=terminal_conflicts_truncated,
    )


def _json_pair(item: Pair) -> list[int]:
    return [int(item[0]), int(item[1])]


def _json_constraint(constraint: Constraint) -> dict[str, list[int]]:
    return {
        "source": _json_pair(constraint[0]),
        "target": _json_pair(constraint[1]),
    }


def _json_inequality(edge: StrictInequality) -> dict[str, object]:
    return {
        "row": int(edge.row),
        "witness_order": [int(label) for label in edge.witness_order],
        "outer_interval": [int(idx) for idx in edge.outer_interval],
        "inner_interval": [int(idx) for idx in edge.inner_interval],
        "outer_pair": _json_pair(edge.outer_pair),
        "inner_pair": _json_pair(edge.inner_pair),
        "outer_class": _json_pair(edge.outer_class),
        "inner_class": _json_pair(edge.inner_class),
    }


def order_result_to_json(result: VertexCircleOrderResult) -> dict[str, object]:
    """Return a JSON-serializable fixed-order result."""
    return {
        "type": "vertex_circle_order_result",
        "pattern": result.pattern,
        "n": result.n,
        "order": result.order,
        "row_count_completed": result.row_count_completed,
        "strict_edge_count": result.strict_edge_count,
        "self_edge_conflicts": [
            _json_inequality(edge) for edge in result.self_edge_conflicts
        ],
        "cycle": bool(result.cycle_edges),
        "cycle_edges": [_json_inequality(edge) for edge in result.cycle_edges],
        "obstructed": result.obstructed,
    }


def search_result_to_json(result: VertexCircleSearchResult) -> dict[str, object]:
    """Return a JSON-serializable search result."""
    return {
        "type": "vertex_circle_order_search_result",
        "pattern": result.pattern,
        "n": result.n,
        "crossing_constraints": [
            _json_constraint(constraint) for constraint in result.crossing_constraints
        ],
        "crossing_constraint_count": len(result.crossing_constraints),
        "symmetry_normalization": result.symmetry_normalization,
        "result": "SAT" if result.sat else "UNSAT",
        "sat": result.sat,
        "order": result.order,
        "nodes_visited": result.nodes_visited,
        "max_depth": result.max_depth,
        "crossing_prunes": result.crossing_prunes,
        "vertex_circle_prunes": result.vertex_circle_prunes,
        "terminal_conflicts": result.terminal_conflicts,
        "terminal_conflicts_truncated": result.terminal_conflicts_truncated,
    }
