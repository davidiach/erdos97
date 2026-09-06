"""Standard-library symbolic identities and an exact convex transitive control."""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction as Q
from itertools import combinations
from core import require

def add(a: dict, b: dict) -> dict:
    out = a.copy()
    for key, value in b.items():
        out[key] = out.get(key, 0) + value
    return {k: v for k, v in out.items() if v}

def mul(a: dict, b: dict, reduce_e: bool=False) -> dict:
    out = {}
    for key, v in a.items():
        for other, w in b.items():
            exponent = tuple((x + y for x, y in zip(key, other)))
            if reduce_e:
                r = exponent[-1] % 3
                terms = [(exponent[:-1] + (r,), 1)] if r < 2 else [(exponent[:-1] + (0,), -1), (exponent[:-1] + (1,), -1)]
            else:
                terms = [(exponent, 1)]
            for monomial, c in terms:
                out[monomial] = out.get(monomial, 0) + c * v * w
    return {k: v for k, v in out.items() if v}

def scaled(p: dict, n: int) -> dict:
    return {k: v * n for k, v in p.items() if v * n}

def polynomial_checks() -> dict:
    one = {(0, 0, 0): 1}
    x = {(1, 0, 0): 1}
    y = {(0, 1, 0): 1}
    e = {(0, 0, 1): 1}
    xy = mul(x, y)

    def factor_expression(eta, reduce_e):
        left = mul(mul(add(x, scaled(one, 2)), add(y, scaled(one, 2)), reduce_e), add(mul(eta, xy, reduce_e), scaled(one, -1)), reduce_e)
        right = mul(mul(eta, add(mul(eta, xy, reduce_e), scaled(one, 2)), reduce_e), mul(add(x, scaled(one, -1)), add(y, scaled(one, -1)), reduce_e), reduce_e)
        return add(left, scaled(right, -1))
    expected = scaled(add(mul(xy, add(x, y)), scaled(one, -2)), 3)
    require(factor_expression(one, False) == expected, 'coherent triangle factor identity')
    e2 = mul(e, e, True)
    primitive = mul(mul(mul(add(scaled(e, 2), one), add(x, scaled(e2, -1)), True), add(y, scaled(e2, -1)), True), add(xy, scaled(one, 2)), True)
    require(factor_expression(e, True) == primitive, 'primitive triangle factor identity')
    U = x
    V = y
    T = {(0, 0, 1): 1}
    lhs = add(mul(T, mul(add(U, scaled(one, -1)), add(V, scaled(one, -1)))), scaled(mul(add(T, scaled(one, -1)), add(T, scaled(one, -4))), -1))
    rhs = add(mul(T, add(mul(U, V), scaled(T, -1))), scaled(add(add(mul(T, add(U, V)), scaled(T, -6)), scaled(one, 4)), -1))
    require(lhs == rhs, 'radius factor identity')
    z = T
    left = add(mul(x, add(x, y)), scaled(mul(z, add(y, z)), -1))
    right = mul(add(x, scaled(z, -1)), add(add(x, y), z))
    require(left == right, 'diamond ratio rigidity identity')
    return {'coherent_circle_factor': True, 'primitive_circle_factor_mod_e2_e_1': True, 'transitive_radius_factor': True, 'diamond_ratio_rigidity': True, 'numerical_tolerances_used': False}
H2 = Q(17745, 114244)

@dataclass(frozen=True)
class R:
    a: Q = Q(0)
    b: Q = Q(0)

    def __post_init__(self):
        object.__setattr__(self, 'a', Q(self.a))
        object.__setattr__(self, 'b', Q(self.b))

    @staticmethod
    def of(x):
        return x if isinstance(x, R) else R(Q(x))

    def __add__(self, x):
        x = R.of(x)
        return R(self.a + x.a, self.b + x.b)
    __radd__ = __add__

    def __neg__(self):
        return R(-self.a, -self.b)

    def __sub__(self, x):
        return self + -R.of(x)

    def __rsub__(self, x):
        return R.of(x) + -self

    def __mul__(self, x):
        x = R.of(x)
        return R(self.a * x.a + self.b * x.b * H2, self.a * x.b + self.b * x.a)
    __rmul__ = __mul__

    def __truediv__(self, x):
        x = R.of(x)
        den = x.a * x.a - x.b * x.b * H2
        require(den != 0, 'division by zero')
        return self * R(x.a / den, -x.b / den)

    def __pow__(self, n):
        require(type(n) is int and n >= 0, 'nonnegative power required')
        result = R(1)
        for _ in range(n):
            result = result * self
        return result

    def sign(self):
        if not self.b:
            return (self.a > 0) - (self.a < 0)
        if not self.a:
            return (self.b > 0) - (self.b < 0)
        if self.a > 0 and self.b > 0:
            return 1
        if self.a < 0 and self.b < 0:
            return -1
        gap = self.a * self.a - self.b * self.b * H2
        return ((gap > 0) - (gap < 0)) * (1 if self.a > 0 else -1)

    def display(self):
        return [str(self.a), str(self.b)]

def rotation(z):
    x, y = z
    return (-(x + 3 * y) / 2, (x - y) / 2)

def norm(z):
    return z[0] ** 2 + 3 * z[1] ** 2

def distance(a, b):
    return norm((a[0] - b[0], a[1] - b[1]))

def area(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

def transitive_control() -> dict:
    a = (R(1), R(0))
    b = (R(Q(-19, 26)), R(Q(-1, 26)))
    s = Q(91, 169)
    t = 1 - s / 2
    h = R(0, 1)
    require(H2 == s * (4 - s) / 12, 'circle-intersection radical')
    dx, dy = (b[0] - 1, b[1])
    c = (1 + t * dx - 3 * dy * h, t * dy + dx * h)
    reps = [a, b, c]
    points = reps + [rotation(z) for z in reps] + [rotation(rotation(z)) for z in reps]
    order = [6, 2, 4, 0, 5, 7, 3, 8, 1]
    checks = [area(points[order[i]], points[order[(i + 1) % 9]], points[j]) for i in range(9) for j in range(9) if j not in (order[i], order[(i + 1) % 9])]
    require(all((x.sign() > 0 for x in checks)), 'transitive control convexity')
    for i, j in combinations(range(9), 2):
        require(distance(points[i], points[j]).sign() > 0, 'duplicate control point')
    arrows = [(0, 1), (0, 2), (1, 2)]
    require(all((distance(reps[i], reps[j]) == 3 * norm(reps[i]) for i, j in arrows)), 'false transitive control arrow')
    require((norm(a) - norm(b)).sign() > 0 and (norm(c) - norm(a)).sign() > 0, 'transitive radius order')
    profiles = [Counter((distance(p, q) for j, q in enumerate(points) if i != j)) for i, p in enumerate(points)]
    maxima = [max(row.values()) for row in profiles]
    require(maxima == [4, 3, 2] * 3, 'transitive control multiplicities')
    return {'coordinate_convention': '(x,sqrt(3)*y), with x,y in Q(h)', 'h_squared': str(H2), 'h_positive': True, 'representatives': [[x.display(), y.display()] for x, y in reps], 'counterclockwise_order': order, 'exact_support_checks': len(checks), 'arrows_zero_gain': [list(edge) for edge in arrows], 'squared_radii': [norm(z).display() for z in reps], 'radial_order': 'r_b < r_a < r_c', 'maximum_multiplicities': maxima, 'not_a_counterexample': True, 'floating_point_used': False}
