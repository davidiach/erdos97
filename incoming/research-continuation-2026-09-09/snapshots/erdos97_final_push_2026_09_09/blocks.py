"""Exact finite controls for the three-small-block obstruction.

The arbitrary-geometry theorem is proved in proofs.md. This program checks
its finite graph bottleneck, and includes an even-cycle positive control.
"""
from itertools import combinations,permutations
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent

def degrees(n,edges):
    out=[0]*n
    for a,b in edges:
        if type(a)is not int or type(b)is not int or not 0<=a<b<n:
            raise ValueError('not a canonical simple edge')
        out[a]+=1;out[b]+=1
    return out

def inversions(p):
    if sorted(p)!=list(range(len(p))):raise ValueError('not a permutation')
    return tuple((i,j)for i,j in combinations(range(len(p)),2)if p[i]>p[j])

def graph_transitive_orientation(n,edges):
    """Natural-order orientation; inversion graphs always pass this test."""
    e=set(edges)
    return all((i,k)in e for i,j,k in combinations(range(n),3)
               if(i,j)in e and(j,k)in e)

def report():
    pairs=list(combinations(range(5),2));regular=[]
    for mask in range(1<<len(pairs)):
        e=tuple(p for k,p in enumerate(pairs)if mask&(1<<k))
        if degrees(5,e)==[2]*5:regular.append(e)
    inv={inversions(p)for p in permutations(range(5))}
    if len(regular)!=12 or any(e in inv for e in regular):
        raise ValueError('five-cycle obstruction failed')
    even=inversions([2,3,0,1])
    if degrees(4,even)!=[2]*4:raise ValueError('even-cycle control failed')
    return {'schema':'erdos97.three_blocks_at_most_five.graph_control.v1',
      'five_vertex_simple_graphs_checked':1024,
      'two_regular_five_vertex_graphs':[[list(x)for x in e]for e in regular],
      'permutation_orders_checked':120,'two_regular_inversion_graphs_on_five_vertices':0,
      'even_cycle_positive_control':{'permutation':[2,3,0,1],'edges':even},
      'scope':'graph bottleneck only; full geometric reduction is in proofs.md'}

if __name__=='__main__':
    r=report();target=ROOT/'evidence/block_certificate.json';target.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    print('1024 graphs; 12 labelled five-cycles; 120 permutation orders; no forbidden overlap')
