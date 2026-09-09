"""Exploratory free-coordinate, witness-switching search.
All numerical outputs are diagnostics; nothing here certifies feasibility.
Exact preflight uses only integer labels/equality classes, before optimization.
"""
from __future__ import annotations
import json
from itertools import combinations
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from quadratic import base9,repair18
from fractions import Fraction

SEED=970908

def preflight(rows):
    n=len(rows)
    pairs=list(combinations(range(n),2));idx={e:k for k,e in enumerate(pairs)};parent=list(range(len(pairs)))
    def find(k):
        while parent[k]!=k:parent[k]=parent[parent[k]];k=parent[k]
        return k
    def edge(i,j):return find(idx[tuple(sorted((i,j)))])
    for i,row in enumerate(rows):
        if len(set(row))!=4 or i in row:return False,'invalid row'
        a=edge(i,row[0])
        for j in row[1:]:parent[edge(i,j)]=find(a)
    cs=[]
    for i in range(n):
        d={}
        for j in range(n):
            if i!=j:d.setdefault(edge(i,j),set()).add(j)
        cs.append(list(d.values()))
    for i,j in combinations(range(n),2):
        if any(len(a&b)>=3 for a in cs[i] for b in cs[j]):return False,'three common circle witnesses'
    for a,b,c,d in combinations(range(n),4):
        diag=sorted([edge(a,c),edge(b,d)])
        if diag==sorted([edge(a,b),edge(c,d)]) or diag==sorted([edge(a,d),edge(b,c)]):return False,'strict Kalmanson equality'
    return True,'passed'

def choose_rows(X,rng,max_attempts=120):
    n=len(X);D=np.sum((X[:,None]-X[None])**2,axis=2);opts=[]
    for i in range(n):
        order=np.array([j for j in np.argsort(D[i]) if j!=i]);os=[]
        for k in range(n-4):
            w=order[k:k+4];v=D[i,w]
            os.append((float(np.sum((v-v.mean())**2)),tuple(sorted(map(int,w)))))
        os.sort();opts.append(os[:min(8,len(os))])
    counts={}
    for trial in range(max_attempts):
        rows=[]
        for i in range(n):
            os=opts[i]
            # Widen beyond the nearest numerical quartet rather than freeze it.
            probs=np.exp(-np.arange(len(os))/(.6+trial/60));probs/=probs.sum()
            rows.append(os[int(rng.choice(len(os),p=probs))][1])
        ok,why=preflight(rows);counts[why]=counts.get(why,0)+1
        if ok:return np.array(rows),counts
    # A geometry-nearest quartet choice often collapses into an impossible
    # shared-circle system. Start from a label-valid table instead.
    ss=list(combinations(range(1,n),4));rng.shuffle(ss);templates=[]
    for offsets in ss:
        if any(n-a in offsets for a in offsets):continue
        rs=[set((i+a)%n for a in offsets) for i in range(n)]
        viable=True
        for j in range(1,n):
            sh=rs[0]&rs[j]
            if len(sh)>2:viable=False;break
            if len(sh)==2:
                a,b=sorted(sh)
                if not a<j<b:viable=False;break
        if not viable:continue
        rows=np.array([sorted(r) for r in rs])
        ok,why=preflight(rows)
        if not ok:continue
        value=sum(float(np.var(D[i,rows[i]])) for i in range(n))
        templates.append((value,rows))
        if len(templates)>=12:break
    if not templates:return None,counts
    rows=min(templates,key=lambda t:t[0])[1].copy()
    accepted=0
    for _ in range(32):
        i=int(rng.integers(n));trial=rows.copy()
        trial[i]=opts[i][int(rng.integers(min(5,len(opts[i]))))][1]
        if np.var(D[i,trial[i]])>=np.var(D[i,rows[i]]):continue
        ok,why=preflight(trial)
        if ok:rows=trial;accepted+=1
    counts['label-valid fallback templates']=len(templates)
    counts['accepted individual row mutations']=accepted
    assert preflight(rows)[0]
    return rows,counts

def measures(X,rows):
    n=len(X);D=np.sum((X[:,None]-X[None])**2,axis=2)
    edge=np.roll(X,-1,axis=0)-X;delta=X[None,:,:]-X[:,None,:]
    H=edge[:,None,0]*delta[:,:,1]-edge[:,None,1]*delta[:,:,0]
    mask=np.ones((n,n),dtype=bool);mask[np.arange(n),np.arange(n)]=False;mask[np.arange(n),(np.arange(n)+1)%n]=False
    ds=D[np.triu_indices(n,1)]
    V=D[np.arange(n)[:,None],rows]
    return {'max_squared_distance_spread':float(np.max(np.ptp(V,axis=1))),
            'min_support_determinant':float(np.min(H[mask])),
            'min_pair_distance':float(np.sqrt(np.min(ds))),
            'rms_radius':float(np.sqrt(np.mean(np.sum(X*X,axis=1))))}

