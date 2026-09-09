"""Separate-representation audit of the locally planar rich-star control.

No imports from circle_star_metric or grid_metric. The earlier independent
line-direction oracle validates the incidence input. Circle coordinates use
complex squaring of rational half-angle vectors; distances use determinants
of those vectors. Nonplanarity uses a 5-by-5 Cayley--Menger determinant.
"""
from fractions import Fraction as Q
from pathlib import Path
from itertools import combinations
import json
import grid_oracle
ROOT=Path(__file__).resolve().parent

def matrix(path):
    w=Path(path).read_text().split();n,s,r=map(int,w[:3]);x=list(map(int,w[3:]))
    if n!=138 or s<=0 or len(x)!=n*n:raise ValueError('bad metric matrix')
    return [[Q(v,s)for v in x[i*n:(i+1)*n]]for i in range(n)],Q(r,s)

def half(j):
    t=Q(j+1,1000);return (1-t*t)/(1+t*t),2*t/(1+t*t)

def loc(j):
    a,b=half(j);return a*a-b*b,2*a*b

def det(A):
    A=[[Q(x)for x in row]for row in A];ans=Q(1)
    for k in range(len(A)):
        pivot=next((j for j in range(k,len(A))if A[j][k]),None)
        if pivot is None:return Q(0)
        if pivot!=k:A[k],A[pivot]=A[pivot],A[k];ans=-ans
        d=A[k][k];ans*=d
        for j in range(k,len(A)):A[k][j]/=d
        for i in range(k+1,len(A)):
            d=A[i][k]
            for j in range(k,len(A)):A[i][j]-=d*A[k][j]
    return ans

def check():
    prior=grid_oracle.check();old,_=matrix(ROOT/'evidence/grid_metric_integer_matrix.txt')
    D,radius=matrix(ROOT/'evidence/circle_star_matrix.txt')
    r=json.loads((ROOT/'evidence/circle_star_metric.json').read_text())
    if radius!=1:raise ValueError('incorrect unit radius')
    equalities=0
    for i in range(138):
        for j in range(138):
            if i==j:expected=Q(0)
            elif (i<74)==(j<74):
                off=0 if i<74 else 74;a,b=half(i-off);c,d=half(j-off)
                expected=2*abs(a*d-b*c)
            else:
                u,v=sorted((i,j));perturb=(old[u][v]-781100)/10**8
                expected=1 if perturb==0 else 1+perturb+Q(64*u+v-74+1,10**60)
            if D[i][j]!=expected:raise ValueError(f'incorrect distance {i} {j}')
    fibers=[[j for j in range(138)if i!=j and D[i][j]==1]for i in range(138)]
    if fibers!=r['full_unit_fibers']or min(map(len,fibers))<4:raise ValueError('wrong rich fibers')
    oriented=0;squared=0
    for i,ws in enumerate(fibers):
        off=74 if i<74 else 0;ls=[i]+ws;xy=[(Q(0),Q(0))]+[loc(j-off)for j in ws]
        for u,v in combinations(range(len(ls)),2):
            x,y=xy[u];a,b=xy[v]
            if (x-a)**2+(y-b)**2!=D[ls[u]][ls[v]]**2:raise ValueError('local distance identity failed')
            squared+=1
        for u,v,w in combinations(range(len(ls)),3):
            x,y=xy[u];a,b=xy[v];c,d=xy[w]
            if (a-x)*(d-y)-(b-y)*(c-x)<=0:raise ValueError('strict local orientation failed')
            oriented+=1
        for a,b,c,d in combinations(ws,4):
            if D[a][c]*D[b][d]!=D[a][b]*D[c][d]+D[a][d]*D[b][c]:raise ValueError('circle identity failed')
            equalities+=1
    labels=[0,1,74,75]
    C=[[Q(0)]+[Q(1)]*4]+[[Q(1)]+[D[i][j]**2 for j in labels]for i in labels]
    cm=det(C)
    if cm==0 or cm!=8*Q(r['nonplanar_gram_determinant']):raise ValueError('nonplanarity determinant failed')
    return {'status':'passed','primary_star_code_imported':False,'matrix_entries_reconstructed':138**2,
       'local_stars':138,'local_squared_distance_identities':squared,'strict_local_ordered_triple_orientations':oriented,
       'witness_circle_equalities':equalities,'cayley_menger_determinant':str(cm),
       'prior_input_oracle_status':prior['status'],'global_planar_realization':False,'external_review':False}
if __name__=='__main__':
    r=check();text=json.dumps(r,indent=2,sort_keys=True)+'\n';(ROOT/'evidence/circle_star_oracle.json').write_text(text);print(text,end='')
