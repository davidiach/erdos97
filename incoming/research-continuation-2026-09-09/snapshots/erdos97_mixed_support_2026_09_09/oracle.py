"""Separate SymPy reconstruction: universal identities, Sturm counts, Bernstein signs.
No import of the primary polynomial, interval, or geometry implementation.
"""
from pathlib import Path
from itertools import combinations
import json,argparse
import sympy as S
ROOT=Path(__file__).resolve().parent
x,c,s,H,b=S.symbols('x c s H b',real=True)
def must(ok,msg):
    if not ok:raise ValueError(msg)
def zero(expr):must(S.cancel(expr)==0,'symbolic identity failed: '+str(expr))
def identity_checks():
    A=(x-c)**2+(x*x-c*c)**2
    B=(x-c)**2+(H-x*x-c*c)**2
    C=2*x**3+(1-2*H+2*c*c)*x-c
    g=2*s**3+(1-2*H+2*c*c)*s+c
    hc=c*c+s*s+S.Rational(1,2)+c/(2*s)
    K=2*s*(s-c)-1
    expressions=[S.diff(A,x)-2*(x-c)*(1+2*x*(x+c)),
       S.diff(B,x)-2*C,
       S.diff(C,x,2)-12*x,
       S.diff(B.subs(x,-s),s)-2*g,
       s*S.diff(g,s)-g-(4*s**3-c),
       g-(2*(s+1)*(s-S.Rational(1,2))**2+2*(c*c-S.Rational(1,4))*s+(c-S.Rational(1,2))+(3-2*H)*s),
       C.subs(x,c)-2*c*(2*c*c-H),
       C.subs({x:b,H:2*b*b})-(b-c)*(1-2*b*b-2*b*c),
       g.subs(s,c)-2*c*(1-H+2*c*c),
       S.diff(g,s).subs(s,c)-(4*c*c-1)-2*(1+2*c*c-H),
       hc-2*s*s+(c+s)*K/(2*s),
       hc*(s-c)-s-(c*c+s*s)*K/(2*s),
       ((s+c)**2+(H-c*c-s*s)**2-(H-2*c*c)**2).subs(H,hc)-(s+c)**2*(c/s-(s-c)**2),
       (A-B).subs(x,b).subs(H,2*b*b),
       B.subs(x,-c)-(4*c*c+(H-2*c*c)**2)]
    for e in expressions:zero(e)
    return len(expressions)

def roots(p,a,b):
    p=S.Poly(p,x).sqf_part()
    if p.degree()==0:return 0
    if a==b:return int(p.eval(a)==0)
    return int(p.count_roots(a,b))
def grid(d):
    hh,bb,cc,rr=map(S.Rational,[d[k]for k in ['H','b','c','squared_radius']])
    A=(x-cc)**2+(x*x-cc*cc)**2-rr
    B=(x-cc)**2+(hh-x*x-cc*cc)**2-rr
    intervals=[(-cc,cc)]if d['selector']=='maximum'else[(-bb,-cc),(cc,bb)]
    zs=[]
    for p in [A,B]:
        n=sum(roots(p,a,b)for a,b in intervals)
        if d['selector']=='minimum'and cc==0 and p.subs(x,0)==0:n-=1
        zs.append(n)
    overlap=0
    if 2*bb*bb==hh:
        overlap=sum(1 for t in [-bb,bb]if any(a<=t<=b for a,b in intervals)and A.subs(x,t)==0)
    must(zs==[d['lower_roots'],d['upper_roots']],'root-count oracle mismatch')
    must(overlap==d['common_endpoint_duplicates'],'junction oracle mismatch')
    must(sum(zs)-overlap==d['distinct_witness_count'],'distinct count mismatch')

