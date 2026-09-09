"""Bounded pattern search with exact convex-quadrilateral checks *before* geometry.

Uses positive integer contradiction certificates for learned row-assignment
cuts. No solver infeasibility status is used as a mathematical exclusion.
"""
from itertools import combinations
from pathlib import Path
import argparse,json,sys,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import kalmanson as K
import moving_seed as M
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import coo_array


def run(seed=622,epsilon=.1,max_rounds=20,time_limit=5):
    X,order=M.initialize(seed,epsilon);D=M.domains(X)
    variables=[(i,S,r,c) for i,rs in enumerate(D) for S,r,c in rs]
    lookup={(i,tuple(S)):k for k,(i,S,r,c) in enumerate(variables)}
    rank={i:k for k,i in enumerate(order)};resources={}
    for k,(i,S,r,c) in enumerate(variables):
        for a,b in combinations(S,2):
            side=int(0<(rank[i]-rank[a])%27<(rank[b]-rank[a])%27)
            resources.setdefault((a,b,side),[]).append(k)
    rr=[];cc=[]
    for k,(i,S,r,c) in enumerate(variables):rr.append(i);cc.append(k)
    lo=[1.]*27;hi=[1.]*27
    for inds in resources.values():
        r=len(lo);rr.extend([r]*len(inds));cc.extend(inds);lo.append(-np.inf);hi.append(1.)
    rng=np.random.default_rng(seed)
    costs=np.asarray([v[3] for v in variables])+rng.uniform(0,1e-6,len(variables))
    cuts=set();history=[];result={'status':'bounded exploratory scan; no family exclusion',
        'seed':seed,'epsilon':epsilon,'round_limit':max_rounds,'time_limit_per_milp':time_limit,
        'boundary_order':order,'initial_coordinates':X.tolist(),'resources':len(resources),
        'variables':len(variables),'rounds':history,'optimization':None}
    for iteration in range(max_rounds):
        mat=coo_array((np.ones(len(rr)),(np.array(rr,dtype=np.int32),np.array(cc,dtype=np.int32))),
                      shape=(len(lo),len(variables))).tocsc()
        start=time.monotonic()
        sol=milp(costs,integrality=np.ones(len(variables)),bounds=Bounds(0,1),
            constraints=LinearConstraint(mat,lo,hi),options={'time_limit':time_limit,'presolve':True})
        record={'iteration':iteration,'milp_status':int(sol.status),'message':sol.message,
                'elapsed_seconds':round(time.monotonic()-start,4),'cuts_before':len(cuts)}
        if sol.x is None:
            record['outcome']='no integral assignment returned; not an exclusion';history.append(record);break
        chosen=np.flatnonzero(sol.x>.5).tolist();chosen.sort(key=lambda k:variables[k][0])
        if len(chosen)!=27 or [variables[k][0] for k in chosen]!=list(range(27)):
            raise RuntimeError('invalid discrete assignment')
        rows=[list(variables[k][1]) for k in chosen]
        if M.preflight(rows,order):raise RuntimeError('failed circle/crossing preflight')
        record['rows']=rows;record['strong_preflight']=K.discover(rows,order,time_limit=15)
        state=record['strong_preflight']['status']
        if state=='exact obstruction':
            for certificate in record['strong_preflight']['certificates']:
                K.validate_certificate(rows,order,certificate)
                cut=tuple(sorted(lookup[(i,tuple(rows[i]))] for i in certificate['selected_centers']))
                if cut in cuts:raise RuntimeError('repeated excluded row assignment')
                cuts.add(cut);r=len(lo);rr.extend([r]*len(cut));cc.extend(cut)
                lo.append(-np.inf);hi.append(float(len(cut)-1))
            record['outcome']='exactly rejected before optimization';history.append(record)
        elif state=='exact feasible linear relaxation':
            record['outcome']='eligible for numerical geometry; not a Euclidean certificate';history.append(record)
            result['selected_rows']=rows
            result['optimization']=M.optimize_coordinates(X,rows,order,maxiter=350)
            break
        else:
            record['outcome']='preflight unresolved; numerical optimization not run';history.append(record);break
    result['learned_exact_cuts']=len(cuts)
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--seed',type=int,default=622)
    p.add_argument('--rounds',type=int,default=20);p.add_argument('--time-limit',type=float,default=5.)
    p.add_argument('--output',required=True);a=p.parse_args()
    r=run(seed=a.seed,max_rounds=a.rounds,time_limit=a.time_limit)
    Path(a.output).write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'rounds':len(r['rounds']),'cuts':r['learned_exact_cuts'],
        'optimization_run':r['optimization'] is not None,'final_outcome':r['rounds'][-1]['outcome']},indent=2))
if __name__=='__main__':main()
