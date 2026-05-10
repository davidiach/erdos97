"""Replayable negative controls for bridge-lemma work.

These certificates are intentionally scoped.  They are not counterexamples to
Erdos Problem #97 and do not move the repository's global or finite-case
status.
"""

from __future__ import annotations

from itertools import combinations
from typing import Sequence

from erdos97.fragile_hypergraph import check_fragile_hypergraph, check_to_json
from erdos97.incidence_filters import chords_cross_in_order, filter_summary
from erdos97.stuck_sets import find_minimal_stuck_sets, forward_ear_order
from erdos97.vertex_circle_order_filter import (
    order_result_to_json,
    vertex_circle_order_obstruction,
)


Pattern = list[list[int]]


def c13_sidon_rows() -> Pattern:
    """Return the retired fixed C13 Sidon selected-witness pattern."""

    offsets = (1, 2, 4, 10)
    return [[(center + offset) % 13 for offset in offsets] for center in range(13)]


def output7_two_block_rows() -> Pattern:
    """Return the abstract two-block full extension from the triage bundle.

    This pattern is kept only as an incidence negative control: it passes the
    pair/crossing entry filters and has no forward ear order, but it is not
    claimed to be geometrically realizable.
    """

    rows = {
        0: [1, 2, 3, 4],
        1: [3, 6, 7, 11],
        2: [1, 5, 9, 11],
        3: [0, 2, 4, 5],
        4: [0, 3, 6, 9],
        5: [0, 2, 10, 11],
        6: [7, 8, 9, 10],
        7: [0, 1, 8, 9],
        8: [4, 5, 7, 11],
        9: [6, 8, 10, 11],
        10: [1, 5, 6, 7],
        11: [0, 3, 5, 8],
    }
    return [rows[center] for center in range(12)]


def false_output8_two_block_rows() -> Pattern:
    """Return the triaged 12-row table whose no-ear claim is false."""

    rows = {
        0: [1, 2, 3, 4],
        1: [3, 6, 9, 11],
        2: [1, 3, 5, 8],
        3: [0, 2, 4, 5],
        4: [0, 3, 8, 11],
        5: [0, 1, 6, 7],
        6: [7, 8, 9, 10],
        7: [0, 4, 6, 9],
        8: [0, 5, 7, 10],
        9: [6, 8, 10, 11],
        10: [2, 5, 9, 11],
        11: [1, 5, 6, 10],
    }
    return [rows[center] for center in range(12)]


def _row_pair_stats(rows: Sequence[Sequence[int]]) -> dict[str, object]:
    max_intersection = 0
    violations: list[dict[str, object]] = []
    for left, right in combinations(range(len(rows)), 2):
        inter = sorted(set(rows[left]) & set(rows[right]))
        max_intersection = max(max_intersection, len(inter))
        if len(inter) > 2:
            violations.append(
                {
                    "centers": [left, right],
                    "intersection": inter,
                    "intersection_size": len(inter),
                }
            )
    return {
        "max_row_intersection": max_intersection,
        "row_pair_cap_ok": not violations,
        "row_pair_cap_violations": violations,
    }


def _column_pair_violations(rows: Sequence[Sequence[int]]) -> list[dict[str, object]]:
    violations: list[dict[str, object]] = []
    for left, right in combinations(range(len(rows)), 2):
        centers = [
            center for center, row in enumerate(rows) if left in row and right in row
        ]
        if len(centers) > 2:
            violations.append(
                {"pair": [left, right], "centers": centers, "count": len(centers)}
            )
    return violations


def fixed_pattern_summary(
    name: str,
    rows: Pattern,
    order: Sequence[int] | None = None,
) -> dict[str, object]:
    """Return exact fixed-pattern diagnostics for a negative control."""

    if order is None:
        order = list(range(len(rows)))
    filters = filter_summary(rows, order)
    ear = forward_ear_order(rows)
    stuck = find_minimal_stuck_sets(rows, max_examples=2)
    vertex_circle = vertex_circle_order_obstruction(rows, order, name)
    column_violations = _column_pair_violations(rows)
    return {
        "type": "bridge_negative_control_fixed_pattern",
        "name": name,
        "n": len(rows),
        "selected_rows": rows,
        **_row_pair_stats(rows),
        "column_pair_cap_ok": not column_violations,
        "column_pair_cap_violations": column_violations,
        "phi_edges": filters["phi_edges"],
        "crossing_bisector_violations": filters["crossing_bisector_violations"],
        "odd_forced_perpendicular_cycle_length": filters["odd_cycle_length"],
        "rectangle_trap_4_cycles": filters["rectangle_trap_4_cycles"],
        "forward_ear_order": {
            "exists": ear.exists,
            "seed": ear.seed,
            "order": ear.order,
            "largest_closure_size": ear.largest_closure_size,
            "largest_closure_seed": ear.largest_closure_seed,
        },
        "minimal_stuck_set": {
            "size": stuck.minimal_size,
            "count_at_size": stuck.total_at_minimal_size,
            "examples": [
                {
                    "vertices": example.vertices,
                    "internal_counts": [
                        row.internal_count for row in example.rows
                    ],
                }
                for example in stuck.examples
            ],
        },
        "vertex_circle_in_supplied_order": order_result_to_json(vertex_circle),
        "interpretation": (
            "Fixed selected-witness pattern diagnostics only; passing any "
            "incidence filter here is not a Euclidean realization certificate."
        ),
    }


