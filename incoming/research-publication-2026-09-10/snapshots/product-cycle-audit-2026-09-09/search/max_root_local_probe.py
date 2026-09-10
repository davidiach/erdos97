"""Numerical adversarial test of a C3 maximum-root local-closure conjecture.
A candidate is only a negative control, never an all-rich solution.
"""
import argparse,json,time
from pathlib import Path
import numpy as np
from scipy.spatial import ConvexHull,QhullError
OM=np.exp(2j*np.pi/3);S3=np.sqrt(3.)
def polygon(z):return (np.asarray(z)[:,None]*OM**np.arange(3)).ravel()
def convex(z):
 p=polygon(z)
 if min(abs(p[i]-p[j])for i in range(len(p))for j in range(i))<1e-9:return False
 try:return len(ConvexHull(np.c_[p.real,p.imag]).vertices)==len(p)
 except QhullError:return False

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seeds',type=int,default=80);ap.add_argument('--grid',type=int,default=240);ap.add_argument('--seed',type=int,default=970909);ap.add_argument('--output',required=True);args=ap.parse_args();rng=np.random.default_rng(args.seed);start=time.monotonic();records=[];hit=None
 theta=np.linspace(0,2*np.pi,args.grid,endpoint=False)+.00031
 for k in range(args.seeds):
  ts=rng.uniform(-np.pi/6,np.pi/6,2);a,b=1-S3*np.exp(1j*ts);base=[1+0j,a,b]
  if not convex(base):continue
  suppliers=[];pairs=[]
  for center in [a,b]:
   good=[complex(q)for q in center*(1+S3*np.exp(1j*theta)) if abs(q)<1-1e-8 and convex(base+[q])]
   suppliers.append(good);valid=[]
   for _ in range(min(300,len(good)**2)):
    if len(good)<2:break
    i,j=rng.choice(len(good),2,replace=False)
    if convex(base+[good[i],good[j]]):valid.append((good[i],good[j]))
   pairs.append(valid)
  rec={'seed_index':k,'root_circle_parameters':ts.tolist(),'individual_supplier_counts':list(map(len,suppliers)),'compatible_sampled_pair_counts':list(map(len,pairs))};records.append(rec)
  if pairs[0] and pairs[1]:
   for _ in range(400):
    c,d=pairs[0][rng.integers(len(pairs[0]))];e,f=pairs[1][rng.integers(len(pairs[1]))]
    z=base+[c,d,e,f]
    if convex(z):hit={'orbits':[[v.real,v.imag]for v in z],'source_rows':[[1,2],[3,4],[5,6]],'parameters':rec};break
  Path(args.output).write_text(json.dumps({'scope':'float64 local-star construction search','args':vars(args),'records':records,'hit':hit,'seconds':time.monotonic()-start},indent=2)+'\n')
  if hit:break
 print(json.dumps({'seeds_tested':len(records),'hit':hit,'seconds':time.monotonic()-start},indent=2))
if __name__=='__main__':main()
