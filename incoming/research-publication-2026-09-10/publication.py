"""Verify preserved research bytes and replay exact evidence in isolated copies.

No accepted mathematical status changes. Historical numerical searches are not
rerun. The two-star catalogue's enumeration completeness is not certified here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def canonical_json(value):
    return json.loads(json.dumps(value))


def write_report(path, report):
    path = Path(path)
    require('snapshots' not in path.resolve().parts, 'Do not write reports into immutable snapshots')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')


def check_integrity(root=ROOT):
    root = Path(root)
    manifest = load(root / 'provenance.json')
    require(manifest.get('schema') == 1, 'Invalid provenance schema')
    entries = manifest['snapshot_files']
    actual = {p.relative_to(root / 'snapshots').as_posix()
              for p in (root / 'snapshots').rglob('*') if p.is_file()
              and not {'__pycache__', '.pytest_cache'}.intersection(p.parts)}
    storage_paths = {entry.get('storage', {}).get('archive', name) for name, entry in entries.items()}
    require(actual == storage_paths, 'Snapshot inventory mismatch')
    for name, entry in entries.items():
        rel = PurePosixPath(name)
        require(not rel.is_absolute() and '..' not in rel.parts, 'Unsafe snapshot path')
        storage = entry.get('storage')
        stored_name = storage['archive'] if storage else name
        stored_rel = PurePosixPath(stored_name)
        require(not stored_rel.is_absolute() and '..' not in stored_rel.parts, 'Unsafe storage path')
        path = root / 'snapshots' / stored_name
        require(not path.is_symlink(), 'Snapshot symlinks are not allowed')
        if storage:
            require(storage['kind'] == 'zip_member', 'Unknown storage kind')
            with ZipFile(path) as archive:
                require(archive.namelist() == [storage['member']], 'Original ZIP member inventory mismatch')
                data = archive.read(storage['member'])
        else:
            data = path.read_bytes()
        require(len(data) == entry['bytes'], f'Byte count mismatch: {name}')
        require(hashlib.sha256(data).hexdigest() == entry['sha256'], f'SHA256 mismatch: {name}')
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        require(blob == entry['git_blob_sha1'], f'Git blob mismatch: {name}')
    return {'status': 'PASS_SNAPSHOT_INTEGRITY_ONLY', 'snapshot_files': len(entries),
            'snapshot_bytes': sum(x['bytes'] for x in entries.values())}


def run_command(command, cwd, timeout=180):
    env = dict(os.environ)
    env.pop('PYTHONOPTIMIZE', None)
    env.update(PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8', PYTHONUTF8='1')
    start = time.monotonic()
    proc = subprocess.run(command, cwd=cwd, env=env, capture_output=True,
                          text=True, encoding='utf-8', timeout=timeout, check=False)
    result = {'command': ['python' if x == sys.executable else str(x) for x in command],
              'returncode': proc.returncode, 'seconds': time.monotonic() - start,
              'stdout': proc.stdout, 'stderr': proc.stderr}
    require(proc.returncode == 0, f'Command failed: {command}\n{proc.stdout}\n{proc.stderr}')
    return result


def run_scoped(root=ROOT):
    root = Path(root)
    require(not sys.flags.optimize, 'Do not disable assertions')
    before = check_integrity(root)
    records, comparisons = [], []
    with tempfile.TemporaryDirectory(prefix='erdos97-publication-') as folder:
        work = Path(folder) / 'packet'
        shutil.copytree(root, work, ignore=shutil.ignore_patterns('__pycache__', '.pytest_cache'))
        fresh = Path(folder) / 'fresh'
        fresh.mkdir()
        product = work / 'snapshots/product-cycle-audit-2026-09-09'
        unrestricted = work / 'snapshots/unrestricted-angle-bridge-2026-09-09'
        stress = work / 'snapshots/global-bridge-stress-2026-09-09'

        def run(cwd, args):
            rec = run_command([sys.executable, '-S', *map(str, args)], cwd)
            rec['cwd'] = Path(cwd).relative_to(work).as_posix()
            records.append(rec)

        def compare(new, old):
            require(load(new) == load(old), f'Exact generated report differs: {old}')
            comparisons.append({'retained': old.relative_to(work).as_posix(), 'comparison': 'complete JSON equality'})

        run(product, ['package.py', '--check'])
        run(product, ['replay.py', '--output', fresh / 'product.json'])
        latest = load(fresh / 'product.json')
        require(latest['fixed_system_certificates'] == 333 and latest['defensive_tests'] == 38
                and latest['publication_core_tests'] == 12, 'Unexpected product-cycle replay coverage')
        run(unrestricted, ['verify/degree_lifting_control.py', '--check'])
        for stem, retained in [
            ('local_middle_radius_negative_control', 'exact_middle_radius_independent_replay'),
            ('local_full_star_radius_negative_control', 'exact_full_star_radius_control'),
        ]:
            output = fresh / (stem + '.json')
            run(unrestricted, ['verify/rational_geometry.py', f'candidate_counterexamples/{stem}.json', '--output', output])
            compare(output, unrestricted / 'reports' / (retained + '.json'))
        for script, stem in [('geometry_control', 'mec_support_control_9'),
                             ('star_control', 'nonincreasing_star_control_17_robust')]:
            output = fresh / (stem + '.json')
            run(stress, [f'verify/{script}.py', f'candidate_counterexamples/{stem}.json', '--output', output])
            compare(output, stress / 'reports' / (stem + '.json'))
        run(stress, ['search/circumcenter_completion.py', 'candidate_counterexamples/mec_support_control_9.json',
                     '--output', fresh / 'circumcenters.json'])
        compare(fresh / 'circumcenters.json', stress / 'reports/mec_circumcenter_completion.json')
        run(work, ['verify_attachment_angles.py', '--output', fresh / 'angles.json'])
        angles = load(fresh / 'angles.json')
        check_integrity(work)
        evidence = {'product_cycle': latest, 'earlier_angle_evidence': angles,
                    'circumcenter_summary': {k: v for k, v in load(fresh / 'circumcenters.json').items()
                                            if k != 'candidates'}}
    require(check_integrity(root) == before, 'Snapshot changed during replay')
    return {'status': 'PASS_SCOPED_PUBLICATION_REPLAY', 'python': platform.python_version(),
            'integrity': before, 'commands': records, 'exact_report_comparisons': comparisons,
            'evidence': evidence, 'original_product_tests': 50,
            'exact_geometric_controls': 9,
            'stored_fixed_system_contradiction_records': 333 + 912 + 799 + 487,
            'separate_positive_two_star_angle_vectors': 1354,
            'search_discovery_rerun': False, 'all_nine_orbit_systems_exhausted': False,
            'two_star_enumeration_completeness_checked': False,
            'repository_wide_gates_run': False, 'external_mathematical_review': False,
            'unrestricted_solution': False}


if __name__ == '__main__':
    require(not sys.flags.optimize, 'Do not disable assertions')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scoped', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = run_scoped() if args.scoped else check_integrity()
    if args.output:
        write_report(args.output, report)
    print(json.dumps({k: v for k, v in report.items() if k not in ('commands', 'evidence')}, indent=2))
