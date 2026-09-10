"""Unrestricted-incidence search on finite integer-coordinate pools.
Only removes vertices lacking a four-witness row in an open angular half-plane.
A surviving pool is not a convex polygon. A failed finite pool is not a global bound.
"""
from collections import defaultdict
from itertools import combinations
from pathlib import Path
import argparse,json,time

def possible(P,i,group,keep):
    g=[j for j in group if j in keep]
    if len(g)<4:return False
    x,y=P[i]
    for a in g:
        u,v=P[a][0]-x,P[a][1]-y
        count=1
        for b in g:
            s,t=P[b][0]-x,P[b][1]-y
            if u*t-v*s>0:count+=1
        if count>=4:return True
    return False

def core(P):
    rows=[]
    for i,p in enumerate(P):
        g=defaultdict(list)
        for j,q in enumerate(P):
            if i!=j:g[(p[0]-q[0])**2+(p[1]-q[1])**2].append(j)
        rows.append([(r,ns)for r,ns in g.items()if len(ns)>=4])
    keep=set(range(len(P)));rounds=[]
    while keep:
        nex={i for i in keep if any(possible(P,i,g,keep)for _,g in rows[i])}
        rounds.append({'before':len(keep),'removed':sorted(keep-nex)})
        if nex==keep:break
        keep=nex
    return {'pool_size':len(P),'retained_size':len(keep),'retained':sorted(keep),'rounds':rounds}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--max-side',type=int,default=20);ap.add_argument('--output',required=True);args=ap.parse_args()
    records=[];start=time.monotonic()
    for L in range(6,args.max_side+1):
        P=[(x,y)for x in range(L)for y in range(L)]
        rec={'pool':'integer_square','side_points':L,**core(P)};records.append(rec)
        Path(args.output).write_text(json.dumps({'scope':'finite-pool exact local elimination only','records':records,'seconds':time.monotonic()-start},indent=2)+'\n')
        print(L,rec['pool_size'],rec['retained_size'],len(rec['rounds']),flush=True)
if __name__=='__main__':main()
