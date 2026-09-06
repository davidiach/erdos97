#!/usr/bin/env python3
"""Optional SciPy certificate discovery, followed by exact integer verification.
Only the checked integer certificates, never a floating LP status, certify rejection.
HiGHS versions may choose different valid certificates. Coverage is not regenerated.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
import json
from math import gcd, lcm
from pathlib import Path
from c3_eight_angles import model
from c3_eight_check import Geometry, require
ROOT = Path(__file__).resolve().parent

def discover(rows):
    """Use a numerical LP to propose multipliers, then require an exact integer contradiction."""
    import numpy as np
    from scipy.optimize import linprog
    from scipy.sparse import csr_matrix, hstack, vstack
    A, E, al, el = model(rows)
    na, ne = (len(A), len(E))
    dim = len(A[0])
    matrix = vstack([hstack([csr_matrix(np.array(A).T), csr_matrix(np.array(E).T)]), csr_matrix([[1] * na + [0] * ne])], format='csr')
    result = linprog(np.zeros(na + ne), A_eq=matrix, b_eq=np.r_[np.zeros(dim), 1], bounds=[(0, None)] * na + [(None, None)] * ne, method='highs')
    require(result.success, 'LP did not provide a candidate certificate; this is not a feasibility conclusion')
    support = [i for i, x in enumerate(result.x) if abs(x) > 1e-08]
    values = [Q(float(result.x[i])).limit_denominator(1000000) for i in support]
    denominator = lcm(*(v.denominator for v in values))
    weights = [int(v * denominator) for v in values]
    divisor = gcd(*weights)
    weights = [v // divisor for v in weights]
    certificate = {'strict': [], 'equal': []}
    for i, weight in zip(support, weights):
        if weight:
            kind = 'strict' if i < na else 'equal'
            label = al[i] if i < na else el[i - na]
            certificate[kind].append([label, weight])
    Geometry(rows).verify_angle_certificate(certificate)
    return certificate

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--index', type=int)
    args = parser.parse_args()
    original = json.loads((ROOT / 'certificates.json').read_text())
    if args.index is not None and (not 0 <= args.index < len(original['cases'])):
        parser.error('index is out of range')
    if args.output.resolve() == (ROOT / 'certificates.json').resolve():
        parser.error('write discovery output to a new path, not the canonical artifact')
    records = original['cases'] if args.index is None else [original['cases'][args.index]]
    updated = []
    for record in records:
        updated.append({**record, 'angle_certificate': discover(record['rows'])})
    args.output.write_text(json.dumps({'schema': 1, 'cases': updated}, separators=(',', ':')) + '\n')
    print(f'Exactly checked {len(updated)} regenerated certificates; graph coverage was not rerun.')
if __name__ == '__main__':
    main()
