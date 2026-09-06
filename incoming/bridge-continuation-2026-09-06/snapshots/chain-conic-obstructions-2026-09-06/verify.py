#!/usr/bin/env python3
"""Exact regressions and symbolic identities for the accompanying proofs.

Finite tests are regression checks, not proofs of the all-real theorems.
The all-real arguments are in proofs.md. Fractions are used for every
point-coordinate, distance-class, hull, and chain test. SymPy is used only
for polynomial identities, exact ranks, and Sturm/root-isolation checks.
"""
from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
from typing import Iterable

Point = tuple[F, F]


def point(x: int | F, y: int | F) -> Point:
    return F(x), F(y)


def sub(a: Point, b: Point) -> Point:
    return a[0]-b[0], a[1]-b[1]


def dot(a: Point, b: Point) -> F:
    return a[0]*b[0]+a[1]*b[1]


def cross(a: Point, b: Point) -> F:
    return a[0]*b[1]-a[1]*b[0]


def orient(a: Point, b: Point, c: Point) -> F:
    return cross(sub(b,a), sub(c,a))


def d2(a: Point, b: Point) -> F:
    z=sub(a,b)
    return dot(z,z)


def maximum_multiplicity(P: list[Point], p: Point) -> int:
    return max(Counter(d2(p,q) for q in P if q != p).values(), default=0)


def hull(P: Iterable[Point]) -> list[Point]:
    Q=sorted(set(P))
    if len(Q)<3:
        return Q
    low: list[Point]=[]
    high: list[Point]=[]
    for q in Q:
        while len(low)>1 and orient(low[-2],low[-1],q)<=0:
            low.pop()
        low.append(q)
    for q in reversed(Q):
        while len(high)>1 and orient(high[-2],high[-1],q)<=0:
            high.pop()
        high.append(q)
    return low[:-1]+high[:-1]


def all_supports(P: list[Point]) -> list[F]:
    H=hull(P)
    assert len(H)==len(P), "not strictly convex"
    out=[]
    for i,a in enumerate(H):
        b=H[(i+1)%len(H)]
        for q in H:
            if q not in (a,b):
                out.append(orient(a,b,q))
    assert not out or min(out)>0
    return out


def subsets(P: list[Point]) -> Iterable[list[Point]]:
    for mask in range(1,1<<len(P)):
        yield [p for i,p in enumerate(P) if (mask>>i)&1]


def rotation_translation(p: Point) -> Point:
    x,y=p
    # An exact Euclidean isometry, not an arbitrary affine transformation.
    return (F(3,5)*x-F(4,5)*y+F(7,3),
            F(4,5)*x+F(3,5)*y-F(2,7))


def graph_minimum_check(P: list[Point]) -> Point:
    P=sorted(P)
    p=min(P,key=lambda p:(p[1],p[0]))
    k=P.index(p)
    left=[d2(p,q) for q in reversed(P[:k])]
    right=[d2(p,q) for q in P[k+1:]]
    assert all(a<b for a,b in zip(left,left[1:]))
    assert all(a<b for a,b in zip(right,right[1:]))
    assert maximum_multiplicity(P,p)<=2
    return p


def circle_parameter(a: F,b: F,t: F) -> Point:
    return a*(1-t*t)/(1+t*t), b*2*t/(1+t*t)


def hyperbola_parameter(a: F,b: F,t: F) -> Point:
    assert t!=0
    return a*(t+1/t)/2, b*(t-1/t)/2


def quartic(t: F) -> F:
    return F(3,5)*t+F(3,10)*t*t-t**3+F(13,10)*t**4


def is_weak_graph_chain(Q: list[Point]) -> bool:
    """For a CCW polygonal subchain of total turn < 2*pi, test span <= pi."""
    if len(Q)<3:
        return True
    E=[sub(b,a) for a,b in zip(Q,Q[1:])]
    return all(cross(E[0],e)>=0 for e in E)


def chain_good_vertex(Q: list[Point]) -> Point:
    assert is_weak_graph_chain(Q)
    if len(Q)<2:
        return Q[0]
    e=sub(Q[1],Q[0]); u=(-e[1],e[0]); v=(-u[1],u[0])
    X=[dot(u,p) for p in Q]; Y=[dot(v,p) for p in Q]
    assert all(a<=b for a,b in zip(X,X[1:]))
    k=min(range(len(Q)),key=lambda k:Y[k]); p=Q[k]
    left=[d2(p,q) for q in reversed(Q[:k])]
    right=[d2(p,q) for q in Q[k+1:]]
    assert all(a<b for a,b in zip(left,left[1:]))
    assert all(a<b for a,b in zip(right,right[1:]))
    assert maximum_multiplicity(Q,p)<=2
    return p


