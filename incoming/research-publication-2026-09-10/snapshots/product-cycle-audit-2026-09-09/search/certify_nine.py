"""Discover integer certificates; floating solver status alone is not proof."""
import argparse,json,sys,time
from pathlib import Path
from fractions import Fraction as F
from math import lcm,gcd
import numpy as np
from c3_model import margin
ROOT=Path(__file__).resolve().parents[1]

def certificate(result, model):
    A,E,al,el=model
    if not result.success or result.x[-1]>1e-9:return None
    lam=[F(float(-q)).limit_denominator(1000000) for q in result.ineqlin.marginals]
    mu=[F(float(q)).limit_denominator(1000000) for q in result.eqlin.marginals[:-1]]
    w=F(float(result.eqlin.marginals[-1])).limit_denominator(1000000)
    if w<0 or any(q<0 for q in lam):raise ValueError('Wrong dual sign')
    total=[F(0) for _ in range(A.shape[1])]
    for mat,coef in [(A,lam),(E,mu)]:
        for v,q in zip(mat,coef):
            if q:
                for j in np.flatnonzero(v):total[j]+=q*int(v[j])
    total[-1]+=w
    if any(total):raise ValueError('Rational dual reconstruction failed')
    terms=[(lab,q,False)for lab,q in zip(al,lam)if q]+[(lab,q,True)for lab,q in zip(el,mu)if q]
    if w:terms.append((['pi_positive'],w,False))
    d=lcm(*(q.denominator for _,q,_ in terms));g=gcd(*(int(q*d)for _,q,_ in terms))
    return {'strict':[[lab,int(q*d)//g]for lab,q,eq in terms if not eq], 'equal':[[lab,int(q*d)//g]for lab,q,eq in terms if eq]}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--inputs',nargs='+',required=True);ap.add_argument('--output',required=True);ap.add_argument('--limit',type=int);args=ap.parse_args()
    seen={}
    for name in args.inputs:
        for case in json.load(open(name)):
            key=json.dumps(case['rows']);seen.setdefault(key,{'rows':case['rows'],'sources':[]})['sources'].append({'file':Path(name).name,'index':case['index']})
    records=[];start=time.monotonic()
    for idx,case in enumerate(seen.values()):
        if args.limit is not None and idx>=args.limit:break
        r,mod=margin(case['rows']);cert=certificate(r,mod)
        rec={**case,'index':idx,'certificate':cert,'solver_success':bool(r.success),'numerical_margin':float(r.x[-1])if r.success else None}
        records.append(rec)
        output={'scope':'exact certificates for these stored fixed-order systems only; no exhaustive nine-orbit theorem','cases':records,'seconds':time.monotonic()-start}
        Path(args.output).write_text(json.dumps(output,indent=2)+'\n')
        print(idx, bool(cert), rec['numerical_margin'],flush=True)
if __name__=='__main__':main()
