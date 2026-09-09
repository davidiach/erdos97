"""Defensive tests of the exact computations; not a formalization of proof.md."""
import copy,json,unittest
from pathlib import Path
from fractions import Fraction as F
import exact as E
import verify as V
ROOT=Path(__file__).resolve().parent

class PolynomialKernel(unittest.TestCase):
    def test_arithmetic(self):
        a=E.poly([1,2,3]);b=E.poly([-2,0,1])
        self.assertEqual(E.divrem(E.mul(a,b),a),(b,E.ZERO))
    def test_sturm_endpoint_inclusion(self):
        p=E.poly([-1,0,1]);self.assertEqual(E.roots_closed(p,F(-1),F(1)),2)
        self.assertEqual(E.roots_closed(p,F(-1),F(0)),1)
    def test_distinct_not_multiplicity(self):
        self.assertEqual(E.roots_closed(E.poly([0,0,0,0,1]),F(-1),F(1)),1)
    def test_singleton_interval(self):
        self.assertEqual(E.roots_closed(E.poly([-1,1]),F(1),F(1)),1)
        self.assertEqual(E.roots_closed(E.poly([-1,1]),F(0),F(0)),0)
    def test_gcd(self):
        self.assertEqual(E.gcd(E.poly([-1,0,1]),E.poly([-1,1])),E.poly([-1,1]))
    def test_algebraic_sign(self):
        f=E.poly([-2,0,1]);self.assertEqual(E.sign_at_root(E.poly([-1,1]),f,F(1),F(2)),1)
        self.assertEqual(E.sign_at_root(f,f,F(1),F(2)),0)
    def test_multiple_root_isolation_rejected(self):
        with self.assertRaises(ValueError):E.sign_at_root(E.X,E.poly([-2,0,1]),F(-2),F(2))
    def test_reversed_interval(self):
        with self.assertRaises(ValueError):E.roots_closed(E.X,F(1),F(-1))
    def test_zero_polynomial_rejected(self):
        with self.assertRaises(ValueError):E.roots_closed(E.ZERO,F(0),F(1))
    def test_float_coefficient_rejected(self):
        with self.assertRaises(TypeError):E.poly([1,0.1])
    def test_constant_polynomial(self):
        self.assertEqual(E.roots_closed(E.poly([2]),F(-5),F(8)),0)

class LensControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.inputs=json.loads((ROOT/'data/controls.json').read_text())['controls']
    def test_two_controls(self):
        for d in self.inputs:
            with self.subTest(d['name']):
                r=V.check_control(d);self.assertEqual(r['max_multiplicities'],[4,1,1,1,1]);self.assertEqual(r['support_count'],15)
    def test_wrong_isolation_rejected(self):
        d=copy.deepcopy(self.inputs[0]);d['lower_root_interval']=['5','6']
        with self.assertRaises(ValueError):V.check_control(d)
    def test_reversed_orientation_rejected(self):
        d=copy.deepcopy(self.inputs[0]);d['order'].reverse()
        with self.assertRaises(ValueError):V.check_control(d)
    def test_duplicate_formal_witness_rejected(self):
        d=copy.deepcopy(self.inputs[0]);d['upper_parameters'][1]=d['upper_parameters'][0]
        with self.assertRaises(ValueError):V.check_control(d)
    def test_float_input_rejected(self):
        d=copy.deepcopy(self.inputs[0]);d['upper_parameters'][0]=-.85
        with self.assertRaises(ValueError):V.check_control(d)
    def test_false_selector_rejected(self):
        d=copy.deepcopy(self.inputs[0]);d['invalid_selector']='maximum'
        with self.assertRaises(ValueError):V.check_control(d)
    def test_invalid_order_rejected(self):
        d=copy.deepcopy(self.inputs[0]);d['order']=[0,1,2,3,3]
        with self.assertRaises(ValueError):V.check_control(d)

