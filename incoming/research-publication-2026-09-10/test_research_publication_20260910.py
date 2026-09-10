"""Defensive checks for the maintained importer and sparse certificate replay."""
from copy import deepcopy
import importlib.util
from itertools import combinations
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


P = module('_research_pub_20260910', ROOT / 'publication.py')
A = module('_research_angles_20260910', ROOT / 'verify_attachment_angles.py')
OLD = module('_original_angle_check_20260909', ROOT / 'snapshots/unrestricted-angle-bridge-2026-09-09/verify/check_angles.py')
CAT = P.load(A.SOURCE / 'two_star_angles.json')
BAD = next(c for c in CAT['cases'] if 'certificate' in c['result'])
GOOD = next(c for c in CAT['cases'] if 'chord_directions_over_pi' in c['result'])


class PublicationTests(unittest.TestCase):
    def test_integrity(self):
        self.assertEqual(P.check_integrity()['snapshot_files'], 168)

    def test_sparse_and_original_rows(self):
        for n in range(5, 9):
            rows = {'0': [1, 2, 3, 4], '2': [0, 1, 3, 4]}
            angles, equations = OLD.constraints(n, rows)
            pairs = list(combinations(range(n), 2))
            for dense, sparse in [(angles, A.base_angles(n)), (equations, A.equations(n, rows))]:
                self.assertEqual(len(dense), len(sparse))
                for (vector, constant), (mapping, rhs) in zip(dense, sparse):
                    self.assertEqual(constant, rhs)
                    self.assertEqual(vector, [mapping.get(pair, 0) for pair in pairs])

    def test_stored_contradiction_both_implementations(self):
        c = BAD
        self.assertTrue(OLD.check(c['n'], c['rows'], c['result']['certificate']))
        A.check_case(c)

    def test_stored_positive_vector_both_implementations(self):
        c = GOOD
        values = c['result']['chord_directions_over_pi']
        self.assertEqual(OLD.check_feasible(c['n'], c['rows'], values),
                         A.check_feasible(c['n'], c['rows'], values))

    def test_larger_cases_both_implementations(self):
        for name in ['angle_minconflicts_n20_exact.json', 'angle_minconflicts_n30.json']:
            c = P.load(A.SOURCE / name)['events'][0]
            self.assertTrue(OLD.check(c['n'], c['rows'], c['result']['certificate']))
            A.check_case(c)

    def test_negative_strict_multiplier(self):
        c = deepcopy(next(c for c in CAT['cases'] if c['result'].get('certificate', {}).get('angle_weights')))
        c['result']['certificate']['angle_weights'][0][1] = '-1'
        with self.assertRaises(ValueError):
            A.check_case(c)

    def test_wrong_constant(self):
        c = deepcopy(BAD)
        c['result']['certificate']['constant'] = '123456'
        with self.assertRaises(ValueError):
            A.check_case(c)

    def test_missing_strictness(self):
        c = deepcopy(next(c for c in CAT['cases'] if c['result'].get('certificate', {}).get('angle_weights')))
        c['result']['certificate']['angle_weights'] = []
        with self.assertRaises(ValueError):
            A.check_case(c)

    def test_floating_and_boolean_rationals(self):
        for value in (0.5, True):
            with self.assertRaises(ValueError):
                A.rational(value)

    def test_duplicate_weights(self):
        with self.assertRaises(ValueError):
            A.weights([[0, '1'], [0, '2']], 1)

    def test_bad_witness(self):
        with self.assertRaises(ValueError):
            A.normalize_rows(5, {'0': [0, 1, 2, 3]})

    def test_changed_positive_vector(self):
        c = deepcopy(GOOD)
        c['result']['chord_directions_over_pi'] = ['0'] * len(c['result']['chord_directions_over_pi'])
        with self.assertRaises(ValueError):
            A.check_case(c)

    def test_unverified_case_rejected(self):
        c = deepcopy(BAD)
        c['result']['classification'] = 'NUMERICAL_ONLY'
        with self.assertRaises(ValueError):
            A.check_case(c)

    def test_manifest_tampering(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'snapshots').mkdir()
            (root / 'snapshots/a.txt').write_text('changed')
            entry = next(iter(P.load(ROOT / 'provenance.json')['snapshot_files'].values()))
            (root / 'provenance.json').write_text(json.dumps({'schema': 1, 'snapshot_files': {'a.txt': entry}}))
            with self.assertRaises(ValueError):
                P.check_integrity(root)

    def test_nonzero_subprocess_rejected(self):
        with self.assertRaises(ValueError):
            P.run_command([sys.executable, '-c', 'raise SystemExit(7)'], ROOT)

    def test_unicode_subprocess(self):
        rec = P.run_command([sys.executable, '-c', "print('Erdős — ω')"], ROOT)
        self.assertIn('Erdős — ω', rec['stdout'])

    def test_snapshot_report_write_rejected(self):
        with self.assertRaises(ValueError):
            P.write_report(ROOT / 'snapshots/bad.json', {})

    def test_lf_report_serialization(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'report.json'
            P.write_report(path, {'value': 'ω'})
            self.assertNotIn(b'\r\n', path.read_bytes())
            self.assertEqual(P.load(path), {'value': 'ω'})

    def test_disabled_assertions_rejected(self):
        with self.assertRaises(ValueError):
            P.run_command([sys.executable, '-O', str(ROOT / 'publication.py')], ROOT)


if __name__ == '__main__':
    unittest.main()
