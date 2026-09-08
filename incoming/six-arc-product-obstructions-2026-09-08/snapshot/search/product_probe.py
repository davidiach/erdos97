"""Reproduce the 27-point product seed and inspect the full fixed-witness Jacobian.
Exploration only: SVD and hull calls below use IEEE float64, not certification.
"""
import json
from pathlib import Path
import numpy as np
from scipy.spatial import ConvexHull

ROOT = Path(__file__).resolve().parents[1]
OMEGA = np.exp(2j*np.pi/3)

def seed():
    s=np.sqrt(3.)
    def X(t): return 1+s*(1+1j*t)/(1-1j*t)
    ua=min(np.roots([-75+44*s,-18+6*s,-33-14*s]))
    ub=min(np.roots([-162+96*s,-32+16*s,-50-16*s]))
    a=np.array([1,X(2),X(2)*X(ua)])
    b=np.array([1,X(3),X(3)*X(ub)])
    z=(a[:,None]*b).ravel()
    return z, float(ua),float(ub)

def witness_table():
    def ix(i,j,k): return (3*i+j)*3+k%3
    W=[]
    for i in range(3):
      for j in range(3):
       for k in range(3):
        W.append([ix(i,j,k+1),ix(i,j,k+2),
                  ix((i+1)%3,j,k+(i==2)),
                  ix(i,(j+1)%3,k+(j==2))])
    return np.array(W)

def full_equations(P, W):
    eq=[]; J=[]
    for i, row in enumerate(W):
      a=row[0]
      for b in row[1:]:
        eq.append(abs(P[i]-P[b])**2-abs(P[i]-P[a])**2)
        j=np.zeros((len(P),2))
        def v(z): return np.array([z.real,z.imag])
        j[i]=2*v(P[a]-P[b]); j[a]=2*v(P[i]-P[a]); j[b]=2*v(P[b]-P[i])
        J.append(j.ravel())
    return np.array(eq),np.array(J)

def c3_equations(z):
    eq=[]; J=[]
    for i in range(3):
     for j in range(3):
      t=3*i+j
      for u,g in [(3*((i+1)%3)+j,int(i==2)),(3*i+(j+1)%3,int(j==2))]:
       w=OMEGA**g
       d=w*z[u]-z[t]
       eq.append(abs(d)**2-3*abs(z[t])**2)
       r=np.zeros((9,2))
       a=-2*d-6*z[t]
       b=2*d*np.conj(w)
       r[t]=[a.real,a.imag];r[u]=[b.real,b.imag]
       J.append(r.ravel())
    return np.array(eq),np.array(J)

if __name__=='__main__':
    z,ua,ub=seed(); P=(z[:,None]*OMEGA**np.arange(3)).ravel(); W=witness_table()
    E,J=full_equations(P,W); C,K=c3_equations(z)
    sf=np.linalg.svd(J,compute_uv=False);sc=np.linalg.svd(K,compute_uv=False)
    h=ConvexHull(np.c_[P.real,P.imag])
    d=abs(P[:,None]-P[None,:]); np.fill_diagonal(d,np.inf)
    report={'classification':'float64 exploration; no rank or convexity certificate',
      'u_A':ua,'u_B':ub,'full_equality_max_abs':max(abs(E)),
      'full_singular_values':sf.tolist(),'full_numerical_rank_1e-9':int(sum(sf>1e-9)),
      'c3_equality_max_abs':max(abs(C)), 'c3_singular_values':sc.tolist(),
      'c3_numerical_rank_1e-9':int(sum(sc>1e-9)),
      'hull_size':len(h.vertices),'hull_labels':h.vertices.tolist(),
      'minimum_separation':float(d.min()),'points_float64':[[v.real,v.imag] for v in P],
      'witnesses':W.tolist()}
    (ROOT/'reports/product_probe.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['points_float64','witnesses']},indent=2))
