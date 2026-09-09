"""Small rational polynomial/Sturm/interval kernel. No floats enter exact checks."""
from fractions import Fraction as F
from typing import Iterable

Poly=tuple[F,...]
def poly(a:Iterable)->Poly:
    a=list(a)
    if any(isinstance(x,(float,bool))for x in a):raise TypeError('inexact or boolean polynomial coefficient')
    z=[F(x) for x in a]
    if not z:z=[F(0)]
    while len(z)>1 and not z[-1]:z.pop()
    return tuple(z)
ZERO=poly([0]);ONE=poly([1]);X=poly([0,1])
def add(a,b):return poly((a[i]if i<len(a)else 0)+(b[i]if i<len(b)else 0)for i in range(max(len(a),len(b))))
def neg(a):return poly(-x for x in a)
def sub(a,b):return add(a,neg(b))
def scale(a,s):return poly(x*s for x in a)
def mul(a,b):
    z=[F(0)]*(len(a)+len(b)-1)
    for i,u in enumerate(a):
        for j,v in enumerate(b):z[i+j]+=u*v
    return poly(z)
def square(a):return mul(a,a)
def ev(a,x):
    y=F(0)
    for v in reversed(a):y=y*x+v
    return y
def deriv(a):return poly(i*a[i]for i in range(1,len(a)))
def divrem(a,b):
    a,b=poly(a),poly(b)
    if b==ZERO:raise ZeroDivisionError('polynomial division by zero')
    q=[F(0)]*max(1,len(a)-len(b)+1);r=list(a)
    while len(r)>=len(b) and poly(r)!=ZERO:
        k=len(r)-len(b);v=r[-1]/b[-1];q[k]+=v
        for j,w in enumerate(b):r[k+j]-=v*w
        r=list(poly(r))
    return poly(q),poly(r)
def monic(a):return scale(a,1/a[-1])if a!=ZERO else ZERO
def gcd(a,b):
    while b!=ZERO:a,b=b,divrem(a,b)[1]
    return monic(a)
def sqfree(a):
    if a==ZERO:raise ValueError('zero polynomial has no finite root census')
    if len(a)==1:return ONE
    q,r=divrem(a,gcd(a,deriv(a)))
    if r!=ZERO:raise ArithmeticError('square-free quotient is not exact')
    return monic(q)
def sturm(a):
    a=sqfree(a)
    if len(a)==1:return [a]
    seq=[a,deriv(a)]
    while True:
        r=neg(divrem(seq[-2],seq[-1])[1])
        if r==ZERO:return seq
        # Positive scaling leaves signs and the Sturm property unchanged.
        r=scale(r,1/abs(r[-1]));seq.append(r)
def variations(values):
    ss=[1 if x>0 else -1 for x in values if x]
    return sum(a!=b for a,b in zip(ss,ss[1:]))
def roots_closed(a,lo,hi):
    if lo>hi:raise ValueError('reversed root interval')
    a=sqfree(a)
    if lo==hi:return int(ev(a,lo)==0)
    endpoints=0
    for x in (lo,hi):
        if ev(a,x)==0:
            endpoints+=1;a,r=divrem(a,poly([-x,1]))
            if r!=ZERO:raise ArithmeticError('endpoint division failed')
    ss=sturm(a)
    return endpoints+variations(ev(q,lo)for q in ss)-variations(ev(q,hi)for q in ss)
def interval_mul(a,b):
    z=[x*y for x in a for y in b];return min(z),max(z)
def interval(a,lo,hi):
    if lo>hi:raise ValueError('reversed interval')
    z=(F(0),F(0))
    for v in reversed(a):
        l,h=interval_mul(z,(lo,hi));z=(l+v,h+v)
    return z

def sign_at_root(a,f,lo,hi):
    if roots_closed(f,lo,hi)!=1:raise ValueError('root must be uniquely isolated')
    a=divrem(a,f)[1]
    if a==ZERO or roots_closed(gcd(a,f),lo,hi):return 0
    for _ in range(256):
        l,h=interval(a,lo,hi)
        if l>0:return 1
        if h<0:return -1
        mid=(lo+hi)/2
        if ev(f,mid)==0:return 1 if ev(a,mid)>0 else -1
        if roots_closed(f,lo,mid):hi=mid
        else:lo=mid
    raise ArithmeticError('could not separate algebraic sign after 256 bisections')
