"""Standard-library exact replay. No numerical optimizer or network required."""
from __future__ import annotations
import argparse
from collections import Counter
from itertools import combinations
import json
from pathlib import Path
from quadratic import Q,F,base9,cycle9,repair18,hull,turn,dist,norm,sub,add,mul,classes,maximum
from extensions import E

ROOT=Path(__file__).resolve().parent
BASE_SHA='047d05149382e48b602b292df4b8fc9e2da560bb'

def rq(v):
    if not isinstance(v,list) or len(v)!=2 or not all(isinstance(x,str) for x in v):raise ValueError('canonical exact coefficient pair required')
    return Q(F(v[0]),F(v[1]))

def rp(v):
    if not isinstance(v,list) or len(v)!=2:raise ValueError('point pair required')
    return rq(v[0]),rq(v[1])

def same_point(a,b):return a[0]==b[0] and a[1]==b[1]

def check_strict(P,order):
    n=len(P)
    assert sorted(order)==list(range(n))
    assert len(set(P))==n
    signs=[]
    for k,i in enumerate(order):
        j=order[(k+1)%n]
        for h in range(n):
            if h not in (i,j):
                s=turn(P[i],P[j],P[h]);assert s>0;signs.append(s.sign())
    return len(signs)

def check_containment(P,ob):
    n=len(P);v=ob['target'];tr=ob['triangle']
    assert isinstance(v,int) and 0<=v<n
    assert len(tr)==3 and len(set(tr))==3 and v not in tr
    assert all(isinstance(i,int) and 0<=i<n for i in tr)
    a,b,c=tr;assert turn(P[a],P[b],P[c])>0
    signs=[turn(P[a],P[b],P[v]).sign(),turn(P[b],P[c],P[v]).sign(),turn(P[c],P[a],P[v]).sign()]
    assert signs==ob['signs'] and min(signs)>=0
    return min(signs)>0

def check_root_obstruction(P,c,entry):
    assert ('coincides_with'in entry)^('obstruction'in entry)
    if 'coincides_with'in entry:
        i=entry['coincides_with'];assert isinstance(i,int) and 0<=i<len(P)
        assert same_point(c,P[i]);return 'old'
    assert all(not same_point(c,q) for q in P)
    return 'strict containment' if check_containment(P+[c],entry['obstruction']) else 'closed containment'

def check_circumcenters(cert):
    P=base9();assert cert['base_sha']==BASE_SHA and cert['radicand']=='721'
    assert [rp(v) for v in cert['points']]==P
    expected=list(combinations(range(9),3));assert [tuple(x['triple']) for x in cert['triples']]==expected
    C=[rp(x['point']) for x in cert['centers']];assert len(set(C))==len(C)
    seen=set()
    for item in cert['triples']:
        a,b,c=item['triple'];assert turn(P[a],P[b],P[c])!=0
        k=item['center'];assert isinstance(k,int) and 0<=k<len(C);seen.add(k)
        r=dist(C[k],P[a]);assert r>0 and r==dist(C[k],P[b])==dist(C[k],P[c])
    assert seen==set(range(len(C)))
    counts=Counter(check_root_obstruction(P,c,en) for c,en in zip(C,cert['centers']))
    assert len(C)==64 and counts=={'old':6,'strict containment':55,'closed containment':3}
    return {'triples':84,'distinct_centers':64,**dict(counts)}

def check_pairs(cert):
    P=base9();radii=[Q(3)]*3+[3*norm(P[i]) for i in range(3,6)]
    assert cert['base_sha']==BASE_SHA
    assert [rp(v) for v in cert['centers']]==P[:6]
    assert [rq(v) for v in cert['radii_squared']]==radii
    assert [tuple(e['sources']) for e in cert['pairs']]==list(combinations(range(6),2))
    counts=Counter();total=0
    for en in cert['pairs']:
        i,j=en['sources'];v=sub(P[j],P[i]);d=norm(v);assert d>0
        t=(radii[i]-radii[j]+d)/(2*d);S=(radii[i]/d-t*t)/3
        assert rq(en['radicand'])==S
        if S<0:
            assert en['status']=='disjoint' and not en['roots'];continue
        assert [r['branch'] for r in en['roots']]==([-1,1] if S>0 else [0])
        foot=add(P[i],mul(v,t));w=(-3*v[1],v[0])
        PP=[(E(q[0],0,S),E(q[1],0,S)) for q in P]
        for root in en['roots']:
            sg=root['branch'];total+=1
            expected=(E(foot[0],sg*w[0],S),E(foot[1],sg*w[1],S))
            cc=[]
            for coord in root['point']:
                assert len(coord)==2;cc.append(E(rq(coord[0]),rq(coord[1]),S))
            c=tuple(cc)
            assert same_point(c,expected)
            assert dist(c,PP[i])==radii[i] and dist(c,PP[j])==radii[j]
            counts[check_root_obstruction(PP,c,root)]+=1
    assert total==30 and counts=={'old':12,'strict containment':18}
    return {'pairs':15,'real_intersection_branches':30,**dict(counts)}

