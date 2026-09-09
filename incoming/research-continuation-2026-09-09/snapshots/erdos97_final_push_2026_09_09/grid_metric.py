"""An exact all-rich strict Kalmanson/Ptolemy metric, not planar Euclidean.

Standard-library construction and exact bound certificate. The companion C++
checker tests every triangle and every quadrilateral after one integer scaling.
No geometric realization of this metric is claimed.
"""
from __future__ import annotations
from fractions import Fraction as F
from itertools import combinations
from functools import reduce
from math import gcd, lcm
from pathlib import Path
from collections import Counter
import argparse
import json

ROOT=Path(__file__).resolve().parent
M=10**6
NGRID=8

def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)

def primitive(a: int,b: int,c: int) -> tuple[int,int,int]:
    g=reduce(gcd,(a,b,c))
    require(g!=0,'zero line')
    a,b,c=a//g,b//g,c//g
    if a<0 or (a==0 and b<0):a,b,c=-a,-b,-c
    return a,b,c

def incidence_configuration():
    points=[(x,y)for x in range(NGRID)for y in range(NGRID)]
    lines=set()
    for (x,y),(u,v) in combinations(points,2):
        lines.add(primitive(y-v,u-x,x*v-u*y))
    lines=[L for L in sorted(lines) if sum(L[0]*x+L[1]*y+L[2]==0 for x,y in points)>=4]
    require(len(points)==64 and len(lines)==74,'wrong incidence configuration size')
    require(min(sum(a*x+b*y+c==0 for a,b,c in lines)for x,y in points)>=4,'under-supported point')
    return points,lines

def build():
    points,lines=incidence_configuration()
    coords=[(F(x+11*y,M+x+97*y),F(y,M+x+97*y))for x,y in points]
    require(len(set(x for x,y in coords))==64,'point projections collide')
    po=sorted(range(64),key=lambda j:coords[j][0])
    parameters=[]
    for a,b,c in lines:
        u=M*a-c;v=M*(b-11*a)-86*c
        require(v!=0,'vertical transformed line')
        parameters.append((F(u,v),F(c,v),(a,b,c)))
    parameters.sort()
    require(len({a for a,b,L in parameters})==74,'line slopes collide')
    B=[[al*coords[j][0]+be+coords[j][1]for j in po]for al,be,L in parameters]
    for i,(_,_,L)in enumerate(parameters):
        for k,j in enumerate(po):
            x,y=points[j]
            require((B[i][k]==0)==(L[0]*x+L[1]*y+L[2]==0),'incidence translation failure')
    U=max(abs(v)for row in B for v in row)
    n=138;na=74;K=566;R=781100
    f=lambda s:K*s-s*s
    D=[[F(0)for _ in range(n)]for _ in range(n)]
    for i,j in combinations(range(n),2):
        d=F(f(j-i))if(i<na)==(j<na)else R+B[i][j-na]
        D[i][j]=D[j][i]=d
    fibers=[[j for j in range(n)if j!=i and D[i][j]==R]for i in range(n)]
    require(min(map(len,fibers))>=4,'not all-rich')
    bounds={
        'within_monotonicity':F(K-2*n),
        'cross_positivity':R-U,
        'triangle_short_side':K-1-2*U,
        'triangle_long_sides':2*(R-U)-K*n,
        'kalmanson_three_one':K-2*n-2*U,
        'kalmanson_two_two_noncrossing':2*(R-U)-2*K*n,
        'ptolemy_three_one':2*R-3*K*n*U,
        'ptolemy_two_two_cross_products':F((K-1)**2)-4*R*U-2*U*U,
        'ptolemy_two_two_within_product':2*(R-U)**2-(K*n)**2,
    }
    require(min(bounds.values())>0,'insufficient analytic margin')
    elementary=[]
    for i in range(n):
        for j in range(i+1,n):
            a,b,c,d=i,(i+1)%n,j,(j+1)%n
            if len({a,b,c,d})==4:
                elementary.append(D[a][c]+D[b][d]-D[a][d]-D[b][c])
    require(min(elementary)>0,'elementary strict Kalmanson failure')
    # Gram of three difference vectors; a planar realization has determinant 0.
    G=[[ (D[0][i]**2+D[0][j]**2-D[i][j]**2)/2 for j in (1,2,3)]for i in (1,2,3)]
    det=(G[0][0]*(G[1][1]*G[2][2]-G[1][2]*G[2][1])
         -G[0][1]*(G[1][0]*G[2][2]-G[1][2]*G[2][0])
         +G[0][2]*(G[1][0]*G[2][1]-G[1][1]*G[2][0]))
    require(det==4*(K-3)**2*(3*K-4)*(5*K-12)>0,'wrong nonplanarity certificate')
    report={
        'schema':'erdos97.all_rich_non_euclidean_metric.v1',
        'status':'exact metric control; not a planar point-set counterexample',
        'n':n,'line_vertices':74,'point_vertices':64,
        'common_witness_radius':R,'within_distance_formula':'566*s - s*s',
        'projectivity':[[1,11,0],[0,1,0],[1,97,M]],
        'old_grid':points,'point_order':po,
        'lines_in_vertex_order':[L for al,be,L in parameters],
        'line_alpha_beta':[[str(al),str(be)]for al,be,L in parameters],
        'cross_perturbation_bound':str(U),
        'common_radius_fibers':fibers,
        'fiber_size_histogram':dict(sorted(Counter(map(len,fibers)).items())),
        'selected_witness_rows':[f[:4]for f in fibers],
        'margin_bounds':{k:str(v)for k,v in bounds.items()},
        'strict_elementary_kalmanson_checks':len(elementary),
        'minimum_elementary_kalmanson_margin':str(min(elementary)),
        'nonplanar_gram_vertices':[0,1,2,3],
        'nonplanar_gram_determinant':str(det),
        'external_review':False,'formalized':False,
    }
    return D,report

def write_integer_matrix(D,report,path: Path):
    scale=lcm(*(x.denominator for row in D for x in row))
    with path.open('w')as f:
        f.write(f'{len(D)}\n{scale}\n{report["common_witness_radius"]*scale}\n')
        for row in D:
            f.write(' '.join(str(x.numerator*(scale//x.denominator))for x in row)+'\n')
    return {'scale_bits':scale.bit_length(),'matrix_path':path.name}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check',action='store_true')
    p.add_argument('--write',action='store_true')
    args=p.parse_args();D,report=build()
    target=ROOT/'evidence/grid_metric_certificate.json'
    text=json.dumps(report,indent=2,sort_keys=True)+'\n'
    if args.check:
        require(target.read_text()==text,'saved certificate differs')
    if args.write:
        target.write_text(text)
        extra=write_integer_matrix(D,report,ROOT/'evidence/grid_metric_integer_matrix.txt')
        print(json.dumps(extra))
    print(json.dumps({k:report[k]for k in ('n','fiber_size_histogram','nonplanar_gram_determinant','margin_bounds')},indent=2))
if __name__=='__main__':main()
