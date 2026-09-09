"""Different-representation audit of the metric's coordinates and integer matrix.

Does not import grid_metric.py. Lines are enumerated by primitive directions,
line equations are obtained from two projectively transformed points, and
nonplanarity is checked with a Cayley--Menger determinant.
"""
from fractions import Fraction as R
from itertools import combinations
from math import gcd
from pathlib import Path
from collections import Counter
import json
ROOT=Path(__file__).resolve().parent

def det_integer(A):
    A=[row[:]for row in A];last=1;sign=1
    for k in range(len(A)-1):
        if A[k][k]==0:
            j=next((j for j in range(k+1,len(A))if A[j][k]),None)
            if j is None:return 0
            A[k],A[j]=A[j],A[k];sign=-sign
        pivot=A[k][k]
        for i in range(k+1,len(A)):
            for j in range(k+1,len(A)):
                v=A[i][j]*pivot-A[i][k]*A[k][j]
                if v%last:raise ValueError('nonexact Bareiss division')
                A[i][j]=v//last
        for i in range(k+1,len(A)):A[i][k]=0
        last=pivot
    return sign*A[-1][-1]

def check(matrix_path=None,certificate_path=None):
    matrix_path=matrix_path or ROOT/'evidence/grid_metric_integer_matrix.txt'
    certificate_path=certificate_path or ROOT/'evidence/grid_metric_certificate.json'
    record=json.loads(Path(certificate_path).read_text());grid=[(x,y)for x in range(8)for y in range(8)]
    line_sets={}
    for u in range(8):
        for v in range(-7,8):
            if not(u>0 or(u==0 and v>0))or gcd(u,v)!=1:continue
            levels={}
            for j,(x,y)in enumerate(grid):levels.setdefault(v*x-u*y,[]).append(j)
            for level,I in levels.items():
                if len(I)<4:continue
                a,b,c=v,-u,-level
                if a<0 or(a==0 and b<0):a,b,c=-a,-b,-c
                line_sets[(a,b,c)]=I
    if len(line_sets)!=74:raise ValueError('wrong line count')
    pts=[(R(x+11*y,1000000+x+97*y),R(y,1000000+x+97*y))for x,y in grid]
    point_order=sorted(range(64),key=lambda j:pts[j][0]);ordered=[]
    for L,I in line_sets.items():
        x,y=pts[I[0]];u,v=pts[I[1]]
        m=(v-y)/(u-x);b=y-m*x
        ordered.append((-m,-b,L))
    ordered.sort()
    if [list(x[2])for x in ordered]!=record['lines_in_vertex_order']or point_order!=record['point_order']:
        raise ValueError('projective order mismatch')
    if [[str(a),str(b)]for a,b,L in ordered]!=record['line_alpha_beta']:
        raise ValueError('line equation mismatch')
    words=Path(matrix_path).read_text().split();n=int(words[0]);scale=int(words[1]);radius=int(words[2]);v=list(map(int,words[3:]))
    if n!=138 or scale<=0 or radius!=781100*scale or len(v)!=n*n:
        raise ValueError('matrix header mismatch')
    d=[v[i*n:(i+1)*n]for i in range(n)];checked=0
    for i in range(n):
        for j in range(n):
            if i==j:expected=R(0)
            elif(i<74)==(j<74):s=abs(j-i);expected=R(566*s-s*s)
            else:
                a,b=sorted((i,j));al,be,L=ordered[a];p=point_order[b-74];x,y=pts[p]
                expected=781100+al*x+be+y
            if d[i][j]*expected.denominator!=scale*expected.numerator:
                raise ValueError(f'distance mismatch at {i},{j}')
            checked+=1
    fibers=[[j for j in range(n)if j!=i and d[i][j]==radius]for i in range(n)]
    if fibers!=record['common_radius_fibers']or min(map(len,fibers))<4:
        raise ValueError('fiber mismatch')
    if [f[:4]for f in fibers]!=record['selected_witness_rows']:
        raise ValueError('selected row mismatch')
    intersections=0
    for i,j in combinations(range(n),2):
        if len(set(fibers[i])&set(fibers[j]))>1:raise ValueError('linear-incidence control failed')
        intersections+=1
    CM=[[0]+[1]*4]+[[1]+[(d[i][j]//scale)**2 for j in range(4)]for i in range(4)]
    cm=det_integer(CM)
    if cm!=8*int(record['nonplanar_gram_determinant'])or cm==0:
        raise ValueError('nonplanarity mismatch')
    return {'status':'passed','matrix_entries_reconstructed':checked,
      'full_radius_fiber_pairs_with_overlap_at_most_one':intersections,
      'cayley_menger_determinant':str(cm),'grid_lines_reconstructed':74,
      'fiber_histogram':dict(sorted(Counter(map(len,fibers)).items())),
      'uses_primary_code':False,'external_review':False}
if __name__=='__main__':
    result=check();(ROOT/'evidence/grid_oracle.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result,indent=2))
