#!/usr/bin/env python3
"""Exploration only: freely moving coordinates, fixed directed witnesses.

Convexity is tested by all supporting half-planes, not only local turns.
No small residual is a certificate. The output retains coordinates and W.
"""
from __future__ import annotations
import argparse, itertools, json, math, pathlib, time
import numpy as np
from scipy.optimize import minimize
from scipy.spatial import ConvexHull
ROOT=pathlib.Path(__file__).resolve().parents[1]

def normalized(x):
    q=x.reshape(-1,2); q=q-q.mean(axis=0)
    rms=np.sqrt(np.mean(np.sum(q*q,axis=1)))
    if rms<1e-12: rms=1e-12
    return q/rms, rms

def objective(x, W, order, convex_weight=80., sep_weight=1.):
    n=len(W); p,rms=normalized(x); grad=np.zeros_like(p)
    diff=p[:,None,:]-p[W]; ds=np.sum(diff*diff,axis=2)
    residual=ds-ds.mean(axis=1,keepdims=True)
    val=np.mean(residual*residual)
    g=(4/(4*n))*residual[:,:,None]*diff
    grad+=g.sum(axis=1); np.add.at(grad, W.ravel(), -g.reshape(-1,2))
    a=order; b=np.roll(order,-1)
    e=p[b]-p[a]; v=p[None,:,:]-p[a,None,:]
    cross=e[:,None,0]*v[:,:,1]-e[:,None,1]*v[:,:,0]
    mask=np.ones((n,n),bool); mask[np.arange(n),a]=False; mask[np.arange(n),b]=False
    loss=np.minimum(cross-1e-6,0)*mask
    val+=convex_weight*np.mean(loss*loss)
    coef=2*convex_weight*loss/(n*n)
    # cross(e,v): gradient in e is (v_y,-v_x), in v is (-e_y,e_x).
    ge=np.sum(coef[:,:,None]*np.stack([v[:,:,1],-v[:,:,0]],axis=2),axis=1)
    gv=coef[:,:,None]*np.stack([-e[:,1],e[:,0]],axis=1)[:,None,:]
    np.add.at(grad,b,ge); np.add.at(grad,a,-ge-gv.sum(axis=1)); grad+=gv.sum(axis=0)
    ii,jj=np.triu_indices(n,1); d=p[ii]-p[jj]; d2=np.sum(d*d,axis=1)
    lack=np.minimum(d2-.002**2,0)
    val+=sep_weight*np.mean(lack*lack)/(.002**2)
    gs=4*sep_weight*lack[:,None]*d/(len(ii)*(.002**2))
    np.add.at(grad,ii,gs); np.add.at(grad,jj,-gs)
    # Pull gradient back through centering and unit-RMS normalization.
    grad=(grad-p*np.sum(grad*p)/n)/rms; grad-=grad.mean(axis=0)
    return float(val),grad.ravel()

def diagnostics(x,W,order):
    p,_=normalized(x);n=len(p);d=p[:,None,:]-p[W];ds=np.sum(d*d,axis=2)
    res=ds-ds.mean(axis=1,keepdims=True)
    distances=np.linalg.norm(p[:,None,:]-p[None,:,:],axis=2);np.fill_diagonal(distances,np.inf)
    a=order;b=np.roll(a,-1);e=p[b]-p[a];v=p[None,:,:]-p[a,None,:]
    cross=e[:,None,0]*v[:,:,1]-e[:,None,1]*v[:,:,0]
    cross[np.arange(n),a]=np.inf;cross[np.arange(n),b]=np.inf
    try:hull=ConvexHull(p).vertices.tolist()
    except Exception:hull=[]
    return dict(max_squared_distance_residual=float(np.max(np.abs(res))),
        rms_residual=float(np.sqrt(np.mean(res*res))),min_separation=float(distances.min()),
        min_supporting_margin=float(cross.min()),hull_size=len(hull),hull=hull,
        coordinates=p.tolist(),witnesses=W.tolist(),cyclic_order=order.tolist())

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--sizes',default='12,15,18,24,30')
    ap.add_argument('--patterns',type=int,default=12);ap.add_argument('--iterations',type=int,default=700)
    ap.add_argument('--output',default='reports/nonsymmetric_circulant_probe.json');args=ap.parse_args()
    rng=np.random.default_rng(97090872);out=[];start=time.time()
    for n in map(int,args.sizes.split(',')):
        one=[s for s in range(1,n) if s%3==1];two=[s for s in range(1,n) if s%3==2]
        choices=[]
        for a in itertools.combinations(one,2):
            for b in itertools.combinations(two,2):
                S=tuple(sorted(a+b))
                if n//3 in S and 2*n//3 in S:continue
                if any(len(set(S)&{(s+k)%n for s in S})>=3 for k in range(1,n)):continue
                choices.append(S)
        rng.shuffle(choices)
        for case,S in enumerate(choices[:args.patterns]):
            W=(np.arange(n)[:,None]+np.array(S)[None,:])%n
            m=n//3;eps=[.025,.075,.18][case%3];p=np.zeros((n,2));order=[]
            for cluster in range(3):
                labels=np.arange(cluster,n,3);angles=np.linspace(-.95,.95,m)
                rng.shuffle(labels)
                phase=2*np.pi*cluster/3
                zz=np.exp(1j*phase)+eps*np.exp(1j*(phase+angles))
                p[labels,0]=zz.real;p[labels,1]=zz.imag;order.extend(labels.tolist())
            order=np.array(order);x=p.ravel()
            value,grad=objective(x,W,order)
            errs=[]
            for k in (0,n,2*n-1):
                h=1e-6;xp=x.copy();xm=x.copy();xp[k]+=h;xm[k]-=h
                fd=(objective(xp,W,order)[0]-objective(xm,W,order)[0])/(2*h)
                errs.append(abs(fd-grad[k]))
            if max(errs)>1e-5:raise RuntimeError(f'Gradient check failed: {errs}')
            sol=minimize(objective,x,args=(W,order),method='L-BFGS-B',jac=True,
                options=dict(maxiter=args.iterations,ftol=1e-15,gtol=1e-10,maxls=30,maxcor=20))
            row=dict(n=n,offsets=list(S),initial_epsilon=eps,iterations=int(sol.nit),
                     merit=float(sol.fun),solver_message=str(sol.message),gradient_check=max(errs),
                     **diagnostics(sol.x,W,order))
            out.append(row)
            result=dict(status='NUMERICAL_EXPLORATION_NOT_CERTIFIED',seed=97090872,
                        elapsed_seconds=time.time()-start,cases=out)
            target=ROOT/args.output;target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(json.dumps(result,indent=2)+'\n')
            print(n,case,S,'res',row['max_squared_distance_residual'],'hull',row['hull_size'],
                  'sep',row['min_separation'],'support',row['min_supporting_margin'],flush=True)
    print('Completed',len(out),'cases',flush=True)
if __name__=='__main__':main()
