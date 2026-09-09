from quadratic import *
from extensions import E
from pathlib import Path
from itertools import combinations
import json

BASE_SHA='047d05149382e48b602b292df4b8fc9e2da560bb'

def contains_witness(P):
    # A point in a nondegenerate closed triangle of other distinct points
    # cannot be a vertex of the convex hull. Coefficients need not be computed.
    n=len(P);new=n-1
    for target in [new]+list(range(new)):
        for tr in combinations([i for i in range(n) if i!=target],3):
            if target!=new and new not in tr:continue
            a,b,c=tr;ar=turn(P[a],P[b],P[c])
            if ar==0:continue
            if ar<0:b,c=c,b
            ss=[turn(P[a],P[b],P[target]),turn(P[b],P[c],P[target]),turn(P[c],P[a],P[target])]
            if all(s>=0 for s in ss):
                return {'target':target,'triangle':[a,b,c],'signs':[s.sign() for s in ss]}
    raise AssertionError('No closed-triangle obstruction exists')

def old_coincidence(P,c):
    for i,p0 in enumerate(P):
        if c[0]==p0[0] and c[1]==p0[1]:return i
    return None

def circumcenter_certificate(P):
    all_centers={};triples=[]
    for tr in combinations(range(len(P)),3):
        c=circle(*(P[i] for i in tr));assert c is not None
        if c not in all_centers:
            entry={'point':[x.json() for x in c]}
            old=old_coincidence(P,c)
            if old is not None:entry['coincides_with']=old
            else:entry['obstruction']=contains_witness(P+[c])
            all_centers[c]=(len(all_centers),entry)
        triples.append({'triple':tr,'center':all_centers[c][0]})
    return {'base_sha':BASE_SHA,'radicand':str(D),'points':[[x.json() for x in p0] for p0 in P],
            'centers':[e for _,e in all_centers.values()],'triples':triples}

def pair_certificate():
    P=base9();radii=[Q(3)]*3+[3*norm(P[i]) for i in range(3,6)];cases=[]
    for i,j in combinations(range(6),2):
        v=sub(P[j],P[i]);d=norm(v);t=(radii[i]-radii[j]+d)/(2*d)
        S=(radii[i]/d-t*t)/3
        en={'sources':[i,j],'radicand':S.json(),'roots':[]}
        if S<0:
            en['status']='disjoint';cases.append(en);continue
        for sg in ([-1,1] if S>0 else [0]):
            foot=add(P[i],mul(v,t));w=(-3*v[1],v[0])
            c=(E(foot[0],sg*w[0],S),E(foot[1],sg*w[1],S))
            PP=[(E(q[0],0,S),E(q[1],0,S)) for q in P]
            assert norm(sub(c,PP[i]))==radii[i]
            assert norm(sub(c,PP[j]))==radii[j]
            root={'branch':sg,'point':[q.json() for q in c]}
            old=old_coincidence(PP,c)
            if old is not None:root['coincides_with']=old
            else:root['obstruction']=contains_witness(PP+[c])
            en['roots'].append(root)
        cases.append(en)
    return {'base_sha':BASE_SHA,'centers':[[q.json() for q in x] for x in P[:6]],'radii_squared':[q.json() for q in radii],'pairs':cases}

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--write',action='store_true')
    args=parser.parse_args()
    root=Path(__file__).resolve().parent/'data'
    outputs={'base9_circumcenters.json':circumcenter_certificate(base9()),
             'prescribed_circle_pairs.json':pair_certificate()}
    for name,data in outputs.items():
        payload=json.dumps(data,indent=2)+'\n'
        if args.write:(root/name).write_text(payload)
        else:assert (root/name).read_text()==payload,name
    print('Both exhaustive certificates reproduce exactly.')