def bernstein_bounds(expr,a,b):
    # Convex hull of Bernstein coefficients after exact affine substitution.
    u=S.symbols('u');p=S.Poly(S.expand(expr.subs(x,a+(b-a)*u)),u);n=p.degree()
    if p.is_zero:return S.Rational(0),S.Rational(0)
    coeff=[p.nth(j)for j in range(n+1)]
    beta=[sum(coeff[j]*S.binomial(k,j)/S.binomial(n,j)for j in range(k+1))for k in range(n+1)]
    return min(beta),max(beta)

def control(inp,expected):
    ts=list(map(S.Rational,inp['upper_parameters']));ts.append(-sum(ts))
    cc=sum(a*b*t for a,b,t in combinations(ts,3))/2
    hh=cc*cc+(1-sum(a*b for a,b in combinations(ts,2)))/2
    pts=[S.Matrix([cc,cc*cc])]+[S.Matrix([t,hh-t*t])for t in ts[:3]]+[S.Matrix([x,x*x])]
    distance=lambda p,q:S.expand((p-q).dot(p-q))
    rr=distance(pts[0],pts[1]);f=S.Poly(distance(pts[0],pts[-1])-rr,x)
    lo,hi=map(S.Rational,inp['lower_root_interval'])
    must(roots(f.as_expr(),lo,hi)==1,'control root isolation failed')
    # Separately obtain a much tighter exact isolation from SymPy.
    intervals=f.intervals(eps=S.Rational(1,10**35))
    overlaps=[(a,b)for ((a,b),mult)in intervals if a>=lo and b<=hi]
    must(len(overlaps)==1,'independent isolator disagrees');a,b=overlaps[0]
    def equal(expr):
        e=S.Poly(expr,x)
        if e.is_zero:return True
        g=S.gcd(e,f)
        return roots(g.as_expr(),a,b)==1
    def positive(expr):
        low,up=bernstein_bounds(S.expand(expr),a,b)
        must(low>0,'Bernstein sign not positive')
    for j in range(1,5):must(equal(distance(pts[0],pts[j])-rr),'rich equality failed')
    order=inp['order'];supports=0
    for i,j in zip(order,order[1:]+order[:1]):
        for k in order:
            if k in (i,j):continue
            positive(S.det(S.Matrix.hstack(pts[j]-pts[i],pts[k]-pts[i])));supports+=1
    for p in pts:positive(hh-2*p[0]**2)
    direction=1 if inp['invalid_selector']=='minimum'else -1
    for p in pts[1:]:positive(direction*(p[0]**2-cc**2))
    maxima=[]
    for i,p in enumerate(pts):
        groups=[]
        for j,q in enumerate(pts):
            if i==j:continue
            dd=distance(p,q)
            for z,count in groups:
                if equal(dd-z):count.append(j);break
            else:groups.append((dd,[j]))
        maxima.append(max(len(v)for _,v in groups))
    must(maxima==expected['max_multiplicities'],'multiplicity oracle mismatch')
    must(str(cc)==expected['c']and str(hh)==expected['H']and str(rr)==expected['squared_radius'],'parameter oracle mismatch')
    return dict(name=inp['name'],support_signs=supports,max_multiplicities=maxima,
                exact_root_interval=[str(a),str(b)],method='SymPy exact isolation plus Bernstein coefficient signs')

def run():
    v=json.loads((ROOT/'data/verification.json').read_text())
    inputs=json.loads((ROOT/'data/controls.json').read_text())['controls']
    controls=[control(d,e)for d,e in zip(inputs,v['controls'])]
    n=identity_checks()
    for d in v['grid']:grid(d)
    return dict(schema='erdos97.mixed_lens_oracle.v1',status='passed',
                universal_symbolic_identities=n,exact_level_counts=len(v['grid']),controls=controls,
                separate_implementation_not_external_review=True)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');ap.add_argument('--check',action='store_true');a=ap.parse_args()
    d=run();s=json.dumps(d,indent=2,sort_keys=True)+'\n';p=ROOT/'data/oracle.json'
    if a.write:p.write_text(s)
    if a.check:must(p.read_text()==s,'oracle stored report differs')
    print(s)
if __name__=='__main__':main()