def c13_sidon_negative_control() -> dict[str, object]:
    """Return the exact C13 linear/Sidon negative-control certificate."""

    rows = c13_sidon_rows()
    witness_map = {vertex: (vertex - 1) % 13 for vertex in range(13)}
    fragile = check_fragile_hypergraph(
        13,
        {center: row for center, row in enumerate(rows)},
        witness_map=witness_map,
    )
    payload = fixed_pattern_summary("C13_sidon_1_2_4_10", rows)
    payload["fragile_cover_all_rows"] = {
        **check_to_json(fragile),
        "witness_map": {str(vertex): center for vertex, center in witness_map.items()},
    }
    payload["interpretation"] = (
        "Abstract linear selected-witness negative control. The fixed C13 "
        "Sidon pattern is already killed across all cyclic orders by the "
        "repo's exact Kalmanson/Farkas search; this certificate is only a "
        "guardrail against incidence-only bridge claims."
    )
    return payload


def output7_two_block_negative_control() -> dict[str, object]:
    """Return the abstract no-forward-ear two-block control."""

    return fixed_pattern_summary(
        "two_block_full_extension_no_forward_ear",
        output7_two_block_rows(),
        order=[0, 4, 3, 1, 2, 5, 6, 10, 9, 7, 8, 11],
    )


def false_output8_correction_certificate() -> dict[str, object]:
    """Return the correction for the false no-ear claim in outputs 8/10."""

    rows = false_output8_two_block_rows()
    return fixed_pattern_summary(
        "false_no_ear_two_block_table_from_outputs_8_10",
        rows,
    )


def _sympy():
    try:
        import sympy as sp  # type: ignore
    except ImportError as exc:  # pragma: no cover - depends on dev dependency
        raise RuntimeError("SymPy is required for this exact certificate") from exc
    return sp


def block6_geometric_atom_certificate() -> dict[str, object]:
    """Verify the exact six-label fragile atom over ``Q(sqrt(3))``."""

    sp = _sympy()
    sqrt3 = sp.sqrt(3)
    points = {
        0: (sp.Rational(0), sp.Rational(0)),
        1: (sp.Rational(-5, 13), sp.Rational(12, 13)),
        2: (sp.Rational(1, 2), sqrt3 / 2),
        3: (sp.Rational(1), sp.Rational(0)),
        4: (sp.Rational(1, 2), -sqrt3 / 2),
        5: (sp.Rational(2, 5), sp.Rational(-4, 5)),
    }
    order = [0, 1, 2, 3, 4, 5]
    rows = {0: [1, 2, 3, 4], 3: [0, 2, 4, 5]}

    def det(a: int, b: int, c: int):
        ax, ay = points[a]
        bx, by = points[b]
        cx, cy = points[c]
        return sp.simplify((bx - ax) * (cy - ay) - (by - ay) * (cx - ax))

    def dist2(a: int, b: int):
        ax, ay = points[a]
        bx, by = points[b]
        return sp.simplify((ax - bx) ** 2 + (ay - by) ** 2)

    side_values = []
    strict_convex = True
    for idx, left in enumerate(order):
        right = order[(idx + 1) % len(order)]
        edge_values = [
            det(left, right, label)
            for label in order
            if label not in {left, right}
        ]
        side_values.append([str(sp.simplify(value)) for value in edge_values])
        strict_convex = strict_convex and all(value.is_negative for value in edge_values)

    distance_rows = {
        center: {label: str(dist2(center, label)) for label in range(6) if label != center}
        for center in (0, 3)
    }
    row_equalities_ok = all(dist2(0, label) == 1 for label in rows[0]) and all(
        dist2(3, label) == 1 for label in rows[3]
    )
    uniqueness_ok = dist2(0, 5) != 1 and dist2(3, 1) != 1
    fragile = check_fragile_hypergraph(6, rows, witness_map={0: 3, 1: 0, 2: 0, 3: 0, 4: 0, 5: 3})

    return {
        "type": "block6_geometric_atom_certificate",
        "status": "EXACT_GEOMETRIC_NEGATIVE_CONTROL",
        "field": "Q(sqrt(3))",
        "n": 6,
        "order": order,
        "points": {
            str(label): [str(coord) for coord in coords]
            for label, coords in points.items()
        },
        "fragile_rows": {str(center): row for center, row in rows.items()},
        "strict_convex_clockwise": strict_convex,
        "edge_side_determinants": side_values,
        "distance_rows": distance_rows,
        "row_equalities_ok": row_equalities_ok,
        "unique_size4_rows_at_fragile_centers": uniqueness_ok,
        "fragile_hypergraph": check_to_json(fragile),
        "source_witness_chords_cross": chords_cross_in_order((0, 3), (2, 4), order),
        "forced_dependency_cycle": [[0, 3], [3, 0]],
        "interpretation": (
            "Exact strict-convex realization of the fragile rows only. The "
            "non-fragile centers are not bad, so this is not a counterexample "
            "and not a full selected-witness realization."
        ),
    }
