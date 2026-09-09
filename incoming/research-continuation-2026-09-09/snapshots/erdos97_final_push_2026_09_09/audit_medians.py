"""Exact audit of median domains and the five saved fixed-pattern exclusions."""
from itertools import combinations
from collections import Counter,defaultdict
from pathlib import Path
import json,argparse
from median_probe import ORDER,POS,pool,med,group_domains
from previous import load_kalmanson
ROOT=Path(__file__).resolve().parent

def check_pattern(rows):
    if len(rows)!=27:raise ValueError('wrong row count')
    resources=Counter()
    for i,row in enumerate(rows):
        if len(row)!=4 or len(set(row))!=4 or any(type(x)is not int or not 0<=x<27 or x==i for x in row):
            raise ValueError('invalid row')
        counts=Counter(x//3 for x in row)
        if set(counts)!=set(pool(i//3))or sorted(counts.values())!=[1,1,2]:
            raise ValueError('wrong source pool or distribution')
        for a,b in combinations(sorted(row),2):
            side=int(0<(POS[i]-POS[a])%27<(POS[b]-POS[a])%27)
            resources[(a,b,side)]+=1
    if max(resources.values())>1:raise ValueError('same-side pair capacity exceeded')
    for g in range(9):
        a,b,c=range(3*g,3*g+3)
        rows3=[set(rows[v])for v in (a,b,c)]
        if len(set.union(*rows3))!=9 or set.intersection(*rows3):raise ValueError('cover saturation failed')
        common=[rows3[i]&rows3[j]for i,j in ((0,1),(0,2),(1,2))]
        if any(len(x)!=1 for x in common):raise ValueError('shared-witness saturation failed')
        if not med(*[next(iter(x))for x in common],c):raise ValueError('source median failed')
        owners=[]
        for pair in ((a,b),(a,c),(b,c)):
            found=[i for i,row in enumerate(rows)if set(pair)<=set(row)]
            if len(found)!=1:raise ValueError('internal pair not uniquely owned')
            owners.append(found[0])
        if not med(*owners,c):raise ValueError('target median failed')
    return True

def alternate_certificate_check(rows,order,certificate):
    """Graph-connected-components version, not the inherited DSU checker."""
    n=len(rows)
    if sorted(order)!=list(range(n)):raise ValueError('bad boundary order')
    rank={v:i for i,v in enumerate(order)}
    centers=certificate['selected_centers'];records=certificate['inequalities']
    if centers!=sorted(set(centers))or not centers or not records:raise ValueError('missing premises')
    chords=list(combinations(range(n),2));adj=defaultdict(set)
    for i in centers:
        if type(i)is not int or not 0<=i<n:raise ValueError('bad center')
        row=rows[i]
        if len(row)!=4 or len(set(row))!=4 or i in row:raise ValueError('bad witness row')
        q=[tuple(sorted((i,v)))for v in row]
        for j in range(1,4):adj[q[0]].add(q[j]);adj[q[j]].add(q[0])
    comp={}
    for p in chords:
        if p in comp:continue
        todo=[p];comp[p]=p
        while todo:
            x=todo.pop()
            for y in adj[x]:
                if y not in comp:comp[y]=p;todo.append(y)
    terms=Counter()
    for record in records:
        q=record['quadruple'];kind=record['kind'];w=record['weight']
        if type(w)is not int or w<=0 or kind not in (0,1)or len(q)!=4 or len(set(q))!=4:
            raise ValueError('bad strict inequality')
        if any(type(v)is not int or v not in rank for v in q):raise ValueError('invalid vertex')
        r=[(rank[x]-rank[q[0]])%n for x in q]
        if r!=sorted(r):raise ValueError('not cyclic order')
        a,b,c,d=q
        pos=[(a,c),(b,d)];neg=[(a,b),(c,d)]if kind==0 else[(a,d),(b,c)]
        for sign,pairs in ((1,pos),(-1,neg)):
            for x,y in pairs:terms[comp[tuple(sorted((x,y)))]]+=sign*w
    if any(terms.values()):raise ValueError('strict sum does not cancel')
    return True

def report():
    data=json.loads((ROOT/'evidence/median_direct_1.json').read_text());legacy=load_kalmanson()
    patterns=[];cert_count=0
    for h in data['history']:
        if 'rows'not in h:continue
        rows=h['rows'];check_pattern(rows)
        v=h['kalmanson']
        if v['status']!='exact obstruction':raise ValueError('unresolved stored pattern')
        for c in v['certificates']:
            legacy.validate_certificate(rows,ORDER,c);alternate_certificate_check(rows,ORDER,c)
        cert_count+=len(v['certificates']);patterns.append(rows)
    if len(patterns)!=5 or cert_count!=54:raise ValueError('changed bounded search inventory')
    stats={}
    for i in range(9):
        D,s=group_domains(i)
        if len(D)!=4374 or s['pairwise_and_cover']!=13122:raise ValueError('domain census changed')
        stats[i]=s
    return {'schema':'erdos97.median_audit.v1','fixed_patterns':5,'exact_certificates':54,
      'each_certificate_checked_by_two_representations':True,
      'domain_counts':stats,'full_family_excluded':False,
      'final_solver_attempt':{k:data['history'][-1][k]for k in ('status','message')}}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
    r=report();t=json.dumps(r,indent=2,sort_keys=True)+'\n';path=ROOT/'evidence/median_audit.json'
    if a.check:
        if path.read_text()!=t:raise ValueError('saved report differs')
    else:path.write_text(t)
    print(json.dumps({k:r[k]for k in ('fixed_patterns','exact_certificates','full_family_excluded')},indent=2))
