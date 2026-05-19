"""Exact grid search helpers for the two-parabola lens closure scaffold."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import Iterable


SCHEMA = "erdos97.two_parabola_lens_grid_search.v1"


@dataclass(frozen=True)
class LensEdge:
    """One zero-sum opposite-chain 4-subset and the center it supports."""

    center: Fraction
    c_value: Fraction
    witnesses: tuple[Fraction, Fraction, Fraction, Fraction]


@dataclass(frozen=True)
class GridCaseSummary:
    denominator: int
    max_abs: int
    value_count: int
    edge_count: int
    c_value_count: int
    closure_found: bool
    max_fixed_point_size: int
    best_c_values: tuple[Fraction, ...]


@dataclass(frozen=True)
class ZeroSumPatternSummary:
    point_count: int
    max_zero_sum_four_subsets: int
    feasible_pattern_count_at_max: int
    checked_pattern_count_at_next: int


def rational_grid(*, max_abs: int, denominator: int) -> tuple[Fraction, ...]:
    """Return the grid `{k/denominator : |k| <= max_abs*denominator}`."""

    if max_abs < 0:
        raise ValueError("max_abs must be nonnegative")
    if denominator <= 0:
        raise ValueError("denominator must be positive")
    radius = max_abs * denominator
    return tuple(Fraction(k, denominator) for k in range(-radius, radius + 1))


def _elementary_symmetric_2(values: Iterable[Fraction]) -> Fraction:
    return sum(x * y for x, y in combinations(values, 2))


def _elementary_symmetric_3(values: Iterable[Fraction]) -> Fraction:
    return sum(x * y * z for x, y, z in combinations(values, 3))


def grid_edges(*, max_abs: int, denominator: int) -> tuple[LensEdge, ...]:
    """Enumerate exact closure hyperedges whose generated center is in the grid.

    Each edge is a distinct zero-sum 4-subset `Q` of the grid. It supports the
    opposite-chain center `a=e3(Q)/2` at global parameter
    `c=e2(Q)-2*a^2`.
    """

    values = rational_grid(max_abs=max_abs, denominator=denominator)
    value_set = set(values)
    nums = tuple(range(-max_abs * denominator, max_abs * denominator + 1))
    num_set = set(nums)
    edges: list[LensEdge] = []

    for i, j, k in combinations(nums, 3):
        ell = -(i + j + k)
        if ell not in num_set or not (k < ell):
            continue
        witnesses = tuple(Fraction(n, denominator) for n in (i, j, k, ell))
        e2 = _elementary_symmetric_2(witnesses)
        e3 = _elementary_symmetric_3(witnesses)
        center = e3 / 2
        if center not in value_set:
            continue
        c_value = e2 - 2 * center * center
        edges.append(LensEdge(center=center, c_value=c_value, witnesses=witnesses))

    return tuple(edges)


def greatest_fixed_point_for_c(edges: Iterable[LensEdge]) -> frozenset[Fraction]:
    """Return the greatest same-grid closure set for one `c` value.

    If an asymmetric finite pair `(A,B)` exists inside the grid, then this
    symmetric greatest fixed point is nonempty and contains `A union B`.
    Thus an empty or too-small fixed point rules out both symmetric and
    asymmetric closures in the bounded grid.
    """

    by_center: dict[Fraction, list[frozenset[Fraction]]] = defaultdict(list)
    current: set[Fraction] = set()
    for edge in edges:
        witnesses = frozenset(edge.witnesses)
        by_center[edge.center].append(witnesses)
        current.add(edge.center)
        current.update(witnesses)

    while True:
        next_current = {
            center
            for center in current
            if any(witnesses <= current for witnesses in by_center.get(center, ()))
        }
        if next_current == current:
            return frozenset(current)
        current = next_current


def summarize_grid_case(*, max_abs: int, denominator: int) -> GridCaseSummary:
    edges = grid_edges(max_abs=max_abs, denominator=denominator)
    edges_by_c: dict[Fraction, list[LensEdge]] = defaultdict(list)
    for edge in edges:
        edges_by_c[edge.c_value].append(edge)

    best_size = 0
    best_c_values: list[Fraction] = []
    closure_found = False
    for c_value, c_edges in edges_by_c.items():
        fixed_point = greatest_fixed_point_for_c(c_edges)
        size = len(fixed_point)
        if size > best_size:
            best_size = size
            best_c_values = [c_value]
        elif size == best_size and size > 0:
            best_c_values.append(c_value)
        if size >= 4:
            closure_found = True

    return GridCaseSummary(
        denominator=denominator,
        max_abs=max_abs,
        value_count=2 * max_abs * denominator + 1,
        edge_count=len(edges),
        c_value_count=len(edges_by_c),
        closure_found=closure_found,
        max_fixed_point_size=best_size,
        best_c_values=tuple(sorted(best_c_values)),
    )


def default_grid_cases() -> tuple[tuple[int, int], ...]:
    """Grid cases used by the checked exploratory artifact.

    The pair order is `(denominator, max_abs)`.
    """

    integer_cases = tuple((1, max_abs) for max_abs in range(2, 13))
    rational_cases = tuple(
        (denominator, max_abs)
        for denominator in range(2, 7)
        for max_abs in (2, 3, 4, 5, 6, 8, 10)
    )
    return integer_cases + rational_cases


def fraction_to_json(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _rank_over_q(rows: tuple[tuple[int, ...], ...]) -> int:
    matrix = [
        [Fraction(value) for value in row]
        for row in rows
        if any(row)
    ]
    if not matrix:
        return 0
    row_count = len(matrix)
    col_count = len(matrix[0])
    rank = 0
    for col in range(col_count):
        pivot = None
        for row in range(rank, row_count):
            if matrix[row][col]:
                pivot = row
                break
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        pivot_value = matrix[rank][col]
        matrix[rank] = [value / pivot_value for value in matrix[rank]]
        for row in range(row_count):
            if row == rank:
                continue
            factor = matrix[row][col]
            if factor:
                matrix[row] = [
                    current - factor * rank_value
                    for current, rank_value in zip(matrix[row], matrix[rank])
                ]
        rank += 1
        if rank == row_count:
            break
    return rank


def _subset_rows(edges: tuple[tuple[int, ...], ...], point_count: int) -> tuple[tuple[int, ...], ...]:
    return tuple(
        tuple(1 if index in edge else 0 for index in range(point_count))
        for edge in edges
    )


def _forces_equality(
    rows: tuple[tuple[int, ...], ...],
    *,
    first: int,
    second: int,
) -> bool:
    point_count = len(rows[0]) if rows else max(first, second) + 1
    diff = tuple(
        (1 if index == first else -1 if index == second else 0)
        for index in range(point_count)
    )
    return _rank_over_q(rows + (diff,)) == _rank_over_q(rows)


def _has_distinct_solution(edges: tuple[tuple[int, ...], ...], point_count: int) -> bool:
    rows = _subset_rows(edges, point_count)
    if _rank_over_q(rows) >= point_count:
        return False
    return not any(
        _forces_equality(rows, first=first, second=second)
        for first, second in combinations(range(point_count), 2)
    )


def zero_sum_pattern_summary(point_count: int) -> ZeroSumPatternSummary:
    """Max zero-sum 4-subsets possible on `point_count <= 7` distinct reals.

    The check is over abstract 4-subset incidence patterns. A feasible pattern
    is a homogeneous linear system whose solution space is not contained in any
    equality hyperplane `x_i=x_j`.
    """

    if not 4 <= point_count <= 7:
        raise ValueError("point_count must be between 4 and 7")

    all_edges = tuple(combinations(range(point_count), 4))

    if point_count == 7:
        checked_six = 0
        feasible_six = 0
        for edges in combinations(all_edges, 6):
            if any(
                len(set(left) & set(right)) == 3
                for left, right in combinations(edges, 2)
            ):
                continue
            checked_six += 1
            if _has_distinct_solution(edges, point_count):
                feasible_six += 1

        if feasible_six:
            return ZeroSumPatternSummary(
                point_count=point_count,
                max_zero_sum_four_subsets=6,
                feasible_pattern_count_at_max=feasible_six,
                checked_pattern_count_at_next=0,
            )

        feasible_five = 0
        for edges in combinations(all_edges, 5):
            if any(
                len(set(left) & set(right)) == 3
                for left, right in combinations(edges, 2)
            ):
                continue
            if _has_distinct_solution(edges, point_count):
                feasible_five += 1

        return ZeroSumPatternSummary(
            point_count=point_count,
            max_zero_sum_four_subsets=5,
            feasible_pattern_count_at_max=feasible_five,
            checked_pattern_count_at_next=checked_six,
        )

    max_feasible = 0
    feasible_at_max = 0
    checked_at_next = 0

    for size in range(len(all_edges), 0, -1):
        feasible = 0
        checked = 0
        for edges in combinations(all_edges, size):
            if any(
                len(set(left) & set(right)) == 3
                for left, right in combinations(edges, 2)
            ):
                continue
            checked += 1
            if _has_distinct_solution(edges, point_count):
                feasible += 1
        if feasible:
            max_feasible = size
            feasible_at_max = feasible
            break
        checked_at_next = checked

    return ZeroSumPatternSummary(
        point_count=point_count,
        max_zero_sum_four_subsets=max_feasible,
        feasible_pattern_count_at_max=feasible_at_max,
        checked_pattern_count_at_next=checked_at_next,
    )


def zero_sum_pattern_summary_to_json(summary: ZeroSumPatternSummary) -> dict[str, int]:
    return {
        "point_count": summary.point_count,
        "max_zero_sum_four_subsets": summary.max_zero_sum_four_subsets,
        "feasible_pattern_count_at_max": summary.feasible_pattern_count_at_max,
        "checked_pattern_count_at_next": summary.checked_pattern_count_at_next,
    }


def grid_case_to_json(summary: GridCaseSummary) -> dict[str, object]:
    return {
        "denominator": summary.denominator,
        "max_abs": summary.max_abs,
        "value_count": summary.value_count,
        "edge_count": summary.edge_count,
        "c_value_count": summary.c_value_count,
        "closure_found": summary.closure_found,
        "max_fixed_point_size": summary.max_fixed_point_size,
        "best_c_values": [fraction_to_json(value) for value in summary.best_c_values],
    }


def grid_search_summary(
    cases: Iterable[tuple[int, int]] | None = None,
) -> dict[str, object]:
    """Return JSON-ready summary for a list of `(denominator, max_abs)` cases."""

    selected_cases = tuple(cases if cases is not None else default_grid_cases())
    summaries = [
        summarize_grid_case(max_abs=max_abs, denominator=denominator)
        for denominator, max_abs in selected_cases
    ]
    zero_sum_summaries = [
        zero_sum_pattern_summary(point_count) for point_count in range(4, 8)
    ]
    closure_cases = [summary for summary in summaries if summary.closure_found]
    return {
        "schema": SCHEMA,
        "status": (
            "GRID_CLOSURE_FOUND"
            if closure_cases
            else "NO_GRID_CLOSURE_IN_BOUNDED_RATIONAL_GRIDS"
        ),
        "trust": "FINITE_BOOKKEEPING_NOT_A_PROOF",
        "claim_scope": (
            "Bounded rational-grid search for the opposite-chain two-parabola "
            "lens closure ansatz only; not a proof of Erdos Problem #97 and "
            "not a counterexample search over arbitrary real parameters."
        ),
        "case_count": len(summaries),
        "closure_found": bool(closure_cases),
        "closure_case_count": len(closure_cases),
        "opposite_chain_size_floor": {
            "min_points_per_chain": 8,
            "min_total_points": 16,
            "reason": (
                "each point on one chain needs a distinct zero-sum 4-subset on "
                "the opposite chain; exact pattern enumeration gives at most "
                "five zero-sum 4-subsets on seven distinct real parameters"
            ),
            "zero_sum_pattern_summaries": [
                zero_sum_pattern_summary_to_json(summary)
                for summary in zero_sum_summaries
            ],
        },
        "cases": [grid_case_to_json(summary) for summary in summaries],
        "does_not_check": [
            "arbitrary real or algebraic parameter sets",
            "mixed same-chain/opposite-chain witness classes",
            "strict-convex lens inequalities",
            "general Erdos Problem #97",
        ],
    }
