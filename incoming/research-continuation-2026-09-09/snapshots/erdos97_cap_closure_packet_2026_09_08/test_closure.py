"""Defensive tests for the new reduction, geometry, and independent checker."""
import copy
import json
import unittest
import subprocess
import sys
import core
import oracle


class ClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads((core.ROOT/'data/verification.json').read_text())
        cls.P = core.base9()
        cls.slots = core.build_slots(cls.P, core.ORDER)
        cls.edges, cls.counts, cls.digest = core.graph_data(cls.P, cls.slots)
        cls.R = oracle.ring()
        cls.OP = oracle.seed(cls.R)
        cls.orecords = oracle.ray_slots(cls.R, cls.OP, core.ORDER)
        cls.oedges, cls.ocounts, cls.odigest = oracle.graph(cls.R, cls.OP, cls.orecords)

    def discrete(self, record):
        return oracle.check_discrete(record,self.orecords,self.oedges,self.ocounts,self.odigest)

    def core_record(self, record):
        return oracle.check_core(record,self.R,self.OP,self.orecords)

    def test_01_full_primary_report(self):
        self.assertEqual(core.run(), self.report)

    def test_02_full_independent_report(self):
        expected = json.loads((core.ROOT/'data/oracle_report.json').read_text())
        self.assertEqual(oracle.audit(self.report), expected)

    def test_03_exact_input_rejects_float(self):
        with self.assertRaises(TypeError):
            core.Q(0.1)
        with self.assertRaises(TypeError):
            self.R(0.1)
        with self.assertRaises(ValueError):
            core.rq([1,2])
        result = subprocess.run([sys.executable,"-O","verify.py"],cwd=core.ROOT,capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn("without Python -O",result.stderr)

    def test_04_reversed_boundary_rejected(self):
        with self.assertRaises(ValueError):
            core.strict_check(self.P, core.ORDER[::-1])

    def test_05_duplicate_boundary_rejected(self):
        with self.assertRaises(ValueError):
            core.strict_check(self.P, [0]*9)

    def test_06_duplicate_point_rejected(self):
        with self.assertRaises(ValueError):
            core.strict_check(self.P+[self.P[0]], list(range(10)))

    def test_07_all_slots_are_on_one_ray(self):
        self.assertEqual(len(self.slots),42)
        for s in self.slots:
            self.assertTrue(s.lower >= 0 or s.upper <= 0)
            self.assertLess(s.lower,s.upper)

    def test_08_insertion_cell_midpoints(self):
        for s in self.slots:
            x = s.point((s.lower+s.upper)/2)
            for k in range(9):
                sign = core.turn(self.P[core.ORDER[k]],self.P[core.ORDER[(k+1)%9]],x).sign()
                self.assertEqual(sign,-1 if k == s.cell else 1)
            self.assertEqual(core.dist(x,self.P[s.pair[0]]),core.dist(x,self.P[s.pair[1]]))

    def test_09_pair_ray_capacity_triangle(self):
        for s in self.slots:
            t1=(2*s.lower+s.upper)/3
            t2=(s.lower+2*s.upper)/3
            if t1 < 0:
                t1,t2=t2,t1
            near,far=s.point(t1),s.point(t2)
            a,b=[self.P[k] for k in s.pair]
            triangle=[a,b,far]
            if core.turn(*triangle)<0:
                triangle[0],triangle[1]=triangle[1],triangle[0]
            self.assertGreater(core.turn(*triangle),0)
            self.assertTrue(all(core.turn(triangle[k],triangle[(k+1)%3],near)>0 for k in range(3)))

    def test_10_range_contains_exact_grid(self):
        for i,j in [(0,1),(6,14),(14,22),(4,5),(22,6),(33,37)]:
            s,t=self.slots[i],self.slots[j]
            low,high=core.interval_range(self.P,s,t)
            for u in [s.lower,(s.lower+s.upper)/2,s.upper]:
                for v in [t.lower,(t.lower+t.upper)/2,t.upper]:
                    value=core.dist(s.point(u),t.point(v))-core.dist(s.point(u),self.P[s.pair[0]])
                    self.assertLessEqual(low,value)
                    self.assertLessEqual(value,high)

    def test_11_two_slot_builders_agree(self):
        self.assertEqual([s.json() for s in self.slots],self.orecords)

    def test_12_two_range_implementations_agree(self):
        self.assertEqual([list(e) for e in self.edges],self.oedges)
        self.assertEqual(self.counts,self.ocounts)
        self.assertEqual(self.digest,self.odigest)

    def test_13_graph_peeling_control(self):
        self.assertEqual(core.peel(range(4),[(0,1),(0,2),(1,0),(1,2),(2,0),(2,1),(3,0)])[0],[0,1,2])
        self.assertEqual(core.peel(range(3),[(0,1),(1,2),(2,0)])[0],[])

    def test_14_missing_slot_rejected(self):
        r=copy.deepcopy(self.report);r['slots'].pop()
        with self.assertRaises(AssertionError):self.discrete(r)

    def test_15_changed_slot_endpoint_rejected(self):
        r=copy.deepcopy(self.report);r['slots'][0]['lower']=['0','0']
        with self.assertRaises(AssertionError):self.discrete(r)

    def test_16_missing_graph_edge_rejected(self):
        r=copy.deepcopy(self.report);r['possible_edges'].pop()
        with self.assertRaises(AssertionError):self.discrete(r)

    def test_17_invented_graph_edge_rejected(self):
        r=copy.deepcopy(self.report);r['possible_edges'].append([0,0])
        with self.assertRaises(AssertionError):self.discrete(r)

    def test_18_changed_range_digest_rejected(self):
        r=copy.deepcopy(self.report);r['range_digest']='0'*64
        with self.assertRaises(AssertionError):self.discrete(r)

    def test_19_invalid_peeling_rejected(self):
        r=copy.deepcopy(self.report);r['peeling_layers'][0].append(6)
        with self.assertRaises(AssertionError):self.discrete(r)

    def test_20_incomplete_peeling_rejected(self):
        r=copy.deepcopy(self.report);r['peeling_layers'].pop()
        with self.assertRaises(AssertionError):self.discrete(r)

    def test_21_wrong_core_rejected(self):
        r=copy.deepcopy(self.report);r['remaining_core']=[6,14]
        with self.assertRaises(AssertionError):self.discrete(r)

    def test_22_changed_quadratic_rejected(self):
        r=copy.deepcopy(self.report);r['core_classification']['quadratic'][0]=['1','0']
        with self.assertRaises(AssertionError):self.core_record(r)

    def test_23_changed_radical_rejected(self):
        r=copy.deepcopy(self.report);r['core_classification']['discriminant']=['1','0']
        with self.assertRaises(AssertionError):self.core_record(r)

    def test_24_wrong_root_branch_rejected(self):
        r=copy.deepcopy(self.report);r['core_classification']['roots'][0]['in_open_slot']=True
        with self.assertRaises(AssertionError):self.core_record(r)

    def test_25_inexact_new_coordinate_rejected(self):
        r=copy.deepcopy(self.report);r['core_classification']['points'][9][0][0][0]='0'
        with self.assertRaises(AssertionError):self.core_record(r)

    def test_26_false_all_rich_claim_rejected(self):
        r=copy.deepcopy(self.report);r['core_classification']['maxima']=[4]*12
        with self.assertRaises(AssertionError):self.core_record(r)

    def test_27_false_witness_rejected(self):
        r=copy.deepcopy(self.report);r['core_classification']['new_witness_rows'][0]['witnesses'][0]=9
        with self.assertRaises(AssertionError):self.core_record(r)

    def test_28_invalid_extension_field_rejected(self):
        with self.assertRaises(AssertionError):oracle.ring(1,0)
        S=self.report['core_classification']['discriminant']
        R4=oracle.ring(oracle.F(S[0]),oracle.F(S[1]))
        Y=R4(0,0,1)
        self.assertEqual(Y*Y,R4(oracle.F(S[0]),oracle.F(S[1])))
        self.assertGreater(Y.sign(),0)

    def test_29_positive_cap_control(self):
        oracle.positive(self.R,self.report['positive_control'])
        self.assertEqual(self.report['positive_control']['maxima'],[4]*3+[2]*6)

    def test_30_unbounded_input_fails_closed(self):
        Q=core.Q
        triangle=[(Q(0),Q(0)),(Q(2),Q(0)),(Q(0),Q(2))]
        with self.assertRaises(NotImplementedError):core.build_slots(triangle,[0,1,2])


if __name__ == '__main__':
    unittest.main()
