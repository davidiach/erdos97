"""C3 chord-angle discovery model, adapted from c3_eight_angles.py at 9b8b8f.
A solution is necessary, not sufficient, for geometric realization.
Each orbit row may be partial. Rotational and source-side hypotheses required.
"""
from itertools import combinations
from math import gcd
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import csr_matrix, hstack

def model(rows, ordered=True, right=True):
    m=len(rows); n=3*m; pairs=list(combinations(range(n),2))
    def key(a,b):
        i,j=a%m,b%m; p,q=a//m,b//m
        return (i,) if i==j else (i,j,(q-p)%3) if i<j else (j,i,(p-q)%3)
    reps={}
    for a,b in pairs:reps.setdefault(key(a,b),(a,b))
    ids={v:i for i,v in enumerate(reps)}; k=len(ids); dim=k+1
    cls={p:ids[key(*p)] for p in pairs}
    eta={p:(sum(p)-sum(reps[key(*p)]))//m for p in pairs}
    def cl(a,b):return cls[tuple(sorted((a,b)))]
    length=list(range(k))
    def find(x):
        while length[x]!=x:
            length[x]=length[length[x]];x=length[x]
        return x
    def join(a,b):length[find(a)]=find(b)
    own=[cl(i,i+m) for i in range(m)]
    for i,row in enumerate(rows):
        for j,g in zip(row[::2],row[1::2]):join(cl(i,j+g*m),own[i])
    length=[find(i) for i in range(k)]
    less=set()
    for i,row in enumerate(rows):
        for j,g in zip(row[::2],row[1::2]):
            off=(j+g*m-i)%n
            less.add((length[own[j]],length[own[i]]) if m<off<2*m else (length[own[i]],length[own[j]]))
    A=[];E=[];al=[];el=[];cache={}
    def angle(a,b,c):
        ret=[]
        for cs,base in [([((a,c),1),((a,b),-1)],0),([((a,b),1),((b,c),-1)],3),([((b,c),1),((a,c),-1)],0)]:
            v=np.zeros(dim,dtype=np.int64);v[-1]=base
            for p,s in cs:v[cls[p]]+=s;v[-1]+=s*eta[p]
            ret.append(v)
        return ret
    for tri in combinations(range(n),3):
        ang=angle(*tri);cache[tri]=ang
        for t,v in enumerate(ang):A.append(v);al.append(['angle_positive',*tri,t])
        a,b,c=tri;op=[length[cl(b,c)],length[cl(a,c)],length[cl(a,b)]]
        for i,j in combinations(range(3),2):
            if op[i]==op[j]:E.append(ang[i]-ang[j]);el.append(['equal_sides',*tri,i,j])
            elif ordered:
                if (op[i],op[j]) in less:A.append(ang[j]-ang[i]);al.append(['angle_order',*tri,i,j])
                elif (op[j],op[i]) in less:A.append(ang[i]-ang[j]);al.append(['angle_order',*tri,j,i])
    v=np.zeros(dim,dtype=np.int64);v[-1]=1;A.append(v);al.append(['pi_positive'])
    if right:
        for i,row in enumerate(rows):
            for j,g in zip(row[::2],row[1::2]):
                tri=tuple(sorted((i,j+(g+1)%3*m,j+(g+2)%3*m)))
                v=2*cache[tri][tri.index(i)];v=v.copy();v[-1]-=3;E.append(v);el.append(['right_angle',i,j,g])
    def norm(v,eq):
        g=0
        for x in v:g=gcd(g,int(x))
        if not g:return None
        if eq and next(x for x in v if x)<0:g=-g
        return tuple(int(x)//g for x in v)
    def dedup(mat,labs,eq):
        seen={}
        for v,lab in zip(mat,labs):
            t=norm(v,eq)
            if t is not None:seen.setdefault(t,lab)
        return np.array(list(seen),dtype=np.int64).reshape(-1,dim),list(seen.values())
    A,al=dedup(A,al,False);E,el=dedup(E,el,True)
    return A,E,al,el

def margin(rows, ordered=True, right=True, time_limit=10.0, presolve=True):
    A,E,al,el=model(rows,ordered,right);dim=A.shape[1]
    obj=np.zeros(dim+1);obj[-1]=-1
    ae=np.zeros((len(E)+1,dim+1));ae[:-1,:dim]=E;ae[-1,dim-1]=1
    be=np.zeros(len(E)+1);be[-1]=1
    au=hstack([csr_matrix(-A),csr_matrix(np.ones((len(A),1)))],format='csr')
    result=linprog(obj,A_ub=au,b_ub=np.zeros(len(A)),A_eq=csr_matrix(ae),b_eq=be,bounds=[(None,None)]*(dim+1),method='highs',options={'time_limit':float(time_limit),'presolve':bool(presolve)})
    return result,(A,E,al,el)
