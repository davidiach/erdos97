"""Exact arithmetic and exact signs in Q(sqrt(3)); no floating point."""
from dataclasses import dataclass
from fractions import Fraction as F
from functools import total_ordering

@total_ordering
@dataclass(frozen=True)
class Q3:
    a: F = F(0)
    b: F = F(0)
    def __post_init__(self):
        object.__setattr__(self,'a',F(self.a));object.__setattr__(self,'b',F(self.b))
    @staticmethod
    def coerce(x):
        return x if isinstance(x,Q3) else Q3(F(x))
    def __add__(self,x):
        x=self.coerce(x);return Q3(self.a+x.a,self.b+x.b)
    __radd__=__add__
    def __neg__(self):return Q3(-self.a,-self.b)
    def __sub__(self,x):return self+-self.coerce(x)
    def __rsub__(self,x):return self.coerce(x)+-self
    def __mul__(self,x):
        x=self.coerce(x);return Q3(self.a*x.a+3*self.b*x.b,self.a*x.b+self.b*x.a)
    __rmul__=__mul__
    def __truediv__(self,x):
        x=self.coerce(x);d=x.a*x.a-3*x.b*x.b
        if d==0:raise ZeroDivisionError()
        return self*Q3(x.a/d,-x.b/d)
    def __pow__(self,k):
        if not isinstance(k,int) or k<0:raise ValueError('nonnegative integer exponent only')
        r=Q3(1);x=self
        while k:
            if k%2:r=r*x
            x=x*x;k//=2
        return r
    def sign(self):
        a,b=self.a,self.b
        if not b:return (a>0)-(a<0)
        if not a:return (b>0)-(b<0)
        if a>0 and b>0:return 1
        if a<0 and b<0:return -1
        c=a*a-3*b*b
        if not c:raise AssertionError('sqrt(3) irrationality violated')
        return ((c>0)-(c<0)) if a>0 else -((c>0)-(c<0))
    def __eq__(self,x):
        try:x=self.coerce(x)
        except (TypeError,ValueError):return False
        return self.a==x.a and self.b==x.b
    def __lt__(self,x):return (self-x).sign()<0
    def __hash__(self):return hash((self.a,self.b))
    def dump(self):return [str(self.a),str(self.b)]
    @classmethod
    def load(cls,x):
        if not isinstance(x,list)or len(x)!=2:raise ValueError('expected two rational coefficients')
        return cls(F(x[0]),F(x[1]))

def dot(u,v):return u[0]*v[0]+u[1]*v[1]
def sub(u,v):return u[0]-v[0],u[1]-v[1]
def cross(u,v):return u[0]*v[1]-u[1]*v[0]
def sqdist(u,v):return dot(sub(u,v),sub(u,v))
