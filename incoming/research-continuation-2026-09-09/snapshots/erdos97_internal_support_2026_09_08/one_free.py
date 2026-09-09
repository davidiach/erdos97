"""Exact exclusion of a single internally supported vertex over the fixed seed.

No cap-size cutoff, numerical inequality, SAT solver, or optimizer is used.
The support graph is only a necessary relaxation. All its branches are rejected.
"""
from functools import lru_cache
from itertools import combinations
from pathlib import Path
import argparse
import hashlib
import json
import sys
from inherited import load, archive_hash

if sys.flags.optimize:
    raise RuntimeError('Exact checking must not run under -O')
B = load('core')
Q,F = B.Q,B.F
add,sub,mul = B.add,B.sub,B.mul
dot,norm,dist,turn,cross = B.dot,B.norm,B.dist,B.turn,B.cross
ROOT=Path(__file__).resolve().parent
FREE=42

def canonical(value):
    return json.dumps(value,indent=2,sort_keys=True)+'\n'

def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()

@lru_cache(None)
def setup():
    P=B.base9()
    ceiling=B.old_ceiling()
    slots=B.build_slots(P,B.ORDER)
    edges,counts,sha=B.graph_data(P,slots)
    previous=json.loads((B.ROOT/'data/verification.json').read_text())
    assert [s.json() for s in slots]==previous['slots']
    assert [list(e) for e in edges]==previous['possible_edges']
    assert sha==previous['range_digest']
    assert len(slots)==42
    return P,slots,edges,ceiling

def intersection(a,b,c,d):
    u,v=sub(b,a),sub(d,c)
    determinant=cross(u,v)
    if determinant==0:
        raise ValueError('parallel insertion-cell sides')
    return add(a,mul(u,cross(sub(c,a),v)/determinant))

def insertion_triangle(P,cell):
    order=B.ORDER
    a,b=P[order[cell]],P[order[(cell+1)%9]]
    v=intersection(P[order[cell-1]],a,b,P[order[(cell+2)%9]])
    T=(a,v,b)
    assert turn(*T)>0
    for k in range(9):
        sign=turn(P[order[k]],P[order[(k+1)%9]],v)
        assert sign<0 if k==cell else sign>=0
    return T

def closest_on_segment(p,a,b):
    v=sub(b,a)
    s=max(Q(0),min(Q(1),dot(sub(p,a),v)/norm(v)))
    return add(a,mul(v,s))

def closest_on_triangle(p,T):
    if all(turn(T[k],T[(k+1)%3],p)>=0 for k in range(3)):
        return p
    points=[closest_on_segment(p,T[k],T[(k+1)%3]) for k in range(3)]
    return min(points,key=lambda x:dist(p,x))

def segment_meets_triangle(a,b,T):
    lo,hi=Q(0),Q(1)
    v=sub(b,a)
    for k in range(3):
        alpha=turn(T[k],T[(k+1)%3],a)
        beta=cross(sub(T[(k+1)%3],T[k]),v)
        if beta==0:
            if alpha<0: return False
        elif beta>0: lo=max(lo,-alpha/beta)
        else: hi=min(hi,-alpha/beta)
    return lo<=hi

def distance_interval(slot,T):
    a,b=slot.point(slot.lower),slot.point(slot.upper)
    hi=max(dist(p,q) for p in (a,b) for q in T)
    if segment_meets_triangle(a,b,T):
        return Q(0),hi
    values=[dist(p,closest_on_triangle(p,T)) for p in (a,b)]
    values.extend(dist(p,closest_on_segment(p,a,b)) for p in T)
    return min(values),hi

def regular_to_free_range(P,slot,T):
    values=[]
    for s in (slot.lower,slot.upper):
        x=slot.point(s)
        r=dist(x,P[slot.pair[0]])
        values.extend(dist(x,y)-r for y in T)
        values.append(dist(x,closest_on_triangle(x,T))-r)
    return min(values),max(values)

def free_to_regular_range(P,old,slot,T):
    values=[]
    A=norm(slot.direction)
    for f in T:
        C=dist(f,slot.midpoint)-dist(f,P[old])
        H=2*dot(slot.direction,sub(slot.midpoint,f))
        s=max(slot.lower,min(slot.upper,-H/(2*A)))
        values.extend(A*t*t+H*t+C for t in (slot.lower,s,slot.upper))
    return min(values),max(values)

def possible(bounds):
    return bounds[0]<=0<=bounds[1]

def graph_peel(edges,free_degree):
    active=set(range(FREE+1))
    adjacency={i:set() for i in active}
    for a,b in edges:
        assert a!=b and 0<=a<=FREE and 0<=b<=FREE
        adjacency[a].add(b)
    layers=[]
    while True:
        removed=sorted(i for i in active if len(adjacency[i]&active)<(free_degree if i==FREE else 2))
        if not removed:
            return sorted(active),layers
        layers.append(removed)
        active.difference_update(removed)

def split(T):
    k=max(range(3),key=lambda i:dist(T[i],T[(i+1)%3]))
    a,b,c=T[k],T[(k+1)%3],T[(k+2)%3]
    m=mul(add(a,b),Q(F(1,2)))
    return k,((a,m,c),(m,b,c))

