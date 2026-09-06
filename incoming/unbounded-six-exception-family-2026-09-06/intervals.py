"""Outward-rounded dyadic interval arithmetic using only Python integers.

The construction follows the prior 2026-09-06 packet's interval technique,
with per-object precision and explicit mixed-precision rejection.
"""
from __future__ import annotations

from fractions import Fraction
from math import isqrt


class Interval:
    __slots__ = ('lo', 'hi', 'bits')

    def __init__(self, lo: int, hi: int, bits: int):
        if not isinstance(bits, int) or isinstance(bits, bool) or bits < 32:
            raise ValueError('precision must be an integer of at least 32 bits')
        if lo > hi:
            raise ValueError('reversed interval')
        self.lo, self.hi, self.bits = lo, hi, bits

    @staticmethod
    def exact(value, bits=256):
        q = Fraction(value)
        scale = 1 << bits
        return Interval(q.numerator * scale // q.denominator,
                        -((-q.numerator * scale) // q.denominator), bits)

    def coerce(self, x):
        if not isinstance(x, Interval):
            return Interval.exact(x, self.bits)
        if x.bits != self.bits:
            raise ValueError('mixed interval precisions')
        return x

    def __add__(self, x):
        x = self.coerce(x)
        return Interval(self.lo + x.lo, self.hi + x.hi, self.bits)

    __radd__ = __add__

    def __neg__(self):
        return Interval(-self.hi, -self.lo, self.bits)

    def __sub__(self, x):
        return self + -self.coerce(x)

    def __rsub__(self, x):
        return self.coerce(x) + -self

    def __mul__(self, x):
        x = self.coerce(x)
        v = [a * b for a in (self.lo, self.hi) for b in (x.lo, x.hi)]
        scale = 1 << self.bits
        return Interval(min(v) // scale, -((-max(v)) // scale), self.bits)

    __rmul__ = __mul__

    def __truediv__(self, x):
        x = self.coerce(x)
        if x.lo <= 0 <= x.hi:
            raise ZeroDivisionError('interval divisor contains zero')
        scale = 1 << self.bits
        v = [Fraction(a * scale, b) for a in (self.lo, self.hi) for b in (x.lo, x.hi)]
        lo, hi = min(v), max(v)
        return Interval(lo.numerator // lo.denominator,
                        -((-hi.numerator) // hi.denominator), self.bits)

    def __rtruediv__(self, x):
        return self.coerce(x) / self

    def square(self):
        scale = 1 << self.bits
        lo = 0 if self.lo <= 0 <= self.hi else min(self.lo * self.lo, self.hi * self.hi)
        hi = max(self.lo * self.lo, self.hi * self.hi)
        return Interval(lo // scale, -((-hi) // scale), self.bits)

    def sqrt(self):
        if self.lo < 0:
            raise ArithmeticError('square root not certified nonnegative')
        scale = 1 << self.bits
        lo = isqrt(self.lo * scale)
        hi = isqrt(self.hi * scale)
        if hi * hi < self.hi * scale:
            hi += 1
        return Interval(lo, hi, self.bits)

    def intersect(self, other):
        other = self.coerce(other)
        return Interval(max(self.lo, other.lo), min(self.hi, other.hi), self.bits)
