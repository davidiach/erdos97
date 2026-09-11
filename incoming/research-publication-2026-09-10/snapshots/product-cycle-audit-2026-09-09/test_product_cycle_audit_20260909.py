"""Defensive exact replay tests. Search/optimization is never imported."""
from pathlib import Path
from copy import deepcopy
from fractions import Fraction as F
import unittest,json,sys,subprocess
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'verify'))
from check_c3 import Geometry
from diamond_phase import check as phase_check,relation,TWO_DIAMOND_CERTIFICATE
from check_combined import verify as combined
from check_geometry import check as geometry
from check_six_cycle import check as six
from check_positive_relaxations import angle_check,metric_check
from quartic_field import K,S,MOD,INITIAL,root_interval,evaluate,validate_embedding
from q3_field import Q3

class ExactAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet=json.loads((ROOT/'reports/all_fixed_system_certificates.json').read_text())
        cls.angle=cls.packet['cases'][0]
        cls.phases=[c for c in cls.packet['cases']if c.get('diamond_phase_certificate')]
        cls.positive=json.loads((ROOT/'reports/angle_survivor_preflight.json').read_text())
        cls.metrics=json.loads((ROOT/'reports/full_metric_preflight.json').read_text())
    def test_all_fixed_certificates(self):
        r=combined(self.packet);self.assertEqual((r['unique_cases'],r['base_angle_certificates'],r['diamond_phase_certificates']),(333,330,3))
    def test_three_arrow_certificate(self):
        d=json.loads((ROOT/'reports/three_arrow_core_basic.json').read_text())
        for c in d['cases']:self.assertTrue(Geometry(c['rows']).certificate(c['certificate']))
    def test_missing_certificate_rejected(self):
        d=deepcopy(self.packet);d['cases'][0]['certificate']=None
        with self.assertRaises(ValueError):combined(d)
    def test_duplicate_system_rejected(self):
        d=deepcopy(self.packet);d['cases'].append(d['cases'][0])
        with self.assertRaises(ValueError):combined(d)
    def test_negative_strict_multiplier(self):
        c=deepcopy(self.angle['certificate']);c['strict'][0][1]*=-1
        with self.assertRaises(ValueError):Geometry(self.angle['rows']).certificate(c)
    def test_zero_strict_multiplier(self):
        c=deepcopy(self.angle['certificate']);c['strict'][0][1]=0
        with self.assertRaises(ValueError):Geometry(self.angle['rows']).certificate(c)
    def test_noninteger_multiplier(self):
        c=deepcopy(self.angle['certificate']);c['strict'][0][1]=1.0
        with self.assertRaises(ValueError):Geometry(self.angle['rows']).certificate(c)
    def test_coefficient_corruption(self):
        c=deepcopy(self.angle['certificate']);c['equal'][0][1]+=1
        with self.assertRaises(ValueError):Geometry(self.angle['rows']).certificate(c)
    def test_unforced_premise(self):
        c=deepcopy(self.angle['certificate']);c['equal'][0][0]=['right_angle',0,0,0]
        with self.assertRaises(ValueError):Geometry(self.angle['rows']).certificate(c)
    def test_no_strict_term(self):
        c=deepcopy(self.angle['certificate']);c['strict']=[]
        with self.assertRaises(ValueError):Geometry(self.angle['rows']).certificate(c)
    def test_bad_target(self):
        r=deepcopy(self.angle['rows']);r[0][0]=len(r)
        with self.assertRaises(ValueError):Geometry(r)
    def test_all_two_diamond_cancellations(self):
        for c in self.phases:self.assertTrue(phase_check(c['rows'],c['diamond_phase_certificate']))
    def test_wrong_phase_multiplier(self):
        c=deepcopy(TWO_DIAMOND_CERTIFICATE);c['equal'][0][1]=1
        with self.assertRaises(ValueError):phase_check(self.phases[0]['rows'],c)
    def test_wrong_phase_order(self):
        c=deepcopy(TWO_DIAMOND_CERTIFICATE);c['strict'][0][0]=['phase_gap',3,1]
        with self.assertRaises(ValueError):phase_check(self.phases[0]['rows'],c)
    def test_mismatched_diamond_gains(self):
        r=deepcopy(self.phases[0]['rows']);r[0][1]=2
        with self.assertRaises(ValueError):relation(r,0,1,2,6)
    def test_missing_diamond_arrow(self):
        r=deepcopy(self.phases[0]['rows']);r[0]=r[0][2:]
        with self.assertRaises(ValueError):relation(r,0,1,2,6)
    def test_coincident_diamond_orbits(self):
        with self.assertRaises(ValueError):relation(self.phases[0]['rows'],0,1,1,6)
    def test_one_diamond_can_have_positive_phase_gaps(self):
        rows=[[3,0,2,0],[],[1,1],[1,1]]
        v=relation(rows,0,2,3,1);x={0:F(0),1:F(11,20),2:F(3,4),3:F(4,5),'L':F(1)}
        self.assertEqual(sum(w*x[k]for k,w in v.items()),0)
        self.assertTrue(0<x[1]<x[2]<x[3]<x['L'])
    def test_exact_base_angle_controls(self):
        for c in self.positive:self.assertTrue(F(angle_check(c)['minimum_positive_value'])>0)
    def test_exact_metric_controls(self):
        for c in self.metrics:self.assertEqual(metric_check(c)['strict_Kalmanson_inequalities'],35100)
    def test_angle_vector_corruption(self):
        c=deepcopy(self.positive[0]);c['rational_angle_vector'][0]='999'
        with self.assertRaises(ValueError):angle_check(c)
    def test_metric_vector_corruption(self):
        c=deepcopy(self.metrics[0]);c['metric']['rational_vector'][0]='-1'
        with self.assertRaises(ValueError):metric_check(c)
    def fixture(self,name):return json.loads((ROOT/f'candidate_counterexamples/{name}.json').read_text())
    def test_exact_convex_controls(self):
        for name,count in [('c3_maximum_root_rich_neighborhood_21',399),('supplier_arc_positive_12',120),('convex_product_diamond_positive_12',120)]:
            r=geometry(self.fixture(name));self.assertEqual(r['global_support_checks'],count);self.assertFalse(r['all_rich'])
    def test_missing_control_premises(self):
        d=self.fixture('supplier_arc_positive_12');d['own_side_arrows']=[[],[],[],[]];d['own_side_source_rows']=[[],[],[],[]]
        with self.assertRaises(ValueError):geometry(d)
    def test_wrong_control_row_count(self):
        d=self.fixture('supplier_arc_positive_12');d['own_side_source_rows']=[]
        with self.assertRaises(ValueError):geometry(d)
    def test_exact_phase_filter_crosscheck(self):
        from check_phase_filter import verify
        r,certs=verify();self.assertEqual(r['phase_rejections'],200);self.assertEqual(len(certs['cases']),200)
    def test_reversed_global_order(self):
        d=self.fixture('supplier_arc_positive_12');d['cyclic_order'].reverse()
        with self.assertRaises(ValueError):geometry(d)
    def test_collided_vertices(self):
        d=self.fixture('supplier_arc_positive_12');d['coordinates'][1]=d['coordinates'][0]
        with self.assertRaises(ValueError):geometry(d)
    def test_bad_named_witness(self):
        d=self.fixture('c3_maximum_root_rich_neighborhood_21');d['own_side_arrows'][0][0][1]=1
        with self.assertRaises(ValueError):geometry(d)
    def test_unknown_control_kind(self):
        d=self.fixture('supplier_arc_positive_12');d['kind']='counterexample'
        with self.assertRaises(ValueError):geometry(d)
    def test_quartic_root_isolation(self):
        self.assertTrue(validate_embedding());a,b=root_interval(32)
        self.assertGreater(evaluate(MOD,a),0);self.assertLess(evaluate(MOD,b),0)
    def test_quartic_field_identities(self):
        self.assertEqual(7*S**4-24*S**3+44*S**2-42*S+13,0)
        self.assertEqual((S+1)/(S+1),1);self.assertTrue(K(F(1,2))<S<K(F(3,4)))
    def test_exact_six_cycle_and_nonconvexity(self):
        r=six(self.fixture('upper_six_cycle_exact_nonconvex_18'))
        self.assertEqual((r['hull_vertices'],r['strict_interior_points']),(6,12));self.assertEqual(r['all_radius_maximum_multiplicities'],[3]*18)
    def test_six_cycle_wrong_root(self):
        d=self.fixture('upper_six_cycle_exact_nonconvex_18');d['isolating_interval']=['1','2']
        with self.assertRaises(ValueError):six(d)
    def test_six_cycle_wrong_hull(self):
        d=self.fixture('upper_six_cycle_exact_nonconvex_18');d['hull_order'].reverse()
        with self.assertRaises(ValueError):six(d)
    def test_q3_exact_signs(self):
        lo=F(17320508075688772,10**16);hi=F(17320508075688774,10**16)
        self.assertTrue(lo*lo<3<hi*hi)
        for a in range(-8,9):
            for b in range(-8,9):
                q=Q3(a,b);l,u=sorted((a+b*lo,a+b*hi))
                expected=1 if l>0 else -1 if u<0 else 0
                self.assertEqual(q.sign(),expected)
    def test_incidence_only_no_diamond_control(self):
        from diamond_free_incidence import build
        d=build();self.assertEqual(d['states'],60);self.assertEqual(d['directed_diamonds'],0)
    def test_assertion_disabled_cli_rejected(self):
        p=subprocess.run([sys.executable,'-O',str(ROOT/'verify/check_combined.py'),str(ROOT/'reports/all_fixed_system_certificates.json')],capture_output=True,text=True)
        self.assertNotEqual(p.returncode,0)
if __name__=='__main__':unittest.main()