def has_graph_chain(P: list[Point]) -> bool:
    H=hull(P)
    if len(H)!=len(P):
        return False
    return any(is_weak_graph_chain(H[i:]+H[:i]) for i in range(len(H)))


def fraction_string(p: Point) -> list[str]:
    return [str(v) for v in p]


def rational_regressions() -> dict:
    counts=Counter()
    X=[F(i,2) for i in range(-4,5)]
    functions=[lambda x:x*x, quartic,
               lambda x:x**4+F(1,3)*x*x-F(7,4)*x+F(2,5)]
    for fn in functions:
        pool=[(x,fn(x)) for x in X]
        slopes=[(b[1]-a[1])/(b[0]-a[0]) for a,b in zip(pool,pool[1:])]
        assert all(a<b for a,b in zip(slopes,slopes[1:]))
        for P in subsets(pool):
            p=graph_minimum_check(P)
            counts['convex_graph_subsets']+=1
            R=[rotation_translation(q) for q in P]
            assert maximum_multiplicity(R,rotation_translation(p))<=2
            counts['isometric_graph_checks']+=1
            x=point(F(17,11),F(-31,13))
            if x not in P:
                assert maximum_multiplicity(P+[x],p)<=3
                counts['graph_plus_one_checks']+=1

    params=[F(-3),F(-2),F(-1),F(-1,2),F(0),F(1,2),F(1),F(2),F(3)]
    for a,b in [(F(1),F(1)),(F(2),F(1)),(F(5),F(2)),(F(3),F(1)),(F(13),F(12))]:
        pool=[circle_parameter(a,b,t) for t in params]+[(-a,F(0))]
        assert len(set(pool))==len(pool)
        for P in subsets(pool):
            p=max(P,key=lambda q:(abs(q[0]),q[0],q[1]))
            assert maximum_multiplicity(P,p)<=2
            counts['ellipse_subsets']+=1
            R=[rotation_translation(q) for q in P]
            assert maximum_multiplicity(R,rotation_translation(p))<=2
            counts['isometric_ellipse_checks']+=1
            x=point(F(17,11),F(-31,13))
            if x not in P:
                assert maximum_multiplicity(P+[x],p)<=3
                counts['ellipse_plus_one_checks']+=1

    hs=[F(-3),F(-2),F(-1),F(-1,2),F(1,2),F(1),F(2),F(3)]
    for a,b in [(F(1),F(1)),(F(2),F(1)),(F(1),F(2))]:
        pool=[hyperbola_parameter(a,b,t) for t in hs]
        for P in subsets(pool):
            branch=[p for p in P if p[0]>0] or [p for p in P if p[0]<0]
            p=max(branch,key=lambda q:q[1])
            assert maximum_multiplicity(P,p)<=3
            counts['hyperbola_subsets']+=1
            if any(q[0]<0 for q in P) and any(q[0]>0 for q in P):
                counts['hyperbola_subsets_meeting_both_branches']+=1
                if len(hull(P))==len(P):
                    assert len(P)<=4
                    q=min(P,key=lambda q:maximum_multiplicity(P,q))
                    assert maximum_multiplicity(P,q)<=2
                    counts['strictly_convex_both_branch_subsets']+=1
                    z=point(F(17,11),F(-31,13))
                    if z not in P:
                        assert maximum_multiplicity(P+[z],q)<=3
                        counts['strictly_convex_both_branch_plus_one_checks']+=1

    # A union of two lines. Select an endpoint on either occupied line.
    pool=[point(i,0) for i in [-2,-1,0,1,2]]+[point(0,j) for j in [-2,-1,1,2]]
    for P in subsets(pool):
        on_horizontal=[p for p in P if p[1]==0]
        if on_horizontal:
            p=max(on_horizontal,key=lambda q:q[0])
        else:
            p=max(P,key=lambda q:q[1])
        assert maximum_multiplicity(P,p)<=3
        counts['two_line_subsets']+=1

    # Rational hulls, including short chains with vertical end edges.
    import random
    rng=random.Random(97)
    for _ in range(400):
        P=hull(point(rng.randrange(-20,21),rng.randrange(-20,21)) for __ in range(15))
        if len(P)<3:
            continue
        for k in range(2,len(P)+1):
            for j in range(len(P)):
                Q=[P[(j+t)%len(P)] for t in range(k)]
                if is_weak_graph_chain(Q):
                    chain_good_vertex(Q)
                    counts['weak_convex_chain_checks']+=1
        for removed in range(len(P)):
            Q=[P[(removed+1+t)%len(P)] for t in range(len(P)-1)]
            if is_weak_graph_chain(Q):
                p=chain_good_vertex(Q)
                assert maximum_multiplicity(P,p)<=3
                counts['triple_turn_certificates']+=1
    return dict(counts)


