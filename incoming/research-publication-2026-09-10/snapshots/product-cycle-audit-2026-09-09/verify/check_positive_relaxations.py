"""Reconstruct every base-angle and ordinary-distance condition over rational vectors.
The two vectors are separate relaxations, not a joint Euclidean realization.
"""
from pathlib import Path
from itertools import combinations
from fractions import Fraction as F
import sys,json,argparse
from check_c3 import Geometry,PI

def angle_check(c):
    g=Geometry(c['rows']);vec=list(map(F,c['rational_angle_vector']))
    if len(vec)!=len(g.variables):raise ValueError('wrong angle dimension')
    x=dict(zip(g.variables,vec))
    if x[PI]!=1:raise ValueError('pi gauge')
    def val(row):return sum(F(a)*x[p]for p,a in row.items())
    positive=[];eq=orders=right=0
    for tri in combinations(range(g.n),3):
        a,b,c0=tri;angs=[g.reduced(g.angle(tri,k),False)for k in range(3)]
        vals=list(map(val,angs))
        if min(vals)<=0:raise ValueError('nonpositive base angle')
        positive.extend(vals)
        opp=[g.length[b,c0],g.length[a,c0],g.length[a,b]]
        for u,v in combinations(range(3),2):
            if opp[u]==opp[v]:
                if val(g.premise(['equal_sides',*tri,u,v],True))!=0:raise ValueError('forced equal-side angle')
                eq+=1
            else:
                for p,q in [(u,v),(v,u)]:
                    if (g.owners.get(opp[p]),g.owners.get(opp[q]))in g.less:
                        z=val(g.premise(['angle_order',*tri,p,q],False))
                        if z<=0:raise ValueError('forced angle order')
                        positive.append(z);orders+=1
    for i,row in enumerate(c['rows']):
        for j,h in zip(row[::2],row[1::2]):
            if val(g.premise(['right_angle',i,j,h],True))!=0:raise ValueError('forced right angle')
            right+=1
    return {'triangle_angles_checked':g.n*(g.n-1)*(g.n-2)//2,'equal_side_rows_checked':eq,'strict_side_orders_checked':orders,'right_angles_checked':right,'minimum_positive_value':str(min(positive))}

def metric_check(c):
    rows=c['rows'];g=Geometry(rows);n=g.n;m=g.m;d=c['metric'];reps=[tuple(p)for p in d['representatives']]
    if reps!=sorted(set(g.length.values())):raise ValueError('wrong distance classes')
    vec=list(map(F,d['rational_vector']))
    if len(vec)!=len(reps)or min(vec)<=0 or sum(vec)!=1:raise ValueError('distance positivity/gauge')
    values=dict(zip(reps,vec))
    def dist(a,b):return values[g.length[tuple(sorted((a,b)))]]
    K=[];T=[]
    for a,b,c0,e in combinations(range(n),4):
        v=dist(a,c0)+dist(b,e)-dist(a,b)-dist(c0,e);w=dist(a,c0)+dist(b,e)-dist(a,e)-dist(b,c0)
        if min(v,w)<=0:raise ValueError('Kalmanson violation')
        K.extend([v,w])
    for a,b,c0 in combinations(range(n),3):
        x,y,z=dist(a,b),dist(a,c0),dist(b,c0)
        v=[x+y-z,x+z-y,y+z-x]
        if min(v)<=0:raise ValueError('strict triangle violation')
        T.extend(v)
    radius=[dist(i,i+m)for i in range(m)]
    if any(r>radius[0]for r in radius):raise ValueError('root not maximum')
    for i,j in g.less:
        if not radius[i]<radius[j]:raise ValueError('arrow radius order')
    arcs=0
    for source,row in enumerate(rows):
        W=[j+h*m for j,h in zip(row[::2],row[1::2])]
        for A,Y in [W,W[::-1]]:
            for sign in[-1,1]:
                C=(Y+sign*m)%n
                pos=lambda t:sign*(t-A)%n
                if 0<pos(source)<pos(C)<m:
                    if not radius[C%m]<radius[A%m]:raise ValueError('supplier arc endpoint order')
                    arcs+=1
                    for D in range(n):
                        if pos(C)<pos(D)<m:
                            if not radius[C%m]<radius[D%m]:raise ValueError('supplier arc radial lifting')
                            arcs+=1
    return {'positive_distance_classes':len(vec),'strict_Kalmanson_inequalities':len(K),'minimum_Kalmanson_slack':str(min(K)),'strict_triangle_inequalities':len(T),'minimum_triangle_slack':str(min(T)),'supplier_arc_orders':arcs}

def run(angle_path,metric_path):
    aa=json.loads(Path(angle_path).read_text());bb=json.loads(Path(metric_path).read_text());B={c['index']:c for c in bb};out=[]
    for c in aa:
        d=B[c['index']]
        if c['rows']!=d['rows']:raise ValueError('different witness systems')
        out.append({'index':c['index'],'base_angle':angle_check(c),'ordinary_distance':metric_check(d)})
    return {'status':'PASS_EXACT_RATIONAL_RELAXATION_CONTROLS','cases':out,'joint_Euclidean_realization_claimed':False,'diamond_phase_equations_not_assumed':True}
if __name__=='__main__':
    if sys.flags.optimize:raise ValueError('assertions disabled')
    ap=argparse.ArgumentParser();ap.add_argument('angles');ap.add_argument('metric');ap.add_argument('--output');a=ap.parse_args();r=run(a.angles,a.metric);text=json.dumps(r,indent=2)+'\n'
    if a.output:Path(a.output).write_text(text)
    print(text)
