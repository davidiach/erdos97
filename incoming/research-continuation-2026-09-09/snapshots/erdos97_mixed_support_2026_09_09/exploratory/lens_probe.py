import numpy as np,json
from pathlib import Path

def roots(coeff):return sorted(float(z.real) for z in np.roots(coeff) if abs(z.imag)<1e-7)
def run(b,c):
 H=2*b*b
 polys=[[1,0,1-2*c*c,-2*c,c*c+c**4], [1,0,1-2*H+2*c*c,-2*c,c*c+(H-c*c)**2]]
 levels={0.0}
 for f in polys:
  ts=[-b,-c,c,b]+[x for x in roots([4,0,2*f[2],f[3]]) if -b<=x<=b and abs(x)>=c-1e-8]
  levels.update(np.polyval(f,t) for t in ts)
 ls=sorted(levels);best=0;data=None
 for r in [(u+v)/2 for u,v in zip(ls,ls[1:])]+ls:
  points=[]
  for i,f in enumerate(polys):
   ff=f.copy();ff[-1]-=r
   for t in roots(ff):
    if -b+1e-7<t<b-1e-7 and abs(t)>=c-1e-7 and not(i==0 and abs(t-c)<1e-7):points.append([i,t])
  if len(points)>best:best=len(points);data=[float(r),points]
 return best,data
bad=[]
for b in np.geomspace(.05,30,80):
 for rat in np.linspace(0,.995,101):
  c=float(b*rat);n,d=run(float(b),c)
  if n>=4:
   bad.append(dict(b=float(b),c=c,count=n,data=d))
   if len(bad)==5:break
 if len(bad)==5:break
print(json.dumps(bad,indent=2))
Path(__file__).with_suffix('.json').write_text(json.dumps({'status':'floating exploratory only','bad_to_minimum_absolute_x_claim':bad},indent=2))
