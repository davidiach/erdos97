"""Independent finite ear-resource audit; no geometric feasibility is asserted.

For a cyclic k-gon, a possible blocked-edge assignment at vertex v has base
{v-1,v+1}. Distinct assigned vertices must have distinct bases. The resource
inequality counts unused vertices plus assigned bases in a triangulation.
"""
from functools import lru_cache
from itertools import combinations


@lru_cache(None)
def triangle_sets(vertices):
    if len(vertices)<3:
        return (frozenset(),)
    a,b=vertices[0],vertices[-1]
    out=[]
    for j in range(1,len(vertices)-1):
        for left in triangle_sets(vertices[:j+1]):
            for right in triangle_sets(vertices[j:]):
                out.append(left|right|{tuple(sorted((a,vertices[j],b)))})
    return tuple(out)


def audit(max_vertices=9):
    if not 4<=max_vertices<=11:
        raise ValueError('Use a finite audit size between four and eleven.')
    records=[]; total_tri=total_assign=0
    for n in range(4,max_vertices+1):
        base=[tuple(sorted(((v-1)%n,(v+1)%n))) for v in range(n)]
        count=0; minimum=None
        triangulations=triangle_sets(tuple(range(n)))
        if len(set(triangulations))!=len(triangulations):
            raise ValueError('Duplicate triangulation.')
        for triangles in triangulations:
            edges={e for t in triangles for e in combinations(t,2)}
            if len(edges)!=2*n-3 or len(triangles)!=n-2:
                raise ValueError('Invalid triangulation counts.')
            ears=[v for v in range(n) if base[v] in edges]
            if len(ears)<2:
                raise ValueError('Fewer than two ears.')
            for mask in range(1<<n):
                used=[v for v in range(n) if mask>>v&1]
                if len({base[v] for v in used})!=len(used):
                    continue
                resources=(n-len(used))+sum(base[v] in edges for v in used)
                if resources<2:
                    raise ValueError('Cycle resource deficit failed.')
                charges=[('edge',base[v]) if v in used else ('vertex',v) for v in ears[:2]]
                if len(set(charges))!=2:
                    raise ValueError('An ear resource was charged twice.')
                minimum=resources if minimum is None else min(minimum,resources)
                count+=1
        records.append({'cycle_vertices':n,'triangulations':len(triangulations),
                        'injective_blocker_assignments':count,'minimum_resource_sum':minimum})
        total_tri+=len(triangulations);total_assign+=count
    return {'scope':'Finite combinatorial relaxation only, not geometric realizability.',
            'max_cycle_vertices':max_vertices,'triangulations':total_tri,
            'injective_blocker_assignments':total_assign,'records':records}

if __name__=='__main__':
    import json
    print(json.dumps(audit(),indent=2))
