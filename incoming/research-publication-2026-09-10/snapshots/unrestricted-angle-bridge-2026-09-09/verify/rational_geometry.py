"""Independent exact rational-coordinate verifier; standard library only.

Reconstructs every squared distance, distinctness and all global supporting
inequalities. The cyclic order is supplied but never trusted without checking.
Partial witness rows certify only their named centers, not an all-rich set.
"""
from __future__ import annotations
from fractions import Fraction as F
from itertools import combinations
from collections import defaultdict,Counter
import argparse,json
from pathlib import Path


def inspect(data):
    points=[tuple(map(F,p)) for p in data['coordinates']];n=len(points)
    if n<3 or any(len(p)!=2 for p in points):raise ValueError('invalid point set')
    order=data['cyclic_order']
    if sorted(order)!=list(range(n)):raise ValueError('cyclic order is not a permutation')
    def sub(a,b):return a[0]-b[0],a[1]-b[1]
    def cross(a,b):return a[0]*b[1]-a[1]*b[0]
    def squared(a,b):v=sub(a,b);return v[0]*v[0]+v[1]*v[1]
    distances={}
    for i,j in combinations(range(n),2):
        q=squared(points[i],points[j])
        if q<=0:raise ValueError('coincident points')
        distances[i,j]=q
    supports=[]
    for k,i in enumerate(order):
        j=order[(k+1)%n]
        for v in range(n):
            if v in (i,j):continue
            margin=cross(sub(points[j],points[i]),sub(points[v],points[i]))
            if margin<=0:raise ValueError(f'global support failure: {i},{j},{v}')
            supports.append(margin)
    classes=[]
    for i in range(n):
        groups=defaultdict(list)
        for j in range(n):
            if j!=i:groups[distances[tuple(sorted((i,j)))]].append(j)
        classes.append([{'radius_squared':str(r),'witnesses':w} for r,w in sorted(groups.items())])
    equalities=0
    for center,ws in data.get('witness_rows',{}).items():
        center=int(center)
        if not 0<=center<n or len(ws)<4 or len(set(ws))!=len(ws) or center in ws or any(not isinstance(j,int) or not 0<=j<n for j in ws):raise ValueError('invalid witness row')
        radii=[distances[tuple(sorted((center,j)))] for j in ws]
        if len(set(radii))!=1:raise ValueError('unequal named distances')
        equalities+=len(ws)-1
    maxima=[max(len(g['witnesses']) for g in row) for row in classes]
    return {'n':n,'distinct_pairs_checked':len(distances),'global_supports_checked':len(supports),'minimum_squared_separation':str(min(distances.values())),'minimum_global_support':str(min(supports)),'named_equalities_checked':equalities,'multiplicity_by_center':maxima,'multiplicity_histogram':dict(Counter(maxima)),'good_vertices':[i for i,m in enumerate(maxima) if m<=3],'rich_vertices':[i for i,m in enumerate(maxima) if m>=4],'all_actual_distance_classes':classes,'all_rich':all(m>=4 for m in maxima)}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('file');p.add_argument('--output');a=p.parse_args();r=inspect(json.loads(Path(a.file).read_text()))
    if a.output:Path(a.output).write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({k:v for k,v in r.items() if k!='all_actual_distance_classes'},indent=2))
