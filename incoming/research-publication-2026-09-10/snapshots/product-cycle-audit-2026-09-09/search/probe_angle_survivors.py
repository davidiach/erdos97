from pathlib import Path
import json,sys,time
from fractions import Fraction as F
from c3_model import margin
ROOT=Path(__file__).resolve().parents[1]

def radial(rows,arc=False):
    m=len(rows);n=3*m;edges={(i,0):{'kind':'maximum_root','source':i}for i in range(1,m)}
    for i,row in enumerate(rows):
        for j,g in zip(row[::2],row[1::2]):
            d=(j+g*m-i)%n
            a,b=(j,i)if m<d<2*m else(i,j)
            edges[a,b]={'kind':'arrow','source':i,'target':j,'gain':g}
        if not arc:continue
        W=[j+g*m for j,g in zip(row[::2],row[1::2])]
        for A,Y in [W,W[::-1]]:
            for s in [-1,1]:
                C=(Y+s*m)%n
                pos=lambda x:(s*(x-A))%n
                if 0<pos(i)<pos(C)<m:
                    edges[C%m,A%m]={'kind':'supplier_arc','physical':[A,i,C],'sign':s,'norm_edge':[C%m,A%m]}
                    for D in range(n):
                        if pos(C)<pos(D)<m:edges[C%m,D%m]={'kind':'supplier_arc','physical':[A,i,C,D],'sign':s,'norm_edge':[C%m,D%m]}
    reach=[[None]*m for _ in range(m)]
    for (a,b),why in edges.items():reach[a][b]=[a,b]
    for k in range(m):
        for i in range(m):
            for j in range(m):
                if reach[i][j]is None and reach[i][k]and reach[k][j]:reach[i][j]=reach[i][k]+reach[k][j][1:]
    cycle=next((reach[i][i]for i in range(m)if reach[i][i]),None)
    return {'cycle':cycle,'premises':[edges[a,b]for a,b in zip(cycle,cycle[1:])]if cycle else[],'edges':[[a,b,why]for(a,b),why in edges.items()]}

def main():
    inp=json.loads((ROOT/'reports/angle_potential_survivors.json').read_text());out=[]
    for c in inp:
        start=time.monotonic();r,mod=margin(c['rows'],time_limit=5,presolve=False)
        q={'index':c['index'],'rows':c['rows'],'solver_status':int(r.status),'message':r.message,'seconds':time.monotonic()-start,
           'basic_radial':radial(c['rows']),'arc_radial':radial(c['rows'],True)}
        if r.success:
            A,E,al,el=mod;v=[F(float(x)).limit_denominator(1000000)for x in r.x[:-1]]
            strict=[sum(int(x)*y for x,y in zip(row,v))for row in A]
            eq=[sum(int(x)*y for x,y in zip(row,v))for row in E]
            q.update({'numerical_margin':float(r.x[-1]),'rational_angle_vector':[str(x)for x in v],
                      'exact_equality_check':not any(eq),'minimum_rational_strict_margin':str(min(strict)),
                      'exact_positive_model':not any(eq)and min(strict)>0})
        out.append(q);(ROOT/'reports/angle_survivor_preflight.json').write_text(json.dumps(out,indent=2)+'\n')
        print(q['index'],q.get('numerical_margin'),q.get('exact_positive_model'),q['basic_radial']['cycle'],q['arc_radial']['cycle'],flush=True)
if __name__=='__main__':main()
