"""Exact replay of the one/two-diamond phase filter and saved C++ cross-check.
Default mode uses only the standard library, not a compiler or optimizer.
It also emits separately checkable integer phase certificates for each rejection.
"""
from pathlib import Path
from itertools import combinations
import argparse,json,sys
from diamond_phase import diamonds,relation,check
ROOT=Path(__file__).resolve().parents[1]

def certificate(rows):
    m=len(rows);eq=[]
    for info in diamonds(rows):
        lab=['diamond',*info['labels']];v=relation(rows,*info['labels'])
        gap=[v.get('L',0)+sum(a for k,a in v.items()if k!='L' and k>h)for h in range(m)]
        eq.append((lab,gap))
    def convert(vector,terms):
        positive=any(x>0 for x in vector);negative=any(x<0 for x in vector)
        if positive==negative:return None
        sign=1 if positive else -1
        strict=[]
        for h,x in enumerate(vector):
            if x:
                lab=['phase_gap',h,h+1]if h<m-1 else ['sector_span',0,m-1]
                strict.append([lab,sign*x])
        cert={'strict':strict,'equal':[[lab,-sign*w]for lab,w in terms if w]}
        check(rows,cert)
        return cert
    for lab,vec in eq:
        result=convert(vec,[(lab,1)])
        if result:return result
    for (lab,v),(label,w)in combinations(eq,2):
        for h in range(m):
            result=convert([w[h]*a-v[h]*b for a,b in zip(v,w)],[(lab,w[h]),(label,-v[h])])
            if result:return result
    return None

def verify():
    if sys.flags.optimize:raise ValueError('Do not disable assertions')
    data=json.loads((ROOT/'reports/all_fixed_system_certificates.json').read_text())
    expected=[int(x)for x in(ROOT/'reports/phase_batch_output.txt').read_text().split()]
    results=[];certs=[]
    for case in data['cases']:
        cert=certificate(case['rows']);results.append(int(cert is None))
        if cert:certs.append({'index':case['index'],'rows':case['rows'],'certificate':cert})
    if results!=expected or len(results)!=333:raise ValueError('C++/Python phase filter disagreement')
    crosswalk=json.loads((ROOT/'reports/phase_2m_crosswalk.json').read_text())
    retained=json.loads((ROOT/'reports/phase_2m_systems.json').read_text())
    lookup={tuple(map(tuple,c['rows'])):c['index']for c in data['cases']}
    if [lookup[tuple(map(tuple,r))]for r in retained]!=crosswalk['previously_certified_indices']:raise ValueError('Bad bounded-search crosswalk')
    if any(certificate(r)for r in retained):raise ValueError('New search retained a rejected phase system')
    report={'status':'PASS_EXACT_PHASE_FILTER_CROSSCHECK','input_systems':333,'phase_rejections':len(certs),'one_diamond_certificates':sum(len(c['certificate']['equal'])==1 for c in certs),'two_diamond_certificates':sum(len(c['certificate']['equal'])==2 for c in certs),'bounded_new_run_leaves':len(retained),'new_leaves_already_exactly_rejected':len(retained),'all_nine_orbit_patterns_exhausted':False}
    return report,{'schema':1,'scope':'phase certificates for a fixed stored corpus, not exhaustive nine-orbit coverage','cases':certs}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path);p.add_argument('--certificates',type=Path);a=p.parse_args();report,certs=verify()
    if a.output:a.output.write_text(json.dumps(report,indent=2)+'\n')
    if a.certificates:a.certificates.write_text(json.dumps(certs,indent=2)+'\n')
    print(json.dumps(report,indent=2))
