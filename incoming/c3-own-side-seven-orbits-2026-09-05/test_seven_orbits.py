"""Regression controls for a restricted result, not examples of a counterexample."""
from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


verify = module("seven_verify_test", ROOT / "verify.py")
replay = module("seven_replay_test", ROOT / "replay.py")
RECORDS = json.loads((ROOT / "frontier.json").read_text())["records"]


class ExactGeometryTests(unittest.TestCase):
    def test_polynomial_identity(self):
        self.assertTrue(verify.polynomial_identity())

    def test_valid_local_two_arrow_fixture(self):
        controls = verify.controls()
        self.assertEqual(controls["positive_multiplicity_distribution"], {"2": 6, "4": 3})
        self.assertTrue(controls["two_right_angles_and_crossing"])

    def test_extreme_center_is_required(self):
        self.assertTrue(verify.controls()["extreme_center_hypothesis_control"])
        self.assertFalse(verify.crossing(0, 1, 2, 3, 4))

    def test_chord_crossing_rotation_and_reflection(self):
        for n in (6, 9, 21):
            for endpoints in ((0, 2, 1, 3), (0, 1, 2, 3), (0, 3, 1, 2)):
                expected = verify.crossing(*endpoints, n)
                for sign in (-1, 1):
                    for shift in range(n):
                        transformed = [(sign*v+shift) % n for v in endpoints]
                        self.assertEqual(verify.crossing(*transformed, n), expected)

    def test_every_stored_case_has_a_right_angle_certificate(self):
        result = verify.audit_frontier(full=False)
        self.assertEqual(result["certificates"], 138)

    def test_sample_replays_survive_the_old_filters(self):
        for index in (0, 69, 137):
            self.assertIsNone(verify.before_right_obstruction(RECORDS[index]))

    def test_first_case_certificate_endpoints(self):
        self.assertEqual(verify.right_certificate(RECORDS[0])["opposite_sides"], [[1, 8], [12, 19]])

    def test_shortcut_path_logic(self):
        self.assertTrue(verify.shortcut([[1], [2], [0]]))
        self.assertFalse(verify.shortcut([[2], [0], [1]]))

    def test_controls_survive_json_round_trip(self):
        data = verify.audit_frontier(full=False)
        self.assertEqual(json.loads(json.dumps(data)), data)

    def test_bad_masks_and_self_target_fail(self):
        for mask in (True, 1, 128, 3):
            record = deepcopy(RECORDS[0])
            record[1][0] = mask
            with self.assertRaises(ValueError):
                verify.decode(record)

    def test_malformed_angular_order_and_gain_fail(self):
        record = deepcopy(RECORDS[0])
        record[2][1] = record[2][0]
        with self.assertRaises(ValueError):
            verify.decode(record)
        for value in (-1, 3, True):
            record = deepcopy(RECORDS[0])
            record[3][0] = value
            with self.assertRaises(ValueError):
                verify.decode(record)

    def test_rejecting_center_must_be_in_range(self):
        record = deepcopy(RECORDS[0])
        record[4] = 7
        with self.assertRaises(ValueError):
            verify.right_certificate(record)

    def test_frontier_digest_rejects_tampering(self):
        old = verify.digest(RECORDS)
        records = deepcopy(RECORDS)
        records[0][0] += 1
        self.assertNotEqual(old, verify.digest(records))


class CoverageTests(unittest.TestCase):
    def valid(self):
        return {"first": 0, "stop": 1, "input_graphs": 1, "graphs": 1,
                "exhausted": True, "survivors": 0, "phase_cases": 10,
                "right_angle_rejections": 4, "pair_rejections": 5, "metric_rejections": 1}

    def test_partition_validates(self):
        self.assertEqual(replay.sum_shards([self.valid()], 1)["phase_cases"], 10)

    def test_abort_and_survivor_are_not_exclusions(self):
        for field, value in (("exhausted", False), ("survivors", 1), ("exhausted", "true")):
            record = self.valid()
            record[field] = value
            with self.assertRaises(ValueError):
                replay.sum_shards([record], 1)

    def test_gaps_duplicates_and_missing_shards_fail(self):
        with self.assertRaises(ValueError):
            replay.sum_shards([], 1)
        with self.assertRaises(ValueError):
            replay.sum_shards([self.valid(), self.valid()], 1)
        with self.assertRaises(ValueError):
            replay.sum_shards([self.valid()], 2)

    def test_noninteger_counters_and_wrong_partition_fail(self):
        for field, value in (("phase_cases", 11), ("stop", True), ("first", False), ("metric_rejections", -1)):
            record = self.valid()
            record[field] = value
            with self.assertRaises(ValueError):
                replay.sum_shards([record], 1)


class CompiledReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("c++")
        if compiler is None:
            raise unittest.SkipTest("C++ compiler unavailable")
        cls.temp = tempfile.TemporaryDirectory(prefix="seven-test-")
        cls.work = Path(cls.temp.name)
        cls.binary = cls.work / "search"
        subprocess.run([compiler, "-O2", "-std=c++17", str(ROOT / "search.cpp"), "-o", str(cls.binary)], check=True)
        cls.graphs = cls.work / "graphs.txt"
        result = subprocess.run([str(cls.binary), "--graphs", "--output", str(cls.graphs)],
                                text=True, capture_output=True, check=True)
        cls.graph_report = json.loads(result.stdout)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_complete_graph_count(self):
        self.assertEqual(self.graph_report["oriented_graphs"], 4590360)
        self.assertEqual(self.graph_report["graphs"], 2755)
        self.assertEqual(len(self.graphs.read_text().splitlines()), 2755)

    def test_target_slice_is_exhausted(self):
        result = subprocess.run([str(self.binary), "--phases", str(self.graphs), "--start", "50", "--stop", "51",
                                 "--output", str(self.work / "slice.jsonl")], text=True, capture_output=True, check=True)
        report = json.loads(result.stdout)
        self.assertTrue(report["exhausted"])
        self.assertEqual(report["graphs"], 1)
        self.assertEqual(report["survivors"], 0)
        self.assertEqual(report["phase_cases"], report["right_angle_rejections"]+report["pair_rejections"]
                         +report["radial_kalmanson_rejections"]+report["cycle_kalmanson_rejections"])

    def test_deferred_target_slice_emits_checkable_cases(self):
        path = self.work / "deferred.jsonl"
        result = subprocess.run([str(self.binary), "--phases", str(self.graphs), "--start", "50", "--stop", "51",
                                 "--defer-right-angle", "--output", str(path)], text=True, capture_output=True, check=True)
        report = json.loads(result.stdout)
        cases = [json.loads(line) for line in path.read_text().splitlines()]
        self.assertEqual(report["pre_right_frontier"], len(cases))
        self.assertEqual(len(cases), 2)
        for case in cases:
            verify.right_certificate(case)

    def test_invalid_cli_cannot_emit_exclusion(self):
        for flags in (["--unknown"], ["--graphs", "--start", "-1"],
                      ["--phases", str(self.graphs), "--start", "999999"]):
            result = subprocess.run([str(self.binary), *flags, "--output", str(self.work / "bad.txt")],
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")

    def test_invalid_graph_input_fails(self):
        path = self.work / "bad_graph.txt"
        path.write_text("3 96 65 17 6 12 48\n")
        result = subprocess.run([str(self.binary), "--phases", str(path), "--output", str(self.work / "bad.jsonl")],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