def exact_controls() -> dict:
    ellipse=[point(0,0),point(F(3,5),F(4,5)),point(F(3,5),F(-4,5)),
             point(F(5,13),F(12,13)),point(F(5,13),F(-12,13))]
    assert all(80*x*x+15*y*y-64*x==0 for x,y in ellipse)
    assert all(d2(ellipse[0],q)==1 for q in ellipse[1:])
    supp=all_supports(ellipse)
    em=[maximum_multiplicity(ellipse,p) for p in ellipse]
    assert em[0]==4
    assert maximum_multiplicity(ellipse,ellipse[3])<=2

    hyperbola=[point(0,0),point(F(9,41),F(-40,41)),point(F(3,5),F(4,5)),
               point(F(5,13),F(12,13)),point(F(7,25),F(24,25))]
    assert all(192*x*x+220*x*y+57*y*y-288*x-48*y==0 for x,y in hyperbola)
    assert all(d2(hyperbola[0],q)==1 for q in hyperbola[1:])
    hsupp=all_supports(hyperbola)
    hm=[maximum_multiplicity(hyperbola,p) for p in hyperbola]
    assert hm[0]==4

    plus_one=[point(2,0),point(0,1),point(0,-1),point(1,2)]
    assert all(x*x/4+y*y==1 for x,y in plus_one[:3])
    assert plus_one[3][0]**2/4+plus_one[3][1]**2!=1
    assert all(d2(plus_one[0],q)==5 for q in plus_one[1:])
    all_supports(plus_one)
    assert maximum_multiplicity(plus_one,plus_one[0])==3

    # This polygon is NOT a counterexample. It refutes an unrestricted
    # geometric reduction to either of the two '+ one point' families.
    escape=[point(5,0),point(3,4),point(0,F(51,10)),point(-3,4),
            point(-5,0),point(-3,F(-41,10)),point(0,-5),point(3,-4)]
    all_supports(escape)
    H=hull(escape)
    E=[sub(H[(i+1)%8],H[i]) for i in range(8)]
    signs=[cross(E[(i+1)%8],E[(i-2)%8]) for i in range(8)]
    assert all(t<0 for t in signs)
    for i in range(8):
        assert not has_graph_chain(escape[:i]+escape[i+1:])
    return {
        'ellipse_four_rich_control':{
            'points':[fraction_string(p) for p in ellipse],
            'conic_coefficients_x2_xy_y2_x_y_1':[80,0,15,-64,0,0],
            'maximum_multiplicities':em,
            'support_determinants_checked':len(supp),
            'minimum_support_determinant':str(min(supp)),
        },
        'hyperbola_four_rich_control':{
            'points':[fraction_string(p) for p in hyperbola],
            'conic_coefficients_x2_xy_y2_x_y_1':[192,220,57,-288,-48,0],
            'quadratic_discriminant':220**2-4*192*57,
            'maximum_multiplicities':hm,
            'support_determinants_checked':len(hsupp),
            'minimum_support_determinant':str(min(hsupp)),
        },
        'ellipse_plus_one_sharpness':{
            'points':[fraction_string(p) for p in plus_one],
            'selected_center_index':0,'selected_squared_radius':'5',
            'maximum_multiplicity_at_selected_center':3,
        },
        'nonconic_nonchain_bridge_control':{
            'points':[fraction_string(p) for p in escape],
            'maximum_multiplicities':[maximum_multiplicity(escape,p) for p in escape],
            'turn_test_cross_products':[str(t) for t in signs],
            'one_point_deletions_tested_for_graph_chain':8,
            'graph_chain_deletion_survivors':0,
            'status':'NOT_A_COUNTEREXAMPLE_TO_ERDOS97',
        }
    }


