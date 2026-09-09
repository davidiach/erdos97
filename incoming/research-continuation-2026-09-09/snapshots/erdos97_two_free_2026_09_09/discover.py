"""Optional fresh exact partition discovery for one two-free support case.

A search/depth guard produces an explicitly UNRESOLVED domain, never a proof.
The delivered certificate is instead reconstructed by build_certificate.py
from the retained historical partitions and checked by both full replayers.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import geometry as G
from row_search import Search


def discover(cells, old, max_depth=36, max_nodes=100000):
    if len(cells)!=2 or any(type(x)is not int or not 0<=x<9 for x in cells):
        raise ValueError('Invalid cells')
    if len(old)!=2 or any(x is not None and (type(x)is not int or not 0<=x<9)for x in old):
        raise ValueError('Invalid old witnesses')
    counters=dict(nodes=0,leaves=0,maximum_depth=0,unresolved=0)
    def visit(first,second,depth):
        counters['nodes']+=1
        counters['maximum_depth']=max(counters['maximum_depth'],depth)
        if counters['nodes']>max_nodes:
            counters['unresolved']+=1
            return {'UNRESOLVED':'partition node guard'}
        assignments=[]
        for model in G.models(first,second,cells,old):
            result=Search(model,node_limit=1000000).run()
            if result['status']!='exhausted':assignments.append(result);break
        if not assignments:
            counters['leaves']+=1
            return None
        if depth>=max_depth:
            counters['unresolved']+=1
            return {'UNRESOLVED':'depth guard','necessary_row_assignment':assignments[0]}
        spans=[max(G.O.dist(T[k],T[(k+1)%3])for k in range(3))for T in(first,second)]
        coordinate=0 if spans[0]>=spans[1]else 1
        T=(first,second)[coordinate]
        edge=max(range(3),key=lambda k:G.O.dist(T[k],T[(k+1)%3]))
        children=[]
        for part in G.split(T,edge):
            children.append(visit(part if coordinate==0 else first,second if coordinate==0 else part,depth+1))
        return dict(coordinate=coordinate,edge=edge,children=children)
    T=G.context()[4]
    tree=visit(T[cells[0]],T[cells[1]],0)
    return dict(status='closed'if not counters['unresolved']else'unresolved',
                cells=cells,old_witnesses=old,statistics=counters,tree=tree,
                not_an_unrestricted_solution=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cells',type=int,nargs=2,required=True)
    p.add_argument('--old',type=int,nargs=2,default=[-1,-1])
    p.add_argument('--depth',type=int,default=36)
    p.add_argument('--nodes',type=int,default=100000)
    p.add_argument('--output',type=Path)
    a=p.parse_args();result=discover(a.cells,[None if v==-1 else v for v in a.old],a.depth,a.nodes)
    text=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if a.output:a.output.write_text(text)
    print(text)
