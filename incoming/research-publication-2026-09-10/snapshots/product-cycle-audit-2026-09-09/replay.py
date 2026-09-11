"""Run exact checks in a temporary copy, with no optimizer or network access.
Does not rerun bounded numerical searches or establish exhaustive nine-orbit coverage.
"""
from pathlib import Path
import argparse,hashlib,json,os,platform,shutil,subprocess,sys,tempfile,time
ROOT=Path(__file__).resolve().parent

def hashes(root):
    return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((root/'inputs').glob('*'))if p.is_file()}

def run():
    if sys.flags.optimize:raise ValueError('Do not use -O')
    before=hashes(ROOT);records=[];env=dict(os.environ)
    env.pop('PYTHONOPTIMIZE',None);env['PYTHONDONTWRITEBYTECODE']='1';env['PYTHONIOENCODING']='utf-8'
    with tempfile.TemporaryDirectory(prefix='erdos97-phase-replay-')as folder:
        work=Path(folder)/'packet';shutil.copytree(ROOT,work,ignore=shutil.ignore_patterns('__pycache__','.pytest_cache'))
        commands=[['verify/check_combined.py','reports/all_fixed_system_certificates.json'],
          ['verify/check_positive_relaxations.py','reports/angle_survivor_preflight.json','reports/full_metric_preflight.json'],
          ['verify/check_geometry.py','candidate_counterexamples/c3_maximum_root_rich_neighborhood_21.json'],
          ['verify/check_geometry.py','candidate_counterexamples/supplier_arc_positive_12.json'],
          ['verify/check_geometry.py','candidate_counterexamples/convex_product_diamond_positive_12.json'],
          ['verify/check_six_cycle.py','candidate_counterexamples/upper_six_cycle_exact_nonconvex_18.json'],
          ['verify/diamond_free_incidence.py'],
          ['verify/check_phase_filter.py'],
          ['-m','unittest','-v','test_product_cycle_audit_20260909.py'],
          ['publication_core/verify.py'],
          ['-m','unittest','discover','-s','publication_core','-p','test_diamond_phase_obstruction_20260909.py','-v']]
        for cmd in commands:
            start=time.monotonic();p=subprocess.run([sys.executable,'-S',*cmd],cwd=work,env=env,capture_output=True,text=True,encoding='utf-8',timeout=60)
            records.append({'command':['python','-S',*cmd],'returncode':p.returncode,'seconds':time.monotonic()-start,'stdout':p.stdout,'stderr':p.stderr})
            if p.returncode:raise RuntimeError(p.stderr)
        if hashes(work)!=before:raise ValueError('immutable input bytes changed')
    if hashes(ROOT)!=before:raise ValueError('original input bytes changed')
    return {'status':'PASS_SCOPED_EXACT_REPLAY','python':platform.python_version(),'commands':records,'immutable_input_sha256':before,
       'defensive_tests':38,'publication_core_tests':12,'fixed_system_certificates':333,'exact_geometry_controls':4,
       'all_nine_orbit_systems_exhausted':False,'repository_wide_gates_run':False,'external_review':False,'unrestricted_solution':False}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path);args=ap.parse_args();r=run()
    if args.output:args.output.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({k:v for k,v in r.items()if k!='commands'},indent=2))
