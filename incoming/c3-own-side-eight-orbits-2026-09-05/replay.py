#!/usr/bin/env python3
"""Fresh C++ replays. --quick is partial at eight orbits; --full is exhaustive.
The stored certificate checker is independent of the optional LP generator.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from c3_eight_check import Geometry, require, verify_packet
from c3_eight_controls import audit_controls
ROOT = Path(__file__).resolve().parent
COUNTERS = ('nodes', 'radius_prunes', 'shortcut_prunes', 'metric_prunes', 'pair_dead', 'survivors')

def build(compiler, kind, m, folder, sanitize=False):
    """Compile one enumerator with strict warnings, optionally under undefined-behavior sanitization."""
    target = folder / f'{kind}-{m}'
    flags = ['-O1', '-g', '-fsanitize=undefined', '-fno-sanitize-recover=undefined'] if sanitize else ['-O3']
    command = [compiler, *flags, '-std=c++17', '-Wall', '-Wextra', '-Wpedantic', '-Werror', f'-DORBIT_COUNT={m}', str(ROOT / ('search.cpp' if kind == 'primary' else 'oracle.cpp')), '-o', str(target)]
    subprocess.run(command, check=True, capture_output=True, text=True, timeout=120)
    return target

def run_case(spec):
    """Run and validate one completed search, retaining its actual emitted frontier."""
    kind, m, slice_id, binary, folder, timeout = spec
    output = folder / f'{kind}-{m}-{slice_id}.jsonl'
    command = [str(binary), '--output', str(output)]
    if kind == 'primary':
        command.append('--all')
    if slice_id >= 0:
        command += ['--slice', str(slice_id)]
    result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=timeout)
    require(not result.stderr.strip(), 'unexpected solver stderr')
    report = json.loads(result.stdout)
    require(report['orbits'] == m and report['slice'] == slice_id, 'run identity mismatch')
    require(report['exhausted'] is True and report['termination_reason'] == 'exhausted', 'run was not exhausted')
    if kind == 'primary':
        require(report['metric_enabled'] is True and report['shortcut_enabled'] is True, 'filter contract changed')
    rows = [json.loads(line) for line in output.read_text().splitlines()]
    require(len(rows) == report['survivors'], 'survivor count mismatch')
    require(all((type(report[k]) is int and report[k] >= 0 for k in COUNTERS)), 'invalid counters')
    return {'implementation': kind, 'report': report, 'rows': rows}

def replay(full=False, jobs=4, sanitize=False, check=False, timeout=600):
    compiler = shutil.which(os.environ.get('CXX', 'c++'))
    require(compiler is not None, 'a GNU-compatible C++17 compiler is required')
    payload = json.loads((ROOT / 'certificates.json').read_text())
    cases = payload['cases']
    expected = {json.dumps(c['rows'], separators=(',', ':')): c for c in cases}
    stored = json.loads((ROOT / 'runs.json').read_text()) if check else None
    if stored is not None:
        for name in ('search.cpp', 'oracle.cpp'):
            require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == stored['source_sha256'][name], 'enumerator source hash differs from recorded run')
    with tempfile.TemporaryDirectory(prefix='c3-eight-replay-') as temp:
        folder = Path(temp)
        bins = {}
        for kind in ('primary', 'oracle'):
            for m in (5, 6, 7, 8):
                bins[kind, m] = build(compiler, kind, m, folder, sanitize)
        specs = []
        for kind in ('primary', 'oracle'):
            for m in (5, 6, 7):
                specs.append((kind, m, -1, bins[kind, m], folder, timeout))
            for i in range(21) if full else (0,):
                specs.append((kind, 8, i, bins[kind, 8], folder, timeout))
        with ThreadPoolExecutor(max_workers=jobs) as executor:
            results = list(executor.map(run_case, specs))
    actual = {kind: [] for kind in ('primary', 'oracle')}
    for result in results:
        kind = result['implementation']
        report = result['report']
        rows = result['rows']
        m = report['orbits']
        slice_id = report['slice']
        if m < 8:
            require(not rows, 'small case has an abstract survivor')
        else:
            for r in rows:
                key = json.dumps(r, separators=(',', ':'))
                require(key in expected, 'unexpected frontier case')
                Geometry(r).verify_angle_certificate(expected[key]['angle_certificate'])
            actual[kind] += rows
        if stored is not None:
            old = next((record['report'] for record in stored['records'] if record['implementation'] == kind and record['report']['orbits'] == m and (record['report']['slice'] == slice_id)), None)
            require(old is not None, 'stored run coverage missing')
            for key in COUNTERS:
                require(report[key] == old[key], f'{kind} m={m} slice={slice_id}: {key} mismatch')
    if full:
        for kind, rows in actual.items():
            keys = [json.dumps(r, separators=(',', ':')) for r in rows]
            require(len(keys) == len(set(keys)) == 632 and set(keys) == set(expected), f'{kind} full frontier mismatch')
    return {'schema': 1, 'scope': 'fresh full enumeration through eight orbits' if full else 'fresh small cases and eight-orbit slice zero only', 'full_eight_orbit_coverage': full, 'undefined_behavior_sanitizer': sanitize, 'source_sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in ('search.cpp', 'oracle.cpp')}, 'runs': [{'implementation': r['implementation'], 'report': r['report']} for r in results], 'certificate_audit': verify_packet(), 'positive_controls': audit_controls()}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--full', action='store_true')
    modes.add_argument('--quick', action='store_true')
    parser.add_argument('--sanitize', action='store_true')
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--jobs', type=int, default=4)
    parser.add_argument('--timeout', type=int, default=600)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.jobs < 1 or args.jobs > 32 or args.timeout < 1:
        parser.error('jobs must be 1..32 and timeout positive')
    result = replay(args.full, args.jobs, args.sanitize, args.check, args.timeout)
    text = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.write_text(text)
    print(text, end='')
if __name__ == '__main__':
    main()
