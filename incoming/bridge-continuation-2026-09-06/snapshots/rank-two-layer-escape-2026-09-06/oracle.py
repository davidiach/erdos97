#!/usr/bin/env python3
"""Second-representation exact checks of the stored named controls.

This file does NOT import geometry.py, fixtures.py, or verify.py. It checks
squared lengths, signed-area crossings, closed-disk blockers by dot products,
component counts, assigned rows, minimum-layer exports, and the return profile.
It is not independent external review or an arbitrary-real formal proof.
"""
from collections import Counter
from fractions import Fraction as F
from itertools import combinations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent


def ensure(x,msg):
    if not x: raise ValueError(msg)


def run():
    counts=Counter()
    for item in json.loads((ROOT/'exact_controls.json').read_text()):
        if 'points' not in item: continue
        pts=[tuple(F(x) for x in p) for p in item['points']]; n=len(pts)
        scale=F(item.get('vertical_scale_squared',1)); order=item['cyclic_order']
        ensure(len(set(pts))==n and sorted(order)==list(range(n)),'Point/order mismatch.')
        def dot(u,v): return u[0]*v[0]+scale*u[1]*v[1]
        def diff(i,j): return tuple(pts[i][k]-pts[j][k] for k in (0,1))
        def orient(i,j,k):
            u,v=diff(j,i),diff(k,i); return u[0]*v[1]-u[1]*v[0]
        ds={(i,j):dot(diff(i,j),diff(i,j)) for i in range(n) for j in range(n)}
        counts['point_pairs']+=n*(n-1)//2
        for a,b in zip(order,order[1:]+order[:1]):
            if n<3: continue
            for k in range(n):
                if k not in (a,b):
                    ensure(orient(a,b,k)>0,'Supporting line failed.')
                    counts['supporting_line_checks']+=1
        maximum=[max(Counter(ds[i,j] for j in range(n) if i!=j).values(),default=0) for i in range(n)]
        ensure(maximum==item['all_radius_maximum_multiplicities'],'All-radius profile mismatch.')
        counts['geometric_controls']+=1
        for cert in item.get('threshold_certificates',[]):
            r=F(cert['radius_squared'])
            short={e for e in combinations(range(n),2) if ds[e]<r}
            equal={e for e in combinations(range(n),2) if ds[e]==r}
            adj=[set() for _ in pts]
            for a,b in short: adj[a].add(b);adj[b].add(a)
            ensure(max(map(len,adj),default=0)<=2,'Short degree too high.')
            done=set();paths=cycles=0
            for root in range(n):
                if root in done: continue
                stack=[root];vertices=set()
                while stack:
                    v=stack.pop()
                    if v in vertices: continue
                    vertices.add(v);stack.extend(adj[v]-vertices)
                done |= vertices
                if len(vertices)>1:
                    if all(len(adj[v])==2 for v in vertices): cycles+=1
                    else: paths+=1
            ensure(paths==cert['nontrivial_short_paths'] and cycles==cert['short_cycles'],'Component mismatch.')
            bound=0 if n==1 else 2*n-3-paths-2*cycles
            ensure(len(equal)<=bound and bound==cert['unit_edge_bound'],'Edge bound failed.')
            def crosses(e,f):
                if len(set(e+f))<4:return False
                a,b=e;c,d=f
                return orient(a,b,c)*orient(a,b,d)<0 and orient(c,d,a)*orient(c,d,b)<0
            ensure(not any(crosses(a,b) for a,b in combinations(short,2)),'Short crossing.')
            gab=set()
            for a,b in short|equal:
                blockers=[k for k in range(n) if k not in (a,b) and dot(diff(k,a),diff(k,b))<=0]
                if not blockers:gab.add((a,b))
            ensure(gab=={tuple(e) for e in cert['strict_gabriel_edges']},'Disk blocker mismatch.')
            ensure(not any(crosses(a,b) for a,b in combinations(gab,2)),'Gabriel crossing.')
            counts['fixed_radius_certificates']+=1
        if 'radii_squared' in item:
            radii=list(map(F,item['radii_squared']))
            shorter=[[j for j in range(n) if j!=i and ds[i,j]<radii[i]] for i in range(n)]
            witnesses=[[j for j in range(n) if j!=i and ds[i,j]==radii[i]] for i in range(n)]
            ensure(max(map(len,shorter))<=2,'Too many strictly closer points.')
            ensure(shorter==item['assigned_rows']['closer'] and witnesses==item['assigned_rows']['witnesses'],'Assigned rows mismatch.')
            ensure(all(sorted(ds[i,j] for j in range(n) if i!=j)[2]==radii[i] for i in range(n)), 'Third-nearest mismatch.')
            r=min(radii);layer=[i for i in range(n) if radii[i]==r]
            ensure(all(len(witnesses[i])>=4 for i in layer),'Expected all-rich minimum layer.')
            exported={(i,j) for i in layer for j in witnesses[i] if j not in layer}
            targets={j for i,j in exported}
            ensure(len(targets)>=4 and all(r<radii[j]<4*r for j in targets),'Escape band failed.')
            if len(layer)>=2:ensure(len(exported)>=6,'Six-export bound failed.')
            counts['assigned_radius_controls']+=1
        if item['name']=='nine_point_rational_return':
            after=[max(Counter(ds[i,j] for j in range(1,n) if i!=j).values(),default=0) for i in range(1,n)]
            ensure(after==[1,1,1,1,3,1,1,1],'Return deletion mismatch.')
            ensure(maximum[5]==4 and after[4]==3,'Wrong returning vertex.')
            counts['all_radius_deletion_controls']+=1
    return {'result':'PASS','scope':'Second representation on stored named controls only.',
            'counts':dict(sorted(counts.items()))}

if __name__=='__main__':
    print(json.dumps(run(),indent=2))
