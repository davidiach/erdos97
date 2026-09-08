#!/usr/bin/env python3
"""Exact coordinate controls, independent of all code in search/.

Arithmetic in Q(sqrt(3), sqrt(-519+348sqrt(3)),sqrt(-761+488sqrt(3))).
Signs use rational outward enclosures in the positive-root real embedding.
No floating-point hull routine or distance tolerance is used.
"""
from __future__ import annotations
import argparse,itertools,json,math,pathlib
from fractions import Fraction as Q
from functools import lru_cache,cmp_to_key
ROOT=pathlib.Path(__file__).resolve().parents[1]

# Basis 1,S,A,SA,B,SB,AB,SAB, with S^2=3, A^2=-519+348S,
# B^2=-761+488S. Multiplication is reduced symbolically, not numerically.
@lru_cache(None)
def monomial(s:int,a:int,b:int):
 if s>=2:return tuple(3*x for x in monomial(s-2,a,b))
 if a>=2:
  x,y=monomial(s,a-2,b),monomial(s+1,a-2,b)
  return tuple(-519*t+348*u for t,u in zip(x,y))
 if b>=2:
  x,y=monomial(s,a,b-2),monomial(s+1,a,b-2)
  return tuple(-761*t+488*u for t,u in zip(x,y))
 out=[0]*8;out[s+2*a+4*b]=1;return tuple(out)
TABLE=[[monomial((i&1)+(j&1),((i>>1)&1)+((j>>1)&1),((i>>2)&1)+((j>>2)&1))for j in range(8)]for i in range(8)]
class K:
 __slots__=('c',)
 def __init__(self,value=0):
  self.c=value.c if isinstance(value,K) else tuple(map(Q,value)) if isinstance(value,(list,tuple)) else (Q(value),)+(Q(0),)*7
  if len(self.c)!=8:raise ValueError('Eight basis coefficients required')
 def __add__(self,other):
  o=K(other);return K(tuple(x+y for x,y in zip(self.c,o.c)))
 __radd__=__add__
 def __neg__(self):return K(tuple(-x for x in self.c))
 def __sub__(self,other):return self+-K(other)
 def __rsub__(self,other):return K(other)+-self
 def __mul__(self,other):
  o=K(other);out=[Q(0)]*8
  for i,x in enumerate(self.c):
   if not x:continue
   for j,y in enumerate(o.c):
    if not y:continue
    v=x*y
    for k,m in enumerate(TABLE[i][j]):
     if m:out[k]+=m*v
  return K(out)
 __rmul__=__mul__
 def inv(self):
  cols=[(self*K(tuple(int(i==j) for i in range(8)))).c for j in range(8)]
  mat=[[cols[j][i]for j in range(8)]+[Q(i==0)]for i in range(8)]
  for j in range(8):
   pivot=next((i for i in range(j,8) if mat[i][j]),None)
   if pivot is None:raise ZeroDivisionError('Non-invertible element')
   mat[j],mat[pivot]=mat[pivot],mat[j];d=mat[j][j];mat[j]=[x/d for x in mat[j]]
   for i in range(8):
    if i!=j and mat[i][j]:
     d=mat[i][j];mat[i]=[a-d*b for a,b in zip(mat[i],mat[j])]
  return K(tuple(row[-1]for row in mat))
 def __truediv__(self,other):return self*K(other).inv()
 def __pow__(self,k):
  if k<0:return self.inv()**(-k)
  out=K(1);a=self
  while k:
   if k&1:out=out*a
   a=a*a;k//=2
  return out
 def __eq__(self,o):return self.c==K(o).c
 def __hash__(self):return hash(self.c)
 def sign(self):return sign_coeffs(self.c)
 def data(self):return [str(x) for x in self.c]
S=K([0,1,0,0,0,0,0,0]);A=K([0,0,1,0,0,0,0,0]);B=K([0,0,0,0,1,0,0,0])

def interval_mul(x,y):
 vals=[a*b for a in x for b in y];return min(vals),max(vals)
