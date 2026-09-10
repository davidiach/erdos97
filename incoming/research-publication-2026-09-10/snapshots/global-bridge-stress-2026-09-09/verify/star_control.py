#!/usr/bin/env python3
"""Independent exact global geometry and complete actual-rich-radius audit."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from collections import defaultdict,Counter
from itertools import combinations
from field import Q3,sub,cross,sqdist

def verify(d):
    P=[tuple(Q3.load(c) for c in p)for p in d['coordinates']];n=len(P);order=d['cyclic_order']
    if n<3 or any(len(p)!=2 for p in P)or sorted(order)!=list(range(n)):raise ValueError('invalid point set or order')
    D={}
    for i,j in combinations(range(n),2):
        z=sqdist(P[i],P[j])
        if z<=0:raise ValueError('points are not distinct')
        D[i,j]=z
    margins=[]
    for a,b in zip(order,order[1:]+order[:1]):
        for c in range(n):
            if c in [a,b]:continue
            z=cross(sub(P[b],P[a]),sub(P[c],P[a]))
            if z<=0:raise ValueError(f'global support failure {(a,b,c)}')
            margins.append(z)
    actual=[];rich={};mx=[]
    for i in range(n):
        C=defaultdict(list)
        for j in range(n):
            if j!=i:C[D[tuple(sorted((i,j)))]].append(j)
        actual.append([{'radius_squared':r.dump(),'witnesses':w}for r,w in sorted(C.items())])
        rich[i]=[r for r,w in C.items() if len(w)>=4];mx.append(max(map(len,C.values())))
    rows={int(i):W for i,W in d['witness_rows'].items()}
    for i,W in rows.items():
        if i not in range(n)or i in W or len(W)<4 or len(W)!=len(set(W))or any(j not in range(n)for j in W):raise ValueError('invalid witness row')
        r=Q3.load(d['witness_radius_squared'][str(i)])
        if r<=0 or any(D[tuple(sorted((i,j)))]!=r for j in W):raise ValueError('false named equality')
    root=d['root'];W=d['root_witnesses']
    if root not in rows or set(W)!=set(rows[root]):raise ValueError('root witnesses not verified')
    R=Q3.load(d['witness_radius_squared'][str(root)])
    if any(not rich[j] or min(rich[j])>R for j in W):raise ValueError('not every root witness has a nonlarger rich radius')
    if max(r for vals in rich.values() for r in vals)!=R:raise ValueError('root radius is not the global maximum actual rich radius')
    if all(rich.values()):raise ValueError('unexpected all-rich candidate: requires separate review')
    return {'status':'PASS_EXACT_NONINCREASING_STAR_CONTROL','n':n,'distinct_pairs':len(D),'global_supports':len(margins),
            'minimum_support':min(margins).dump(),'multiplicity_by_center':mx,'histogram':dict(Counter(mx)),
            'rich_vertices':[i for i,v in rich.items()if v],'good_vertices':[i for i,v in rich.items()if not v],
            'all_actual_distance_classes':actual,'actual_rich_radii_squared':{i:[r.dump()for r in v]for i,v in rich.items()if v},
            'root_radius_is_maximum_actual_rich_radius':True,'every_root_witness_rich_at_nonlarger_radius':True,
            'unrestricted_solution':False,'independent_external_review':False}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    r=verify(json.loads(a.input.read_text()));a.output.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({k:v for k,v in r.items()if k!='all_actual_distance_classes'},indent=2))
