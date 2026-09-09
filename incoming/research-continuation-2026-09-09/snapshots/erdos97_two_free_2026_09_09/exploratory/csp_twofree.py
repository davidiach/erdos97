import sys,itertools,time,json
from functools import lru_cache
sys.path.insert(0,'/mnt/data/work')
import twofree_probe as G
O,P,S=G.O,G.P,G.S

class Search:
 def __init__(self, report, cells, olds, limit=100000):
  self.A={int(i):v for i,v in report['adjacency'].items()};self.olds=olds
  self.need={i:2 if i<42 else 4 if olds[i-42] is None else 3 for i in self.A}
  self.ranks={v:2*k for k,v in enumerate(O.B.ORDER)}
  self.ranks.update({i+9:2*S[i].cell+1 for i in range(42)})
  self.ranks.update({51:2*cells[0]+1,52:2*cells[1]+1})
  self.options={i:[(sum(1<<j for j in opt),sum(1<<(j+9) for j in opt)|self.oldmask(i))for opt in itertools.combinations(a,self.need[i])]for i,a in self.A.items()}
  self.nodes=0;self.limit=limit;self.stats={};self.start=time.time()
 def oldmask(self,i):
  if i<42:return sum(1<<j for j in S[i].pair)
  old=self.olds[i-42];return 0 if old is None else 1<<old
 @lru_cache(None)
 def cross_possible(self,i,j,a,b):
  # In a convex realization, the two center labels and two common witnesses must alternate.
  r=[self.ranks[k]for k in(i+9,j+9,a,b)]
  for perm in itertools.permutations(range(4)):
   if [r[k]for k in perm]!=sorted(r):continue
   if [int(k<2)for k in perm]in([0,1,0,1],[1,0,1,0]):return True
  return False
 def compatible(self,i,row,j,other):
  shared=row&other
  c=shared.bit_count()
  if c<=1:return True
  if c>=3:return False
  a=(shared&-shared).bit_length()-1;b=(shared^(1<<a)).bit_length()-1
  return self.cross_possible(i,j,a,b)
 def run(self):
  def visit(assigned,required,domains):
   self.nodes+=1
   if self.nodes>self.limit:raise TimeoutError('node budget')
   todo=required-sum(1<<i for i in assigned)
   if not todo:return {i:list(k for k in range(53)if row>>k&1)for i,(_,row)in assigned.items()}
   active=[]
   while todo:
    bit=todo&-todo;todo^=bit;i=bit.bit_length()-1
    if not domains[i]:return None
    active.append(i)
   i=min(active,key=lambda i:len(domains[i]))
   for opt in domains[i]:
    targets,row=opt
    selected={**assigned,i:opt};req=required|targets
    if any(not self.compatible(i,row,j,r)for j,(_,r)in assigned.items()):continue
    dom={}
    impossible=0
    for j,opts in domains.items():
     if j in selected:continue
     dd=[o for o in opts if self.compatible(i,row,j,o[1])]
     dom[j]=dd
     if not dd:impossible|=1<<j
    if req&impossible:continue
    # Remove options using a label with no compatible row and iterate domain deletion.
    while impossible:
     lost=0
     for j,opts in dom.items():
      if not opts:continue
      dd=[o for o in opts if not o[0]&impossible]
      dom[j]=dd
      if not dd:lost|=1<<j
     impossible=lost
     if req&lost:break
    else:
     found=visit(selected,req,dom)
     if found:return found
   return None
  try:result=visit({},(1<<42)|(1<<43),self.options);status='survivor'if result else'exhausted'
  except TimeoutError:result=None;status='budget'
  return {'status':status,'nodes':self.nodes,'seconds':time.time()-self.start,'rows':result}

if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--cells',nargs=2,type=int,default=[0,0]);ap.add_argument('--limit',type=int,default=100000);args=ap.parse_args()
 r=G.check(G.Ts[args.cells[0]],G.Ts[args.cells[1]],(None,None));res=[]
 for c in r['survivors']:
  s=Search(c,args.cells,(None,None),args.limit);q=s.run();res.append(q);print(q,flush=True)
 json.dump(res,open('/mnt/data/work/csp-result.json','w'),indent=2)
