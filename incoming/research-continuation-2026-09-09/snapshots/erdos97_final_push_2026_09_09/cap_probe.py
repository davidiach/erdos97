"""Numerical scouting of incoming-repair + outgoing-old own-side intersections."""
from pathlib import Path
from itertools import combinations
import numpy as np,math,json,sys
from scipy.spatial import ConvexHull
from previous import load_quadratic
base9=load_quadratic().base9
P=np.array([[float(x),math.sqrt(3)*float(y)] for x,y in base9()])
w=np.exp(2j*math.pi/3)
def rotate(q,k):
 z=(q[0]+1j*q[1])*w**k
 return np.array([z.real,z.imag])
def circleints(a,R,b,S):
 dvec=b-a;d=np.linalg.norm(dvec)
 if d<1e-12 or d>R+S+1e-12 or d<abs(R-S)-1e-12:return []
 t=(R*R-S*S+d*d)/(2*d);h2=R*R-t*t
 if h2< -1e-10:return []
 mid=a+(t/d)*dvec;v=np.array([-dvec[1],dvec[0]])/d
 return [mid+sign*math.sqrt(max(h2,0))*v for sign in [-1,1]]
def valid(q):
 Y=np.vstack([P,*[rotate(q,k)[None,:] for k in range(3)]])
 if min(np.linalg.norm(Y[i]-Y[j]) for i,j in combinations(range(len(Y)),2))<1e-7:return False
 return len(ConvexHull(Y).vertices)==len(Y)
raw=[];ok=[]
for i in [0,3]:
 for j in range(9):
  for k,q in enumerate(circleints(P[i],math.sqrt(3)*np.linalg.norm(P[i]),-P[j]/2,math.sqrt(3)/2*np.linalg.norm(P[j]))):
   row=dict(repair_source=i,old_supplier=j,branch=k,q=q.tolist(),admissible_numeric=valid(q))
   raw.append(row)
   if row['admissible_numeric']:ok.append(row)
edges=[]
for i,a in enumerate(ok):
 for j,b in enumerate(ok):
  for k in range(3):
   if i==j:continue
   q=np.array(a['q']);r=rotate(b['q'],k);v=float(np.sum((q-r)**2)-3*np.sum(q*q))
   if abs(v)<1e-8:edges.append(dict(source=i,target=j,phase=k,residual=v))
report=dict(status='numerical scouting only, not an exclusion',raw_count=len(raw),admissible_count=len(ok),admissible=ok,near_edges=edges,raw=raw)
Path(sys.argv[1]).write_text(json.dumps(report,indent=2)+'\n');print('raw',len(raw),'admissible',len(ok),'near edges',len(edges));print(ok);print(edges)
