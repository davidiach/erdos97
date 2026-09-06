"""Focused defensive tests; these do not formalize the arbitrary-size proof."""
from __future__ import annotations

from fractions import Fraction as Q
import importlib.util
import json
from pathlib import Path
import random
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from algebra import check_algebra, identical, s, t  # noqa: E402
from intervals import Interval as I  # noqa: E402


def module(name, path):
    """Load a packet module under a packet-specific name.

    Other incoming packets also ship a top-level ``verify.py``; importing it by
    plain module name binds whichever packet was imported first when the whole
    repository is collected in one pytest session.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


verify = module('unbounded_six_family_verify', ROOT / 'verify.py')
build, finite_check, norm = verify.build, verify.finite_check, verify.norm


class AlgebraTests(unittest.TestCase):
    def test_full_coefficient_replay(self):
        self.assertTrue(check_algebra()['status'].startswith('EXACT_ALGEBRA_CHECKS_PASSED'))

    def test_polynomial_cancellation(self):
        self.assertTrue(((s + t) ** 2 - s * s - 2 * s * t - t * t).is_zero())

    def test_wrong_identity_rejected(self):
        with self.assertRaises(AssertionError):
            identical((s + t) ** 2, s * s + t * t, 'deliberately wrong')

    def test_derivative(self):
        self.assertTrue(((s * t * t + 3 * t).dt() - (2 * s * t + 3)).is_zero())

    def test_box_contains_exact_evaluations(self):
        p = 3 * s * s * t * t - 3 * s * s * t + 2 * s * s - 6 * s * t * t + 2 * s * t + t * t + t
        lo, hi = p.box()
        for a in range(11):
            for b in range(11):
                self.assertTrue(lo <= p.evaluate(Q(a, 100), Q(b, 100)) <= hi)

    def test_invalid_exponent(self):
        with self.assertRaises(ValueError):
            _ = s ** -1

    def test_scalar_division_guard(self):
        with self.assertRaises(ZeroDivisionError):
            _ = s / 0

    def test_report_matches_regeneration(self):
        self.assertEqual(json.loads((ROOT / 'algebra_checks.json').read_text()), check_algebra())


class IntervalTests(unittest.TestCase):
    def contains(self, interval, value):
        self.assertLessEqual(Q(interval.lo, 1 << interval.bits), value)
        self.assertLessEqual(value, Q(interval.hi, 1 << interval.bits))

    def test_rational_outward_rounding(self):
        rng = random.Random(970906)
        for _ in range(400):
            a = Q(rng.randint(-10000, 10000), rng.randint(1, 1000))
            b = Q(rng.randint(-10000, 10000), rng.randint(1, 1000))
            x, y = I.exact(a, 64), I.exact(b, 64)
            for v, e in ((x, a), (x + y, a + b), (x - y, a - b), (x * y, a * b), (x.square(), a * a)):
                self.contains(v, e)
            if b:
                self.contains(x / y, a / b)

    def test_square_crossing_zero(self):
        q = I(-3, 4, 64).square()
        self.assertEqual(q.lo, 0)
        self.assertGreaterEqual(q.hi, 0)

    def test_sqrt_outward_rounding(self):
        for a in (Q(0), Q(1), Q(2), Q(3), Q(1, 7), Q(37, 103)):
            q = I.exact(a, 128).sqrt()
            self.assertLessEqual(Q(q.lo, 1 << q.bits) ** 2, a)
            self.assertLessEqual(a, Q(q.hi, 1 << q.bits) ** 2)

    def test_exact_square_root(self):
        q = I.exact(4, 64).sqrt()
        self.assertEqual((q.lo, q.hi), (2 << 64, 2 << 64))

    def test_zero_divisor(self):
        with self.assertRaises(ZeroDivisionError):
            _ = I.exact(1) / I(-1, 1, 256)

    def test_negative_square_root(self):
        with self.assertRaises(ArithmeticError):
            _ = I.exact(-1).sqrt()

    def test_mixed_precision(self):
        with self.assertRaises(ValueError):
            _ = I.exact(1, 64) + I.exact(1, 128)

    def test_empty_intersection(self):
        with self.assertRaises(ValueError):
            I.exact(1).intersect(I.exact(2))

    def test_bad_precision(self):
        for b in (0, 16, True):
            with self.assertRaises(ValueError):
                I(0, 0, b)


class GeometricControlTests(unittest.TestCase):
    def test_six_points(self):
        v = finite_check(1, 256)
        self.assertEqual(v['maximum_multiplicity_distribution'], {2: 3, 3: 3})
        self.assertEqual(v['good_vertices'], 6)

    def test_nine_points(self):
        v = finite_check(2, 256)
        self.assertEqual(v['maximum_multiplicity_distribution'], {2: 3, 3: 3, 4: 3})

    def test_eighteen_points(self):
        v = finite_check(5, 2048)
        self.assertEqual(v['maximum_multiplicity_distribution'], {2: 3, 3: 3, 4: 12})
        self.assertEqual(v['support_checks'], 288)
        self.assertEqual(v['distinct_pairs'], 153)

    def test_precision_agreement(self):
        low, high = finite_check(5, 1024), finite_check(5, 2048)
        for k in ('cyclic_order', 'rows', 'maximum_multiplicity_distribution',
                  'distance_class_separations'):
            self.assertEqual(low[k], high[k])

    def test_insufficient_precision_fails(self):
        with self.assertRaises((ArithmeticError, AssertionError)):
            finite_check(10, 64)

    def test_recurrence_strict_decrease(self):
        reps, ts = build(7, 4096)
        self.assertTrue(all(0 < ts[j + 1].lo <= ts[j + 1].hi < ts[j].lo for j in range(len(ts) - 1)))
        self.assertTrue(all(norm(r).hi < (1 << 4096) for r in reps[1:]))

    def test_rotation_exact_rational_control(self):
        p = (Q(-43, 206), Q(97, 206))
        q = p
        for _ in range(3):
            q = (-(q[0] + 3 * q[1]) / 2, (q[0] - q[1]) / 2)
        self.assertEqual(q, p)
        self.assertEqual(p[0] ** 2 + 3 * p[1] ** 2, Q(73, 103))

    def test_witness_list(self):
        v = finite_check(3, 512)
        r = next(r for r in v['rows'] if r['vertex'] == [3, 0])
        self.assertEqual(len(r['rich_classes']), 1)
        self.assertEqual({tuple(a) for a in r['rich_classes'][0]}, {(0, 0), (2, 0), (3, 1), (3, 2)})

    def test_bad_parameters(self):
        for m, b in ((0, 256), (-1, 256), (True, 256), (1, 32), (1, True)):
            with self.assertRaises(ValueError):
                build(m, b)

    def test_cli_failure_has_no_success_report(self):
        p = subprocess.run([sys.executable, str(ROOT / 'verify.py'), '--chain-orbits', '0'],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)
        self.assertEqual(p.stdout, '')
        self.assertIn('verification failed', p.stderr)

    def test_cli_algebra_only(self):
        p = subprocess.run([sys.executable, str(ROOT / 'verify.py'), '--algebra-only'],
                           capture_output=True, text=True, check=True)
        self.assertEqual(set(json.loads(p.stdout)), {'algebra'})


if __name__ == '__main__':
    unittest.main(verbosity=2)
