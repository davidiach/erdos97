"""All-rich metric with exactly realizable convex planar rich stars.

This is NOT a global planar realization. Each selected star has its own local
coordinate chart. The two sorts of labels do not share one coordinate chart.
All arithmetic in generation and checking is rational.
"""
from __future__ import annotations
from fractions import Fraction as F
from itertools import combinations
from collections import defaultdict, Counter
from pathlib import Path
from math import lcm
import json,argparse
import grid_metric
ROOT=Path(__file__).resolve().parent
A=74;B=64;N=A+B;L=1000
EPS=F(1,10**8);ETA=F(1,10**60)

def require(ok,message):
    if not ok:raise ValueError(message)

def point(j):
    a=j+1;den=(L*L+a*a)**2
    return F(L**4-6*L*L*a*a+a**4,den),F(4*L*a*(L*L-a*a),den)

def chord(i,j):
    if i==j:return F(0)
    i,j=sorted((i+1,j+1))
    return F(4*L*(j-i)*(L*L+i*j),(L*L+i*i)*(L*L+j*j))

def determinant(G):
    return (G[0][0]*(G[1][1]*G[2][2]-G[1][2]*G[2][1])
            -G[0][1]*(G[1][0]*G[2][2]-G[1][2]*G[2][0])
            +G[0][2]*(G[1][0]*G[2][1]-G[1][1]*G[2][0]))

def gram(D,labels):
    p,*vs=labels
    G=[[(D[p][i]**2+D[p][j]**2-D[i][j]**2)/2 for j in vs]for i in vs]
    return determinant(G)

