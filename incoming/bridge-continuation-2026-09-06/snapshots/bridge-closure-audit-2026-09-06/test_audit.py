import unittest
from fractions import Fraction as F
from verify import (Geometry, unit, multiply, fan_control, ear_control, middle_cycle_control,
                    circumcircle, fixed_radius_audit, has_cycle)

class AuditTests(unittest.TestCase):
    def test_floats_rejected(self):
        with self.assertRaises(TypeError): Geometry([(0,0),(1.0,0),(0,1)])
    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError): Geometry([(0,0),(1,0),(0,0)])
    def test_collinear_rejected(self):
        with self.assertRaises(ValueError): Geometry([(0,0),(1,0),(2,0)])
    def test_interior_rejected(self):
        with self.assertRaises(ValueError): Geometry([(0,0),(3,0),(0,3),(1,1)])
    def test_invalid_scale_rejected(self):
        with self.assertRaises(ValueError): Geometry([(0,0),(1,0),(0,1)],-1)
    def test_invalid_radius_rejected(self):
        g=Geometry([(0,0),(1,0),(0,1)])
        for rr in ([1,1],[1,1,0],[-1,1,1]):
            with self.assertRaises(ValueError):g.rows(rr)
    def test_closed_disk_square_boundary(self):
        g=Geometry([(0,0),(1,0),(1,1),(0,1)])
        self.assertEqual(g.blockers(0,2),(1,3))
        self.assertEqual(g.blockers(1,3),(0,2))
        self.assertEqual(len(g.gabriel()),4)
        fixed_radius_audit(g)
    def test_unit_rhombus_sharpness(self):
        g=Geometry([(0,0),(1,0),(F(3,2),F(1,2)),(F(1,2),F(1,2))],3)
        row=g.rows([1]*4)
        self.assertEqual(sum(map(len,row['witnesses']))//2,2*g.n-3)
        self.assertTrue(all(not x for x in row['closer']))
        fixed_radius_audit(g)
    def test_rational_rotations(self):
        a=unit(F(1,40));b=(F(1),F(0))
        for _ in range(12):
            self.assertEqual(b[0]**2+b[1]**2,1)
            b=multiply(a,b)
    def test_fan_capacity_failure(self):
        g,r=fan_control();row=g.rows(r)
        self.assertEqual(sum(map(len,row['witnesses'])),36)
        self.assertEqual(len(g.gabriel()),16)
        self.assertTrue(all(len(s)<=2 for s in row['closer']))
        self.assertTrue(all(s for s in row['witnesses']))
        self.assertGreater(36,2*len(g.gabriel()))
    def test_fan_not_full_counterexample(self):
        g,r=fan_control()
        self.assertEqual(g.multiplicities()[0],12)
        self.assertTrue(any(k<4 for k in g.multiplicities()))
    def test_ear_delaunay_certificate(self):
        g=ear_control();c,r=circumcircle(*(g.points[i]for i in(0,1,2)))
        self.assertEqual(c,(F(1207,212000),F(2887,212000)))
        self.assertEqual(r,F(4895809,22472000000))
        powers=[(x-c[0])**2+(y-c[1])**2-r for x,y in g.points[3:]]
        self.assertGreater(min(powers),0)
    def test_ear_deletion_loses_richness(self):
        g=ear_control();after=Geometry(g.points[1:])
        self.assertEqual(g.multiplicities()[3],4)
        self.assertEqual(after.multiplicities()[2],3)
    def test_lifting_hypothesis_not_silently_removed(self):
        g=ear_control();row=g.rows([1]*g.n)
        self.assertEqual(len(row['closer'][0]),2)
        self.assertGreater(max(len(row['closer'][z])for z in row['closer'][0]),2)
        self.assertEqual(sum(0 in e for e in g.gabriel()),2)
        self.assertEqual(len(row['witnesses'][0]),4)
    def test_middle_cycle_scope(self):
        g=middle_cycle_control();row=g.rows([1]*g.n)
        self.assertTrue(all(len(s)<=1 for s in row['closer']))
        self.assertEqual(g.multiplicities(),(3,3,3,2,2,2))
        self.assertTrue(has_cycle(6,[(0,1),(1,2),(0,2)]))
    def test_cycle_detector_tree(self):
        self.assertFalse(has_cycle(6,[(0,1),(1,2),(2,3),(3,4),(4,5)]))
    def test_collinear_circle_rejected(self):
        with self.assertRaises(ValueError):circumcircle((F(0),F(0)),(F(1),F(0)),(F(2),F(0)))

if __name__=='__main__':unittest.main()
