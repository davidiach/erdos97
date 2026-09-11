"""Exact incidence-only guardrail: a 60-state two-out graph with no diamonds.
No convex order, metric, gain assignment or Euclidean realization is asserted.
"""
from itertools import combinations
from collections import deque

def compose(p,q):return tuple(p[q[i]]for i in range(5))
def build():
    identity=tuple(range(5));a=(1,2,0,3,4);b=(1,2,3,4,0)
    group={identity};Q=deque([identity])
    while Q:
        p=Q.popleft()
        for g in(a,b):
            q=compose(p,g)
            if q not in group:group.add(q);Q.append(q)
    perms=sorted(group);ids={p:i for i,p in enumerate(perms)}
    rows=[[ids[compose(p,g)]for g in(a,b)]for p in perms]
    if len(rows)!=60:raise ValueError('wrong generated group size')
    for i,row in enumerate(rows):
        if len(set(row))!=2 or i in row:raise ValueError('bad directed row')
        if any(i in rows[j]for j in row):raise ValueError('reciprocity')
        j,k=row
        if set(rows[j])&set(rows[k]):raise ValueError('diamond')
    return {'status':'PASS_EXACT_ABSTRACT_NEGATIVE_CONTROL','states':60,'outdegree':2,'reciprocal_pairs':0,'directed_diamonds':0,'generators':[a,b],
      'permutations':perms,'rows':rows,'convex_order_claimed':False,'Euclidean_realization_claimed':False,
      'meaning':'outdegree two and no reciprocity alone do not force the diamond pattern'}
if __name__=='__main__':
    import json
    print(json.dumps(build(),indent=2))
