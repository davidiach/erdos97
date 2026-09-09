import sys,json,numpy as np
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
# Import only the definition portion to avoid executing old scans.
s=Path(__file__).with_name('lens_probe.py').read_text().split('bad=[]')[0]
ns={};exec(s,ns);run_min=ns['run']
s=Path(__file__).with_name('lens_max_probe.py').read_text().split('bad=[]')[0]
ns={};exec(s,ns);run_max=ns['run']
rows=[]
for H in np.linspace(.5,3.4,117):
 b=np.sqrt(H/2);mi=[];ma=[]
 for f in np.linspace(0,.999,161):
  c=float(b*f)
  n,d=run_min(b,c)
  if n>=4:mi.append((c,d))
  n,d=run_max(b,c)
  if n>=4:ma.append((c,d))
 rows.append(dict(H=float(H),min_bad_count=len(mi),max_bad_count=len(ma),min_example=mi[:1],max_example=ma[:1]))
 print(round(H,4),len(mi),len(ma),flush=True)
Path(__file__).with_suffix('.json').write_text(json.dumps({'status':'floating exploratory only; critical levels may merge roots','rows':rows},indent=2))
