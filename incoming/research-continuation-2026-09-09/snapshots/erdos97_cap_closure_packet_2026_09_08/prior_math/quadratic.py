"""Exact Q(sqrt(721)); points (x,y) mean Cartesian (x,sqrt(3)*y)."""
from __future__ import annotations
from fractions import Fraction as F
from functools import total_ordering
from itertools import combinations

D = F(721)

@total_ordering
class Q:
    __slots__ = ('a', 'b')
    def __init__(self,a=0,b=0):
        if isinstance(a,float) or isinstance(b,float): raise TypeError('floating-point input is not exact')
        if isinstance(a,Q):
            if b: raise ValueError('invalid second argument')
            self.a,self.b=a.a,a.b
        else: self.a,self.b=F(a),F(b)
    def __add__(self,o):
        o=Q(o);return Q(self.a+o.a,self.b+o.b)
    __radd__=__add__
    def __neg__(self):return Q(-self.a,-self.b)
    def __sub__(self,o):return self+-Q(o)
    def __rsub__(self,o):return Q(o)+-self
    def __mul__(self,o):
        o=Q(o);return Q(self.a*o.a+D*self.b*o.b,self.a*o.b+self.b*o.a)
    __rmul__=__mul__
    def __truediv__(self,o):
        o=Q(o);den=o.a*o.a-D*o.b*o.b
        if not den:raise ZeroDivisionError
        return self*Q(o.a/den,-o.b/den)
    def __rtruediv__(self,o):return Q(o)/self
    def __pow__(self,n):
        if not isinstance(n,int):raise TypeError
        if n<0:return (1/self)**(-n)
        out=Q(1);b=self
        while n:
            if n&1:out=out*b
            b=b*b;n//=2
        return out
    def sign(self):
        a,b=self.a,self.b
        if not a:return (b>0)-(b<0)
        if not b:return (a>0)-(a<0)
        if (a>0)==(b>0):return (a>0)-(a<0)
        h=a*a-D*b*b
        return ((h>0)-(h<0))*((a>0)-(a<0))
    def __bool__(self):return bool(self.a or self.b)
    def __eq__(self,o):
        try:o=Q(o)
        except (TypeError,ValueError):return NotImplemented
        return (self.a,self.b)==(o.a,o.b)
    def __lt__(self,o):return (self-Q(o)).sign()<0
    def __hash__(self):return hash(self.a) if self.b==0 else hash((self.a,self.b))
    def __float__(self):return float(self.a)+float(self.b)*float(D)**.5
    def __repr__(self):return f'Q({str(self.a)!r},{str(self.b)!r})'
    def json(self):return [str(self.a),str(self.b)]

def p(x,y):return Q(x),Q(y)
def add(a,b):return a[0]+b[0],a[1]+b[1]
def sub(a,b):return a[0]-b[0],a[1]-b[1]
def mul(a,t):return a[0]*t,a[1]*t
def cross(a,b):return a[0]*b[1]-a[1]*b[0]
def turn(a,b,c):return cross(sub(b,a),sub(c,a))
def dot(a,b):return a[0]*b[0]+3*a[1]*b[1]
def norm(a):return dot(a,a)
def dist(a,b):return norm(sub(a,b))
def rot(a):return (-a[0]-3*a[1])/2,(a[0]-a[1])/2

def hull(points):
    if len(set(points))!=len(points):raise ValueError('duplicate points')
    ids=sorted(range(len(points)),key=lambda i:points[i])
    if len(ids)<3:return ids
    def half(seq):
        out=[]
        for i in seq:
            while len(out)>1 and turn(points[out[-2]],points[out[-1]],points[i])<=0:out.pop()
            out.append(i)
        return out
    return half(ids)[:-1]+half(ids[::-1])[:-1]

def strict(points):return len(hull(points))==len(points)

def circle(a,b,c):
    u,v=sub(b,a),sub(c,a)
    determinant=6*cross(u,v)
    if not determinant:return None
    ub=norm(b)-norm(a);vc=norm(c)-norm(a)
    x=3*(ub*v[1]-u[1]*vc)/determinant
    y=(u[0]*vc-ub*v[0])/determinant
    return x,y

def classes(points,center):
    out={}
    for j,q in enumerate(points):
        r=dist(center,q)
        if r:out.setdefault(r,[]).append(j)
    return sorted(out.items(),key=lambda a:a[0])

def maximum(points,c):return max((len(v) for r,v in classes(points,c)),default=0)

def z(t):
    t=Q(t);den=1+3*t*t
    return -Q(F(1,2))+3*t/den,(1-3*t*t)/(2*den)

def base9():
    t0=Q(F(1,10));t1=Q(F(83,200),-F(3,200))
    out=[]
    for a in [p(1,0),z(t0),(z(t1)[0],-z(t1)[1])]:
        out.extend([a,rot(a),rot(rot(a))])
    return out

def cycle9():
    A,B,C=p(0,0),p(1,0),p(F(1,2),F(1,2));O=p(F(1,2),F(1,6))
    out=[A,B,C]
    for t in [F(1,40),F(1,20)]:
        a=p((1-3*t*t)/(1+3*t*t),-2*t/(1+3*t*t))
        out.extend([add(O,rotpow(sub(a,O),k)) for k in range(3)])
    return out

def rotpow(a,k):
    for _ in range(k):a=rot(a)
    return a

def repair18():
    """Nine-point seed plus nine off-carrier points, all coordinates exact."""
    P=base9()
    for q in [p(F(-10585,20006),F(-9397,20006)),
              p(F(-2785,5006),F(-2197,5006)),
              p(F(209908,260281),F(-34731,260281))]:
        P.extend([rotpow(q,k) for k in range(3)])
    return P