def symbolic_checks(controls: dict) -> dict:
    import sympy as s
    a,b,u,v,c,x,t,tau=s.symbols('a b u v c x t tau',real=True)
    alpha=1-b*b/(a*a)
    poly=s.Poly(s.expand((alpha*x*x-2*u*x+c)**2+4*b*b*v*v*x*x/(a*a)-4*b*b*v*v),x)
    assert s.simplify(-poly.nth(3)/poly.nth(4)-4*u/alpha)==0

    h1,h2,h3=s.symbols('h1 h2 h3',nonzero=True)
    def hp(h):
        return s.Matrix([a*(h+1/h)/2,b*(h-1/h)/2])
    hdet=s.det(s.Matrix.hstack(hp(h2)-hp(h1),hp(h3)-hp(h1)))
    hexact=-a*b*(h2-h1)*(h3-h1)*(h3-h2)/(2*h1*h2*h3)
    assert s.factor(hdet-hexact)==0

    D=a*a*(s.cos(t)-s.cos(tau))**2+b*b*(s.sin(t)-s.sin(tau))**2
    G=(b*b-a*a)*s.sin(t)*s.cos(t)+a*a*s.cos(tau)*s.sin(t)-b*b*s.sin(tau)*s.cos(t)
    assert s.trigsimp(s.diff(D,t)/2-G)==0
    z=s.symbols('z',real=True)
    B=b*b*s.sin(tau)-(a*a-b*b)*s.sin(z)-a*a*s.cos(tau)*s.tan(z)
    assert s.trigsimp(G.subs(t,s.pi+z)-s.cos(z)*B)==0
    assert s.trigsimp(s.diff(B,z)+(a*a-b*b)*s.cos(z)+a*a*s.cos(tau)/s.cos(z)**2)==0

    g=s.Rational(3,5)*t+s.Rational(3,10)*t*t-t**3+s.Rational(13,10)*t**4
    gpp=s.Poly(s.diff(g,t,2),t)
    assert gpp.LC()>0 and s.discriminant(gpp,t)==-s.Rational(36,25)
    f=s.Poly(s.expand(100*((t+1)**2+(g-2)**2-5)),t)
    assert f==s.Poly(169*t**8-260*t**7+178*t**6+96*t**5-631*t**4+436*t**3+16*t*t-40*t,t)
    assert f.count_roots(-1,1)==4
    assert f.count_roots(-s.Rational(3,10),-s.Rational(1,4))==1
    assert f.eval(0)==0
    assert f.count_roots(s.Rational(2,5),s.Rational(1,2))==1
    assert f.count_roots(s.Rational(7,10),s.Rational(4,5))==1

    P=[tuple(s.Rational(x) for x in p) for p in controls['nonconic_nonchain_bridge_control']['points']]
    ranks=[]
    for i in range(len(P)):
        Q=P[:i]+P[i+1:]
        M=s.Matrix([[x*x,x*y,y*y,x,y,1]for x,y in Q])
        ranks.append(M.rank())
    assert ranks==[6]*8
    controls['nonconic_nonchain_bridge_control']['conic_evaluation_ranks_after_each_deletion']=ranks

    return {
        'ellipse_vieta_identity':'PASS',
        'hyperbola_orientation_determinant_identity':'PASS',
        'ellipse_distance_derivative_identity':'PASS',
        'ellipse_third_quadrant_factorization':'PASS',
        'ellipse_third_quadrant_bracket_derivative':'PASS',
        'quartic_second_derivative_discriminant':'-36/25',
        'quartic_distance_fiber_identity':'PASS',
        'quartic_distinct_roots_in_minus1_plus1':4,
        'quartic_isolating_intervals':['(-3/10,-1/4)','{0}','(2/5,1/2)','(7/10,4/5)'],
        'bridge_control_no_conic_plus_one':'PASS',
        'sympy_version':s.__version__,
    }


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--skip-symbolic',action='store_true')
    args=parser.parse_args()
    controls=exact_controls()
    report={
        'status':'EXACT_REGRESSIONS_PASS_NOT_A_PROOF_OF_UNRESTRICTED_ERDOS97',
        'claim_scope':'Paper proofs of restricted all-size obstructions; no general solution claimed.',
        'rational_regressions':rational_regressions(),
        'controls':controls,
    }
    if not args.skip_symbolic:
        report['symbolic_checks']=symbolic_checks(controls)
    else:
        report['symbolic_checks']='SKIPPED'
    text=json.dumps(report,indent=2,sort_keys=True)+'\n'
    if args.output:
        args.output.write_text(text)
    print(text,end='')

if __name__=='__main__':
    main()
