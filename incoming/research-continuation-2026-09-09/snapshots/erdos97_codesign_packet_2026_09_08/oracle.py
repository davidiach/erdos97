"""Separate certificate checker: flattened polynomials + rational enclosures.
Does not import quadratic.py, extensions.py, verify.py, or the generator.
"""
from fractions import Fraction as F
from math import isqrt
from itertools import combinations
from functools import lru_cache
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent
MAX_BITS_USED=0
D=F(721)

def rational_sqrt(x):
    if x<0:return None
    a,b=isqrt(x.numerator),isqrt(x.denominator)
    return F(a,b) if a*a==x.numerator and b*b==x.denominator else None

@lru_cache(None)
def enclosure(x,bits):
    assert x>=0
    k=isqrt((x.numerator << (2*bits))//x.denominator)
    lo=F(k,1<<bits)
    return lo,lo if lo*lo==x else F(k+1,1<<bits)

def ring(S=F(0)):
    S=F(S);assert S>=0
    aroot=rational_sqrt(S);broot=rational_sqrt(S/D)
    class R:
        __slots__=('c',)
        def __init__(self,a=0,b=0,c=0,d=0):
            if isinstance(a,R):self.c=a.c;return
            if any(isinstance(v,float) for v in [a,b,c,d]):raise TypeError('float')
            a,b,c,d=map(F,[a,b,c,d])
            if aroot is not None:a,b,c,d=a+aroot*c,b+aroot*d,F(0),F(0)
            elif broot is not None:a,b,c,d=a+D*broot*d,b+broot*c,F(0),F(0)
            self.c=(a,b,c,d)
        def __add__(self,o):return R(*(a+b for a,b in zip(self.c,R(o).c)))
        __radd__=__add__
        def __neg__(self):return R(*(-a for a in self.c))
        def __sub__(self,o):return self+-R(o)
        def __rsub__(self,o):return R(o)+-self
        def __mul__(self,o):
            o=R(o);out=[F(0)]*4
            for i,a in enumerate(self.c):
                for j,b in enumerate(o.c):
                    out[i^j]+=a*b*(D if i&j&1 else 1)*(S if i&j&2 else 1)
            return R(*out)
        __rmul__=__mul__
        def __truediv__(self,o):
            a,b,c,d=R(o).c;assert c==d==0
            den=a*a-D*b*b;assert den
            return self*R(a/den,-b/den)
        def __rtruediv__(self,o):return R(o)/self
        def __eq__(self,o):return self.c==R(o).c
        def __hash__(self):return hash(self.c)
        def sign(self):
            global MAX_BITS_USED
            if not any(self.c):return 0
            for bits in [32,64,128,256,512,1024,2048]:
                X=enclosure(D,bits);Y=enclosure(S,bits)
                bases=[(F(1),F(1)),X,Y,(X[0]*Y[0],X[1]*Y[1])]
                lo=hi=F(0)
                for a,(l,h) in zip(self.c,bases):
                    lo+=a*(l if a>=0 else h);hi+=a*(h if a>=0 else l)
                if lo>0 or hi<0:
                    MAX_BITS_USED=max(MAX_BITS_USED,bits)
                    return 1 if lo>0 else -1
            raise AssertionError('rational enclosures did not isolate sign')
        @classmethod
        def q(cls,data):
            assert len(data)==2 and all(isinstance(s,str) for s in data)
            return cls(F(data[0]),F(data[1]))
        @classmethod
        def e(cls,data):
            assert len(data)==2
            return cls(F(data[0][0]),F(data[0][1]),F(data[1][0]),F(data[1][1]))
    return R

def plus(a,b):return a[0]+b[0],a[1]+b[1]
def minus(a,b):return a[0]-b[0],a[1]-b[1]
def times(a,s):return a[0]*s,a[1]*s
def cross(a,b):return a[0]*b[1]-a[1]*b[0]
def orient(a,b,c):return cross(minus(b,a),minus(c,a))
def square(a):return a[0]*a[0]+3*a[1]*a[1]
def distance(a,b):return square(minus(a,b))
def rotate(a):return (-a[0]-3*a[1])/2,(a[0]-a[1])/2

def base(R):
    def z(t):
        den=1+3*t*t
        return -R(F(1,2))+3*t/den,(1-3*t*t)/(2*den)
    a=z(R(F(1,10)));b=z(R(F(83,200),F(-3,200)))
    P=[]
    for c in [(R(1),R(0)),a,(b[0],-b[1])]:P.extend([c,rotate(c),rotate(rotate(c))])
    return P

def strict(P,order):
    assert sorted(order)==list(range(len(P))) and len(set(P))==len(P)
    count=0
    for k,i in enumerate(order):
        j=order[(k+1)%len(order)]
        for h in range(len(P)):
            if h not in (i,j):assert orient(P[i],P[j],P[h]).sign()>0;count+=1
    return count

def obstruction(P,c,en):
    assert ('coincides_with'in en)^('obstruction'in en)
    if 'coincides_with'in en:assert c==P[en['coincides_with']];return
    assert c not in P;P=P+[c];ob=en['obstruction'];v=ob['target'];a,b,d=ob['triangle']
    assert len({v,a,b,d})==4 and orient(P[a],P[b],P[d]).sign()>0
    signs=[orient(P[a],P[b],P[v]).sign(),orient(P[b],P[d],P[v]).sign(),orient(P[d],P[a],P[v]).sign()]
    assert signs==ob['signs'] and min(signs)>=0

def maxes(P):
    out=[]
    for i,p in enumerate(P):
        cnt={}
        for j,q in enumerate(P):
            if i!=j:
                d=distance(p,q);assert d.sign()>0;cnt[d]=cnt.get(d,0)+1
        out.append(max(cnt.values()))
    return out

def run():
    R=ring();P=base(R)
    report=json.loads((ROOT/'data/verification.json').read_text())
    cert=json.loads((ROOT/'data/base9_circumcenters.json').read_text())
    assert P==[tuple(R.q(z) for z in p) for p in cert['points']]
    assert [tuple(x['triple']) for x in cert['triples']]==list(combinations(range(9),3))
    C=[tuple(R.q(z) for z in c['point']) for c in cert['centers']]
    for en in cert['triples']:
        a,b,c=en['triple'];q=C[en['center']]
        assert orient(P[a],P[b],P[c]).sign()!=0
        assert distance(q,P[a])==distance(q,P[b])==distance(q,P[c])
    for c,en in zip(C,cert['centers']):obstruction(P,c,en)
    pc=json.loads((ROOT/'data/prescribed_circle_pairs.json').read_text())
    assert [tuple(en['sources']) for en in pc['pairs']]==list(combinations(range(6),2))
    for en in pc['pairs']:
        assert F(en['radicand'][1])==0
        S=F(en['radicand'][0]);R1=ring(S);PP=base(R1)
        radii=[R1(3)]*3+[3*square(PP[i]) for i in range(3,6)]
        i,j=en['sources'];v=minus(PP[j],PP[i]);d=square(v);t=(radii[i]-radii[j]+d)/(2*d)
        assert (radii[i]/d-t*t)/3==S
        assert [r['branch'] for r in en['roots']]==([-1,1] if S>0 else [0])
        foot=plus(PP[i],times(v,t));perp=(-3*v[1],v[0])
        for root in en['roots']:
            c=tuple(R1.e(z) for z in root['point']);sroot=R1(0,0,root['branch'])
            assert c==plus(foot,times(perp,sroot))
            assert distance(c,PP[i])==radii[i] and distance(c,PP[j])==radii[j]
            obstruction(PP,c,root)
    signs=0
    signs+=strict(P,[4,2,6,5,0,7,3,1,8])
    for name in ['repair','middle_cycle']:
        P1=[tuple(R.q(z) for z in p) for p in report[name]['points']]
        signs+=strict(P1,report[name]['hull_order'])
        assert maxes(P1)==report[name]['maximum_multiplicities']
        if name=='repair':
            assert P1[:9]==P
            for k in range(9):
                rad=3*square(P1[k]);assert sum(distance(P1[k],P1[j])==rad for j in range(18) if j!=k)==4
            for c in P1[9:]:
                assert all((distance(c,P1[k])-3*square(c)).sign()!=0 for k in range(3))
        else:
            assert all(sum(distance(p,q).sign()>0 and (distance(p,q)-1).sign()<0 for q in P1)==2 for p in P1)
            for en in report[name]['middle_rows']:
                i=en['source'];order=report[name]['hull_order'];k=order.index(i);fan=order[k+1:]+order[:k]
                row=[j for j in fan if distance(P1[i],P1[j])==1]
                assert row==en['angular_witness_order'] and row[1:3]==en['middle_witnesses']
    out={'status':'passed','arithmetic':'independent flattened polynomial arithmetic and rational square-root enclosures','largest_enclosure_precision_bits':MAX_BITS_USED,'supporting_signs':signs,'circumcenter_triples':84,'circle_pairs':15,'circle_intersection_branches':30,'external_mathematical_review':False}
    return out

if __name__=='__main__':
    payload=json.dumps(run(),indent=2,sort_keys=True)+'\n'
    path=ROOT/'data/oracle_report.json'
    import sys
    if '--write'in sys.argv:path.write_text(payload)
    else:assert path.read_text()==payload
    print(payload)
