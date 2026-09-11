"""Exact all-distance and global-support reconstruction. No search imports."""
from pathlib import Path
from itertools import combinations
from collections import defaultdict,Counter
import json,argparse,sys
from q3_field import Q3,sub,cross,dot,sqdist

def check(d):
    if sys.flags.optimize:raise ValueError('assertions disabled')
    kinds={'c3_maximum_root_rich_neighborhood_21':21,'supplier_arc_positive_12':12,'convex_product_diamond_positive_12':12}
    if d.get('kind')not in kinds:raise ValueError('unknown control kind')
    P=[tuple(Q3.load(c)for c in p)for p in d['coordinates']];n=len(P);order=d['cyclic_order']
    if n!=kinds[d['kind']]or any(type(i)is not int for i in order):raise ValueError('bad dimensions or indices')
    if sorted(order)!=list(range(n)):raise ValueError('bad order')
    distances={}
    for i,j in combinations(range(n),2):
        t=sqdist(P[i],P[j])
        if t<=0:raise ValueError('coincident points')
        distances[i,j]=t
    signs=[]
    for k,i in enumerate(order):
        j=order[(k+1)%n]
        for l in range(n):
            if l in (i,j):continue
            c=cross(sub(P[j],P[i]),sub(P[l],P[i]))
            if c<=0:raise ValueError(f'failed support {i,j,l}')
            signs.append(c)
    inventory=[];rich=[];maxima=[]
    for i in range(n):
        groups=defaultdict(list)
        for j in range(n):
            if j!=i:groups[distances[tuple(sorted((i,j)))]].append(j)
        inventory.append([{'squared_radius':r.dump(),'witnesses':w}for r,w in sorted(groups.items())])
        maxima.append(max(map(len,groups.values())))
        for r,w in groups.items():
            if len(w)>=4:rich.append({'center':i,'squared_radius':r.dump(),'witnesses':w})
    origin=(Q3(0),Q3(0));norms=[sqdist(p,origin)for p in P]
    # Check C3 structure directly, independent of the coordinate generator.
    S=Q3(0,1)
    for base in range(0,n,3):
        for k in range(3):
            x,y=P[base+k];rot=((-x-S*y)/2,(S*x-y)/2)
            if rot!=P[base+(k+1)%3]:raise ValueError('not a C3 orbit')
    rows=d['own_side_source_rows'];equalities=[]
    expected_arrows={
      'c3_maximum_root_rich_neighborhood_21':[[[1,0],[2,0]],[[3,0],[4,0]],[[5,0],[6,0]],[],[],[],[]],
      'supplier_arc_positive_12':[[],[[0,0],[2,2]],[],[]],
      'convex_product_diamond_positive_12':[[[1,0],[2,0]],[[3,0]],[[3,0]],[]]}
    required=expected_arrows[d['kind']]
    if d.get('own_side_arrows')!=required or rows!=[[j for j,g in a]for a in required]:raise ValueError('named control premises differ')
    for i,row in enumerate(rows):
        if not row:continue
        arrows=d['own_side_arrows'][i]
        if [j for j,g in arrows]!=row or any(type(j)is not int or type(g)is not int or not(0<=j<n//3 and 0<=g<3)for j,g in arrows):raise ValueError('bad explicit arrows')
        gains=[g for j,g in arrows]
        for k in range(3):
            p=3*i+k;W=[3*i+(k+1)%3,3*i+(k+2)%3]+[3*j+(k+g)%3 for j,g in zip(row,gains)]
            if len(set(W))!=len(W)or p in W:raise ValueError('repeated witness')
            if any(distances[tuple(sorted((p,j)))]!=3*norms[p]for j in W):raise ValueError('own-side identity fails')
            equalities.append({'center':p,'witnesses':W,'squared_radius':(3*norms[p]).dump()})
    claims={}
    if d['kind']=='c3_maximum_root_rich_neighborhood_21':
        if any(r>1 for r in norms)or[n for n,r in enumerate(norms)if r==1]!=[0,1,2]:raise ValueError('not maximum root')
        if maxima!=[4]*9+[2]*12:raise ValueError('wrong all-radius inventory')
        if any(Q3.load(c['squared_radius'])>3 for c in rich):raise ValueError('larger actual rich radius')
        if not all(maxima[j]>=4 for j in equalities[0]['witnesses']):raise ValueError('root witness not rich')
        claims={'root_norm_squared':'1','global_maximum_actual_rich_radius_squared':'3','all_root_named_witnesses_rich':True,'only_root_orbit_on_unit_circle':True}
    elif d['kind']=='supplier_arc_positive_12':
        if not norms[6]<norms[9]<norms[0]:raise ValueError('radial lifting/control bounds fail')
        pos={v:(order.index(v)-order.index(0))%n for v in range(n)}
        if not 0<pos[3]<pos[6]<pos[9]<pos[1]:raise ValueError('not the required strict sector order')
        delta=sqdist(P[6],P[10])-3*norms[6]
        if delta<=0:raise ValueError('third arrow not strictly forbidden')
        claims={'strict_C_D_A_norm_order':True,'required_sector_order_checked':True,'radial_gap_D_minus_C':(norms[9]-norms[6]).dump(),'forbidden_third_arrow_squared_gap':delta.dump()}
    else:
        if maxima!=[4]*3+[3]*6+[2]*3:raise ValueError('wrong diamond inventory')
        # Direct product identity in Cartesian complex coordinates.
        A,B=P[3],P[6];C=P[9]
        if (A[0]*B[0]-A[1]*B[1],A[0]*B[1]+A[1]*B[0])!=C:raise ValueError('product identity')
        claims={'genuine_convex_diamond':True,'all_diamonds_forbidden_shortcut_refuted':True}
    return {'status':'PASS_EXACT_GEOMETRY_CONTROL','kind':d['kind'],'points':n,'distinct_pairs':len(distances),'global_support_checks':len(signs),'minimum_support':min(signs).dump(),'all_radius_maximum_multiplicities':maxima,'rich_distance_classes':rich,'full_distance_partitions':inventory,'named_own_side_rows':equalities,'claims':claims,'all_rich':all(v>=4 for v in maxima),'external_review':False}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('input');ap.add_argument('--output');a=ap.parse_args();r=check(json.loads(Path(a.input).read_text()))
    if a.output:Path(a.output).write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({k:v for k,v in r.items()if k not in ['full_distance_partitions','rich_distance_classes','named_own_side_rows']},indent=2))
if __name__=='__main__':main()
