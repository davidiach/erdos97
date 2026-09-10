"""Numerical phase-cycle and free-coordinate realization of preflight-surviving C3 systems.
All phases and all relative radii move. No numerical output is an exact counterexample.
"""
from pathlib import Path
from itertools import combinations
import argparse,json,time,sys,platform
import numpy as np
import scipy
from scipy.optimize import least_squares,minimize
ROOT=Path(__file__).resolve().parents[1]
TAU=2*np.pi/3

def setup(rows):
    m=len(rows);edges=[(i,j,g)for i,row in enumerate(rows)for j,g in zip(row[::2],row[1::2])]
    B=np.zeros((len(edges),m-1))
    for k,(i,j,_)in enumerate(edges):
        if i:B[k,i-1]-=1
        if j:B[k,j-1]+=1
    H=np.linalg.pinv(B);Z=np.eye(len(edges))-B@H
    return edges,B,H,Z

def qlog(theta):return .5*np.log(2.)+np.arcsinh(np.cos(theta)/np.sqrt(2.))
def qlog_derivative(theta):return-np.sin(theta)/np.sqrt(2+np.cos(theta)**2)

def quality(theta,h,rows):
    m=len(rows);z=np.exp(h+1j*theta);p=np.concatenate([z*np.exp(1j*k*TAU)for k in range(3)])
    D=abs(p[:,None]-p[None,:])**2
    separation=float(np.sqrt(np.min(D+np.eye(3*m)*1e9)))
    v=np.roll(p,-1)-p;S=(np.conj(v[:,None])*(p[None,:]-p[:,None])).imag
    mask=np.ones_like(S,dtype=bool)
    for i in range(3*m):mask[i,i]=False;mask[i,(i+1)%(3*m)]=False
    eq=[abs(z[i]-np.exp(1j*g*TAU)*z[j])**2-3*abs(z[i])**2 for i,row in enumerate(rows)for j,g in zip(row[::2],row[1::2])]
    from scipy.spatial import ConvexHull
    hull=len(ConvexHull(np.c_[p.real,p.imag]).vertices)if separation>1e-12 else None
    return {'theta':theta.tolist(),'log_radii':h.tolist(),'orbit_coordinates':np.c_[z.real,z.imag].tolist(),
      'named_equality_max_abs':float(np.max(abs(np.array(eq)))),'minimum_separation':separation,
      'minimum_global_support_margin':float(np.min(S[mask])),'hull_vertices':hull,'radii_maximum':float(np.exp(h).max())}

def run(rows,phase_seed,seed,restarts,nfev):
    rng=np.random.default_rng(seed);m=len(rows);edges,B,H,Z=setup(rows);records=[]
    G=np.array([[j if j else -1,i if i else -1]for i,j,g in edges])
    def values(x):
        theta=np.r_[0,x];angles=np.array([theta[j]-theta[i]+g*TAU for i,j,g in edges]);f=qlog(angles);h=np.r_[0,H@f]
        return theta,f,h,angles
    def fun(x):return Z@values(x)[1]
    def jac(x):
        der=qlog_derivative(values(x)[3]);return Z@(der[:,None]*B)
    for k in range(restarts):
        if k==0:x0=np.array(phase_seed[1:])
        elif k==1:x0=np.arange(1,m)*TAU/m
        else:x0=np.sort(rng.uniform(.002,TAU-.002,m-1))
        r=least_squares(fun,x0,jac=jac,bounds=(np.full(m-1,1e-9),np.full(m-1,TAU-1e-9)),max_nfev=nfev,ftol=1e-13,xtol=1e-13,gtol=1e-13)
        theta,_,h,_=values(r.x);q=quality(theta,h,rows);q.update({'stage':'phase_cycle','restart':k,'status':int(r.status),'nfev':int(r.nfev),'cycle_max_residual':float(max(abs(r.fun))),'ordered':bool(np.all(np.diff(theta)>0)),'initial_phases':np.r_[0,x0].tolist()});records.append(q)
        print(seed,k,q['cycle_max_residual'],q['named_equality_max_abs'],q['minimum_global_support_margin'],q['minimum_separation'],q['hull_vertices'],q['ordered'],flush=True)
    return records

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--restarts',type=int,default=30);ap.add_argument('--nfev',type=int,default=1500);ap.add_argument('--seed',type=int,default=9709093);ap.add_argument('--output',required=True);a=ap.parse_args()
    inp=json.loads((ROOT/'reports/angle_survivor_preflight.json').read_text());out=[];start=time.monotonic()
    sys.path.insert(0,str(ROOT/'verify'));from check_c3 import Geometry
    from fractions import Fraction
    for c in inp:
        g=Geometry(c['rows']);vec=np.array([float(Fraction(x))for x in c['rational_angle_vector']]);ids={p:k for k,p in enumerate(g.variables)}
        theta=np.array([np.pi*(vec[ids[i,i+g.m]]-vec[ids[0,g.m]])/3 for i in range(g.m)])
        rec=run(c['rows'],theta,a.seed+c['index'],a.restarts,a.nfev)
        out.append({'index':c['index'],'rows':c['rows'],'records':rec})
        Path(a.output).write_text(json.dumps({'classification':'NUMERICAL_REALIZATION_ATTEMPTS_NOT_COUNTEREXAMPLES','argv':sys.argv,'python':platform.python_version(),'scipy':scipy.__version__,'numpy':np.__version__,'seed':a.seed,'cases':out,'elapsed_seconds':time.monotonic()-start,'termination':'all specified restarts completed','exact_solution_claimed':False},indent=2)+'\n')
if __name__=='__main__':main()