def optimize(X,rows,minsep,margin,max_nfev=220):
    n=len(X);rr=np.arange(n)[:,None];i,j=np.triu_indices(n,1)
    mask=np.ones((n,n),dtype=bool);mask[np.arange(n),np.arange(n)]=False;mask[np.arange(n),(np.arange(n)+1)%n]=False
    baseline=measures(X,rows)
    # Start from feasible bounds; enforce them as constraints, not penalties.
    floor=max(1e-12,min(margin,baseline['min_support_determinant']/4))
    separation=max(1e-6,min(minsep,baseline['min_pair_distance']/2))
    def objective(flat):
        P=flat.reshape(n,2);V=np.sum((P[:,None,:]-P[rows])**2,axis=2)
        return float(np.sum((V-V.mean(axis=1,keepdims=True))**2))
    def grad(flat):
        P=flat.reshape(n,2);delta=P[:,None,:]-P[rows];V=np.sum(delta**2,axis=2)
        R=V-V.mean(axis=1,keepdims=True);G=np.zeros_like(P)
        for a in range(n):
            for b in range(4):
                g=4*R[a,b]*delta[a,b];G[a]+=g;G[rows[a,b]]-=g
        return G.ravel()
    def inequality(flat):
        P=flat.reshape(n,2);edge=np.roll(P,-1,axis=0)-P;delta=P[None,:,:]-P[:,None,:]
        H=edge[:,None,0]*delta[:,:,1]-edge[:,None,1]*delta[:,:,0]
        return np.r_[H[mask]-floor,np.sum((P[i]-P[j])**2,axis=1)-separation**2]
    def equality(flat):
        P=flat.reshape(n,2)
        return np.r_[P.mean(axis=0),np.mean(np.sum(P*P,axis=1))-1]
    sol=minimize(objective,X.ravel(),jac=grad,method='SLSQP',constraints=[{'type':'ineq','fun':inequality},{'type':'eq','fun':equality}],options={'maxiter':160,'ftol':1e-10})
    return sol.x.reshape(n,2),{'nfev':int(sol.nfev),'nit':int(sol.nit),'status':int(sol.status),'success':bool(sol.success),'cost':float(sol.fun),'message':str(sol.message),'hard_support_floor':floor,'hard_separation':separation,'min_inequality_slack':float(np.min(inequality(sol.x))),'max_equality_residual':float(np.max(np.abs(equality(sol.x))))}

def start(n,rng,hybrid=False):
    if hybrid:
        P=repair18()
        from quadratic import hull
        X=np.array([[float(P[i][0]),3**.5*float(P[i][1])] for i in hull(P)])
        # Independent perturbation explicitly breaks C3 symmetry.
        X+=rng.normal(0,1e-9,X.shape)
    else:
        theta=2*np.pi*(np.arange(n)+rng.uniform(-.2,.2,n))/n
        X=np.c_[np.cos(theta),np.sin(theta)]
        # Affine ellipse keeps a strict initial hull without regular distance ties.
        X[:,0]*=rng.uniform(.75,1.4)
    X-=X.mean(0);X/=np.sqrt(np.mean(np.sum(X*X,axis=1)))
    return X

def main():
    rng=np.random.default_rng(SEED);runs=[]
    specs=[(12,False),(12,False),(15,False),(15,False),(18,False),(18,False),(18,True),(18,True)]
    for k,(n,hybrid) in enumerate(specs):
        X=start(n,rng,hybrid);trace=[];accepted=0
        for stage in range(2):
            rows,counts=choose_rows(X,rng)
            entry={'stage':stage,'preflight_counts':counts}
            if rows is None:
                entry['outcome']='no preflight-passing row table in bounded attempts';trace.append(entry);break
            accepted+=1;entry['rows']=rows.tolist();entry['before']=measures(X,rows)
            X,solver=optimize(X,rows,.012 if hybrid else .06,1e-5 if hybrid else 1e-4)
            entry['solver']=solver;entry['after']=measures(X,rows);trace.append(entry)
        out={'run':k,'n':n,'start':'perturbed exact off-carrier repair' if hybrid else 'randomized ellipse','stages':trace,'final_coordinates':X.tolist()}
        runs.append(out)
        Path(__file__).with_name('codesign_search.json').write_text(json.dumps({'seed':SEED,'status':'numerical exploration, not an exclusion or exact realization','runs':runs},indent=2)+'\n')
        print(k,n,hybrid,'optimized stages',accepted,trace[-1].get('after',trace[-1].get('outcome')),flush=True)
if __name__=='__main__':main()
