import sympy as s,json
from itertools import combinations
from pathlib import Path
x=s.symbols('x')
def attempt(ts):
 ts=list(map(s.Rational,ts));ts.append(-sum(ts))
 e2=sum(a*b for a,b in combinations(ts,2));e3=sum(a*b*c for a,b,c in combinations(ts,3))
 c=e3/2;H=c*c+s.Rational(1,2)-e2/2
 if c<=0:return
 r=(ts[0]-c)**2+(H-ts[0]**2-c*c)**2
 f=s.Poly((x-c)**2+(x*x-c*c)**2-r,x)
 print('ts',ts,'c,H',c,H,float(c),float(H),'r2',r)
 print('curve tests',[(float(t),bool(2*t*t<H),float(abs(t)-c))for t in ts]);print('roots',s.polys.polytools.intervals(f,eps=s.Rational(1,10**6)))
 return
attempt(['-9/10','-3/4','-3/8'])
attempt(['-4/5','-3/4','2/5'])
attempt(['-3/4','-37/50','2/5'])
