import sys,json,itertools,time
from functools import lru_cache
sys.path.insert(0,'/mnt/data/work/erdos97_internal_support_2026_09_08')
import one_free as O
P,S,E,_=O.setup();Ts=[O.insertion_triangle(P,k)for k in range(9)]

@lru_cache(None)
def incoming(T):return tuple(O.allowed_incoming(P,S,T))
@lru_cache(None)
def outgoing(T,old):return tuple(range(42))if old is None else tuple(i for i,s in enumerate(S) if O.possible(O.free_to_regular_range(P,old,s,T)))
@lru_cache(None)
def mutual(T,U,old):
 if old is None:return True
 values=[]
 for f in T:
  r=O.dist(f,P[old]);values.extend(O.dist(f,g)-r for g in U)
  values.append(O.dist(f,O.closest_on_triangle(f,U))-r)
 return min(values)<=0<=max(values)

@lru_cache(None)
def trange(T,U):
 hi=max(O.dist(x,y)for x in T for y in U)
 if any(O.segment_meets_triangle(T[k],T[(k+1)%3],U)for k in range(3))or any(O.segment_meets_triangle(U[k],U[(k+1)%3],T)for k in range(3)):return O.Q(0),hi
 return min([O.dist(x,O.closest_on_triangle(x,U))for x in T]+[O.dist(x,O.closest_on_triangle(x,T))for x in U]),hi
@lru_cache(None)
def drange(i,T):return O.distance_interval(S[i],T)

def peel(A,need):
 active=set(range(44));layers=[]
 while True:
  rem=sorted(i for i in active if len(A[i]&active)<need[i])
  if not rem:return active,layers
  active.difference_update(rem);layers.append(rem)

def cliques(ranges,need):
 C=set()
 for t in sorted(set(v for interval in ranges.values()for v in interval)):
  c=frozenset(i for i,(lo,hi) in ranges.items()if lo<=t<=hi)
  if len(c)>=need:C.add(c)
 return sorted((c for c in C if not any(c<d for d in C)),key=lambda c:tuple(sorted(c)))

def base_graph(T,U,olds):
 A=[set()for _ in range(44)]
 for a,b in E:A[a].add(b)
 for k,V,old in[(42,T,olds[0]),(43,U,olds[1])]:
  for i in incoming(V):A[i].add(k)
  A[k].update(outgoing(V,old))
 if mutual(T,U,olds[0]):A[42].add(43)
 if mutual(U,T,olds[1]):A[43].add(42)
 return A,[2]*42+[4 if old is None else 3 for old in olds]

def possible_required(A,need,active,olds):
 # Generate conflicts between full forced rows; new labels are slot_id+9.
 rows={i:set(S[i].pair)if i<42 else (set()if olds[i-42]is None else{olds[i-42]}) for i in active}
 for i in active:
  if len(A[i]&active)==need[i]:rows[i].update(j+9 for j in A[i]&active)
 bad={tuple(sorted((i,j)))for i,j in itertools.combinations(sorted(active),2)if len(rows[i]&rows[j])>2}
 if (42,43)in bad:return False
 # Free centers are compulsory; remove ordinary nodes conflicting with either.
 forbidden={i for i in active if i<42 and ((i,42)in bad or (i,43)in bad)}
 if forbidden:return 'remove',forbidden
 for f in (42,43):
  opts=A[f]&active
  viable=[c for c in itertools.combinations(sorted(opts),need[f]) if all(tuple(sorted(pair))not in bad for pair in itertools.combinations(c,2))]
  if not viable:return False
  # A free source with forced witnesses carries active-requirement clauses.
 return True

def check(T,U,olds):
 A,need=base_graph(T,U,olds);act,l=peel(A,need)
 if 42 not in act or 43 not in act:return {'status':'peel','size':len(act)}
 cs=[]
 for k,V,W,old in[(42,T,U,olds[0]),(43,U,T,olds[1])]:
  if old is None:
   r={i:drange(i,V)if i<42 else trange(V,W)for i in A[k]&act}
   cs.append(cliques(r,need[k]))
  else:cs.append([frozenset(A[k]&act)])
 survivors=[];total=0
 for c,d in itertools.product(*cs):
  total+=1
  AA=[set(v)for v in A];AA[42]=set(c);AA[43]=set(d)
  active,lay=peel(AA,need)
  while 42 in active and 43 in active:
   r=possible_required(AA,need,active,olds)
   if type(r)is tuple:
    for i in r[1]:AA[i]=set()
    active,lay=peel(AA,need)
   else:break
  if 42 not in active or 43 not in active or r is False:continue
  survivors.append({'out42':sorted(c),'out43':sorted(d),'active':sorted(active),'adjacency':{i:sorted(AA[i]&active)for i in sorted(active)}})
 return {'status':'survivors'if survivors else'closed','initial_size':len(act),'radius_cases':total,'survivors':survivors}

if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--cells',nargs=2,type=int);ap.add_argument('--olds',nargs=2,type=int,default=[-1,-1]);args=ap.parse_args()
 old=tuple(None if j<0 else j for j in args.olds)
 cells=[args.cells] if args.cells else itertools.combinations_with_replacement(range(9),2)
 report=[]
 for a,b in cells:
  start=time.time();r=check(Ts[a],Ts[b],old);r.update(cells=[a,b],olds=old);report.append(r)
  print(a,b,r['status'],r.get('radius_cases'),len(r.get('survivors',[])),round(time.time()-start,2),flush=True)
 json.dump(report,open('/mnt/data/work/twofree-probe-report.json','w'),indent=2)
