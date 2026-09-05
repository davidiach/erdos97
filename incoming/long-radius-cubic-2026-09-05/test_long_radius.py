"""Exact regression controls; not formal verification of the paper proofs."""
from fractions import Fraction as Q
import json
from pathlib import Path
import unittest

from check_long_radius import (
    algebra_checks, build_report, certify_convex, cube, downward_shortcuts,
    graph_checks, nonconverse_control, power_fixture, rotate, seed_cycle_control,
)


class LongRadiusTests(unittest.TestCase):
    def test_unit_and_cubic_identities(self):
        result = algebra_checks()
        self.assertEqual(result["unit_identity_residual"], {})
        self.assertEqual(result["cubic_identity_residual"], {})
        self.assertEqual(result["conjugate_squared_bound"], "3/4")

    def test_exact_convex_seed_cycle(self):
        result = seed_cycle_control()
        self.assertEqual(result["maximum_multiplicity"], [3]*9)
        self.assertTrue(all(x["rational_noninteger"] for x in result["selected_cycle"]))
        self.assertTrue(result["cube_quotient"]["origin_outside_hull"])

    def test_variable_norm_power_fixture(self):
        result = power_fixture()
        self.assertEqual(result["original"]["supporting_edge_checks"], 399)
        self.assertEqual(result["quotient"]["supporting_edge_checks"], 35)
        self.assertTrue(result["varying_norms"])

    def test_other_power_fixture_sizes(self):
        for m in [3, 4, 8, 12]:
            self.assertEqual(power_fixture(m)["quotient"]["number_of_points"], m)

    def test_power_rotation_identity(self):
        p = (Q(7, 13), Q(-11, 17))
        self.assertEqual(cube(rotate(p)), cube(p))
        self.assertEqual(rotate(rotate(rotate(p))), p)

    def test_nonconverse(self):
        result = nonconverse_control()
        self.assertLess(result["original_hull_vertices"], result["original_points"])
        self.assertEqual(result["strict_interior_coefficients"], ["2/3", "1/6", "1/6"])

    def test_path_obstruction_and_survivor(self):
        result = graph_checks()
        self.assertEqual(len(result["rejected_control"]["obstructions"]), 1)
        self.assertEqual(result["downward_shortcuts"], [])

    def test_invalid_geometry_and_graph_rejected(self):
        with self.assertRaisesRegex(ValueError, "not strictly convex"):
            certify_convex([(Q(0), Q(0)), (Q(1), Q(0)), (Q(2), Q(0))])
        with self.assertRaisesRegex(ValueError, "reciprocal"):
            downward_shortcuts([[1], [0]])

    def test_stored_report(self):
        stored = json.loads((Path(__file__).parent / "report.json").read_text())
        self.assertEqual(stored, build_report())


if __name__ == "__main__":
    unittest.main()
