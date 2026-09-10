"""Q[s]/(7s^4-24s^3+44s^2-42s+13), with a specified real embedding.
Standard-library exact arithmetic. Nonzero signs require rational interval separation.
"""
from fractions import Fraction as F
from functools import lru_cache
from functools import total_ordering

MOD = tuple(map(F, (13,-42,44,-24,7)))
INITIAL = (F(536,1000),F(537,1000))

def trim(p):
    p=list(p)
    while p and not p[-1]:p.pop()
    return p

def add(a,b):
    return trim([(a[i]if i<len(a)else F(0))+(b[i]if i<len(b)else F(0)) for i in range(max(len(a),len(b)))])

def mul(a,b):
    p=[F(0)]*max(0,len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):p[i+j]+=x*y
    return trim(p)

def divmod_poly(a,b):
    a=trim(a);b=trim(b)
    if not b:raise ZeroDivisionError
    q=[F(0)]*max(0,len(a)-len(b)+1)
    while len(a)>=len(b):
        k=len(a)-len(b);v=a[-1]/b[-1];q[k]=v
        for j,w in enumerate(b):a[k+j]-=v*w
        a=trim(a)
    return trim(q),a

def evaluate(p,s):
    v=F(0)
    for c in reversed(p):v=v*s+c
    return v

def interval_mul(a,b):
    vals=[x*y for x in a for y in b]
    return min(vals),max(vals)

def interval_value(p,ab):
    v=(F(0),F(0))
    for c in reversed(p):
        lo,hi=interval_mul(v,ab);v=(lo+c,hi+c)
    return v

def validate_embedding():
    a,b=INITIAL
    if not evaluate(MOD,a)>0 or not evaluate(MOD,b)<0:raise ValueError('root bracket')
    derivative=[i*MOD[i]for i in range(1,len(MOD))]
    if interval_value(derivative,(a,b))[1]>=0:raise ValueError('not certified strictly decreasing')
    # IVT plus strict decrease proves one and only one real root in this interval.
    return True

@lru_cache(maxsize=None)
def root_interval(bits):
    validate_embedding();a,b=INITIAL
    for _ in range(bits):
        m=(a+b)/2;t=evaluate(MOD,m)
        if t>0:a=m
        elif t<0:b=m
        else:return m,m
    return a,b

@total_ordering
class K:
    def __init__(self,c=0):
        if isinstance(c,K):self.c=c.c;return
        p=list(map(F,c))if isinstance(c,(list,tuple))else[F(c)]
        self.c=tuple(divmod_poly(p,MOD)[1])
    def __add__(self,other):return K(add(self.c,K(other).c))
    __radd__=__add__
    def __neg__(self):return K([-x for x in self.c])
    def __sub__(self,other):return self+-K(other)
    def __rsub__(self,other):return K(other)+-self
    def __mul__(self,other):return K(mul(self.c,K(other).c))
    __rmul__=__mul__
    def reciprocal(self):
        r0,r1=list(MOD),list(self.c);t0,t1=[],[F(1)]
        while r1:
            q,r=divmod_poly(r0,r1);r0,r1=r1,r
            t0,t1=t1,add(t0,[-v for v in mul(q,t1)])
        if len(r0)!=1:raise ZeroDivisionError('nonunit in quotient')
        return K([v/r0[0]for v in t0])
    def __truediv__(self,other):return self*K(other).reciprocal()
    def __rtruediv__(self,other):return K(other)*self.reciprocal()
    def __pow__(self,n):
        if type(n)is not int or n<0:raise ValueError('nonnegative integral exponent')
        a=self;r=K(1)
        while n:
            if n&1:r=r*a
            a=a*a;n//=2
        return r
    def sign(self):
        if not self.c:return 0
        for bits in (16,32,64,128,256):
            lo,hi=interval_value(self.c,root_interval(bits))
            if lo>0:return 1
            if hi<0:return -1
        raise ValueError('nonzero sign not isolated')
    def __eq__(self,other):return not(self-K(other)).c
    def __lt__(self,other):return (self-K(other)).sign()<0
    def __hash__(self):return hash(self.c)
    def dump(self):return [str(x)for x in self.c]or['0']
    def approximate(self):return float(evaluate(self.c,sum(root_interval(64))/2))

S=K([0,1])
def cadd(a,b):return a[0]+b[0],a[1]+b[1]
def csub(a,b):return a[0]-b[0],a[1]-b[1]
def cmul(a,b):return a[0]*b[0]-3*a[1]*b[1],a[0]*b[1]+a[1]*b[0]
def cnorm(a):return a[0]**2+3*a[1]**2
def cdiv(a,b):return cmul(a,(b[0]/cnorm(b),-b[1]/cnorm(b)))
def rotate(a):return(-a[0]-3*a[1])/2,(a[0]-a[1])/2
def det(a,b):return a[0]*b[1]-a[1]*b[0]