def build():
    old,oldrecord=grid_metric.build()
    R=oldrecord['common_witness_radius']
    D=[[F(0)for _ in range(N)]for _ in range(N)]
    for i,j in combinations(range(N),2):
        if (i<A)==(j<A):
            off=0 if i<A else A;v=chord(i-off,j-off)
        else:
            b=old[i][j]-R
            v=F(1) if b==0 else 1+EPS*b+ETA*(i*B+j-A+1)
        D[i][j]=D[j][i]=v
    fibers=[[j for j in range(N)if j!=i and D[i][j]==1]for i in range(N)]
    require(fibers==oldrecord['common_radius_fibers'],'unit incidence changed')
    require(min(map(len,fibers))>=4,'not all rich')
    cross=[D[i][j]for i in range(A)for j in range(A,N)if D[i][j]!=1]
    require(len(cross)==len(set(cross)),'an unwanted cross equality remains')
    for i in range(N):
        other=[D[i][j]for j in range(N)if i!=j and D[i][j]!=1]
        require(len(other)==len(set(other)),'an unwanted row equality remains')
    same=[[chord(i,j)for j in range(A)]for i in range(A)]
    smallest=min(same[i][j]for i,j in combinations(range(A),2))
    largest=max(same[i][j]for i,j in combinations(range(A),2))
    delta=min(same[i][k]-max(same[i][j],same[j][k])for i,j,k in combinations(range(A),3))
    tri=min(same[i][j]+same[j][k]-same[i][k]for i,j,k in combinations(range(A),3))
    perturb=max(abs(v-1)for v in cross)
    rectangles=[D[i][j]+D[i+1][j+1]-D[i][j+1]-D[i+1][j]for i in range(A-1)for j in range(A,N-1)]
    margins={
      'positive_cross':1-perturb,
      'within_diameter_below_half':F(1,2)-largest,
      'mixed_triangle_short':smallest-2*perturb,
      'mixed_triangle_long':2*(1-perturb)-largest,
      'mixed_kalmanson_three_one':delta-2*perturb,
      'mixed_kalmanson_two_two_long':2*(1-perturb)-2*largest,
      'mixed_kalmanson_elementary_rectangle':min(rectangles),
      'mixed_ptolemy_three_one':min(tri,smallest)-3*largest*perturb,
      'mixed_ptolemy_two_two_cross':smallest**2-4*perturb-2*perturb**2,
      'mixed_ptolemy_two_two_within':2*(1-perturb)**2-largest**2,
    }
    require(min(margins.values())>0,'a sufficient strict margin failed')
    signs=0;equalities=0;star_distances=0
    for i,ws in enumerate(fibers):
        off=A if i<A else 0
        labels=[i]+ws;coords=[(F(0),F(0))]+[point(j-off)for j in ws]
        for u,v in combinations(range(len(labels)),2):
            x,y=coords[u];a,b=coords[v]
            require((x-a)**2+(y-b)**2==D[labels[u]][labels[v]]**2,'local star distance mismatch')
            star_distances+=1
        for u in range(len(labels)):
            v=(u+1)%len(labels);x,y=coords[u];a,b=coords[v]
            for z in range(len(labels)):
                if z in (u,v):continue
                c,d=coords[z]
                require((a-x)*(d-y)-(b-y)*(c-x)>0,'local star is not strictly convex in order')
                signs+=1
        for a,b,c,d in combinations(ws,4):
            require(D[a][c]*D[b][d]==D[a][b]*D[c][d]+D[a][d]*D[b][c],'witness circle Ptolemy equality fails')
            equalities+=1
    labels=[0,1,A,A+1];det=gram(D,labels)
    require(det>0,'mixed four-point nonplanarity vanished')
    maxoverlap=0
    for i,j in combinations(range(N),2):
        buckets=Counter((D[i][v],D[j][v])for v in range(N)if v not in (i,j))
        maxoverlap=max(maxoverlap,max(buckets.values()))
    require(maxoverlap==1,'full all-radius pair-overlap condition failed')
    report={
      'schema':'erdos97.locally_planar_rich_star_metric.v1',
      'status':'exact metric with locally convex planar rich stars; NOT a global planar counterexample',
      'n':N,'line_vertices':A,'point_vertices':B,'common_radius':'1',
      'epsilon':str(EPS),'nonincidence_perturbation_eta':str(ETA),
      'nonincidence_perturbation_code':'64*i + (j-74) + 1 for i<74<=j',
      'circle_parameter':'t_j=(j+1)/1000, angle=4*arctan(t_j)',
      'unit_circle_coordinates':[[str(x),str(y)]for x,y in map(point,range(A))],
      'full_unit_fibers':fibers,'degree_histogram':dict(sorted(Counter(map(len,fibers)).items())),
      'no_repeated_nonunit_distance_at_any_vertex':True,
      'all_radius_two_center_max_fiber_intersection':maxoverlap,
      'full_rich_stars_realized_locally':N,'local_star_squared_distance_checks':star_distances,
      'local_star_strict_supporting_signs':signs,'witness_quad_ptolemy_equalities_checked':equalities,
      'exact_margin_bounds':{k:str(v)for k,v in margins.items()},
      'nonplanar_gram_labels':labels,'nonplanar_gram_determinant':str(det),
      'external_review':False,'formalized':False,
    }
    return D,report

def write_matrix(D,path):
    scale=lcm(*(d.denominator for row in D for d in row))
    with path.open('w')as f:
        f.write(f'{N}\n{scale}\n{scale}\n')
        for row in D:f.write(' '.join(str(x.numerator*(scale//x.denominator))for x in row)+'\n')
    return scale.bit_length()

def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--write',action='store_true');args=p.parse_args()
    D,r=build();text=json.dumps(r,indent=2,sort_keys=True)+'\n';target=ROOT/'evidence/circle_star_metric.json'
    if args.check:require(target.read_text()==text,'saved star metric differs')
    if args.write:
        target.write_text(text);print('matrix_scale_bits',write_matrix(D,ROOT/'evidence/circle_star_matrix.txt'))
    print(json.dumps({k:r[k]for k in ['n','degree_histogram','no_repeated_nonunit_distance_at_any_vertex','all_radius_two_center_max_fiber_intersection','full_rich_stars_realized_locally','local_star_squared_distance_checks','local_star_strict_supporting_signs','witness_quad_ptolemy_equalities_checked']},indent=2))
if __name__=='__main__':main()
