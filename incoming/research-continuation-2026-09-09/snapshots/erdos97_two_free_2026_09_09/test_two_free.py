"""Focused regression, independent controls, and fail-closed certificate tests.

The two full 4,500-case replays are separate commands, not replaced by these
unit tests or by comparisons of saved report counters.
"""
from __future__ import annotations
import copy
from fractions import Fraction as F
from itertools import combinations, permutations, product
import json
from pathlib import Path
import random
import tempfile
import unittest
from unittest.mock import patch

import oracle as independent
import geometry as G
import verify
from row_search import Model, Search
from metric_filter import obstruction
from certificate_arithmetic import check as check_metric
import audit_sharpness
import sharpness
import prior
from build_certificate import build, partition
from discover import discover

ROOT=Path(__file__).resolve().parent


def rich_control_model():
    order=[4,10,2,12,6,5,11,0,13,7,3,9,1,14,8]
    ranks={v:k for k,v in enumerate(order)}
    adjacency={};support={}
    for i in range(6):
        orbit,k=divmod(i,3)
        if orbit==0:
            support[i]=(k,6+k)
            adjacency[i]=tuple(j for j in range(3)if j!=i)
        else:
            support[i]=(k,)
            adjacency[i]=(k,3+(k+1)%3,3+(k+2)%3)
    return Model(adjacency,support,ranks,mandatory=(3,4))


def brute(model):
    vertices=sorted(model.adjacency)
    for size in range(len(model.mandatory),len(vertices)+1):
        for used in combinations(vertices,size):
            if not set(model.mandatory)<=set(used):continue
            domains=[]
            for i in used:
                options=[]
                for chosen in combinations(sorted(set(model.adjacency[i])&set(used)),4-len(model.old_support[i])):
                    options.append(frozenset(model.old_support[i])|frozenset(9+j for j in chosen))
                domains.append(options)
            for selected in product(*domains):
                okay=True
                for a,b in combinations(range(size),2):
                    common=selected[a]&selected[b]
                    if len(common)>2:
                        okay=False;break
                    if len(common)==2:
                        x,y=common
                        if not independent.interlace_possible(model.ranks,9+used[a],9+used[b],x,y):
                            okay=False;break
                if okay:
                    rows={9+i:sorted(row)for i,row in zip(used,selected)}
                    if independent.metric_cancelled(rows,model.ranks) is None:return True
    return False


class CoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.certificate=json.loads((ROOT/'data/certificate.json').read_text())
    def modified(self):return copy.deepcopy(self.certificate)
    def test_all_4500_cases(self):
        verify.validate_structure(self.certificate)
        self.assertEqual(len(self.certificate['cases']),4500)
    def test_generator_is_exact(self):self.assertEqual(build(),self.certificate)
    def test_partition_counters(self):
        nodes=leaves=depth=0
        def walk(t,d):
            nonlocal nodes,leaves,depth
            nodes+=1;depth=max(depth,d)
            if t is None:leaves+=1
            else:
                self.assertEqual(len(t['children']),2)
                for c in t['children']:walk(c,d+1)
        for case in self.certificate['cases']:walk(case['tree'],0)
        self.assertEqual((nodes,leaves,depth),(24742,14621,36))
    def test_missing_case_rejected(self):
        r=self.modified();r['cases'].pop()
        with self.assertRaises(ValueError):verify.validate_structure(r)
    def test_duplicate_case_rejected(self):
        r=self.modified();r['cases'][1]=r['cases'][0]
        with self.assertRaises(ValueError):verify.validate_structure(r)
    def test_reordered_cases_rejected(self):
        r=self.modified();r['cases'][0],r['cases'][1]=r['cases'][1],r['cases'][0]
        with self.assertRaises(ValueError):verify.validate_structure(r)
    def test_false_scope_rejected(self):
        r=self.modified();r['not_an_unrestricted_solution']=False
        with self.assertRaises(ValueError):verify.validate_structure(r)
    def test_extra_claim_rejected(self):
        r=self.modified();r['solved']=True
        with self.assertRaises(ValueError):verify.validate_structure(r)
    def test_wrong_hash_rejected(self):
        r=self.modified();r['input_sha256']='0'*64
        with self.assertRaises(ValueError):verify.validate_structure(r)
    def test_wrong_commit_rejected(self):
        r=self.modified();r['base_sha']='0'*40
        with self.assertRaises(ValueError):verify.validate_structure(r)
    def test_boolean_cell_rejected(self):
        r=self.modified();r['cases'][0]['cells'][0]=False
        with self.assertRaises(ValueError):verify.validate_structure(r)
        with self.assertRaises(ValueError):independent.audit(r,[])
    def test_boolean_old_witness_rejected(self):
        r=self.modified();r['cases'][0]['old_witnesses'][0]=True
        with self.assertRaises(ValueError):verify.validate_structure(r)
        with self.assertRaises(ValueError):independent.audit(r,[])
    def test_dropped_child_rejected(self):
        r=self.modified();r['cases'][0]['tree']={'coordinate':0,'edge':0,'children':[None]}
        with self.assertRaises(ValueError):verify.verify(r,[0])
        with self.assertRaises(ValueError):independent.audit(r,[0])
    def test_invalid_edge_rejected(self):
        r=self.modified();r['cases'][0]['tree']={'coordinate':0,'edge':3,'children':[None,None]}
        with self.assertRaises(ValueError):verify.verify(r,[0])
        with self.assertRaises(ValueError):independent.audit(r,[0])
    def test_unresolved_leaf_rejected(self):
        r=self.modified();r['cases'][0]['tree']={'UNRESOLVED':'depth guard'}
        with self.assertRaises(ValueError):verify.verify(r,[0])
        with self.assertRaises(ValueError):independent.audit(r,[0])
    def test_abstract_assignment_not_a_rejection(self):
        r=self.modified();r['cases'][0]['tree']=None
        with patch.object(verify,'models',return_value=[rich_control_model()]):
            with self.assertRaises(ValueError):verify.verify(r,[0])
    def test_partition_path_hole_rejected(self):
        with self.assertRaises(ValueError):partition([[[0,0,0]]])
    def test_partition_path_duplicate_rejected(self):
        with self.assertRaises(ValueError):partition([[],[]])
    def test_incompatible_splits_rejected(self):
        with self.assertRaises(ValueError):partition([[[0,0,0]],[[1,0,1]]])
    def test_case_index_guards(self):
        for indices in([0,0],[-1],[4500],[True]):
            with self.subTest(indices=indices):
                with self.assertRaises(ValueError):verify.verify(self.certificate,indices)
                with self.assertRaises(ValueError):independent.audit(self.certificate,indices)
    def test_corrupted_archive_rejected(self):
        with tempfile.TemporaryDirectory()as tmp:
            directory=Path(tmp);(directory/'inputs').mkdir();(directory/'inputs/internal_support.zip').write_bytes(b'bad')
            with patch.object(prior,'ROOT',directory):
                with self.assertRaises(ValueError):prior.archive_hash()
    def test_unknown_dependency_rejected(self):
        with self.assertRaises(ValueError):prior.load('nonexistent')


class GeometryTests(unittest.TestCase):
    def test_preceding_old_ceiling(self):
        points,slots,edges,ceiling,triangles=G.context()
        self.assertEqual((len(points),len(slots),len(edges),len(triangles)),(9,42,123,9))
        self.assertEqual(ceiling['triples'],84)
    def test_split_covers_parent_area(self):
        for triangle in G.context()[4]:
            for edge in range(3):
                left,right=G.split(triangle,edge)
                self.assertEqual(G.O.turn(*left)+G.O.turn(*right),G.O.turn(*triangle))
                self.assertGreater(G.O.turn(*left),0)
                self.assertGreater(G.O.turn(*right),0)
    def test_invalid_split_rejected(self):
        for edge in(-1,3,True,1.0):
            with self.assertRaises(ValueError):G.split(G.context()[4][0],edge)
    def test_common_radius_disjoint_intervals(self):
        Q=G.O.Q
        intervals={i:(Q(2*i),Q(2*i+1))for i in range(5)}
        self.assertEqual(G.radius_covers(intervals,4),[])
    def test_common_radius_boundary_retained(self):
        Q=G.O.Q
        intervals={0:(Q(0),Q(1)),1:(Q(1),Q(2)),2:(Q(1),Q(1)),3:(Q(0),Q(3))}
        self.assertEqual(G.radius_covers(intervals,4),[frozenset(range(4))])
    def test_two_cover_implementations(self):
        rng=random.Random(9702)
        for _ in range(40):
            intervals={i:tuple(sorted((rng.randrange(9),rng.randrange(9))))for i in range(7)}
            self.assertEqual(G.radius_covers(intervals,4),independent.covers(intervals,4))
    def test_closed_triangle_self_distance(self):
        for triangle in G.context()[4]:
            low,high=G.triangle_distance_range(triangle,triangle)
            self.assertEqual(low,0);self.assertGreater(high,0)
    def test_independent_root_graphs(self):
        ts=G.context()[4];us=independent.context()[4]
        cases=[((0,0),(None,None)),((2,5),(3,4)),((2,8),(3,5)),((5,8),(4,5))]
        for cells,old in cases:
            a=G.models(ts[cells[0]],ts[cells[1]],cells,old)
            b=independent.model_list(us[cells[0]],us[cells[1]],cells,old)
            normalize=lambda graph:tuple((i,tuple(sorted(v)))for i,v in sorted(graph.items()))
            self.assertEqual(sorted(normalize(m.adjacency)for m in a),sorted(normalize(g)for g,s,r in b))
    def test_fresh_discovery_guard_is_inconclusive(self):
        result=discover([2,5],[3,4],max_depth=0,max_nodes=0)
        self.assertEqual(result['status'],'unresolved')
        self.assertIn('UNRESOLVED',result['tree'])


