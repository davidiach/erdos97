"""Regression tests for exact controls; these do not prove the geometry."""
import json
from pathlib import Path
import unittest

from check_side_cap_extension import (
    build_report,
    calibrate_local_row_forcing,
    certify_polygon,
    check_midpoint_terminal,
    check_turn_identity,
    five_point_control,
    nine_point_control,
    point,
    seven_point_control,
)


class SideCapExtensionTests(unittest.TestCase):
    def test_turn_identity(self):
        self.assertEqual(check_turn_identity()["positive_multipliers"], ["2", "1", "1", "1", "1"])

    def test_midpoint_terminal(self):
        self.assertTrue(check_midpoint_terminal()["O_strictly_between_W_and_Z"])

    def test_local_row_forcing(self):
        result = calibrate_local_row_forcing(12)
        self.assertEqual(result["mismatches"], 0)
        self.assertEqual(result["summaries"][-1], {"n": 12, "admissible_rows": 8})

    def test_seven_point_control(self):
        result = seven_point_control()
        self.assertEqual(result["maximum_radius_window_multiplicity_by_label"][0], 4)
        self.assertFalse(result["is_erdos97_counterexample"])

    def test_subthreshold_control(self):
        result = five_point_control()
        self.assertEqual(result["two_witnesses"], [2, 3])

    def test_nine_point_control(self):
        result = nine_point_control()
        self.assertEqual(result["multiplicity_distribution"], {"2": 6, "4": 3})
        self.assertEqual(result["rich_to_cap_squared_ratio"], "7")
        self.assertEqual(result["maximum_norm_orbit"], [0, 3, 6])

    def test_reject_nonconvex_or_duplicate_control(self):
        with self.assertRaisesRegex(ValueError, "strictly convex"):
            certify_polygon([point(0, 0), point(1, 0), point(2, 0)], [0, 1, 2])
        with self.assertRaisesRegex(ValueError, "polygon order"):
            certify_polygon([point(0, 0), point(1, 0), point(0, 1)], [0, 1, 1])

    def test_stored_report(self):
        stored = json.loads((Path(__file__).parent / "side_cap_report.json").read_text())
        self.assertEqual(stored, build_report())


if __name__ == "__main__":
    unittest.main()
