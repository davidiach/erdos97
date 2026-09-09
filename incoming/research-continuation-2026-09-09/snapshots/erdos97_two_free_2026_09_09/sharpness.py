"""Exact 15-point control: three internally supported vertices are attainable.

The configuration is the known recurrence continued twice, not a new
construction or an all-rich polygon. Arithmetic uses a tower of positive
quadratic radicals; signs are reduced recursively to rational comparisons.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as F
from functools import lru_cache, total_ordering
import json
from pathlib import Path

RADICANDS: list[tuple[F, ...]] = []


def plus(a, b):
    return tuple(x+y for x,y in zip(a,b))


def minus(a, b):
    return tuple(x-y for x,y in zip(a,b))


@lru_cache(maxsize=None)
def product(a, b):
    if len(a)!=len(b):raise ValueError('Unequal coefficient dimensions')
    if len(a)==1:return (a[0]*b[0],)
    m=len(a)//2
    a0,a1,b0,b1=a[:m],a[m:],b[:m],b[m:]
    low=product(a0,b0)
    high=plus(product(a0,b1),product(a1,b0))
    if any(a1) and any(b1):
        rad=RADICANDS[len(a).bit_length()-2]
        low=plus(low,product(product(a1,b1),rad))
    return low+high


@lru_cache(maxsize=None)
def sign(a):
    if len(a)==1:return (a[0]>0)-(a[0]<0)
    m=len(a)//2;u,v=a[:m],a[m:];su,sv=sign(u),sign(v)
    if not sv:return su
    if not su:return sv
    if su==sv:return su
    rad=RADICANDS[len(a).bit_length()-2]
    norm=minus(product(u,u),product(product(v,v),rad))
    return su*sign(norm)


def reciprocal(a):
    if len(a)==1:
        if not a[0]:raise ZeroDivisionError
        return (1/a[0],)
    m=len(a)//2;u,v=a[:m],a[m:]
    rad=RADICANDS[len(a).bit_length()-2]
    norm=minus(product(u,u),product(product(v,v),rad))
    # This implementation deliberately refuses a reducible norm-zero inversion.
    # None of the explicitly checked construction denominators has that form.
    if sign(norm)==0:raise ZeroDivisionError('Zero norm denominator')
    inv=reciprocal(norm)
    return product(u,inv)+tuple(-x for x in product(v,inv))


@total_ordering
class Number:
    def __init__(self, coefficients=0):
        self.c=coefficients.c if isinstance(coefficients,Number) else tuple(F(x)for x in coefficients)if isinstance(coefficients,(tuple,list))else(F(coefficients),)
        if not self.c or len(self.c)&(len(self.c)-1):raise ValueError('Bad tower dimension')
    def aligned(self,other):
        other=Number(other);n=max(len(self.c),len(other.c))
        return self.c+(F(0),)*(n-len(self.c)),other.c+(F(0),)*(n-len(other.c))
    def __add__(self,other):return Number(plus(*self.aligned(other)))
    __radd__=__add__
    def __neg__(self):return Number(tuple(-x for x in self.c))
    def __sub__(self,other):return self+-Number(other)
    def __rsub__(self,other):return Number(other)+-self
    def __mul__(self,other):return Number(product(*self.aligned(other)))
    __rmul__=__mul__
    def __truediv__(self,other):
        a,b=self.aligned(other);return Number(product(a,reciprocal(b)))
    def __rtruediv__(self,other):return Number(other)/self
    def __pow__(self,n):
        if type(n)is not int or n<0:raise ValueError('Nonnegative integer exponent required')
        r=Number(1)
        for _ in range(n):r=r*self
        return r
    def sign(self):return sign(self.c)
    def __eq__(self,other):return (self-other).sign()==0
    def __lt__(self,other):return (self-other).sign()<0
    def __le__(self,other):return (self-other).sign()<=0
    def serial(self):return [str(q)for q in self.c]
    def approximate(self):
        roots=[]
        def evaluate(c):
            if len(c)==1:return float(c[0])
            m=len(c)//2
            return evaluate(c[:m])+evaluate(c[m:])*roots[len(c).bit_length()-2]
        for rad in RADICANDS:roots.append(evaluate(rad)**.5)
        return evaluate(self.c)


def root(value):
    value=Number(value)
    n=1<<len(RADICANDS)
    if len(value.c)>n or value.sign()<=0:raise ValueError('Nonpositive or forward-referencing radical')
    RADICANDS.append(value.c+(F(0),)*(n-len(value.c)))
    return Number((F(0),)*n+(F(1),)+(F(0),)*(n-1))


def point_add(a,b):return a[0]+b[0],a[1]+b[1]
def point_sub(a,b):return a[0]-b[0],a[1]-b[1]
def rotate(a):return (-a[0]-3*a[1])/2,(a[0]-a[1])/2
def norm(a):return a[0]**2+3*a[1]**2
def distance(a,b):return norm(point_sub(a,b))
def orientation(a,b,c):
    u,v=point_sub(b,a),point_sub(c,a)
    return u[0]*v[1]-u[1]*v[0]


def construct():
    RADICANDS.clear();product.cache_clear();sign.cache_clear()
    r=root(721)
    ts=[Number(F(1,10)),(83-3*r)/200]
    for _ in range(2):
        t=ts[-1]
        d=(1-t)*(1-3*t)*(1+3*t*t)
        ts.append((1-2*t+3*t*t-root(d))/2)
    points=[]
    for j in range(5):
        if j==0:p=(Number(1),Number(0))
        else:
            t=ts[j-1];den=1+3*t*t
            p=(-Number(F(1,2))+3*t/den,(1-3*t*t)/(2*den))
            if (j-1)%2:p=(p[0],-p[1])
        for _ in range(3):points.append(p);p=rotate(p)
    return ts,points


def verify():
    ts,points=construct();n=len(points)
    recurrences=[]
    for t,s in zip(ts,ts[1:]):
        if not(0<s<t):raise ValueError('Wrong recurrence branch')
        residual=s*s-(1-2*t+3*t*t)*s+t*t
        if residual!=0:raise ValueError('Recurrence equation failed')
        recurrences.append(residual.serial())
    # This proposed order is input data. It is certified below by all n(n-2)
    # strict supporting-half-plane signs; no floating hull test is trusted.
    order=[4,10,2,12,6,5,11,0,13,7,3,9,1,14,8]
    signs=[]
    for k,a in enumerate(order):
        b=order[(k+1)%n]
        for c in range(n):
            if c in(a,b):continue
            s=orientation(points[a],points[b],points[c]).sign();signs.append(s)
            if s!=1:raise ValueError(f'Non-supporting claimed edge {a,b,c}: {s}')
    classes=[]
    internal=[]
    chosen=[]
    for i,p in enumerate(points):
        buckets=[]
        for j,q in enumerate(points):
            if i==j:continue
            r=distance(p,q)
            if r.sign()<=0:raise ValueError('Collided vertices')
            for value,labels in buckets:
                if r==value:labels.append(j);break
            else:buckets.append((r,[j]))
        row=[sorted(labels)for _,labels in buckets]
        row.sort(key=lambda labels:(-len(labels),labels))
        classes.append(row)
        rich=[w for w in row if len(w)>=4]
        if i>=9:
            if not rich:raise ValueError('Good cap vertex')
            if all(sum(j<9 for j in w)<=1 for w in rich):internal.append(i)
        if i>=6:
            orbit,k=divmod(i,3)
            w=[k,3*(orbit-1)+k,3*orbit+(k+1)%3,3*orbit+(k+2)%3]
            if sorted(w) not in row:raise ValueError('Named recurrence witnesses not complete class')
            chosen.append({'center':i,'witnesses':w,'old_support':sum(j<9 for j in w)})
    maximum=[max(map(len,row))for row in classes]
    if maximum!=[2]*3+[3]*3+[4]*9 or internal!=[12,13,14]:raise ValueError('Wrong sharpness census')
    return {'status':'passed','definition':'known recurrence, t0=1/10, through t3',
            'coordinate_convention':'(x,y) denotes Cartesian (x,sqrt(3)*y)',
            'radicands':[Number(v).serial()for v in RADICANDS],
            'parameters':[t.serial()for t in ts],
            'points':[[x.serial(),y.serial()]for x,y in points],
            'order':order,'strict_support_checks':len(signs),'pair_distinctness_checks':n*(n-1)//2,
            'all_distance_classes':classes,'maximum_multiplicities':maximum,
            'internally_supported_new_vertices':internal,'named_rich_rows':chosen,
            'old_good_vertices':[i for i in range(9)if maximum[i]<4],
            'all_rich':False,'new_construction_claimed':False,
            'recurrence_residuals':recurrences,'arithmetic':'exact recursive quadratic radical tower'}


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');ap.add_argument('--check',action='store_true');ap.add_argument('--discover-order',action='store_true');a=ap.parse_args()
    if a.discover_order:
        import math
        _,p=construct();print(sorted(range(len(p)),key=lambda i:math.atan2(p[i][1].approximate()*3**.5,p[i][0].approximate())));raise SystemExit
    result=verify();text=json.dumps(result,indent=2,sort_keys=True)+'\n';path=Path(__file__).resolve().parent/'data/sharpness.json'
    if a.write:path.write_text(text)
    if a.check and path.read_text()!=text:raise ValueError('Sharpness report differs')
    print(text)
