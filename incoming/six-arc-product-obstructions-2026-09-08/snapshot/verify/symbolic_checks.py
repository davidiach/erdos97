"""Independent exact algebra checks for the two written restricted proofs.

This module imports no search code. All identities are checked in rational
polynomial arithmetic, allowing sqrt(3) in intermediate coordinate formulas.
The accompanying paper proofs, not numerical testing, supply universal signs.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]

def run() -> dict:
    checks: list[str] = []
    def zero(name: str, expression) -> None:
        value = sp.factor(sp.cancel(sp.expand_complex(expression)))
        if value != 0:
            raise AssertionError(f"{name}: nonzero remainder {value}")
        checks.append(name)

    s, t = sp.symbols('s t', real=True)
    rt = sp.sqrt(3)
    w = (-1+sp.I*rt)/2
    Ds, Dt = 1+3*s*s, 1+3*t*t
    def z(u):
        return -sp.Rational(1,2)+3*u/(1+3*u*u)+sp.I*rt*(1-3*u*u)/(2*(1+3*u*u))
    def norm2(a):
        return sp.expand(a*sp.conjugate(a))
    nums = [
        9*(s-t)**2,
        3*(9*s*s*t*t-9*s*t*t+3*s*t+3*t*t-3*t+1),
        3*(9*s*s*t*t-9*s*s*t+3*s*s+3*s*t-3*s+1),
        3*(3*s*t-1)**2,
        3*(3*s*s+3*s*t-3*s+3*t*t-3*t+1),
        9*(3*s*s*t*t-3*s*s*t+s*s-3*s*t*t+s*t+t*t),
    ]
    derivs = [
        -18*(s-t)*(3*s*t+1),
        9*(s-1)*(6*s*t-3*t*t+1),
        9*(3*s-1)*(3*s*t*t-s+2*t),
        18*(s+t)*(3*s*t-1),
        -9*(s-1)*(6*s*t+3*t*t-1),
        9*(3*s-1)*(3*s*t*t-s-2*t),
    ]
    fs = [n/(Ds*Dt) for n in nums]
    labels = ['+0','+1','+2','-0','-1','-2']
    targets = [w**k*z(t) for k in range(3)] + [w**k*sp.conjugate(z(t)) for k in range(3)]
    for name, f, n, der, target in zip(labels, fs, nums, derivs, targets):
        zero('carrier distance '+name, norm2(z(s)-target)-f)
        zero('carrier derivative '+name, sp.diff(f,t)*Ds*Dt**2-der)
    L=9*s*s/Ds; R=3*(3*s*s-3*s+1)/Ds; H=3/Ds
    S=27*s*s*(1-s)**2/Ds**2
    T=3*(1-3*s*s)**2/Ds**2; U=3*(1-3*s)**2/Ds**2
    ends=[(L,0),(H,R),(R,R),(H,T),(R,U),(L,S)]
    for name,f,(left,right) in zip(labels,fs,ends):
        zero('left endpoint '+name, f.subs(t,0)-left)
        zero('right endpoint '+name, f.subs(t,s)-right)
    for name, left, right in [
        ('S-L',S-L,-18*s*s*(3*s-1)/Ds**2),
        ('R-S',R-S,3*(3*s-1)*(3*s*s-1)/Ds**2),
        ('T-R',T-R,9*s*(s-1)*(3*s-1)/Ds**2),
        ('H-T',H-T,-27*s*s*(s-1)*(s+1)/Ds**2),
    ]: zero('range factor '+name,left-right)
    Q=(3*s**3+s)*t+s*s-s-(3*s+1)*t*t
    zero('uniform T-F+2 gap', Ds**2*Dt*(T-fs[2])-9*(3*s-1)*Q)
    # The following equality isolates two nonnegative terms on 0<=t<=s.
    bound=s*(3*s**3+2*s-1)
    zero('Q upper-bound decomposition', bound-Q-((3*s**3+s)*(s-t)+(3*s+1)*t*t))
    zero('shared point at L', targets[0].subs(t,0)-targets[5].subs(t,0))
    zero('shared point at R', targets[2].subs(t,0)-targets[4].subs(t,0))
    zero('shared point at H', targets[1].subs(t,0)-targets[3].subs(t,0))

    # Diamond algebra without assuming coordinates from any search output.
    ax,ay,bx,by=sp.symbols('ax ay bx by',real=True)
    a=ax+sp.I*ay; b=bx+sp.I*by
    ca=norm2(a-1)-3; cb=norm2(b-1)-3
    zero('product completion from a', norm2(a*b-a)-3*norm2(a)-norm2(a)*cb)
    zero('product completion from b', norm2(a*b-b)-3*norm2(b)-norm2(b)*ca)
    zero('minus-two completion from a', norm2(a+2)-3*norm2(a)+2*ca)
    zero('minus-two completion from b', norm2(b+2)-3*norm2(b)+2*cb)
    zero('minus-two midpoint obstruction',(w*(-2)+w*w*(-2))/2-1)
    # Circles after rotation and inversion.
    x,y=sp.symbols('x y',real=True); B=x+sp.I*y
    circle=norm2(B-w)-3
    zero('inverse-circle equation',norm2(B)* (norm2(1/B+w*w/2)-sp.Rational(3,4)) + circle/2)
    for name,center,radius,normal in [
        ('A tangent',w*w,rt,1+sp.I/rt),
        ('B tangent',w,rt,1-sp.I/rt),
        ('inverse B tangent',-w*w/2,rt/2,1-sp.I/rt),
    ]:
        maximum=sp.re(center*sp.conjugate(normal))+radius*sp.sqrt(norm2(normal))
        zero(name+' maximum',maximum-1)
        point=center+radius*normal/sp.sqrt(norm2(normal))
        zero(name+' unique equality point',point-1)

    alpha,beta,rho,sigma=sp.symbols('alpha beta rho sigma',real=True)
    X=rho*(sp.cos(alpha)+sp.I*sp.sin(alpha))
    Y=sigma*(sp.cos(beta)-sp.I*sp.sin(beta))
    xx=rho*sigma*sp.sin(beta)/sp.sin(alpha)
    yy=sigma*sp.sin(alpha-beta)/sp.sin(alpha)
    residual=sp.trigsimp(sp.expand_complex(X*Y-xx-yy*X),method='fu')
    zero('barycentric representation',residual)
    residual=sp.trigsimp(xx+yy-sigma*(sp.cos(beta)+(rho-sp.cos(alpha))*sp.sin(beta)/sp.sin(alpha)),method='fu')
    zero('barycentric coefficient sum',residual)
    # A rationalized form of the tangent half-angle identity.
    zero('half-angle coefficient identity', sp.trigsimp((1-sp.cos(alpha))/sp.sin(alpha)-sp.sin(alpha)/(1+sp.cos(alpha))))
    zero('growth arc right of x=1',sp.trigsimp(
        1/sp.cos(alpha)**2+(sp.cos(alpha)-rt*sp.sin(alpha))/sp.cos(alpha)-2
        -sp.tan(alpha)*(sp.tan(alpha)-rt)))
    report={
        'classification':'exact symbolic identity checks; written proofs supply sign and geometric arguments',
        'independent_of_search_implementation':True,
        'checks_passed':len(checks),'checks':checks,
        'sympy_version':sp.__version__,
        'unrestricted_solution':False,
    }
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
    report=run(); path=ROOT/'reports/symbolic_checks.json'
    if args.check:
        old=json.loads(path.read_text())
        for k in ['classification','independent_of_search_implementation','checks_passed','checks','unrestricted_solution']:
            if old[k]!=report[k]:raise AssertionError(f'Report mismatch: {k}')
    else:path.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'checks_passed':report['checks_passed'],'status':'PASS'},indent=2))
