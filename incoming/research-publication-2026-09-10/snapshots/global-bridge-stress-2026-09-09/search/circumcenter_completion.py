#!/usr/bin/env python3
"""Exact necessary three-old-witness universe for additions to the new MEC seed.
Every added point with at least three old witnesses must be a circumcenter of
an old triple.  Convex compatibility is checked by the exact monotone hull.
This enumerates candidates, not arbitrary additions with fewer old witnesses.
"""
from __future__ import annotations
import argparse,json,sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'verify'))
from field import Q3,sub,cross,dot,sqdist

def circumcenter(a,b,c):
    u=sub(b,a);v=sub(c,a);det=cross(u,v)
    if det==0:raise ValueError('collinear old triple')
    r=dot(u,u)/2;s=dot(v,v)/2
    return (a[0]+(r*v[1]-s*u[1])/det,a[1]+(u[0]*s-v[0]*r)/det)

def hull(P):
    order=sorted(range(len(P)),key=lambda i:P[i]);lo=[];hi=[]
    for i in order:
        while len(lo)>1 and cross(sub(P[lo[-1]],P[lo[-2]]),sub(P[i],P[lo[-2]]))<=0:lo.pop()
        lo.append(i)
    for i in reversed(order):
        while len(hi)>1 and cross(sub(P[hi[-1]],P[hi[-2]]),sub(P[i],P[hi[-2]]))<=0:hi.pop()
        hi.append(i)
    return lo[:-1]+hi[:-1]

def run(d):
    P=[tuple(Q3.load(v)for v in p)for p in d['coordinates']];n=len(P)
    origins=defaultdict(list)
    for T in combinations(range(n),3):origins[circumcenter(*(P[i]for i in T))].append(list(T))
    rows=[]
    for C,triples in origins.items():
        groups=defaultdict(list)
        for i,p in enumerate(P):groups[sqdist(C,p)].append(i)
        alias=next((i for i,p in enumerate(P)if p==C),None)
        H=hull(P+[C]) if alias is None else []
        rows.append({'coordinates':[x.dump()for x in C],'triples':triples,
                     'alias':alias,'old_classes':[{'radius_squared':r.dump(),'witnesses':v}for r,v in sorted(groups.items())],
                     'hull':H,'convex_compatible':alias is None and len(H)==n+1})
    return {'scope':'complete old-triple circumcenter universe, with exact convex compatibility',
            'old_vertices':n,'triples':sum(len(r['triples'])for r in rows),'distinct_centers':len(rows),
            'new_compatible_centers':sum(r['convex_compatible']for r in rows),'candidates':rows,
            'unrestricted_solution':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    r=run(json.loads(a.input.read_text()));a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items()if k!='candidates'},indent=2))
