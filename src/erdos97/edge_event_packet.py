"""Coordinate-level edge-event and edge-Gram packet checks.

This module extracts the transverse edge-event packet suggested by the bridge
review.  It verifies exact algebraic identities for supplied polygon
coordinates and optional selected witness rows.  It is a diagnostic layer only;
it does not certify global infeasibility.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, Sequence

Point = tuple[Fraction, Fraction]
Matrix = tuple[tuple[Fraction, ...], ...]


@dataclass(frozen=True)
class IntervalPacket:
    """One consecutive selected-witness gap in one row."""

    center: int
    left_witness: int
    right_witness: int
    edge_interval: tuple[int, ...]
    row_zero_sum: Fraction
    gram_center_sum: Fraction
    gram_prev_sum: Fraction
    next_row_sum: Fraction
    prev_row_sum: Fraction
    zero_sum_verified: bool
    transverse_verified: bool


@dataclass(frozen=True)
class ColumnSignSummary:
    """Vertex-level sign shape for one edge-bisector column."""

    edge: int
    positive_vertices: tuple[int, ...]
    negative_vertices: tuple[int, ...]
    zero_vertices: tuple[int, ...]
    positive_is_cyclic_interval: bool
    negative_is_cyclic_interval: bool
    zero_count_at_most_two: bool
    forced_edge_sign_transition: bool


def as_fraction(value: object) -> Fraction:
    """Parse ints, strings, and floats into a deterministic Fraction."""

    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, str):
        return Fraction(value)
    if isinstance(value, float):
        return Fraction(str(value))
    raise TypeError(f"unsupported coordinate value {value!r}")


def normalize_points(points: Iterable[Sequence[object]]) -> list[Point]:
    """Return points with Fraction coordinates."""

    output: list[Point] = []
    for raw in points:
        if len(raw) != 2:
            raise ValueError(f"point must have two coordinates, got {raw!r}")
        output.append((as_fraction(raw[0]), as_fraction(raw[1])))
    if len(output) < 3:
        raise ValueError("expected at least three polygon vertices")
    return output


def add(left: Point, right: Point) -> Point:
    return (left[0] + right[0], left[1] + right[1])


def sub(left: Point, right: Point) -> Point:
    return (left[0] - right[0], left[1] - right[1])


def dot(left: Point, right: Point) -> Fraction:
    return left[0] * right[0] + left[1] * right[1]


def cross(left: Point, right: Point) -> Fraction:
    return left[0] * right[1] - left[1] * right[0]


def norm2(point: Point) -> Fraction:
    return dot(point, point)


def edge_vectors(points: Sequence[Point]) -> list[Point]:
    n = len(points)
    return [sub(points[(idx + 1) % n], points[idx]) for idx in range(n)]


def cyclic_interval(start: int, end: int, n: int) -> tuple[int, ...]:
    """Return edge indices in the cyclic interval ``[start,end)``."""

    if not 0 <= start < n or not 0 <= end < n:
        raise ValueError("interval endpoints out of range")
    output: list[int] = []
    cursor = start
    while cursor != end:
        output.append(cursor)
        cursor = (cursor + 1) % n
        if len(output) > n:
            raise AssertionError("cyclic interval did not terminate")
    return tuple(output)


def boundary_order_from_center(
    n: int,
    center: int,
    vertices: Sequence[int],
) -> tuple[int, ...]:
    """Order vertices on the boundary chain ``center+1,...,center-1``."""

    if not 0 <= center < n:
        raise ValueError("center out of range")
    for vertex in vertices:
        if vertex == center:
            raise ValueError("center cannot be a witness")
        if not 0 <= vertex < n:
            raise ValueError(f"vertex {vertex} out of range")
    return tuple(sorted((int(v) for v in vertices), key=lambda v: (v - center) % n))


def edge_event_matrix(points: Sequence[Point]) -> Matrix:
    """Return ``D[i][k]=|p_i-p_{k+1}|^2-|p_i-p_k|^2``."""

    n = len(points)
    rows: list[tuple[Fraction, ...]] = []
    for center in range(n):
        row = []
        for edge in range(n):
            row.append(
                norm2(sub(points[center], points[(edge + 1) % n]))
                - norm2(sub(points[center], points[edge]))
            )
        rows.append(tuple(row))
    return tuple(rows)


def edge_gram_matrix(points: Sequence[Point]) -> Matrix:
    """Return the edge Gram matrix ``G[i][k]=e_i.e_k``."""

    edges = edge_vectors(points)
    return tuple(tuple(dot(left, right) for right in edges) for left in edges)


def row_difference_identity_errors(d_matrix: Matrix, g_matrix: Matrix) -> Matrix:
    """Return errors in ``D[i+1,k]-D[i,k]+2G[i,k]=0``."""

    n = len(d_matrix)
    return tuple(
        tuple(
            d_matrix[(row + 1) % n][col] - d_matrix[row][col] + 2 * g_matrix[row][col]
            for col in range(n)
        )
        for row in range(n)
    )


def gram_closure_sums(g_matrix: Matrix) -> tuple[Fraction, ...]:
    """Return row sums of ``G``; closure gives zero sums."""

    return tuple(sum(row, Fraction(0)) for row in g_matrix)


def _sign(value: Fraction) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def _is_cyclic_interval(vertices: Sequence[int], n: int) -> bool:
    """Return whether a subset is one cyclic interval of vertex labels."""

    subset = set(vertices)
    if not subset or len(subset) == n:
        return True
    transitions = 0
    for idx in range(n):
        if (idx in subset) != ((idx + 1) % n in subset):
            transitions += 1
    return transitions <= 2


def column_sign_summaries(d_matrix: Matrix) -> list[ColumnSignSummary]:
    """Return softened line-cut sign checks for each edge column."""

    n = len(d_matrix)
    summaries: list[ColumnSignSummary] = []
    for edge in range(n):
        positive = tuple(row for row in range(n) if _sign(d_matrix[row][edge]) > 0)
        negative = tuple(row for row in range(n) if _sign(d_matrix[row][edge]) < 0)
        zero = tuple(row for row in range(n) if _sign(d_matrix[row][edge]) == 0)
        summaries.append(
            ColumnSignSummary(
                edge=edge,
                positive_vertices=positive,
                negative_vertices=negative,
                zero_vertices=zero,
                positive_is_cyclic_interval=_is_cyclic_interval(positive, n),
                negative_is_cyclic_interval=_is_cyclic_interval(negative, n),
                zero_count_at_most_two=len(zero) <= 2,
                forced_edge_sign_transition=(
                    d_matrix[edge][edge] > 0
                    and d_matrix[(edge + 1) % n][edge] < 0
                ),
            )
        )
    return summaries


def selected_interval_packets(
    points: Sequence[Point],
    selected_rows: dict[int, Sequence[int]],
) -> list[IntervalPacket]:
    """Return selected-row zero interval and transverse sign packets."""

    n = len(points)
    d_matrix = edge_event_matrix(points)
    g_matrix = edge_gram_matrix(points)
    packets: list[IntervalPacket] = []
    for center, raw_witnesses in sorted(selected_rows.items()):
        witnesses = boundary_order_from_center(n, center, raw_witnesses)
        if len(witnesses) != 4:
            raise ValueError(f"row {center} must have four witnesses")
        for left, right in zip(witnesses, witnesses[1:]):
            interval = cyclic_interval(left, right, n)
            row_zero = sum((d_matrix[center][edge] for edge in interval), Fraction(0))
            gram_center = sum((g_matrix[center][edge] for edge in interval), Fraction(0))
            gram_prev = sum(
                (g_matrix[(center - 1) % n][edge] for edge in interval),
                Fraction(0),
            )
            next_row = sum(
                (d_matrix[(center + 1) % n][edge] for edge in interval),
                Fraction(0),
            )
            prev_row = sum(
                (d_matrix[(center - 1) % n][edge] for edge in interval),
                Fraction(0),
            )
            packets.append(
                IntervalPacket(
                    center=center,
                    left_witness=left,
                    right_witness=right,
                    edge_interval=interval,
                    row_zero_sum=row_zero,
                    gram_center_sum=gram_center,
                    gram_prev_sum=gram_prev,
                    next_row_sum=next_row,
                    prev_row_sum=prev_row,
                    zero_sum_verified=row_zero == 0,
                    transverse_verified=(
                        gram_center < 0
                        and gram_prev < 0
                        and next_row > 0
                        and prev_row < 0
                    ),
                )
            )
    return packets


def fraction_to_json(value: Fraction) -> int | str:
    """Return compact JSON for an exact Fraction."""

    if value.denominator == 1:
        return value.numerator
    return f"{value.numerator}/{value.denominator}"


def _matrix_to_json(matrix: Matrix) -> list[list[int | str]]:
    return [[fraction_to_json(value) for value in row] for row in matrix]


def edge_event_report(
    points: Iterable[Sequence[object]],
    selected_rows: dict[int, Sequence[int]] | None = None,
) -> dict[str, object]:
    """Return a JSON-friendly edge-event packet report."""

    normalized = normalize_points(points)
    selected_rows = selected_rows or {}
    d_matrix = edge_event_matrix(normalized)
    g_matrix = edge_gram_matrix(normalized)
    identity_errors = row_difference_identity_errors(d_matrix, g_matrix)
    closure_sums = gram_closure_sums(g_matrix)
    column_summaries = column_sign_summaries(d_matrix)
    interval_packets = selected_interval_packets(normalized, selected_rows)

    return {
        "schema": "erdos97.edge_event_packet.v1",
        "trust": "RESEARCH_PACKET_COORDINATE_DIAGNOSTIC",
        "claim_scope": (
            "Exact edge-event and Gram identities for supplied coordinates; "
            "not a proof of Erdos #97."
        ),
        "n": len(normalized),
        "rank_bounds": {
            "edge_event_matrix_rank_at_most": 3,
            "edge_gram_matrix_rank_at_most": 2,
        },
        "identity_checks": {
            "row_difference_identity_verified": all(
                value == 0 for row in identity_errors for value in row
            ),
            "gram_closure_verified": all(value == 0 for value in closure_sums),
            "column_line_cut_checks_verified": all(
                row.positive_is_cyclic_interval
                and row.negative_is_cyclic_interval
                and row.zero_count_at_most_two
                and row.forced_edge_sign_transition
                for row in column_summaries
            ),
            "selected_interval_packets_verified": all(
                row.zero_sum_verified and row.transverse_verified
                for row in interval_packets
            ),
        },
        "D": _matrix_to_json(d_matrix),
        "G": _matrix_to_json(g_matrix),
        "row_difference_identity_errors": _matrix_to_json(identity_errors),
        "gram_closure_sums": [fraction_to_json(value) for value in closure_sums],
        "column_sign_summaries": [
            {
                "edge": row.edge,
                "positive_vertices": list(row.positive_vertices),
                "negative_vertices": list(row.negative_vertices),
                "zero_vertices": list(row.zero_vertices),
                "positive_is_cyclic_interval": row.positive_is_cyclic_interval,
                "negative_is_cyclic_interval": row.negative_is_cyclic_interval,
                "zero_count_at_most_two": row.zero_count_at_most_two,
                "forced_edge_sign_transition": row.forced_edge_sign_transition,
            }
            for row in column_summaries
        ],
        "selected_interval_packets": [
            {
                "center": row.center,
                "left_witness": row.left_witness,
                "right_witness": row.right_witness,
                "edge_interval": list(row.edge_interval),
                "row_zero_sum": fraction_to_json(row.row_zero_sum),
                "gram_center_sum": fraction_to_json(row.gram_center_sum),
                "gram_prev_sum": fraction_to_json(row.gram_prev_sum),
                "next_row_sum": fraction_to_json(row.next_row_sum),
                "prev_row_sum": fraction_to_json(row.prev_row_sum),
                "zero_sum_verified": row.zero_sum_verified,
                "transverse_verified": row.transverse_verified,
            }
            for row in interval_packets
        ],
    }
