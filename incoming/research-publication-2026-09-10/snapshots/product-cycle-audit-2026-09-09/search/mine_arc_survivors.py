"""Greedily shrink extra-arrow supports; certify each retained contradiction exactly.
Deletion minimality is only with respect to this angle relaxation and this pass.
"""
from pathlib import Path
from copy import deepcopy
import sys,json,time,argparse
from c3_model import margin
from certify_nine import certificate
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'verify'))
from check_c3 import Geometry

def compress(rows):
    kept=sorted({i for i,r in enumerate(rows)if r}|{j for r in rows for j in r[::2]})
    ids={j:i for i,j in enumerate(kept)}
    return [[v for j,g in zip(rows[i][::2],rows[i][1::2])for v in(ids[j],g)]for i in kept],kept

def mine(rows):
    rows=deepcopy(rows);trials=[]
    # Remove a full center's optional row first when possible, then individual arrows.
    for i in range(len(rows)):
        trial=deepcopy(rows);trial[i]=[]
        small,_=compress(trial)
        if len(small)<3:continue
        r,mod=margin(small,ordered=False,right=False)
        c=certificate(r,mod)
        if c is not None:
            Geometry(small).certificate(c);rows=trial;trials.append(['row',i])
    changed=True
    while changed:
        changed=False
        for i in range(len(rows)):
            for k in range(len(rows[i])//2-1,-1,-1):
                trial=deepcopy(rows);del trial[i][2*k:2*k+2]
                small,_=compress(trial)
                if len(small)<3:continue
                r,mod=margin(small,ordered=False,right=False);c=certificate(r,mod)
                if c is not None:
                    Geometry(small).certificate(c);rows=trial;changed=True;trials.append(['arrow',i,k])
    rows,labels=compress(rows);r,mod=margin(rows,ordered=False,right=False);c=certificate(r,mod)
    if c is not None:Geometry(rows).certificate(c)
    return {'rows':rows,'old_labels':labels,'arrows':sum(len(x)//2 for x in rows),'certificate':c,'numerical_margin':float(r.x[-1])if r.success else None,'accepted_deletions':trials,'no_right_or_order_rows':True}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,default=8);ap.add_argument('--output',required=True);a=ap.parse_args()
    inp=json.loads((ROOT/'reports/arc_2m_systems.json').read_text());result=[];start=time.monotonic()
    for case in inp[:a.limit]:
        q=mine(case['rows']);q['source_index']=case['index'];result.append(q)
        Path(a.output).write_text(json.dumps({'scope':'local certificate mining, not all-n coverage','cases':result,'seconds':time.monotonic()-start},indent=2)+'\n')
        print(q['source_index'],len(q['rows']),q['arrows'],q['numerical_margin'],flush=True)
if __name__=='__main__':main()
