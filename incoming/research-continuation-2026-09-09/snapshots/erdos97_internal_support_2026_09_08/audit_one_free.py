"""Second-representation checker for the one-free certificate.

Imports neither one_free nor its arithmetic/geometry implementation. Uses the
preceding independent radical ring, convex hulls of Minkowski differences for
distance minima, interpolation for quadratics, and reverse graph deletion.
"""
from itertools import combinations
from functools import lru_cache
from pathlib import Path
import argparse
import json
import sys
from inherited import load, archive_hash

if sys.flags.optimize:
    raise RuntimeError('Exact checking must not run under -O')
O=load('oracle')
ROOT=Path(__file__).resolve().parent
FREE=42
ORDER=[4,2,6,5,0,7,3,1,8]
plus,minus,times=O.plus,O.minus,O.times
square,distance,orientation,area=O.square,O.distance,O.orientation,O.area

def scalar(a,b):
    return (square(plus(a,b))-square(a)-square(b))/2

def hull(points):
    points=sorted(set(points))
    if len(points)<=2: return points
    def half(seq):
        result=[]
        for p in seq:
            while len(result)>=2 and orientation(result[-2],result[-1],p)<=0:
                result.pop()
            result.append(p)
        return result
    return half(points)[:-1]+half(reversed(points))[:-1]

def distance_from_origin(points,R):
    H=hull(points)
    zero=(R(0),R(0))
    if len(H)>=3 and all(orientation(H[k],H[(k+1)%len(H)],zero)>=0 for k in range(len(H))):
        return R(0)
    values=[square(p) for p in H]
    if len(H)>=2:
        for i,p in enumerate(H):
            q=H[(i+1)%len(H)]
            v=minus(q,p)
            t=max(R(0),min(R(1),-scalar(p,v)/square(v)))
            values.append(square(plus(p,times(v,t))))
    return min(values)

def point(slot,t):
    return plus(slot[1],times(slot[2],t))

def source_range(P,slot,T,R):
    values=[]
    for t in slot[3:]:
        p=point(slot,t)
        r=distance(p,P[slot[0][0]])
        differences=[minus(p,q) for q in T]
        values.extend(square(v)-r for v in differences)
        values.append(distance_from_origin(differences,R)-r)
    return min(values),max(values)

def target_range(P,a,slot,T,R):
    values=[]
    for f in T:
        def evaluate(t):
            return distance(f,point(slot,t))-distance(f,P[a])
        C=evaluate(R(0)); p=evaluate(R(1)); m=evaluate(R(-1))
        A=(p+m-2*C)/2; B=(p-m)/2
        assert A>0
        t=-B/(2*A)
        values.extend([evaluate(slot[3]),evaluate(slot[4])])
        if slot[3]<t<slot[4]: values.append(evaluate(t))
    return min(values),max(values)

def radial_range(slot,T,R):
    differences=[minus(point(slot,t),q) for t in slot[3:] for q in T]
    return distance_from_origin(differences,R),max(square(v) for v in differences)

def inside_range(bounds):
    return bounds[0]<=0<=bounds[1]

def initial_triangle(P,cell):
    a,b=P[ORDER[cell]],P[ORDER[(cell+1)%9]]
    u=minus(a,P[ORDER[cell-1]])
    v=minus(P[ORDER[(cell+2)%9]],b)
    # Intersect a+s*u and b+t*v: independent anchoring of the side lines.
    w=plus(a,times(u,area(minus(b,a),v)/area(u,v)))
    T=(a,w,b)
    assert orientation(*T)>0
    for k in range(9):
        s=orientation(P[ORDER[k]],P[ORDER[(k+1)%9]],w)
        assert s<0 if k==cell else s>=0
    return T

def core(edges,required):
    active=set(range(FREE+1))
    while True:
        changed=False
        for i in sorted(active,reverse=True):
            if len({b for a,b in edges if a==i and b in active})<(required if i==FREE else 2):
                active.remove(i); changed=True
        if not changed: return sorted(active)

def check_peeling(edges,required,layers,remaining):
    active=set(range(FREE+1))
    for layer in layers:
        expected=sorted(i for i in active if len({b for a,b in edges if a==i and b in active})<(required if i==FREE else 2))
        assert layer==expected and layer
        active.difference_update(layer)
    assert sorted(active)==remaining==core(edges,required)