def sqrt_bracket(x:Q,bits:int):
 if x<0:raise ValueError('Negative radicand bound')
 den=1<<bits;r=math.isqrt((x.numerator*den*den)//x.denominator)
 lo=Q(r,den);return lo,Q(r+1,den)
@lru_cache(None)
def basis_intervals(bits):
 slo,shi=sqrt_bracket(Q(3),bits)
 alo=sqrt_bracket(-519+348*slo,bits)[0];ahi=sqrt_bracket(-519+348*shi,bits)[1]
 blo=sqrt_bracket(-761+488*slo,bits)[0];bhi=sqrt_bracket(-761+488*shi,bits)[1]
 roots=[(slo,shi),(alo,ahi),(blo,bhi)];out=[]
 for i in range(8):
  v=(Q(1),Q(1))
  for bit in range(3):
   if (i>>bit)&1:v=interval_mul(v,roots[bit])
  out.append(v)
 return out
@lru_cache(None)
def sign_coeffs(c):
 if not any(c):return 0
 for bits in [64,128,256,512,1024,2048]:
  lo=hi=Q(0)
  for v,(a,b) in zip(c,basis_intervals(bits)):
   if v>=0:lo+=v*a;hi+=v*b
   else:lo+=v*b;hi+=v*a
  if lo>0:return 1
  if hi<0:return -1
 raise ArithmeticError('Unable to separate sign by certified intervals')

class C:
 __slots__=('x','y')
 def __init__(self,x=0,y=0):self.x=K(x);self.y=K(y)
 def __add__(self,o):o=o if isinstance(o,C) else C(o);return C(self.x+o.x,self.y+o.y)
 __radd__=__add__
 def __neg__(self):return C(-self.x,-self.y)
 def __sub__(self,o):return self+-(o if isinstance(o,C)else C(o))
 def __mul__(self,o):o=o if isinstance(o,C) else C(o);return C(self.x*o.x-self.y*o.y,self.x*o.y+self.y*o.x)
 __rmul__=__mul__
 def norm(self):return self.x*self.x+self.y*self.y
 def data(self):return [self.x.data(),self.y.data()]
OMEGA=C(-Q(1,2),S/2)
def orbit(z):return [z,z*OMEGA,z*OMEGA*OMEGA]
def cross(a,b):return a.x*b.y-a.y*b.x

def hull_exact(points):
 def cmp(i,j):
  s=(points[i].x-points[j].x).sign()
  return s if s else (points[i].y-points[j].y).sign()
 seq=sorted(range(len(points)),key=cmp_to_key(cmp))
 for a,b in zip(seq,seq[1:]):
  if cmp(a,b)==0:raise AssertionError('Duplicate points')
 def half(seq):
  h=[]
  for i in seq:
   while len(h)>1 and cross(points[h[-1]]-points[h[-2]],points[i]-points[h[-1]]).sign()<=0:h.pop()
   h.append(i)
  return h
 return half(seq)[:-1]+half(seq[::-1])[:-1]

def X(t):
 t=K(t);d=(1+t*t).inv()
 return C(1+S*(1-t*t)*d,2*S*t*d)

def control27():
 ua=(9-3*S-A)/(-75+44*S);ub=(16-8*S-2*B)/(-162+96*S)
 assert ((-75+44*S)*ua*ua+(-18+6*S)*ua-33-14*S)==0
 assert ((-162+96*S)*ub*ub+(-32+16*S)*ub-50-16*S)==0
 # The signs of the leading coefficients and selected square roots specify
 # the lower roots; these are independent of any decimal approximations.
 assert (-75+44*S).sign()>0 and (-162+96*S).sign()>0 and A.sign()>0 and B.sign()>0
 a=[C(1),X(2),X(2)*X(ua)];b=[C(1),X(3),X(3)*X(ub)]
 reps=[x*y for x in a for y in b];pts=[p for z in reps for p in orbit(z)]
 norms=[z.norm()for z in reps]
 for n in norms:assert n.sign()>0
 for x,y in itertools.combinations(norms,2):assert (x-y).sign()!=0
 def ix(i,j,k):return (3*i+j)*3+k%3
 ws=[]
 for i,j,k in itertools.product(range(3),repeat=3):
  row=[ix(i,j,k+1),ix(i,j,k+2),ix((i+1)%3,j,k+(i==2)),ix(i,(j+1)%3,k+(j==2))]
  center=ix(i,j,k);assert len(set(row))==4 and center not in row
  for q in row:assert (pts[center]-pts[q]).norm()==3*pts[center].norm()
  ws.append(row)
 h=hull_exact(pts);assert len(h)==18
 interior=sorted(set(range(27))-set(h));assert interior==[0,1,2,6,7,8,18,19,20]
 margins=0
 for i,j in zip(h,h[1:]+h[:1]):
  for k in range(27):
   if k in (i,j):continue
   assert cross(pts[j]-pts[i],pts[k]-pts[i]).sign()>0;margins+=1
 return dict(kind='exact_nonconvex_all_rich_control',basis=['1','S','A','S*A','B','S*B','A*B','S*A*B'],
  radicands=dict(S='3',A='-519+348*S',B='-761+488*S'),root_embedding='all three square roots positive',
  point_order='index=(3*i+j)*3+k',coordinates=[p.data()for p in pts],witnesses=ws,
  hull=h,strict_interior=interior,distance_equalities_verified=108,strict_supporting_signs_verified=margins)

def control12():
 a=X(Q(8,3));b=X(Q(11,4));reps=[C(1),a,b,a*b];pts=[p for z in reps for p in orbit(z)]
 assert (a-1).norm()==3 and (b-1).norm()==3
 assert a.y.sign()>0 and b.y.sign()>0
 assert (a*b-a).norm()==3*a.norm() and (a*b-b).norm()==3*b.norm()
 h=hull_exact(pts);assert len(h)==12
 count=0
 for i,j in zip(h,h[1:]+h[:1]):
  for k in range(12):
   if k not in (i,j):assert cross(pts[j]-pts[i],pts[k]-pts[i]).sign()>0;count+=1
 return dict(kind='exact_convex_same_half_plane_diamond_control',coordinates=[p.data()for p in pts],
  field='Q(sqrt(3)); stored in the same eight-coordinate basis as the 27-point control',
  multiplier_parameters=['8/3','11/4'],hull=h,strict_supporting_signs_verified=count)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');ap.add_argument('--which',choices=['12','27','all'],default='all');a=ap.parse_args()
 outputs={}
 if a.which in ['12','all']:outputs['convex_diamond_12']=control12()
 if a.which in ['27','all']:outputs['product_27_exact_nonconvex']=control27()
 for name,data in outputs.items():
  path=ROOT/'candidate_counterexamples'/f'{name}.json'
  if a.check:
   if data!=json.loads(path.read_text()):raise AssertionError('Stored exact control mismatch: '+name)
  else:path.write_text(json.dumps(data,indent=2)+'\n')
 report={name:{k:v for k,v in data.items()if k not in ['coordinates','basis','radicands','root_embedding','point_order','field']}for name,data in outputs.items()}
 print(json.dumps(dict(status='PASS_EXACT_ALGEBRAIC_CONTROLS',controls=report),indent=2))
 if not a.check:(ROOT/'reports'/f'exact_controls_{a.which}.json').write_text(json.dumps(dict(status='PASS_EXACT_ALGEBRAIC_CONTROLS',controls=report),indent=2)+'\n')
if __name__=='__main__':main()
