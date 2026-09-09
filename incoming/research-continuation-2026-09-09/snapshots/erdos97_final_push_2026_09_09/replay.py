"""Reproduce the delivered checks; explicitly report unavailable toolchains."""
from pathlib import Path
import argparse,hashlib,json,platform,shutil,subprocess,sys,tempfile,time
from previous import previous_root,EXPECTED
ROOT=Path(__file__).resolve().parent

def run():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--full-metric',action='store_true')
    p.add_argument('--with-inherited',action='store_true')
    p.add_argument('--output',default='fresh_validation.json')
    args=p.parse_args();records=[]
    tracked=sorted(list(ROOT.rglob('*.py'))+list(ROOT.rglob('*.cpp'))+list((ROOT/'inputs').glob('*.zip')))
    before={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest()for f in tracked}
    def command(argv,cwd=ROOT):
        start=time.monotonic();r=subprocess.run(list(map(str,argv)),cwd=cwd,capture_output=True,text=True)
        item={'command':list(map(str,argv)),'directory':str(cwd.relative_to(ROOT)) if cwd.is_relative_to(ROOT) else 'temporary preceding packet',
              'elapsed_seconds':round(time.monotonic()-start,3),'returncode':r.returncode,
              'stdout':r.stdout,'stderr':r.stderr}
        records.append(item)
        if r.returncode:raise RuntimeError('command failed: '+' '.join(map(str,argv)))
        return r
    result={'schema':'erdos97.final_push.validation.v1','python':platform.python_version(),
      'repository_baseline':'047d05149382e48b602b292df4b8fc9e2da560bb',
      'repository_write':False,'pull_request_opened':False,'repository_wide_ci':False,
      'external_mathematical_review':False,'Lean_formalization':False,
      'full_metric_requested':args.full_metric,'inherited_replay_requested':args.with_inherited,
      'commands':records}
    try:
        command([sys.executable,'grid_metric.py','--check'])
        command([sys.executable,'grid_oracle.py'])
        command([sys.executable,'circle_star_metric.py','--check'])
        command([sys.executable,'circle_star_oracle.py'])
        command([sys.executable,'turn_control.py','--check'])
        command([sys.executable,'audit_medians.py','--check'])
        command([sys.executable,'-m','unittest','-v','test_final_push.py','test_star_extension.py'])
        command([sys.executable,'verify.py','--check'],cwd=ROOT/'parabola')
        command([sys.executable,'-m','unittest','-v','test_parabola.py'],cwd=ROOT/'parabola')
        with tempfile.TemporaryDirectory(prefix='erdos97-final-check-')as t:
            if args.full_metric:
                if not shutil.which('g++'):raise RuntimeError('g++ not found; requested exhaustive C++/GMP check not run')
                binary=Path(t)/'metric'
                command(['g++','-O3','-std=c++17','-Wall','-Wextra','-Werror','check_metric.cpp','-lgmpxx','-lgmp','-o',binary])
                out=command([binary,ROOT/'evidence/grid_metric_integer_matrix.txt'])
                if out.stdout!=(ROOT/'evidence/metric_exhaustive.json').read_text():
                    raise RuntimeError('exhaustive report did not regenerate byte-for-byte')
                result['exhaustive_report_byte_identity']=True
                starbinary=Path(t)/'circle_metric'
                command(['g++','-O3','-std=c++17','-Wall','-Wextra','-Werror','check_circle_metric.cpp','-lgmpxx','-lgmp','-o',starbinary])
                starout=command([starbinary,ROOT/'evidence/circle_star_matrix.txt'])
                if starout.stdout!=(ROOT/'evidence/circle_metric_exhaustive.json').read_text():
                    raise RuntimeError('star metric exhaustive report did not regenerate byte-for-byte')
                result['star_exhaustive_report_byte_identity']=True
            if args.with_inherited:
                outpath=Path(t)/'preceding_replay.json'
                command([sys.executable,'replay.py','--with-inherited','--output',outpath],cwd=previous_root())
                inherited=json.loads(outpath.read_text())
                if inherited.get('status')!='passed':raise RuntimeError('preceding replay did not pass')
                result['preceding_replay']=inherited
        after={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest()for f in tracked}
        if after!=before:raise RuntimeError('source or input archive changed during replay')
        result['source_and_archive_hashes_before_and_after']=before
        result['status']='passed'
    except Exception as e:
        result['status']='failed';result['error']=str(e)
        Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        raise
    Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'],'commands':len(records),'report':args.output},indent=2))
if __name__=='__main__':run()
