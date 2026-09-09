"""Execute this packet's checks and record actual command evidence.
The arbitrary-real proof remains a written argument, not code verification.
"""
from pathlib import Path
import argparse,hashlib,json,platform,re,subprocess,sys,time
import sympy
ROOT=Path(__file__).resolve().parent

def run(output:Path):
    commands=[['verify.py','--check'],['oracle.py','--check'],['cap_pair_probe.py','--check'],
              ['-m','unittest','-v','test_mixed_lens.py'],
              ['-m','py_compile','exact.py','verify.py','oracle.py','cap_pair_probe.py','select_good.py','test_mixed_lens.py','check_manifest.py']]
    records=[];test_count=None
    for i,argv in enumerate(commands):
        command=[sys.executable,*argv];start=time.perf_counter()
        r=subprocess.run(command,cwd=ROOT,text=True,capture_output=True,timeout=180,check=False)
        out=ROOT/f'data/check_{i+1}.stdout';err=ROOT/f'data/check_{i+1}.stderr'
        out.write_text(r.stdout);err.write_text(r.stderr)
        found=re.search(r'Ran (\d+) tests',r.stderr)
        if found:test_count=int(found.group(1))
        records.append(dict(command=command,returncode=r.returncode,elapsed_seconds=round(time.perf_counter()-start,4),
                            stdout=str(out.relative_to(ROOT)),stderr=str(err.relative_to(ROOT)),
                            stdout_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),stderr_sha256=hashlib.sha256(err.read_bytes()).hexdigest()))
    v=json.loads((ROOT/'data/verification.json').read_text());o=json.loads((ROOT/'data/oracle.json').read_text());p=json.loads((ROOT/'data/cap_pair_probe.json').read_text())
    d=dict(schema='erdos97.mixed_lens_validation.v1',status='passed'if all(r['returncode']==0 for r in records)else'failed',
           research_date='2026-09-09',commands=records,tests_passed=test_count,
           environment=dict(python=sys.version,sympy=sympy.__version__,platform=platform.platform()),
           exact_level_count_cases=v['grid_case_count'],universal_symbolic_identity_checks=o['universal_symbolic_identities'],
           algebraic_controls=len(v['controls']),control_support_signs=v['control_support_count'],
           cap_probe_cases=p['cases'],cap_probe_survivors=sum(x['survived']for x in p['counts'].values()),
           independent_external_review=False,formalized=False,repository_writes=False,pr_opened=False,
           repository_wide_ci_run=False,inherited_full_test_suite_run=False,
           mathematical_scope='all-size symmetric parabolic-lens theorem only; written proof in proof.md',
           not_an_unrestricted_solution=True)
    output.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in d.items()if k not in ('commands','environment')},indent=2))
    if d['status']!='passed':raise SystemExit(1)

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();run(a.output.resolve())
if __name__=='__main__':main()
