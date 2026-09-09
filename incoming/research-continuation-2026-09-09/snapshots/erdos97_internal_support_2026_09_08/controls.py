"""An exact rational positive control for the seed-specific hypothesis.

All four designated cap vertices are rich, with exactly one internally
supported vertex, over a *different* ten-point old seed. Not an Erdos97
counterexample: all ten old vertices have maximum multiplicity one.
"""
from collections import defaultdict
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import argparse,json,math,sys
if sys.flags.optimize:raise RuntimeError('Do not disable exact assertions')
ROOT=Path(__file__).resolve().parent
ORDER=[7,0,11,12,13,1,8,9,10,2,4,3,5,6]


def add(a,b):return a[0]+b[0],a[1]+b[1]
def sub(a,b):return a[0]-b[0],a[1]-b[1]
def norm(a):return a[0]*a[0]+a[1]*a[1]
def distance(a,b):return norm(sub(a,b))
def orientation(a,b,c):
    u,v=sub(b,a),sub(c,a)
    return u[0]*v[1]-u[1]*v[0]
def rotate(p,t):
    if isinstance(t,float):raise TypeError('exact rational rotation requires exact input')
    t=F(t);x,y=p;d=1+t*t
    return ((1-t*t)*x-2*t*y)/d,(2*t*x+(1-t*t)*y)/d


def points():
    p=[(F(0),F(0)),(F(1),F(0)),(F(3,5),F(4,5)),(F(0),F(1))]
    p.append(rotate(p[2],F(1,100)))
    for center,target in ((1,3),(3,1),(2,0)):
        for k in (1,2,3):p.append(add(p[center],rotate(sub(p[target],p[center]),F(k,100))))
    return p


def classes(P,i):
    result=defaultdict(list)
    for j,q in enumerate(P):
        if j!=i:
            d=distance(P[i],q)
            if d<=0:raise ValueError('distinct points required')
            result[d].append(j)
    return result


def strict(P,order):
    if sorted(order)!=list(range(len(P))):raise ValueError('invalid boundary permutation')
    for i,j in combinations(range(len(P)),2):
        if distance(P[i],P[j])<=0:raise ValueError('coincident vertices')
    signs=[orientation(P[order[k]],P[order[(k+1)%len(P)]],P[j])
           for k in range(len(P)) for j in range(len(P)) if j not in (order[k],order[(k+1)%len(P)])]
    if min(signs)<=0:raise ValueError('not strict convex position in this order')
    return signs


def generate():
    P=points();signs=strict(P,ORDER)
    rows=[];maxima=[];internal=[]
    for i in range(len(P)):
        C=classes(P,i);maxima.append(max(map(len,C.values())))
        rich=[(r,S) for r,S in C.items() if len(S)>=4]
        if i<4:
            if not rich:raise AssertionError('cap point not rich')
            if all(sum(j>=4 for j in S)<=1 for r,S in rich):internal.append(i)
        for r,S in sorted(rich):rows.append({'center':i,'squared_radius':str(r),'witnesses':S,
                                            'old_witnesses':[j for j in S if j>=4],
                                            'new_witnesses':[j for j in S if j<4]})
    assert maxima==[4]*4+[1]*10 and internal==[0]
    return {'status':'exact positive control on a different seed; not a counterexample',
            'points':[[str(c) for c in p] for p in P],'old_labels':list(range(4,14)),
            'new_labels':list(range(4)),'order':ORDER,'supporting_checks':len(signs),
            'distinct_pair_checks':math.comb(len(P),2),'minimum_supporting_determinant':str(min(signs)),
            'maxima':maxima,'rich_classes':rows,'internally_supported_new_vertices':internal}


def homogeneous_check(report):
    """Separate arithmetic: integer homogeneous coordinates, no geometry helpers."""
    pts=[]
    for p in report['points']:
        if len(p)!=2 or any(not isinstance(x,str) for x in p):raise ValueError('rational strings required')
        x,y=map(F,p);d=math.lcm(x.denominator,y.denominator)
        pts.append((int(x*d),int(y*d),d))
    n=len(pts);order=report['order']
    if sorted(order)!=list(range(n)):raise ValueError('invalid order')
    determinants=[]
    for k,i in enumerate(order):
        j=order[(k+1)%n]
        a,b=pts[i],pts[j]
        for h,c in enumerate(pts):
            if h in (i,j):continue
            v=a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])
            if v<=0:raise ValueError('nonpositive integer homogeneous determinant')
            determinants.append(F(v,a[2]*b[2]*c[2]))
    all_classes=[];maxima=[];rows=[]
    for i,(x,y,d) in enumerate(pts):
        bins={}
        for j,(u,v,e) in enumerate(pts):
            if i==j:continue
            r=F((x*e-u*d)**2+(y*e-v*d)**2,d*d*e*e)
            if r<=0:raise ValueError('coincident homogeneous vertices')
            bins.setdefault(r,[]).append(j)
        all_classes.append(bins);maxima.append(max(map(len,bins.values())))
        for r,S in sorted(bins.items()):
            if len(S)>=4:rows.append({'center':i,'squared_radius':str(r),'witnesses':S,
                'old_witnesses':[j for j in S if j in report['old_labels']],
                'new_witnesses':[j for j in S if j in report['new_labels']]})
    internal=[i for i in report['new_labels'] if any(len(S)>=4 for S in all_classes[i].values()) and
              all(len(set(S)&set(report['old_labels']))<=1 for S in all_classes[i].values() if len(S)>=4)]
    if maxima!=report['maxima'] or rows!=report['rich_classes']:raise ValueError('incorrect census')
    if internal!=report['internally_supported_new_vertices']:raise ValueError('incorrect internal classification')
    if len(determinants)!=report['supporting_checks'] or str(min(determinants))!=report['minimum_supporting_determinant']:
        raise ValueError('incorrect supporting report')
    if math.comb(n,2)!=report['distinct_pair_checks']:raise ValueError('incorrect distinctness count')
    return {'status':'passed','arithmetic':'integer homogeneous determinants and squared-distance ratios',
            'vertices':n,'supporting_checks':len(determinants),'maxima':maxima}


def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
    r=generate();homogeneous_check(r);text=json.dumps(r,indent=2,sort_keys=True)+'\n'
    path=ROOT/'data/positive_control.json'
    if a.write:path.write_text(text)
    elif path.read_text()!=text:raise AssertionError('control report differs')
    print(json.dumps(homogeneous_check(r),indent=2))
if __name__=='__main__':main()
