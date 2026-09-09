"""Exact controls for the all-size parallel-parabola finite-cycle theorem."""
from fractions import Fraction as F
from itertools import combinations,product
from pathlib import Path
from collections import Counter
import argparse,json
ROOT=Path(__file__).resolve().parent

def dist(a,b):return sum((x-y)**2 for x,y in zip(a,b))
def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def circumcenter(points):
    p,q,r=points[:3]
    A=[2*(q[i]-p[i])for i in (0,1)];B=[2*(r[i]-p[i])for i in (0,1)]
    u=sum(x*x for x in q)-sum(x*x for x in p);v=sum(x*x for x in r)-sum(x*x for x in p)
    det=A[0]*B[1]-A[1]*B[0]
    if not det:raise ValueError('collinear circumcenter input')
    return (u*B[1]-A[1]*v)/det,(A[0]*v-u*B[0])/det

def row(a,h,c,ts):
    if not all(isinstance(x,F)for x in (a,h,c,*ts)):raise TypeError('exact Fraction inputs required')
    if a==0 or len(ts)!=4 or len(set(ts))!=4 or sum(ts)!=0:raise ValueError('invalid four-root parabola row')
    e2=sum(x*y for x,y in combinations(ts,2));e3=sum(x*y*z for x,y,z in combinations(ts,3))
    center=(h+a*a*e3/2,c+(1-a*a*e2)/(2*a))
    points=[(h+t,a*t*t+c)for t in ts]
    if center!=circumcenter(points):raise ValueError('independent circumcenter disagrees')
    r2=dist(center,points[0])
    if r2<=0 or any(dist(center,p)!=r2 for p in points):raise ValueError('not an exact circle row')
    mean=sum(p[1]for p in points)/4
    if mean!=center[1]-1/(2*a):raise ValueError('Vieta height identity fails')
    return {'curvature':str(a),'horizontal_shift':str(h),'vertical_shift':str(c),
            'parameters':list(map(str,ts)),'center':list(map(str,center)),
            'squared_radius':str(r2),'witness_mean_height':str(mean)}

def control():
    pts=[(F(9),F(12)),(F(-4),F(16)),(F(-2),F(4)),(F(1),F(1)),(F(5),F(25))]
    order=[0,4,1,2,3];signs=[]
    for a,b in zip(order,order[1:]+order[:1]):
        for j in order:
            if j not in (a,b):
                z=cross(pts[a],pts[b],pts[j])
                if z<=0:raise ValueError('positive control is not strictly convex')
                signs.append(z)
    maxima=[max(Counter(dist(p,q)for j,q in enumerate(pts)if j!=i).values())for i,p in enumerate(pts)]
    if maxima!=[4,1,1,1,1]:raise ValueError('wrong positive-control multiplicities')
    return {'points':[[str(x),str(y)]for x,y in pts],'order':order,
            'squared_radius':'185','max_multiplicities':maxima,
            'strict_support_signs':list(map(str,signs)),
            'all_vertices_rich':False}

def verify():
    rows=[]
    for a,h,c,t in product(map(F,[-3,-1,F(-1,2),F(1,3),1,2]),map(F,[0,F(5,7)]),map(F,[-2,3]),[[-4,-2,1,5],[-3,-1,1,3],[-5,-1,2,4],[-7,-2,3,6]]):
        rows.append(row(a,h,c,list(map(F,t))))
    cycles=[]
    for k in range(1,5):
        count=Counter()
        for aa in product([-3,-2,-1,1,2,3],repeat=k):
            drift=-sum(F(1,2*a)for a in aa)
            count['zero'if drift==0 else'positive'if drift>0 else'negative']+=1
        cycles.append({'length':k,'coefficient_tuples':6**k,'drift_counts':dict(count)})
    return {'schema':'erdos97.parallel_parabola_cycle_controls.v1','status':'passed',
       'row_count':len(rows),'rows':rows,'positive_control':control(),
       'cycle_arithmetic_controls':cycles,'all_size_proof_is_in':'proof.md',
       'finite_checks_are_not_an_exhaustive_geometry_proof':True,
       'external_review':False,'formalized':False}

def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--write',action='store_true');a=p.parse_args()
    r=verify();s=json.dumps(r,indent=2,sort_keys=True)+'\n';out=ROOT/'certificate.json'
    if a.check and out.read_text()!=s:raise ValueError('stored controls differ')
    if a.write:out.write_text(s)
    print(json.dumps({'status':r['status'],'rational_rows':r['row_count'],'positive_control':r['positive_control'],'cycles':r['cycle_arithmetic_controls']},indent=2))
if __name__=='__main__':main()
