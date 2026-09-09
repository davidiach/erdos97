"""Bounded median-constrained selection; solver failures are not exclusions."""
from median_probe import *
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import coo_array
import time
import sys
from previous import load_kalmanson
kalmanson=load_kalmanson()

def run(seed=1,rounds=8):
 data=json.load(open(Path(__file__).with_name('evidence')/'median_domains.json'))
 domains=[[tuple(tuple(r)for r in config)for config in data[str(g)]['domains']]for g in range(9)]
 variables=[(g,c)for g,D in enumerate(domains)for c in D]
 resources={};rr=[];cc=[]
 for v,(g,config)in enumerate(variables):
  rr.append(g);cc.append(v)
  used=[]
  for s,row in enumerate(config):
   center=3*g+s
   for a,b in combinations(row,2):
    side=int(0<(POS[center]-POS[a])%27<(POS[b]-POS[a])%27)
    key=(a,b,side)
    if key not in resources:resources[key]=len(resources)+9
    used.append(resources[key])
  if len(set(used))!=18:raise AssertionError
  rr.extend(used);cc.extend([v]*18)
 nr=9+len(resources);lower=[1.]*9+[-np.inf]*len(resources);upper=[1.]*nr
 weights=list(np.ones(len(rr)))
 rng=np.random.default_rng(seed);cost=rng.uniform(0,1,len(variables));history=[];cuts=[]
 print('matrix',nr,len(variables),len(rr),flush=True)
 for step in range(rounds):
  A=coo_array((np.array(weights),(np.array(rr,dtype=np.int32),np.array(cc,dtype=np.int32))),shape=(len(lower),len(variables))).tocsc()
  st=time.monotonic();res=milp(cost,integrality=np.ones(len(variables)),bounds=Bounds(0,1),constraints=LinearConstraint(A,lower,upper), options={'time_limit':30.,'mip_rel_gap':.1})
  h={'round':step,'status':int(res.status),'message':res.message,'seconds':time.monotonic()-st}
  if res.x is None:
   history.append(h);print(h,flush=True);break
  chosen=sorted(np.flatnonzero(res.x>.5).tolist(),key=lambda v:variables[v][0]);assert len(chosen)==9 and [variables[v][0]for v in chosen]==list(range(9))
  rows=[list(r)for v in chosen for r in variables[v][1]]
  h['rows']=rows;bad=[]
  for t in range(9):
   a,b,c=range(3*t,3*t+3);op=[]
   for pair in ((a,b),(a,c),(b,c)):
    owners=[i for i,row in enumerate(rows)if set(pair)<=set(row)]
    assert len(owners)==1
    op.append(owners[0])
   if not med(*op,c):
    combo=sorted({chosen[o//3]for o in op});bad.append(combo)
  h['target_median_violations']=len(bad)
  if not bad:
   st=time.monotonic();verdict=kalmanson.discover(rows,ORDER)
   h['kalmanson']=verdict;h['kalmanson_seconds']=time.monotonic()-st
   # Discover schema inspected below; no reliance for exclusion claims.
   Path(__file__).with_name('evidence').joinpath(f'median_candidate_{seed}_{step}.json').write_text(json.dumps(h,indent=2))
   print('candidate',step, str(verdict)[:250],flush=True)
   break
  for combo in bad:
   idx=len(lower);rr.extend([idx]*len(combo));cc.extend(combo);weights.extend([1.]*len(combo));lower.append(-np.inf);upper.append(float(len(combo)-1));cuts.append(combo)
  history.append(h);print('round',step,'med bad',len(bad),'status',res.status,flush=True)
 result={'seed':seed,'exact_source_domain_size':len(variables),'variables':len(variables),'history':history,'no_good_cuts':cuts,'exhaustive':False}
 Path(__file__).with_name('evidence').joinpath(f'median_search_{seed}.json').write_text(json.dumps(result,indent=2))
if __name__=='__main__':run()
