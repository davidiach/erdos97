"""Exact positive controls, proof tampering, coverage, and replay-contract tests."""
from __future__ import annotations
import copy
from fractions import Fraction as Q
import gzip
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest
from algebra_controls import R, polynomial_checks, transitive_control, rotation, distance, norm
from core import AngleModel, check_rational_feasible, verify_certificate
from graph_domain import ascending_transitive, contains_diamond, phase_count, target_graph
from verify import ROOT, diamond_arrows, load, seven_model_input, verify_diamond, verify_transitive_radius, static_report

class ExactTests(unittest.TestCase):

    def test_polynomial_factorizations(self):
        self.assertTrue(all((v for k, v in polynomial_checks().items() if k != 'numerical_tolerances_used')))

    def test_quadratic_field_sign(self):
        self.assertEqual(R(0, 1).sign(), 1)
        self.assertEqual(R(0, -1).sign(), -1)
        self.assertEqual(R(1, -2).sign(), 1)
        self.assertEqual(R(1, -3).sign(), -1)
        self.assertEqual(R(-1, 3).sign(), 1)
        self.assertEqual(R(0).sign(), 0)

    def test_transitive_positive_control(self):
        r = transitive_control()
        self.assertEqual(r['maximum_multiplicities'], [4, 3, 2] * 3)
        self.assertEqual(r['exact_support_checks'], 63)
        self.assertTrue(r['not_a_counterexample'])

    def test_positive_transitive_angle_model(self):
        record = transitive_control()
        reps = [tuple((R(Q(x[0]), Q(x[1])) for x in z)) for z in record['representatives']]
        phase_reps = [reps[0], rotation(reps[2]), rotation(rotation(reps[1]))]
        arrows = [(0, 2, 1), (0, 1, 2), (2, 1, 1)]
        for a, b, g in arrows:
            w = phase_reps[b]
            for _ in range(g):
                w = rotation(w)
            self.assertEqual(distance(phase_reps[a], w), 3 * norm(phase_reps[a]))
        A, E = AngleModel(3).build(arrows, [(0, 2), (1, 2), (1, 0)])
        check_rational_feasible(A, E, ['0', '14', '17', '18', '23', '31', '32', '18', '20', '24', '33', '27', '12'])

    def test_previous_guardrail_has_diamond(self):
        self.assertEqual(contains_diamond(target_graph()), (0, 2, 1, 6))

    def test_transitive_radius_rule_not_all_transitive_triangles(self):
        self.assertEqual(ascending_transitive([6, 4, 0]), (0, 1, 2))
        self.assertIsNone(ascending_transitive([4, 5, 0]))

    def test_all_transitive_radius_certificates(self):
        self.assertEqual(verify_transitive_radius()['cases'], 18)

    def test_generated_static_report(self):
        self.assertEqual(static_report(), load('report.json'))

    def test_all_diamond_certificates(self):
        self.assertEqual(verify_diamond()['cases'], 162)

    def test_missing_diamond_case_rejected(self):
        with self.assertRaisesRegex(ValueError, 'coverage'):
            verify_diamond(load('diamond_certificates.json')[:-1])

    def test_duplicate_diamond_case_rejected(self):
        records = load('diamond_certificates.json')
        records[-1] = copy.deepcopy(records[0])
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            verify_diamond(records)

    def test_damaged_integer_certificate_rejected(self):
        r = load('diamond_certificates.json')[0]
        A, E = AngleModel(4).build(diamond_arrows(r), [])
        bad = copy.deepcopy(r['positive'])
        bad[0][1] += 1
        with self.assertRaisesRegex(ValueError, 'nonzero'):
            verify_certificate(A, E, bad, r['equality'])

    def test_invalid_positive_multiplier_rejected(self):
        r = load('diamond_certificates.json')[0]
        A, E = AngleModel(4).build(diamond_arrows(r), [])
        bad = copy.deepcopy(r['positive'])
        bad[0][1] = 0
        with self.assertRaisesRegex(ValueError, 'sign'):
            verify_certificate(A, E, bad, r['equality'])

    def test_seven_residual_certificate(self):
        r = load('seven_angle_certificates.json')[0]
        A, E = AngleModel(7).build(*seven_model_input(r))
        verify_certificate(A, E, r['positive'], r['equality'])
        with self.assertRaisesRegex(ValueError, 'strict positive'):
            verify_certificate(A, E, [], r['equality'])

    def test_phase_domain_count(self):
        self.assertEqual(phase_count(load('radial_graphs.json')), 7718400)

    def test_full_graph_oracle_alignment(self):
        r = load('graph_oracle_report.json')
        self.assertTrue(r['exhausted'])
        self.assertEqual(r['complete_tuples'], 15 ** 7)
        self.assertEqual(r['graphs'], load('radial_graphs.json'))

    def test_proof_stream_record_count(self):
        total = 0
        with gzip.open(ROOT / 'phase_certificates.bin.gz', 'rb') as stream:
            self.assertEqual(stream.read(8), b'C3P7v1\r\n')
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                total += len(chunk)
        self.assertEqual(total, 5 * 7718400)

class CompiledTamperingTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        compiler = shutil.which('c++')
        if not compiler:
            raise unittest.SkipTest('C++ compiler unavailable')
        cls.tmp = tempfile.TemporaryDirectory(prefix='erdos97-proof-tamper-')
        cls.binary = Path(cls.tmp.name) / 'replay'
        subprocess.run([compiler, '-O2', '-std=c++17', str(ROOT / 'phase_replay.cpp'), '-o', str(cls.binary)], check=True)
        cls.input = (ROOT / 'radial_graphs.txt').read_text().splitlines()[0] + '\n'

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def rejected(self, payload, reason):
        path = Path(self.tmp.name) / 'damaged.bin'
        path.write_bytes(payload)
        result = subprocess.run([str(self.binary), str(path)], input=self.input, text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn(reason, result.stderr)
        self.assertEqual(result.stdout, '')

    def test_wrong_header(self):
        self.rejected(b'notproof', 'format')

    def test_missing_record(self):
        self.rejected(b'C3P7v1\r\n', 'truncated')

    def test_unknown_record(self):
        self.rejected(b'C3P7v1\r\n' + struct.pack('<BHH', 5, 0, 0), 'unknown')

    def test_invalid_inequality(self):
        self.rejected(b'C3P7v1\r\n' + struct.pack('<BHH', 2, 65535, 65535), 'index out of range')

    def test_wrong_residual_index(self):
        self.rejected(b'C3P7v1\r\n' + struct.pack('<BHH', 4, 1, 0), 'coverage')
if __name__ == '__main__':
    unittest.main()
