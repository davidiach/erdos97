"""Defensive tests and exact controls; not formal proof of the all-size claims."""
import unittest
from fractions import Fraction as Q
from itertools import combinations

from geometry import Geometry, contains_disk, edge, rational, unit
from fixtures import (double_star, five_point_escape, eight_point_exports,
                      nine_point_return, third_nearest_squared)


class InputTests(unittest.TestCase):
    def test_coordinate_float_rejected(self):
        with self.assertRaises(ValueError): Geometry([(0.,0),(1,0),(0,1)])
    def test_radius_float_rejected(self):
        with self.assertRaises(ValueError): Geometry([(0,0),(1,0)]).threshold(1.)
    def test_bool_rejected(self):
        with self.assertRaises(ValueError): rational(True)
    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError): Geometry([(0,0),(0,0)])
    def test_collinear_rejected(self):
        with self.assertRaises(ValueError): Geometry([(0,0),(1,0),(2,0)])
    def test_interior_point_rejected(self):
        with self.assertRaises(ValueError): Geometry([(0,0),(4,0),(0,4),(1,1)])
    def test_empty_rejected(self):
        with self.assertRaises(ValueError): Geometry([])
    def test_bad_coordinate_dimension(self):
        with self.assertRaises(ValueError): Geometry([(0,0,0)])
    def test_zero_scale_rejected(self):
        with self.assertRaises(ValueError): Geometry([(0,0)],0)
    def test_negative_threshold_rejected(self):
        with self.assertRaises(ValueError): Geometry([(0,0),(1,0)]).threshold(-1)
    def test_wrong_radius_count(self):
        with self.assertRaises(ValueError): Geometry([(0,0),(1,0)]).rows([1])
    def test_zero_assigned_radius(self):
        with self.assertRaises(ValueError): Geometry([(0,0),(1,0)]).rows([0,1])
    def test_degenerate_edge_rejected(self):
        with self.assertRaises(ValueError): edge(0,0)
    def test_insufficient_third_nearest(self):
        with self.assertRaises(ValueError): third_nearest_squared(Geometry([(0,0),(1,0)]))


class GeometryTests(unittest.TestCase):
    def setUp(self):
        self.square=Geometry([(0,0),(1,0),(1,1),(0,1)])
    def test_rational_unit_identity(self):
        for t in [0,Q(1,3),-7,Q(16,5),Q(22,3),39]:
            x,y=unit(t); self.assertEqual(x*x+y*y,1)
    def test_support_sign_isometry(self):
        pts=[(3-4*y,2+4*x) for x,y in self.square.points]
        g=Geometry(pts)
        self.assertEqual(g.support_count,8)
        self.assertEqual(g.d2[0][2],32)
    def test_closed_diameter_disk_right_angle(self):
        self.assertEqual(self.square.blockers((0,2)),[1,3])
        self.assertEqual(self.square.blockers((0,1)),[])
    def test_crossing_diagonal_lemma(self):
        self.assertEqual(self.square.crossing_diagonal_lemma(),{'quadrilaterals':1})
    def test_short_graph_not_whole_threshold_graph(self):
        c=self.square.threshold(2)
        self.assertEqual(len(self.square.crossings(c['unit_edges'])),1)
        self.assertEqual(len(self.square.crossings(c['short_edges'])),0)
    def test_cycle_not_forest(self):
        c=self.square.mutual_short([2,2,2,2])
        self.assertEqual(c['degrees'],[2,2,2,2])
        self.assertEqual(len(c['edges']),4)
    def test_rank_three_cannot_enter_checker(self):
        with self.assertRaises(ValueError): self.square.mutual_short([3]*4)
    def test_common_threshold_rank_three_rejected(self):
        with self.assertRaises(ValueError): self.square.threshold(3)
    def test_crossing_graph_not_triangulated(self):
        with self.assertRaises(ValueError): self.square.triangulation({(0,2),(1,3)})
    def test_one_point_convention(self):
        c=Geometry([(0,0)]).threshold(1)
        self.assertEqual(c['unit_edge_bound'],0)
    def test_two_point_short_path_penalty(self):
        c=Geometry([(0,0),(1,0)]).threshold(2)
        self.assertEqual(c['unit_edge_bound'],0)
        self.assertEqual(c['nontrivial_short_paths'],1)
    def test_triangle_exact_base_bound(self):
        c=Geometry([(0,0),(1,0),('1/2','1/2')],3).threshold(1)
        self.assertEqual(c['unit_edge_count'],3)
        self.assertEqual(c['unit_edge_bound'],3)
    def test_rhombus_exact_base_bound(self):
        c=Geometry([(0,0),(1,0),('1/2','1/2'),('1/2','-1/2')],3).threshold(1)
        self.assertEqual(c['unit_edge_count'],5)
        self.assertEqual(c['unit_edge_bound'],5)
    def test_square_duplicate_ear_base_resources(self):
        c=self.square.threshold(2)
        self.assertEqual(len(c['cycle_ear_charges']),2)
        self.assertEqual(len(c['non_gabriel_unit_blockers']),2)
        self.assertEqual(c['short_cycles'],1)
        self.assertEqual(c['unit_edge_bound'],3)
    def test_hexagon_long_cycle(self):
        g=Geometry([(1,0),('1/2','1/2'),('-1/2','1/2'),(-1,0),
                    ('-1/2','-1/2'),('1/2','-1/2')],3)
        c=g.threshold(3)
        self.assertEqual(c['unit_edge_count'],6)
        self.assertEqual(c['unit_edge_bound'],7)
        self.assertEqual(len(c['cycle_ear_charges']),2)
    def test_obtuse_short_triangle_one_blocked_edge(self):
        g=Geometry([(0,0),(3,0),(1,1)]); c=g.threshold(10)
        self.assertEqual(c['short_cycles'],1)
        self.assertEqual(len(c['strict_gabriel_edges']),2)
    def test_acute_short_triangle_no_blocked_edge(self):
        c=Geometry([(0,0),(2,0),(1,2)]).threshold(6)
        self.assertEqual(len(c['strict_gabriel_edges']),3)
    def test_hereditary_constant_radius_condition(self):
        g=self.square
        for size in range(1,5):
            for ids in combinations(range(4),size):
                sub=Geometry([g.points[i] for i in ids]); sub.threshold(2)


