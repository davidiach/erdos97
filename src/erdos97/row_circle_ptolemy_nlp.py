"""Row-circle Ptolemy fixed-order nonlinear diagnostics.

This module strengthens the Ptolemy-order NLP relaxation by adding the
Ptolemy equality for each selected witness quadruple.  If row ``i`` is
realized, its four selected witnesses lie on a circle centered at ``i``; in
their angular order around ``i`` they satisfy Ptolemy with equality.

The solve here is numerical only.  A reported obstruction is a target for
exactification, not an exact certificate.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Sequence

from erdos97.min_radius_filter import angular_witness_order
from erdos97.ptolemy_order_nlp import _linear_relaxation_problem, _optimization
from erdos97.altman_diagonal_sums import _validate_order

Pattern = Sequence[Sequence[int]]


@dataclass(frozen=True)
class RowCirclePtolemyNLPResult:
    pattern: str
    n: int
    order: list[int]
    trust_label: str
    status: str
    obstructed: bool | None
    distance_class_count: int
    linear_inequality_count: int
    ptolemy_inequality_count: int
    row_ptolemy_equality_count: int
    max_margin: float | None
    tolerance: float
    optimizer_success: bool
    optimizer_iterations: int | None
    optimizer_message: str
    linear_min_slack: float | None
    ptolemy_min_slack: float | None
    row_ptolemy_max_abs_residual: float | None
    row_ptolemy_rms_residual: float | None
    tight_linear_count: int
    tight_ptolemy_count: int


def _ptolemy_value(x, indices: tuple[int, int, int, int, int, int]) -> float:
    ac, bd, ab, cd, bc, ad = indices
    return x[ab] * x[cd] + x[bc] * x[ad] - x[ac] * x[bd]


def row_circle_ptolemy_nlp_diagnostic(
    S: Pattern,
    order: Sequence[int] | None = None,
    pattern: str = "",
    *,
    tolerance: float = 1e-8,
    maxiter: int = 3000,
) -> RowCirclePtolemyNLPResult:
    """Run the row-circle Ptolemy nonlinear diagnostic for one fixed order."""

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
    class_count = len(class_reps)
    if not lp_result.success:
        return RowCirclePtolemyNLPResult(
            pattern=pattern,
            n=n,
            order=order,
            trust_label="NUMERICAL_NONLINEAR_DIAGNOSTIC",
            status="ROW_CIRCLE_PTOLEMY_NLP_INITIAL_LP_FAILED",
            obstructed=None,
            distance_class_count=class_count,
            linear_inequality_count=int(linear_rows.shape[0]),
            ptolemy_inequality_count=0,
            row_ptolemy_equality_count=0,
            max_margin=None,
            tolerance=tolerance,
            optimizer_success=False,
            optimizer_iterations=None,
            optimizer_message=str(lp_result.message),
            linear_min_slack=None,
            ptolemy_min_slack=None,
            row_ptolemy_max_abs_residual=None,
            row_ptolemy_rms_residual=None,
            tight_linear_count=0,
            tight_ptolemy_count=0,
        )

    _, minimize = _optimization()
    ptolemy_indices = [
        (
            class_idx(a, c),
            class_idx(b, d),
            class_idx(a, b),
            class_idx(c, d),
            class_idx(b, c),
            class_idx(a, d),
        )
        for a, b, c, d in combinations(order, 4)
    ]
    row_ptolemy_indices = []
    for center in range(n):
        a, b, c, d = angular_witness_order(order, center, S[center])
        row_ptolemy_indices.append(
            (
                class_idx(a, c),
                class_idx(b, d),
                class_idx(a, b),
                class_idx(c, d),
                class_idx(b, c),
                class_idx(a, d),
            )
        )

    def linear_slacks(variables):
        return -linear_rows @ variables

    def ptolemy_slacks(variables):
        x = variables[:class_count]
        return np.array([_ptolemy_value(x, item) for item in ptolemy_indices])

    def row_ptolemy_residuals(variables):
        x = variables[:class_count]
        return np.array([_ptolemy_value(x, item) for item in row_ptolemy_indices])

    def objective(variables):
        return -variables[class_count]

    start = lp_result.x.copy()
    start[class_count] = min(float(start[class_count]), 1e-4)
    start[:class_count] = 0.85 * start[:class_count] + 0.15 / class_count
    constraints = [
        {"type": "eq", "fun": lambda variables: np.sum(variables[:class_count]) - 1.0},
        {"type": "ineq", "fun": linear_slacks},
        {"type": "ineq", "fun": ptolemy_slacks},
        {"type": "eq", "fun": row_ptolemy_residuals},
    ]
    result = minimize(
        objective,
        start,
        method="SLSQP",
        bounds=[(0.0, None)] * class_count + [(None, None)],
        constraints=constraints,
        options={"maxiter": maxiter, "ftol": 1e-12, "disp": False},
    )

    lin = linear_slacks(result.x)
    ptolemy = ptolemy_slacks(result.x)
    row_residuals = row_ptolemy_residuals(result.x)
    row_abs = np.abs(row_residuals)
    row_rms = float(np.sqrt(np.mean(row_residuals * row_residuals)))
    margin = float(result.x[class_count])
    feasible = bool(
        lin.min() >= -tolerance
        and ptolemy.min() >= -tolerance
        and row_abs.max() <= tolerance
    )

    if not result.success:
        status = "ROW_CIRCLE_PTOLEMY_NLP_FAILED"
        obstructed = None
    elif not feasible:
        status = "ROW_CIRCLE_PTOLEMY_NLP_INFEASIBLE_RESULT"
        obstructed = None
    else:
        obstructed = margin <= tolerance
        status = (
            "ROW_CIRCLE_PTOLEMY_NLP_NUMERICAL_OBSTRUCTION"
            if obstructed
            else "PASS_ROW_CIRCLE_PTOLEMY_NLP_RELAXATION"
        )

    return RowCirclePtolemyNLPResult(
        pattern=pattern,
        n=n,
        order=order,
        trust_label="NUMERICAL_NONLINEAR_DIAGNOSTIC",
        status=status,
        obstructed=obstructed,
        distance_class_count=class_count,
        linear_inequality_count=int(linear_rows.shape[0]),
        ptolemy_inequality_count=len(ptolemy_indices),
        row_ptolemy_equality_count=len(row_ptolemy_indices),
        max_margin=margin,
        tolerance=tolerance,
        optimizer_success=bool(result.success),
        optimizer_iterations=int(getattr(result, "nit", 0)),
        optimizer_message=str(result.message),
        linear_min_slack=float(lin.min()),
        ptolemy_min_slack=float(ptolemy.min()),
        row_ptolemy_max_abs_residual=float(row_abs.max()),
        row_ptolemy_rms_residual=row_rms,
        tight_linear_count=int((lin <= tolerance).sum()),
        tight_ptolemy_count=int((ptolemy <= tolerance).sum()),
    )


def result_to_json(result: RowCirclePtolemyNLPResult) -> dict[str, object]:
    """Return a JSON-serializable result."""

    return {
        "type": "row_circle_ptolemy_nlp_diagnostic",
        "pattern": result.pattern,
        "n": result.n,
        "order": result.order,
        "trust_label": result.trust_label,
        "status": result.status,
        "obstructed": result.obstructed,
        "distance_class_count": result.distance_class_count,
        "linear_inequality_count": result.linear_inequality_count,
        "ptolemy_inequality_count": result.ptolemy_inequality_count,
        "row_ptolemy_equality_count": result.row_ptolemy_equality_count,
        "max_margin": result.max_margin,
        "tolerance": result.tolerance,
        "optimizer_success": result.optimizer_success,
        "optimizer_iterations": result.optimizer_iterations,
        "optimizer_message": result.optimizer_message,
        "linear_min_slack": result.linear_min_slack,
        "ptolemy_min_slack": result.ptolemy_min_slack,
        "row_ptolemy_max_abs_residual": result.row_ptolemy_max_abs_residual,
        "row_ptolemy_rms_residual": result.row_ptolemy_rms_residual,
        "tight_linear_count": result.tight_linear_count,
        "tight_ptolemy_count": result.tight_ptolemy_count,
        "semantics": (
            "Numerical fixed-order nonlinear relaxation over ordinary distance "
            "classes with global Ptolemy inequalities and row-circle Ptolemy "
            "equalities. Passing is not evidence of geometric realizability; "
            "failure or numerical obstruction requires exactification before "
            "it can be treated as an exact obstruction."
        ),
    }
