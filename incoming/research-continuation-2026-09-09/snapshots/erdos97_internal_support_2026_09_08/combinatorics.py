"""Independent discrete audit of retained moving-seed patterns and certificates."""
from collections import Counter,defaultdict
from fractions import Fraction as F
from itertools import combinations,product
from pathlib import Path
import argparse,json
ROOT=Path(__file__).resolve().parent


def preflight(rows,order):
    n=len(rows)
    if sorted(order)!=list(range(n)):raise ValueError('invalid boundary order')
    position={v:k for k,v in enumerate(order)}
    for i,S in enumerate(rows):
        if len(S)!=4 or len(set(S))!=4 or i in S or any(type(j) is not int or not 0<=j<n for j in S):
            raise ValueError('invalid witness row')
    errors=[]
    for i,j in combinations(range(n),2):
        shared=set(rows[i])&set(rows[j])
        if len(shared)>2:errors.append((i,j,'three common witnesses'))
        elif len(shared)==2:
            a,b=sorted(shared)
            side_i=0<(position[i]-position[a])%n<(position[b]-position[a])%n
            side_j=0<(position[j]-position[a])%n<(position[b]-position[a])%n
            if side_i==side_j:errors.append((i,j,'same-side pair apices'))
    return errors


def verify_inequality_certificate(rows,order,certificate):
    """Connected chord-equality graph, rather than the primary disjoint sets."""
    n=len(rows);pos={v:k for k,v in enumerate(order)}
    if sorted(order)!=list(range(n)):raise ValueError('invalid order')
    G={e:set() for e in combinations(range(n),2)}
    selected=certificate['selected_centers']
    if selected!=sorted(set(selected)) or not selected:raise ValueError('invalid source rows')
    for i in selected:
        if type(i) is not int or not 0<=i<n:raise ValueError('invalid selected center')
        chords=[tuple(sorted((i,j))) for j in rows[i]]
        for a,b in combinations(chords,2):G[a].add(b);G[b].add(a)
    label={};index=0
    for e in G:
        if e in label:continue
        stack=[e];label[e]=index
        while stack:
            for q in G[stack.pop()]:
                if q not in label:label[q]=index;stack.append(q)
        index+=1
    coeff=Counter()
    if not certificate['inequalities']:raise ValueError('empty strict sum')
    for r in certificate['inequalities']:
        q=r['quadruple'];w=r['weight'];k=r['kind']
        if len(q)!=4 or len(set(q))!=4 or type(w) is not int or w<=0:raise ValueError('invalid strict term')
        positions=[(pos[x]-pos[q[0]])%n for x in q]
        if positions!=sorted(positions):raise ValueError('invalid cyclic quadrilateral')
        a,b,c,d=q
        if k==0:negative=((a,b),(c,d))
        elif k==1:negative=((a,d),(b,c))
        else:raise ValueError('invalid kind')
        for u,v in ((a,c),(b,d)):coeff[label[tuple(sorted((u,v)))]]+=w
        for u,v in negative:coeff[label[tuple(sorted((u,v)))]]-=w
    if any(coeff.values()):raise ValueError('strict sum does not cancel')
    return True


def cluster_resources(rows,copies=3):
    resources=Counter();costs=[]
    for i,S in enumerate(rows):
        if any(j//copies==i//copies for j in S):raise ValueError('witness from source cluster')
        groups=defaultdict(list)
        for j in S:groups[j//copies].append(j)
        if len(groups)>3:raise ValueError('more than three target clusters')
        cost=0
        for G in groups.values():
            for pair in combinations(sorted(G),2):resources[pair]+=1;cost+=1
        costs.append(cost)
    if max(resources.values(),default=0)>1:raise ValueError('internal witness pair used twice')
    return resources,costs


def certificate_audit():
    base=json.loads((ROOT/'data/moving_pattern_obstructions.json').read_text())
    certificates=0
    for item in base['patterns']:
        if preflight(item['rows'],item['order']):raise ValueError('retained circle preflight changed')
        resources,costs=cluster_resources(item['rows'])
        if len(resources)!=27 or costs!=[1]*27:raise ValueError('triple saturation changed')
        for cert in item['certificates']:
            verify_inequality_certificate(item['rows'],item['order'],cert);certificates+=1
    filtered=0;filtered_certificates=0
    for path in sorted((ROOT/'exploratory').glob('filtered_moving_*.json')):
        packet=json.loads(path.read_text())
        for step in packet['rounds']:
            if 'rows' not in step:continue
            filtered+=1;rows=step['rows'];order=packet['boundary_order']
            if preflight(rows,order):raise ValueError('filtered circle preflight changed')
            cluster_resources(rows)
            for cert in step['strong_preflight'].get('certificates',[]):
                verify_inequality_certificate(rows,order,cert);filtered_certificates+=1
            if step['strong_preflight']['status']=='exact feasible linear relaxation':
                # Check the exact feasibility independently by an equality graph.
                from kalmanson import constraints
                classes,C=constraints(rows,order)
                x=list(map(F,step['strong_preflight']['class_distances']))
                if min(x)<=0 or any(sum(x[i]*v for i,v in coeff.items())<=0 for _,_,coeff in C):
                    raise ValueError('invalid exact relaxation point')
    return {'initial_distinct_fixed_patterns':len(base['patterns']),
            'initial_exact_certificates':certificates,'filtered_patterns_checked':filtered,
            'filtered_exact_certificates':filtered_certificates,
            'status':'passed; no family infeasibility inferred'}


def main():
    argparse.ArgumentParser().parse_args()
    print(json.dumps(certificate_audit(),indent=2))
if __name__=='__main__':main()
