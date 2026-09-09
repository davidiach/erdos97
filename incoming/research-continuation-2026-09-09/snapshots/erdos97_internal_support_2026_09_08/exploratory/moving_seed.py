"""Bounded, nonsymmetric three-copy moving-seed experiment; not a certificate.

The nine approximate Danzer base points come from the repository's documented
numerical base at commit 047d05149382e48b602b292df4b8fc9e2da560bb, module
src/erdos97/danzer18_doubling.py. They are initialization data only.

All 27 physical coordinates move independently (modulo four similarity gauges).
Witness pools are restricted to the three old distance-three target clusters.
Selected rows pass exact *combinatorial* pair/cyclic-order tests before geometry
is optimized. MILP failures/timeouts and numerical failures are not exclusions.
"""
from itertools import combinations, product
from pathlib import Path
import argparse
import json
import math
import platform
import time
import numpy as np
import scipy
from scipy.optimize import milp, Bounds, LinearConstraint, minimize
from scipy.sparse import coo_array

ROOT=Path(__file__).resolve().parent
OLD_ORDER=[2,4,8,0,5,6,1,3,7]
CROSS={0:(2,1),1:(0,0),2:(1,0)}

def base():
    radii=[1.,1.0232765362286151212279138415749844121975239899365,
           .84430467659553225135054203657922644411506189825712]
    phases=[0.,2.1348899349009594429280251524108783933547943057754,
            .34318985719866858113539443829133834740024089795205]
    return np.array([[r*math.cos(ph+2*math.pi*j/3),r*math.sin(ph+2*math.pi*j/3)]
                     for r,ph in zip(radii,phases) for j in range(3)])

def pool(i):
    m,j=divmod(i,3); vm,tv=CROSS[m]
    return [3*m+(j+1)%3,3*m+(j+2)%3,3*vm+(j+tv)%3]

def initialize(seed,epsilon):
    P=base(); rng=np.random.default_rng(seed)
    result=np.empty((27,2))
    for k,i in enumerate(OLD_ORDER):
        u=P[i]-P[OLD_ORDER[k-1]]
        v=P[OLD_ORDER[(k+1)%9]]-P[i]
        alpha=math.atan2(-u[0],u[1])
        delta=math.atan2(u[0]*v[1]-u[1]*v[0],u@v)
        assert delta>0
        # Samples of the outer circular arc of P+epsilon*disk are convex.
        # Independent small fractional perturbations break C3 symmetry.
        fractions=np.array([.2,.5,.8])+rng.uniform(-.035,.035,3)
        angles=alpha+delta*fractions
        result[3*i:3*i+3]=P[i]+epsilon*np.column_stack((np.cos(angles),np.sin(angles)))
    order=[3*i+s for i in OLD_ORDER for s in range(3)]
    return result,order

def crosses(i,j,a,b,rank,n):
    d=(rank[j]-rank[i])%n
    return (0<(rank[a]-rank[i])%n<d)!=(0<(rank[b]-rank[i])%n<d)

def rows_compatible(i,S,j,T,rank,n):
    common=sorted(set(S)&set(T))
    if len(common)>2:return False
    return len(common)<2 or crosses(i,j,*common,rank,n)

def preflight(rows,order):
    n=len(rows); rank={i:k for k,i in enumerate(order)}
    assert len(rank)==n
    bad=[]
    for i,S in enumerate(rows):
        if len(S)!=4 or len(set(S))!=4 or i in S or any(not 0<=x<n for x in S):
            raise ValueError('invalid four-point row')
    for i,j in combinations(range(n),2):
        if not rows_compatible(i,rows[i],j,rows[j],rank,n):bad.append([i,j])
    return bad

