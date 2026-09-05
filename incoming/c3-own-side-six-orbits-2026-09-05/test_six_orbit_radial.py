"""Exact regression tests; no numerical near-miss is accepted as evidence."""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import importlib.util
from itertools import permutations, product
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("six_orbit_radial_certificate", ROOT / "certificate.py")
assert SPEC is not None and SPEC.loader is not None
c = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(c)


class SixOrbitRadialTests(unittest.TestCase):
    def test_graph_automorphisms_are_bijections(self):
        autos = c.automorphisms()
        self.assertEqual(len(set(autos)), 24)
        for image in autos:
            self.assertEqual(set(image), set(range(6)))
            for v in range(6):
                self.assertEqual({image[w] for w in c.ROWS[v]}, set(c.ROWS[image[v]]))

    def test_radial_coverage_is_complete(self):
        records = c.radius_audit()
        self.assertEqual({tuple(r["order"]) for r in records}, set(permutations(range(6))))
        self.assertEqual(sum("downward_triangle" in r for r in records), 672)
        self.assertEqual(Counter(tuple(r["canonical"]) for r in records if "canonical" in r),
                         Counter({order: 24 for order in c.CANONICAL}))

    def test_every_radial_rejection_has_a_downward_triangle(self):
        for record in c.radius_audit():
            if "downward_triangle" not in record:
                continue
            lo, mid, hi = record["downward_triangle"]
            rank = {v: i for i, v in enumerate(record["order"])}
            self.assertLess(rank[lo], rank[mid])
            self.assertLess(rank[mid], rank[hi])
            self.assertEqual(len({lo // 2, mid // 2, hi // 2}), 3)
            self.assertIn(lo, c.ROWS[hi])

    def test_gain_rules_match_open_angular_sectors(self):
        for radial in c.CANONICAL:
            rank = {v: i for i, v in enumerate(radial)}
            for order in permutations(range(6)):
                pos = {v: i for i, v in enumerate(order)}
                for source in range(6):
                    for target in c.ROWS[source]:
                        expected = []
                        for gain in range(3):
                            sector = (pos[target] - pos[source] + 6 * gain) % 18
                            downward = rank[target] < rank[source]
                            admissible = (6 < sector < 12) if downward else (sector < 6 or sector > 12)
                            if admissible:
                                expected.append(gain)
                        self.assertEqual(set(c.allowed_gains(source, target, rank, pos)), set(expected))

    def test_case_counts_and_unique_keys(self):
        for radial in c.CANONICAL:
            entries = list(c.cases(radial))
            self.assertEqual(len(entries), 1920)
            self.assertEqual(len(set(entries)), 1920)
            self.assertEqual(len({order for order, _ in entries}), 120)

    def test_expansion_has_four_distinct_witnesses_and_rotation_covariance(self):
        for radial in c.CANONICAL:
            for order, gains in c.cases(radial):
                rows = c.expand(order, gains)
                for i, row in enumerate(rows):
                    self.assertEqual(len(set(row)), 4)
                    self.assertNotIn(i, row)
                    self.assertEqual({(j + 6) % 18 for j in row}, set(rows[(i + 6) % 18]))

    def test_invalid_gain_rejected(self):
        for gains in ((0,) * 11, (0,) * 11 + (3,), (0,) * 11 + (False,)):
            with self.assertRaises(ValueError):
                c.expand(c.CANONICAL[0], gains)

    def test_invalid_order_rejected(self):
        with self.assertRaises(ValueError):
            c.expand((0, 0, 1, 2, 3, 4), (0,) * 12)

    def test_exact_three_witness_positive_control_survives(self):
        result = c.positive_control()
        self.assertEqual(result["maximum_multiplicities"], [3] * 9)
        self.assertTrue(result["passes_exact_filters"])

    def test_all_certificates_and_stored_report(self):
        report, certificates = c.generate()
        self.assertEqual(report, json.loads((ROOT / "report.json").read_text()))
        self.assertEqual(len(certificates), 3840)
        self.assertEqual(report["survivors"], 0)
        for record in certificates:
            c.verify_certificate(c.expand(record["angle_order"], record["gains"]),
                                 record["certificate"])

    def test_tampered_crossing_certificate_rejected(self):
        order, gains = next(c.cases(c.CANONICAL[0]))
        rows = c.expand(order, gains)
        certificate = c.find_certificate(rows)
        self.assertEqual(certificate["kind"], "crossing")
        certificate["witnesses"][0] = certificate["centers"][0]
        with self.assertRaises(ValueError):
            c.verify_certificate(rows, certificate)

    def test_tampered_inverse_certificate_rejected(self):
        order, gains = list(c.cases(c.CANONICAL[0]))[417]
        rows = c.expand(order, gains)
        certificate = c.find_certificate(rows)
        self.assertEqual(certificate["kind"], "kalmanson_inverse")
        bad = deepcopy(certificate)
        bad["inequalities"][1] = bad["inequalities"][0]
        with self.assertRaises(ValueError):
            c.verify_certificate(rows, bad)

    def test_invalid_inequality_and_rows_rejected(self):
        order, gains = list(c.cases(c.CANONICAL[0]))[417]
        rows = c.expand(order, gains)
        certificate = c.find_certificate(rows)
        bad = deepcopy(certificate)
        bad["inequalities"][0][4] = 2
        with self.assertRaises(ValueError):
            c.verify_certificate(rows, bad)
        rows[0].append(0)
        with self.assertRaises(ValueError):
            c.verify_certificate(rows, certificate)

    def test_cubic_identity_exact_calibration(self):
        def mul(a, b):
            return (a[0] * b[0] - 3 * a[1] * b[1], a[0] * b[1] + a[1] * b[0])

        def norm(a):
            return a[0] ** 2 + 3 * a[1] ** 2

        def sub(a, b):
            return (a[0] - b[0], a[1] - b[1])

        omega = (Q(-1, 2), Q(1, 2))
        for coordinates in product((Q(-2, 3), Q(0), Q(5, 7)), repeat=4):
            a, b = coordinates[:2], coordinates[2:]
            s, t = norm(a), norm(b)
            lhs, rotated = Q(1), b
            for _ in range(3):
                lhs *= norm(sub(a, rotated)) - 3 * s
                rotated = mul(omega, rotated)
            a3, b3 = mul(mul(a, a), a), mul(mul(b, b), b)
            self.assertEqual(lhs, norm(sub(a3, b3)) - 9 * s * (s - t) ** 2)


if __name__ == "__main__":
    unittest.main()
