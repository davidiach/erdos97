"""Record a bounded phase-filtered run, including every kind of early exit."""
from pathlib import Path
import argparse,subprocess,json,time,hashlib
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--binary',type=Path,required=True);p.add_argument('--limit',type=int,default=2000000);p.add_argument('--seconds',type=float,default=30);p.add_argument('--slice',type=int,default=-1);p.add_argument('--name',default='phase_2m');a=p.parse_args()
if a.limit<1 or a.seconds<=0:raise SystemExit('positive limits required')
base=ROOT/'reports'/a.name;out=base.with_suffix('.jsonl')
cmd=[str(a.binary),'--all','--limit',str(a.limit),'--output',str(out)]
if a.slice>=0:cmd+=['--slice',str(a.slice)]
t=time.monotonic();timed=False
with base.with_suffix('.stdout').open('w')as so,base.with_suffix('.stderr').open('w')as se:
 try:r=subprocess.run(cmd,stdout=so,stderr=se,text=True,timeout=a.seconds);code=r.returncode
 except subprocess.TimeoutExpired:timed=True;code=None
text=base.with_suffix('.stdout').read_text();lines=out.read_text().splitlines()if out.exists()else[]
rows=[];partial=False
for line in lines:
 try:rows.append(json.loads(line))
 except json.JSONDecodeError:partial=True
r={'command':cmd,'source_sha256':hashlib.sha256((ROOT/'search/nine_with_phase.cpp').read_bytes()).hexdigest(),'returncode':code,'external_timeout':timed,'elapsed_seconds':time.monotonic()-t,'timeout_seconds':a.seconds,'saved_complete_rows':len(rows),'truncated_output_line':partial,'exhausted':False,'scope':'bounded necessary-condition search; no mathematical exclusion from a guard'}
if not timed and text.strip():r['search_report']=json.loads(text);r['exhausted']=r['search_report']['exhausted']
base.with_suffix('.json').write_text(json.dumps(r,indent=2)+'\n');Path(str(base)+'_systems.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(r,indent=2))
