"""Full isolated replay with before/after integrity checks.

No network, optimizer, external dependency, or repository checkout is needed.
Prints a JSON execution record. Does not rewrite preserved reports or inputs.
"""
from pathlib import Path
import argparse
import hashlib
import json
import platform
import subprocess
import sys
import tempfile
import time
import zipfile

if sys.flags.optimize:
    raise RuntimeError('Run exact checks without Python -O or -OO')

ROOT = Path(__file__).resolve().parent


def manifest_check(root):
    count = 0
    for line in (root/'MANIFEST.sha256').read_text().splitlines():
        digest, name = line.split('  ', 1)
        path = (root/name).resolve()
        if root.resolve() not in path.parents:
            raise ValueError('unsafe manifest path')
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise AssertionError('hash mismatch: '+name)
        count += 1
    return count


def execute(args, cwd):
    start = time.monotonic()
    process = subprocess.run(args,cwd=cwd,text=True,capture_output=True,check=False)
    result = {'command':args,'directory':'new packet' if cwd == ROOT else 'temporary inherited packet',
              'returncode':process.returncode,'elapsed_seconds':round(time.monotonic()-start,3),
              'stdout':process.stdout,'stderr':process.stderr}
    if process.returncode != 0:
        print(json.dumps(result,indent=2),file=sys.stderr)
        raise RuntimeError('replay command failed')
    return result


def run(manifest_only=False):
    before = manifest_check(ROOT)
    if manifest_only:
        return {'status':'manifest passed','entries':before}
    commands = []
    for command in ([sys.executable,'verify.py'],[sys.executable,'oracle.py'],
                    [sys.executable,'-m','unittest','-v','test_closure.py'],
                    [sys.executable,'exploratory/one_free_relaxation.py']):
        commands.append(execute(command,ROOT))
    with tempfile.TemporaryDirectory(prefix='erdos97-prior-replay-') as directory:
        tmp = Path(directory).resolve()
        with zipfile.ZipFile(ROOT/'inputs/previous_packet.zip') as archive:
            for item in archive.infolist():
                target = (tmp/item.filename).resolve()
                if tmp not in target.parents:
                    raise ValueError('unsafe archive path')
            archive.extractall(tmp)
        prior = tmp/'erdos97_codesign_packet_2026_09_08'
        inherited_before = manifest_check(prior)
        for command in ([sys.executable,'verify.py'],[sys.executable,'oracle.py'],
                        [sys.executable,'-m','unittest','-v','test_research.py']):
            commands.append(execute(command,prior))
        inherited_after = manifest_check(prior)
        assert inherited_before == inherited_after
    after = manifest_check(ROOT)
    assert before == after
    return {'status':'passed','python':platform.python_version(),'platform':platform.platform(),
            'new_manifest_entries_before_and_after':before,
            'inherited_manifest_entries_before_and_after':inherited_before,
            'new_test_count':30,'inherited_test_count':31,'commands':commands,
            'repository_wide_ci':False,'external_mathematical_review':False,'Lean_formalization':False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest-only',action='store_true')
    args = parser.parse_args()
    print(json.dumps(run(args.manifest_only),indent=2,sort_keys=True))