def allowed_incoming(P,slots,T):
    return [i for i,s in enumerate(slots) if possible(regular_to_free_range(P,s,T))]

def forced_conflicts(slots,edges,active):
    active=set(active)
    rows={}
    for i in sorted(active-{FREE}):
        outgoing={b for a,b in edges if a==i and b in active}
        assert len(outgoing)>=2
        row=set(slots[i].pair)
        if len(outgoing)==2:
            row.update(j+9 for j in outgoing)
        rows[i]=row
    result=[]
    for i,j in combinations(sorted(rows),2):
        common=sorted(rows[i]&rows[j])
        if len(common)>2:
            result.append({'centers':[i,j],'common_witnesses':common})
    return result

def obstruction(P,slots,base_edges,T,old):
    incoming=allowed_incoming(P,slots,T)
    E=list(base_edges)+[(i,FREE) for i in incoming]
    if old is not None:
        outgoing=[i for i,s in enumerate(slots) if possible(free_to_regular_range(P,old,s,T))]
        active,layers=graph_peel(E+[(FREE,i) for i in outgoing],3)
        if FREE in active: return None
        return {'kind':'one-old','incoming':incoming,'outgoing':outgoing,
                'remaining':active,'layers':layers}
    active,layers=graph_peel(E+[(FREE,i) for i in range(FREE)],4)
    if FREE not in active:
        return {'kind':'zero-old-empty','incoming':incoming,'remaining':active,'layers':layers}
    eligible=[i for i in active if i!=FREE]
    ranges={i:distance_interval(slots[i],T) for i in eligible}
    endpoints=sorted(set(x for r in ranges.values() for x in r))
    cliques=set()
    for r in endpoints:
        C=tuple(i for i in eligible if ranges[i][0]<=r<=ranges[i][1])
        if len(C)>=4: cliques.add(C)
    maximal=sorted(c for c in cliques if not any(set(c)<set(d) for d in cliques))
    cases=[]
    for C in maximal:
        sub_edges=E+[(FREE,i) for i in C]
        act,peeling=graph_peel(sub_edges,4)
        item={'outgoing':list(C),'remaining':act,'layers':peeling}
        if FREE not in act:
            item['kind']='empty'
        else:
            conflicts=forced_conflicts(slots,sub_edges,act)
            bad={tuple(c['centers']) for c in conflicts}
            selected=sorted(set(C)&set(act))
            cover=[]
            for four in combinations(selected,4):
                pairs=[list(pair) for pair in combinations(four,2) if pair in bad]
                if not pairs: return None
                cover.append({'targets':list(four),'conflict':pairs[0]})
            item.update(kind='pair-sharing',conflicts=conflicts,four_subset_cover=cover)
        cases.append(item)
    return {'kind':'zero-old-radius-cover','incoming':incoming,'initial_remaining':active,
            'initial_layers':layers,'distance_intervals':[
                {'slot':i,'lower':ranges[i][0].json(),'upper':ranges[i][1].json()} for i in eligible],
            'maximal_radius_target_sets':[list(c) for c in maximal],'cases':cases}

def certify_case(cell,old,max_depth=12):
    P,slots,edges,_=setup()
    nodes=0; leaves=0; maximum=0
    def visit(T,depth):
        nonlocal nodes,leaves,maximum
        nodes+=1; maximum=max(maximum,depth)
        certificate=obstruction(P,slots,edges,T,old)
        if certificate is not None:
            leaves+=1
            return {'leaf':certificate}
        if depth>=max_depth:
            raise RuntimeError('unresolved domain; no exclusion certificate is produced')
        k,children=split(T)
        return {'split_edge':k,'children':[visit(child,depth+1) for child in children]}
    tree=visit(insertion_triangle(P,cell),0)
    return {'cell':cell,'old_witness':old,'nodes':nodes,'leaves':leaves,
            'maximum_depth':maximum,'tree':tree}

def run():
    P,slots,edges,ceiling=setup()
    cases=[]
    # Explicit coverage: no quotient by unproved rotational label symmetry.
    for cell in range(9):
        for old in [None]+list(range(9)):
            cases.append(certify_case(cell,old))
    return {'status':'restricted one-free-vertex exclusion; written reduction review pending',
            'not_an_erdos97_solution':True,'inherited_archive_sha256':archive_hash(),
            'base_sha':B.BASE_SHA,'old_ceiling':ceiling,'slot_count':len(slots),
            'base_edge_count':len(edges),'case_count':len(cases),
            'nodes':sum(c['nodes'] for c in cases),'leaves':sum(c['leaves'] for c in cases),
            'maximum_depth':max(c['maximum_depth'] for c in cases),'cases':cases}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--write',action='store_true')
    args=parser.parse_args()
    report=run(); payload=canonical(report)
    path=ROOT/'data/one_free_certificate.json'
    if args.write: path.write_text(payload)
    elif path.read_text()!=payload: raise AssertionError('one-free certificate differs')
    print(json.dumps({k:v for k,v in report.items() if k!='cases'},indent=2))

if __name__=='__main__': main()
