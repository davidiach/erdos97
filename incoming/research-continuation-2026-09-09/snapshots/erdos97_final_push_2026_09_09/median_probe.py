"""Exploratory exact row-domain construction for the tripled Danzer pools."""
from itertools import combinations, product
import json
from pathlib import Path
OLD_ORDER=[2,4,8,0,5,6,1,3,7]
CROSS={0:(2,1),1:(0,0),2:(1,0)}
ORDER=[3*i+s for i in OLD_ORDER for s in range(3)]
POS={v:k for k,v in enumerate(ORDER)}
def pool(i):
 m,j=divmod(i,3);a,b=CROSS[m]
 return [3*m+(j+1)%3,3*m+(j+2)%3,3*a+(j+b)%3]
def med(a,b,c,cut):
 a,b,c=[(POS[v]-POS[cut])%27 for v in (a,b,c)]
 return min(a,c)<b<max(a,c)
def domains(i):
 result=[]
 clusters=pool(i)
 for target in clusters:
  other=[x for x in clusters if x!=target]
  for ab in combinations(range(3),2):
   for sing in product(range(3),repeat=2):
    row=tuple(sorted([3*target+s for s in ab]+[3*t+s for t,s in zip(other,sing)]))
    result.append(row)
 return result

def group_domains(i):
 D=domains(i);M=[sum(1<<v for v in row) for row in D]
 out=[];stats={'raw':81**3,'pairwise_and_cover':0,'source_median':0,'target_median_internal':0}
 for ia,a in enumerate(M):
  for ib,b in enumerate(M):
   ab=a&b
   if ab.bit_count()!=1:continue
   for ic,c in enumerate(M):
    ac=a&c;bc=b&c
    if ac.bit_count()!=1 or bc.bit_count()!=1 or ab&c:continue
    if (a|b|c).bit_count()!=9:raise AssertionError
    stats['pairwise_and_cover']+=1
    x,y,z=[x.bit_length()-1 for x in (ab,ac,bc)]
    if not med(x,y,z,3*i+2):continue
    stats['source_median']+=1
    rows=[D[j] for j in (ia,ib,ic)]
    owners={}
    for s,row in enumerate(rows):
     for t in pool(i):
      p=[v for v in row if v//3==t]
      if len(p)==2:owners[tuple(p)]=3*i+s
    bad=False
    for t in pool(i):
     ps=[(3*t,3*t+1),(3*t,3*t+2),(3*t+1,3*t+2)]
     if all(p in owners for p in ps):
      if not med(*[owners[p] for p in ps],3*t+2):bad=True;break
    if bad:continue
    stats['target_median_internal']+=1
    out.append(tuple(rows))
 return out,stats
if __name__=='__main__':
 out={}
 for i in range(9):
  D,s=group_domains(i);out[i]={'stats':s,'domains':D};print(i,s,flush=True)
 Path(__file__).with_name('evidence').joinpath('median_domains.json').write_text(json.dumps(out))
