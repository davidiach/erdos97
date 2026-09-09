"""Bounded search using exact source- and target-median necessary conditions."""
from median_probe import *
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import coo_array
import time,sys,os
from previous import load_kalmanson
kalmanson=load_kalmanson()

def run(seed=1,rounds=15):
 data=json.load(open(Path(__file__).with_name('evidence')/'median_domains.json'))
 D=[[tuple(tuple(r)for r in c)for c in data[str(g)]['domains']]for g in range(9)]
 sv=[(g,c)for g,domain in enumerate(D)for c in domain]
 tv=[]
 for t in range(9):
  allowed=[3*g+s for g in range(9)if t in pool(g)for s in range(3)]
  for a,b,c in product(allowed,repeat=3):
   if len({a,b,c})==3 and med(a,b,c,3*t+2):tv.append((t,(a,b,c)))
 print('source vars',len(sv),'target vars',len(tv),flush=True)
 rr=[];cc=[];ww=[];lo=[1.]*18;hi=[1.]*18;resource={};links={};rows_index={}
 def con(key,kind='resource'):
  dic=resource if kind=='resource'else links
  if key not in dic:
   dic[key]=len(lo);lo.append(-np.inf if kind=='resource'else 0.);hi.append(1. if kind=='resource'else 0.)
  return dic[key]
 for v,(g,config)in enumerate(sv):
  rr.append(g);cc.append(v);ww.append(1.)
  for s,row in enumerate(config):
   i=3*g+s;rows_index.setdefault((i,row),[]).append(v)
   for a,b in combinations(row,2):
    side=int(0<(POS[i]-POS[a])%27<(POS[b]-POS[a])%27)
    rr.append(con((a,b,side)));cc.append(v);ww.append(1.)
    if a//3==b//3:
     rr.append(con((a,b,i),'link'));cc.append(v);ww.append(1.)
 for j,(t,owners)in enumerate(tv):
  v=len(sv)+j;rr.append(9+t);cc.append(v);ww.append(1.)
  for pair,i in zip(combinations(range(3*t,3*t+3),2),owners):
   rr.append(con((*pair,i),'link'));cc.append(v);ww.append(-1.)
 nv=len(sv)+len(tv);rng=np.random.default_rng(seed)
 cost=np.r_[rng.uniform(0,1,len(sv)),np.zeros(len(tv))]
 history=[];nogoods=set()
 for step in range(rounds):
  A=coo_array((np.array(ww),(np.array(rr,dtype=np.int32),np.array(cc,dtype=np.int32))),shape=(len(lo),nv)).tocsc()
  print('round',step,'constraints',len(lo),'nonzero',len(ww),flush=True)
  st=time.monotonic();res=milp(cost,integrality=np.ones(nv),bounds=Bounds(0,1),constraints=LinearConstraint(A,lo,hi),options={'time_limit':30.,'mip_rel_gap':.25})
  h={'round':step,'status':int(res.status),'message':res.message,'seconds':time.monotonic()-st}
  if res.x is None:
   history.append(h);print(h,flush=True);break
  chosen=sorted(np.flatnonzero(res.x[:len(sv)]>.5).tolist(),key=lambda v:sv[v][0]);assert len(chosen)==9
  rows=[list(r)for v in chosen for r in sv[v][1]]
  for t in range(9):
   ps=list(combinations(range(3*t,3*t+3),2));op=[]
   for pair in ps:
    owners=[i for i,row in enumerate(rows)if set(pair)<=set(row)];assert len(owners)==1;op.append(owners[0])
   assert med(*op,3*t+2)
  h['rows']=rows
  verdict=kalmanson.discover(rows,ORDER);h['kalmanson']=verdict
  print(verdict['status'],'certificates',len(verdict.get('certificates',[])),flush=True)
  history.append(h)
  if verdict['status']!='exact obstruction':break
  for cert in verdict['certificates']:
   key=tuple((i,tuple(rows[i]))for i in cert['selected_centers'])
   if key in nogoods:continue
   nogoods.add(key);idx=len(lo);lo.append(-np.inf);hi.append(float(len(key)-1))
   for rowkey in key:
    indices=rows_index[rowkey];rr.extend([idx]*len(indices));cc.extend(indices);ww.extend([1.]*len(indices))
  Path(__file__).with_name('evidence').joinpath(f'median_direct_{seed}.json').write_text(json.dumps({'seed':seed,'order':ORDER,'history':history,'exhaustive':False,'cuts':len(nogoods)},indent=2))
 result={'seed':seed,'order':ORDER,'history':history,'exhaustive':False,'cuts':len(nogoods)}
 Path(__file__).with_name('evidence').joinpath(f'median_direct_{seed}.json').write_text(json.dumps(result,indent=2))
if __name__=='__main__':run()
