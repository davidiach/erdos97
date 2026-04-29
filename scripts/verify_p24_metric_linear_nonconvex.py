#!/usr/bin/env python3
"""Exact verifier for a 24-point metric-linear nonconvex control.

This is a negative-control artifact for Erdos Problem #97. It verifies an
exact 24-point configuration with four equal selected distances from every
center and pairwise row intersections of size at most one. The cyclic angular
order is not a strictly convex polygon, so this is not a counterexample.

Arithmetic is exact in Q(sqrt(3)), represented as a + b*sqrt(3) with rational
coefficients.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations

N = 24


@dataclass(frozen=True)
class Q3:
    """Element a + b*sqrt(3), with rational a and b."""

    a: Fraction = Fraction(0)
    b: Fraction = Fraction(0)

    def __add__(self, other: Q3) -> Q3:
        return Q3(self.a + other.a, self.b + other.b)

    def __sub__(self, other: Q3) -> Q3:
        return Q3(self.a - other.a, self.b - other.b)

    def __neg__(self) -> Q3:
        return Q3(-self.a, -self.b)

    def __mul__(self, other: Q3) -> Q3:
        return Q3(
            self.a * other.a + 3 * self.b * other.b,
            self.a * other.b + self.b * other.a,
        )

    def inv(self) -> Q3:
        den = self.a * self.a - 3 * self.b * self.b
        if den == 0:
            raise ZeroDivisionError(self)
        return Q3(self.a / den, -self.b / den)

    def __truediv__(self, other: Q3) -> Q3:
        return self * other.inv()

    def is_zero(self) -> bool:
        return self.a == 0 and self.b == 0

    def __repr__(self) -> str:
        if self.b == 0:
            return str(self.a)
        if self.a == 0:
            return f"{self.b}*sqrt(3)"
        sign = "+" if self.b > 0 else "-"
        return f"{self.a} {sign} {abs(self.b)}*sqrt(3)"


ZERO = Q3()
ONE = Q3(Fraction(1))
TWO = Q3(Fraction(2))
HALF = Q3(Fraction(1, 2))
SQRT3_OVER_2 = Q3(Fraction(0), Fraction(1, 2))

COS30 = [
    ONE,
    SQRT3_OVER_2,
    HALF,
    ZERO,
    -HALF,
    -SQRT3_OVER_2,
    -ONE,
    -SQRT3_OVER_2,
    -HALF,
    ZERO,
    HALF,
    SQRT3_OVER_2,
]
SIN30 = [
    ZERO,
    HALF,
    SQRT3_OVER_2,
    ONE,
    SQRT3_OVER_2,
    HALF,
    ZERO,
    -HALF,
    -SQRT3_OVER_2,
    -ONE,
    -SQRT3_OVER_2,
    -HALF,
]


def c30(k: int) -> Q3:
    return COS30[k % 12]


def s30(k: int) -> Q3:
    return SIN30[k % 12]


def construction_points() -> list[tuple[Q3, Q3]]:
    """Return p_j = rho_j exp(i*j*pi/12) in exact Q(sqrt(3)) coordinates."""

    points: list[tuple[Q3, Q3]] = []
    for j in range(N):
        if j % 2 == 0:
            k = j // 2
            points.append((c30(k), s30(k)))
        else:
            k = (j - 1) // 2
            points.append((c30(k) + c30(k + 1), s30(k) + s30(k + 1)))
    return points


POINTS = construction_points()


def support(j: int) -> set[int]:
    offsets = (-4, -1, 1, 4) if j % 2 == 0 else (-5, -4, 4, 5)
    return {(j + offset) % N for offset in offsets}


def supports() -> list[set[int]]:
    return [support(j) for j in range(N)]


def sqdist(a: int, b: int) -> Q3:
    ax, ay = POINTS[a]
    bx, by = POINTS[b]
    dx = ax - bx
    dy = ay - by
    return dx * dx + dy * dy


def det(u: tuple[Q3, Q3], v: tuple[Q3, Q3]) -> Q3:
    return u[0] * v[1] - u[1] * v[0]


def exact_rank(matrix: list[list[Q3]]) -> int:
    """Return matrix rank by Gaussian elimination over Q(sqrt(3))."""

    reduced = [row[:] for row in matrix]
    m = len(reduced)
    n = len(reduced[0]) if m else 0
    rank = 0
    for col in range(n):
        pivot = None
        for row_index in range(rank, m):
            if not reduced[row_index][col].is_zero():
                pivot = row_index
                break
        if pivot is None:
            continue
        if pivot != rank:
            reduced[rank], reduced[pivot] = reduced[pivot], reduced[rank]
        pivot_value = reduced[rank][col]
        for row_index in range(rank + 1, m):
            if reduced[row_index][col].is_zero():
                continue
            factor = reduced[row_index][col] / pivot_value
            for c in range(col, n):
                reduced[row_index][c] = reduced[row_index][c] - factor * reduced[rank][c]
        rank += 1
        if rank == m:
            break
    return rank


def equal_distance_rows() -> bool:
    for center in range(N):
        distances = [sqdist(center, witness) for witness in sorted(support(center))]
        if not all((distance - distances[0]).is_zero() for distance in distances):
            return False
    return True


def max_support_intersection() -> int:
    all_supports = supports()
    return max(
        len(all_supports[i] & all_supports[j])
        for i, j in combinations(range(N), 2)
    )


def signed_turns() -> list[Q3]:
    turns: list[Q3] = []
    for j in range(N):
        x0, y0 = POINTS[j]
        x1, y1 = POINTS[(j + 1) % N]
        x2, y2 = POINTS[(j + 2) % N]
        v1 = (x1 - x0, y1 - y0)
        v2 = (x2 - x1, y2 - y1)
        turns.append(det(v1, v2))
    return turns


def jacobian_matrix() -> list[list[Q3]]:
    rows: list[list[Q3]] = []
    for center in range(N):
        witnesses = sorted(support(center))
        base = witnesses[0]
        center_x, center_y = POINTS[center]
        base_x, base_y = POINTS[base]
        for witness in witnesses[1:]:
            witness_x, witness_y = POINTS[witness]
            row = [ZERO] * (2 * N)

            row[2 * center] = row[2 * center] + TWO * (base_x - witness_x)
            row[2 * center + 1] = row[2 * center + 1] + TWO * (base_y - witness_y)

            row[2 * witness] = row[2 * witness] + TWO * (witness_x - center_x)
            row[2 * witness + 1] = row[2 * witness + 1] + TWO * (witness_y - center_y)

            row[2 * base] = row[2 * base] - TWO * (base_x - center_x)
            row[2 * base + 1] = row[2 * base + 1] - TWO * (base_y - center_y)

            rows.append(row)
    return rows


def jacobian_rank() -> int:
    return exact_rank(jacobian_matrix())


def run_checks() -> dict[str, object]:
    turns = signed_turns()
    even_turns = {turns[j] for j in range(N) if j % 2 == 0}
    odd_turns = {turns[j] for j in range(N) if j % 2 == 1}
    jacobian = jacobian_matrix()
    rank = exact_rank(jacobian)

    result = {
        "equal_distance_rows": equal_distance_rows(),
        "max_support_intersection": max_support_intersection(),
        "even_turns": even_turns,
        "odd_turns": odd_turns,
        "jacobian_shape": (len(jacobian), len(jacobian[0])),
        "jacobian_rank": rank,
    }
    assert result["equal_distance_rows"] is True
    assert result["max_support_intersection"] == 1
    assert even_turns == {HALF}
    assert odd_turns == {Q3(Fraction(0), Fraction(-1, 2))}
    assert result["jacobian_shape"] == (72, 48)
    assert rank == 44
    return result


def main() -> int:
    result = run_checks()
    print("Equal-distance rows: PASS")
    print(
        "Linearity |S_i cap S_k| <= 1: "
        f"PASS; max intersection = {result['max_support_intersection']}"
    )
    print("Even turns:", result["even_turns"])
    print("Odd turns:", result["odd_turns"])
    print("Convexity failure by alternating turn signs: PASS")
    print("Jacobian shape:", result["jacobian_shape"])
    print("Exact Jacobian rank:", result["jacobian_rank"])
    print("Local rigidity modulo similarities: PASS")
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
