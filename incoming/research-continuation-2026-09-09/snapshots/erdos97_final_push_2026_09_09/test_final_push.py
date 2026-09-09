"""Exact regression and defensive tests for the delivered results."""
from pathlib import Path
from fractions import Fraction
from itertools import combinations,permutations,product
from math import comb
import copy,hashlib,json,random,shutil,subprocess,tempfile,unittest
import grid_metric as gm
import grid_oracle as go
import blocks
import audit_medians as am
from median_probe import group_domains,ORDER
from previous import previous_root,load_kalmanson,EXPECTED
ROOT=Path(__file__).resolve().parent

class MetricTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.D,cls.r=gm.build()
    def test_01_every_label_is_rich_at_common_radius(self):
        self.assertEqual(len(self.D),138)
        self.assertGreaterEqual(min(map(len,self.r['common_radius_fibers'])),4)
    def test_02_every_selected_row_has_four_exact_distances(self):
        for i,row in enumerate(self.r['selected_witness_rows']):
            self.assertEqual(len(set(row)),4);self.assertNotIn(i,row)
            self.assertTrue(all(self.D[i][j]==781100 for j in row))
    def test_03_full_fibers_are_linear(self):
        rows=list(map(set,self.r['common_radius_fibers']))
        self.assertTrue(all(len(a&b)<=1 for a,b in combinations(rows,2)))
    def test_04_all_analytic_margins_are_strict(self):
        self.assertTrue(all(Fraction(v)>0 for v in self.r['margin_bounds'].values()))
    def test_05_degree_histogram_and_incidence_count(self):
        self.assertEqual(self.r['fiber_size_histogram'],{4:52,5:20,6:20,7:12,8:34})
        self.assertEqual(sum(map(len,self.r['common_radius_fibers'])),784)
    def test_06_all_elementary_cyclic_constraints_checked(self):
        self.assertEqual(self.r['strict_elementary_kalmanson_checks'],138*135//2)
        self.assertGreater(Fraction(self.r['minimum_elementary_kalmanson_margin']),0)
    def test_07_nonplanarity_is_exact(self):
        self.assertEqual(self.r['nonplanar_gram_determinant'],'6052449518192')
    def test_08_saved_primary_certificate_matches(self):
        self.assertEqual(json.loads(json.dumps(self.r)),json.loads((ROOT/'evidence/grid_metric_certificate.json').read_text()))
    def test_09_different_representation_reconstructs_entire_matrix(self):
        r=go.check();self.assertEqual(r['matrix_entries_reconstructed'],138**2)
        self.assertEqual(r['cayley_menger_determinant'],'48419596145536')
    def check_bad_certificate(self,mutate):
        r=copy.deepcopy(self.r);mutate(r)
        with tempfile.TemporaryDirectory()as t:
            f=Path(t)/'bad.json';f.write_text(json.dumps(r))
            with self.assertRaises(ValueError):go.check(certificate_path=f)
    def test_10_false_gram_determinant_rejected(self):
        self.check_bad_certificate(lambda r:r.update(nonplanar_gram_determinant='0'))
    def test_11_omitted_radius_witness_rejected(self):
        self.check_bad_certificate(lambda r:r['common_radius_fibers'][0].pop())
    def test_12_wrong_point_order_rejected(self):
        self.check_bad_certificate(lambda r:r['point_order'].reverse())
    def test_13_altered_integer_entry_rejected(self):
        words=(ROOT/'evidence/grid_metric_integer_matrix.txt').read_text().split();words[4]=str(int(words[4])+1)
        with tempfile.TemporaryDirectory()as t:
            f=Path(t)/'bad.txt';f.write_text(' '.join(words))
            with self.assertRaises(ValueError):go.check(matrix_path=f)
    def test_14_unit_radius_normalization(self):
        for i,row in enumerate(self.r['selected_witness_rows']):
            self.assertTrue(all(self.D[i][j]/781100==1 for j in row))
    def test_15_general_grid_direction_argument_finite_controls(self):
        for k in range(4,9):
            N=2*(k-1)**2+1;directions=[(1,0),(0,1)]+[(1,j)for j in range(1,k-1)]
            self.assertEqual(len(directions),k)
            for x in range(N):
                for y in range(N):
                    sx=1 if x<=(N-1)//2 else -1;sy=1 if y<=(N-1)//2 else -1
                    for u,v in directions:
                        xx=x+(k-1)*sx*u;yy=y+(k-1)*sy*v
                        self.assertTrue(0<=xx<N and 0<=yy<N)
    def test_16_exhaustive_checker_inventory(self):
        r=json.loads((ROOT/'evidence/metric_exhaustive.json').read_text())
        self.assertEqual(r['strict_triangle_inequalities'],3*comb(138,3))
        self.assertEqual(r['strict_kalmanson_inequalities'],2*comb(138,4))
        self.assertEqual(r['strict_ptolemy_inequalities'],3*comb(138,4))
        self.assertFalse(r['planar_euclidean'])

class BlockTests(unittest.TestCase):
    def test_17_count_forces_three_five_point_blocks(self):
        for sizes in product(range(1,6),repeat=3):
            slack=sum(comb(s,2)for s in sizes)-2*sum(sizes)
            self.assertLessEqual(slack,0)
            self.assertEqual(slack==0,sizes==(5,5,5))
    def test_18_pair_cost_equality_forces_two_plus_two(self):
        for a in range(5):
            cost=comb(a,2)+comb(4-a,2)
            self.assertGreaterEqual(cost,2);self.assertEqual(cost==2,a==2)
    def test_19_incidence_square_identity(self):
        rng=random.Random(97092026)
        for _ in range(1000):
            d=[0]*10
            for _ in range(20):d[rng.randrange(10)]+=1
            lhs=sum((x-2)**2 for x in d);rhs=2*sum(comb(x,2)for x in d)-20
            self.assertEqual(lhs,rhs)
            if rhs<=0:self.assertEqual(d,[2]*10)
    def test_20_all_five_cycles_excluded_as_inversion_graphs(self):
        r=blocks.report();self.assertEqual(len(r['two_regular_five_vertex_graphs']),12)
        self.assertEqual(r['two_regular_inversion_graphs_on_five_vertices'],0)
    def test_21_even_cycle_positive_control(self):
        self.assertEqual(blocks.degrees(4,blocks.inversions([2,3,0,1])),[2]*4)
    def test_22_every_inversion_orientation_is_transitive(self):
        self.assertTrue(all(blocks.graph_transitive_orientation(5,blocks.inversions(p))for p in permutations(range(5))))
    def test_23_invalid_permutation_rejected(self):
        with self.assertRaises(ValueError):blocks.inversions([0,0,1])

class MedianTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'evidence/median_direct_1.json').read_text())
        cls.h=[h for h in cls.data['history']if'rows'in h]
        cls.legacy=load_kalmanson()
    def test_24_complete_local_domain_census(self):
        D,s=group_domains(0);self.assertEqual(s['raw'],531441)
        self.assertEqual(s['pairwise_and_cover'],13122);self.assertEqual(len(D),4374)
    def test_25_all_five_saved_patterns_pass_both_medians(self):
        self.assertEqual(len(self.h),5)
        for h in self.h:self.assertTrue(am.check_pattern(h['rows']))
    def test_26_all_fifty_four_certificates_pass_two_checkers(self):
        count=0
        for h in self.h:
            for c in h['kalmanson']['certificates']:
                self.assertTrue(self.legacy.validate_certificate(h['rows'],ORDER,c))
                self.assertTrue(am.alternate_certificate_check(h['rows'],ORDER,c));count+=1
        self.assertEqual(count,54)
    def check_bad(self,mutate):
        h=self.h[0];c=copy.deepcopy(h['kalmanson']['certificates'][0]);mutate(c)
        with self.assertRaises(ValueError):self.legacy.validate_certificate(h['rows'],ORDER,c)
        with self.assertRaises(ValueError):am.alternate_certificate_check(h['rows'],ORDER,c)
    def test_27_negative_weight_rejected(self):
        self.check_bad(lambda c:c['inequalities'][0].update(weight=-1))
    def test_28_missing_strict_inequality_rejected(self):
        self.check_bad(lambda c:c.update(inequalities=[]))
    def test_29_wrong_cyclic_order_rejected(self):
        self.check_bad(lambda c:c['inequalities'][0]['quadruple'].reverse())
    def test_30_omitted_equality_premise_rejected(self):
        self.check_bad(lambda c:c['selected_centers'].pop())
    def test_31_prior_pattern_is_not_a_median_survivor(self):
        x=json.loads((previous_root()/'data/moving_pattern_obstructions.json').read_text())['patterns'][0]
        with self.assertRaises(ValueError):am.check_pattern(x['rows'])
    def test_32_prior_archive_unchanged(self):
        self.assertEqual(hashlib.sha256((ROOT/'inputs/internal_support.zip').read_bytes()).hexdigest(),EXPECTED)

class CppDefensiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which('g++'):raise unittest.SkipTest('g++ absent; full metric replay reports this separately')
        cls.tmp=tempfile.TemporaryDirectory();cls.exe=Path(cls.tmp.name)/'check'
        r=subprocess.run(['g++','-O3','-std=c++17','-Wall','-Wextra','-Werror',str(ROOT/'check_metric.cpp'),'-lgmpxx','-lgmp','-o',str(cls.exe)],capture_output=True,text=True)
        if r.returncode:raise RuntimeError('C++/GMP build failed: '+r.stderr)
    @classmethod
    def tearDownClass(cls):
        if hasattr(cls,'tmp'):cls.tmp.cleanup()
    def rejected(self,text):
        f=Path(self.tmp.name)/'bad.txt';f.write_text(text)
        r=subprocess.run([str(self.exe),str(f)],capture_output=True,text=True)
        self.assertNotEqual(r.returncode,0);return r.stderr
    def simplex(self):return '6\n1\n1\n'+'\n'.join(' '.join('0'if i==j else'1'for j in range(6))for i in range(6))+'\n'
    def test_33_simplex_control_is_rich_but_not_strict_kalmanson(self):
        self.assertIn('Kalmanson',self.rejected(self.simplex()))
    def test_34_trailing_data_rejected(self):
        self.assertIn('trailing',self.rejected(self.simplex()+'1\n'))
    def test_35_truncated_data_rejected(self):
        self.assertIn('truncated',self.rejected('6\n1\n1\n0 1\n'))
    def test_36_noninteger_data_rejected(self):
        self.assertIn('truncated',self.rejected(self.simplex().replace('0 1','0 1.5',1)))

if __name__=='__main__':unittest.main(verbosity=2)
