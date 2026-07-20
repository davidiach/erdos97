"""Exact marked-root Gram helpers for polynomial quartic graph samples.

The lifted variable is the symmetric Gram matrix ``A = a a^T`` for

    f_a(t) = a_1 t + a_2 t^2 + a_3 t^3 + a_4 t^4.

For fixed rational parameters, each prescribed four-witness row gives three
affine equations in the ten upper-triangular entries of ``A``.  Linear
feasibility is only a relaxation: a planar quartic graph additionally needs
``A`` to be nonzero, positive semidefinite, and rank one.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from itertools import combinations
from math import isqrt
from typing import Iterable, Sequence


SCHEMA = "erdos97.quartic_marked_root_gram.v1"

GRAM_PAIRS: tuple[tuple[int, int], ...] = tuple(
    (left, right)
    for left in range(1, 5)
    for right in range(left, 5)
)
PAIR_INDEX = {pair: index for index, pair in enumerate(GRAM_PAIRS)}
VARIABLE_COUNT = len(GRAM_PAIRS)

Equation = tuple[Fraction, ...]
Rref = tuple[Equation, ...]


@dataclass(frozen=True)
class AffineSolution:
    """Canonical description of a consistent rational affine system."""

    rref: Rref
    pivots: tuple[int, ...]
    free_columns: tuple[int, ...]
    particular: tuple[Fraction, ...]
    nullspace: tuple[tuple[Fraction, ...], ...]

    @property
    def rank(self) -> int:
        return len(self.pivots)

    @property
    def dimension(self) -> int:
        return len(self.free_columns)


@dataclass(frozen=True)
class RankOneCheck:
    """Exact nonlinear gate for one fully specified symmetric Gram matrix."""

    rank_one: bool
    positive_semidefinite: bool
    degree_four: bool
    pivot_index: int | None

    @property
    def quartic_gram(self) -> bool:
        return self.rank_one and self.positive_semidefinite and self.degree_four


@dataclass(frozen=True)
class LineRankOneResult:
    """Rank-one intersection of an affine Gram line with the minor variety."""

    kind: str
    rational_parameters: tuple[Fraction, ...] = ()
    irreducible_quadratic: tuple[Fraction, Fraction, Fraction] | None = None


@dataclass(frozen=True)
class AnchorTripleSummary:
    """Exact accounting for one three-center marked-row scan."""

    parameters: tuple[Fraction, ...]
    centers: tuple[Fraction, Fraction, Fraction]
    quartet_count_per_center: int
    raw_triple_count: int
    overlap_admissible_count: int
    pair_inconsistent_pruned_triple_count: int
    inconsistent_count: int
    rank_counts: tuple[tuple[int, int], ...]
    line_without_real_rank_at_most_one_count: int
    line_zero_matrix_root_count: int
    line_negative_semidefinite_rank_one_root_count: int
    line_lower_degree_rank_one_psd_root_count: int
    line_rational_quartic_gram_count: int
    line_irrational_rank_at_most_one_component_count: int
    line_all_rank_at_most_one_count: int
    exceptional_affine_state_count: int
    sample_survivors: tuple[dict[str, object], ...]
    exceptional_rrefs: tuple[Rref, ...] = field(repr=False, compare=False)
    unresolved_line_rrefs: tuple[Rref, ...] = field(repr=False, compare=False)
    rank_one_quartic_grams: tuple[tuple[Fraction, ...], ...] = field(
        repr=False,
        compare=False,
    )


@dataclass(frozen=True)
class QuarticClosurePilotSummary:
    """Full fixed-grid continuation from anchors through every other center."""

    anchor: AnchorTripleSummary
    extension_centers: tuple[Fraction, ...]
    extension_steps: tuple[dict[str, int | str], ...]
    unresolved_affine_state_count: int
    rank_one_quartic_candidate_count: int
    convex_rank_one_candidate_count: int
    all_row_quartic_candidate_count: int
    strict_finite_full_closure_candidate_count: int
    continuous_convex_full_closure_candidate_count: int
    sample_candidates: tuple[dict[str, object], ...]


def _as_fraction(value: int | Fraction) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"expected an exact integer or Fraction, got {value!r}")
    return Fraction(value)


def validate_parameters(parameters: Sequence[int | Fraction]) -> tuple[Fraction, ...]:
    """Return a distinct, increasing tuple of exact parameters."""

    values = tuple(_as_fraction(value) for value in parameters)
    if len(values) < 5:
        raise ValueError("at least five parameters are required")
    if len(set(values)) != len(values):
        raise ValueError("parameters must be distinct")
    if tuple(sorted(values)) != values:
        raise ValueError("parameters must be strictly increasing")
    return values


def gram_upper_from_coefficients(
    coefficients: Sequence[int | Fraction],
) -> tuple[Fraction, ...]:
    """Return upper-triangular entries of ``a a^T`` in ``GRAM_PAIRS`` order."""

    if len(coefficients) != 4:
        raise ValueError("quartic graph coefficient vector must have length four")
    values = tuple(_as_fraction(value) for value in coefficients)
    return tuple(values[left - 1] * values[right - 1] for left, right in GRAM_PAIRS)


def gram_matrix(upper: Sequence[int | Fraction]) -> tuple[tuple[Fraction, ...], ...]:
    """Expand ten upper-triangular values to a symmetric 4 by 4 matrix."""

    if len(upper) != VARIABLE_COUNT:
        raise ValueError(f"expected {VARIABLE_COUNT} upper-triangular entries")
    values = tuple(_as_fraction(value) for value in upper)
    rows = [[Fraction(0) for _ in range(4)] for _ in range(4)]
    for value, (left, right) in zip(values, GRAM_PAIRS, strict=True):
        rows[left - 1][right - 1] = value
        rows[right - 1][left - 1] = value
    return tuple(tuple(row) for row in rows)


def polynomial_value(
    coefficients: Sequence[int | Fraction],
    parameter: int | Fraction,
) -> Fraction:
    """Evaluate ``sum(a_k t^k, k=1..4)`` exactly."""

    if len(coefficients) != 4:
        raise ValueError("quartic graph coefficient vector must have length four")
    t = _as_fraction(parameter)
    values = tuple(_as_fraction(value) for value in coefficients)
    return sum((value * t**degree for degree, value in enumerate(values, 1)), Fraction(0))


def squared_distance(
    coefficients: Sequence[int | Fraction],
    center: int | Fraction,
    witness: int | Fraction,
) -> Fraction:
    """Evaluate the squared Euclidean graph distance exactly."""

    s = _as_fraction(center)
    q = _as_fraction(witness)
    vertical = polynomial_value(coefficients, q) - polynomial_value(coefficients, s)
    return (q - s) ** 2 + vertical**2


def lifted_squared_distance(
    upper: Sequence[int | Fraction],
    center: int | Fraction,
    witness: int | Fraction,
) -> Fraction:
    """Evaluate squared distance from the ten lifted Gram coordinates."""

    s = _as_fraction(center)
    q = _as_fraction(witness)
    values = tuple(_as_fraction(value) for value in upper)
    if len(values) != VARIABLE_COUNT:
        raise ValueError(f"expected {VARIABLE_COUNT} upper-triangular entries")

    total = (q - s) ** 2
    for value, (left, right) in zip(values, GRAM_PAIRS, strict=True):
        multiplier = 1 if left == right else 2
        total += (
            multiplier
            * value
            * (q**left - s**left)
            * (q**right - s**right)
        )
    return total


def marked_row_equations(
    center: int | Fraction,
    witnesses: Sequence[int | Fraction],
) -> tuple[Equation, Equation, Equation]:
    """Return the three affine Gram equations for one four-witness row.

    Every returned row has eleven entries: ten coefficients followed by the
    right-hand side.  The first witness is the deterministic reference.
    """

    s = _as_fraction(center)
    qs = tuple(_as_fraction(value) for value in witnesses)
    if len(qs) != 4 or len(set(qs)) != 4:
        raise ValueError("a marked row needs four distinct witnesses")
    if s in qs:
        raise ValueError("the center cannot be one of its witnesses")
    if tuple(sorted(qs)) != qs:
        raise ValueError("witnesses must be supplied in increasing order")

    reference = qs[0]
    rows: list[Equation] = []
    for witness in qs[1:]:
        coefficients: list[Fraction] = []
        for left, right in GRAM_PAIRS:
            multiplier = 1 if left == right else 2
            current = (witness**left - s**left) * (witness**right - s**right)
            baseline = (reference**left - s**left) * (
                reference**right - s**right
            )
            coefficients.append(Fraction(multiplier) * (current - baseline))
        horizontal_difference = (witness - s) ** 2 - (reference - s) ** 2
        rows.append(tuple(coefficients) + (-horizontal_difference,))
    return rows[0], rows[1], rows[2]


def distance_fiber_coefficients(
    upper: Sequence[int | Fraction],
    center: int | Fraction,
    radius_squared: int | Fraction,
) -> tuple[Fraction, ...]:
    """Return low-to-high coefficients of the lifted degree-eight fiber."""

    values = tuple(_as_fraction(value) for value in upper)
    if len(values) != VARIABLE_COUNT:
        raise ValueError(f"expected {VARIABLE_COUNT} upper-triangular entries")
    s = _as_fraction(center)
    radius = _as_fraction(radius_squared)
    coefficients = [Fraction(0) for _ in range(9)]
    coefficients[0] = s * s - radius
    coefficients[1] = -2 * s
    coefficients[2] = 1

    for value, (left, right) in zip(values, GRAM_PAIRS, strict=True):
        multiplier = 1 if left == right else 2
        weight = multiplier * value
        coefficients[left + right] += weight
        coefficients[left] -= weight * s**right
        coefficients[right] -= weight * s**left
        coefficients[0] += weight * s ** (left + right)
    return _polynomial_trim(coefficients)


def marked_root_divisibility_check(
    center: int | Fraction,
    witnesses: Sequence[int | Fraction],
    upper: Sequence[int | Fraction],
) -> bool:
    """Independently check divisibility by the marked witness polynomial."""

    s = _as_fraction(center)
    qs = tuple(_as_fraction(value) for value in witnesses)
    if len(qs) != 4 or len(set(qs)) != 4 or s in qs:
        raise ValueError("need four distinct witnesses different from the center")
    radius = lifted_squared_distance(upper, s, qs[0])
    fiber = distance_fiber_coefficients(upper, s, radius)
    marked_polynomial: tuple[Fraction, ...] = (Fraction(1),)
    for witness in qs:
        product = [Fraction(0) for _ in range(len(marked_polynomial) + 1)]
        for index, value in enumerate(marked_polynomial):
            product[index] -= witness * value
            product[index + 1] += value
        marked_polynomial = tuple(product)
    _, remainder = _polynomial_divmod(fiber, marked_polynomial)
    return not remainder


def equations_hold(
    equations: Iterable[Equation],
    upper: Sequence[int | Fraction],
) -> bool:
    """Check a lifted Gram vector against augmented affine equations."""

    values = tuple(_as_fraction(value) for value in upper)
    if len(values) != VARIABLE_COUNT:
        raise ValueError(f"expected {VARIABLE_COUNT} upper-triangular entries")
    return all(
        sum((coefficient * value for coefficient, value in zip(row[:-1], values, strict=True)), Fraction(0))
        == row[-1]
        for row in equations
    )


def reduced_row_echelon(equations: Iterable[Sequence[int | Fraction]]) -> Rref | None:
    """Return canonical RREF, or ``None`` for an inconsistent affine system."""

    rows: list[list[Fraction]] = []
    for raw_row in equations:
        if len(raw_row) != VARIABLE_COUNT + 1:
            raise ValueError(f"each augmented row must have {VARIABLE_COUNT + 1} entries")
        row = [_as_fraction(value) for value in raw_row]
        if any(row):
            rows.append(row)

    pivot_row = 0
    for column in range(VARIABLE_COUNT):
        pivot = next(
            (index for index in range(pivot_row, len(rows)) if rows[index][column]),
            None,
        )
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        pivot_value = rows[pivot_row][column]
        rows[pivot_row] = [value / pivot_value for value in rows[pivot_row]]
        for index, row in enumerate(rows):
            if index == pivot_row or not row[column]:
                continue
            multiplier = row[column]
            rows[index] = [
                value - multiplier * pivot_entry
                for value, pivot_entry in zip(row, rows[pivot_row], strict=True)
            ]
        pivot_row += 1
        if pivot_row == len(rows):
            break

    cleaned: list[Equation] = []
    for row in rows:
        if not any(row[:-1]):
            if row[-1]:
                return None
            continue
        cleaned.append(tuple(row))

    cleaned.sort(key=lambda row: next(index for index, value in enumerate(row[:-1]) if value))
    return tuple(cleaned)


def solve_affine(equations: Iterable[Sequence[int | Fraction]]) -> AffineSolution | None:
    """Solve an exact affine Gram system and expose a nullspace basis."""

    rref = reduced_row_echelon(equations)
    if rref is None:
        return None
    pivots = tuple(
        next(index for index, value in enumerate(row[:-1]) if value)
        for row in rref
    )
    free_columns = tuple(index for index in range(VARIABLE_COUNT) if index not in pivots)
    particular = [Fraction(0) for _ in range(VARIABLE_COUNT)]
    for row, pivot in zip(rref, pivots, strict=True):
        particular[pivot] = row[-1]

    nullspace: list[tuple[Fraction, ...]] = []
    for free in free_columns:
        vector = [Fraction(0) for _ in range(VARIABLE_COUNT)]
        vector[free] = Fraction(1)
        for row, pivot in zip(rref, pivots, strict=True):
            vector[pivot] = -row[free]
        nullspace.append(tuple(vector))

    return AffineSolution(
        rref=rref,
        pivots=pivots,
        free_columns=free_columns,
        particular=tuple(particular),
        nullspace=tuple(nullspace),
    )


def rank_one_psd_check(upper: Sequence[int | Fraction]) -> RankOneCheck:
    """Check exact rank-one, PSD, and degree-four conditions."""

    matrix = gram_matrix(upper)
    all_minors_zero = all(
        matrix[row_a][column_a] * matrix[row_b][column_b]
        - matrix[row_a][column_b] * matrix[row_b][column_a]
        == 0
        for row_a, row_b in combinations(range(4), 2)
        for column_a, column_b in combinations(range(4), 2)
    )
    diagonal = tuple(matrix[index][index] for index in range(4))
    nonzero = any(any(value for value in row) for row in matrix)
    rank_one = nonzero and all_minors_zero
    positive_semidefinite = all(
        _determinant(
            tuple(
                tuple(matrix[row][column] for column in indices)
                for row in indices
            )
        )
        >= 0
        for size in range(1, 5)
        for indices in combinations(range(4), size)
    )
    pivot_index = next((index for index, value in enumerate(diagonal) if value > 0), None)
    degree_four = matrix[3][3] > 0
    return RankOneCheck(
        rank_one=rank_one,
        positive_semidefinite=positive_semidefinite,
        degree_four=degree_four,
        pivot_index=pivot_index,
    )


def _determinant(matrix: Sequence[Sequence[Fraction]]) -> Fraction:
    """Return an exact determinant by fraction-preserving elimination."""

    size = len(matrix)
    if any(len(row) != size for row in matrix):
        raise ValueError("determinant needs a square matrix")
    rows = [list(row) for row in matrix]
    determinant = Fraction(1)
    for column in range(size):
        pivot = next((row for row in range(column, size) if rows[row][column]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            rows[column], rows[pivot] = rows[pivot], rows[column]
            determinant = -determinant
        pivot_value = rows[column][column]
        determinant *= pivot_value
        for row in range(column + 1, size):
            if not rows[row][column]:
                continue
            multiplier = rows[row][column] / pivot_value
            for index in range(column + 1, size):
                rows[row][index] -= multiplier * rows[column][index]
    return determinant


def recover_rational_direction(
    upper: Sequence[int | Fraction],
) -> tuple[Fraction, Fraction, Fraction, Fraction]:
    """Recover coefficient ratios from an exact rank-one PSD Gram matrix.

    The returned vector ``b`` satisfies ``A = A_pp * b b^T`` with ``b_p=1``.
    The actual coefficient vector is ``sqrt(A_pp) * b``; no square root is
    needed for convexity or orientation checks.
    """

    check = rank_one_psd_check(upper)
    if not check.rank_one or not check.positive_semidefinite or check.pivot_index is None:
        raise ValueError("matrix must be nonzero, rank one, and positive semidefinite")
    matrix = gram_matrix(upper)
    pivot = check.pivot_index
    pivot_value = matrix[pivot][pivot]
    return tuple(matrix[index][pivot] / pivot_value for index in range(4))  # type: ignore[return-value]


def second_derivative_has_constant_sign(
    direction: Sequence[int | Fraction],
    lower: int | Fraction,
    upper: int | Fraction,
) -> bool:
    """Check strict convexity/concavity of the polynomial graph on an interval.

    For a polynomial, a nonzero second derivative with one weak sign makes the
    first derivative strictly monotone.  Isolated zeros, including endpoint
    zeros such as for ``t^4``, are therefore accepted.
    """

    if len(direction) != 4:
        raise ValueError("quartic graph coefficient direction must have length four")
    values = tuple(_as_fraction(value) for value in direction)
    lo = _as_fraction(lower)
    hi = _as_fraction(upper)
    if not lo < hi:
        raise ValueError("convexity interval must have positive length")

    constant = 2 * values[1]
    linear = 6 * values[2]
    quadratic = 12 * values[3]
    if not (constant or linear or quadratic):
        return False

    def evaluate(t: Fraction) -> Fraction:
        return constant + linear * t + quadratic * t * t

    candidates = [evaluate(lo), evaluate(hi)]
    if quadratic:
        vertex = -linear / (2 * quadratic)
        if lo <= vertex <= hi:
            candidates.append(evaluate(vertex))

    if quadratic > 0:
        minimum = min(candidates)
        maximum = max(evaluate(lo), evaluate(hi))
    elif quadratic < 0:
        minimum = min(evaluate(lo), evaluate(hi))
        maximum = max(candidates)
    else:
        minimum = min(evaluate(lo), evaluate(hi))
        maximum = max(evaluate(lo), evaluate(hi))
    return minimum >= 0 or maximum <= 0


def finite_graph_chain_is_strict(
    direction: Sequence[int | Fraction],
    parameters: Sequence[int | Fraction],
) -> bool:
    """Check that every consecutive graph triple has one strict orientation."""

    ts = validate_parameters(parameters)
    values = tuple(_as_fraction(value) for value in direction)
    points = tuple((t, polynomial_value(values, t)) for t in ts)
    orientations: list[Fraction] = []
    for left, middle, right in zip(points, points[1:], points[2:], strict=False):
        x1, y1 = left
        x2, y2 = middle
        x3, y3 = right
        orientations.append((x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1))
    return bool(orientations) and (
        all(value > 0 for value in orientations)
        or all(value < 0 for value in orientations)
    )


def maximum_distance_multiplicity(
    upper: Sequence[int | Fraction],
    center: int | Fraction,
    parameters: Sequence[int | Fraction],
) -> int:
    """Return the largest exact distance class away from one center."""

    ts = validate_parameters(parameters)
    s = _as_fraction(center)
    if s not in ts:
        raise ValueError("center must belong to the parameter set")
    counts: dict[Fraction, int] = {}
    for witness in ts:
        if witness == s:
            continue
        distance = lifted_squared_distance(upper, s, witness)
        counts[distance] = counts.get(distance, 0) + 1
    return max(counts.values(), default=0)


def rich_center_multiplicities(
    upper: Sequence[int | Fraction],
    parameters: Sequence[int | Fraction],
) -> tuple[int, ...]:
    """Return the exact largest distance-class size for every center."""

    ts = validate_parameters(parameters)
    return tuple(maximum_distance_multiplicity(upper, center, ts) for center in ts)


def _polynomial_trim(polynomial: Sequence[Fraction]) -> tuple[Fraction, ...]:
    values = list(polynomial)
    while values and not values[-1]:
        values.pop()
    return tuple(values)


def _polynomial_divmod(
    dividend: Sequence[Fraction],
    divisor: Sequence[Fraction],
) -> tuple[tuple[Fraction, ...], tuple[Fraction, ...]]:
    numerator = list(_polynomial_trim(dividend))
    denominator = _polynomial_trim(divisor)
    if not denominator:
        raise ZeroDivisionError("polynomial division by zero")
    if len(numerator) < len(denominator):
        return (), tuple(numerator)
    quotient = [Fraction(0) for _ in range(len(numerator) - len(denominator) + 1)]
    while numerator and len(numerator) >= len(denominator):
        degree = len(numerator) - len(denominator)
        multiplier = numerator[-1] / denominator[-1]
        quotient[degree] = multiplier
        for index, value in enumerate(denominator):
            numerator[index + degree] -= multiplier * value
        numerator = list(_polynomial_trim(numerator))
    return _polynomial_trim(quotient), tuple(numerator)


def _polynomial_gcd(
    left: Sequence[Fraction],
    right: Sequence[Fraction],
) -> tuple[Fraction, ...]:
    a = _polynomial_trim(left)
    b = _polynomial_trim(right)
    while b:
        _, remainder = _polynomial_divmod(a, b)
        a, b = b, remainder
    if not a:
        return ()
    leading = a[-1]
    return tuple(value / leading for value in a)


def _matrix_entry_from_upper(
    upper: Sequence[Fraction],
    row: int,
    column: int,
) -> Fraction:
    pair = (min(row, column) + 1, max(row, column) + 1)
    return upper[PAIR_INDEX[pair]]


def _minor_polynomial(
    particular: Sequence[Fraction],
    direction: Sequence[Fraction],
    row_a: int,
    row_b: int,
    column_a: int,
    column_b: int,
) -> tuple[Fraction, ...]:
    p_ac = _matrix_entry_from_upper(particular, row_a, column_a)
    p_ad = _matrix_entry_from_upper(particular, row_a, column_b)
    p_bc = _matrix_entry_from_upper(particular, row_b, column_a)
    p_bd = _matrix_entry_from_upper(particular, row_b, column_b)
    v_ac = _matrix_entry_from_upper(direction, row_a, column_a)
    v_ad = _matrix_entry_from_upper(direction, row_a, column_b)
    v_bc = _matrix_entry_from_upper(direction, row_b, column_a)
    v_bd = _matrix_entry_from_upper(direction, row_b, column_b)
    return _polynomial_trim(
        (
            p_ac * p_bd - p_ad * p_bc,
            p_ac * v_bd + v_ac * p_bd - p_ad * v_bc - v_ad * p_bc,
            v_ac * v_bd - v_ad * v_bc,
        )
    )


def _fraction_square_root(value: Fraction) -> Fraction | None:
    if value < 0:
        return None
    numerator_root = isqrt(value.numerator)
    denominator_root = isqrt(value.denominator)
    if numerator_root * numerator_root != value.numerator:
        return None
    if denominator_root * denominator_root != value.denominator:
        return None
    return Fraction(numerator_root, denominator_root)


def rank_one_intersection_on_line(
    particular: Sequence[int | Fraction],
    direction: Sequence[int | Fraction],
) -> LineRankOneResult:
    """Solve all rank-one minors on ``particular + lambda * direction``.

    The common minor gcd has degree at most two.  Irrational real quadratic
    roots are retained exactly rather than being approximated or rejected.
    """

    p = tuple(_as_fraction(value) for value in particular)
    v = tuple(_as_fraction(value) for value in direction)
    if len(p) != VARIABLE_COUNT or len(v) != VARIABLE_COUNT:
        raise ValueError(f"line vectors must have length {VARIABLE_COUNT}")
    if not any(v):
        raise ValueError("line direction must be nonzero")

    gcd: tuple[Fraction, ...] = ()
    found_nonzero_minor = False
    for row_a, row_b in combinations(range(4), 2):
        for column_a, column_b in combinations(range(4), 2):
            polynomial = _minor_polynomial(
                p,
                v,
                row_a,
                row_b,
                column_a,
                column_b,
            )
            if not polynomial:
                continue
            found_nonzero_minor = True
            gcd = polynomial if not gcd else _polynomial_gcd(gcd, polynomial)
            if len(gcd) == 1:
                return LineRankOneResult(kind="NO_RANK_ONE")

    if not found_nonzero_minor:
        return LineRankOneResult(kind="ALL_PARAMETERS_RANK_AT_MOST_ONE")
    if len(gcd) == 2:
        return LineRankOneResult(kind="RATIONAL_PARAMETERS", rational_parameters=(-gcd[0] / gcd[1],))
    if len(gcd) != 3:
        raise AssertionError(f"unexpected minor gcd degree: {len(gcd) - 1}")

    constant, linear, quadratic = gcd
    discriminant = linear * linear - 4 * quadratic * constant
    if discriminant < 0:
        return LineRankOneResult(kind="NO_REAL_RANK_ONE")
    square_root = _fraction_square_root(discriminant)
    if square_root is not None:
        roots = tuple(
            sorted(
                {
                    (-linear - square_root) / (2 * quadratic),
                    (-linear + square_root) / (2 * quadratic),
                }
            )
        )
        return LineRankOneResult(kind="RATIONAL_PARAMETERS", rational_parameters=roots)
    return LineRankOneResult(
        kind="IRRATIONAL_REAL_QUADRATIC",
        irreducible_quadratic=(constant, linear, quadratic),
    )


def _fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _upper_at_parameter(
    particular: Sequence[Fraction],
    direction: Sequence[Fraction],
    parameter: Fraction,
) -> tuple[Fraction, ...]:
    return tuple(
        base + parameter * delta
        for base, delta in zip(particular, direction, strict=True)
    )


def anchor_triple_scan(
    parameters: Sequence[int | Fraction] = tuple(range(-4, 5)),
    centers: Sequence[int | Fraction] = (0, 3, 4),
    *,
    sample_limit: int = 20,
) -> AnchorTripleSummary:
    """Enumerate three marked rows on one fixed rational parameter set.

    Pairwise witness overlap greater than two is removed by the exact
    two-circle intersection cap.  Rank-nine affine lines are intersected with
    every 2 by 2 rank-one minor.  Lower-rank affine families and irrational
    real quadratic branches are retained explicitly as unresolved states.
    """

    ts = validate_parameters(parameters)
    center_values = tuple(_as_fraction(value) for value in centers)
    if len(center_values) != 3 or len(set(center_values)) != 3:
        raise ValueError("the pilot needs three distinct anchor centers")
    if any(center not in ts for center in center_values):
        raise ValueError("every center must belong to the parameter set")
    if sample_limit < 0:
        raise ValueError("sample_limit must be nonnegative")

    options: dict[Fraction, tuple[tuple[tuple[Fraction, ...], tuple[Equation, ...]], ...]] = {}
    for center in center_values:
        witnesses = tuple(value for value in ts if value != center)
        options[center] = tuple(
            (quartet, marked_row_equations(center, quartet))
            for quartet in combinations(witnesses, 4)
        )

    option_count = len(options[center_values[0]])
    if any(len(options[center]) != option_count for center in center_values):
        raise AssertionError("anchor centers unexpectedly have different option counts")

    raw_triple_count = option_count**3
    overlap_admissible_count = 0
    pair_inconsistent_pruned_triple_count = 0
    inconsistent_count = 0
    rank_counts: dict[int, int] = {}
    line_without_real_rank_at_most_one_count = 0
    line_zero_matrix_root_count = 0
    line_negative_semidefinite_rank_one_root_count = 0
    line_lower_degree_rank_one_psd_root_count = 0
    line_rational_quartic_gram_count = 0
    line_irrational_rank_at_most_one_component_count = 0
    line_all_rank_at_most_one_count = 0
    exceptional_rrefs: set[Rref] = set()
    unresolved_line_rrefs: set[Rref] = set()
    rank_one_quartic_grams: set[tuple[Fraction, ...]] = set()
    samples: list[dict[str, object]] = []

    first_center, second_center, third_center = center_values
    for first_witnesses, first_equations in options[first_center]:
        first_set = frozenset(first_witnesses)
        for second_witnesses, second_equations in options[second_center]:
            second_set = frozenset(second_witnesses)
            if len(first_set & second_set) > 2:
                continue
            admissible_third_options = tuple(
                (third_witnesses, third_equations)
                for third_witnesses, third_equations in options[third_center]
                if len(first_set & frozenset(third_witnesses)) <= 2
                and len(second_set & frozenset(third_witnesses)) <= 2
            )
            overlap_admissible_count += len(admissible_third_options)
            pair_solution = solve_affine(first_equations + second_equations)
            if pair_solution is None:
                pair_inconsistent_pruned_triple_count += len(admissible_third_options)
                continue
            for third_witnesses, third_equations in admissible_third_options:
                solution = solve_affine(pair_solution.rref + third_equations)
                if solution is None:
                    inconsistent_count += 1
                    continue
                rank_counts[solution.rank] = rank_counts.get(solution.rank, 0) + 1
                witness_record = tuple(
                    tuple(_fraction_text(value) for value in row)
                    for row in (first_witnesses, second_witnesses, third_witnesses)
                )

                if solution.dimension == 0:
                    raise AssertionError("nine anchor equations cannot have rank ten")

                if solution.dimension == 1:
                    line_result = rank_one_intersection_on_line(
                        solution.particular,
                        solution.nullspace[0],
                    )
                    if line_result.kind in {"NO_RANK_ONE", "NO_REAL_RANK_ONE"}:
                        line_without_real_rank_at_most_one_count += 1
                        continue
                    if line_result.kind == "RATIONAL_PARAMETERS":
                        viable_parameters: list[Fraction] = []
                        for parameter in line_result.rational_parameters:
                            upper_at_root = _upper_at_parameter(
                                solution.particular,
                                solution.nullspace[0],
                                parameter,
                            )
                            root_check = rank_one_psd_check(upper_at_root)
                            if root_check.quartic_gram:
                                viable_parameters.append(parameter)
                                rank_one_quartic_grams.add(upper_at_root)
                            elif not root_check.rank_one:
                                line_zero_matrix_root_count += 1
                            elif not root_check.positive_semidefinite:
                                line_negative_semidefinite_rank_one_root_count += 1
                            else:
                                line_lower_degree_rank_one_psd_root_count += 1
                        if not viable_parameters:
                            continue
                        line_rational_quartic_gram_count += len(viable_parameters)
                        if len(samples) < sample_limit:
                            samples.append(
                                {
                                    "kind": "RATIONAL_LINE_RANK_ONE",
                                    "witnesses": witness_record,
                                    "parameters": tuple(
                                        _fraction_text(value) for value in viable_parameters
                                    ),
                                }
                            )
                        continue
                    if line_result.kind == "IRRATIONAL_REAL_QUADRATIC":
                        line_irrational_rank_at_most_one_component_count += 1
                        unresolved_line_rrefs.add(solution.rref)
                        if len(samples) < sample_limit:
                            samples.append(
                                {
                                    "kind": "IRRATIONAL_REAL_QUADRATIC_LINE",
                                    "witnesses": witness_record,
                                    "polynomial": tuple(
                                        _fraction_text(value)
                                        for value in line_result.irreducible_quadratic or ()
                                    ),
                                }
                            )
                        continue
                    if line_result.kind == "ALL_PARAMETERS_RANK_AT_MOST_ONE":
                        line_all_rank_at_most_one_count += 1
                        unresolved_line_rrefs.add(solution.rref)
                        if len(samples) < sample_limit:
                            samples.append(
                                {
                                    "kind": "ENTIRE_LINE_RANK_AT_MOST_ONE",
                                    "witnesses": witness_record,
                                }
                            )
                        continue
                    raise AssertionError(f"unhandled line classification: {line_result.kind}")

                exceptional_rrefs.add(solution.rref)
                if len(samples) < sample_limit:
                    samples.append(
                        {
                            "kind": "UNRESOLVED_AFFINE_FAMILY",
                            "witnesses": witness_record,
                            "rank": solution.rank,
                            "dimension": solution.dimension,
                        }
                    )

    return AnchorTripleSummary(
        parameters=ts,
        centers=(center_values[0], center_values[1], center_values[2]),
        quartet_count_per_center=option_count,
        raw_triple_count=raw_triple_count,
        overlap_admissible_count=overlap_admissible_count,
        pair_inconsistent_pruned_triple_count=pair_inconsistent_pruned_triple_count,
        inconsistent_count=inconsistent_count,
        rank_counts=tuple(sorted(rank_counts.items())),
        line_without_real_rank_at_most_one_count=line_without_real_rank_at_most_one_count,
        line_zero_matrix_root_count=line_zero_matrix_root_count,
        line_negative_semidefinite_rank_one_root_count=(
            line_negative_semidefinite_rank_one_root_count
        ),
        line_lower_degree_rank_one_psd_root_count=(
            line_lower_degree_rank_one_psd_root_count
        ),
        line_rational_quartic_gram_count=line_rational_quartic_gram_count,
        line_irrational_rank_at_most_one_component_count=(
            line_irrational_rank_at_most_one_component_count
        ),
        line_all_rank_at_most_one_count=line_all_rank_at_most_one_count,
        exceptional_affine_state_count=len(exceptional_rrefs),
        sample_survivors=tuple(samples),
        exceptional_rrefs=tuple(sorted(exceptional_rrefs)),
        unresolved_line_rrefs=tuple(sorted(unresolved_line_rrefs)),
        rank_one_quartic_grams=tuple(sorted(rank_one_quartic_grams)),
    )


def quartic_closure_pilot(
    parameters: Sequence[int | Fraction] = tuple(range(-4, 5)),
    anchor_centers: Sequence[int | Fraction] = (0, 3, 4),
    extension_centers: Sequence[int | Fraction] | None = None,
    *,
    sample_limit: int = 20,
) -> QuarticClosurePilotSummary:
    """Run the exact fixed-grid quartic marked-root closure pilot.

    The three anchors are exhaustively enumerated first.  Every surviving
    higher-dimensional affine state is then extended, center by center, across
    all four-witness choices.  Canonical RREF states are deduplicated; the
    extension deliberately omits overlap pruning, so deduplication cannot hide
    a future witness choice.
    """

    ts = validate_parameters(parameters)
    anchors = tuple(_as_fraction(value) for value in anchor_centers)
    anchor_summary = anchor_triple_scan(
        ts,
        anchors,
        sample_limit=sample_limit,
    )
    if extension_centers is None:
        extension_values = tuple(value for value in ts if value not in anchors)
    else:
        extension_values = tuple(_as_fraction(value) for value in extension_centers)
        expected = {value for value in ts if value not in anchors}
        if len(extension_values) != len(set(extension_values)) or set(extension_values) != expected:
            raise ValueError("extension centers must list every non-anchor parameter exactly once")

    states = set(anchor_summary.exceptional_rrefs) | set(anchor_summary.unresolved_line_rrefs)
    rank_one_candidates = set(anchor_summary.rank_one_quartic_grams)
    extension_steps: list[dict[str, int | str]] = []

    for center in extension_values:
        witness_values = tuple(value for value in ts if value != center)
        row_options = tuple(
            marked_row_equations(center, quartet)
            for quartet in combinations(witness_values, 4)
        )
        input_state_count = len(states)
        raw_branch_count = input_state_count * len(row_options)
        linearly_inconsistent_count = 0
        consistent_branch_count = 0
        consistent_states: set[Rref] = set()

        for state in states:
            for equations in row_options:
                solution = solve_affine(state + equations)
                if solution is None:
                    linearly_inconsistent_count += 1
                    continue
                consistent_branch_count += 1
                consistent_states.add(solution.rref)

        states_without_real_rank_at_most_one = 0
        zero_matrix_root_count = 0
        negative_semidefinite_rank_one_root_count = 0
        lower_degree_rank_one_psd_root_count = 0
        specified_non_rank_one_gram_count = 0
        unique_quartic_gram_state_count = 0
        rational_line_quartic_gram_count = 0
        irrational_line_state_count = 0
        higher_dimensional_state_count = 0
        next_states: set[Rref] = set()

        for state in consistent_states:
            solution = solve_affine(state)
            if solution is None:
                raise AssertionError("stored RREF state became inconsistent")
            if solution.dimension >= 2:
                next_states.add(solution.rref)
                higher_dimensional_state_count += 1
                continue
            if solution.dimension == 1:
                result = rank_one_intersection_on_line(
                    solution.particular,
                    solution.nullspace[0],
                )
                if result.kind in {"NO_RANK_ONE", "NO_REAL_RANK_ONE"}:
                    states_without_real_rank_at_most_one += 1
                    continue
                if result.kind == "RATIONAL_PARAMETERS":
                    viable = 0
                    for parameter in result.rational_parameters:
                        candidate = _upper_at_parameter(
                            solution.particular,
                            solution.nullspace[0],
                            parameter,
                        )
                        candidate_check = rank_one_psd_check(candidate)
                        if candidate_check.quartic_gram:
                            rank_one_candidates.add(candidate)
                            viable += 1
                        elif not candidate_check.rank_one:
                            zero_matrix_root_count += 1
                        elif not candidate_check.positive_semidefinite:
                            negative_semidefinite_rank_one_root_count += 1
                        else:
                            lower_degree_rank_one_psd_root_count += 1
                    rational_line_quartic_gram_count += viable
                    continue
                if result.kind in {
                    "IRRATIONAL_REAL_QUADRATIC",
                    "ALL_PARAMETERS_RANK_AT_MOST_ONE",
                }:
                    next_states.add(solution.rref)
                    irrational_line_state_count += 1
                    continue
                raise AssertionError(f"unhandled line classification: {result.kind}")

            check = rank_one_psd_check(solution.particular)
            if check.quartic_gram:
                rank_one_candidates.add(solution.particular)
                unique_quartic_gram_state_count += 1
            elif not check.rank_one:
                specified_non_rank_one_gram_count += 1
            elif not check.positive_semidefinite:
                negative_semidefinite_rank_one_root_count += 1
            else:
                lower_degree_rank_one_psd_root_count += 1

        states = next_states
        extension_steps.append(
            {
                "center": _fraction_text(center),
                "input_affine_states": input_state_count,
                "row_options_per_state": len(row_options),
                "raw_state_row_branches": raw_branch_count,
                "linearly_inconsistent_branches": linearly_inconsistent_count,
                "linearly_consistent_branches": consistent_branch_count,
                "deduplicated_consistent_affine_states": len(consistent_states),
                "states_without_real_rank_at_most_one": (
                    states_without_real_rank_at_most_one
                ),
                "zero_matrix_roots": zero_matrix_root_count,
                "negative_semidefinite_rank_one_roots": (
                    negative_semidefinite_rank_one_root_count
                ),
                "lower_degree_rank_one_psd_roots": lower_degree_rank_one_psd_root_count,
                "specified_non_rank_one_grams": specified_non_rank_one_gram_count,
                "unique_rank_one_quartic_gram_states": unique_quartic_gram_state_count,
                "rational_line_rank_one_quartic_grams": rational_line_quartic_gram_count,
                "irrational_or_rank_one_line_states_retained": irrational_line_state_count,
                "higher_dimensional_states_retained": higher_dimensional_state_count,
                "deduplicated_affine_states_out": len(states),
            }
        )
        if not states:
            break

    convex_candidates: set[tuple[Fraction, ...]] = set()
    all_row_candidates: set[tuple[Fraction, ...]] = set()
    strict_finite_closure_candidates: set[tuple[Fraction, ...]] = set()
    continuous_convex_closure_candidates: set[tuple[Fraction, ...]] = set()
    candidate_samples: list[dict[str, object]] = []
    for candidate in sorted(rank_one_candidates):
        direction = recover_rational_direction(candidate)
        continuous_convexity = second_derivative_has_constant_sign(
            direction,
            ts[0],
            ts[-1],
        )
        strict_chain = finite_graph_chain_is_strict(direction, ts)
        multiplicities = rich_center_multiplicities(candidate, ts)
        all_rows_rich = all(value >= 4 for value in multiplicities)
        if continuous_convexity and strict_chain:
            convex_candidates.add(candidate)
        if all_rows_rich:
            all_row_candidates.add(candidate)
            if strict_chain:
                strict_finite_closure_candidates.add(candidate)
                if continuous_convexity:
                    continuous_convex_closure_candidates.add(candidate)
        if len(candidate_samples) < sample_limit:
            candidate_samples.append(
                {
                    "gram_upper": tuple(_fraction_text(value) for value in candidate),
                    "continuous_convexity": continuous_convexity,
                    "strict_finite_chain": strict_chain,
                    "center_multiplicities": multiplicities,
                }
            )

    return QuarticClosurePilotSummary(
        anchor=anchor_summary,
        extension_centers=extension_values,
        extension_steps=tuple(extension_steps),
        unresolved_affine_state_count=len(states),
        rank_one_quartic_candidate_count=len(rank_one_candidates),
        convex_rank_one_candidate_count=len(convex_candidates),
        all_row_quartic_candidate_count=len(all_row_candidates),
        strict_finite_full_closure_candidate_count=len(strict_finite_closure_candidates),
        continuous_convex_full_closure_candidate_count=(
            len(continuous_convex_closure_candidates)
        ),
        sample_candidates=tuple(candidate_samples),
    )
