#!/usr/bin/env python3
"""Independent exact verifier; Python standard library only.

No optimization, numerical tolerance, or import from search/. Reconstructs all
necessary chord-angle relations from the stated six-point metric hypotheses.
"""
from __future__ import annotations
import argparse,itertools,json,pathlib
from fractions import Fraction as F
ROOT=pathlib.Path(__file__).resolve().parents[1]
PAIRS=list(itertools.combinations(range(6),2));INDEX={p:i for i,p in enumerate(PAIRS)}
W={0:[1,2,3],1:[0,2,4],2:[0,1,5],3:[4,5],4:[3,5],5:[3,4]}
def ccw(order,t):
 a,b,c=[order.index(x) for x in t]
 return (b-a)%6<(c-a)%6

def system(order):
 """Return U beta < b and E beta = e, with angles measured in pi."""
 pos={v:i for i,v in enumerate(order)};U=[];b=[];E=[];e=[]
 for i,j,k in itertools.combinations(range(6),3):
  ij,ik,jk=[INDEX[p] for p in [(i,j),(i,k),(j,k)]]
  for entries,rhs in [({ij:1,ik:-1},0),({ik:1,jk:-1},0),({jk:1,ij:-1},1)]:
   row=[0]*15
   for z,c in entries.items():row[z]=c
   U.append(row);b.append(rhs)
 for center,partners in W.items():
  for left,right in itertools.combinations(partners,2):
   i,j,k=sorted([pos[center],pos[left],pos[right]])
   ij,ik,jk=[INDEX[p] for p in [(i,j),(i,k),(j,k)]];row=[0]*15
   if pos[center]==i:row[ij]=1;row[ik]=1;row[jk]=-2;rhs=-1
   elif pos[center]==j:row[ij]=1;row[jk]=1;row[ik]=-2;rhs=0
   else:row[ik]=1;row[jk]=1;row[ij]=-2;rhs=1
   E.append(row);e.append(rhs)
 row=[0]*15;row[INDEX[(0,1)]]=1;E.append(row);e.append(0)
 return U,b,E,e

def verify(data):
 expected={(0,)+tail for tail in itertools.permutations(range(1,6))
           if ccw((0,)+tail,(0,1,2)) and not ccw((0,)+tail,(3,4,5))}
 if len(expected)!=30:raise AssertionError('Order enumeration')
 seen=set();bounds={}
 for certificate in data['certificates']:
  order=tuple(certificate['order'])
  if order not in expected or order in seen:raise AssertionError('Missing/duplicate/unexpected order')
  seen.add(order);U,b,E,e=system(order)
  w=list(map(F,certificate['inequality_weights']));v=list(map(F,certificate['equality_weights']))
  if len(w)!=len(U) or len(v)!=len(E):raise AssertionError('Coefficient count')
  if any(x<0 for x in w) or not any(x>0 for x in w):raise AssertionError('Strict positive combination')
  for j in range(15):
   value=sum(w[i]*U[i][j] for i in range(len(U)))+sum(v[i]*E[i][j] for i in range(len(E)))
   if value!=0:raise AssertionError(f'Angle {j} fails cancellation in {order}')
  rhs=sum(w[i]*b[i] for i in range(len(U)))+sum(v[i]*e[i] for i in range(len(E)))
  if rhs!=F(certificate['right_hand_side']) or rhs>0:raise AssertionError('Wrong contradiction bound')
  bounds[str(rhs)]=bounds.get(str(rhs),0)+1
 if seen!=expected:raise AssertionError('Incomplete coverage')
 return dict(status='PASS_EXACT_RATIONAL_CERTIFICATES',orders=len(seen),
             contradiction_bounds=bounds,arithmetic='fractions.Fraction',
             relies_on_search_implementation=False,
             scope='Six-point opposite-orientation matched-equilateral obstruction only')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--certificate',type=pathlib.Path,
  default=ROOT/'candidate_counterexamples/opposite_triangle_contradictions.json')
 ap.add_argument('--check',action='store_true');args=ap.parse_args()
 report=verify(json.loads(args.certificate.read_text()))
 target=ROOT/'reports/opposite_triangle_exact_verification.json'
 if args.check:
  if report!=json.loads(target.read_text()):raise AssertionError('Stored report mismatch')
 else:target.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
