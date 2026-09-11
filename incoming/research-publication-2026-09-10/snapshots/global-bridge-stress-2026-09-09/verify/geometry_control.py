"""Reconstruct all field distances and every support sign. No search imports."""
import json,argparse
from pathlib import Path
from itertools import combinations
from collections import defaultdict,Counter
from field import Q3,dot,sub,cross,sqdist

def verify(d):
    points=[tuple(Q3.load(x)for x in p)for p in d['coordinates']];n=len(points)
    if n<3 or any(len(p)!=2 for p in points):raise ValueError('invalid coordinates')
    order=d['cyclic_order']
    if sorted(order)!=list(range(n)):raise ValueError('invalid cyclic order')
    ds={}
    for i,j in combinations(range(n),2):
        x=sqdist(points[i],points[j])
        if x<=0:raise ValueError('coincident points')
        ds[i,j]=x
    margins=[]
    for k,i in enumerate(order):
        j=order[(k+1)%n]
        for v in range(n):
            if v not in (i,j):
                m=cross(sub(points[j],points[i]),sub(points[v],points[i]))
                if m<=0:raise ValueError(f'global support failed at {i},{j},{v}')
                margins.append(m)
    classes=[];mx=[]
    for i in range(n):
        g=defaultdict(list)
        for j in range(n):
            if i!=j:g[ds[tuple(sorted((i,j)))]].append(j)
        classes.append([{'radius_squared':r.dump(),'witnesses':w}for r,w in sorted(g.items())]);mx.append(max(map(len,g.values())))
    for p,ws in d['witness_rows'].items():
        p=int(p)
        if p not in range(n)or len(ws)<4 or len(ws)!=len(set(ws))or p in ws or any(w not in range(n)for w in ws):raise ValueError('invalid named witnesses')
        vals=[ds[tuple(sorted((p,w)))]for w in ws]
        if any(v!=vals[0]for v in vals):raise ValueError('false distance equality')
        if vals[0]!=Q3.load(d['witness_radius_squared'][str(p)]):raise ValueError('false named radius')
    center=tuple(Q3.load(x)for x in d['mec_center']);radius=Q3.load(d['mec_radius_squared'])
    norm=[sqdist(p,center)for p in points]
    if radius<=0 or any(x>radius for x in norm):raise ValueError('not an enclosing disk')
    supp=d['mec_support']
    if len(supp)!=3 or len(set(supp))!=3 or any(k not in range(n)for k in supp):raise ValueError('invalid support triple')
    if [i for i,v in enumerate(norm)if v==radius]!=sorted(supp):raise ValueError('wrong disk boundary support')
    if any(sum(points[k][j]-center[j]for k in supp)!=0 for j in [0,1]):raise ValueError('support centroid condition missing')
    # For any c, the three support squared distances average to R^2+|c-center|^2.
    if any(mx[k]<4 for k in supp):raise ValueError('not all MEC supports rich')
    if all(m>=4 for m in mx):raise ValueError('unexpected all-rich result requires separate audit')
    return {'status':'PASS_EXACT_CONTROL','n':n,'distinct_pairs':len(ds),'global_supports':len(margins),'minimum_support':min(margins).dump(),'all_actual_distance_classes':classes,'multiplicity_by_center':mx,'histogram':dict(Counter(mx)),'good_vertices':[i for i,m in enumerate(mx)if m<=3],'rich_vertices':[i for i,m in enumerate(mx)if m>=4],'unique_minimum_enclosing_disk_verified':True,'all_mec_supports_rich':True,'all_rich':False,'external_review':False}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('--output');a=p.parse_args();r=verify(json.loads(Path(a.input).read_text()))
    if a.output:Path(a.output).write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({k:v for k,v in r.items()if k!='all_actual_distance_classes'},indent=2))
