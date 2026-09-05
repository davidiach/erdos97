"""Regression tests for exact proofs and controls; not external geometry review."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from audit_expanded_model import ExpandedEncoding
from core import AngleModel, MetricModel, OrbitPairs, all_cases, decode_case, verify_certificate
from check_common_suppliers import (build_report, check_artifact, controls, copair_obstructions,
                                    enumerate_radial_graphs, graph_well_formed, shortcut_obstructions)

ROOT = Path(__file__).resolve().parent


class CommonSupplierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifact = json.loads((ROOT / 'certificates.json').read_text())

    def test_complete_exact_certificate_coverage(self):
        result = check_artifact(self.artifact)
        self.assertEqual(result['exact_cases'], 486)
        self.assertEqual(result['certificate_types'], {'angle': 480, 'metric': 6})
        self.assertEqual(result['maximum_nonzero_terms'], 21)
        self.assertEqual(result['maximum_integer_multiplier'], 210)

    def test_missing_case_is_rejected(self):
        altered = deepcopy(self.artifact)
        altered['records'].pop()
        with self.assertRaisesRegex(ValueError, 'coverage'):
            check_artifact(altered)

    def test_changed_multiplier_is_rejected(self):
        altered = deepcopy(self.artifact)
        altered['records'][0][4][0][1] += 1
        with self.assertRaisesRegex(ValueError, 'residual'):
            check_artifact(altered)

    def test_strictness_is_required(self):
        record = self.artifact['records'][0]
        A, E = AngleModel().build(*decode_case(tuple(record[:3])))
        with self.assertRaisesRegex(ValueError, 'no strict'):
            verify_certificate(A, E, [], [])
        with self.assertRaisesRegex(ValueError, 'sign'):
            verify_certificate(A, E, [[record[4][0][0], -1]], [])

    def test_indices_are_not_silently_trusted(self):
        with self.assertRaisesRegex(ValueError, 'row index'):
            verify_certificate([(1,)], [], [[1, 1]], [])
        with self.assertRaisesRegex(ValueError, 'row index'):
            verify_certificate([(0,)], [], [[0, 1], [0, 1]], [])

    def test_models_and_domain(self):
        self.assertEqual(len(all_cases()), 486)
        self.assertEqual(OrbitPairs(4).count, 22)
        self.assertEqual(AngleModel(4).dimension, 23)
        A, E = MetricModel().build(*decode_case((0, 39, 1)))
        self.assertTrue(A)
        self.assertEqual(E, [])
        with self.assertRaisesRegex(ValueError, 'invalid case'):
            decode_case((2, 0, 0))

    def test_six_orbit_frontier_and_obstructions(self):
        graphs, _ = enumerate_radial_graphs(6)
        self.assertEqual(graphs, [[24, 33, 33, 6, 6, 24], [40, 33, 33, 6, 6, 24],
                                 [48, 33, 33, 6, 6, 24], [48, 48, 3, 3, 12, 12]])
        self.assertTrue(all(copair_obstructions(g) for g in graphs))

    def test_smaller_frontiers(self):
        for n in (3, 4, 5):
            self.assertEqual(enumerate_radial_graphs(n)[0], [])

    def test_shortcut_rejects_only_correct_cycle_order(self):
        self.assertEqual(shortcut_obstructions([2, 4, 1]),
                         [{'downward_edge': [2, 0], 'increasing_path': [0, 1, 2]}])
        self.assertEqual(shortcut_obstructions([4, 1, 2]), [])

    def test_seven_orbit_graph_is_not_overclaimed(self):
        rows = [6, 80, 66, 65, 12, 10, 48]
        self.assertTrue(graph_well_formed(rows))
        self.assertEqual(shortcut_obstructions(rows), [])
        self.assertEqual(copair_obstructions(rows), [])
        self.assertEqual(len(set(rows)), 7)

    def test_exact_positive_geometry_controls(self):
        result = controls()
        rectangle = result['interlacing_common_supplier_rectangle']
        self.assertEqual(rectangle['supporting_edge_checks'], 120)
        self.assertEqual(rectangle['squared_radii'], ['1', '247/148', '91/37', '13/7'])
        self.assertFalse(rectangle['is_erdos97_counterexample'])
        cycle = result['irrational_three_orbit_cycle_is_permitted']
        self.assertEqual(cycle['maximum_multiplicity_by_vertex'], [3] * 9)
        self.assertEqual(len(cycle['two_cos_double_angle_rational_nonintegers']), 3)

    def test_expanded_encoding_reconstructs_representative_cases(self):
        expanded = ExpandedEncoding()
        self.assertEqual(len(expanded.pairs), 66)
        for case in [(0, 0, 0), (0, 39, 1), (1, 7, 2), (1, 80, 2)]:
            arrows, greater = decode_case(case)
            self.assertEqual(expanded.angles(arrows, greater), AngleModel().build(arrows, greater))
            self.assertEqual(expanded.metric(arrows, greater), MetricModel().build(arrows, greater))

    def test_stored_report_replays(self):
        self.assertEqual(json.loads((ROOT / 'report.json').read_text()), build_report())


if __name__ == '__main__':
    unittest.main()
