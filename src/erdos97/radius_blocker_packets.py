"""Radius-blocker packet diagnostics with vertex-circle replay.

This module is bridge-program tooling.  It checks finite packets of possible
exact four-witness rows against the radius-blocker condition, incidence/order
filters, and the existing vertex-circle selected-distance quotient replay.
Passing or failing a packet is not a proof of Erdos Problem #97.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from math import prod
from typing import Iterable, Mapping, Sequence

from erdos97.adaptive_blockers import RichClasses, is_radius_blocker, validate_rich_classes
from erdos97.incidence_filters import chords_cross_in_order, normalize_chord
from erdos97.vertex_circle_quotient_replay import (
    SelectedRow,
    replay_vertex_circle_quotient,
    result_to_json,
)

Pair = tuple[int, int]
Row = tuple[int, int, int, int]
Rows = list[list[int]]

SCHEMA = "erdos97.radius_blocker_vertex_circle_packet.v1"
STATUS = "RADIUS_BLOCKER_VERTEX_CIRCLE_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Finite exact-four-row radius-blocker packet diagnostic. It may obstruct "
    "the encoded row-option packet under the supplied cyclic order, but it is "
    "not a proof of the adaptive blocker bridge, not a proof of Erdos Problem "
    "#97, and not a counterexample."
)


@dataclass(frozen=True)
class PacketConfig:
    """Search controls for a radius-blocker packet."""

    max_nodes: int = 100_000
    max_survivor_examples: int = 8
    max_obstruction_examples_per_status: int = 2
    enforce_pair_filters: bool = True
    enforce_column_pair_cap: bool = True
    enforce_indegree_cap: bool = True


@dataclass(frozen=True)
class RadiusBlockerPacketResult:
    """Summary of one finite packet replay."""

    name: str
    n: int
    order: tuple[int, ...]
    blocker: tuple[int, ...]
    radius_blocker_ok: bool
    row_option_counts: tuple[int, ...]
    raw_selection_upper_bound: int
    nodes_visited: int
    incidence_survivors: int
    aborted: bool
    vertex_circle_status_counts: Mapping[str, int]
    survivor_examples: tuple[Rows, ...]
    obstruction_examples: Mapping[str, tuple[dict[str, object], ...]]
    rejection_counts: Mapping[str, int]

    @property
    def all_incidence_survivors_obstructed(self) -> bool:
        return (
            self.incidence_survivors > 0
            and self.vertex_circle_status_counts.get("ok", 0) == 0
            and not self.aborted
        )


def exact_four_rich_classes_from_rows(rows: Sequence[Sequence[int]]) -> RichClasses:
    """Treat each selected four-row as the only exact rich class at its center."""

    out: list[tuple[tuple[int, ...], ...]] = []
    for center, row in enumerate(rows):
        normalized = tuple(sorted(int(label) for label in row))
        if len(normalized) != 4 or len(set(normalized)) != 4:
            raise ValueError(f"row {center} is not a four-set")
        if center in normalized:
            raise ValueError(f"row {center} selects its center")
        out.append((normalized,))
    return tuple(out)


def full_exact_four_radius_blocker_rich_classes(
    n: int,
    blocker: Iterable[int],
    threshold: int = 3,
) -> tuple[tuple[Row, ...], ...]:
    """Return all exact-four rows compatible with ``blocker`` being blocked.

    For centers inside the blocker, every row option is required to contain
    fewer than ``threshold`` blocker vertices.  For centers outside the
    blocker, all exact four-subsets avoiding the center are allowed.
    """

    if n < 4:
        raise ValueError(f"expected at least four centers, got {n}")
    if threshold <= 0:
        raise ValueError("threshold must be positive")
    blocker_set = set(int(label) for label in blocker)
    bad = sorted(label for label in blocker_set if label < 0 or label >= n)
    if bad:
        raise ValueError(f"blocker contains out-of-range labels: {bad}")
    if len(blocker_set) < threshold + 1:
        raise ValueError(
            f"blocker must have at least {threshold + 1} vertices, got "
            f"{len(blocker_set)}"
        )

    options: list[tuple[Row, ...]] = []
    for center in range(n):
        center_options: list[Row] = []
        for row in combinations((label for label in range(n) if label != center), 4):
            if center in blocker_set and len(blocker_set.intersection(row)) >= threshold:
                continue
            center_options.append((row[0], row[1], row[2], row[3]))
        options.append(tuple(center_options))
    return tuple(options)


def row_options_from_rich_classes(rich_classes: RichClasses) -> tuple[tuple[Row, ...], ...]:
    """Return deterministic exact-four row options for every center.

    The first bridge diagnostic intentionally accepts only exact four-rich
    classes.  Larger rich classes need a separate sound replay convention,
    because their full equality information is stronger than a chosen
    four-subset.
    """

    validate_rich_classes(rich_classes)
    options: list[tuple[Row, ...]] = []
    for center, classes in enumerate(rich_classes):
        center_options: list[Row] = []
        seen: set[Row] = set()
        for class_index, rich_class in enumerate(classes):
            row = tuple(sorted(int(label) for label in rich_class))
            if len(row) != 4:
                raise ValueError(
                    "radius-blocker packet replay currently requires exact "
                    f"four-rich classes; center {center} class {class_index} "
                    f"has size {len(row)}"
                )
            typed_row = (row[0], row[1], row[2], row[3])
            if typed_row not in seen:
                seen.add(typed_row)
                center_options.append(typed_row)
        options.append(tuple(center_options))
    return tuple(options)


def analyze_radius_blocker_packet(
    name: str,
    rich_classes: RichClasses,
    blocker: Sequence[int],
    order: Sequence[int] | None = None,
    config: PacketConfig | None = None,
) -> RadiusBlockerPacketResult:
    """Replay one exact-four radius-blocker packet in a supplied cyclic order."""

    config = config or PacketConfig()
    options = row_options_from_rich_classes(rich_classes)
    n = len(options)
    if order is None:
        order = tuple(range(n))
    order_tuple = tuple(int(label) for label in order)
    _validate_order(order_tuple, n)
    blocker_tuple = tuple(sorted(int(label) for label in blocker))
    radius_blocker_ok = is_radius_blocker(rich_classes, blocker_tuple)

    max_indegree = 2 * (n - 1) // 3
    assigned: dict[int, Row] = {}
    column_counts = [0] * n
    witness_pair_counts: Counter[Pair] = Counter()
    nodes_visited = 0
    incidence_survivors = 0
    aborted = False
    vertex_status_counts: Counter[str] = Counter()
    rejection_counts: Counter[str] = Counter()
    survivor_examples: list[Rows] = []
    obstruction_examples: dict[str, list[dict[str, object]]] = {}

    def row_is_valid(center: int, row: Row) -> bool:
        if config.enforce_indegree_cap:
            if any(column_counts[target] >= max_indegree for target in row):
                rejection_counts["indegree_cap"] += 1
                return False
        if config.enforce_column_pair_cap:
            for pair_item in combinations(row, 2):
                if witness_pair_counts[_pair(*pair_item)] >= 2:
                    rejection_counts["column_pair_cap"] += 1
                    return False
        if config.enforce_pair_filters:
            for other, other_row in assigned.items():
                reason = _row_pair_rejection(
                    center,
                    row,
                    other,
                    other_row,
                    order_tuple,
                )
                if reason is not None:
                    rejection_counts[reason] += 1
                    return False
        return True

    def add_row(row: Row) -> None:
        for target in row:
            column_counts[target] += 1
        for pair_item in combinations(row, 2):
            witness_pair_counts[_pair(*pair_item)] += 1

    def remove_row(row: Row) -> None:
        for pair_item in combinations(row, 2):
            witness_pair_counts[_pair(*pair_item)] -= 1
        for target in row:
            column_counts[target] -= 1

    def current_rows() -> Rows:
        return [list(assigned[center]) for center in range(n)]

    def replay_full_assignment() -> None:
        nonlocal incidence_survivors
        incidence_survivors += 1
        selected = [
            SelectedRow(center=center, witnesses=assigned[center])
            for center in range(n)
        ]
        replay = replay_vertex_circle_quotient(n, order_tuple, selected)
        vertex_status_counts[replay.status] += 1
        if replay.status == "ok":
            if len(survivor_examples) < config.max_survivor_examples:
                survivor_examples.append(current_rows())
            return
        bucket = obstruction_examples.setdefault(replay.status, [])
        if len(bucket) < config.max_obstruction_examples_per_status:
            bucket.append(
                {
                    "selected_rows": current_rows(),
                    "vertex_circle_replay": result_to_json(replay),
                }
            )

    def viable_options(center: int) -> list[Row]:
        return [row for row in options[center] if row_is_valid(center, row)]

    def choose_center() -> tuple[int | None, list[Row]]:
        best_center: int | None = None
        best_options: list[Row] = []
        for center in range(n):
            if center in assigned:
                continue
            rows = viable_options(center)
            if best_center is None or len(rows) < len(best_options):
                best_center = center
                best_options = rows
            if not rows:
                break
        return best_center, best_options

    def search() -> None:
        nonlocal aborted
        nonlocal nodes_visited
        if aborted:
            return
        if len(assigned) == n:
            replay_full_assignment()
            return
        if nodes_visited >= config.max_nodes:
            aborted = True
            return
        center, rows = choose_center()
        if center is None:
            replay_full_assignment()
            return
        if not rows:
            return
        for row in rows:
            if nodes_visited >= config.max_nodes:
                aborted = True
                return
            nodes_visited += 1
            assigned[center] = row
            add_row(row)
            search()
            remove_row(row)
            del assigned[center]
            if aborted:
                return

    search()

    return RadiusBlockerPacketResult(
        name=name,
        n=n,
        order=order_tuple,
        blocker=blocker_tuple,
        radius_blocker_ok=radius_blocker_ok,
        row_option_counts=tuple(len(rows) for rows in options),
        raw_selection_upper_bound=prod(len(rows) for rows in options),
        nodes_visited=nodes_visited,
        incidence_survivors=incidence_survivors,
        aborted=aborted,
        vertex_circle_status_counts=dict(sorted(vertex_status_counts.items())),
        survivor_examples=tuple(survivor_examples),
        obstruction_examples={
            status: tuple(examples)
            for status, examples in sorted(obstruction_examples.items())
        },
        rejection_counts=dict(sorted(rejection_counts.items())),
    )


def result_to_packet_json(result: RadiusBlockerPacketResult) -> dict[str, object]:
    """Return a JSON-safe packet result."""

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "name": result.name,
        "n": result.n,
        "order": list(result.order),
        "blocker": list(result.blocker),
        "radius_blocker_ok": result.radius_blocker_ok,
        "row_option_counts": list(result.row_option_counts),
        "raw_selection_upper_bound": result.raw_selection_upper_bound,
        "nodes_visited": result.nodes_visited,
        "incidence_survivors": result.incidence_survivors,
        "aborted": result.aborted,
        "vertex_circle_status_counts": dict(result.vertex_circle_status_counts),
        "all_incidence_survivors_obstructed": (
            result.all_incidence_survivors_obstructed
        ),
        "survivor_examples": list(result.survivor_examples),
        "obstruction_examples": {
            status: list(examples)
            for status, examples in result.obstruction_examples.items()
        },
        "rejection_counts": dict(result.rejection_counts),
        "interpretation": (
            "Diagnostic for this finite exact-four row-option packet only. "
            "A positive obstruction count does not prove the adaptive "
            "radius-blocker bridge or Erdos Problem #97."
        ),
    }


def _validate_order(order: Sequence[int], n: int) -> None:
    if len(order) != n or set(order) != set(range(n)):
        missing = sorted(set(range(n)) - set(order))
        extra = sorted(set(order) - set(range(n)))
        raise ValueError(
            f"cyclic order is not a permutation; missing={missing}, extra={extra}"
        )


def _pair(left: int, right: int) -> Pair:
    if left == right:
        raise ValueError("loop pair")
    return (left, right) if left < right else (right, left)


def _row_pair_rejection(
    left: int,
    left_row: Sequence[int],
    right: int,
    right_row: Sequence[int],
    order: Sequence[int],
) -> str | None:
    inter = sorted(set(left_row) & set(right_row))
    if len(inter) > 2:
        return "row_pair_cap"
    if len(inter) == 2:
        source = normalize_chord(left, right)
        target = normalize_chord(inter[0], inter[1])
        if not chords_cross_in_order(source, target, order):
            return "two_overlap_crossing"
    return None
