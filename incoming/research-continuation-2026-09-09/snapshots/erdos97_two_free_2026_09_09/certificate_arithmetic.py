"""Check a stored strict-distance cancellation without using its discoverer."""
from collections import defaultdict


def check(record, ranks):
    rows={int(i):tuple(w)for i,w in record['rows'].items()}
    links=defaultdict(set)
    for source,witnesses in rows.items():
        if len(witnesses)!=4 or len(set(witnesses))!=4 or source in witnesses:
            raise ValueError('Malformed selected row')
        pairs=[frozenset([source,target])for target in witnesses]
        for pair in pairs:
            links[pair].update(pairs)
    component={}
    for pair in links:
        if pair in component:continue
        reached={pair};queue=[pair]
        while queue:
            next_pair=queue.pop()
            for candidate in links[next_pair]:
                if candidate not in reached:
                    reached.add(candidate);queue.append(candidate)
        key=min(tuple(sorted(p))for p in reached)
        component.update({p:key for p in reached})
    rows_required=1 if record['type']=='zero' else 2 if record['type']=='inverse' else 0
    if not rows_required or len(record['inequalities'])!=rows_required:
        raise ValueError('Wrong strict-inequality count')
    sum_coefficients=defaultdict(int)
    for inequality in record['inequalities']:
        quad=inequality['quad'];kind=inequality['kind']
        if len(quad)!=4 or len(set(quad))!=4 or type(kind)is not int or kind not in(0,1):
            raise ValueError('Invalid quadrilateral inequality')
        if not all(ranks[quad[k]]<ranks[quad[k+1]]for k in range(3)):
            raise ValueError('Cyclic order is not forced by four distinct ranks')
        a,b,c,d=quad
        sides=((a,b),(c,d))if kind==0 else((a,d),(b,c))
        for pair,weight in[((a,c),1),((b,d),1),(sides[0],-1),(sides[1],-1)]:
            key=component.get(frozenset(pair),tuple(sorted(pair)))
            sum_coefficients[key]+=weight
    if any(sum_coefficients.values()):raise ValueError('The strict sum does not cancel')
    return True