def check_repair():
    P=repair18();order=[17,4,12,9,2,6,15,5,13,10,0,7,16,3,14,11,1,8]
    num=check_strict(P,order)
    mm=[maximum(P,c) for c in P];assert mm==[4]*9+[2]*9
    old=base9();oldmax=[maximum(old,c) for c in old];assert oldmax==[2]*3+[3]*3+[4]*3
    incidences={}
    for i in range(9):
        r=3*norm(P[i]);w=[j for j in range(18) if j!=i and dist(P[i],P[j])==r]
        assert len(w)==4;incidences[str(i)]={'r2':r.json(),'witnesses':w}
    carrier=[]
    for c in P[9:]:
        values=[dist(c,P[k])-3*norm(c) for k in range(3)]
        assert all(v!=0 for v in values);carrier.extend(values)
    # Explicit rotations around the repaired centers independently reconstruct the new orbits.
    for start,source,witness,t in [(9,0,2,F(-1,100)),(12,0,2,F(-1,50)),(15,3,0,F(-3,50))]:
        v=sub(P[witness],P[source]);a=(1-3*t*t)/(1+3*t*t);b=2*t/(1+3*t*t)
        q=add(P[source],(a*v[0]-3*b*v[1],b*v[0]+a*v[1]));assert q==P[start]
    return {'n':18,'hull_order':order,'supporting_signs':num,'distinct_pairs':153,'old_seed_maxima':oldmax,'maximum_multiplicities':mm,'off_carrier_circle_inequalities':len(carrier),'old_rich_rows':incidences,'points':[[q.json() for q in c] for c in P]}

def check_middle_cycle():
    P=cycle9();order=[8,5,0,6,3,1,7,4,2];num=check_strict(P,order)
    closers=[sum(0<dist(c,q)<1 for q in P) for c in P];assert closers==[2]*9
    mm=[maximum(P,c) for c in P];assert mm==[4]*3+[2]*6
    rows=[]
    for i in range(3):
        k=order.index(i);fan=order[k+1:]+order[:k]
        row=[j for j in fan if dist(P[i],P[j])==1]
        assert len(row)==4 and (i+1)%3 in row[1:3]
        rows.append({'source':i,'angular_witness_order':row,'middle_witnesses':row[1:3]})
    return {'n':9,'hull_order':order,'supporting_signs':num,'closer_counts_at_radius_1':closers,'maximum_multiplicities':mm,'middle_rows':rows,'points':[[q.json() for q in c] for c in P]}

def run():
    initial=base9();seed_signs=check_strict(initial,[4,2,6,5,0,7,3,1,8])
    cc=check_circumcenters(json.loads((ROOT/'data/base9_circumcenters.json').read_text()))
    pp=check_pairs(json.loads((ROOT/'data/prescribed_circle_pairs.json').read_text()))
    return {'status':'restricted exact results; no solution to Erdos97','base_sha':BASE_SHA,'seed_supporting_signs':seed_signs,'circumcenter_exhaustion':cc,'prescribed_circle_pair_exhaustion':pp,'repair':check_repair(),'middle_cycle':check_middle_cycle()}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    report=run();payload=json.dumps(report,indent=2,sort_keys=True)+'\n';path=ROOT/'data/verification.json'
    if args.write:path.write_text(payload)
    else:assert path.read_text()==payload,'stored report differs'
    print(json.dumps({k:v for k,v in report.items() if k not in ('repair','middle_cycle')},indent=2))
    print('Repair maxima:',report['repair']['maximum_multiplicities'])
    print('Middle-cycle maxima:',report['middle_cycle']['maximum_multiplicities'])
if __name__=='__main__':main()
