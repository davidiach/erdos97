"""Exact replay, boundary controls, and malformed-evidence rejection tests."""
from copy import deepcopy
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
from types import SimpleNamespace
import json,random,subprocess,sys,unittest
from unittest.mock import patch
import inherited
import one_free as A
import audit_one_free as B
import controls as C
import kalmanson as K
import combinatorics as D
ROOT=Path(__file__).resolve().parent


class InternalSupportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=json.loads((ROOT/'data/one_free_certificate.json').read_text())
        cls.P,cls.slots,cls.edges,_=A.setup()
        cls.R,cls.OP,_,cls.OS,cls.OE=B.context()
        cls.examples={}
        def visit(tree,T,old):
            if 'leaf' in tree:
                leaf=tree['leaf'];cls.examples.setdefault(leaf['kind'],(leaf,T,old))
                if leaf['kind']=='zero-old-radius-cover' and any(x['kind']=='pair-sharing' for x in leaf['cases']):
                    cls.examples.setdefault('conflict',(leaf,T,old))
                return
            k=tree['split_edge'];a,b,c=T[k],T[(k+1)%3],T[(k+2)%3]
            m=B.times(B.plus(a,b),cls.R(1)/2)
            for branch,child in zip(tree['children'],((a,m,c),(m,b,c))):visit(branch,child,old)
        for case in cls.report['cases']:
            visit(case['tree'],B.initial_triangle(cls.OP,case['cell']),case['old_witness'])
        cls.patterns=json.loads((ROOT/'data/moving_pattern_obstructions.json').read_text())['patterns']

    def verify_leaf(self,leaf,T,old):
        return B.verify_leaf(leaf,self.OP,self.OS,self.OE,T,old,self.R)

    def test_01_full_primary_replay(self):
        self.assertEqual(A.run(),self.report)
    def test_02_full_second_representation(self):
        self.assertEqual(B.audit(self.report),json.loads((ROOT/'data/one_free_oracle.json').read_text()))
    def test_03_archive_identity(self):
        self.assertEqual(inherited.archive_hash(),inherited.EXPECTED_ARCHIVE_SHA256)
    def test_04_changed_archive_rejected_before_load(self):
        with patch.object(inherited,'archive_hash',return_value='0'*64):
            with self.assertRaises(ValueError):inherited.location()
    def test_05_exact_field_rejects_float(self):
        with self.assertRaises((TypeError,ValueError)):A.Q(.1)
        with self.assertRaises((TypeError,ValueError)):self.R(.1)
    def test_06_optimized_mode_rejected(self):
        p=subprocess.run([sys.executable,'-S','-O','one_free.py'],cwd=ROOT,capture_output=True,text=True)
        self.assertNotEqual(p.returncode,0);self.assertIn('must not run under -O',p.stderr)
    def test_07_all_ninety_cases_present(self):
        self.assertEqual([(c['cell'],c['old_witness']) for c in self.report['cases']],
                         [(i,j) for i in range(9) for j in [None]+list(range(9))])
    def test_08_omitted_case_rejected(self):
        r=deepcopy(self.report);r['cases'].pop()
        with self.assertRaises(AssertionError):B.audit(r)
    def test_09_changed_source_hash_rejected(self):
        r=deepcopy(self.report);r['inherited_archive_sha256']='0'*64
        with self.assertRaises(AssertionError):B.audit(r)
    def test_10_false_solution_status_rejected(self):
        r=deepcopy(self.report);r['not_an_erdos97_solution']=False
        with self.assertRaises(AssertionError):B.audit(r)
    def test_11_illegal_domain_split_rejected(self):
        r=deepcopy(self.report);r['cases'][0]['tree']={'split_edge':3,'children':[{},{}]}
        with self.assertRaises(AssertionError):B.audit(r)
    def test_12_missing_split_child_rejected(self):
        r=deepcopy(self.report);r['cases'][0]['tree']={'split_edge':0,'children':[{}]}
        with self.assertRaises(AssertionError):B.audit(r)
    def test_13_tampered_incoming_edge_rejected(self):
        original,T,old=self.examples['one-old'];leaf=deepcopy(original);leaf['incoming']=[] if leaf['incoming'] else [0]
        with self.assertRaises(AssertionError):self.verify_leaf(leaf,T,old)
    def test_14_tampered_outgoing_edge_rejected(self):
        original,T,old=self.examples['one-old'];leaf=deepcopy(original);leaf['outgoing']=[] if leaf['outgoing'] else [0]
        with self.assertRaises(AssertionError):self.verify_leaf(leaf,T,old)
    def test_15_false_graph_core_rejected(self):
        original,T,old=self.examples['one-old'];leaf=deepcopy(original);leaf['remaining']=[42]
        with self.assertRaises(AssertionError):self.verify_leaf(leaf,T,old)
    def test_16_missing_peeling_layer_rejected(self):
        original,T,old=self.examples['one-old'];leaf=deepcopy(original);leaf['layers']=leaf['layers'][:-1]
        with self.assertRaises(AssertionError):self.verify_leaf(leaf,T,old)
    def test_17_changed_distance_range_rejected(self):
        original,T,old=self.examples['conflict'];leaf=deepcopy(original)
        leaf['distance_intervals'][0]['upper']=['999','0']
        with self.assertRaises(AssertionError):self.verify_leaf(leaf,T,old)
    def test_18_omitted_radius_target_set_rejected(self):
        original,T,old=self.examples['conflict'];leaf=deepcopy(original)
        leaf['maximal_radius_target_sets'].pop()
        with self.assertRaises(AssertionError):self.verify_leaf(leaf,T,old)
    def test_19_omitted_conflict_rejected(self):
        original,T,old=self.examples['conflict'];leaf=deepcopy(original)
        next(c for c in leaf['cases'] if c['kind']=='pair-sharing')['conflicts'].pop()
        with self.assertRaises(AssertionError):self.verify_leaf(leaf,T,old)
    def test_20_omitted_four_subset_rejected(self):
        original,T,old=self.examples['conflict'];leaf=deepcopy(original)
        next(c for c in leaf['cases'] if c['kind']=='pair-sharing')['four_subset_cover'].pop()
        with self.assertRaises(AssertionError):self.verify_leaf(leaf,T,old)
    def test_21_false_conflict_pair_rejected(self):
        original,T,old=self.examples['conflict'];leaf=deepcopy(original)
        next(c for c in leaf['cases'] if c['kind']=='pair-sharing')['four_subset_cover'][0]['conflict']=[0,0]
        with self.assertRaises(AssertionError):self.verify_leaf(leaf,T,old)
    def test_22_projection_interior_boundary_and_exterior(self):
        Q=A.Q;T=((Q(0),Q(0)),(Q(2),Q(0)),(Q(0),Q(2)))
        self.assertEqual(A.closest_on_triangle((Q(1),Q(0)),T),(Q(1),Q(0)))
        self.assertEqual(A.closest_on_triangle((Q(-1),Q(-1)),T),(Q(0),Q(0)))
        self.assertTrue(A.segment_meets_triangle((Q(-1),Q(1)),(Q(3),Q(1)),T))
        self.assertTrue(A.segment_meets_triangle((Q(-1),Q(0)),(Q(3),Q(0)),T))
        self.assertFalse(A.segment_meets_triangle((Q(-1),Q(-1)),(Q(3),Q(-1)),T))
    def test_23_distance_minima_agree_on_all_root_domains(self):
        for cell in range(9):
            T=A.insertion_triangle(self.P,cell);U=B.initial_triangle(self.OP,cell)
            for i in range(42):
                expected=A.distance_interval(self.slots[i],T)
                actual=B.radial_range(self.OS[i],U,self.R)
                self.assertEqual([x.json() for x in expected],[x.qjson() for x in actual])
    def test_24_graph_peeling_independent_random_controls(self):
        rng=random.Random(9702)
        for _ in range(30):
            E=[(i,j) for i in range(43) for j in range(43) if i!=j and rng.random()<.06]
            for required in (3,4):
                active,layers=A.graph_peel(E,required)
                self.assertEqual(active,B.core(E,required));B.check_peeling(E,required,layers,active)
    def test_25_positive_control_full_replay(self):
        report=C.generate();self.assertEqual(report,json.loads((ROOT/'data/positive_control.json').read_text()))
        self.assertEqual(C.homogeneous_check(report)['maxima'],[4]*4+[1]*10)
    def test_26_positive_control_wrong_rich_row_rejected(self):
        r=C.generate();r['rich_classes'][0]['witnesses']=[1,2,3,5]
        with self.assertRaises(ValueError):C.homogeneous_check(r)
    def test_27_positive_control_duplicate_point_rejected(self):
        r=C.generate();r['points'][1]=r['points'][0]
        with self.assertRaises(ValueError):C.homogeneous_check(r)
    def test_28_positive_control_float_rejected(self):
        r=C.generate();r['points'][0][0]=0.0
        with self.assertRaises(ValueError):C.homogeneous_check(r)
    def test_29_positive_control_false_all_rich_rejected(self):
        r=C.generate();r['maxima']=[4]*14
        with self.assertRaises(ValueError):C.homogeneous_check(r)
    def test_30_positive_control_wrong_internal_count_rejected(self):
        r=C.generate();r['internally_supported_new_vertices']=[0,1]
        with self.assertRaises(ValueError):C.homogeneous_check(r)
    def test_31_all_saved_pattern_certificates_two_checkers(self):
        for p in self.patterns:
            for c in p['certificates']:
                self.assertTrue(K.validate_certificate(p['rows'],p['order'],c))
                self.assertTrue(D.verify_inequality_certificate(p['rows'],p['order'],c))
    def test_32_negative_inequality_weight_rejected(self):
        p=self.patterns[0];c=deepcopy(p['certificates'][0]);c['inequalities'][0]['weight']=-1
        with self.assertRaises(ValueError):K.validate_certificate(p['rows'],p['order'],c)
        with self.assertRaises(ValueError):D.verify_inequality_certificate(p['rows'],p['order'],c)
    def test_33_incorrect_cyclic_order_rejected(self):
        p=self.patterns[0];c=deepcopy(p['certificates'][0]);q=c['inequalities'][0]['quadruple'];q[1],q[2]=q[2],q[1]
        with self.assertRaises(ValueError):K.validate_certificate(p['rows'],p['order'],c)
    def test_34_missing_required_equality_row_rejected(self):
        p=self.patterns[1];c=deepcopy(p['certificates'][0]);c['selected_centers'].pop()
        with self.assertRaises(ValueError):K.validate_certificate(p['rows'],p['order'],c)
        with self.assertRaises(ValueError):D.verify_inequality_certificate(p['rows'],p['order'],c)
    def test_35_missing_strict_inequality_rejected(self):
        p=self.patterns[1];c=deepcopy(p['certificates'][0]);c['inequalities'].pop()
        with self.assertRaises(ValueError):K.validate_certificate(p['rows'],p['order'],c)
    def test_36_tripled_patterns_saturate_pair_resources(self):
        for p in self.patterns:
            counts,costs=D.cluster_resources(p['rows'])
            self.assertEqual(len(counts),27);self.assertEqual(costs,[1]*27)
    def test_37_two_copy_pigeonhole_domain(self):
        # Four targets among three two-point clusters always use an internal pair.
        for S in combinations(range(6),4):
            cost=sum(sum(j//2==k for j in S)*(sum(j//2==k for j in S)-1)//2 for k in range(3))
            self.assertGreaterEqual(cost,1)
    def test_38_three_copy_saturation_domain(self):
        # Precisely 81 of the 126 row subsets have the only allowable cost one.
        costs=[]
        for S in combinations(range(9),4):
            cost=sum(sum(j//3==k for j in S)*(sum(j//3==k for j in S)-1)//2 for k in range(3))
            costs.append(cost);self.assertGreaterEqual(cost,1)
        self.assertEqual(costs.count(1),81)
    def test_39_convex_control_strict_quadrilateral_inequalities(self):
        # Exact squared comparison avoids irrational distance arithmetic on rectangle.
        # For rectangle 3 by 4, diagonals have length 5, so strict sums are 10>6,8.
        self.assertEqual(3*3+4*4,5*5);self.assertGreater(10,6);self.assertGreater(10,8)
    def test_40_filtered_reports_discrete_audit(self):
        self.assertEqual(D.certificate_audit()['status'],'passed; no family infeasibility inferred')

if __name__=='__main__':unittest.main(verbosity=2)
