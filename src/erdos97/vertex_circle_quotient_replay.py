"""Replay vertex-circle quotient obstructions from selected rows.

This module is intentionally smaller than the cyclic-order searchers. It
checks one supplied cyclic order and one supplied set of selected rows by
rebuilding the selected-distance quotient and the strict vertex-circle graph.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any, Sequence

Pair = tuple[int, int]

VALID_STATUSES = {"ok", "self_edge", "strict_cycle"}


@dataclass(frozen=True)
class SelectedRow:
    center: int
    witnesses: tuple[int, int, int, int]


@dataclass(frozen=True)
class StrictInequality:
    row: int
    witness_order: tuple[int, ...]
    outer_interval: tuple[int, int]
    inner_interval: tuple[int, int]
    outer_pair: Pair
    inner_pair: Pair
    outer_class: Pair
    inner_class: Pair


@dataclass(frozen=True)
class QuotientReplayResult:
    n: int
    order: tuple[int, ...]
    selected_row_count: int
    strict_edge_count: int
    status: str
    self_edge_conflicts: tuple[StrictInequality, ...]
    cycle_edges: tuple[StrictInequality, ...]

    @property
    def obstructed(self) -> bool:
        return self.status != "ok"


@dataclass(frozen=True)
class LocalCoreReplay:
    family_id: str
    expected_status: str | None
    result: QuotientReplayResult

    @property
    def status_matches_expected(self) -> bool:
        return self.expected_status is None or self.expected_status == self.result.status


def pair(u: int, v: int) -> Pair:
    """Return a normalized unordered pair and reject loops."""
    if u == v:
        raise ValueError(f"loop pair is not allowed: ({u}, {v})")
    return (u, v) if u < v else (v, u)


class UnionFind:
    """Deterministic union-find over pair labels."""

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


def parse_selected_rows(raw_rows: Sequence[Any]) -> list[SelectedRow]:
    """Parse full-row lists or explicit ``{"row", "witnesses"}`` records."""
    rows: list[SelectedRow] = []
    for index, raw in enumerate(raw_rows):
        if isinstance(raw, dict):
            if "row" in raw:
                center = int(raw["row"])
            elif "center" in raw:
                center = int(raw["center"])
            else:
                raise ValueError("row record must contain row or center")
            witnesses_raw = raw.get("witnesses")
        else:
            center = index
            witnesses_raw = raw
            if (
                isinstance(raw, Sequence)
                and not isinstance(raw, str)
                and len(raw) == 5
            ):
                center = int(raw[0])
                witnesses_raw = raw[1:]
        if not isinstance(witnesses_raw, Sequence) or isinstance(witnesses_raw, str):
            raise ValueError(f"row {center} witnesses must be a sequence")
        witnesses = tuple(int(label) for label in witnesses_raw)
        if len(witnesses) != 4:
            raise ValueError(f"row {center} has {len(witnesses)} witnesses, expected 4")
        rows.append(
            SelectedRow(
                center=center,
                witnesses=(witnesses[0], witnesses[1], witnesses[2], witnesses[3]),
            )
        )
    return rows


def rows_from_payload(payload: dict[str, Any]) -> list[SelectedRow]:
    """Extract selected rows from a replay payload."""
    for key in ("compact_selected_rows", "core_selected_rows", "selected_rows", "rows", "S"):
        if key in payload:
            raw_rows = payload[key]
            if not isinstance(raw_rows, Sequence) or isinstance(raw_rows, str):
                raise ValueError(f"{key} must be a sequence")
            return parse_selected_rows(raw_rows)
    raise ValueError("payload must contain selected_rows, core_selected_rows, rows, or S")


def replay_payload(payload: dict[str, Any]) -> QuotientReplayResult:
    """Replay a single vertex-circle quotient payload."""
    rows = rows_from_payload(payload)
    order_raw = payload.get("cyclic_order", payload.get("order"))
    if order_raw is None:
        raise ValueError("payload must contain cyclic_order or order")
    if not isinstance(order_raw, Sequence) or isinstance(order_raw, str):
        raise ValueError("cyclic_order/order must be a sequence")
    order = tuple(int(label) for label in order_raw)
    n = int(payload.get("n", len(order)))
    return replay_vertex_circle_quotient(n, order, rows)


def replay_local_core_bundle(payload: dict[str, Any]) -> list[LocalCoreReplay]:
    """Replay every local-core certificate in an n=9 local-core bundle."""
    raw_certificates = payload.get("certificates")
    if not isinstance(raw_certificates, Sequence) or isinstance(raw_certificates, str):
        raise ValueError("local-core bundle must contain certificates")
    order_raw = payload.get("cyclic_order", payload.get("order"))
    if not isinstance(order_raw, Sequence) or isinstance(order_raw, str):
        raise ValueError("local-core bundle must contain cyclic_order/order")
    order = tuple(int(label) for label in order_raw)
    n = int(payload.get("n", len(order)))

    replays: list[LocalCoreReplay] = []
    for index, raw_certificate in enumerate(raw_certificates):
        if not isinstance(raw_certificate, dict):
            raise ValueError(f"certificate {index} must be an object")
        rows = rows_from_payload(raw_certificate)
        expected = raw_certificate.get("status")
        if expected is not None and expected not in VALID_STATUSES:
            raise ValueError(f"certificate {index} has invalid status {expected!r}")
        result = replay_vertex_circle_quotient(n, order, rows)
        replays.append(
            LocalCoreReplay(
                family_id=str(raw_certificate.get("family_id", index)),
                expected_status=expected,
                result=result,
            )
        )
    return replays


def replay_vertex_circle_quotient(
    n: int,
    order: Sequence[int],
    rows: Sequence[SelectedRow],
) -> QuotientReplayResult:
    """Check the vertex-circle quotient graph for supplied selected rows."""
    order_tuple = tuple(int(label) for label in order)
    _validate_order(n, order_tuple)
    _validate_rows(n, rows)
    uf = _distance_class_union_find(n, rows)
    strict_edges = _strict_inequalities(n, order_tuple, rows, uf)
    self_edges = tuple(edge for edge in strict_edges if edge.outer_class == edge.inner_class)
    cycle_edges = () if self_edges else tuple(_find_strict_cycle(strict_edges))
    if self_edges:
        status = "self_edge"
    elif cycle_edges:
        status = "strict_cycle"
    else:
        status = "ok"
    return QuotientReplayResult(
        n=n,
        order=order_tuple,
        selected_row_count=len(rows),
        strict_edge_count=len(strict_edges),
        status=status,
        self_edge_conflicts=self_edges,
        cycle_edges=cycle_edges,
    )


def result_to_json(result: QuotientReplayResult) -> dict[str, Any]:
    """Return a JSON-safe replay result."""
    return {
        "type": "vertex_circle_quotient_replay_result",
        "n": result.n,
        "order": list(result.order),
        "selected_row_count": result.selected_row_count,
        "strict_edge_count": result.strict_edge_count,
        "status": result.status,
        "obstructed": result.obstructed,
        "self_edge_conflicts": [
            _inequality_to_json(edge) for edge in result.self_edge_conflicts
        ],
        "cycle_edges": [_inequality_to_json(edge) for edge in result.cycle_edges],
    }


def local_core_bundle_to_json(replays: Sequence[LocalCoreReplay]) -> dict[str, Any]:
    """Return a compact JSON-safe local-core replay summary."""
    status_counts = Counter(replay.result.status for replay in replays)
    mismatches = [
        replay
        for replay in replays
        if not replay.status_matches_expected
    ]
    return {
        "type": "vertex_circle_local_core_replay_summary",
        "certificate_count": len(replays),
        "status_counts": dict(sorted(status_counts.items())),
        "expected_status_mismatches": [
            {
                "family_id": replay.family_id,
                "expected_status": replay.expected_status,
                "actual_status": replay.result.status,
            }
            for replay in mismatches
        ],
        "all_expected_statuses_match": not mismatches,
        "results": [
            {
                "family_id": replay.family_id,
                "expected_status": replay.expected_status,
                "status_matches_expected": replay.status_matches_expected,
                "result": result_to_json(replay.result),
            }
            for replay in replays
        ],
    }


def _all_pairs(n: int) -> list[Pair]:
    return [(u, v) for u in range(n) for v in range(u + 1, n)]


def _validate_order(n: int, order: Sequence[int]) -> None:
    seen = set(order)
    if len(order) != n or seen != set(range(n)):
        raise ValueError("cyclic order must be a permutation of range(n)")


def _validate_rows(n: int, rows: Sequence[SelectedRow]) -> None:
    seen_centers: set[int] = set()
    for row in rows:
        if row.center in seen_centers:
            raise ValueError(f"duplicate selected row for center {row.center}")
        seen_centers.add(row.center)
        if row.center < 0 or row.center >= n:
            raise ValueError(f"row center out of range: {row.center}")
        witnesses = set(row.witnesses)
        if len(witnesses) != 4:
            raise ValueError(f"row {row.center} has repeated witnesses")
        if row.center in witnesses:
            raise ValueError(f"row {row.center} includes its own center")
        bad = [label for label in witnesses if label < 0 or label >= n]
        if bad:
            raise ValueError(f"row {row.center} has witness out of range: {bad[0]}")


def _distance_class_union_find(n: int, rows: Sequence[SelectedRow]) -> UnionFind:
    uf = UnionFind(_all_pairs(n))
    for row in rows:
        base = pair(row.center, row.witnesses[0])
        for witness in row.witnesses[1:]:
            uf.union(base, pair(row.center, witness))
    return uf


def _strict_inequalities(
    n: int,
    order: Sequence[int],
    rows: Sequence[SelectedRow],
    uf: UnionFind,
) -> list[StrictInequality]:
    positions = {label: idx for idx, label in enumerate(order)}
    edges: list[StrictInequality] = []
    for row in rows:
        witnesses = tuple(
            sorted(row.witnesses, key=lambda witness: (positions[witness] - positions[row.center]) % n)
        )
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
                        edges.append(
                            StrictInequality(
                                row=row.center,
                                witness_order=witnesses,
                                outer_interval=(outer_start, outer_end),
                                inner_interval=(inner_start, inner_end),
                                outer_pair=outer_pair,
                                inner_pair=inner_pair,
                                outer_class=uf.find(outer_pair),
                                inner_class=uf.find(inner_pair),
                            )
                        )
    return edges


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
                    if parent_item is None:
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


def _inequality_to_json(edge: StrictInequality) -> dict[str, Any]:
    return {
        "row": edge.row,
        "witness_order": list(edge.witness_order),
        "outer_interval": list(edge.outer_interval),
        "inner_interval": list(edge.inner_interval),
        "outer_pair": list(edge.outer_pair),
        "inner_pair": list(edge.inner_pair),
        "outer_class": list(edge.outer_class),
        "inner_class": list(edge.inner_class),
    }
