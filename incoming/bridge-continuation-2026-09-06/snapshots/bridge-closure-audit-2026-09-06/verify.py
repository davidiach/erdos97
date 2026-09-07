#!/usr/bin/env python3
"""Exact audit of three proposed bridge steps for Erdős #97.

Standard library only. This does NOT prove or refute Erdős #97.
The closed diameter-disk convention is deliberate: boundary blockers count.
Coordinates (x,y) with metric_scale=s stand for (x, sqrt(s)*y).
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from fractions import Fraction as F
from itertools import combinations
import json
from pathlib import Path
from typing import Iterable

Point = tuple[F, F]

def rational(x: object) -> F:
    if isinstance(x, bool) or not isinstance(x, (int, str, F)):
        raise TypeError('Only exact integers, rational strings, and Fraction inputs are accepted')
    return F(x)

def unit(t: F) -> Point:
    t = rational(t)
    return ((1-t*t)/(1+t*t), 2*t/(1+t*t))

def multiply(a: Point, b: Point) -> Point:
    return (a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0])

def orient(a: Point, b: Point, c: Point) -> F:
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])

class Geometry:
    def __init__(self, points: Iterable[tuple[object, object]], metric_scale: object = 1):
        self.points = tuple((rational(x), rational(y)) for x,y in points)
        self.n = len(self.points)
        self.scale = rational(metric_scale)
        if self.n < 3 or self.scale <= 0 or len(set(self.points)) != self.n:
            raise ValueError('Need at least three distinct points and positive metric scale')
        ids = sorted(range(self.n), key=lambda i:self.points[i])
        def chain(js):
            out=[]
            for j in js:
                while len(out)>=2 and orient(self.points[out[-2]],self.points[out[-1]],self.points[j])<=0:
                    out.pop()
                out.append(j)
            return out
        self.order=tuple(chain(ids)[:-1]+chain(ids[::-1])[:-1])
        if len(self.order)!=self.n:
            raise ValueError('Points are not in strictly convex position')
        self.pos={j:i for i,j in enumerate(self.order)}
        self.supports=[]
        for a,b in zip(self.order,self.order[1:]+self.order[:1]):
            for j in range(self.n):
                if j not in (a,b):
                    val=orient(self.points[a],self.points[b],self.points[j])
                    if val<=0:raise ValueError('A supporting-line inequality failed')
                    self.supports.append(val)
        self.d2=tuple(tuple((a[0]-b[0])**2+self.scale*(a[1]-b[1])**2 for b in self.points) for a in self.points)
    def blockers(self,a:int,b:int)->tuple[int,...]:
        return tuple(z for z in range(self.n) if z not in (a,b) and self.d2[a][z]+self.d2[z][b]<=self.d2[a][b])
    def gabriel(self)->tuple[tuple[int,int],...]:
        return tuple((a,b) for a,b in combinations(range(self.n),2) if not self.blockers(a,b))
    def rows(self,radii2:Iterable[object])->dict:
        rr=tuple(rational(x)for x in radii2)
        if len(rr)!=self.n or any(x<=0 for x in rr):raise ValueError('Invalid radius vector')
        return {'radii_squared':rr,
                'closer':tuple(tuple(j for j in range(self.n) if j!=i and self.d2[i][j]<rr[i])for i in range(self.n)),
                'witnesses':tuple(tuple(j for j in range(self.n) if j!=i and self.d2[i][j]==rr[i])for i in range(self.n))}
    def third_nearest(self)->tuple[F,...]:
        if self.n<4:raise ValueError('Third nearest requires at least four points')
        return tuple(sorted(self.d2[i][j]for j in range(self.n)if j!=i)[2]for i in range(self.n))
    def multiplicities(self)->tuple[int,...]:
        return tuple(max(Counter(self.d2[i][j]for j in range(self.n)if j!=i).values())for i in range(self.n))

def fan_control(m:int=12)->tuple[Geometry,tuple[F,...]]:
    if m<2:raise ValueError('m must be at least two')
    w=unit(F(1,40));q=[(F(1),F(0))]
    for _ in range(m-1):q.append(multiply(q[-1],w))
    a=tuple(x/5 for x in unit(-F(1,4)))
    b=tuple(x/5 for x in multiply(q[-1],unit(F(1,4))))
    g=Geometry([(0,0),a,*q,b])
    return g,(F(1),F(1,25),*((g.d2[2][3],)*m),F(1,25))

def ear_control()->Geometry:
    p=[(F(0),F(0)),(F(1,100),-F(1,2000)),(-F(3,400),F(7,1000)),(F(1),F(0)),unit(F(23,22)),unit(F(153,100)),unit(F(7,3))]
    p += [(1+x,y)for x,y in (unit(F(3,200)),unit(F(2,125)),unit(F(17,1000)))]
    return Geometry(p)

def middle_cycle_control()->Geometry:
    return Geometry([(0,0),(1,0),(F(1,2),F(1,2)),(F(397,403),-F(40,403)),(F(529,806),F(437,806)),(-F(57,403),F(23,403))],3)

def circumcircle(a:Point,b:Point,c:Point)->tuple[Point,F]:
    u=(2*(b[0]-a[0]),2*(b[1]-a[1]));v=(2*(c[0]-a[0]),2*(c[1]-a[1]))
    ub=b[0]**2+b[1]**2-a[0]**2-a[1]**2
    vb=c[0]**2+c[1]**2-a[0]**2-a[1]**2
    det=u[0]*v[1]-u[1]*v[0]
    if not det:raise ValueError('Collinear triple')
    center=((ub*v[1]-u[1]*vb)/det,(u[0]*vb-ub*v[0])/det)
    return center,(center[0]-a[0])**2+(center[1]-a[1])**2

def has_cycle(n:int,edges:Iterable[tuple[int,int]])->bool:
    par=list(range(n))
    def root(x):
        while par[x]!=x:x=par[x]
        return x
    for i,j in edges:
        a,b=root(i),root(j)
        if a==b:return True
        par[a]=b
    return False

def describe(g:Geometry,radii2:Iterable[object])->dict:
    rows=g.rows(radii2);edges=g.gabriel()
    return {'points':g.points,'metric_scale':g.scale,'counterclockwise_order':g.order,
            'supporting_line_checks':len(g.supports),'minimum_support_determinant_in_stored_coordinates':min(g.supports),
            'maximum_multiplicities':g.multiplicities(),'gabriel_edges':edges,
            'gabriel_degrees':tuple(sum(i in e for e in edges)for i in range(g.n)),
            **rows,'incidence_count':sum(map(len,rows['witnesses']))}

def fixed_radius_audit(g:Geometry)->dict:
    edges=g.gabriel();deg=[sum(i in e for e in edges)for i in range(g.n)]
    # Exact combinatorial noncrossing check in inherited cyclic order.
    def inside(a,b,x):return 0<(g.pos[x]-g.pos[a])%g.n<(g.pos[b]-g.pos[a])%g.n
    for e,f in combinations(edges,2):
        if len(set(e+f))==4 and inside(*e,f[0])!=inside(*e,f[1]) and inside(*f,e[0])!=inside(*f,e[1]):
            raise AssertionError('Gabriel edges cross')
    local=global_=0
    for r2 in sorted({g.d2[a][b]for a,b in combinations(range(g.n),2)}):
        row=g.rows([r2]*g.n);b=list(map(len,row['closer']));k=list(map(len,row['witnesses']))
        for i in range(g.n):
            if b[i]<=2 and all(b[z]<=2 for z in row['closer'][i]):
                assert deg[i]>=k[i]
                local+=1
        if max(b)<=2:
            assert sum(k)//2<=len(edges)<=2*g.n-3
            global_+=1
    descent=0
    if g.n>=4:
        rr=g.third_nearest();rows=g.rows(rr)
        for i in range(g.n):
            if len(rows['witnesses'][i])>=4 and deg[i]<=3:
                assert any(rr[z]<rr[i] for z in rows['closer'][i])
                descent+=1
    return {'local_degree_lifting_checks':local,'global_fixed_radius_checks':global_,
            'low_degree_rich_vertex_descent_checks':descent}

def regression_geometries():
    ts=[F(-3),F(-2),F(-1),F(-1,2),F(0),F(1,2),F(1),F(2),F(3)]
    circle=[unit(t)for t in ts]
    # Bounded regression, not an exhaustive statement about arbitrary polygons.
    for a in (F(1,2),F(1),F(2)):
        p=[(a*x,y)for x,y in circle]
        for size in (3,4,5):
            for ids in combinations(range(len(p)),size):
                yield Geometry([p[i]for i in ids])
    yield middle_cycle_control()
    yield ear_control()
    yield fan_control()[0]

def build_report()->dict:
    gf,rf=fan_control();fan=describe(gf,rf)
    assert gf.n==15 and fan['incidence_count']==36 and len(fan['gabriel_edges'])==16
    assert max(map(len,fan['closer']))==2 and len(fan['witnesses'][0])==12
    assert fan['incidence_count']>2*len(fan['gabriel_edges'])
    assert all(row for row in fan['witnesses'])
    ge=ear_control();re=ge.third_nearest();ear=describe(ge,re)
    assert ear['maximum_multiplicities']==(4,1,1,4,1,1,1,1,1,1)
    assert max(map(len,ear['closer']))==2 and ear['gabriel_degrees'][0]==2
    assert ear['witnesses'][0]==(3,4,5,6) and ear['witnesses'][3]==(0,7,8,9)
    circle,r2=circumcircle(*(ge.points[i]for i in (0,1,2)))
    powers=tuple((ge.points[i][0]-circle[0])**2+(ge.points[i][1]-circle[1])**2-r2 for i in range(3,ge.n))
    assert min(powers)>0
    assert circle==(F(1207,212000),F(2887,212000)) and r2==F(4895809,22472000000)
    assert min(powers)==F(104510671,107378000)
    pos=ge.pos[0];assert {ge.order[(pos-1)%ge.n],ge.order[(pos+1)%ge.n]}=={1,2}
    deleted=Geometry(ge.points[1:]);assert deleted.multiplicities()==(1,1,3,1,1,1,1,1,1)
    ear.update({'empty_ear_triangle':(0,1,2),'circumcenter':circle,'circumradius_squared':r2,
                'other_vertex_circle_powers':powers,'deleted_original_labels':(0,),
                'remaining_original_labels':tuple(range(1,10)),
                'multiplicities_after_deletion':deleted.multiplicities()})
    gm=middle_cycle_control();middle=describe(gm,[F(1)]*gm.n)
    assert middle['maximum_multiplicities']==(3,3,3,2,2,2)
    assert max(map(len,middle['closer']))==1
    directed=[]
    for i,ws in enumerate(middle['witnesses']):
        if len(ws)>=3:
            s=sorted(ws,key=lambda j:(gm.pos[j]-gm.pos[i])%gm.n)
            directed += [(i,j)for j in s[1:-1]]
    undirected=sorted({tuple(sorted(e))for e in directed})
    assert directed==[(0,1),(1,2),(2,0)] and has_cycle(gm.n,undirected)
    middle.update({'middle_directed_edges':directed,'middle_undirected_edges':undirected,
                   'all_centers_four_rich':False})
    totals=Counter()
    for g in regression_geometries():
        totals.update(fixed_radius_audit(g));totals['geometry_instances']+=1
    return {'status':'NO_PROOF_OR_COUNTEREXAMPLE_TO_ERDOS_97',
            'paper_result':'Simpler proof of previously established fixed-radius bound; no scope extension',
            'controls':{'variable_radius_gabriel_capacity_failure':fan,'rich_delaunay_ear_deletion_failure':ear,
                        'three_witness_middle_cycle':middle},'regression':dict(totals),
            'limitations':['None of the controls has every vertex four-rich.',
                           'The six-point middle cycle uses three-witness rows, not four-witness rows.',
                           'Finite regression is not an arbitrary-size proof.',
                           'No independent mathematical review or full formalization is claimed.']}

def encode(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,dict):return {str(k):encode(v)for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [encode(v)for v in x]
    return x

def main()->None:
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--write',action='store_true');group.add_argument('--check',action='store_true')
    args=parser.parse_args();report=encode(build_report())
    path=Path(__file__).with_name('verification.json')
    if args.write:
        path.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
        print('Wrote exact report:',path.name)
    else:
        if json.loads(path.read_text())!=report:raise SystemExit('Report differs from fresh exact calculation')
        print('Exact report reproduced. Erdős #97 remains unsolved in this packet.')
    print(json.dumps(report['regression'],sort_keys=True))

if __name__=='__main__':main()
