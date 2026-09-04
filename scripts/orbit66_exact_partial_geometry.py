"""Standard-library interval geometry for the orbit66 partial construction."""

from __future__ import annotations

from fractions import Fraction
from math import isqrt
import random
from typing import Any

from scripts.orbit66_exact_partial_data import HISTORY

BITS = 256
SCALE = 1 << BITS


def configure_precision(bits: int) -> None:
    """Configure the common denominator used by all dyadic intervals."""

    global BITS, SCALE
    if bits < 64:
        raise ValueError("precision must be at least 64 bits")
    BITS = bits
    SCALE = 1 << BITS


def ceildiv(numerator: int, denominator: int) -> int:
    return -((-numerator) // denominator)


class Interval:
    """Closed dyadic interval with denominator ``2**BITS``."""

    __slots__ = ("lo", "hi")

    def __init__(self, lo: int, hi: int | None = None) -> None:
        self.lo = lo
        self.hi = lo if hi is None else hi
        if self.lo > self.hi:
            raise ValueError("invalid interval")

    @staticmethod
    def exact(value: int | Fraction) -> Interval:
        rational = Fraction(value)
        return Interval(
            rational.numerator * SCALE // rational.denominator,
            ceildiv(rational.numerator * SCALE, rational.denominator),
        )

    @staticmethod
    def coerce(value: Interval | int | Fraction) -> Interval:
        return value if isinstance(value, Interval) else Interval.exact(value)

    def __add__(self, value: Interval | int | Fraction) -> Interval:
        other = Interval.coerce(value)
        return Interval(self.lo + other.lo, self.hi + other.hi)

    __radd__ = __add__

    def __neg__(self) -> Interval:
        return Interval(-self.hi, -self.lo)

    def __sub__(self, value: Interval | int | Fraction) -> Interval:
        return self + -Interval.coerce(value)

    def __rsub__(self, value: Interval | int | Fraction) -> Interval:
        return Interval.coerce(value) + -self

    def __mul__(self, value: Interval | int | Fraction) -> Interval:
        other = Interval.coerce(value)
        products = (
            self.lo * other.lo,
            self.lo * other.hi,
            self.hi * other.lo,
            self.hi * other.hi,
        )
        return Interval(min(products) // SCALE, ceildiv(max(products), SCALE))

    __rmul__ = __mul__

    def __truediv__(self, value: Interval | int | Fraction) -> Interval:
        other = Interval.coerce(value)
        if other.lo <= 0 <= other.hi:
            raise ZeroDivisionError("interval divisor contains zero")
        quotients = (
            Fraction(numerator * SCALE, denominator)
            for numerator in (self.lo, self.hi)
            for denominator in (other.lo, other.hi)
        )
        quotients = tuple(quotients)
        lower = min(quotients)
        upper = max(quotients)
        return Interval(
            lower.numerator // lower.denominator,
            ceildiv(upper.numerator, upper.denominator),
        )

    def __rtruediv__(self, value: Interval | int | Fraction) -> Interval:
        return Interval.coerce(value) / self

    def square(self) -> Interval:
        lower = (
            0
            if self.lo <= 0 <= self.hi
            else min(self.lo * self.lo, self.hi * self.hi)
        )
        upper = max(self.lo * self.lo, self.hi * self.hi)
        return Interval(lower // SCALE, ceildiv(upper, SCALE))

    def sqrt(self) -> Interval:
        if self.lo < 0:
            raise ValueError("square-root interval crosses negative reals")
        lower = isqrt(self.lo * SCALE)
        scaled_upper = self.hi * SCALE
        upper = isqrt(scaled_upper)
        if upper * upper < scaled_upper:
            upper += 1
        return Interval(lower, upper)


Point = tuple[Interval, Interval]
Arc = tuple[int, int, int]


def add(left: Point, right: Point) -> Point:
    return (left[0] + right[0], left[1] + right[1])


def subtract(left: Point, right: Point) -> Point:
    return (left[0] - right[0], left[1] - right[1])


def scale(point: Point, scalar: Interval | int | Fraction) -> Point:
    return (point[0] * scalar, point[1] * scalar)


def norm_squared(point: Point) -> Interval:
    return point[0].square() + point[1].square()


def squared_distance(left: Point, right: Point) -> Interval:
    return norm_squared(subtract(left, right))


def determinant(left: Point, right: Point) -> Interval:
    return left[0] * right[1] - left[1] * right[0]


def orientation(a: Point, b: Point, c: Point) -> Interval:
    return determinant(subtract(b, a), subtract(c, a))


def rotate(point: Point, power: int) -> Point:
    root_three = Interval.exact(3).sqrt()
    result = point
    for _ in range(power % 3):
        result = (
            (-result[0] - root_three * result[1]) / 2,
            (root_three * result[0] - result[1]) / 2,
        )
    return result


def constraint_circle(point: Point, direction: str) -> tuple[Point, Interval]:
    if direction == "in":
        return point, 3 * norm_squared(point)
    if direction == "out":
        return scale(point, Fraction(-1, 2)), 3 * norm_squared(point) / 4
    raise ValueError(f"unknown direction {direction!r}")


def intersect_circles(
    first_center: Point,
    second_center: Point,
    first_radius_squared: Interval,
    second_radius_squared: Interval,
    branch: int,
) -> tuple[Point, Interval]:
    """Enclose the selected exact intersection of two transverse circles."""

    if branch not in (0, 1):
        raise ValueError("invalid root branch")
    delta = subtract(second_center, first_center)
    distance_squared = norm_squared(delta)
    if distance_squared.lo <= 0:
        raise ArithmeticError("circle centers are not provably distinct")
    parameter = (
        first_radius_squared - second_radius_squared + distance_squared
    ) / (2 * distance_squared)
    height_squared = first_radius_squared / distance_squared - parameter.square()
    if height_squared.lo <= 0:
        raise ArithmeticError("circle intersection is not provably transverse")
    height = height_squared.sqrt()
    if branch == 1:
        height = -height
    perpendicular = (-delta[1], delta[0])
    point = add(
        add(first_center, scale(delta, parameter)),
        scale(perpendicular, height),
    )
    return point, height_squared


def check_seed_equalities() -> None:
    """Check the three rational seed arrows exactly in Q(sqrt(3))."""

    rational = Fraction
    # A pair (X,Y) denotes the physical point (sqrt(3) X, Y).
    seeds = (
        (rational(0), rational(2)),
        (-rational(8991, 10927), -rational(26503, 10927)),
        (-rational(10753, 18529), -rational(44665, 18529)),
    )

    def rotate_seed(
        point: tuple[Fraction, Fraction], power: int
    ) -> tuple[Fraction, Fraction]:
        result = point
        for _ in range(power % 3):
            result = (
                (-result[0] - result[1]) / 2,
                (3 * result[0] - result[1]) / 2,
            )
        return result

    def seed_norm_squared(point: tuple[Fraction, Fraction]) -> Fraction:
        return 3 * point[0] ** 2 + point[1] ** 2

    for source, target, phase in ((0, 1, 1), (1, 2, 1), (2, 0, 0)):
        center = seeds[source]
        witness = rotate_seed(seeds[target], phase)
        difference = (center[0] - witness[0], center[1] - witness[1])
        assert seed_norm_squared(difference) == 3 * seed_norm_squared(center)


def interval_self_test() -> None:
    """Exercise outward rounding against exact rational arithmetic."""

    rng = random.Random(970904)
    for _ in range(1_000):
        left = Fraction(rng.randint(-10_000, 10_000), rng.randint(1, 1_000))
        right = Fraction(rng.randint(-10_000, 10_000), rng.randint(1, 1_000))
        left_interval = Interval.exact(left)
        right_interval = Interval.exact(right)
        checks = [
            (left_interval + right_interval, left + right),
            (left_interval - right_interval, left - right),
            (left_interval * right_interval, left * right),
            (left_interval.square(), left * left),
        ]
        if right:
            checks.append((left_interval / right_interval, left / right))
        for enclosure, exact in checks:
            assert Fraction(enclosure.lo, SCALE) <= exact
            assert exact <= Fraction(enclosure.hi, SCALE)
        square_root = Interval.exact(abs(left)).sqrt()
        assert Fraction(square_root.lo, SCALE) ** 2 <= abs(left)
        assert abs(left) <= Fraction(square_root.hi, SCALE) ** 2


def build_representatives() -> tuple[list[Point], list[Arc], list[Interval]]:
    """Build interval enclosures and the exact selected-arrow bookkeeping."""

    root_three = Interval.exact(3).sqrt()
    representatives: list[Point] = [
        (Interval.exact(0), Interval.exact(2)),
        (
            -root_three * Fraction(8991, 10927),
            Interval.exact(-Fraction(26503, 10927)),
        ),
        (
            -root_three * Fraction(10753, 18529),
            Interval.exact(-Fraction(44665, 18529)),
        ),
    ]
    arcs: list[Arc] = [(0, 1, 1), (1, 2, 1), (2, 0, 0)]
    radicands: list[Interval] = []

    for first, second, phase, first_direction, second_direction, branch in HISTORY:
        new_index = len(representatives)
        if not (0 <= first < second < new_index and 0 <= phase < 3):
            raise ValueError("invalid construction history reference")
        first_center, first_radius_squared = constraint_circle(
            representatives[first], first_direction
        )
        rotated_second = rotate(representatives[second], phase)
        second_center, second_radius_squared = constraint_circle(
            rotated_second, second_direction
        )
        new_point, radicand = intersect_circles(
            first_center,
            second_center,
            first_radius_squared,
            second_radius_squared,
            branch,
        )
        representatives.append(new_point)
        radicands.append(radicand)

        if first_direction == "in":
            arcs.append((first, new_index, 0))
        else:
            arcs.append((new_index, first, 0))
        if second_direction == "in":
            arcs.append((second, new_index, (-phase) % 3))
        else:
            arcs.append((new_index, second, phase))

    return representatives, arcs, radicands


def dyadic_lower_bound(numerator: int) -> dict[str, Any]:
    return {
        "numerator": str(numerator),
        "denominator_power_of_two": BITS,
        "decimal_approximation_not_used_as_proof": float(
            Fraction(numerator, SCALE)
        ),
    }

