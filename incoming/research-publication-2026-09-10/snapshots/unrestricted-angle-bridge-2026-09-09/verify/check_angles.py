"""Standard-library certificate checker. Imports no optimizer or search module."""
from __future__ import annotations
from fractions import Fraction as F
from itertools import combinations
import argparse,json
from pathlib import Path


def constraints(n,rows):
    if not isinstance(n,int) or n<3:raise ValueError('bad point count')
    chords=list(combinations(range(n),2));index={v:k for k,v in enumerate(chords)}
    angles=[];equations=[]
    def vec(terms):
        result=[0]*len(chords)
        for chord,coefficient in terms:result[index[tuple(sorted(chord))]]+=coefficient
        return result
    for a,b,c in combinations(range(n),3):
        angles.extend([
            (vec([((a,c),1),((a,b),-1)]),0),
            (vec([((b,c),1),((a,c),-1)]),0),
            (vec([((a,b),1),((b,c),-1)]),1)])
    for apex,targets in sorted((int(k),v) for k,v in rows.items()):
        if apex<0 or apex>=n or len(targets)!=len(set(targets)) or apex in targets:raise ValueError('invalid row')
        if any(not isinstance(x,int) or x<0 or x>=n for x in targets):raise ValueError('invalid target')
        for u,v in combinations(sorted(targets),2):
            s=sorted([apex,u,v]);a,b,c=s
            # Equality of the two base angles in triangle (apex,u,v).
            if apex==a:
                terms=[((a,b),1),((a,c),1),((b,c),-2)];rhs=-1
            elif apex==b:
                terms=[((a,b),1),((b,c),1),((a,c),-2)];rhs=0
            else:
                terms=[((a,c),1),((b,c),1),((a,b),-2)];rhs=1
            equations.append((vec(terms),rhs))
    equations.append((vec([((0,1),1)]),0))
    return angles,equations


def parse_weights(items,limit,nonnegative=False):
    result=[];seen=set()
    for i,s in items:
        if not isinstance(i,int) or not 0<=i<limit or i in seen:raise ValueError('bad/duplicate index')
        seen.add(i);v=F(s)
        if not v or (nonnegative and v<0):raise ValueError('invalid weight')
        result.append((i,v))
    return result


def check(n,rows,certificate):
    angles,equations=constraints(n,rows)
    v=parse_weights(certificate['equality_weights'],len(equations))
    coefficients=[F(0)]*len(equations[0][0])
    for i,w in v:
        for j,x in enumerate(equations[i][0]):coefficients[j]+=w*x
    if certificate['kind']=='inconsistent-equalities':
        value=sum(w*equations[i][1] for i,w in v)
        if any(coefficients) or not value or value!=F(certificate['constant']):raise ValueError('invalid equality contradiction')
        return True
    if certificate['kind']!='strict-positive-angle-contradiction':raise ValueError('unknown certificate kind')
    u=parse_weights(certificate['angle_weights'],len(angles),True)
    if not u:raise ValueError('strictness has no positive coefficient')
    for i,w in u:
        for j,x in enumerate(angles[i][0]):coefficients[j]+=w*x
    value=sum(w*angles[i][1] for i,w in u)-sum(w*equations[i][1] for i,w in v)
    if any(coefficients) or value>0 or value!=F(certificate['constant']):raise ValueError('invalid angle contradiction')
    return True


def check_feasible(n,rows,beta):
    angles,eqs=constraints(n,rows);beta=list(map(F,beta))
    if len(beta)!=len(eqs[0][0]):raise ValueError('wrong variable count')
    if any(sum(x*y for x,y in zip(co,beta))!=rhs for co,rhs in eqs):raise ValueError('equality failure')
    m=min(sum(x*y for x,y in zip(co,beta))+rhs for co,rhs in angles)
    if m<=0:raise ValueError('nonpositive angle')
    return m

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('path',type=Path);args=p.parse_args()
    data=json.loads(args.path.read_text());count=0;feasible=0
    for case in data['cases']:
        r=case['result']
        if 'certificate'in r:check(case['n'],case['rows'],r['certificate']);count+=1
        elif r['classification']=='EXACT_ANGLE_RELAXATION_FEASIBLE' and 'chord_directions_over_pi'in r:
            check_feasible(case['n'],case['rows'],r['chord_directions_over_pi']);feasible+=1
    print(json.dumps({'verified_contradictions':count,'verified_abstract_angle_solutions':feasible,'euclidean_realizations_verified':0}))
