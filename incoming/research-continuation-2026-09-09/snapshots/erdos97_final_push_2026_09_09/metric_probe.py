"""Exploratory search in the strict Kalmanson cone, not Euclidean geometry."""
from itertools import combinations
from pathlib import Path
import json,math,time,sys
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix,csr_matrix,vstack,hstack

def template(n):
 pairs=list(combinations(range(n),2));idx={p:k for k,p in enumerate(pairs)};m=len(pairs)
 rr=[];cc=[];vv=[];quads=[]
 for i in range(n):
  for j in range(i+1,n):
   if j==i+1 or (i==0 and j==n-1):continue
   a,b,c,d=i,(i+1)%n,j,(j+1)%n
   q=[a,b,c,d];quads.append(q);k=len(quads)-1
   for x,y,s in [(a,c,-1),(b,d,-1),(a,d,1),(b,c,1)]:
    rr.append(k);cc.append(idx[tuple(sorted((x,y)))]);vv.append(s)
 K=csr_matrix((vv,(rr,cc)),shape=(len(quads),m))
 return pairs,idx,K,quads

def start(n,rng):
 # Strict Kalmanson distances from positively weighted circular splits and stars.
 pairs,idx,K,quads=template(n);D=np.zeros((n,n));stars=rng.uniform(0,5*n,n)
 for a in range(n):
  for b in range(a+1,n):
   w=rng.exponential(1.)+.1;S=np.array([a<j<=b for j in range(n)])
   D+=w*(S[:,None]!=S[None,:])
 D+=stars[:,None]+stars[None,:];np.fill_diagonal(D,0)
 return D

def choices(D,rng,temperature=0):
 n=len(D);rows=[]
 for i in range(n):
  ids=np.array([j for j in range(n) if j!=i]);ids=ids[np.argsort(D[i,ids])]
  costs=np.array([D[i,ids[k+3]]-D[i,ids[k]] for k in range(n-4)])
  k=int(np.argmin(costs+temperature*rng.random(len(costs))))
  rows.append(list(map(int,ids[k:k+4])))
 return rows

def optimize(n,rows,pairs,idx,K,costperturb):
 m=len(pairs); nv=m+n+4*n; nr=K.shape[0]+8*n
 A=lil_matrix((nr,nv)); A[:K.shape[0],:m]=K;rhs=-np.ones(nr);rhs[K.shape[0]:]=0
 for i,W in enumerate(rows):
  for k,j in enumerate(W):
   e=idx[tuple(sorted((i,j)))];t=m+n+4*i+k;r=K.shape[0]+8*i+2*k
   A[r,e]=1;A[r,m+i]=-1;A[r,t]=-1
   A[r+1,e]=-1;A[r+1,m+i]=1;A[r+1,t]=-1
 c=np.r_[costperturb*1e-7,np.zeros(n),np.ones(4*n)]
 sol=linprog(c,A_ub=A.tocsr(),b_ub=rhs,bounds=[(1,10000)]*m+[(1,10000)]*n+[(0,None)]*(4*n),method='highs')
 if sol.x is None:return None,float('inf')
 D=np.zeros((n,n))
 for (i,j),x in zip(pairs,sol.x[:m]):D[i,j]=D[j,i]=x
 return D,float(sum(sol.x[m+n:]))

def run(n,seed,iterations=100):
 rng=np.random.default_rng(seed); pairs,idx,K,quads=template(n);D=start(n,rng);best=math.inf;history=[];t=time.monotonic();saved=None
 for k in range(iterations):
  rows=choices(D,rng,0 if k%10 else 20)
  D,err=optimize(n,rows,pairs,idx,K,rng.random(len(pairs)))
  history.append(err)
  if D is None:break
  if err<best:best=err;saved=(rows,D.copy())
  if err<1e-7:break
  if k%10==9:D=.8*D+.2*start(n,rng)
 if saved:
  rows,D=saved
  return dict(n=n,seed=seed,iterations=len(history),best_error=best,history=history,rows=rows,distances=D.tolist(),elapsed=time.monotonic()-t,status='relaxation only; no Euclidean claim')
 return dict(n=n,seed=seed,best_error=best,history=history)
if __name__=='__main__':
 n=int(sys.argv[1]);s=int(sys.argv[2]);it=int(sys.argv[3]);out=Path(sys.argv[4]);res=run(n,s,it);out.write_text(json.dumps(res,indent=2)+'\n');print(n,s,res['best_error'],res.get('iterations'))
