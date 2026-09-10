"""Exact Q(sqrt(3)) control construction. Verification is in a separate module."""
from fractions import Fraction as F
from pathlib import Path
import sys,json,math
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'verify'))
from q3_field import Q3
S=Q3(0,1);OM=(Q3(F(-1,2)),Q3(0,F(1,2)))
def add(a,b):return(a[0]+b[0],a[1]+b[1])
def mul(a,b):return(a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
def scalar(a,s):return(a[0]*s,a[1]*s)
def U(t):return(Q3((1-t*t)/(1+t*t)),Q3(2*t/(1+t*t)))
def M(t):return add((Q3(1),Q3(0)),scalar(U(t),S))
def orbits(z):
    out=[]
    for a in z:
        for _ in range(3):out.append(a);a=mul(a,OM)
    return out

def record(name,z,rows,extra=None):
    P=orbits(z)
    def approx(x):return float(x.a)+float(x.b)*math.sqrt(3)
    order=sorted(range(len(P)),key=lambda i:math.atan2(approx(P[i][1]),approx(P[i][0])))
    data={'kind':name,'coordinates':[[x.dump(),y.dump()]for x,y in P],'cyclic_order':order,'orbit_representatives':[[x.dump(),y.dump()]for x,y in z],'own_side_source_rows':rows,'own_side_arrows':[[[j,2 if name=='supplier_arc_positive_12' and i==1 and j==2 else 0]for j in row]for i,row in enumerate(rows)],'all_rich_claim':False,'extra':extra or {}}
    (ROOT/'candidate_counterexamples'/f'{name}.json').write_text(json.dumps(data,indent=2)+'\n')
    return data

def main():
    # Parameters are fixed rationals, reconstructed once from the retained numerical probe.
    parents=[0,0,1,1,2,2]
    ts=list(map(F,['-106087/7633','28301/5800','-23875/9169','-23235/9274','111260/8739','26484/8219']))
    z=[(Q3(1),Q3(0))]
    for i,t in zip(parents,ts):z.append(mul(z[i],M(t)))
    record('c3_maximum_root_rich_neighborhood_21',z,[[1,2],[3,4],[5,6],[],[],[],[]],{'parameters':[str(t)for t in ts],'parents':parents,'expected_rich_orbits':[0,1,2],'root_is_global_maximum_norm':True})
    def Q(t):return add(OM,mul(add((Q3(1),Q3(0)),scalar(OM,-1)),U(t)))
    C=Q(F(1,100));D=scalar(Q(F(1,50)),F(100000001,100000000));AP=Q(F(3,100));A=mul(mul(AP,OM),OM)
    record('supplier_arc_positive_12',[A,(Q3(1),Q3(0)),C,D],[[],[0,2],[],[]],{'gains':[[0,0],[2,2]],'forced_radial_order':[2,3],'third_arrow_forbidden':[2,3,1]})
    a,b=M(F(8,3)),M(F(5,2))
    record('convex_product_diamond_positive_12',[(Q3(1),Q3(0)),a,b,mul(a,b)],[[1,2],[3],[3],[]],
           {'sector_old_orbits':[0,3,2,1],'sector_rep_rotations':[0,2,0,0],
            'sector_rows':[[3,0,2,0],[],[1,1],[1,1]],
            'phase_relaxation_vector_L_1':['0','11/20','3/4','4/5']})
    print('max-root parameters',list(map(str,ts)))
if __name__=='__main__':main()
