"""Exact rational coefficient checks; no symbolic-algebra package is required.

A pair (x,y) represents x + i*sqrt(3)*y. These checks verify the algebra
used by the paper proof, not a formalization of its geometric implications.
"""
from __future__ import annotations

from fractions import Fraction as Q
from typing import Union

Number = Union[int, Q]


class Poly:
    """Bivariate polynomial over Q; exponent order is (s,t)."""

    def __init__(self, terms=None):
        self.terms = {e: Q(c) for e, c in (terms or {}).items() if c}

    @staticmethod
    def coerce(value):
        return value if isinstance(value, Poly) else Poly({(0, 0): Q(value)})

    def __add__(self, value):
        other = Poly.coerce(value)
        result = self.terms.copy()
        for e, c in other.terms.items():
            result[e] = result.get(e, Q(0)) + c
        return Poly(result)

    __radd__ = __add__

    def __neg__(self):
        return Poly({e: -c for e, c in self.terms.items()})

    def __sub__(self, value):
        return self + -Poly.coerce(value)

    def __rsub__(self, value):
        return Poly.coerce(value) + -self

    def __mul__(self, value):
        other = Poly.coerce(value)
        result = {}
        for (a, b), c in self.terms.items():
            for (d, e), f in other.terms.items():
                k = (a + d, b + e)
                result[k] = result.get(k, Q(0)) + c * f
        return Poly(result)

    __rmul__ = __mul__

    def __truediv__(self, scalar):
        scalar = Q(scalar)
        if not scalar:
            raise ZeroDivisionError('zero polynomial scalar divisor')
        return self * (1 / scalar)

    def __pow__(self, n):
        if not isinstance(n, int) or n < 0:
            raise ValueError('nonnegative integer exponent required')
        result = Poly.coerce(1)
        for _ in range(n):
            result = result * self
        return result

    def dt(self):
        return Poly({(a, b - 1): b * c for (a, b), c in self.terms.items() if b})

    def evaluate(self, s=0, t=0):
        return sum((c * Q(s) ** a * Q(t) ** b for (a, b), c in self.terms.items()), Q(0))

    def box(self, a=Q(1, 10), b=Q(1, 10)):
        """Conservative rational range on [0,a] x [0,b]."""
        lo = hi = Q(0)
        for (i, j), c in self.terms.items():
            if i == j == 0:
                lo += c
                hi += c
            elif c > 0:
                hi += c * a ** i * b ** j
            else:
                lo += c * a ** i * b ** j
        return lo, hi

    def is_zero(self):
        return not self.terms

    def serialized(self):
        return [[a, b, str(c)] for (a, b), c in sorted(self.terms.items())]


s = Poly({(1, 0): 1})
t = Poly({(0, 1): 1})


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def identical(left, right, label):
    require((Poly.coerce(left) - right).is_zero(), f'polynomial identity failed: {label}')


def rot(p):
    return (-(p[0] + 3 * p[1]) / 2, (p[0] - p[1]) / 2)


def dot(p, q):
    return p[0] * q[0] + 3 * p[1] * q[1]


def sub(p, q):
    return p[0] - q[0], p[1] - q[1]


def D(v):
    return 1 + 3 * v * v


# z(v) = numerator(v) / (2 D(v)).
def znum(v):
    return -D(v) + 6 * v, 1 - 3 * v * v


# q(v) = omega^2 z(v); the arc approaching 1 from below.
def qnum(v):
    return 2 - 3 * v - 3 * v * v, 3 * v * (v - 1)


