import sys,itertools,json
from functools import lru_cache
sys.path.insert(0,'/mnt/data/work')
import twofree_probe as G
O,P,S=G.O,G.P,G.S

def can_coexist(c,D,d,E):
 if c==d:
  a,b=P[O.B.ORDER[c]],P[O.B.ORDER[(c+1)%9]]
  return any(max(O.turn(a,x,y) for x in L for y in R)>0 and max(O.turn(x,y,b)for x in L for y in R)>0 for L,R in[(D,E),(E,D)])
 if d==(c+1)%9:
  return max(O.turn(x,P[O.B.ORDER[d]],y) for x in D for y in E)>0
 if c==(d+1)%9:
  return max(O.turn(y,P[O.B.ORDER[c]],x)for x in D for y in E)>0
 return True

@lru_cache(None)
def conflicts(T,U,cells):
 D={i:[s.point(s.lower),s.point(s.upper)]for i,s in enumerate(S)}
 D.update({42:T,43:U});C={i:s.cell for i,s in enumerate(S)};C.update({42:cells[0],43:cells[1]})
 return {pair for pair in itertools.combinations(range(44),2)if not can_coexist(C[pair[0]],D[pair[0]],C[pair[1]],D[pair[1]])}
if __name__=='__main__':
 for cells in [(0,0),(0,3),(2,5)]:
  b=conflicts(G.Ts[cells[0]],G.Ts[cells[1]],cells);print(cells,len(b),sorted(b))
