"""Ptolemy-strengthened fixed-order nonlinear diagnostics.

This module extends the metric-order LP relaxation by adding Ptolemy
inequalities for every cyclic quadrilateral.  The resulting SLSQP solve is a
numerical nonlinear diagnostic only; a pass is not evidence of realizability,
and a failure would require exactification before use as an obstruction.
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

Pattern = Sequence[Sequence[int]]


@dataclass(frozen=True)
class PtolemyOrderNLPResult:
    pattern: str
    n: int
    order: list[int]
    trust_label: str
    status: str
    obstructed: bool | None
    distance_class_count: int
    linear_inequality_count: int
    ptolemy_inequality_count: int
    max_margin: float | None
    tolerance: float
    optimizer_success: bool
    optimizer_iterations: int | None
    optimizer_message: str
    linear_min_slack: float | None
    ptolemy_min_slack: float | None
    tight_linear_count: int
    tight_ptolemy_count: int


def _linear_relaxation_problem(S: Pattern, order: Sequence[int]):
    np, linprog = _linear_programming()
    n = len(S)
    uf = _distance_class_union_find(S)
    class_reps, diagonal_rows = _diagonal_coefficient_rows(S, order)
    class_index = {distance_class: idx for idx, distance_class in enumerate(class_reps)}

    variable_count = len(class_reps) + 1
    gamma_index = len(class_reps)
    rows = []

    for lower_row, upper_row in zip(diagonal_rows, diagonal_rows[1:]):
        diff = upper_row - lower_row
        coefficients = np.zeros(variable_count)
        coefficients[: len(class_reps)] = -diff
        coefficients[gamma_index] = 1.0
        rows.append(coefficients)

    strict_edges, _completed_rows = vertex_circle_strict_inequalities(S, order)
    for edge in strict_edges:
        coefficients = np.zeros(variable_count)
        coefficients[gamma_index] = 1.0
        if edge.outer_class != edge.inner_class:
            coefficients[class_index[edge.outer_class]] = -1.0
            coefficients[class_index[edge.inner_class]] = 1.0
        rows.append(coefficients)

    def class_idx(a: int, b: int) -> int:
        return class_index[uf.find(pair(a, b))]

    for a, b, c in combinations(range(n), 3):
        ab = class_idx(a, b)
        ac = class_idx(a, c)
        bc = class_idx(b, c)
        for left, right_1, right_2 in (
            (ab, ac, bc),
            (ac, ab, bc),
            (bc, ab, ac),
        ):
            coefficients = np.zeros(variable_count)
            coefficients[left] = 1.0
            coefficients[right_1] -= 1.0
            coefficients[right_2] -= 1.0
            rows.append(coefficients)

    objective = np.zeros(variable_count)
    objective[gamma_index] = -1.0
    equality = np.zeros((1, variable_count))
    equality[0, : len(class_reps)] = 1.0
    linear_rows = np.array(rows)
    lp_result = linprog(
        objective,
        A_ub=linear_rows,
        b_ub=np.zeros(linear_rows.shape[0]),
        A_eq=equality,
        b_eq=np.array([1.0]),
        bounds=[(0.0, None)] * len(class_reps) + [(None, None)],
        method="highs",
    )
    return np, class_reps, class_idx, linear_rows, lp_result


def ptolemy_order_nlp_diagnostic(
    S: Pattern,
    order: Sequence[int] | None = None,
    pattern: str = "",
    *,
    tolerance: float = 1e-8,
    maxiter: int = 1500,
) -> PtolemyOrderNLPResult:
    """Run the Ptolemy-strengthened nonlinear diagnostic for one fixed order."""

    if tolerance < 0:
        raise ValueError("tolerance must be nonnegative")
    if maxiter <= 0:
        raise ValueError("maxiter must be positive")
    n = len(S)
    if order is None:
        order = list(range(n))
    order = list(order)
    _validate_order(order, n)

    np, class_reps, class_idx, linear_rows, lp_result = _linear_relaxation_problem(
        S,
        order,
    )
    _, minimize = _optimization()
    if not lp_result.success:
        return PtolemyOrderNLPResult(
            pattern=pattern,
            n=n,
            order=order,
            trust_label="NUMERICAL_NONLINEAR_DIAGNOSTIC",
            status="PTOLEMY_ORDER_NLP_INITIAL_LP_FAILED",
            obstructed=None,
            distance_class_count=len(class_reps),
            linear_inequality_count=int(linear_rows.shape[0]),
            ptolemy_inequality_count=0,
            max_margin=None,
            tolerance=tolerance,
            optimizer_success=False,
            optimizer_iterations=None,
            optimizer_message=str(lp_result.message),
            linear_min_slack=None,
            ptolemy_min_slack=None,
            tight_linear_count=0,
            tight_ptolemy_count=0,
        )

    ptolemy_indices = []
    for a, b, c, d in combinations(order, 4):
        ptolemy_indices.append(
            (
                class_idx(a, c),
                class_idx(b, d),
                class_idx(a, b),
                class_idx(c, d),
                class_idx(b, c),
                class_idx(a, d),
            )
        )

    class_count = len(class_reps)

    def linear_slacks(variables):
        return -linear_rows @ variables

    def ptolemy_slacks(variables):
        x = variables[:class_count]
        return np.array(
            [
                x[ab] * x[cd] + x[bc] * x[ad] - x[ac] * x[bd]
                for ac, bd, ab, cd, bc, ad in ptolemy_indices
            ]
        )

    def objective(variables):
        return -variables[class_count]

    start = lp_result.x.copy()
    start[class_count] = min(float(start[class_count]), 1e-4)
    start[:class_count] = 0.85 * start[:class_count] + 0.15 / class_count
    constraints = [
        {"type": "eq", "fun": lambda variables: np.sum(variables[:class_count]) - 1.0},
        {"type": "ineq", "fun": linear_slacks},
        {"type": "ineq", "fun": ptolemy_slacks},
    ]
    result = minimize(
        objective,
        start,
        method="SLSQP",
        bounds=[(0.0, None)] * class_count + [(None, None)],
        constraints=constraints,
        options={"maxiter": maxiter, "ftol": 1e-12, "disp": False},
    )
    if not result.success:
        return PtolemyOrderNLPResult(
            pattern=pattern,
            n=n,
            order=order,
            trust_label="NUMERICAL_NONLINEAR_DIAGNOSTIC",
            status="PTOLEMY_ORDER_NLP_FAILED",
            obstructed=None,
            distance_class_count=class_count,
            linear_inequality_count=int(linear_rows.shape[0]),
            ptolemy_inequality_count=len(ptolemy_indices),
            max_margin=None,
            tolerance=tolerance,
            optimizer_success=False,
            optimizer_iterations=int(getattr(result, "nit", 0)),
            optimizer_message=str(result.message),
            linear_min_slack=None,
            ptolemy_min_slack=None,
            tight_linear_count=0,
            tight_ptolemy_count=0,
        )

    lin = linear_slacks(result.x)
    ptolemy = ptolemy_slacks(result.x)
    margin = float(result.x[class_count])
    feasible = bool(lin.min() >= -tolerance and ptolemy.min() >= -tolerance)
    obstructed = None if not feasible else margin <= tolerance
    return PtolemyOrderNLPResult(
        pattern=pattern,
        n=n,
        order=order,
        trust_label="NUMERICAL_NONLINEAR_DIAGNOSTIC",
        status=(
            "PASS_PTOLEMY_ORDER_NLP_RELAXATION"
            if obstructed is False
            else (
                "PTOLEMY_ORDER_NLP_NUMERICAL_OBSTRUCTION"
                if obstructed is True
                else "PTOLEMY_ORDER_NLP_INFEASIBLE_RESULT"
            )
        ),
        obstructed=obstructed,
        distance_class_count=class_count,
        linear_inequality_count=int(linear_rows.shape[0]),
        ptolemy_inequality_count=len(ptolemy_indices),
        max_margin=margin,
        tolerance=tolerance,
        optimizer_success=bool(result.success),
        optimizer_iterations=int(getattr(result, "nit", 0)),
        optimizer_message=str(result.message),
        linear_min_slack=float(lin.min()),
        ptolemy_min_slack=float(ptolemy.min()),
        tight_linear_count=int((lin <= tolerance).sum()),
        tight_ptolemy_count=int((ptolemy <= tolerance).sum()),
    )


def result_to_json(result: PtolemyOrderNLPResult) -> dict[str, object]:
    """Return a JSON-serializable result."""

    return {
        "type": "ptolemy_order_nlp_diagnostic",
        "pattern": result.pattern,
        "n": result.n,
        "order": result.order,
        "trust_label": result.trust_label,
        "status": result.status,
        "obstructed": result.obstructed,
        "distance_class_count": result.distance_class_count,
        "linear_inequality_count": result.linear_inequality_count,
        "ptolemy_inequality_count": result.ptolemy_inequality_count,
        "max_margin": result.max_margin,
        "tolerance": result.tolerance,
        "optimizer_success": result.optimizer_success,
        "optimizer_iterations": result.optimizer_iterations,
        "optimizer_message": result.optimizer_message,
        "linear_min_slack": result.linear_min_slack,
        "ptolemy_min_slack": result.ptolemy_min_slack,
        "tight_linear_count": result.tight_linear_count,
        "tight_ptolemy_count": result.tight_ptolemy_count,
        "semantics": (
            "Numerical fixed-order nonlinear relaxation over ordinary distance "
            "classes with Ptolemy inequalities. Passing is not evidence of "
            "geometric realizability; failure requires exactification before "
            "it can be treated as an obstruction."
        ),
    }


def _optimization():
    try:
        import numpy as np  # type: ignore
        from scipy.optimize import minimize  # type: ignore
    except ImportError as exc:  # pragma: no cover - depends on dev deps
        raise RuntimeError("NumPy and SciPy are required for Ptolemy NLP diagnostics") from exc
    return np, minimize
