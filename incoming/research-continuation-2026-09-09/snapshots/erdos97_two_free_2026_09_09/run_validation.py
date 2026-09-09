"""Record actual commands, return codes, and frozen-source hashes for this packet."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import prior

ROOT=Path(__file__).resolve().parent


def sources():
    return {p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(ROOT.glob('*.py'))}


def command(name,args,cwd=ROOT):
    output=ROOT/'data'/f'validation_{name}.stdout.txt'
    error=ROOT/'data'/f'validation_{name}.stderr.txt'
    started=time.monotonic()
    with output.open('w')as out,error.open('w')as err:
        result=subprocess.run(args,cwd=cwd,stdout=out,stderr=err)
    return dict(name=name,command=args,working_directory='packet'if cwd==ROOT else'hash-bound inherited packet',
                returncode=result.returncode,elapsed_seconds=round(time.monotonic()-started,3),
                stdout=output.relative_to(ROOT).as_posix(),stderr=error.relative_to(ROOT).as_posix())


def main():
    before=sources();archive_before=prior.archive_hash()
    jobs=[('primary',[sys.executable,'-S','verify.py','--check']),
          ('independent',[sys.executable,'-S','oracle_parallel.py','--jobs','4','--check'])]
    records=[]
    with ThreadPoolExecutor(max_workers=2)as executor:
        futures=[executor.submit(command,name,args)for name,args in jobs]
        for future in futures:records.append(future.result())
    commands=[('partition_generator',[sys.executable,'-S','build_certificate.py','--check']),
              ('last_leaf_cancellations',[sys.executable,'-S','last_leaf_audit.py','--check']),
              ('sharpness',[sys.executable,'-S','sharpness.py','--check']),
              ('sharpness_independent',[sys.executable,'-S','audit_sharpness.py','--check']),
              ('new_tests',[sys.executable,'-S','-m','unittest','-v','test_two_free.py'])]
    for name,args in commands:records.append(command(name,args))
    inherited=prior.location()
    records.append(command('inherited',[sys.executable,'-S','replay.py','--with-inherited',
                           '--output',str(ROOT/'data/inherited_replay.json')],inherited))
    after=sources();archive_after=prior.archive_hash()
    passed=all(record['returncode']==0 for record in records)and before==after and archive_before==archive_after
    report=dict(status='passed'if passed else'FAILED',python=platform.python_version(),commands=records,
                source_hashes_before=before,source_hashes_after=after,mathematical_sources_unchanged=before==after,
                input_archive_before=archive_before,input_archive_after=archive_after,
                repository_baseline='047d05149382e48b602b292df4b8fc9e2da560bb',repository_write_performed=False,
                pull_request_opened=False,repository_wide_ci_performed=False,
                external_mathematical_review=False,lean_formalization=False,unrestricted_solution_claimed=False)
    (ROOT/'validation.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'commands':[(r['name'],r['returncode'])for r in records]},indent=2))
    if not passed:raise SystemExit(1)


if __name__=='__main__':main()
