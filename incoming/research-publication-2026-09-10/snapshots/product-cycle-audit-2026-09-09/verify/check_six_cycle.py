"""Exact monodromy, distance classes, and strict interior/hull signs.
No search imports; all inequalities certified at the isolated quartic root.
"""
from pathlib import Path
from itertools import combinations
from collections import defaultdict
import sys,json,argparse
from quartic_field import K,S,MOD,INITIAL,cmul,csub,cnorm,rotate,det,validate_embedding

def check(d):
    if sys.flags.optimize:raise ValueError('assertions disabled')
    if d.get('kind')!='exact_upper_six_cycle_nonconvex_control':raise ValueError('wrong kind')
    if d['minimal_polynomial_ascending']!=list(map(str,MOD))or d['isolating_interval']!=list(map(str,INITIAL)):raise ValueError('wrong root')
    validate_embedding()
    P=[tuple(K(c)for c in p)for p in d['coordinates']]
    m=[tuple(K(c)for c in p)for p in d['multipliers']]
    if len(P)!=18 or len(m)!=6:raise ValueError('wrong dimensions')
    one=(K(1),K(0));omega=(K(-1)/2,K(1)/2);z=P[::3]
    product=one
    for i,t in enumerate(m):
        if t[1]<=0 or cnorm(csub(t,one))!=3:raise ValueError('not upper own-side multiplier')
        product=cmul(product,t)
        target=z[i+1]if i<5 else cmul(omega,z[0])
        if cmul(z[i],t)!=target:raise ValueError('cycle mismatch')
    if product!=omega:raise ValueError('wrong projective monodromy')
    distances={}
    for i,j in combinations(range(18),2):
        r=cnorm(csub(P[i],P[j]))
        if r<=0:raise ValueError('collision')
        distances[i,j]=r
    H=d['hull_order'];inside=d['interior_labels']
    if len(H)!=6 or len(set(H))!=6 or sorted(H+inside)!=list(range(18)):raise ValueError('hull partition')
    signs=[]
    for k,i in enumerate(H):
        j=H[(k+1)%6]
        for l in range(18):
            if l in(i,j):continue
            delta=det(csub(P[j],P[i]),csub(P[l],P[i]))
            if delta<=0:raise ValueError('hull edge not strictly supporting')
            signs.append(delta)
    rows=[];partitions=[];maxima=[]
    for i in range(18):
        orbit,k=divmod(i,3)
        if rotate(P[i])!=P[3*orbit+(k+1)%3]:raise ValueError('not C3')
        successor=3*((orbit+1)%6)+(k+int(orbit==5))%3
        W=[3*orbit+(k+1)%3,3*orbit+(k+2)%3,successor]
        if len(set(W))!=3 or any(distances[tuple(sorted((i,j)))]!=3*cnorm(P[i])for j in W):raise ValueError('named triple equality')
        rows.append({'center':i,'witnesses':W})
        group=defaultdict(list)
        for j in range(18):
            if i!=j:group[distances[tuple(sorted((i,j)))]].append(j)
        # Certify no two different polynomial class values coincide in the chosen embedding.
        for a,b in combinations(group,2):
            if (a-b).sign()==0:raise ValueError('unmerged equal class')
        partitions.append([{'squared_radius':v.dump(),'witnesses':w}for v,w in sorted(group.items())]);maxima.append(max(map(len,group.values())))
    if not (K(1)/2<S<K(3)/4):raise ValueError('norm bounds')
    expected=[K(1),1/(S*S),1/S,K(1),1/(S*S),1/S]
    if any(cnorm(a)!=b for a,b in zip(z,expected)):raise ValueError('radial layers')
    return {'status':'PASS_EXACT_UPPER_SIX_CYCLE','root_embedding':'unique real root in (536/1000,537/1000)',
      'point_count':18,'distinct_pairs':len(distances),'hull_vertices':len(H),'strict_interior_points':len(inside),
      'global_hull_support_checks':len(signs),'named_three_witness_rows':rows,'all_radius_maximum_multiplicities':maxima,
      'full_distance_partitions':partitions,'all_multipliers_strictly_upper':True,'exact_monodromy':'omega',
      'all_rich':all(x>=4 for x in maxima),'strictly_convex':False,'external_review':False}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('input');ap.add_argument('--output');a=ap.parse_args()
    r=check(json.loads(Path(a.input).read_text()));text=json.dumps(r,indent=2)+'\n'
    if a.output:Path(a.output).write_text(text)
    print(json.dumps({k:v for k,v in r.items()if k not in['full_distance_partitions','named_three_witness_rows']},indent=2))