def check_algebra():
    ds, dt = D(s), D(t)
    xs, ys = znum(s)
    xt, yt = znum(t)
    B = 1 - 2 * t + 3 * t * t
    f = s * s - B * s + t * t
    identical(B * B - 4 * t * t, (1 - t) * (1 - 3 * t) * dt, 'recurrence discriminant')
    identical(2 * t * t - B * t, -t * (1 - t) * (1 - 3 * t), 'f_t(t)')
    identical(xs * xs + 3 * ys * ys, 4 * ds * (ds - 3 * s), 'norm of z(s)')
    diff = (xs * dt - xt * ds, -ys * dt - yt * ds)
    residual = dot(diff, diff) - 3 * (xs * xs + 3 * ys * ys) * dt * dt
    identical(residual, -36 * f * ds * dt, 'opposite-arc selected arrow')
    # Distances from the anchor 1 to the three rotations of z(t).
    expected_anchor = [3 * (dt - 3 * t), Poly.coerce(3), 9 * t * t]
    p = (xt, yt)
    for k in range(3):
        delta = (p[0] - 2 * dt, p[1])
        identical(dot(delta, delta), 4 * dt * expected_anchor[k], f'anchor distance {k}')
        p = rot(p)
    identical((3 * (dt - 3 * t)).dt() * dt - 3 * (dt - 3 * t) * dt.dt(),
              -9 * (1 - 3 * t * t), 'anchor M derivative')
    identical(Poly.coerce(3).dt() * dt - 3 * dt.dt(), -18 * t, 'anchor H derivative')
    identical((9 * t * t).dt() * dt - 9 * t * t * dt.dt(), 18 * t, 'anchor L derivative')

    x, y = qnum(s)
    rotated_twice = rot(rot(znum(s)))
    identical(x, rotated_twice[0], 'q equals omega^2 z: real coordinate')
    identical(y, rotated_twice[1], 'q equals omega^2 z: imaginary coordinate')
    normal = (2 * x - ds, 2 * y - ds)
    identical(dot(normal, normal), 12 * ds * ds, 'support normal radius')
    P = {
      (1, 0): 3 * (s - t) ** 2,
      (1, 1): (9 * s * s * t * t + 9 * s * s * t - 18 * s * t * t + 6 * s * t + 3 * t * t - 3 * t + 2) / 2,
      (1, 2): (18 * s * s * t * t - 9 * s * s * t + 3 * s * s + 6 * s * t - 6 * s + 3 * t + 1) / 2,
      (-1, 0): 3 * (3 * s * s * t * t - 3 * s * s * t + 2 * s * s - 6 * s * t * t + 2 * s * t + t * t + t) / 2,
      (-1, 1): (3 * s * t - 1) ** 2,
      (-1, 2): (9 * s * s * t + 3 * s * s + 6 * s * t - 6 * s + 6 * t * t - 3 * t + 1) / 2,
    }
    supports = []
    for eps in (1, -1):
        for k in range(3):
            u, v = qnum(t)
            v = eps * v
            for _ in range(k):
                u, v = rot((u, v))
            delta = (x * dt - u * ds, y * dt - v * ds)
            identical(dot(normal, delta), 12 * ds * P[eps, k], f'support margin {eps},{k}')
            supports.append({'reflection': eps, 'rotation': k,
                             'normalized_polynomial': P[eps, k].serialized()})
    identical(P[-1, 0],
              3 * (s * s * (2 - 3 * t) + 2 * s * t * (1 - 3 * t) + t * t + t + 3 * s * s * t * t) / 2,
              'positive cross-arc decomposition')
    lower = {key: P[key].box()[0] for key in [(1, 1), (1, 2), (-1, 2)]}
    require(lower[(1, 1)] == Q(841, 1000), 'first support lower bound')
    require(lower[(1, 2)] == Q(391, 2000), 'second support lower bound')
    require(lower[(-1, 2)] == Q(1, 20), 'third support lower bound')
    require(1 - 3 * Q(1, 10) ** 2 == Q(97, 100), 'square support factor bound')
    require(2 - 3 * Q(1, 10) > 0 and 1 - 3 * Q(1, 10) > 0, 'positive decomposition coefficients')

    # The exceptional starting orbit is also good, at every chain length.
    a = Q(1, 10)
    seed = (Q(-43, 206), Q(97, 206))
    require(f.evaluate(s=Q(1, 80), t=a) == -Q(7, 32000), 'first iterate upper bound')
    numerators = {
      (1, 0): 9 * (10 * t - 1) ** 2,
      (1, 1): 3 * (219 * t * t - 270 * t + 100),
      (1, 2): 3 * (9 * t * t + 21 * t + 73),
      (-1, 0): 3 * (3 * t - 10) ** 2,
      (-1, 1): 3 * (300 * t * t - 270 * t + 73),
      (-1, 2): 9 * (73 * t * t + 7 * t + 1),
    }
    expected_sign = {(1, 0): -1, (1, 1): -1, (1, 2): 1, (-1, 0): -1, (-1, 1): -1, (-1, 2): 1}
    factored_derivatives = {
      (1, 0): 18 * (3 * t + 10) * (10 * t - 1),
      (1, 1): 162 * (15 * t * t - 3 * t - 5),
      (1, 2): -63 * (3 * t * t + 20 * t - 1),
      (-1, 0): 18 * (3 * t - 10) * (10 * t + 1),
      (-1, 1): 162 * (15 * t * t + 3 * t - 5),
      (-1, 2): -63 * (3 * t * t - 20 * t - 1),
    }
    seed_records = []
    for eps in (1, -1):
        for k in range(3):
            u, v = znum(t)
            v = eps * v
            for _ in range(k):
                u, v = rot((u, v))
            delta = (u / 2 - seed[0] * dt, v / 2 - seed[1] * dt)
            F = numerators[eps, k]
            identical(103 * dot(delta, delta), F * dt, f'seed distance function {eps},{k}')
            derivative = F.dt() * dt - F * dt.dt()
            identical(derivative, factored_derivatives[eps, k],
                      f'seed derivative factorization {eps},{k}')
            lo, hi = derivative.box(b=Q(1, 80))
            sign = expected_sign[eps, k]
            require((lo > 0 if sign > 0 else hi < 0), f'seed derivative sign {eps},{k}')
            seed_records.append({'reflection': eps, 'rotation': k, 'numerator': F.serialized(),
              'denominator': '103*(1+3*t^2)', 'limit_at_zero': str(F.evaluate() / 103),
              'strict_derivative_sign': sign, 'derivative_numerator_range': [str(lo), str(hi)]})
    limits = sorted({Q(r['limit_at_zero']) for r in seed_records})
    require(limits == [Q(9, 103), Q(219, 103), Q(300, 103)], 'seed limits')
    require(all(limits[i + 1] - limits[i] > Q(1, 2) for i in range(2)),
            'disjoint quarter-width bands')
    perturbation = 4 * Q(3, 80) + Q(3, 80) ** 2
    require(perturbation < Q(1, 4), 'distance band perturbation bound')
    # The small anchor-distance range and the two large ranges are disjoint.
    require(Q(9, 100) < 1 and 3 - Q(9, 10) > 2, 'anchor small/large range separation')
    return {'status': 'EXACT_ALGEBRA_CHECKS_PASSED_NOT_FORMAL_GEOMETRIC_PROOF',
      'support_polynomials': supports,
      'support_uniform_lower_bounds': {str(k): str(v) for k, v in lower.items()},
      'squared_support_factor_lower_bound': str(Q(97, 100) ** 2),
      'seed_distance_functions': seed_records,
      'seed_band_perturbation_bound': str(perturbation),
      'first_iterate_below': '1/80',
      'arbitrary_length_theorem': 'paper proof in README.md; independent review pending'}


if __name__ == '__main__':
    import json
    print(json.dumps(check_algebra(), indent=2))
