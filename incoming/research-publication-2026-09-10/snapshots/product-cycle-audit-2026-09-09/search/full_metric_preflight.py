"""Full ordinary-distance Kalmanson cone, triangle inequalities, and radius orders.
Floating discovery, exact coefficient certificate reconstruction before rejection.
"""
from pathlib import Path
from itertools import combinations
import sys,json,time
from fractions import Fraction as F
from math import gcd,lcm
import numpy as np
from scipy.sparse import csr_matrix,hstack,vstack
from scipy.optimize import linprog
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'verify'))
from check_c3 import Geometry
from probe_angle_survivors import radial

def model(rows):
    g=Geometry(rows);reps=sorted(set(g.length.values()));ids={p:i for i,p in enumerate(reps)};K=len(reps)
    def cl(a,b):return ids[g.length[tuple(sorted((a,b)))]]
    pool={}
    def add(terms,label):
        v=[0]*K
        for i,a in terms:v[i]+=a
        d=0
        for a in v:d=gcd(d,a)
        if d:v=tuple(a//d for a in v)
        else:v=tuple(v)
        pool.setdefault(v,label)
    for i in range(K):add([(i,1)],['positive',*reps[i]])
    for a,b,c,d in combinations(range(g.n),4):
        add([(cl(a,c),1),(cl(b,d),1),(cl(a,b),-1),(cl(c,d),-1)],['kalmanson',a,b,c,d,0])
        add([(cl(a,c),1),(cl(b,d),1),(cl(a,d),-1),(cl(b,c),-1)],['kalmanson',a,b,c,d,1])
    for a,b,c in combinations(range(g.n),3):
        for x,y,z in [(a,b,c),(b,a,c),(c,a,b)]:add([(cl(x,y),1),(cl(x,z),1),(cl(y,z),-1)],['triangle',x,y,z])
    # Direct arrow strict radius orders; transitivity is already enforced by positive differences.
    for a,b in g.less:add([(cl(b,b+g.m),1),(cl(a,a+g.m),-1)],['radius',a,b])
    # New supplier-arc edges, all strict; maximum-root assumptions handled separately as weak rows.
    rd=radial(rows,True)
    for a,b,why in rd['edges']:
        if why['kind']=='supplier_arc':add([(cl(b,b+g.m),1),(cl(a,a+g.m),-1)],['supplier_arc_radius',why])
    A=np.asarray(list(pool),dtype=np.int64);labs=list(pool.values());weak=[];wlabs=[]
    for i in range(1,g.m):
        v=np.zeros(K,dtype=np.int64);v[cl(0,g.m)]+=1;v[cl(i,i+g.m)]-=1;weak.append(v);wlabs.append(['maximum_root',i])
    return A,np.array(weak),labs,wlabs,reps

def solve(rows):
    A,W,al,wl,reps=model(rows);K=A.shape[1]
    # For a positive homogeneous cone, normalize all distance-class variables to sum to one.
    objective=np.zeros(K+1);objective[-1]=-1
    strict=hstack([csr_matrix(-A),csr_matrix(np.ones((len(A),1)))],format='csr')
    weak=hstack([csr_matrix(-W),csr_matrix((len(W),1))],format='csr')
    eq=np.ones((1,K+1));eq[0,-1]=0
    r=linprog(objective,A_ub=vstack([strict,weak]),b_ub=np.zeros(len(A)+len(W)),A_eq=eq,b_eq=[1],bounds=[(None,None)]*(K+1),method='highs',options={'time_limit':10,'presolve':False})
    ans={'status':int(r.status),'message':r.message,'class_count':K,'strict_rows':len(A),'weak_rows':len(W),'representatives':reps}
    if r.success:
        ans['numerical_margin']=float(r.x[-1]);v=[F(float(x)).limit_denominator(10000000)for x in r.x[:-1]]
        sv=[sum(int(x)*y for x,y in zip(row,v))for row in A];wv=[sum(int(x)*y for x,y in zip(row,v))for row in W]
        ans.update({'rational_vector':list(map(str,v)),'exact_positive':min(sv)>0 and min(wv)>=0 and sum(v)==1,'minimum_strict':str(min(sv)),'minimum_weak':str(min(wv))})
        if r.x[-1]<=1e-8:
            lam=[F(float(-x)).limit_denominator(10000000)for x in r.ineqlin.marginals[:len(A)]]
            mu=[F(float(-x)).limit_denominator(10000000)for x in r.ineqlin.marginals[len(A):]]
            z=F(float(r.eqlin.marginals[0])).limit_denominator(10000000)
            total=[F(0)]*K
            for mat,vals in [(A,lam),(W,mu)]:
                for row,q in zip(mat,vals):
                    if q:
                        for j in np.flatnonzero(row):total[j]+=q*int(row[j])
            # Stationarity: weighted strict + weak + z*sum_distances =0.
            total=[x+z for x in total]
            if not any(total) and all(x>=0 for x in lam+mu)and z>=0:
                terms=[(lab,x,'strict')for lab,x in zip(al,lam)if x]+[(lab,x,'weak')for lab,x in zip(wl,mu)if x]
                if z:
                    for a,b in reps:terms.append((['positive',a,b],z,'strict'))
                den=lcm(*(x.denominator for _,x,_ in terms));gc=gcd(*(int(x*den)for _,x,_ in terms))
                ans['certificate']={kind:[[lab,int(x*den)//gc]for lab,x,k in terms if k==kind]for kind in['strict','weak']}
    return ans

if __name__=='__main__':
    inp=json.loads((ROOT/'reports/angle_potential_survivors.json').read_text());out=[]
    for c in inp:
        q={'index':c['index'],'rows':c['rows'],'metric':solve(c['rows'])};out.append(q)
        (ROOT/'reports/full_metric_preflight.json').write_text(json.dumps(out,indent=2)+'\n')
        print(c['index'],q['metric'].get('numerical_margin'),q['metric'].get('exact_positive'),bool(q['metric'].get('certificate')),flush=True)
