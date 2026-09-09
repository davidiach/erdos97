"""Bounded numerical search for same-half-plane own-side cycles.
All metric equations follow the circle-product construction up to floating
roundoff; convexity and distinctness are numerical diagnostics only.
"""
import math,json,time
from pathlib import Path
import numpy as np
from scipy.spatial import ConvexHull
W=complex(-.5,math.sqrt(3)/2)
def intersects(c):
 # |a-1|=sqrt3; |a+c/2|=sqrt3|c|/2.
 C=1+0j;D=-c/2;r=math.sqrt(3);s=math.sqrt(3)*abs(c)/2
 d=abs(D-C)
 if d<1e-12 or d>r+s or d<abs(r-s):return []
 x=(d*d+r*r-s*s)/(2*d);h2=r*r-x*x
 if h2<0:return []
 t=(D-C)/d
 return [C+x*t+sgn*1j*math.sqrt(h2)*t for sgn in (-1,1)]
def run(m,nsamples,rng):
 best=None;valid=0;full=0;start=time.monotonic()
 for k in range(nsamples):
  theta=rng.uniform(math.pi/3+1e-4,math.pi-1e-4,m-2)
  norms=np.cos(theta)+np.sqrt(2+np.cos(theta)**2)
  a=list(norms*np.exp(1j*theta));prod=np.prod(a)
  for gain in range(3):
   c=W**gain/prod
   for v in intersects(c):
    b=c/v
    if min(v.imag,b.imag)<1e-10 or max(abs(v),abs(b))>=2:continue
    aa=a+[v,b];z=[1+0j]
    for val in aa[:-1]:z.append(z[-1]*val)
    rads=list(map(abs,z))
    if max(rads)>=2*min(rads):continue
    valid+=1
    pts=np.array([[q.real,q.imag]for q in [zz*W**g for zz in z for g in range(3)]])
    hull=ConvexHull(pts);score=len(hull.vertices)
    if best is None or score>best['hull_vertices']:
     mind=min(abs(z[i]-W**g*z[j])for i in range(m)for j in range(i+1,m)for g in range(3))
     best={'hull_vertices':score,'total':3*m,'gain':gain,'theta':theta.tolist(),'last_ratio':[v.real,v.imag],'radii':rads,'minimum_orbit_separation':mind,'representatives':[[x.real,x.imag]for x in z]}
    if score==3*m:
     full+=1;best['found_at_sample']=k
     print('FOUND',m,k,best,flush=True);return {'m':m,'samples_requested':nsamples,'samples_done':k+1,'valid_cycles':valid,'full_hull':full,'best':best,'exact_certificate':False,'seconds':time.monotonic()-start}
 return {'m':m,'samples_requested':nsamples,'samples_done':nsamples,'valid_cycles':valid,'full_hull':full,'best':best,'exact_certificate':False,'seconds':time.monotonic()-start}
if __name__=='__main__':
 rng=np.random.default_rng(97092026);out=[]
 for m in range(3,11):
  x=run(m,10000,rng);out.append(x);print(m,x['valid_cycles'], x['best']['hull_vertices']if x['best']else None,flush=True)
  Path(__file__).with_name('evidence').joinpath('product_cycle_probe.json').write_text(json.dumps(out,indent=2))
