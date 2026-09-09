import sys,itertools,time,json,collections,argparse
sys.path.insert(0,'/mnt/data/work')
from refine_twofree import run
ap=argparse.ArgumentParser();ap.add_argument('--output',default='/mnt/data/work/twofree-sweep.jsonl');ap.add_argument('--depth',type=int,default=20);a=ap.parse_args()
start=time.time();done=set()
try:
 for line in open(a.output):
  x=json.loads(line);done.add(tuple(x['cells']+x['olds']))
except FileNotFoundError:pass
with open(a.output,'a',buffering=1) as out:
 count=0
 for c,d in itertools.combinations_with_replacement(range(9),2):
  for oldf,oldg in itertools.product([None]+list(range(9)),repeat=2):
   if (c,d,oldf,oldg)in done:continue
   try:r=run([c,d],(oldf,oldg),a.depth,50000)
   except Exception as e:r={'cells':[c,d],'olds':[oldf,oldg],'error':repr(e)}
   out.write(json.dumps(r)+'\n');count+=1
   print(count,[c,d,oldf,oldg],{k:v for k,v in r.items()if k not in['cells','olds','closed','unresolved']},'elapsed',round(time.time()-start,2),flush=True)
