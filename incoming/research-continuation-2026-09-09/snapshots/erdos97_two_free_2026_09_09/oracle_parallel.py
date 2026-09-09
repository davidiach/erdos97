"""Replay the independent checker in disjoint, explicitly covered case ranges.

This is execution plumbing only: each worker runs oracle.py itself. The
combined mathematical report must equal a complete sequential replay report.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parent
SUM_FIELDS={'cases','partition_nodes','leaves','row_models','row_search_nodes',
            'metric_zero_rejections','metric_inverse_rejections'}
MAX_FIELDS={'maximum_depth','largest_sign_enclosure_bits'}


def run(jobs=4,write=False,check=False):
    if type(jobs)is not int or not 1<=jobs<=16:raise ValueError('Use one through sixteen workers')
    destination=ROOT/'data/oracle_shards';destination.mkdir(exist_ok=True)
    tasks=[]
    for i in range(jobs):
        start=4500*i//jobs;stop=4500*(i+1)//jobs
        out=destination/f'{i:02d}.json';err=destination/f'{i:02d}.stderr.txt'
        command=[sys.executable,'oracle.py','--cases',*map(str,range(start,stop))]
        stdout=out.open('w');stderr=err.open('w')
        process=subprocess.Popen(command,cwd=ROOT,stdout=stdout,stderr=stderr)
        tasks.append((start,stop,out,err,process,stdout,stderr))
    records=[];reports=[]
    for start,stop,out,err,process,stdout,stderr in tasks:
        code=process.wait();stdout.close();stderr.close()
        records.append(dict(first_case=start,stop_case=stop,returncode=code,
                            stdout=out.relative_to(ROOT).as_posix(),stderr=err.relative_to(ROOT).as_posix()))
        if code:raise RuntimeError(f'Independent worker [{start},{stop}) failed: {err.read_text()}')
        report=json.loads(out.read_text())
        if report['status']!='passed' or report['cases']!=stop-start:raise ValueError('Incomplete worker result')
        reports.append(report)
    # Ranges were generated as a disjoint partition; check rather than infer it.
    coverage=[i for record in records for i in range(record['first_case'],record['stop_case'])]
    if coverage!=list(range(4500)):raise ValueError('Worker coverage is not complete and disjoint')
    combined={}
    if any(set(report)!=set(reports[0])for report in reports):raise ValueError('Worker schema mismatch')
    for key in reports[0]:
        values=[report[key]for report in reports]
        if key in SUM_FIELDS:combined[key]=sum(values)
        elif key in MAX_FIELDS:combined[key]=max(values)
        elif any(v!=values[0]for v in values):raise ValueError(f'Inconsistent worker field {key}')
        else:combined[key]=values[0]
    text=json.dumps(combined,indent=2,sort_keys=True)+'\n'
    path=ROOT/'data/oracle_report.json'
    if check and path.read_text()!=text:raise ValueError('Parallel and full sequential reports differ')
    if write:path.write_text(text)
    (destination/'execution.json').write_text(json.dumps(dict(status='passed',jobs=jobs,cases=4500,
         complete_disjoint_coverage=True,workers=records,combined_sha256=hashlib.sha256(text.encode()).hexdigest()),indent=2,sort_keys=True)+'\n')
    return combined


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--jobs',type=int,default=4)
    ap.add_argument('--write',action='store_true');ap.add_argument('--check',action='store_true');a=ap.parse_args()
    print(json.dumps(run(a.jobs,a.write,a.check),indent=2,sort_keys=True))
