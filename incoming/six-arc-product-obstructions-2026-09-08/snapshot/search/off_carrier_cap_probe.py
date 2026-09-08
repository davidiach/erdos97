#!/usr/bin/env python3
"""Explore finite transition caps outside the six-arc carrier.
All outputs are floating-point exploration, not exact counterexamples.
"""
from __future__ import annotations
import argparse,json,pathlib,itertools
import numpy as np
from scipy.spatial import ConvexHull
ROOT=pathlib.Path(__file__).resolve().parents[1]
W=np.exp(2j*np.pi/3)
def z(t):return -.5+3*t/(1+3*t*t)+1j*np.sqrt(3)*(1-3*t*t)/(2*(1+3*t*t))
def cap(u):return 1+(W-1)*(1+1j*np.sqrt(3)*u)/(1-1j*np.sqrt(3)*u)
def roots(q,outgoing):
 results=[]
 for conj,k in itertools.product([False,True],range(3)):
  def f(t):
   p=z(t);p=np.conj(p) if conj else p;p*=W**k
   return (abs(q-p)**2-3*abs(q if outgoing else p)**2)*(1+3*t*t)
  vals=[f(t) for t in [-1.,0.,1.]]
  coef=[(vals[0]+vals[2])/2-vals[1],(vals[2]-vals[0])/2,vals[1]]
  for t in np.roots(coef):
   if abs(t.imag)<1e-8 and 1e-10<t.real<1/3-1e-10:
    t=float(t.real);p=z(t);p=np.conj(p) if conj else p;p*=W**k
    results.append(dict(parameter=t,conjugated=conj,phase=k,point=[p.real,p.imag],residual=abs(f(t))))
 return results

def scan(count):
 records=[]
 for u in np.geomspace(1e-5,.3,count):
  q=cap(u);out=roots(q,True);inc=roots(q,False)
  reps=[1,q,q.conjugate()]+[complex(*p['point']) for p in out+inc]
  # Remove orbit aliases, but not distinct near coincidences.
  distinct=[]
  for a in reps:
   if not any(min(abs(a-b*W**k) for k in range(3))<1e-8 for b in distinct):distinct.append(a)
  pts=np.array([a*W**k for a in distinct for k in range(3)])
  hull=len(ConvexHull(np.c_[pts.real,pts.imag]).vertices)
  records.append(dict(u=float(u),cap=[q.real,q.imag],outgoing=out,incoming=inc,
   all_roots_hull_vertices=hull,all_roots_point_count=len(pts),
   outgoing_parameters=[p['parameter'] for p in out],incoming_parameters=[p['parameter']for p in inc]))
 return dict(kind='exploration_only',precision='numpy.float64',records=records)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--count',type=int,default=100);a=ap.parse_args();r=scan(a.count)
 (ROOT/'reports/off_carrier_caps.json').write_text(json.dumps(r,indent=2)+'\n')
 from collections import Counter
 print('root counts',Counter((len(x['outgoing']),len(x['incoming']))for x in r['records']))
 for i in [0,10,25,50,75,99]:
  if i<len(r['records']):
   x=r['records'][i];print(x['u'],'out',x['outgoing_parameters'],'in',x['incoming_parameters'],'hull',x['all_roots_hull_vertices'],x['all_roots_point_count'])