class LensRegression(unittest.TestCase):
    def test_complete_report_replay(self):
        self.assertEqual(V.canonical(V.run()),(ROOT/'data/verification.json').read_text())
    def test_exact_switch_height(self):
        for mode in ('minimum','maximum'):
            for r in map(F,['1/16','1','3','7/2']):
                self.assertLessEqual(V.count_level(F(3,2),F(3,4),F(1,2),r,mode)['distinct_witness_count'],2 if mode=='maximum'else 3)
    def test_tangent_root_not_four_points(self):
        r=V.count_level(F(1,2),F(1,2),F(0),F(1,4),'maximum')
        self.assertEqual(r['distinct_witness_count'],1)
    def test_common_junction_deduplication(self):
        r=V.count_level(F(2),F(1),F(0),F(2),'minimum')
        self.assertEqual(r['distinct_witness_count'],2);self.assertEqual(r['common_endpoint_duplicates'],2)
    def test_deep_three_witnesses_attained(self):
        r=V.count_level(F(7907,3800),F(1019,1000),F(3,5),F(44468521,14440000),'minimum')
        self.assertEqual((r['lower_roots'],r['upper_roots'],r['distinct_witness_count']),(1,2,3))
    def test_wrong_regime_rejected(self):
        with self.assertRaises(ValueError):V.count_level(F(2),F(1),F(1,2),F(1),'maximum')
    def test_zero_radius_rejected(self):
        with self.assertRaises(ValueError):V.count_level(F(2),F(1),F(1,2),F(0),'minimum')
    def test_outside_lens_rejected(self):
        with self.assertRaises(ValueError):V.count_level(F(2),F(2),F(1,2),F(1),'minimum')
    def test_claim_scope_flags(self):
        d=json.loads((ROOT/'data/verification.json').read_text())
        self.assertTrue(d['not_an_unrestricted_solution']);self.assertFalse(d['formalized']);self.assertFalse(d['independent_external_review'])

class SeparateOracle(unittest.TestCase):
    def test_universal_symbolic_identities(self):
        import oracle
        self.assertEqual(oracle.identity_checks(),15)
    def test_separate_controls(self):
        import oracle
        inp=json.loads((ROOT/'data/controls.json').read_text())['controls']
        ref=json.loads((ROOT/'data/verification.json').read_text())['controls']
        for d,e in zip(inp,ref):self.assertEqual(oracle.control(d,e)['support_signs'],15)
    def test_altered_root_count_rejected(self):
        import oracle
        d=json.loads((ROOT/'data/verification.json').read_text())['grid'][-1]
        d['distinct_witness_count']=4
        with self.assertRaises(ValueError):oracle.grid(d)
    def test_separate_endpoint_convention(self):
        import oracle
        self.assertEqual(oracle.roots(oracle.x**2-1,F(-1),F(1)),2)

class TwoFreeScope(unittest.TestCase):
    def test_probe_is_inconclusive(self):
        d=json.loads((ROOT/'data/cap_pair_probe.json').read_text())
        self.assertEqual(d['cases'],4500);self.assertTrue(d['not_a_geometric_candidate'])
        self.assertEqual(sum(c['survived']for c in d['counts'].values()),2676)
        self.assertEqual(sum(c['rejected']for c in d['counts'].values()),1824)
    def test_archive_hash(self):
        import hashlib,cap_pair_probe
        self.assertEqual(hashlib.sha256((ROOT/'inputs/prior_internal_support.zip').read_bytes()).hexdigest(),cap_pair_probe.EXPECTED)

class ConstructiveSelector(unittest.TestCase):
    def test_rational_samples(self):
        from select_good import select_good_vertex
        for b in map(F,['1/2','3/4','1','2','3']):
            H=2*b*b
            ts=[b*F(k,8)for k in range(-8,9)]
            points=list(dict.fromkeys((t,y)for t in ts for y in (t*t,H-t*t)))
            r=select_good_vertex(H,points)
            self.assertLessEqual(r['maximum_multiplicity'],r['proved_bound'])
    def test_selector_rejects_inexact_input(self):
        from select_good import select_good_vertex
        with self.assertRaises(TypeError):select_good_vertex(2,[[0.0,0]])
    def test_selector_rejects_nonboundary(self):
        from select_good import select_good_vertex
        with self.assertRaises(ValueError):select_good_vertex(2,[[0,1]])
    def test_single_vertex(self):
        from select_good import select_good_vertex
        self.assertEqual(select_good_vertex(2,[[0,0]])['maximum_multiplicity'],0)

if __name__=='__main__':unittest.main(verbosity=2)
