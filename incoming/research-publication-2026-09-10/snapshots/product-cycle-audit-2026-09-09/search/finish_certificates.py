"""Resume certificate discovery, with finite solver guards and an exact dual fallback."""
from pathlib import Path
import sys,json,time
from fractions import Fraction as F
from math import lcm,gcd
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import csr_matrix,hstack,vstack
from c3_model import model,margin
from certify_nine import certificate
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'verify'))
from check_c3 import Geometry

def direct_dual(rows,seconds=5):
    A,E,al,el=model(rows);n,k=A.shape;e=len(E)
    mat=hstack([csr_matrix(A.T),csr_matrix(E.T)],format='csr')
    norm=csr_matrix(([1.]*n,([0]*n,list(range(n)))),shape=(1,n+e))
    eq=vstack([mat,norm],format='csr');rhs=np.zeros(k+1);rhs[-1]=1
    r=linprog(np.zeros(n+e),A_eq=eq,b_eq=rhs,bounds=[(0,None)]*n+[(None,None)]*e,method='highs',options={'time_limit':seconds,'presolve':False})
    if not r.success:return None,{'status':int(r.status),'message':r.message}
    vals=[F(float(x)).limit_denominator(1000000)for x in r.x]
    if any(x<0 for x in vals[:n]):return None,{'reason':'negative rationalized strict coefficient'}
    total=[F(0)]*k
    for row,q in zip(np.vstack([A,E]),vals):
        if q:
            for i in np.flatnonzero(row):total[i]+=q*int(row[i])
    if any(total):return None,{'reason':'rationalized dual not exact'}
    den=lcm(*(x.denominator for x in vals));g=gcd(*(int(x*den)for x in vals))
    cert={'strict':[[lab,int(q*den)//g]for lab,q in zip(al,vals[:n])if q],
          'equal':[[lab,int(q*den)//g]for lab,q in zip(el,vals[n:])if q]}
    Geometry(rows).certificate(cert)
    return cert,{'status':0,'method':'direct homogeneous dual, exact reconstruction'}

def main():
    target=ROOT/'reports/all_fixed_system_certificates.json'
    data=json.loads(target.read_text());previous=data['cases'];done={json.dumps(c['rows']):c for c in previous}
    inputs=[ROOT/'inputs/filter9_all.json',ROOT/'inputs/filter9_slices.json',ROOT/'reports/stronger_all_systems.json',ROOT/'reports/arc_2m_systems.json']
    universe={}
    for p in inputs:
        for c in json.loads(p.read_text()):
            key=json.dumps(c['rows']);universe.setdefault(key,{'rows':c['rows'],'sources':[]})['sources'].append({'file':p.name,'index':c['index']})
    start=time.monotonic();out=[]
    for i,(key,c) in enumerate(universe.items()):
        if key in done:q=done[key];q['sources']=c['sources']
        else:
            cert,status=direct_dual(c['rows']);q={**c,'index':i,'certificate':cert,'discovery_status':status}
            print(i,bool(cert),status,flush=True)
        out.append(q)
        report={'scope':'exact rejection only of the stored cases with non-null certificates; not exhaustive nine-orbit coverage',
          'cases':out,'completed_cases':len(out),'universe_size':len(universe),'discovery_completed':len(out)==len(universe),
          'prior_run_status':'external timeouts after 164 primal cases and 314 direct-dual cases; both processes terminated; remaining direct-dual run disables presolve',
          'resumed_seconds':time.monotonic()-start,'per_new_case_solver_time_limit_seconds':5}
        target.write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
