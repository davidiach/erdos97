"""Defensive, exact unit tests. Run: python -m unittest -v test_bridge.py"""
import unittest
from fractions import Fraction as F
from itertools import combinations
from checker import (Geometry,VerificationError,crosses,minimum_layer_certificate,
                     threshold_graph_certificate)
import fixtures


class BridgeTests(unittest.TestCase):
    def test_empty_rejected(self):
        with self.assertRaises(VerificationError):Geometry.build([])

    def test_duplicate_rejected(self):
        with self.assertRaises(VerificationError):Geometry.build([(0,0),(0,0)])

    def test_collinear_rejected(self):
        with self.assertRaises(VerificationError):Geometry.build([(0,0),(1,0),(2,0)])

    def test_interior_rejected(self):
        with self.assertRaises(VerificationError):Geometry.build([(0,0),(3,0),(0,3),(1,1)])

    def test_float_coordinates_rejected(self):
        with self.assertRaises(VerificationError):Geometry.build([(0.0,0)])

    def test_boolean_coordinates_rejected(self):
        with self.assertRaises(VerificationError):Geometry.build([(True,0)])

    def test_float_radius_rejected(self):
        with self.assertRaises(VerificationError):minimum_layer_certificate(Geometry.build([(0,0)]),[1.0])

    def test_nonpositive_radii_rejected(self):
        for r in [0,-1]:
            with self.assertRaises(VerificationError):minimum_layer_certificate(Geometry.build([(0,0)]),[r])

    def test_radius_length_rejected(self):
        with self.assertRaises(VerificationError):minimum_layer_certificate(Geometry.build([(0,0)]),[])

    def test_scale_invalid(self):
        for scale in [0,-3,3.0]:
            with self.assertRaises(VerificationError):Geometry.build([(0,0)],scale)

    def test_singleton(self):
        c=minimum_layer_certificate(Geometry.build([(0,0)]),[1])
        self.assertEqual(c['graph']['face_budget'],0)
        self.assertEqual(c['nonrich_centers_in_minimum_layer'],[0])

    def test_two_points_equal_radii(self):
        c=minimum_layer_certificate(Geometry.build([(0,0),(1,0)]),[1,1])
        self.assertEqual(c['minimum_layer'],[0,1])
        self.assertEqual(c['nonrich_centers_in_minimum_layer'],[0,1])

    def test_two_points_unequal_radii(self):
        c=minimum_layer_certificate(Geometry.build([(0,0),(1,0)]),[1,2])
        self.assertEqual(c['minimum_layer'],[0])

    def test_sharp_deficit(self):
        geo,rho=fixtures.sharp_variable();c=minimum_layer_certificate(geo,rho)
        self.assertEqual(c['minimum_layer'],[0,3,4])
        self.assertEqual(c['rich_centers_in_minimum_layer'],[0])
        self.assertEqual(c['nonrich_centers_in_minimum_layer'],[3,4])
        self.assertEqual(c['graph']['face_budget'],1)

    def test_sharp_control_radii_are_realized(self):
        geo,rho=fixtures.sharp_variable()
        self.assertTrue(all(geo.witnesses(i,r) for i,r in enumerate(rho)))

    def test_four_ties_do_not_count_as_closer(self):
        geo,rho=fixtures.sharp_variable()
        self.assertEqual(geo.closer_counts(rho)[0],0)
        self.assertEqual(len(geo.witnesses(0,F(1))),4)

    def test_two_triangles_same_center(self):
        geo,rho=fixtures.two_short_pairs();c=minimum_layer_certificate(geo,rho)
        self.assertEqual(len(c['graph']['short_base_triangles']),2)
        self.assertEqual(len(c['assignments']),1)
        self.assertEqual({t['apex'] for t in c['graph']['short_base_triangles']},{0})

    def test_short_incident_side_allowed(self):
        geo,rho=fixtures.long_relative_to_side()
        minimum_layer_certificate(geo,rho)
        self.assertEqual(geo.d2[0][1],F(101,10000))
        self.assertEqual(rho[0],1)
        self.assertEqual(geo.closer_counts(rho)[0],1)
        self.assertEqual(len(geo.witnesses(0,rho[0])),4)

    def test_permutation_invariance(self):
        geo,rho=fixtures.sharp_variable();permutation=[3,0,4,1,2]
        moved=Geometry.build([geo.points[i] for i in permutation])
        c=minimum_layer_certificate(moved,[rho[i] for i in permutation])
        self.assertEqual([permutation[i] for i in c['rich_centers_in_minimum_layer']],[0])

    def test_exact_similarity(self):
        geo,rho=fixtures.sharp_variable()
        # Rational orthogonal rotation, a translation, and scale 7/3.
        rot=(F(3,5),F(4,5));s=F(7,3);v=(F(13,7),F(-2,9))
        pts=[fixtures.add(v,tuple(s*z for z in fixtures.mul(p,rot))) for p in geo.points]
        c=minimum_layer_certificate(Geometry.build(pts),[s*s*r for r in rho])
        self.assertEqual(c['rich_centers_in_minimum_layer'],[0])

    def test_reflection(self):
        geo,rho=fixtures.sharp_variable()
        c=minimum_layer_certificate(Geometry.build([(-x,y) for x,y in geo.points]),rho)
        self.assertEqual(c['rich_centers_in_minimum_layer'],[0])

    def test_all_nonempty_sharp_subsets(self):
        geo,rho=fixtures.sharp_variable()
        for mask in range(1,1<<5):
            indices=[i for i in range(5) if (mask>>i)&1]
            sub=Geometry.build([geo.points[i] for i in indices])
            minimum_layer_certificate(sub,[rho[i] for i in indices])

    def test_rank_two_pentagon_blocks_layer_extension(self):
        geo,rho=fixtures.rank_two_pentagon()
        self.assertEqual([i for i,r in enumerate(rho) if r==min(rho)],[0])
        self.assertEqual(len(geo.witnesses(0,rho[0])),4)
        self.assertEqual(max(geo.closer_counts(rho)),2)
        with self.assertRaisesRegex(VerificationError,'One-closer'):minimum_layer_certificate(geo,rho)

    def test_rank_two_eight_has_exactly_two_rich_vertices(self):
        geo,rho=fixtures.rank_two_eight()
        self.assertEqual(geo.maximum_multiplicities(),(4,1,1,1,4,1,1,1))
        self.assertEqual(geo.support_count,48)
        self.assertEqual(rho[4],F(16,13))
        self.assertEqual(geo.witnesses(4,rho[4]),(2,5,6,7))

    def test_rank_two_genuine_propagation_failure(self):
        geo,rho=fixtures.rank_two_eight()
        self.assertEqual(geo.d2[0][3],1);self.assertEqual(geo.d2[0][4],1)
        self.assertLess(geo.d2[3][4],1);self.assertGreater(rho[4],rho[0])
        self.assertEqual(geo.closer_counts(rho)[4],2)

    def test_square_diagonals_cross(self):
        geo,rho=fixtures.rank_two_square()
        self.assertTrue(crosses(geo.points,(0,2),(1,3)))
        self.assertEqual(geo.closer_counts(rho),(2,2,2,2))
        with self.assertRaisesRegex(VerificationError,'matching'):
            threshold_graph_certificate(geo,range(4),F(2))

    def test_square_sides_pass(self):
        geo,_=fixtures.rank_two_square()
        g=threshold_graph_certificate(geo,range(4),F(1))
        self.assertEqual(len(g['unit_edges']),4);self.assertFalse(g['triangles'])

    def test_three_witness_threshold_not_silently_strengthened(self):
        geo,rho=fixtures.three_witnesses_no_short_pair()
        w=geo.witnesses(0,F(1))
        self.assertEqual(len(w),3)
        self.assertTrue(all(geo.d2[a][b]>1 for a,b in combinations(w,2)))
        self.assertFalse(minimum_layer_certificate(geo,rho)['assignments'])

    def test_equilateral_all_blue_face(self):
        geo,rho=fixtures.equilateral_triangle();c=minimum_layer_certificate(geo,rho)
        self.assertEqual(len(c['graph']['triangles']),1)
        self.assertFalse(c['graph']['short_base_triangles'])
        self.assertEqual(geo.maximum_multiplicities(),(2,2,2))

    def test_hexagon_radical_coordinates(self):
        geo,rho=fixtures.regular_hexagon();c=minimum_layer_certificate(geo,rho)
        self.assertEqual(len(c['graph']['unit_edges']),6)
        self.assertFalse(c['graph']['triangles'])
        self.assertEqual(geo.maximum_multiplicities(),(2,2,2,2,2,2))

    def test_semicircle_boundary_equality_rejected(self):
        # Four unit witnesses over a CLOSED semicircle; center lies on the
        # diameter and is not extreme. No strictly short witness pair exists.
        pts=[(0,0),(1,0),(F(1,2),F(1,2)),(F(-1,2),F(1,2)),(-1,0)]
        with self.assertRaises(VerificationError):Geometry.build(pts,3)

    def test_shared_endpoint_not_crossing(self):
        geo,_=fixtures.rank_two_square()
        self.assertFalse(crosses(geo.points,(0,1),(1,2)))

    def test_distinct_close_distances_not_merged(self):
        tiny=F(1,10**20)
        geo=Geometry.build([(0,0),(1,0),(0,1+tiny)])
        self.assertEqual(geo.witnesses(0,F(1)),(1,))
        self.assertEqual(geo.closer_counts([F(1)+tiny,1,1])[0],1)


if __name__=='__main__':unittest.main()
