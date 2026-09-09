"""Exact necessary-graph probe for TWO free new vertices; survivors are not candidates.

This probe uses closed insertion triangles and all 42 old-pair slots. It does
NOT enforce simultaneous common-radius constraints for zero-old rows or mutual
convexity between new points. It cannot certify a construction.
"""
from pathlib import Path
import tempfile,zipfile,sys,hashlib,json,argparse
ROOT=Path(__file__).resolve().parent
EXPECTED='dfd032636763cf67c45338c22f24334eb9e5b17367a0de57b00eb074cdfea0e1'
def load_prior():
    source=ROOT/'inputs/prior_internal_support.zip'
    if hashlib.sha256(source.read_bytes()).hexdigest()!=EXPECTED:raise ValueError('prior archive hash mismatch')
    td=tempfile.TemporaryDirectory(prefix='erdos97-two-free-')
    base=Path(td.name).resolve()
    with zipfile.ZipFile(source)as z:
        for info in z.infolist():
            out=(base/info.filename).resolve()
            if base not in out.parents:raise ValueError('unsafe prior archive path')
        z.extractall(base)
    old=base/'erdos97_internal_support_2026_09_08';sys.path.insert(0,str(old))
    import one_free as O
    return td,O,hashlib.sha256(source.read_bytes()).hexdigest()

def peel(adjacency,need):
    active=set(range(44));layers=[]
    while True:
        rem=sorted(i for i in active if len(adjacency[i]&active)<need[i])
        if not rem:return sorted(active),layers
        active.difference_update(rem);layers.append(rem)

def run():
    td,O,sha=load_prior()
    try:
        P,slots,base_edges,_=O.setup();Ts=[O.insertion_triangle(P,k)for k in range(9)]
        incoming=[O.allowed_incoming(P,slots,T)for T in Ts]
        outgoing={}
        for cell,T in enumerate(Ts):
            for old in [None]+list(range(9)):
                outgoing[cell,old]=list(range(42))if old is None else [i for i,s in enumerate(slots)if O.possible(O.free_to_regular_range(P,old,s,T))]
        def cross_range(cell,target,old):
            if old is None:return True
            vals=[]
            for f in Ts[cell]:
                r=O.dist(f,P[old]);vals.extend(O.dist(f,g)-r for g in Ts[target])
                vals.append(O.dist(f,O.closest_on_triangle(f,Ts[target]))-r)
            return min(vals)<=0<=max(vals)
        mutual={(a,b,j):cross_range(a,b,j)for a in range(9)for b in range(9)for j in [None]+list(range(9))}
        counts={};cell_summary=[];examples=[];rejected=[]
        for a in range(9):
            for b in range(a,9):
                passed=0;failed=0
                for olda in [None]+list(range(9)):
                    for oldb in [None]+list(range(9)):
                        # Same-cell free labels are interchangeable; keep both assignments
                        # anyway. Different-cell order is canonical, so none are omitted.
                        A=[set()for _ in range(44)]
                        for u,v in base_edges:A[u].add(v)
                        for k,cell,old in [(42,a,olda),(43,b,oldb)]:
                            for i in incoming[cell]:A[i].add(k)
                            A[k].update(outgoing[cell,old])
                        if mutual[a,b,olda]:A[42].add(43)
                        if mutual[b,a,oldb]:A[43].add(42)
                        need=[2]*42+[4 if olda is None else 3,4 if oldb is None else 3]
                        active,layers=peel(A,need)
                        survives=42 in active and 43 in active
                        key=('zero'if olda is None else'one')+'-'+('zero'if oldb is None else'one')
                        counts.setdefault(key,dict(cases=0,rejected=0,survived=0));counts[key]['cases']+=1
                        counts[key]['survived'if survives else'rejected']+=1
                        row={'cells':[a,b],'old_witnesses':[olda,oldb],'remaining':active,'layers':layers}
                        if survives:
                            passed+=1
                            if len(examples)<8:examples.append(row)
                        else:failed+=1;rejected.append(row)
                cell_summary.append({'cells':[a,b],'survived':passed,'rejected':failed})
        return dict(schema='erdos97.two_free_coarse_probe.v1',status='inconclusive necessary relaxation',
                    base_sha=O.B.BASE_SHA,input_archive_sha256=sha,
                    slot_count=42,insertion_cell_count=9,cell_pair_count=45,
                    cases=sum(v['cases']for v in counts.values()),counts=counts,
                    cell_summary=cell_summary,survivor_examples=examples,rejections=rejected,
                    omitted_constraints=['one common radius for each zero-old free row',
                    'simultaneous realization of possible graph edges','mutual strict convexity of new points',
                    'richness of old vertices','distance equalities beyond range feasibility'],
                    not_a_geometric_candidate=True,not_an_exclusion_of_all_two_free_caps=True)
    finally:td.cleanup()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');ap.add_argument('--check',action='store_true');a=ap.parse_args()
    d=run();s=json.dumps(d,indent=2,sort_keys=True)+'\n';p=ROOT/'data/cap_pair_probe.json'
    if a.write:p.write_text(s)
    if a.check and p.read_text()!=s:raise ValueError('probe replay differs')
    print(json.dumps({k:v for k,v in d.items()if k not in ['cell_summary','survivor_examples','rejections']},indent=2))
if __name__=='__main__':main()
