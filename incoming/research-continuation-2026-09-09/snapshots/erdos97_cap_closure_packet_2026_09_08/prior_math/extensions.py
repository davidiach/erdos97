"""Real expressions a+b*sqrt(S), with a,b,S in quadratic.Q.
Only addition, multiplication, equality and sign are needed by certificates.
No irreducibility of S is assumed.
"""
from quadratic import Q
from functools import total_ordering

@total_ordering
class E:
    __slots__=('a','b','S')
    def __init__(self,a,b=0,S=0):
        self.a,self.b,self.S=Q(a),Q(b),Q(S)
        if self.S<0:raise ValueError('negative radicand')
        if self.S==0:self.b=Q(0)
    def coerce(self,o):
        if isinstance(o,E):
            if self.S!=o.S:raise ValueError('incompatible radical extensions')
            return o
        return E(o,0,self.S)
    def __add__(self,o):
        o=self.coerce(o);return E(self.a+o.a,self.b+o.b,self.S)
    __radd__=__add__
    def __neg__(self):return E(-self.a,-self.b,self.S)
    def __sub__(self,o):return self+-self.coerce(o)
    def __rsub__(self,o):return self.coerce(o)+-self
    def __mul__(self,o):
        o=self.coerce(o);return E(self.a*o.a+self.S*self.b*o.b,self.a*o.b+self.b*o.a,self.S)
    __rmul__=__mul__
    def __pow__(self,n):
        if not isinstance(n,int) or n<0:raise ValueError('nonnegative integer exponent needed')
        z=E(1,0,self.S)
        for _ in range(n):z=z*self
        return z
    def sign(self):
        a,b=self.a.sign(),self.b.sign()
        if not b:return a
        if not a:return b
        if a==b:return a
        return a*(self.a*self.a-self.b*self.b*self.S).sign()
    def __eq__(self,o):
        try:return (self-self.coerce(o)).sign()==0
        except (TypeError,ValueError):return NotImplemented
    def __lt__(self,o):return (self-self.coerce(o)).sign()<0
    def __bool__(self):return self.sign()!=0
    def json(self):return [self.a.json(),self.b.json()]
    def __repr__(self):return f'E({self.a!r},{self.b!r},{self.S!r})'
