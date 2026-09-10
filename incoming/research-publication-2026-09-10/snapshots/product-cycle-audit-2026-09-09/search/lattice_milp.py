"""Bounded finite lattice-pool search. Solver statuses are diagnostics, not proofs.
Geometry is encoded by every collinear triple and nonconvex quadruple.
A positive result is rechecked using exact integer arithmetic.
"""
from itertools import combinations
from collections import defaultdict
from pathlib import Path
import json,argparse,time,platform
import numpy as np
import scipy
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import coo_matrix
from lattice_core_probe import possible

def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def certify(P):
    n=len(P);order=sorted(range(n),key=lambda i:P[i]);lo=[];hi=[]
    for it,out in [(order,lo),(list(reversed(order)),hi)]:
        for i in it:
            while len(out)>1 and cross(P[out[-2]],P[out[-1]],P[i])<=0:out.pop()
            out.append(i)
    hull=lo[:-1]+hi[:-1]
    if len(hull)!=n:return None
    rows=[]
    for i,p in enumerate(P):
        groups=defaultdict(list)
        for j,q in enumerate(P):
            if i!=j:groups[(p[0]-q[0])**2+(p[1]-q[1])**2].append(j)
        rich=[(r,w)for r,w in groups.items()if r>0 and len(w)>=4]
        if not rich:return None
        r,w=rich[0];rows.append({'center':i,'squared_radius':r,'witnesses':w[:4]})
    support=[cross(P[hull[i]],P[hull[(i+1)%n]],P[j])for i in range(n)for j in range(n)if j not in (hull[i],hull[(i+1)%n])]
    if not all(s>0 for s in support):raise ValueError('hull/support inconsistency')
    return {'points':P,'order':hull,'witnesses':rows,'minimum_support':min(support),'support_count':len(support)}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--side',type=int,default=7);ap.add_argument('--seconds',type=float,default=30);ap.add_argument('--minimum',type=int,default=9);ap.add_argument('--output',required=True);args=ap.parse_args()
    start=time.monotonic();P=[(x,y)for x in range(args.side)for y in range(args.side)];N=len(P);keep=set(range(N));groups=[];bycenter=[[]for _ in P]
    for i,p in enumerate(P):
        g=defaultdict(list)
        for j,q in enumerate(P):
            if i!=j:g[(p[0]-q[0])**2+(p[1]-q[1])**2].append(j)
        for r,ws in g.items():
            if possible(P,i,ws,keep):bycenter[i].append(N+len(groups));groups.append((i,r,ws))
    rr=[];cc=[];vv=[];lb=[];ub=[]
    def con(coefs,low=-np.inf,up=np.inf):
        idx=len(lb)
        for j,v in coefs:rr.append(idx);cc.append(j);vv.append(v)
        lb.append(low);ub.append(up)
    for i,rows in enumerate(bycenter):con([(i,-1)]+[(r,1)for r in rows],low=0)
    for k,(i,_,ws) in enumerate(groups):
        y=N+k;con([(y,1),(i,-1)],up=0);con([(y,4)]+[(j,-1)for j in ws],up=0)
    con([(i,1)for i in range(N)],low=args.minimum)
    orient={}
    collinear=0;nonconvex=0
    for a,b,c in combinations(range(N),3):
        z=cross(P[a],P[b],P[c]);orient[a,b,c]=(z>0)-(z<0)
        if z==0:con([(a,1),(b,1),(c,1)],up=2);collinear+=1
    for a,b,c,d in combinations(range(N),4):
        abc=orient[a,b,c];abd=orient[a,b,d];acd=orient[a,c,d];bcd=orient[b,c,d]
        if 0 in (abc,abd,acd,bcd):continue
        # Alternating affine-dependence coefficients. 1/3 signs means containment.
        signs=(bcd,-acd,abd,-abc)
        count=sum(x>0 for x in signs)
        if count in (1,3):con([(a,1),(b,1),(c,1),(d,1)],up=3);nonconvex+=1
    V=N+len(groups);A=coo_matrix((np.array(vv,dtype=float),(np.array(rr,dtype=np.int32),np.array(cc,dtype=np.int32))),shape=(len(lb),V)).tocsc()
    obj=np.zeros(V);obj[:N]=1
    build=time.monotonic()-start
    res=milp(obj,integrality=np.ones(V,dtype=np.int32),bounds=Bounds(np.zeros(V),np.ones(V)),constraints=LinearConstraint(A,lb,ub),options={'time_limit':args.seconds,'mip_rel_gap':0.0})
    selected=[i for i in range(N)if res.x is not None and res.x[i]>.5]
    exact=certify([P[i]for i in selected])if selected else None
    report={'scope':'finite integer-coordinate pool search; no global or exact infeasibility claim','side':args.side,'minimum_size':args.minimum,'pool_size':N,'active_distance_groups':len(groups),'collinear_triples':collinear,'nonconvex_quadruples':nonconvex,'variables':V,'constraints':len(lb),'solver_status':int(res.status),'solver_message':res.message,'solver_time_limit':args.seconds,'objective':float(res.fun)if res.fun is not None else None,'selected_labels':selected,'exact_positive_certificate':exact,'build_seconds':build,'total_seconds':time.monotonic()-start,'scipy':scipy.__version__,'python':platform.python_version()}
    Path(args.output).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
