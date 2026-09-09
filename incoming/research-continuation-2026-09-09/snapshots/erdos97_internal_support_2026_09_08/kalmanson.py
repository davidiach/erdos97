"""Exact ordinary-distance convex-quadrilateral certificates.

A certificate is a positive integer sum of strict crossing inequalities. Its
chord coefficients cancel after *only* the named selected-witness equalities.
The checker uses standard-library integer arithmetic, never a solver status.
"""
from collections import Counter
from itertools import combinations
from pathlib import Path
import argparse
import json
import math
import sys

if sys.flags.optimize:
    raise RuntimeError('Do not disable exact-check assertions')
ROOT=Path(__file__).resolve().parent


def validate_rows(rows,order):
    n=len(rows)
    if sorted(order)!=list(range(n)) or any(type(x) is not int for x in order):
        raise ValueError('not a labelled boundary permutation')
    for i,row in enumerate(rows):
        if (len(row)!=4 or len(set(row))!=4 or i in row or
            any(type(j) is not int or not 0<=j<n for j in row)):
            raise ValueError('not a four-witness row')


def quotient(rows,selected=None):
    n=len(rows); pairs=list(combinations(range(n),2)); parent={p:p for p in pairs}
    def find(p):
        while parent[p]!=p:
            parent[p]=parent[parent[p]];p=parent[p]
        return p
    for i in (range(n) if selected is None else selected):
        first=tuple(sorted((i,rows[i][0])))
        for j in rows[i][1:]:
            p=find(first);q=find(tuple(sorted((i,j))))
            if p!=q:parent[q]=p
    roots=sorted({find(p) for p in pairs});ids={p:i for i,p in enumerate(roots)}
    return {p:ids[find(p)] for p in pairs}


def terms(quad,kind):
    a,b,c,d=quad
    positives=[(a,c),(b,d)]
    if kind==0:negatives=[(a,b),(c,d)]
    elif kind==1:negatives=[(a,d),(b,c)]
    else:raise ValueError('invalid quadrilateral inequality')
    return [(tuple(sorted(p)),s) for pairs,s in ((positives,1),(negatives,-1)) for p in pairs]


def reduced_sum(rows,records,selected=None):
    classes=quotient(rows,selected); result=Counter()
    for record in records:
        w=record['weight']
        if type(w) is not int or w<=0:raise ValueError('weight must be a positive integer')
        for chord,s in terms(record['quadruple'],record['kind']):result[classes[chord]]+=w*s
    return {k:v for k,v in result.items() if v}


def validate_certificate(rows,order,certificate):
    validate_rows(rows,order);n=len(rows);rank={x:i for i,x in enumerate(order)}
    selected=certificate['selected_centers']
    if (selected!=sorted(set(selected)) or not selected or
        any(type(i) is not int or not 0<=i<n for i in selected)):
        raise ValueError('invalid selected equality rows')
    records=certificate['inequalities']
    if not records:raise ValueError('empty positive sum')
    for r in records:
        q=r['quadruple']
        if len(q)!=4 or len(set(q))!=4 or any(type(x) is not int or x not in rank for x in q):
            raise ValueError('invalid quadruple')
        positions=[(rank[x]-rank[q[0]])%n for x in q]
        if positions!=sorted(positions):raise ValueError('not cyclic order')
    if reduced_sum(rows,records,selected):raise ValueError('coefficients do not cancel exactly')
    return True


def minimize_dependencies(rows,order,records):
    selected=list(range(len(rows)))
    if reduced_sum(rows,records,selected):raise ValueError('not an obstruction')
    for i in list(reversed(selected)):
        trial=[j for j in selected if j!=i]
        if not reduced_sum(rows,records,trial):selected=trial
    certificate={'selected_centers':selected,'inequalities':records}
    validate_certificate(rows,order,certificate)
    return certificate


def constraints(rows,order):
    validate_rows(rows,order);classes=quotient(rows);out=[]
    for inds in combinations(range(len(order)),4):
        q=[order[i] for i in inds]
        for kind in (0,1):
            coefficients=Counter()
            for chord,s in terms(q,kind):coefficients[classes[chord]]+=s
            out.append((q,kind,{i:v for i,v in coefficients.items() if v}))
    return classes,out


def discover(rows,order,time_limit=15):
    """Find an exact obstruction or exact feasible relaxation, if either is certified.

    SciPy is an optional discovery tool. Every returned mathematical object is
    rechecked using rational/integer arithmetic below; timeout is inconclusive.
    """
    from fractions import Fraction
    import numpy as np
    from scipy.sparse import coo_array
    from scipy.optimize import linprog
    classes,C=constraints(rows,order)
    zero=[{'quadruple':q,'kind':kind,'weight':1} for q,kind,c in C if not c]
    if zero:
        return {'status':'exact obstruction','certificates':[
            minimize_dependencies(rows,order,[r]) for r in zero]}
    m=max(classes.values())+1;ri=[];ci=[];data=[]
    for j,(_,_,coeff) in enumerate(C):
        for i,v in coeff.items():ri.append(i);ci.append(j);data.append(v)
        ri.append(m);ci.append(j);data.append(1)
    mat=coo_array((np.asarray(data,dtype=float),(ri,ci)),shape=(m+1,len(C))).tocsc()
    rhs=np.zeros(m+1);rhs[-1]=1
    sol=linprog(np.arange(len(C))/len(C),A_eq=mat,b_eq=rhs,bounds=(0,None),
                method='highs',options={'time_limit':time_limit})
    if sol.x is not None:
        values={j:Fraction(float(x)).limit_denominator(1000000) for j,x in enumerate(sol.x) if x>1e-9}
        denominator=math.lcm(*(v.denominator for v in values.values()))
        records=[{'quadruple':C[j][0],'kind':C[j][1],'weight':int(v*denominator)} for j,v in values.items()]
        if records and not reduced_sum(rows,records):
            g=math.gcd(*(r['weight'] for r in records))
            for r in records:r['weight']//=g
            return {'status':'exact obstruction','certificates':[minimize_dependencies(rows,order,records)]}
    if sol.status!=2:
        return {'status':'unresolved','solver_status':int(sol.status),'message':sol.message}
    # An exact positive-distance feasible point of the *linear relaxation*.
    A=mat[:m,:].T.tocsc()
    primal=linprog(np.zeros(m),A_ub=-A,b_ub=-np.ones(len(C)),bounds=(1,None),
                   method='highs',options={'time_limit':time_limit})
    if primal.x is not None:
        x=[Fraction(float(v)).limit_denominator(1000000) for v in primal.x]
        if min(x)>0 and all(sum(x[i]*v for i,v in c.items())>0 for _,_,c in C):
            return {'status':'exact feasible linear relaxation','class_distances':[str(v) for v in x],
                    'not_a_euclidean_realization':True}
    return {'status':'unresolved','solver_status':int(primal.status),'message':primal.message}


def audit_saved():
    data=json.loads((ROOT/'data/moving_pattern_obstructions.json').read_text())
    for item in data['patterns']:
        for c in item['certificates']:validate_certificate(item['rows'],item['order'],c)
    return {'fixed_patterns':len(data['patterns']),
            'certificates':sum(len(item['certificates']) for item in data['patterns']),
            'status':'all checked exactly; fixed-pattern fixed-order only'}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--audit',action='store_true');parser.parse_args()
    print(json.dumps(audit_saved(),indent=2))
if __name__=='__main__':main()
