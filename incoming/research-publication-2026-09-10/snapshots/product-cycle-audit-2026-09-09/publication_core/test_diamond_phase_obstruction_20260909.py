"""Lightweight exact and mutation tests for the published phase certificate."""
import importlib.util
from pathlib import Path
from copy import deepcopy
from fractions import Fraction as F
import json
import subprocess
import sys
import unittest
ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('_diamond_phase_core_20260909', ROOT / 'verify.py')
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)

class DiamondPhaseTests(unittest.TestCase):

    def setUp(self):
        self.data = json.loads((ROOT / 'cases.json').read_text())
        self.rows = self.data['cases'][0]['rows']

    def test_all_three(self):
        self.assertEqual(V.verify_packet(self.data)['fixed_systems'], 3)

    def test_missing_arrow(self):
        self.rows[0] = self.rows[0][2:]
        with self.assertRaises(ValueError):
            V.check(self.rows, self.data['certificate'])

    def test_unmatched_gain(self):
        self.rows[0][1] = 2
        with self.assertRaises(ValueError):
            V.check(self.rows, self.data['certificate'])

    def test_repeated_orbit(self):
        with self.assertRaises(ValueError):
            V.relation(self.rows, 0, 1, 1, 6)

    def test_wrong_phase_order(self):
        self.data['certificate']['strict'][0][0] = ['phase_gap', 3, 1]
        with self.assertRaises(ValueError):
            V.check(self.rows, self.data['certificate'])

    def test_negative_strict_weight(self):
        self.data['certificate']['strict'][0][1] = -1
        with self.assertRaises(ValueError):
            V.check(self.rows, self.data['certificate'])

    def test_noninteger_weight(self):
        self.data['certificate']['strict'][0][1] = 1.0
        with self.assertRaises(ValueError):
            V.check(self.rows, self.data['certificate'])

    def test_corrupt_equality_weight(self):
        self.data['certificate']['equal'][0][1] = 1
        with self.assertRaises(ValueError):
            V.check(self.rows, self.data['certificate'])

    def test_missing_strictness(self):
        self.data['certificate']['strict'] = []
        with self.assertRaises(ValueError):
            V.check(self.rows, self.data['certificate'])

    def test_duplicate_case(self):
        self.data['cases'][1] = deepcopy(self.data['cases'][0])
        with self.assertRaises(ValueError):
            V.verify_packet(self.data)

    def test_positive_single_diamond_phase_control(self):
        rows = [[3, 0, 2, 0], [], [1, 1], [1, 1]]
        eq = V.relation(rows, 0, 2, 3, 1)
        phase = {0: F(0), 1: F(11, 20), 2: F(3, 4), 3: F(4, 5), 'L': F(1)}
        self.assertEqual(sum((w * phase[k] for k, w in eq.items())), 0)
        self.assertTrue(0 < phase[1] < phase[2] < phase[3] < phase['L'])

    def test_disabled_assertions(self):
        p = subprocess.run([sys.executable, '-O', str(ROOT / 'verify.py')], capture_output=True, text=True)
        self.assertNotEqual(p.returncode, 0)
if __name__ == '__main__':
    unittest.main()
