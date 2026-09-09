"""Separate exact control check: dyadic enclosures plus polynomial identities.

No code from sharpness.py is imported. Equalities follow from rational
polynomial identities and the specified square-root branches. Intervals are
used only for strict inequalities, distinctness, and all-radius upper bounds.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as F
from math import isqrt
from pathlib import Path
import json

BITS=512
UNIT=1<<BITS


def ceil_div(a,b):return -((-a)//b)


class Interval:
    def __init__(self,lo,hi):
        if type(lo)is not int or type(hi)is not int or lo>hi:raise ValueError('Invalid interval')
        self.lo,self.hi=lo,hi
    @classmethod
    def number(cls,x):
        if isinstance(x,Interval):return x
        if isinstance(x,float):raise ValueError('Floating constants are not exact input')
        q=F(x);return cls(q.numerator*UNIT//q.denominator,ceil_div(q.numerator*UNIT,q.denominator))
    def __add__(self,x):
        x=self.number(x);return Interval(self.lo+x.lo,self.hi+x.hi)
    __radd__=__add__
    def __neg__(self):return Interval(-self.hi,-self.lo)
    def __sub__(self,x):return self+-self.number(x)
    def __rsub__(self,x):return self.number(x)+-self
    def __mul__(self,x):
        x=self.number(x);v=[a*b for a in(self.lo,self.hi)for b in(x.lo,x.hi)]
        return Interval(min(v)//UNIT,ceil_div(max(v),UNIT))
    __rmul__=__mul__
    def __truediv__(self,x):
        x=self.number(x)
        if x.lo<=0<=x.hi:raise ZeroDivisionError('Divisor interval contains zero')
        return self*Interval(UNIT*UNIT//x.hi,ceil_div(UNIT*UNIT,x.lo))
    def __rtruediv__(self,x):return self.number(x)/self
    def square(self):
        vals=(self.lo*self.lo,self.hi*self.hi)
        return Interval(0 if self.lo<=0<=self.hi else min(vals)//UNIT,ceil_div(max(vals),UNIT))
    def sqrt(self):
        if self.lo<0:raise ValueError('Negative square-root interval')
        lo=isqrt(self.lo*UNIT);u=self.hi*UNIT;hi=isqrt(u)
        return Interval(lo,hi+(hi*hi<u))
    def serial(self):return [str(self.lo),str(self.hi)]


# An independent two-variable rational polynomial implementation.
class Polynomial:
    def __init__(self,terms=0):
        self.t={k:F(v)for k,v in terms.items()if v}if isinstance(terms,dict)else({(0,0):F(terms)}if terms else{})
    def __add__(self,x):
        x=x if isinstance(x,Polynomial)else Polynomial(x);r=dict(self.t)
        for k,v in x.t.items():r[k]=r.get(k,F(0))+v
        return Polynomial(r)
    __radd__=__add__
    def __neg__(self):return Polynomial({k:-v for k,v in self.t.items()})
    def __sub__(self,x):return self+-(x if isinstance(x,Polynomial)else Polynomial(x))
    def __rsub__(self,x):return Polynomial(x)+-self
    def __mul__(self,x):
        x=x if isinstance(x,Polynomial)else Polynomial(x);r={}
        for (i,j),v in self.t.items():
            for (k,l),w in x.t.items():r[i+k,j+l]=r.get((i+k,j+l),F(0))+v*w
        return Polynomial(r)
    __rmul__=__mul__
    def __pow__(self,n):
        r=Polynomial(1)
        for _ in range(n):r=r*self
        return r


def identities():
    s,t=Polynomial({(1,0):1}),Polynomial({(0,1):1})
    D=lambda u:1+3*u*u
    N=lambda u:-1+6*u-3*u*u
    M=lambda u:1-3*u*u
    B=lambda u:1-2*u+3*u*u
    f=s*s-B(t)*s+t*t
    checks={
        'norm':N(t)**2+3*M(t)**2-4*D(t)**2+12*t*D(t),
        'anchor':(N(t)-2*D(t))**2+3*M(t)**2-3*(N(t)**2+3*M(t)**2),
        'preceding_orbit':(N(s)*D(t)-N(t)*D(s))**2+3*(M(s)*D(t)+M(t)*D(s))**2-3*(N(s)**2+3*M(s)**2)*D(t)**2+36*f*D(s)*D(t),
        'discriminant':B(t)**2-(1-t)*(1-3*t)*D(t)-4*t*t,
        'rotation_norm':(-s-3*t)**2+3*(s-t)**2-4*(s*s+3*t*t),
        'orbit_mates':(-3*s-3*t)**2+3*(s-3*t)**2-12*(s*s+3*t*t),
    }
    if any(value.t for value in checks.values()):raise ValueError('Polynomial identity failed')
    return list(checks)


def add(p,q):return p[0]+q[0],p[1]+q[1]
def sub(p,q):return p[0]-q[0],p[1]-q[1]
def rotate(p):return(-p[0]-3*p[1])/2,(p[0]-p[1])/2
def distance(p,q):
    a,b=sub(p,q);return a.square()+3*b.square()
def orient(p,q,r):
    a,b=sub(q,p),sub(r,p);return a[0]*b[1]-a[1]*b[0]


def verify():
    checked=identities()
    t=[Interval.number(F(1,10))]
    for _ in range(3):
        u=t[-1];disc=(1-u)*(1-3*u)*(1+3*u.square())
        v=(1-2*u+3*u.square()-disc.sqrt())/2
        if v.lo<=0 or v.hi>=u.lo:raise ValueError('Root branch not strictly decreasing and positive')
        t.append(v)
    points=[]
    for orbit in range(5):
        if orbit==0:p=Interval.number(1),Interval.number(0)
        else:
            u=t[orbit-1];d=1+3*u.square()
            p=-Interval.number(F(1,2))+3*u/d,(1-3*u.square())/(2*d)
            if orbit%2==0:p=p[0],-p[1]
        for _ in range(3):points.append(p);p=rotate(p)
    order=[4,10,2,12,6,5,11,0,13,7,3,9,1,14,8]
    minimum=None;sign_count=0
    for k,i in enumerate(order):
        j=order[(k+1)%15]
        for z in range(15):
            if z in(i,j):continue
            value=orient(points[i],points[j],points[z])
            if value.lo<=0:raise ValueError('Supporting sign not certified')
            sign_count+=1;minimum=value.lo if minimum is None else min(minimum,value.lo)
    maxima=[];rows=[];internals=[]
    for i,p in enumerate(points):
        intervals=[(distance(p,q),j)for j,q in enumerate(points)if i!=j]
        if any(d.lo<=0 for d,j in intervals):raise ValueError('Distinctness not certified')
        groups=[]
        for d,j in sorted(intervals,key=lambda pair:pair[0].lo):
            if not groups or d.lo>groups[-1][1]:groups.append([d.lo,d.hi,[j]])
            else:
                groups[-1][1]=max(groups[-1][1],d.hi);groups[-1][2].append(j)
        uppers=sorted([sorted(g[2])for g in groups],key=lambda g:(-len(g),g))
        orbit,k=divmod(i,3)
        witnesses=[3*orbit+(k+1)%3,3*orbit+(k+2)%3]
        if orbit>=1:witnesses.append(k)
        if orbit>=2:witnesses.append(3*(orbit-1)+k)
        if len(witnesses)!=len(uppers[0]) or sorted(witnesses)not in uppers:
            raise ValueError('Exact lower bound and interval upper bound do not meet')
        maxima.append(len(witnesses));rows.append(uppers)
        if i>=9:
            possible_rich=[g for g in uppers if len(g)>=4]
            if all(sum(j<9 for j in g)<=1 for g in possible_rich):internals.append(i)
    if maxima!=[2]*3+[3]*3+[4]*9 or internals!=[12,13,14]:raise ValueError('Unexpected census')
    return dict(status='passed',bits=BITS,universal_polynomial_identities=checked,
                strict_support_checks=sign_count,minimum_support_numerator=str(minimum),
                support_denominator=str(UNIT),parameters=[u.serial()for u in t],
                maximum_multiplicities=maxima,internally_supported_new_vertices=internals,
                all_radius_interval_groups=rows,all_rich=False,
                primary_control_code_imported=False,
                equality_method='six exact rational polynomial identities and specified positive square-root branches',
                inequality_method='outward-rounded dyadic integer intervals')


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');ap.add_argument('--check',action='store_true');a=ap.parse_args()
    result=verify();text=json.dumps(result,sort_keys=True,indent=2)+'\n';path=Path(__file__).resolve().parent/'data/sharpness_oracle.json'
    if a.write:path.write_text(text)
    if a.check and path.read_text()!=text:raise ValueError('Independent control report differs')
    print(text)
