"""Exact positive controls, independent replay, and certificate tampering tests."""
import copy
import json
import unittest
from pathlib import Path
from quadratic import Q,F,base9,cycle9,repair18,norm,dist,rot,turn
from extensions import E
import verify
import oracle

ROOT=Path(__file__).resolve().parent
CC=json.loads((ROOT/'data/base9_circumcenters.json').read_text())
PAIRS=json.loads((ROOT/'data/prescribed_circle_pairs.json').read_text())

class ExactResearchTests(unittest.TestCase):
    def test_01_quadratic_operations(self):
        a=Q(F(3,7),F(-2,11));b=Q(F(5,13),F(1,17))
        self.assertEqual((a+b)-b,a);self.assertEqual(a*b,b*a);self.assertEqual(a/b*b,a)
    def test_02_quadratic_signs(self):
        for q,s in [(Q(27,-1),1),(Q(26,-1),-1),(Q(-27,1),-1),(Q(-26,1),1),(Q(0,1),1),(Q(0,-1),-1),(Q(0),0)]:
            self.assertEqual(q.sign(),s)
    def test_03_fraction_hash_contract(self):
        self.assertEqual(hash(Q(F(2,3))),hash(F(2,3)))
        self.assertEqual(len({Q(1),1}),1)
    def test_04_float_rejection(self):
        for args in [(0.1,),('1',0.1)]:
            with self.assertRaises(TypeError):Q(*args)
    def test_05_zero_division(self):
        with self.assertRaises(ZeroDivisionError):Q(1)/Q(0)
    def test_06_rotations(self):
        for p in base9():
            self.assertEqual(rot(rot(rot(p))),p);self.assertEqual(norm(rot(p)),norm(p))
    def test_07_extension_signs(self):
        self.assertEqual(E(1,-1,2).sign(),-1);self.assertEqual(E(2,-1,2).sign(),1)
        self.assertEqual(E(2,-1,4).sign(),0)
    def test_08_extension_zero_is_semantic(self):
        self.assertEqual(E(Q(0,1),-1,721),0)
        self.assertFalse(E(Q(0,1),-1,721))
    def test_09_negative_radicand(self):
        with self.assertRaises(ValueError):E(0,1,-1)
    def test_10_distinct_extensions_rejected(self):
        with self.assertRaises(ValueError):E(0,1,2)+E(0,1,3)
    def test_11_base_supports(self):
        self.assertEqual(verify.check_strict(base9(),[4,2,6,5,0,7,3,1,8]),63)
    def test_12_repair_exact_census(self):
        r=verify.check_repair();self.assertEqual(r['maximum_multiplicities'],[4]*9+[2]*9)
    def test_13_middle_cycle(self):
        r=verify.check_middle_cycle();self.assertEqual(r['closer_counts_at_radius_1'],[2]*9)
    def test_14_all_circumcenters(self):
        self.assertEqual(verify.check_circumcenters(CC)['distinct_centers'],64)
    def test_15_all_circle_pairs(self):
        self.assertEqual(verify.check_pairs(PAIRS)['real_intersection_branches'],30)
    def test_16_independent_replay(self):
        self.assertEqual(oracle.run()['status'],'passed')
    def test_17_report_matches(self):
        self.assertEqual(json.loads((ROOT/'data/verification.json').read_text()),verify.run())
    def test_18_missing_triple(self):
        c=copy.deepcopy(CC);c['triples'].pop()
        with self.assertRaises(AssertionError):verify.check_circumcenters(c)
    def test_19_duplicate_triple(self):
        c=copy.deepcopy(CC);c['triples'][1]=copy.deepcopy(c['triples'][0])
        with self.assertRaises(AssertionError):verify.check_circumcenters(c)
    def test_20_changed_center_coordinate(self):
        c=copy.deepcopy(CC);c['centers'][0]['point'][0][0]='12345'
        with self.assertRaises(AssertionError):verify.check_circumcenters(c)
    def test_21_reversed_containment_triangle(self):
        c=copy.deepcopy(CC);e=next(e for e in c['centers'] if 'obstruction'in e)
        e['obstruction']['triangle'][0],e['obstruction']['triangle'][1]=e['obstruction']['triangle'][1],e['obstruction']['triangle'][0]
        with self.assertRaises(AssertionError):verify.check_circumcenters(c)
    def test_22_false_coincidence(self):
        c=copy.deepcopy(CC);e=next(e for e in c['centers'] if 'obstruction'in e)
        del e['obstruction'];e['coincides_with']=0
        with self.assertRaises(AssertionError):verify.check_circumcenters(c)
    def test_23_missing_intersection_branch(self):
        c=copy.deepcopy(PAIRS);c['pairs'][0]['roots'].pop()
        with self.assertRaises(AssertionError):verify.check_pairs(c)
    def test_24_wrong_intersection_branch(self):
        c=copy.deepcopy(PAIRS);c['pairs'][0]['roots'][0]['branch']=1
        with self.assertRaises(AssertionError):verify.check_pairs(c)
    def test_25_wrong_radicand(self):
        c=copy.deepcopy(PAIRS);c['pairs'][0]['radicand']=['123','0']
        with self.assertRaises(AssertionError):verify.check_pairs(c)
    def test_26_wrong_radius(self):
        c=copy.deepcopy(PAIRS);c['radii_squared'][0]=['4','0']
        with self.assertRaises(AssertionError):verify.check_pairs(c)
    def test_27_bad_boundary_order(self):
        order=[4,2,6,5,0,7,3,1,8];order[1],order[2]=order[2],order[1]
        with self.assertRaises(AssertionError):verify.check_strict(base9(),order)
    def test_28_float_certificate(self):
        c=copy.deepcopy(CC);c['points'][0][0][0]=1.0
        with self.assertRaises(ValueError):verify.check_circumcenters(c)
    def test_29_wrong_base_sha(self):
        c=copy.deepcopy(CC);c['base_sha']='0'*40
        with self.assertRaises(AssertionError):verify.check_circumcenters(c)
    def test_30_oracle_radical_reductions(self):
        R=oracle.ring(F(4));self.assertEqual(R(2,0,-1).sign(),0)
        R=oracle.ring(F(721));self.assertEqual(R(0,1,-1).sign(),0)
        R=oracle.ring(F(2));self.assertEqual(R(1,0,-1).sign(),-1)
    def test_31_outside_circumcenter_positive_control(self):
        # The center outside its witness triangle can be a legitimate new hull vertex.
        # This prevents mistaking the seed-specific theorem for a general fact.
        P=[(Q(F(1,2)),Q(F(-1,2))),(Q(1),Q(0)),(Q(F(1,2)),Q(F(1,2))),(Q(0),Q(0))]
        self.assertEqual(verify.check_strict(P,[3,0,1,2]),8)
        self.assertTrue(all(dist(P[3],q)==1 for q in P[:3]))

if __name__=='__main__':unittest.main(verbosity=2)
