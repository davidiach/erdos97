import unittest,json
from pathlib import Path
from fractions import Fraction as F
from itertools import product
import verify as v
class ParabolaTests(unittest.TestCase):
    def test_complete_saved_controls(self):
        self.assertEqual(json.loads(json.dumps(v.verify())),json.loads((Path(__file__).parent/'certificate.json').read_text()))
    def test_positive_control(self):
        c=v.control();self.assertEqual(c['max_multiplicities'],[4,1,1,1,1]);self.assertEqual(len(c['strict_support_signs']),15)
    def test_simple_row(self):
        r=v.row(F(1),F(0),F(0),list(map(F,[-4,-2,1,5])));self.assertEqual(r['center'],['9','12']);self.assertEqual(r['squared_radius'],'185')
    def test_zero_curvature_rejected(self):
        with self.assertRaises(ValueError):v.row(F(0),F(0),F(0),list(map(F,[-3,-1,1,3])))
    def test_repeated_parameters_rejected(self):
        with self.assertRaises(ValueError):v.row(F(1),F(0),F(0),list(map(F,[-1,-1,1,1])))
    def test_nonzero_parameter_sum_rejected(self):
        with self.assertRaises(ValueError):v.row(F(1),F(0),F(0),list(map(F,[-3,-1,1,4])))
    def test_float_rejected(self):
        with self.assertRaises(TypeError):v.row(1.0,F(0),F(0),list(map(F,[-3,-1,1,3])))
    def test_circle_fit_rejects_collinearity(self):
        with self.assertRaises(ValueError):v.circumcenter([(F(0),F(0)),(F(1),F(0)),(F(2),F(0))])
    def test_two_step_zero_drift_exactly_opposite_curvatures(self):
        for a,b in product([-3,-2,-1,1,2,3],repeat=2):
            self.assertEqual(F(1,2*a)+F(1,2*b)==0,a==-b)
    def test_zero_drift_three_cycle_is_allowed_arithmetically(self):
        self.assertEqual(sum(F(1,2*a)for a in [F(1),F(1),F(-1,2)]),0)
        # The level-set cardinality step, not nonzero drift, excludes this case.
    def test_extremal_average_forces_all_terms_equal(self):
        for values in product([-2,-1,0,1,2],repeat=4):
            if abs(sum(values))==8:self.assertEqual(len(set(values)),1)
    def test_square_level_has_at_most_two_grid_parameters(self):
        for level in range(50):self.assertLessEqual(sum(t*t==level for t in range(-10,11)),2)
if __name__=='__main__':unittest.main()
