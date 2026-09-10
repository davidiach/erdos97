"""Six-point exact negative control for dropping neighbor-rank hypotheses.

Standard-library, no search imports. This is not an all-rich polygon.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import argparse,json
from rational_geometry import inspect

def data():
    return {'kind':'exact_rational_neighbor_rank_negative_control_not_erdos_counterexample',
            'coordinates':[['0','0'],['10/13','0'],['5/13','12/13'],['5/13','-12/13'],['15/17','8/17'],['91/109','60/109']],
            'cyclic_order':[0,3,1,4,5,2],'witness_rows':{'0':[2,3,4,5]},
            'assigned_radius_squared':['1']*6,
            'unrestricted_counterexample':False}

def verify(obj):
    r=inspect(obj);p=[tuple(map(F,z))for z in obj['coordinates']];n=len(p)
    d=[[sum((a-b)**2 for a,b in zip(x,y))for y in p]for x in p]
    edges=[];blockers={}
    for i in range(n):
        for j in range(i+1,n):
            zs=[k for k in range(n)if k not in(i,j)and d[i][k]+d[k][j]<=d[i][j]]
            if not zs:edges.append([i,j])
            blockers[f'{i},{j}']=zs
    short=[[j for j in range(n)if j!=i and d[i][j]<1]for i in range(n)]
    unit=[[j for j in range(n)if j!=i and d[i][j]==1]for i in range(n)]
    if any(not row for row in unit):raise AssertionError('every assigned radius must be actual')
    degree=[sum(i in edge for edge in edges)for i in range(n)]
    if short[0]!=[1] or short[1]!=[0,4,5] or unit[0]!=[2,3,4,5] or degree[0]!=3:raise AssertionError('negative-control property failed')
    r.update(strict_gabriel_edges=edges,strict_gabriel_degrees=degree,closed_disk_blockers=blockers,strictly_unit_short_neighbors=short,unit_distance_classes=unit,local_degree_lifting_without_neighbor_rank_is_false=True,rank_free_assigned_radius_descent_is_false=True,minimum_possible_size_for_this_failure=6)
    return r

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-dir',default='.');p.add_argument('--check',action='store_true');a=p.parse_args();root=Path(a.output_dir);obj=data();r=verify(obj)
    outputs={root/'candidate_counterexamples/neighbor_rank_six_point_negative_control.json':obj,root/'reports/neighbor_rank_six_point_negative_control.json':r}
    for path,value in outputs.items():
        if a.check:
            if json.loads(path.read_text())!=json.loads(json.dumps(value)):raise AssertionError(f'mismatch {path}')
        else:path.write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps({k:v for k,v in r.items()if k not in('all_actual_distance_classes','closed_disk_blockers')},indent=2))
