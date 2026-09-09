"""Assemble a complete binary partition from preserved discovery paths.

This generator proves only partition coverage. verify.py and oracle.py must
separately establish the mathematical rejection of every resulting leaf.
"""
from pathlib import Path
from itertools import combinations_with_replacement, product
import hashlib
import json

ROOT = Path(__file__).resolve().parent


def read_records(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def key(record):
    return tuple(record['cells'] + record['olds'])


def partition(paths):
    if not paths:
        raise ValueError('Uncovered subdomain')
    if any(not p for p in paths):
        if len(paths) != 1:
            raise ValueError('Overlapping or repeated leaf paths')
        return None
    splits = {tuple(p[0][:2]) for p in paths}
    if len(splits) != 1 or any(len(p[0]) != 3 for p in paths):
        raise ValueError('Inconsistent subdivisions')
    coordinate, edge = splits.pop()
    if coordinate not in (0, 1) or edge not in (0, 1, 2):
        raise ValueError('Invalid split')
    if any(p[0][2] not in (0, 1) for p in paths):
        raise ValueError('Invalid child')
    return dict(coordinate=coordinate, edge=edge, children=[
        partition([p[1:] for p in paths if p[0][2] == child]) for child in (0, 1)])


def build():
    initial = read_records(ROOT/'exploratory/initial_sweep.jsonl')
    if len({key(row) for row in initial}) != 4500:
        raise ValueError('Initial sweep coverage is incomplete')
    records = {key(row): row for row in initial}
    for record in read_records(ROOT/'exploratory/deeper_sweep.jsonl'):
        if key(record) not in records:
            raise ValueError('Unknown refinement case')
        records[key(record)] = record
    endings = json.loads((ROOT/'exploratory/final_leaf_checks.json').read_text())
    endings = {(key(row), json.dumps(row['path'])): row for row in endings}
    cases = []
    for a,b in combinations_with_replacement(range(9),2):
        for u,v in product([None]+list(range(9)),repeat=2):
            row = records[(a,b,u,v)]
            if 'error' in row:
                raise ValueError('Discovery error')
            paths = [leaf['path'] for leaf in row['closed']]
            for leaf in row['unresolved']:
                end = endings[(key(row),json.dumps(leaf['path']))]
                if not end['results'] or any(r['status']!='exhausted' for r in end['results']):
                    raise ValueError('Unresolved discovery leaf')
                paths.append(leaf['path'])
            cases.append(dict(cells=[a,b],old_witnesses=[u,v],tree=partition(paths)))
    return dict(schema='erdos97.two_free_partition.v1',
                base_sha='047d05149382e48b602b292df4b8fc9e2da560bb',
                input_sha256=hashlib.sha256((ROOT/'inputs/internal_support.zip').read_bytes()).hexdigest(),
                not_an_unrestricted_solution=True,cases=cases)


if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args()
    text=json.dumps(build(),sort_keys=True,indent=2)+'\n'
    path=ROOT/'data/certificate.json'
    if args.check:
        if path.read_text()!=text:raise ValueError('Generated certificate differs')
    else:path.write_text(text)
    print(json.dumps({'cases':4500,'bytes':len(text.encode()),'sha256':hashlib.sha256(text.encode()).hexdigest()}))