def verify_leaf(leaf,P,slots,E,T,old,R):
    incoming=[i for i,s in enumerate(slots) if inside_range(source_range(P,s,T,R))]
    assert leaf['incoming']==incoming
    edges=E+[(i,FREE) for i in incoming]
    if old is not None:
        assert leaf['kind']=='one-old'
        outgoing=[i for i,s in enumerate(slots) if inside_range(target_range(P,old,s,T,R))]
        assert outgoing==leaf['outgoing']
        check_peeling(edges+[(FREE,i) for i in outgoing],3,leaf['layers'],leaf['remaining'])
        assert FREE not in leaf['remaining']
        return
    if leaf['kind']=='zero-old-empty':
        check_peeling(edges+[(FREE,i) for i in range(FREE)],4,leaf['layers'],leaf['remaining'])
        assert FREE not in leaf['remaining']
        return
    assert leaf['kind']=='zero-old-radius-cover'
    check_peeling(edges+[(FREE,i) for i in range(FREE)],4,leaf['initial_layers'],leaf['initial_remaining'])
    eligible=[i for i in leaf['initial_remaining'] if i!=FREE]
    ranges={i:radial_range(slots[i],T,R) for i in eligible}
    assert leaf['distance_intervals']==[
        {'slot':i,'lower':ranges[i][0].qjson(),'upper':ranges[i][1].qjson()} for i in eligible]
    target_sets=set()
    for r in set(v for bounds in ranges.values() for v in bounds):
        C=tuple(i for i in eligible if ranges[i][0]<=r<=ranges[i][1])
        if len(C)>=4: target_sets.add(C)
    target_sets=sorted(c for c in target_sets if not any(set(c)<set(d) for d in target_sets))
    assert leaf['maximal_radius_target_sets']==[list(c) for c in target_sets]
    assert len(leaf['cases'])==len(target_sets)
    for C,item in zip(target_sets,leaf['cases']):
        assert item['outgoing']==list(C)
        sub_edges=edges+[(FREE,i) for i in C]
        check_peeling(sub_edges,4,item['layers'],item['remaining'])
        if item['kind']=='empty':
            assert FREE not in item['remaining']
            continue
        assert item['kind']=='pair-sharing' and FREE in item['remaining']
        active=set(item['remaining'])
        rows={}
        for i in sorted(active-{FREE}):
            outgoing={b for a,b in sub_edges if a==i and b in active}
            assert len(outgoing)>=2
            rows[i]=set(slots[i][0])
            if len(outgoing)==2: rows[i].update(j+9 for j in outgoing)
        expected=[]
        for i,j in combinations(sorted(rows),2):
            shared=sorted(rows[i]&rows[j])
            if len(shared)>2: expected.append({'centers':[i,j],'common_witnesses':shared})
        assert expected==item['conflicts']
        bad={tuple(e['centers']) for e in expected}
        targets=sorted(set(C)&active)
        assert [r['targets'] for r in item['four_subset_cover']]==[list(s) for s in combinations(targets,4)]
        for record in item['four_subset_cover']:
            pair=tuple(record['conflict'])
            assert pair in bad and set(pair)<=set(record['targets'])

@lru_cache(None)
def context():
    R=O.ring(); P=O.seed(R)
    prior=json.loads((O.ROOT/'data/verification.json').read_text())
    O.ceiling(R,P,prior['old_ceiling_replay'])
    records=O.ray_slots(R,P,ORDER)
    E,counts,digest=O.graph(R,P,records)
    O.check_discrete(prior,records,E,counts,digest)
    E=[tuple(e) for e in E]
    slots=[O.decode_slot(R,s) for s in records]
    return R,P,prior,slots,E


def audit(report):
    R,P,prior,slots,E=context()
    assert report['base_sha']==prior['base_sha']
    assert report['inherited_archive_sha256']==archive_hash()
    assert report['old_ceiling']==prior['old_ceiling_replay']
    assert report['slot_count']==42 and report['base_edge_count']==123
    assert report['not_an_erdos97_solution'] is True
    expected=[(cell,old) for cell in range(9) for old in [None]+list(range(9))]
    assert [(c['cell'],c['old_witness']) for c in report['cases']]==expected
    totals=[0,0,0]
    for case in report['cases']:
        n=l=dmax=0
        def visit(tree,T,depth):
            nonlocal n,l,dmax
            n+=1; dmax=max(dmax,depth)
            if 'leaf' in tree:
                assert set(tree)=={'leaf'}
                l+=1
                verify_leaf(tree['leaf'],P,slots,E,T,case['old_witness'],R)
            else:
                assert set(tree)=={'split_edge','children'}
                k=tree['split_edge']
                assert type(k) is int and 0<=k<3 and len(tree['children'])==2
                a,b,c=T[k],T[(k+1)%3],T[(k+2)%3]
                m=times(plus(a,b),R(1)/2)
                children=[(a,m,c),(m,b,c)]
                for sub,T2 in zip(tree['children'],children):
                    assert orientation(*T2)>0
                    visit(sub,T2,depth+1)
        visit(case['tree'],initial_triangle(P,case['cell']),0)
        assert (n,l,dmax)==(case['nodes'],case['leaves'],case['maximum_depth'])
        totals[0]+=n; totals[1]+=l; totals[2]=max(totals[2],dmax)
    assert len(expected)==report['case_count']==90
    assert tuple(totals)==(report['nodes'],report['leaves'],report['maximum_depth'])
    return {'status':'passed','cases':90,'nodes':totals[0],'leaves':totals[1],
            'maximum_depth':totals[2],'largest_sign_enclosure_bits':O.MAX_BITS,
            'distance_minima':'origin projections onto Minkowski-difference convex hulls',
            'quadratic_coefficients':'interpolation at zero and plus/minus one',
            'graph_check':'reverse sequential deletion plus full four-subset conflict coverage',
            'primary_code_imported':False,'external_mathematical_review':False}

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--write',action='store_true')
    args=parser.parse_args()
    report=json.loads((ROOT/'data/one_free_certificate.json').read_text())
    output=json.dumps(audit(report),indent=2,sort_keys=True)+'\n'
    path=ROOT/'data/one_free_oracle.json'
    if args.write: path.write_text(output)
    else: assert path.read_text()==output
    print(output)

if __name__=='__main__': main()