def domains(X):
    out=[]
    for i in range(27):
        clusters=pool(i//3)
        rows=[]
        for target in clusters:
            others=[j for j in clusters if j!=target]
            for pair in combinations(range(3),2):
                for singles in product(range(3),repeat=2):
                    S=tuple(sorted([3*target+s for s in pair]+[3*j+s for j,s in zip(others,singles)]))
                    d=((X[list(S)]-X[i])**2).sum(axis=1)
                    cost=float(np.var(d)/(np.mean(d)**2))
                    resource=3*target+list(combinations(range(3),2)).index(pair)
                    rows.append((S,resource,cost))
        assert len(rows)==81 and len({r[0] for r in rows})==81
        out.append(rows)
    return out

def select_pattern(X,order,seed,max_rounds=50):
    D=domains(X); variables=[(i,S,r,c) for i,rows in enumerate(D) for S,r,c in rows]
    nvar=len(variables); rng=np.random.default_rng(seed)
    cost=np.array([r[3] for r in variables])+rng.uniform(0,1e-9,nvar)
    rr=[];cc=[];vv=[]
    for k,(i,S,r,c) in enumerate(variables):
        rr.extend([i,27+r]);cc.extend([k,k]);vv.extend([1.,1.])
    lower=[1.]*27+[-np.inf]*27;upper=[1.]*54
    rank={i:k for k,i in enumerate(order)}
    cuts=set(); history=[]
    for round_index in range(max_rounds):
        mat=coo_array((np.array(vv), (np.array(rr,dtype=np.int32),np.array(cc,dtype=np.int32))),shape=(len(lower),nvar)).tocsc()
        start=time.monotonic()
        res=milp(cost,integrality=np.ones(nvar),bounds=Bounds(0,1),
                 constraints=LinearConstraint(mat,lower,upper),
                 options={'time_limit':2.,'mip_rel_gap':0.001,'presolve':True})
        record={'round':round_index,'solver_status':int(res.status),'message':res.message,
                'elapsed_seconds':round(time.monotonic()-start,4),'cuts':len(cuts)}
        if res.x is None:
            history.append(record)
            return None,history
        chosen=np.flatnonzero(res.x>.5).tolist()
        if len(chosen)!=27 or sorted(variables[k][0] for k in chosen)!=list(range(27)):
            record['invalid_integral_assignment']=True;history.append(record);return None,history
        chosen.sort(key=lambda k:variables[k][0])
        rows=[list(variables[k][1]) for k in chosen]
        bad=preflight(rows,order)
        record['preflight_violations']=len(bad);record['objective']=float(res.fun)
        history.append(record)
        if not bad:return rows,history
        for i,j in bad:
            cut=tuple(sorted([chosen[i],chosen[j]]))
            if cut in cuts:raise RuntimeError('solver repeated a forbidden row pair')
            cuts.add(cut);index=len(lower)
            rr.extend([index,index]);cc.extend(cut);vv.extend([1.,1.]);lower.append(-np.inf);upper.append(1.)
    return None,history

def geometry(X,order):
    n=len(X); signs=[]
    for k,i in enumerate(order):
        j=order[(k+1)%n]; u=X[j]-X[i]
        for t in range(n):
            if t not in (i,j):
                v=X[t]-X[i]; signs.append(u[0]*v[1]-u[1]*v[0])
    distances=[np.linalg.norm(X[i]-X[j]) for i,j in combinations(range(n),2)]
    return {'minimum_supporting_area':float(min(signs)),
            'minimum_pair_distance':float(min(distances)),
            'strict_hull_numeric':bool(min(signs)>0)}

def optimize_coordinates(X,rows,order,maxiter=250):
    # Fix two well-separated physical points. This removes only similarities.
    n=len(X);gauge=(0,12)
    z=X[:,0]+1j*X[:,1];z=(z-z[gauge[0]])/(z[gauge[1]]-z[gauge[0]])
    X=np.column_stack((z.real,z.imag)); X[gauge[0]]=[0.,0.];X[gauge[1]]=[1.,0.]
    free=[i for i in range(n) if i not in gauge]
    columns=np.array([2*i+j for i in free for j in (0,1)])
    initial=X.copy(); seed_geometry=geometry(initial,order)
    area_margin=min(1e-7,max(1e-12,seed_geometry['minimum_supporting_area']/4))
    sep=min(.001,seed_geometry['minimum_pair_distance']/4)
    residual_records=[(i,rows[i][0],j) for i in range(n) for j in rows[i][1:]]
    weights=np.array([max(np.mean(((initial[rows[i]]-initial[i])**2).sum(axis=1)),1e-5)
                      for i,a,b in residual_records])
    supports=[(order[k],order[(k+1)%n],j) for k in range(n) for j in range(n)
              if j not in (order[k],order[(k+1)%n])]
    pairs=list(combinations(range(n),2))
    def unpack(v):
        Y=initial.copy();Y[free]=v.reshape(-1,2);return Y
    def residual(v,gradient=False):
        Y=unpack(v);out=[];J=[]
        for k,(i,a,b) in enumerate(residual_records):
            u=Y[i]-Y[a];w=Y[i]-Y[b]
            out.append((u@u-w@w)/weights[k])
            if gradient:
                g=np.zeros((n,2));g[i]=2*(u-w);g[a]=-2*u;g[b]=2*w
                J.append(g.ravel()[columns]/weights[k])
        return (np.array(out),np.array(J)) if gradient else np.array(out)
    def objective(v):
        r,J=residual(v,True);return float(r@r),2*r@J
    def inequalities(v,gradient=False):
        Y=unpack(v);out=[];J=[]
        for i,j,k in supports:
            u=Y[j]-Y[i];w=Y[k]-Y[i]
            out.append(u[0]*w[1]-u[1]*w[0]-area_margin)
            if gradient:
                g=np.zeros((n,2));g[j]=[w[1],-w[0]];g[k]=[-u[1],u[0]];g[i]=-g[j]-g[k]
                J.append(g.ravel()[columns])
        for i,j in pairs:
            u=Y[i]-Y[j];out.append(u@u-sep**2)
            if gradient:
                g=np.zeros((n,2));g[i]=2*u;g[j]=-2*u;J.append(g.ravel()[columns])
        return np.array(J) if gradient else np.array(out)
    x0=initial[free].ravel()
    # Analytic-derivative validation in a deterministic nontrivial direction.
    direction=np.sin(np.arange(len(x0))+1);h=1e-7
    r,J=residual(x0,True)
    rerr=float(np.max(np.abs((residual(x0+h*direction)-residual(x0-h*direction))/(2*h)-J@direction)))
    gerr=float(np.max(np.abs((inequalities(x0+h*direction)-inequalities(x0-h*direction))/(2*h)-inequalities(x0,True)@direction)))
    if max(rerr,gerr)>1e-6:raise RuntimeError('derivative check failed')
    start=time.monotonic()
    result=minimize(objective,x0,jac=True,method='SLSQP',bounds=[(-3,3)]*len(x0),
                    constraints={'type':'ineq','fun':inequalities,'jac':lambda x:inequalities(x,True)},
                    options={'maxiter':maxiter,'ftol':1e-13,'disp':False})
    final=unpack(result.x); r=residual(result.x)
    return {'initial_coordinates':initial.tolist(),'final_coordinates':final.tolist(),
            'initial_geometry':seed_geometry,'final_geometry':geometry(final,order),
            'maximum_relative_squared_distance_difference':float(np.max(np.abs(r))),
            'residual_sum_squares':float(r@r),'optimizer_success':bool(result.success),
            'optimizer_status':int(result.status),'optimizer_message':result.message,
            'iterations':int(result.nit),'elapsed_seconds':round(time.monotonic()-start,4),
            'required_supporting_area':area_margin,'required_pair_separation':sep,
            'minimum_constraint_slack':float(inequalities(result.x).min()),
            'derivative_errors':{'residual':rerr,'constraint':gerr},
            'all_coordinates_free_modulo_similarities':True,'exact_solution_certified':False}

def select_pattern_direct(X,order,seed,time_limit=15.):
    """Full same-side witness-pair resource model, followed by exact preflight."""
    D=domains(X)
    variables=[(i,S,r,c) for i,rows in enumerate(D) for S,r,c in rows]
    rank={i:k for k,i in enumerate(order)}
    resources={}
    for k,(i,S,r,c) in enumerate(variables):
        for a,b in combinations(S,2):
            side=int(0<(rank[i]-rank[a])%27<(rank[b]-rank[a])%27)
            resources.setdefault((a,b,side),[]).append(k)
    rr=[];cc=[]
    for k,(i,S,r,c) in enumerate(variables):rr.append(i);cc.append(k)
    for j,ids in enumerate(resources.values()):
        rr.extend([27+j]*len(ids));cc.extend(ids)
    mat=coo_array((np.ones(len(rr)),(np.array(rr,dtype=np.int32),np.array(cc,dtype=np.int32))),
                  shape=(27+len(resources),len(variables))).tocsc()
    lower=np.r_[np.ones(27),np.full(len(resources),-np.inf)]
    cost=np.array([v[3] for v in variables])+np.random.default_rng(seed).uniform(0,1e-9,len(variables))
    start=time.monotonic()
    res=milp(cost,integrality=np.ones(len(variables)),bounds=Bounds(0,1),
             constraints=LinearConstraint(mat,lower,np.ones(len(lower))),
             options={'time_limit':time_limit,'mip_rel_gap':.01})
    log={'method':'complete same-side witness-pair resource constraints',
         'solver_status':int(res.status),'message':res.message,'resources':len(resources),
         'variables':len(variables),'elapsed_seconds':round(time.monotonic()-start,4),
         'objective':None if res.fun is None else float(res.fun),
         'optimality_or_infeasibility_certified':False}
    if res.x is None:return None,[log]
    ids=np.flatnonzero(res.x>.5).tolist()
    if len(ids)!=27 or sorted(variables[k][0] for k in ids)!=list(range(27)):
        log['invalid_integral_assignment']=True;return None,[log]
    ids.sort(key=lambda k:variables[k][0])
    rows=[list(variables[k][1]) for k in ids]
    assert len({variables[k][2] for k in ids})==27
    assert not preflight(rows,order)
    log['preflight_violations']=0
    return rows,[log]

def run(seed=1,epsilon=.02,max_rounds=50,maxiter=250,direct=False,pattern=None):
    X,order=initialize(seed,epsilon)
    g=geometry(X,order)
    if not g['strict_hull_numeric']:raise RuntimeError('initialization not convex')
    if pattern is not None:
        rows=json.loads(Path(pattern).read_text())['rows'];history=[{'method':'retained preflight pattern'}]
        assert not preflight(rows,order)
    elif direct:
        rows,history=select_pattern_direct(X,order,seed)
    else:
        rows,history=select_pattern(X,order,seed,max_rounds)
    report={'status':'exploratory only; no infeasibility or exact solution claim',
            'seed':seed,'epsilon':epsilon,'vertices':27,'old_base_vertices':9,
            'copies_per_cluster':3,'boundary_order':order,'initial_coordinates':X.tolist(),
            'initial_geometry':g,'pattern_search':history,'selected_rows':rows,
            'preflight_scope':['four distinct witnesses','two-circle intersection cap',
                               'two-overlap cyclic crossing','internal-cluster-pair capacity'],
            'geometric_hypotheses':['fixed three-original-target-cluster pools','fixed cluster boundary order'],
            'numpy':np.__version__,'scipy':scipy.__version__,'python':platform.python_version()}
    if rows is not None:
        assert not preflight(rows,order)
        report['optimization']=optimize_coordinates(X,rows,order,maxiter)
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--seed',type=int,default=1)
    parser.add_argument('--epsilon',type=float,default=.02);parser.add_argument('--rounds',type=int,default=50)
    parser.add_argument('--iterations',type=int,default=250);parser.add_argument('--output',required=True)
    parser.add_argument('--direct',action='store_true');parser.add_argument('--pattern')
    args=parser.parse_args()
    report=run(args.seed,args.epsilon,args.rounds,args.iterations,args.direct,args.pattern)
    Path(args.output).write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['initial_coordinates','selected_rows','pattern_search','optimization']},indent=2))
    print('preflight pattern',report['selected_rows'] is not None)
    if 'optimization' in report:print('maximum residual',report['optimization']['maximum_relative_squared_distance_difference'])
