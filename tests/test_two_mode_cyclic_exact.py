#!/usr/bin/env python3
"""Focused tests for verify_two_mode_cyclic_exact.py."""

from __future__ import annotations

import cmath
import importlib
import json
import math
import sys
import unittest
from pathlib import Path

import pytest

flint = pytest.importorskip("flint", reason="exact two-mode backend is optional")
arb = flint.arb
ctx = flint.ctx

exact = importlib.import_module("erdos97.two_mode_cyclic_exact")


class ExactTwoModeTests(unittest.TestCase):
    def test_stored_certificate_contract(self) -> None:
        toolchain_error = exact.canonical_toolchain_error()
        if sys.version_info[:2] == exact.CANONICAL_PYTHON:
            self.assertIsNone(toolchain_error)
        else:
            self.assertIn("pinned to CPython 3.12", toolchain_error)
        repo_root = Path(__file__).resolve().parents[1]
        artifact = json.loads(
            (repo_root / "data/certificates/two_mode_cyclic_exact_n80.json").read_text(
                encoding="utf-8"
            )
        )
        totals = artifact["totals"]
        self.assertEqual(artifact["schema"], exact.SCHEMA)
        self.assertEqual(artifact["status"], exact.STATUS)
        self.assertEqual(artifact["trust"], exact.TRUST)
        self.assertEqual(artifact["range"], {"min_n": 9, "max_n": 80})
        self.assertEqual(totals["parameter_pairs"], 2988)
        self.assertEqual(totals["real_root_occurrences"], 1_865_543)
        self.assertEqual(totals["unresolved"], 0)
        self.assertEqual(
            totals["real_root_occurrences"],
            totals["row_failures"] + totals["inradius_strict"] + totals["duplicates"],
        )
        self.assertTrue(
            all(case["maximum_identity_size"] <= 2 for case in artifact["cases"])
        )
        self.assertEqual(
            artifact["case_digest"],
            "fb546261b6d17eb239ad18fb7ec39c15a5685b96cf7de9a8913d07eca1e2f48f",
        )

    def test_cosine_recurrence_and_identity_classes(self) -> None:
        field = exact.build_field(9)
        self.assertEqual(field.cosine[0], field.domain(2))
        self.assertEqual(field.cosine[3], field.domain(-1))
        for k in range(2, 8):
            classes = exact.row_zero_identity_classes(field, k)
            self.assertLessEqual(
                max(len(shifts) for _coefficients, shifts in classes), 2
            )
            self.assertEqual(sum(len(shifts) for _coefficients, shifts in classes), 8)

    def test_root_classification(self) -> None:
        field = exact.build_field(9)
        q = field.domain
        linear = exact.roots_of_collision(field, (q(-1), q(1), q(0)), 40)
        self.assertIsNotNone(linear)
        self.assertEqual(len(linear), 1)
        self.assertTrue(linear[0].ball.contains(1))

        double = exact.roots_of_collision(field, (q(1), q(-2), q(1)), 40)
        self.assertIsNotNone(double)
        self.assertEqual([root.branch for root in double], ["double"])
        self.assertTrue(double[0].ball.contains(1))

        nonreal = exact.roots_of_collision(field, (q(1), q(0), q(1)), 40)
        self.assertEqual(nonreal, ())

        two_real = exact.roots_of_collision(field, (q(-1), q(0), q(1)), 40)
        self.assertIsNotNone(two_real)
        self.assertEqual(len(two_real), 2)
        self.assertTrue(two_real[0].ball.contains(-1))
        self.assertTrue(two_real[1].ball.contains(1))

    def test_certified_band_partition(self) -> None:
        ctx.dps = 40
        values = (
            arb("1 +/- 1e-20"),
            arb("1 +/- 1e-20"),
            arb("2 +/- 1e-20"),
            arb("3 +/- 1e-20"),
            arb("3 +/- 1e-20"),
            arb("3 +/- 1e-20"),
        )
        bands = exact.certified_small_bands(values)
        self.assertIsNotNone(bands)
        self.assertLessEqual(max(map(len, bands)), 3)
        self.assertIsNone(exact.certified_small_bands((arb(1),) * 4))

    def test_inradius_boundary_is_not_strict(self) -> None:
        ctx.dps = 60
        s_values = exact.cosine_balls(12)
        # This regression exercises the boundary distinction: an interval
        # strict checker must not promote equality to a strict obstruction.
        self.assertIsNone(exact.certify_inradius(12, 4, arb(1) / 3, s_values))
        self.assertIsNone(exact.certify_inradius(12, 4, arb(1) / 100, s_values))

        obstructed_parameter = (arb(1) / 5).sqrt().sqrt()
        self.assertIsNotNone(
            exact.certify_inradius(
                60,
                16,
                obstructed_parameter,
                exact.cosine_balls(60),
            )
        )

    def test_duplicate_regression(self) -> None:
        field = exact.build_field(12)
        a, b, c = exact.distance_coefficients(field, 5, 0, 3)
        self.assertEqual(a - b + c, field.domain.zero)

    def test_selected_root_common_factor(self) -> None:
        field = exact.build_field(9)
        q = field.domain
        # (T-1)(T+2) and T-1 share only the upper real branch.
        defining = (q(-2), q(1), q(1))
        upper_query = (q(-1), q(1), q(0))
        lower_query = (q(2), q(1), q(0))
        self.assertFalse(
            exact.root_matches_common_factor(field, defining, upper_query, 0, 60)
        )
        self.assertTrue(
            exact.root_matches_common_factor(field, defining, upper_query, 1, 60)
        )
        self.assertTrue(
            exact.root_matches_common_factor(field, defining, lower_query, 0, 60)
        )
        self.assertFalse(
            exact.root_matches_common_factor(field, defining, lower_query, 1, 60)
        )

    def test_distance_formula_and_row_periodicity(self) -> None:
        n, k, center, shift = 11, 4, 3, 5
        field = exact.build_field(n)
        coefficients = exact.distance_coefficients(field, k, center, shift)
        ctx.dps = 60
        theta = 2 * arb.cos_pi_fmpq(exact.fmpq(2, n))
        parameter = arb(37) / 100
        formula = sum(
            exact.anp_to_arb(coefficient, theta) * parameter**degree
            for degree, coefficient in enumerate(coefficients)
        )
        w = cmath.exp(2j * math.pi / n)
        t = 0.37
        points = [w**index + t * w ** (k * index) for index in range(n)]
        direct = abs(points[(center + shift) % n] - points[center]) ** 2
        self.assertAlmostEqual(float(formula.mid()), direct, places=12)

        n, k = 12, 5
        field = exact.build_field(n)
        d = n // math.gcd(n, k - 1)
        for center in range(d):
            for shift in range(1, n):
                self.assertEqual(
                    exact.distance_coefficients(field, k, center, shift),
                    exact.distance_coefficients(field, k, center + d, shift),
                )

    def test_former_two_mode_hits_are_exact_collision_roots(self) -> None:
        ctx.dps = 60
        field60 = exact.build_field(60)
        collision60 = exact.subtract_coefficients(
            exact.distance_coefficients(field60, 16, 0, 6),
            exact.distance_coefficients(field60, 16, 0, 15),
        )
        roots60 = exact.roots_of_collision(field60, collision60, 60)
        self.assertIsNotNone(roots60)
        self.assertEqual(len(roots60), 2)
        for root in roots60:
            self.assertTrue((root.ball**4 - arb(1) / 5).contains(0))

        field72 = exact.build_field(72)
        sources = ((6, 15), (6, 21), (3, 30), (15, 24))
        qualifying = []
        for left, right in sources:
            collision = exact.subtract_coefficients(
                exact.distance_coefficients(field72, 19, 0, left),
                exact.distance_coefficients(field72, 19, 0, right),
            )
            roots = exact.roots_of_collision(field72, collision, 60)
            self.assertIsNotNone(roots)
            for root in roots:
                quartic = root.ball**4 - 4 * root.ball**2 + 1
                if quartic.contains(0):
                    qualifying.append(root.ball)
        self.assertEqual(len(qualifying), 4)
        qualifying.sort(key=lambda value: float(value.mid()))
        self.assertTrue(
            all(left < right for left, right in zip(qualifying, qualifying[1:]))
        )

    def test_nine_vertex_packet_closes(self) -> None:
        payload = exact.aggregate(9, 9)
        self.assertEqual(payload["status"], exact.STATUS)
        self.assertEqual(payload["totals"]["parameter_pairs"], 6)
        self.assertEqual(payload["totals"]["unresolved"], 0)
        self.assertEqual(payload["totals"]["duplicates"], 4)
        self.assertTrue(
            all(case["maximum_identity_size"] <= 2 for case in payload["cases"])
        )
        self.assertEqual(
            payload["totals"]["real_root_occurrences"],
            payload["totals"]["row_failures"]
            + payload["totals"]["inradius_strict"]
            + payload["totals"]["duplicates"],
        )
        self.assertEqual(
            payload["case_digest"],
            "a10709e2b052d8a7257bcc4b0865d9101f85c7f90b208c0273d912ab5cbcc655",
        )

    def test_parallel_order_is_deterministic(self) -> None:
        serial = exact.aggregate(9, 10, jobs=1)
        parallel = exact.aggregate(9, 10, jobs=2)
        self.assertEqual(serial, parallel)


if __name__ == "__main__":
    unittest.main()
