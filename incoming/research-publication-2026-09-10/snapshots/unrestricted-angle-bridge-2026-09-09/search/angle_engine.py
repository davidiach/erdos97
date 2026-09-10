"""Necessary chord-angle relaxation; discovery only, never a geometry verifier."""
from __future__ import annotations
from fractions import Fraction
from itertools import combinations
import numpy as np
from scipy.optimize import linprog


def matrices(n: int, rows: dict[int, list[int]]):
    edges=list(combinations(range(n),2)); ix={e:i for i,e in enumerate(edges)}
    G=[]; h=[]; angle_keys=[]
    for i,j,k in combinations(range(n),3):
        # Angle at i, k, j respectively, in units of pi.
        for key, coeff, constant in [
            ((j,i,k), {(i,k):1,(i,j):-1},0),
            ((i,k,j), {(j,k):1,(i,k):-1},0),
            ((i,j,k), {(j,k):-1,(i,j):1},1),
        ]:
            v=np.zeros(len(edges),dtype=int)
            for e,c in coeff.items(): v[ix[e]]=c
            G.append(v);h.append(constant);angle_keys.append(key)
    E=[];e=[];eqkeys=[]
    for apex,ws in sorted(rows.items()):
        if apex in ws or len(ws)!=len(set(ws)) or any(x<0 or x>=n for x in ws):
            raise ValueError('invalid witness row')
        for a,b in combinations(sorted(ws),2):
            i,j,k=sorted((apex,a,b));v=np.zeros(len(edges),dtype=int)
            if apex==i: terms={(i,j):1,(i,k):1,(j,k):-2};rhs=-1
            elif apex==j: terms={(i,j):1,(j,k):1,(i,k):-2};rhs=0
            else: terms={(i,k):1,(j,k):1,(i,j):-2};rhs=1
            for edge,co in terms.items():v[ix[edge]]=co
            E.append(v);e.append(rhs);eqkeys.append((apex,a,b))
    gauge=np.zeros(len(edges),dtype=int);gauge[0]=1
    E.append(gauge);e.append(0);eqkeys.append(('gauge',0,1))
    return np.array(G),np.array(h),np.array(E),np.array(e),edges,angle_keys,eqkeys


def exact_certificate(G,h,E,e,u,v):
    u=[x if isinstance(x,Fraction) else Fraction(float(x)).limit_denominator(10**7) for x in u]
    v=[x if isinstance(x,Fraction) else Fraction(float(x)).limit_denominator(10**7) for x in v]
    if any(x<0 for x in u) or not any(x>0 for x in u):return None
    active_u=[(i,x) for i,x in enumerate(u) if x]
    active_v=[(i,x) for i,x in enumerate(v) if x]
    for j in range(G.shape[1]):
        if sum(x*int(G[i,j]) for i,x in active_u)+sum(x*int(E[i,j]) for i,x in active_v):return None
    const=sum(x*int(h[i]) for i,x in active_u)-sum(x*int(e[i]) for i,x in active_v)
    if const>0:return None
    return {'angle_weights':[[i,str(x)] for i,x in active_u],
            'equality_weights':[[i,str(x)] for i,x in active_v],
            'constant':str(const),'kind':'strict-positive-angle-contradiction'}


def reconstruct_dual(G,h,E,e,u,v):
    """Reconstruct a rational dual on its numerical support; then verify it.

    Floating point identifies candidate support only. Exact row reduction and
    the certificate checker decide whether a contradiction is established.
    """
    from flint import fmpq_mat
    for cutoff in (1e-8,1e-10,1e-12):
        iu=[i for i,x in enumerate(u) if abs(x)>cutoff]
        iv=[i for i,x in enumerate(v) if abs(x)>cutoff]
        cols=[G[i] for i in iu]+[E[i] for i in iv]
        if not cols: continue
        ncols=len(cols)
        data=[[int(c[j]) for c in cols]+[0] for j in range(G.shape[1])]
        data.append([1]*len(iu)+[0]*len(iv)+[1])
        reduced,rank=fmpq_mat(data).rref()
        solution=[Fraction(0)]*ncols
        ok=True
        for i in range(reduced.nrows()):
            first=next((j for j in range(ncols+1) if reduced[i,j]),None)
            if first is None:continue
            if first==ncols:ok=False;break
            solution[first]=Fraction(str(reduced[i,ncols]))
        if not ok:continue
        # Free variables are zero; the exact checker rejects any unsupported
        # sign or failed equation. No numerical UNSAT is promoted here.
        eu=[Fraction(0)]*len(G);ev=[Fraction(0)]*len(E)
        for i,x in zip(iu,solution[:len(iu)]):eu[i]=x
        for i,x in zip(iv,solution[len(iu):]):ev[i]=x
        certificate=exact_certificate(G,h,E,e,eu,ev)
        if certificate is not None:return certificate
    return None


def solve(n:int, rows:dict[int,list[int]], retain_solution=True):
    G,h,E,e,edges,ak,ek=matrices(n,rows)
    A=np.column_stack((-G,np.ones(len(G))))
    eq=np.column_stack((E,np.zeros(len(E))))
    c=np.zeros(len(edges)+1);c[-1]=-1
    result=linprog(c,A_ub=A,b_ub=h,A_eq=eq,b_eq=e,bounds=[(None,None)]*len(c),method='highs')
    report={'solver_status':int(result.status),'solver_message':result.message}
    if result.success:
        t=float(result.x[-1]);report['maximum_normalized_angle_margin']=t
        if t<=1e-9:
            cert=exact_certificate(G,h,E,e,-result.ineqlin.marginals,result.eqlin.marginals)
            if cert is None:cert=reconstruct_dual(G,h,E,e,-result.ineqlin.marginals,result.eqlin.marginals)
            if cert is not None: report.update(classification='EXACT_ANGLE_OBSTRUCTION',certificate=cert)
            else:report['classification']='UNVERIFIED_NUMERICAL_ZERO_MARGIN'
        else:
            beta=[Fraction(float(x)).limit_denominator(10**8) for x in result.x[:-1]]
            eq_ok=all(sum(Fraction(int(a))*b for a,b in zip(row,beta))==int(rhs) for row,rhs in zip(E,e))
            margins=[sum(Fraction(int(a))*b for a,b in zip(row,beta))+int(rhs) for row,rhs in zip(G,h)]
            exact=eq_ok and min(margins)>0
            report['classification']='EXACT_ANGLE_RELAXATION_FEASIBLE' if exact else 'NUMERICAL_ANGLE_RELAXATION_FEASIBLE'
            if retain_solution:
                report['chord_directions_over_pi']=[str(x) for x in beta] if exact else result.x[:-1].tolist()
                if exact:report['exact_minimum_angle']=str(min(margins))
    else:
        # Equality-only inconsistencies get exact linear certificates.
        import sympy as sp
        M=sp.Matrix(E.tolist());q=sp.Matrix(e.tolist())
        found=None
        for v in M.T.nullspace():
            rhs=(v.T*q)[0]
            if rhs:
                found={'kind':'inconsistent-equalities','equality_weights':[[i,str(x)] for i,x in enumerate(v) if x],'constant':str(rhs)};break
        if found:report.update(classification='EXACT_ANGLE_OBSTRUCTION',certificate=found)
        else:report['classification']='UNVERIFIED_SOLVER_FAILURE'
    return report
