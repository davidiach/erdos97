"""Integrity checking and isolated replay of the delivered research packet."""
from pathlib import Path
import argparse,hashlib,json,platform,subprocess,sys,time
import inherited
ROOT=Path(__file__).resolve().parent


def members():
    return {p.relative_to(ROOT).as_posix():p for p in ROOT.rglob('*')
            if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'
            and p.name!='manifest.json'}


def inventory():
    return {name:{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
            for name,p in sorted(members().items())}


def check_manifest():
    expected=json.loads((ROOT/'manifest.json').read_text())['files']
    actual=inventory()
    if expected!=actual:raise ValueError('packet inventory/hash mismatch; do not overwrite historical evidence')
    if inherited.archive_hash()!=inherited.EXPECTED_ARCHIVE_SHA256:raise ValueError('inherited input changed')
    return actual


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--with-inherited',action='store_true',help='also run both earlier delivered packets')
    p.add_argument('--manifest-only',action='store_true')
    p.add_argument('--checks-only',action='store_true',help='only controls/discrete certificates, not the full one-free replay')
    p.add_argument('--output',type=Path,help='write report outside the immutable packet directory')
    a=p.parse_args()
    if a.output is not None and (a.output.resolve()==ROOT or ROOT in a.output.resolve().parents):
        p.error('--output must be outside the packet directory')
    before=check_manifest();records=[]
    def command(args,directory=ROOT):
        start=time.monotonic()
        done=subprocess.run(args,cwd=directory,capture_output=True,text=True)
        record={'command':args,'directory':'new packet' if directory==ROOT else 'temporary inherited packet',
                'returncode':done.returncode,'elapsed_seconds':round(time.monotonic()-start,3),
                'stdout':done.stdout,'stderr':done.stderr}
        records.append(record)
        if done.returncode:
            raise RuntimeError('replay failed: '+repr(record))
    if not a.manifest_only:
        if not a.checks_only:
            command([sys.executable,'-S','-m','unittest','-v','test_internal_support.py'])
        for script in ('controls.py','kalmanson.py','combinatorics.py'):
            command([sys.executable,'-S',script])
        if a.with_inherited:
            command([sys.executable,'-S','replay.py'],inherited.location())
    after=check_manifest()
    if before!=after:raise AssertionError('replay modified retained inputs')
    report={'status':'passed','mode':'manifest-only' if a.manifest_only else 'checks-only' if a.checks_only else 'full new packet',
        'inherited_full_replay_requested':a.with_inherited and not a.manifest_only,
        'python':platform.python_version(),'manifest_entries_before_and_after':len(before),
        'commands':records,'external_mathematical_review':False,'Lean_formalization':False,
        'repository_wide_ci':False}
    text=json.dumps(report,indent=2,sort_keys=True)+'\n'
    if a.output:a.output.write_text(text)
    print(text)
if __name__=='__main__':main()
