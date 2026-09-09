import unittest,json,tempfile
from pathlib import Path
from fractions import Fraction as F
from itertools import combinations
import circle_star_metric as s
import circle_star_oracle as o
import turn_control as tc
ROOT=Path(__file__).resolve().parent

class StarExtension(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.D,cls.r=s.build()
        cls.t=list(map(F,json.loads((ROOT/'evidence/turn_values.json').read_text())['normalized_turns']))
    def test_saved_star_certificate(self):
        self.assertEqual(json.loads(json.dumps(self.r)),json.loads((ROOT/'evidence/circle_star_metric.json').read_text()))
    def test_all_rich_and_no_other_ties(self):
        self.assertEqual(min(map(len,self.r['full_unit_fibers'])),4)
        for i,row in enumerate(self.D):
            other=[d for j,d in enumerate(row)if j!=i and d!=1]
            self.assertEqual(len(other),len(set(other)))
    def test_all_circle_coordinates_unit(self):
        for j in range(74):
            x,y=s.point(j);self.assertEqual(x*x+y*y,1)
    def test_two_representations_of_circle(self):
        for j in range(74):self.assertEqual(s.point(j),o.loc(j))
        for i,j in combinations(range(74),2):
            a,b=o.half(i);c,d=o.half(j);self.assertEqual(s.chord(i,j),2*(a*d-b*c))
    def test_strict_mixed_margins(self):
        self.assertGreater(min(map(F,self.r['exact_margin_bounds'].values())),0)
    def test_star_counts(self):
        self.assertEqual(self.r['local_star_squared_distance_checks'],2800)
        self.assertEqual(self.r['local_star_strict_supporting_signs'],4678)
        self.assertEqual(self.r['witness_quad_ptolemy_equalities_checked'],3252)
    def test_nonplanar_but_each_circle_quad_planar(self):
        self.assertGreater(s.gram(self.D,[0,1,74,75]),0)
        self.assertEqual(s.gram(self.D,[0,1,2,3]),0)
        self.assertEqual(s.gram(self.D,[74,75,76,77]),0)
    def test_local_star_gram_zero(self):
        for i,ws in enumerate(self.r['full_unit_fibers']):
            self.assertEqual(s.gram(self.D,[i]+ws[:3]),0)
    def test_separate_matrix_star_oracle(self):
        r=o.check();self.assertEqual(r['status'],'passed')
        self.assertEqual(r['strict_local_ordered_triple_orientations'],5148)
        self.assertFalse(r['global_planar_realization'])
    def test_exact_turns_both_controls(self):
        r=tc.run()
        self.assertEqual(r['strict_ptolemy_metric']['strict_pair_turn_inequalities_checked'],8686)
        self.assertEqual(r['locally_planar_star_metric']['strict_pair_turn_inequalities_checked'],4032)
        self.assertEqual(r['locally_planar_star_metric']['minimum_forced_support_sum'],'84/83')
    def test_turn_total_tampering_rejected(self):
        t=self.t[:];t[0]+=F(1,83)
        with self.assertRaises(ValueError):tc.check_matrix(ROOT/'evidence/circle_star_matrix.txt',t)
    def test_nonpositive_turn_rejected(self):
        t=self.t[:];t[1]+=t[0];t[0]=F(0)
        with self.assertRaises(ValueError):tc.check_matrix(ROOT/'evidence/circle_star_matrix.txt',t)
    def test_uniform_turn_does_not_pass(self):
        with self.assertRaises(ValueError):tc.check_matrix(ROOT/'evidence/circle_star_matrix.txt',[F(4,138)]*138)
    def test_turns_are_not_geometrically_compatible(self):
        self.assertEqual(self.t[1],F(1,83))
        # pi>3; neighboring circle arc forces exterior turn < 1/250.
        self.assertGreater(3*self.t[1]/2,F(1,250))
    def test_three_block_size_reduction_through_16(self):
        for n in range(5,17):
            for m in range(6,n):
                self.assertLess((n-m)*(m+3),16*m)
    def test_size_reduction_not_overextended(self):
        # This necessary scalar bound allows six sources and eleven targets.
        self.assertGreaterEqual((17-6)*(6+3),16*6)
    def test_circle_ptolemy_not_all_strict(self):
        D=self.D;a,b,c,d=0,1,2,3
        self.assertEqual(D[a][c]*D[b][d],D[a][b]*D[c][d]+D[a][d]*D[b][c])
    def test_general_index_tie_bound(self):
        for n in (4,10,20,50,138):
            L=10*n*n
            self.assertLess(F(2*n**3,L*L),1)

if __name__=='__main__':unittest.main()
