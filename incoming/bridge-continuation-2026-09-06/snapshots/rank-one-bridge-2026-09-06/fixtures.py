"""Exact fixtures. Numerical discovery output is not used by the verifier."""
from fractions import Fraction as F
from checker import Geometry, rational, squared


def unit(t):
    t = rational(t)
    return ((1-t*t)/(1+t*t), 2*t/(1+t*t))


def add(a,b):
    return (a[0]+b[0],a[1]+b[1])


def sub(a,b):
    return (a[0]-b[0],a[1]-b[1])


def mul(a,b):
    return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])


def sharp_variable():
    points = [(0,0),(1,0),(F(5,13),F(12,13)),
              (F(-4,5),F(3,5)),(F(-24,25),F(7,25))]
    rho = [F(1),F(16,13),F(16,13),F(1),F(1)]
    return Geometry.build(points),rho


def two_short_pairs():
    points = [(0,0),(F(24,25),F(7,25)),(F(3,5),F(4,5)),
              (F(-3,5),F(4,5)),(F(-24,25),F(7,25))]
    return Geometry.build(points),[F(1)]*5


def long_relative_to_side():
    # Vertex 0 has four unit witnesses and one much closer boundary neighbor.
    points = [(0,0),(F(1,10),F(-1,100)),(1,0),
              (F(5,13),F(12,13)),(F(-4,5),F(3,5)),
              (F(-24,25),F(7,25))]
    geo=Geometry.build(points)
    rho=[max(geo.second_neighbor_options(i)) for i in range(len(points))]
    return geo,rho


def rank_two_pentagon():
    geo,_=two_short_pairs()
    # Actual third-nearest distances; the center's first four distances tie.
    rho=[sorted(d for j,d in enumerate(row) if i!=j)[2]
         for i,row in enumerate(geo.d2)]
    return geo,rho


def rank_two_eight():
    ts=[F(1,10),F(2,3),F(9,10),F(12,5)]
    us=[F(-38,7),F(-7,2),F(-15,4)]
    pts=[(F(0),F(0))]+[unit(t) for t in ts]
    q=4; target=2
    v=sub(pts[target],pts[q])
    pts += [add(pts[q],mul(v,unit(u))) for u in us]
    geo=Geometry.build(pts)
    rho=[F(1)]*8
    rho[q]=squared(pts[q],pts[target])
    return geo,rho


def rank_two_square():
    return Geometry.build([(0,0),(1,0),(1,1),(0,1)]),[F(2)]*4


def three_witnesses_no_short_pair():
    pts=[(0,0),(1,0),(F(5,13),F(12,13)),(F(-4,5),F(3,5))]
    return Geometry.build(pts),[F(1)]*4


def equilateral_triangle():
    # Physical coordinates (x, sqrt(3)*y).
    return Geometry.build([(0,0),(1,0),(F(1,2),F(1,2))],3),[F(1)]*3


def regular_hexagon():
    return Geometry.build([(1,0),(F(1,2),F(1,2)),(F(-1,2),F(1,2)),
                           (-1,0),(F(-1,2),F(-1,2)),(F(1,2),F(-1,2))],3),[F(1)]*6
