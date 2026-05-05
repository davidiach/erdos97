"""Minimum-radius short-chord filter for selected-witness patterns.

This module is exact finite combinatorics. It does not use coordinates,
floating point arithmetic, or numerical optimization.

The geometric input is the following necessary condition. Let ``r_i`` be the
selected radius at center ``i``. If ``i`` has globally minimum selected radius,
then the four selected witnesses around ``i`` must have at least one adjacent
angular pair ``{a,b}`` such that neither endpoint selects the other. Otherwise
the short pair forced by the four witnesses in an angle smaller than ``pi``
would be a selected edge of smaller radius, contradicting minimality of
``r_i``.

The filter is intentionally weak: passing it is not evidence for realizability.
It is useful mainly as a cheap way to record and test the minimum-radius idea.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, permutations
from math import prod
from typing import Sequence

Pair = tuple[int, int]
DirectedEdge = tuple[int, int]
Pattern = Sequence[Sequence[int]]


@dataclass(frozen=True)
class MinRadiusRowResult:
    """Minimum-radius status for one potential minimum center."""

    center: int
    witness_order: list[int]
    consecutive_pairs: list[Pair]
    covered_consecutive_pairs: list[Pair]
    uncovered_consecutive_pairs: list[Pair]
    blocked: bool


@dataclass(frozen=True)
class MinRadiusOrderResult:
    """Minimum-radius status for a fixed cyclic order."""

    pattern: str
    n: int
    order: list[int]
    rows: list[MinRadiusRowResult]
    blocked_centers: list[int]
    possible_min_centers: list[int]
    order_free_blocked_centers: list[int]
    order_free_empty_gap_centers: list[int]
    obstructed: bool


@dataclass(frozen=True)
class RadiusPropagationChoice:
    """One selected short-gap choice and its forced radius inequalities."""

    center: int
    consecutive_pair: Pair
    selected_sources: list[int]
    inequality_edges: list[DirectedEdge]


@dataclass(frozen=True)
class RadiusPropagationResult:
    """Exact fixed-order radius-propagation search result."""

    pattern: str
    n: int
    order: list[int]
    status: str
    obstructed: bool | None
    short_gap_choice_count: int
    nodes_visited: int
    max_depth: int
    search_truncated: bool
    acyclic_choice: list[RadiusPropagationChoice] | None


def pair(a: int, b: int) -> Pair:
    """Return a normalized unordered pair. Reject loops."""

    _reject_loop(a, b)
    return (a, b) if a < b else (b, a)


def _reject_loop(a: int, b: int) -> None:
    if a == b:
        raise ValueError(f"loop pair is not allowed: ({a}, {b})")


def _validate_pattern(S: Pattern) -> None:
    n = len(S)
    for center, row in enumerate(S):
        if len(row) != 4:
            raise ValueError(f"row {center} has length {len(row)}, expected 4")
        if len(set(row)) != 4:
            raise ValueError(f"row {center} has repeated witnesses: {list(row)}")
        if center in row:
            raise ValueError(f"row {center} contains its own center")
        for label in row:
            if label < 0 or label >= n:
                raise ValueError(f"row {center} contains out-of-range label {label}")


def _positions(order: Sequence[int], n: int, require_full: bool = True) -> dict[int, int]:
    pos: dict[int, int] = {}
    for idx, label in enumerate(order):
        if label in pos:
            raise ValueError(f"cyclic order is not a permutation: repeated label {label}")
        if label < 0 or label >= n:
            raise ValueError(f"cyclic order label out of range: {label}")
        pos[label] = idx
    if require_full and set(pos) != set(range(n)):
        missing = sorted(set(range(n)) - set(pos))
        raise ValueError(f"cyclic order is incomplete; missing={missing}")
    return pos


def selected_pair_sources(S: Pattern, a: int, b: int) -> list[int]:
    """Return endpoints among ``a,b`` whose selected row contains the other endpoint."""

    _validate_pattern(S)
    n = len(S)
    if a < 0 or a >= n or b < 0 or b >= n:
        raise ValueError(f"pair labels out of range: ({a}, {b})")
    _reject_loop(a, b)

    return _selected_pair_sources(S, a, b)


def _selected_pair_sources(S: Pattern, a: int, b: int) -> list[int]:
    """Return selected pair sources for a validated pattern and pair."""

    sources: list[int] = []
    if b in S[a]:
        sources.append(a)
    if a in S[b]:
        sources.append(b)
    return sources


def angular_witness_order(
    order: Sequence[int],
    center: int,
    witnesses: Sequence[int],
) -> list[int]:
    """Return witnesses in angular order around a convex-hull vertex center.

    For a strictly convex polygon, the angular order around a hull vertex is the
    boundary order with the center removed, up to reversal. Reversal does not
    change which witness pairs are consecutive.
    """

    n = len(order)
    pos = _positions(order, n, require_full=True)
    return _angular_witness_order_from_positions(pos, n, center, witnesses)


def _angular_witness_order_from_positions(
    pos: dict[int, int],
    n: int,
    center: int,
    witnesses: Sequence[int],
) -> list[int]:
    """Return witness order using prevalidated cyclic-order positions."""

    if center not in pos:
        raise ValueError(f"center {center} is missing from cyclic order")
    missing = [witness for witness in witnesses if witness not in pos]
    if missing:
        raise ValueError(f"witness {missing[0]} is missing from cyclic order")
    center_pos = pos[center]
    return sorted(witnesses, key=lambda witness: (pos[witness] - center_pos) % n)


def consecutive_witness_pairs(
    order: Sequence[int],
    center: int,
    witnesses: Sequence[int],
) -> list[Pair]:
    """Return the three linear consecutive witness pairs around ``center``.

    There is no wraparound pair. The four witnesses lie in the open interior
    cone at ``center``, whose angular width is smaller than ``pi``.
    """

    witness_order = angular_witness_order(order, center, witnesses)
    return _consecutive_witness_pairs(witness_order)


def _consecutive_witness_pairs(witness_order: Sequence[int]) -> list[Pair]:
    """Return the three non-wrapping consecutive pairs in witness order."""

    return [pair(a, b) for a, b in zip(witness_order, witness_order[1:])]


def minimum_radius_row_result(
    S: Pattern,
    order: Sequence[int],
    center: int,
) -> MinRadiusRowResult:
    """Return the minimum-radius filter status for one center in one order."""

    _validate_pattern(S)
    n = len(S)
    pos = _positions(order, n, require_full=True)
    if center < 0 or center >= n:
        raise ValueError(f"center out of range: {center}")

    return _minimum_radius_row_result(S, pos, center)


def _minimum_radius_row_result(
    S: Pattern,
    pos: dict[int, int],
    center: int,
) -> MinRadiusRowResult:
    """Return row status for a validated pattern and cyclic order."""

    witness_order = _angular_witness_order_from_positions(pos, len(S), center, S[center])
    consecutive = _consecutive_witness_pairs(witness_order)
    covered = [item for item in consecutive if _selected_pair_sources(S, *item)]
    uncovered = [item for item in consecutive if not _selected_pair_sources(S, *item)]
    return MinRadiusRowResult(
        center=center,
        witness_order=witness_order,
        consecutive_pairs=consecutive,
        covered_consecutive_pairs=covered,
        uncovered_consecutive_pairs=uncovered,
        blocked=not uncovered,
    )


def row_is_order_free_blocked(S: Pattern, center: int) -> bool:
    """Return True iff ``center`` is blocked for every cyclic order.

    This happens exactly when every pair among the four witnesses is selected in
    at least one direction. Then whatever the angular order is, all three
    consecutive witness pairs are covered, so ``center`` cannot have the global
    minimum selected radius.
    """

    _validate_pattern(S)
    if center < 0 or center >= len(S):
        raise ValueError(f"center out of range: {center}")
    return _row_is_order_free_blocked(S, center)


def _row_is_order_free_blocked(S: Pattern, center: int) -> bool:
    """Return order-free status for a validated pattern."""

    return all(_selected_pair_sources(S, a, b) for a, b in combinations(S[center], 2))


def covered_witness_path_orders(S: Pattern, center: int) -> list[list[int]]:
    """Return witness orders whose three consecutive pairs are all covered.

    Equivalently, these are Hamiltonian paths in the covered-pair graph on the
    four witnesses of ``center``.  Reversed paths are identified.
    """

    _validate_pattern(S)
    if center < 0 or center >= len(S):
        raise ValueError(f"center out of range: {center}")
    return _covered_witness_path_orders(S, center)


def _covered_witness_path_orders(S: Pattern, center: int) -> list[list[int]]:
    """Return all-covered local witness orders for a validated pattern."""

    paths: set[tuple[int, ...]] = set()
    for raw in permutations(sorted(S[center])):
        if all(
            _selected_pair_sources(S, a, b)
            for a, b in zip(raw, raw[1:])
        ):
            path = tuple(int(label) for label in raw)
            paths.add(min(path, tuple(reversed(path))))
    return [list(path) for path in sorted(paths)]


def row_has_order_free_empty_gap(S: Pattern, center: int) -> bool:
    """Return True iff every local witness order has an uncovered short gap.

    This is the exact row-level complement of having an all-covered witness
    path.  It certifies that the row can never be blocked by the minimum-radius
    short-chord test, whatever the ambient cyclic order is.
    """

    _validate_pattern(S)
    if center < 0 or center >= len(S):
        raise ValueError(f"center out of range: {center}")
    return _row_has_order_free_empty_gap(S, center)


def _row_has_order_free_empty_gap(S: Pattern, center: int) -> bool:
    """Return order-free empty-gap status for a validated pattern."""

    return not _covered_witness_path_orders(S, center)


def minimum_radius_order_obstruction(
    S: Pattern,
    order: Sequence[int] | None = None,
    pattern: str = "",
) -> MinRadiusOrderResult:
    """Return the fixed-order minimum-radius obstruction summary."""

    _validate_pattern(S)
    n = len(S)
    if order is None:
        order = list(range(n))
    pos = _positions(order, n, require_full=True)

    rows = [_minimum_radius_row_result(S, pos, center) for center in range(n)]
    blocked = [row.center for row in rows if row.blocked]
    possible = [row.center for row in rows if not row.blocked]
    order_free = [center for center in range(n) if _row_is_order_free_blocked(S, center)]
    order_free_empty_gap = [
        center for center in range(n) if _row_has_order_free_empty_gap(S, center)
    ]
    return MinRadiusOrderResult(
        pattern=pattern,
        n=n,
        order=list(order),
        rows=rows,
        blocked_centers=blocked,
        possible_min_centers=possible,
        order_free_blocked_centers=order_free,
        order_free_empty_gap_centers=order_free_empty_gap,
        obstructed=not possible,
    )


def radius_propagation_order_obstruction(
    S: Pattern,
    order: Sequence[int] | None = None,
    pattern: str = "",
    max_nodes: int | None = None,
) -> RadiusPropagationResult:
    """Search fixed-order short-gap choices for unavoidable radius cycles.

    For each row, the minimum-radius lemma guarantees at least one consecutive
    witness pair is a short chord. If that pair is selected by one or both
    endpoints, it forces a strict inequality ``r_source < r_center``. A strict
    directed cycle in these inequalities is impossible. This routine searches
    all choices of one consecutive pair per row, pruning whenever a cycle is
    already forced.

    A returned acyclic choice is only an escape from this filter, not evidence
    for geometric realizability.
    """

    _validate_pattern(S)
    if max_nodes is not None and max_nodes <= 0:
        raise ValueError("max_nodes must be positive or None")
    n = len(S)
    if order is None:
        order = list(range(n))
    order = list(order)
    pos = _positions(order, n, require_full=True)
    rows = [_minimum_radius_row_result(S, pos, center) for center in range(n)]
    row_choices = [
        [
            (short_pair, _selected_pair_sources(S, *short_pair))
            for short_pair in row.consecutive_pairs
        ]
        for row in rows
    ]
    choice_count = prod(len(choices) for choices in row_choices)
    nodes_visited = 0
    max_depth = 0
    search_truncated = False
    edges: list[DirectedEdge] = []
    choice_stack: list[RadiusPropagationChoice] = []

    def search(row_idx: int) -> list[RadiusPropagationChoice] | None:
        nonlocal nodes_visited, max_depth, search_truncated
        if max_nodes is not None and nodes_visited >= max_nodes:
            search_truncated = True
            return None
        nodes_visited += 1
        max_depth = max(max_depth, row_idx)
        if row_idx == len(rows):
            return list(choice_stack)

        center = rows[row_idx].center
        # Try uncovered gaps first; they are the most direct escape from the
        # propagation filter and make surviving orders cheap to certify.
        choices = sorted(
            row_choices[row_idx],
            key=lambda item: (len(item[1]), item[0]),
        )
        for short_pair, sources in choices:
            new_edges = [(source, center) for source in sources]
            old_edge_count = len(edges)
            edges.extend(new_edges)
            if not _directed_cycle_exists(n, edges):
                choice_stack.append(
                    RadiusPropagationChoice(
                        center=center,
                        consecutive_pair=short_pair,
                        selected_sources=list(sources),
                        inequality_edges=list(new_edges),
                    )
                )
                found = search(row_idx + 1)
                if found is not None:
                    return found
                choice_stack.pop()
            del edges[old_edge_count:]
            if search_truncated:
                return None
        return None

    acyclic_choice = search(0)
    if acyclic_choice is not None:
        status = "PASS_RADIUS_PROPAGATION"
        obstructed: bool | None = False
    elif search_truncated:
        status = "UNKNOWN_RADIUS_PROPAGATION_NODE_LIMIT"
        obstructed = None
    else:
        status = "EXACT_RADIUS_PROPAGATION_OBSTRUCTION"
        obstructed = True

    return RadiusPropagationResult(
        pattern=pattern,
        n=n,
        order=order,
        status=status,
        obstructed=obstructed,
        short_gap_choice_count=choice_count,
        nodes_visited=nodes_visited,
        max_depth=max_depth,
        search_truncated=search_truncated,
        acyclic_choice=acyclic_choice,
    )


def _directed_cycle_exists(n: int, edges: Sequence[DirectedEdge]) -> bool:
    graph: list[list[int]] = [[] for _ in range(n)]
    for source, target in edges:
        graph[source].append(target)
    color = [0] * n

    def visit(node: int) -> bool:
        color[node] = 1
        for target in graph[node]:
            if color[target] == 1:
                return True
            if color[target] == 0 and visit(target):
                return True
        color[node] = 2
        return False

    for node in range(n):
        if color[node] == 0 and visit(node):
            return True
    return False


def _json_pair(item: Pair) -> list[int]:
    return [int(item[0]), int(item[1])]


def _json_row(row: MinRadiusRowResult) -> dict[str, object]:
    return {
        "center": int(row.center),
        "witness_order": [int(label) for label in row.witness_order],
        "consecutive_pairs": [_json_pair(item) for item in row.consecutive_pairs],
        "covered_consecutive_pairs": [_json_pair(item) for item in row.covered_consecutive_pairs],
        "uncovered_consecutive_pairs": [_json_pair(item) for item in row.uncovered_consecutive_pairs],
        "blocked": row.blocked,
    }


def _json_choice(choice: RadiusPropagationChoice) -> dict[str, object]:
    return {
        "center": int(choice.center),
        "consecutive_pair": _json_pair(choice.consecutive_pair),
        "selected_sources": [int(source) for source in choice.selected_sources],
        "inequality_edges": [
            {"source": int(source), "target": int(target)}
            for source, target in choice.inequality_edges
        ],
    }


def result_to_json(result: MinRadiusOrderResult) -> dict[str, object]:
    """Return a JSON-serializable form of a minimum-radius result."""

    return {
        "type": "minimum_radius_order_result",
        "pattern": result.pattern,
        "n": int(result.n),
        "order": [int(label) for label in result.order],
        "result": "OBSTRUCTED" if result.obstructed else "PASS",
        "obstructed": result.obstructed,
        "blocked_centers": [int(center) for center in result.blocked_centers],
        "possible_min_centers": [int(center) for center in result.possible_min_centers],
        "order_free_blocked_centers": [int(center) for center in result.order_free_blocked_centers],
        "order_free_empty_gap_centers": [
            int(center) for center in result.order_free_empty_gap_centers
        ],
        "rows": [_json_row(row) for row in result.rows],
    }


def radius_result_to_json(result: RadiusPropagationResult) -> dict[str, object]:
    """Return a JSON-serializable form of a radius-propagation result."""

    return {
        "type": "radius_propagation_order_result",
        "status_schema": "min_radius_filter.v1",
        "edge_direction": "source -> target means r_source < r_target; here target is the row center",
        "pattern": result.pattern,
        "n": int(result.n),
        "order": [int(label) for label in result.order],
        "status": result.status,
        "result": result.status,
        "obstructed": result.obstructed,
        "short_gap_choice_count": int(result.short_gap_choice_count),
        "nodes_visited": int(result.nodes_visited),
        "max_depth": int(result.max_depth),
        "search_truncated": result.search_truncated,
        "acyclic_choice": (
            None
            if result.acyclic_choice is None
            else [_json_choice(choice) for choice in result.acyclic_choice]
        ),
    }
