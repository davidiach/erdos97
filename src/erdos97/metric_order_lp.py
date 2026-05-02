"""Combined metric LP diagnostics for fixed cyclic orders.

The relaxation uses ordinary distance variables quotiented by the selected-row
equalities.  It combines Altman's adjacent diagonal-sum gaps, vertex-circle
strict chord inequalities, and optional triangle inequalities.  Passing this
LP is not evidence of realizability; failing it is only a numerical linear
diagnostic unless separately exactified.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Sequence

from erdos97.altman_diagonal_sums import (
    _diagonal_coefficient_rows,
    _distance_class_union_find,
    _linear_programming,
    _validate_order,
    pair,
)
from erdos97.vertex_circle_order_filter import vertex_circle_strict_inequalities

Pair = tuple[int, int]
Pattern = Sequence[Sequence[int]]


@dataclass(frozen=True)
class MetricOrderLPResult:
    pattern: str
    n: int
    order: list[int]
    trust_label: str
    status: str
    obstructed: bool | None
    include_triangle_inequalities: bool
    distance_class_count: int
    altman_gap_count: int
    vertex_strict_edge_count: int
    vertex_self_edge_count: int
    triangle_inequality_count: int
    total_inequality_count: int
    max_margin: float | None
    tolerance: float
    tight_altman_gap_count: int
    tight_vertex_strict_count: int
    tight_triangle_inequality_count: int
    message: str


def metric_order_lp_diagnostic(
    S: Pattern,
    order: Sequence[int] | None = None,
    pattern: str = "",
    *,
    include_triangle_inequalities: bool = True,
    tolerance: float = 1e-9,
) -> MetricOrderLPResult:
    """Run the combined fixed-order metric LP diagnostic.

    The LP maximizes one shared strictness margin ``gamma`` subject to:

    - Altman adjacent diagonal gaps ``U_{k+1} - U_k >= gamma``;
    - vertex-circle strict chord inequalities ``d_outer - d_inner >= gamma``;
    - optional metric triangle inequalities ``d_ab <= d_ac + d_bc``.

    Distance variables are nonnegative selected-distance classes normalized by
    ``sum x = 1``.  This is only a relaxation of convex Euclidean geometry.
    """

    if tolerance < 0:
        raise ValueError("tolerance must be nonnegative")
    np, linprog = _linear_programming()
    n = len(S)
    if order is None:
        order = list(range(n))
    order = list(order)
    _validate_order(order, n)
    class_reps, diagonal_rows = _diagonal_coefficient_rows(S, order)
    class_index = {distance_class: idx for idx, distance_class in enumerate(class_reps)}
    uf = _distance_class_union_find(S)

    coefficient_rows = []
    bounds = []
    kinds: list[str] = []

    def add_inequality(coefficients, bound: float, kind: str) -> None:
        coefficient_rows.append(coefficients)
        bounds.append(bound)
        kinds.append(kind)

    variable_count = len(class_reps) + 1
    gamma_index = len(class_reps)

    for lower_row, upper_row in zip(diagonal_rows, diagonal_rows[1:]):
        diff = upper_row - lower_row
        coefficients = np.zeros(variable_count)
        coefficients[: len(class_reps)] = -diff
        coefficients[gamma_index] = 1.0
        add_inequality(coefficients, 0.0, "altman")

    strict_edges, _completed_rows = vertex_circle_strict_inequalities(S, order)
    vertex_self_edge_count = 0
    for edge in strict_edges:
        coefficients = np.zeros(variable_count)
        coefficients[gamma_index] = 1.0
        if edge.outer_class == edge.inner_class:
            vertex_self_edge_count += 1
        else:
            coefficients[class_index[edge.outer_class]] = -1.0
            coefficients[class_index[edge.inner_class]] = 1.0
        add_inequality(coefficients, 0.0, "vertex")

    triangle_count = 0
    if include_triangle_inequalities:
        for a, b, c in combinations(range(n), 3):
            ab = class_index[uf.find(pair(a, b))]
            ac = class_index[uf.find(pair(a, c))]
            bc = class_index[uf.find(pair(b, c))]
            for left, right_1, right_2 in (
                (ab, ac, bc),
                (ac, ab, bc),
                (bc, ab, ac),
            ):
                coefficients = np.zeros(variable_count)
                coefficients[left] = 1.0
                coefficients[right_1] -= 1.0
                coefficients[right_2] -= 1.0
                add_inequality(coefficients, 0.0, "triangle")
                triangle_count += 1

    objective = np.zeros(variable_count)
    objective[gamma_index] = -1.0
    equality = np.zeros((1, variable_count))
    equality[0, : len(class_reps)] = 1.0
    result = linprog(
        objective,
        A_ub=np.array(coefficient_rows),
        b_ub=np.array(bounds),
        A_eq=equality,
        b_eq=np.array([1.0]),
        bounds=[(0.0, None)] * len(class_reps) + [(None, None)],
        method="highs",
    )
    if not result.success:
        return MetricOrderLPResult(
            pattern=pattern,
            n=n,
            order=order,
            trust_label="NUMERICAL_LINEAR_DIAGNOSTIC",
            status="METRIC_ORDER_LP_FAILED",
            obstructed=None,
            include_triangle_inequalities=include_triangle_inequalities,
            distance_class_count=len(class_reps),
            altman_gap_count=max(0, len(diagonal_rows) - 1),
            vertex_strict_edge_count=len(strict_edges),
            vertex_self_edge_count=vertex_self_edge_count,
            triangle_inequality_count=triangle_count,
            total_inequality_count=len(coefficient_rows),
            max_margin=None,
            tolerance=tolerance,
            tight_altman_gap_count=0,
            tight_vertex_strict_count=0,
            tight_triangle_inequality_count=0,
            message=str(result.message),
        )

    margin = float(result.x[gamma_index])
    slacks = np.array(bounds) - np.array(coefficient_rows) @ result.x
    kinds_array = np.array(kinds)

    def tight_count(kind: str) -> int:
        return int(((slacks <= tolerance) & (kinds_array == kind)).sum())

    obstructed = margin <= tolerance
    return MetricOrderLPResult(
        pattern=pattern,
        n=n,
        order=order,
        trust_label="NUMERICAL_LINEAR_DIAGNOSTIC",
        status=(
            "METRIC_ORDER_LP_NUMERICAL_OBSTRUCTION"
            if obstructed
            else "PASS_METRIC_ORDER_LP_RELAXATION"
        ),
        obstructed=obstructed,
        include_triangle_inequalities=include_triangle_inequalities,
        distance_class_count=len(class_reps),
        altman_gap_count=max(0, len(diagonal_rows) - 1),
        vertex_strict_edge_count=len(strict_edges),
        vertex_self_edge_count=vertex_self_edge_count,
        triangle_inequality_count=triangle_count,
        total_inequality_count=len(coefficient_rows),
        max_margin=margin,
        tolerance=tolerance,
        tight_altman_gap_count=tight_count("altman"),
        tight_vertex_strict_count=tight_count("vertex"),
        tight_triangle_inequality_count=tight_count("triangle"),
        message=(
            "The fixed order passes this combined linear relaxation."
            if not obstructed
            else "The fixed order has no positive shared strictness margin in this relaxation."
        ),
    )


def result_to_json(result: MetricOrderLPResult) -> dict[str, object]:
    """Return a JSON-serializable result."""

    return {
        "type": "metric_order_lp_diagnostic",
        "pattern": result.pattern,
        "n": result.n,
        "order": result.order,
        "trust_label": result.trust_label,
        "status": result.status,
        "obstructed": result.obstructed,
        "include_triangle_inequalities": result.include_triangle_inequalities,
        "distance_class_count": result.distance_class_count,
        "altman_gap_count": result.altman_gap_count,
        "vertex_strict_edge_count": result.vertex_strict_edge_count,
        "vertex_self_edge_count": result.vertex_self_edge_count,
        "triangle_inequality_count": result.triangle_inequality_count,
        "total_inequality_count": result.total_inequality_count,
        "max_margin": result.max_margin,
        "tolerance": result.tolerance,
        "tight_altman_gap_count": result.tight_altman_gap_count,
        "tight_vertex_strict_count": result.tight_vertex_strict_count,
        "tight_triangle_inequality_count": result.tight_triangle_inequality_count,
        "message": result.message,
        "semantics": (
            "Numerical fixed-order linear relaxation over ordinary distance "
            "classes. Passing is not evidence of geometric realizability; "
            "failure requires exactification before it can be treated as an "
            "exact obstruction."
        ),
    }