class SearchTests(unittest.TestCase):
    def test_three_internal_positive_control_survives(self):
        m=rich_control_model();a=Search(m).run()
        b,_,_=independent.exact_search({i:frozenset(v)for i,v in m.adjacency.items()},
                                      {i:frozenset(v)for i,v in m.old_support.items()},m.ranks,frozenset(m.mandatory))
        self.assertEqual(a['status'],'abstract_assignment');self.assertIsNotNone(b)
    def test_three_shared_old_witnesses_rejected(self):
        m=Model({0:(1,),1:(0,)},{0:(0,1,2),1:(0,1,2)},{i:i for i in range(11)},mandatory=(0,1))
        self.assertEqual(Search(m).run()['status'],'exhausted')
    def test_node_guard_not_an_exclusion(self):
        self.assertEqual(Search(rich_control_model(),node_limit=0).run()['status'],'unresolved')
    def test_model_duplicate_mandatory_rejected(self):
        m=rich_control_model()
        with self.assertRaises(ValueError):Search(Model(m.adjacency,m.old_support,m.ranks,mandatory=(3,3)))
    def test_model_self_witness_rejected(self):
        m=rich_control_model();adj=dict(m.adjacency);adj[0]=(0,1)
        with self.assertRaises(ValueError):Search(Model(adj,m.old_support,m.ranks,mandatory=(3,4)))
    def test_model_missing_target_rejected(self):
        m=rich_control_model();adj=dict(m.adjacency);adj[0]=(1,99)
        with self.assertRaises(ValueError):Search(Model(adj,m.old_support,m.ranks,mandatory=(3,4)))
    def test_model_repeated_old_witness_rejected(self):
        m=rich_control_model();old=dict(m.old_support);old[0]=(0,0)
        with self.assertRaises(ValueError):Search(Model(m.adjacency,old,m.ranks,mandatory=(3,4)))
    def test_crossing_encodings_exhaustively_agree(self):
        m=rich_control_model()
        for values in product(range(4),repeat=4):
            ranks=dict(m.ranks);ranks.update(dict(zip([9,10,0,1],values)))
            model=Model(m.adjacency,m.old_support,ranks,mandatory=m.mandatory)
            self.assertEqual(Search(model).can_cross(0,1,0,1),independent.interlace_possible(ranks,9,10,0,1))
    def test_subset_search_matches_brute_force(self):
        rng=random.Random(971234)
        for test in range(32):
            n=4
            adjacency={i:tuple(j for j in range(n)if i!=j and rng.randrange(4)!=0)for i in range(n)}
            support={i:tuple(sorted(rng.sample(range(9),2)))for i in range(n)}
            order=list(range(13));rng.shuffle(order);ranks={v:k for k,v in enumerate(order)}
            m=Model(adjacency,support,ranks,mandatory=(0,1))
            self.assertEqual(Search(m).run()['status']=='abstract_assignment',brute(m),test)


class MetricTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.records=json.loads((ROOT/'data/last_leaf_cancellations.json').read_text())
    def ranks(self,case):
        ranks={v:2*k for k,v in enumerate(G.O.B.ORDER)}
        ranks.update({9+i:2*s.cell+1 for i,s in enumerate(G.context()[1])})
        ranks.update({51:2*case['cells'][0]+1,52:2*case['cells'][1]+1})
        return ranks
    def test_all_24_stored_cancellations(self):
        count=0
        for case in self.records['cases']:
            ranks=self.ranks(case)
            for record in case['cancellations']:
                self.assertTrue(check_metric(record,ranks));count+=1
                rows={int(i):w for i,w in record['rows'].items()}
                self.assertIsNotNone(obstruction(rows,ranks))
                self.assertIsNotNone(independent.metric_cancelled(rows,ranks))
        self.assertEqual(count,24)
    def test_missing_equality_rows_rejected(self):
        case=self.records['cases'][0];record=copy.deepcopy(case['cancellations'][0]);record['rows']={}
        with self.assertRaises(ValueError):check_metric(record,self.ranks(case))
    def test_reversed_quad_pair_rejected(self):
        case=self.records['cases'][0];record=copy.deepcopy(case['cancellations'][0]);q=record['inequalities'][0]['quad'];q[0],q[1]=q[1],q[0]
        with self.assertRaises(ValueError):check_metric(record,self.ranks(case))
    def test_dropped_inverse_term_rejected(self):
        case=self.records['cases'][0];record=copy.deepcopy(next(r for r in case['cancellations']if r['type']=='inverse'));record['inequalities'].pop()
        with self.assertRaises(ValueError):check_metric(record,self.ranks(case))
    def test_tied_quad_not_used(self):
        case=self.records['cases'][0];record=copy.deepcopy(case['cancellations'][0]);ranks=self.ranks(case)
        q=record['inequalities'][0]['quad'];ranks[q[0]]=ranks[q[1]]
        with self.assertRaises(ValueError):check_metric(record,ranks)
    def test_real_rich_cap_not_rejected_by_metric_filter(self):
        m=rich_control_model();rows={i+9:list(m.old_support[i])+[9+j for j in m.adjacency[i]]for i in m.adjacency}
        self.assertIsNone(obstruction(rows,m.ranks));self.assertIsNone(independent.metric_cancelled(rows,m.ranks))


class ControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.exact=sharpness.verify();cls.enclosed=audit_sharpness.verify()
    def test_exact_control_report_reproduces(self):self.assertEqual(self.exact,json.loads((ROOT/'data/sharpness.json').read_text()))
    def test_separate_control_report_reproduces(self):self.assertEqual(self.enclosed,json.loads((ROOT/'data/sharpness_oracle.json').read_text()))
    def test_control_is_not_all_rich(self):
        self.assertFalse(self.exact['all_rich']);self.assertEqual(self.exact['old_good_vertices'],list(range(6)))
    def test_internal_count_is_exactly_three(self):
        self.assertEqual(self.exact['internally_supported_new_vertices'],[12,13,14])
        self.assertEqual(self.exact['internally_supported_new_vertices'],self.enclosed['internally_supported_new_vertices'])
    def test_all_distance_classes_match_enclosures(self):
        self.assertEqual(self.exact['all_distance_classes'],self.enclosed['all_radius_interval_groups'])
    def test_195_supporting_signs(self):
        self.assertEqual(self.exact['strict_support_checks'],195);self.assertEqual(self.enclosed['strict_support_checks'],195)
    def test_six_symbolic_identities(self):self.assertEqual(len(audit_sharpness.identities()),6)
    def test_tower_reciprocal_identity(self):
        _,p=sharpness.construct();x=p[14][0]+2
        self.assertEqual(x*(1/x),1)
    def test_interval_rational_arithmetic_encloses(self):
        I=audit_sharpness.Interval;D=audit_sharpness.UNIT
        def contains(interval,x):self.assertLessEqual(F(interval.lo,D),x);self.assertLessEqual(x,F(interval.hi,D))
        for a,b in[(F(-2,7),F(3,11)),(F(8,3),F(-7,13)),(F(1,3),F(4,7))]:
            x,y=I.number(a),I.number(b)
            contains(x+y,a+b);contains(x*y,a*b);contains(x/y,a/b)
    def test_interval_root_enclosure(self):
        I=audit_sharpness.Interval;D=audit_sharpness.UNIT
        for q in[F(1,10),F(721),F(7,3)]:
            r=I.number(q).sqrt();self.assertLessEqual(F(r.lo,D)**2,q);self.assertGreaterEqual(F(r.hi,D)**2,q)
    def test_inexact_interval_constant_rejected(self):
        with self.assertRaises(ValueError):audit_sharpness.Interval.number(.1)
    def test_interval_zero_divisor_rejected(self):
        with self.assertRaises(ZeroDivisionError):audit_sharpness.Interval.number(1)/audit_sharpness.Interval(-1,1)


if __name__=='__main__':unittest.main(verbosity=2)
