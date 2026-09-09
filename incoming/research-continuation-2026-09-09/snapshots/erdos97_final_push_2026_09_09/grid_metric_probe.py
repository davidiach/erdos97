"""Exact all-rich metric construction: exploratory until verified."""
from fractions import Fraction as F
from itertools import combinations
from math import gcd,ceil
from functools import reduce
from pathlib import Path
import json

def grid_lines(k=7):
 P=[(x,y) for x in range(k) for y in range(k)]
 d={}
 for i,j in combinations(range(len(P)),2):
  x,y=P[i];u,v=P[j];A=y-v;B=u-x;C=x*v-u*y
  g=reduce(gcd,(A,B,C));A//=g;B//=g;C//=g
  if A<0 or (A==0 and B<0):A,B,C=-A,-B,-C
  d.setdefault((A,B,C),set()).update((i,j))
 return P,[(L,sorted(I)) for L,I in sorted(d.items()) if len(I)>=4]

def make(k=7,M=10**6):
 P,L=grid_lines(k)
 deg=[sum(j in I for line,I in L) for j in range(len(P))]
 print('points',len(P),'lines',len(L),'min degrees',min(deg),min(len(I) for _,I in L),flush=True)
 X=[(F(x+11*y,M+x+97*y),F(y,M+x+97*y)) for x,y in P]
 LL=[]
 for line,I in L:
  (x,y),(u,v)=[X[j] for j in I[:2]]
  if x==u:raise ValueError('vertical')
  m=(v-y)/(u-x);b=y-m*x
  assert all(X[j][1]==m*X[j][0]+b for j in I)
  LL.append((-m,-b,line,I))
 assert len({x for x,y in X})==len(X)
 assert len({l[0] for l in LL})==len(LL)
 po=sorted(range(len(P)),key=lambda j:X[j][0]);LL.sort()
 B=[[al*X[j][0]+be+X[j][1] for j in po] for al,be,_,_ in LL]
 # Compute signs, min strict elementary cross difference, etc.
 n=len(LL)+len(X);na=len(LL);nb=len(X);V=ceil(max(abs(v) for row in B for v in row))
 K=4*n+4*V+10;R=10*K*n+10*V+10
 D=[[F(0) for j in range(n)]for i in range(n)]
 for i,j in combinations(range(n),2):
  if (i<na)==(j<na):s=j-i;d=F(K*s-s*s)
  else:d=R+B[i][j-na]
  D[i][j]=D[j][i]=d
 rows=[]
 for i in range(na):rows.append([na+j for j,v in enumerate(B[i]) if v==0])
 for j in range(nb):rows.append([i for i in range(na) if B[i][j]==0])
 print('n',n,'V',V,'K',K,'R',R,'min witnesses',min(map(len,rows)),flush=True)
 # Local cyclic four point matrices. Check all quadruples for n small; otherwise generator.
 bcount=0;minsl=None;bad=[]
 for i in range(n):
  a=i;b=(i+1)%n
  for j in range(i+1,n):
   c=j;d=(j+1)%n
   if len({a,b,c,d})<4:continue
   v=D[a][c]+D[b][d]-D[a][d]-D[b][c]
   bcount+=1
   if v<=0:bad.append((a,b,c,d,str(v)))
   minsl=v if minsl is None else min(minsl,v)
 print('elementary',bcount,'bad',len(bad),'min',str(minsl),flush=True)
 return {'schema':'grid_metric_probe_v1','k':k,'M':M,'old_grid':P,'lines':[[list(l),I] for a,b,l,I in LL], 'point_order':po,'projective_points':[[str(a),str(b)]for a,b in X], 'line_alpha_beta':[[str(a),str(b)]for a,b,l,I in LL], 'n':n,'line_vertices':na,'K':K,'R':R,'cross_B':[[str(v)for v in row]for row in B],'witnesses':rows,'elementary_checks':bcount,'bad':bad,'min_elementary':str(minsl)}
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--k',type=int,default=7);a=p.parse_args()
 result=make(a.k);Path(__file__).with_name('evidence').joinpath(f'grid_metric_{a.k}.json').write_text(json.dumps(result,indent=2))
