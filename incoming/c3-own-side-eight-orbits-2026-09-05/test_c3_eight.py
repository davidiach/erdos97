"""Regression tests for the bounded C3 packet, not independent peer review."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from c3_eight_check import Geometry, verify_packet  # noqa: E402
from c3_eight_angles import model  # noqa: E402
from c3_eight_controls import audit_controls, four_orbit_order_control  # noqa: E402

class CertificateTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads((ROOT / 'certificates.json').read_text())
        cls.case = cls.payload['cases'][0]
        cls.geo = Geometry(cls.case['rows'])

    def test_full_exact_certificate_replay(self):
        report = verify_packet()
        self.assertEqual(report['integer_angle_certificates'], 632)
        self.assertEqual(report['obtuse_base_certificates'], 369)

    def test_changed_integer_multiplier_rejected(self):
        cert = copy.deepcopy(self.case['angle_certificate'])
        cert['strict'][0][1] += 1
        with self.assertRaises(ValueError):
            self.geo.verify_angle_certificate(cert)

    def test_float_multiplier_rejected(self):
        cert = copy.deepcopy(self.case['angle_certificate'])
        cert['strict'][0][1] = float(cert['strict'][0][1])
        with self.assertRaises(ValueError):
            self.geo.verify_angle_certificate(cert)

    def test_negative_strict_multiplier_rejected(self):
        cert = copy.deepcopy(self.case['angle_certificate'])
        cert['strict'][0][1] *= -1
        with self.assertRaises(ValueError):
            self.geo.verify_angle_certificate(cert)

    def test_no_strict_premise_rejected(self):
        with self.assertRaises(ValueError):
            self.geo.verify_angle_certificate({'strict': [], 'equal': []})

    def test_unforced_right_angle_rejected(self):
        with self.assertRaises(ValueError):
            self.geo.row(['right_angle', 0, 7, 0], True)

    def test_unknown_premise_rejected(self):
        with self.assertRaises(ValueError):
            self.geo.row(['unknown'], False)

    def test_out_of_range_triangle_rejected(self):
        with self.assertRaises(ValueError):
            self.geo.row(['angle_positive', 0, 1, 99, 0], False)

    def test_wrong_equality_type_rejected(self):
        with self.assertRaises(ValueError):
            self.geo.row(['pi_positive'], True)

    def test_bad_target_types_and_self_target(self):
        for v in [True, '1', 1.5, 0, 99]:
            with self.subTest(value=v):
                rows = copy.deepcopy(self.case['rows'])
                rows[0][0] = v
                with self.assertRaises(ValueError):
                    Geometry(rows)

    def test_bad_gain(self):
        for v in [True, -1, 3, '1']:
            with self.subTest(value=v):
                rows = copy.deepcopy(self.case['rows'])
                rows[0][1] = v
                with self.assertRaises(ValueError):
                    Geometry(rows)

    def test_duplicate_supplier(self):
        rows = copy.deepcopy(self.case['rows'])
        rows[0][2] = rows[0][0]
        with self.assertRaises(ValueError):
            Geometry(rows)

    def test_reciprocal_arrows(self):
        rows = copy.deepcopy(self.case['rows'])
        j = rows[0][0]
        rows[j][0] = 0
        with self.assertRaises(ValueError):
            Geometry(rows)

    def test_duplicate_frontier_case_rejected(self):
        payload = copy.deepcopy(self.payload)
        payload['cases'][1] = copy.deepcopy(payload['cases'][0])
        payload['cases'][1]['index'] = 1
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'bad.json'
            path.write_text(json.dumps(payload))
            with self.assertRaises(ValueError):
                verify_packet(path)

    def test_containment_certificate(self):
        case = next((c for c in self.payload['cases'] if c['containment'] is not None))
        self.assertTrue(Geometry(case['rows']).verify_containment(case['containment']))

    def test_containment_requires_right_angle(self):
        case = next((c for c in self.payload['cases'] if c['containment'] is not None))
        cert = case['containment'][:]
        cert[3] = cert[1]
        with self.assertRaises(ValueError):
            Geometry(case['rows']).verify_containment(cert)

    def test_independent_rotation_and_angle_reconstruction(self):
        A, E, strict, equal = model(self.case['rows'])
        for matrix, labels, equality in [(A, strict, False), (E, equal, True)]:
            for row, label in zip(matrix, labels):
                independent = self.geo.row(label, equality)
                self.assertEqual(tuple(row), tuple((independent.get(v, 0) for v in self.geo.variables)))

    def test_exact_positive_controls(self):
        results = audit_controls()
        self.assertEqual(results['irrational_three_cycle']['maximum_multiplicity_distribution'], {3: 9})
        self.assertEqual(results['two_suppliers_one_center']['maximum_multiplicity_distribution'], {2: 6, 4: 3})

    def test_four_orbit_pythagorean_inequality(self):
        from fractions import Fraction
        result = four_orbit_order_control()
        self.assertGreater(Fraction(result['strict_squared_distance_margin']), 0)

    def test_bad_positive_angle_vector(self):
        payload = json.loads((ROOT / 'positive_angle_vectors.json').read_text())
        payload['irrational_three_cycle'] = ['0'] * len(payload['irrational_three_cycle'])
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'vectors.json'
            path.write_text(json.dumps(payload))
            with self.assertRaises(ValueError):
                audit_controls(path)

@unittest.skipUnless(shutil.which('c++'), 'C++ compiler not installed')
class SearchTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.build = Path(cls.temp.name)
        cls.bins = {}
        for name in ['search', 'oracle']:
            binary = cls.build / name
            subprocess.run(['c++', '-O2', '-std=c++17', '-Wall', '-Wextra', '-Wpedantic', '-Werror', str(ROOT / (name + '.cpp')), '-o', str(binary)], check=True, capture_output=True, timeout=40)
            cls.bins[name] = binary

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def run_solver(self, name, args):
        output = self.build / (name + '.jsonl')
        result = subprocess.run([str(self.bins[name]), '--output', str(output), *args], capture_output=True, text=True, timeout=40)
        return (result, output)

    def test_node_limit_never_reports_exhaustion(self):
        for name in self.bins:
            result, _ = self.run_solver(name, ['--limit', '1'])
            self.assertEqual(result.returncode, 3)
            data = json.loads(result.stdout)
            self.assertFalse(data['exhausted'])
            self.assertFalse(data['decision_complete'])
            self.assertEqual(data['termination_reason'], 'node_limit')

    def test_malformed_numbers_fail_closed(self):
        for name in self.bins:
            for value in ['-1', '1junk', '0x10', '999999999999999999999999999999']:
                with self.subTest(name=name, value=value):
                    result, _ = self.run_solver(name, ['--limit', value])
                    self.assertEqual(result.returncode, 2)
                    self.assertEqual(result.stdout, '')

    def test_invalid_slice(self):
        for name in self.bins:
            result, _ = self.run_solver(name, ['--slice', '21'])
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, '')

    def test_first_abstract_survivor_not_exhaustion(self):
        result, output = self.run_solver('search', [])
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual(data['survivors'], 1)
        self.assertFalse(data['exhausted'])
        self.assertTrue(data['decision_complete'])
        self.assertEqual(data['termination_reason'], 'survivor_found')
        self.assertEqual(len(output.read_text().splitlines()), 1)

    def test_small_case_complete_replays(self):
        for name in ['search', 'oracle']:
            binary = self.build / (name + '5')
            subprocess.run(['c++', '-O2', '-std=c++17', '-DORBIT_COUNT=5', str(ROOT / (name + '.cpp')), '-o', str(binary)], check=True, capture_output=True, timeout=40)
            args = [str(binary), '--output', str(self.build / (name + '5.jsonl'))]
            if name == 'search':
                args.append('--all')
            result = subprocess.run(args, check=True, capture_output=True, text=True, timeout=40)
            data = json.loads(result.stdout)
            self.assertTrue(data['exhausted'])
            self.assertEqual(data['survivors'], 0)
if __name__ == '__main__':
    unittest.main()
