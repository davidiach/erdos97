import sys,time,json,argparse
sys.path.insert(0,'/mnt/data/work')
import twofree_probe as G
from csp_twofree import Search
O=G.O

def run(cells,olds,depth=8,node_budget=10000):
 nodes=0;leaves=0;maxd=0;survivors=[];closed=[];start=time.time();stats={}
 def visit(T,U,path,d):
  nonlocal nodes,leaves,maxd
  nodes+=1;maxd=max(maxd,d)
  if nodes>node_budget:raise RuntimeError('node guard')
  c=G.check(T,U,olds);cs=c.get('survivors',[])
  failures=[]
  for j,item in enumerate(cs):
   r=Search(item,cells,olds,100000).run()
   if r['status']!='exhausted':failures.append([j,r]);break
  if not failures:
   leaves+=1;closed.append({'path':path,'depth':d,'method':c['status'],'cliques':len(cs)})
   return
  if d==depth:
   leaves+=1;survivors.append({'path':path,'depth':d,'cases':failures});return
  spans=[max(O.dist(V[i],V[(i+1)%3])for i in range(3))for V in(T,U)]
  which=0 if spans[0]>=spans[1]else 1
  edge,parts=O.split((T,U)[which])
  for j,V in enumerate(parts):
   visit(V if which==0 else T,U if which==0 else V,path+[[which,edge,j]],d+1)
 visit(G.Ts[cells[0]],G.Ts[cells[1]],[],0)
 return {'cells':cells,'olds':olds,'nodes':nodes,'closed_leaves':len(closed),'unresolved_leaves':len(survivors),'max_depth':maxd,'seconds':time.time()-start,'closed':closed,'unresolved':survivors}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--cells',nargs=2,type=int,default=[0,3]);ap.add_argument('--olds',nargs=2,type=int,default=[-1,-1]);ap.add_argument('--depth',type=int,default=8);ap.add_argument('--out',default='/mnt/data/work/refine-report.json');a=ap.parse_args()
 r=run(a.cells,tuple(None if k<0 else k for k in a.olds),a.depth)
 json.dump(r,open(a.out,'w'),indent=2)
 print({k:v for k,v in r.items()if k not in['closed','unresolved']})