class ExportTests(unittest.TestCase):
    def test_four_target_equality(self):
        f=five_point_escape(); g=Geometry(f['points']); c=g.layer_escape(f['radii_squared'])
        self.assertEqual(c['minimum_layer'],[0])
        self.assertEqual(len(c['higher_radius_targets']),4)
        self.assertEqual(c['export_count'],4)
    def test_six_export_equality(self):
        f=eight_point_exports();g=Geometry(f['points']);c=g.layer_escape(f['radii_squared'])
        self.assertEqual(c['minimum_layer'],[0,1])
        self.assertEqual(c['export_count'],6)
        self.assertEqual(c['export_lower_bound'],6)
    def test_two_center_exact_cyclic_order(self):
        self.assertEqual(Geometry(double_star()).order,[4,0,1,7,6,5,2,3])
    def test_radii_really_third_nearest(self):
        for f in [five_point_escape(),eight_point_exports(),nine_point_return()]:
            self.assertEqual([Q(x) for x in f['radii_squared']],third_nearest_squared(Geometry(f['points'])))
    def test_nonrich_minimum_is_not_rejected(self):
        c=Geometry([(0,0),(1,0),(1,1),(0,1)]).layer_escape([1]*4)
        self.assertFalse(c['all_minimum_vertices_rich'])
    def test_return_whole_minimum_layer_rich(self):
        f=nine_point_return(); g=Geometry(f['points']); c=g.layer_escape(f['radii_squared'])
        self.assertTrue(c['all_minimum_vertices_rich'])
        self.assertEqual(c['minimum_layer'],[0])
        self.assertEqual(c['higher_radius_targets'],[1,2,3,4])
    def test_return_center_has_actual_four_tie(self):
        f=nine_point_return();g=Geometry(f['points']);rows=g.rows(f['radii_squared'])
        self.assertEqual(rows['witnesses'][5],[0,6,7,8])
        self.assertEqual(rows['closer'][5],[3,4])
    def test_return_all_radius_profiles(self):
        f=nine_point_return();g=Geometry(f['points'])
        self.assertEqual(g.multiplicities(),[4,1,1,1,1,4,1,1,1])
        self.assertEqual(Geometry(g.points[1:]).multiplicities(),[1,1,1,1,3,1,1,1])
    def test_return_supporting_margin(self):
        g=Geometry(nine_point_return()['points'])
        self.assertEqual(g.support_count,63)
        self.assertEqual(g.minimum_support,Q(209808,25628605))
    def test_band_is_not_about_every_higher_center(self):
        f=nine_point_return();g=Geometry(f['points']);c=g.layer_escape(f['radii_squared'])
        self.assertNotIn(5,c['higher_radius_targets'])
        self.assertEqual(Q(f['radii_squared'][5]),4*c['minimum_radius_squared'])
    def test_return_has_nonempty_mutual_short_triangle(self):
        f=nine_point_return(); g=Geometry(f['points']); c=g.mutual_short(f['radii_squared'])
        self.assertEqual(c['edges'],[(1,2),(4,5),(6,7),(6,8),(7,8)])
    def test_unequal_radii_symmetric_closer_relation_is_possible(self):
        g=Geometry([(0,0),(0,1),(10,0),(10,2)]); rows=g.rows([1,1,4,4])
        self.assertEqual(rows['closer'],[[],[],[],[]])
        self.assertEqual(list(map(len,rows['witnesses'])),[1,1,1,1])


class DiskTests(unittest.TestCase):
    def test_internal_tangency_included(self):
        self.assertTrue(contains_disk(4,1,1))
    def test_strict_containment(self):
        self.assertTrue(contains_disk(9,1,1))
    def test_overlap_not_containment(self):
        self.assertFalse(contains_disk(4,1,4))
    def test_center_equal_nested(self):
        self.assertTrue(contains_disk(4,1,0))
    def test_wrong_direction(self):
        self.assertFalse(contains_disk(1,4,1))
    def test_invalid_disk_data(self):
        with self.assertRaises(ValueError): contains_disk(0,1,1)
    def test_four_closer_bound_sharp(self):
        g=Geometry(five_point_escape()['points'])
        self.assertEqual(sum(g.d2[1][j]<4 for j in range(5) if j!=1),4)


if __name__=='__main__':
    unittest.main()
