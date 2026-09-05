#!/usr/bin/env python3
"""Optional SciPy certificate discovery; exact verification is mandatory.

This is not imported by the verifier. It may produce different valid sparse
multipliers with a different solver version. --output is explicit; nothing
silently replaces a stored proof or promotes a solver result to a theorem.
"""
from __future__ import annotations
import argparse
from fractions import Fraction
from functools import reduce
from math import gcd, lcm
import json
from pathlib import Path
from core import AngleModel, verify_certificate
from verify import load, diamond_arrows, transitive_model_input, seven_model_input

def discover_certificate(A, E):
    import numpy as np
    from scipy.optimize import linprog
    for i, row in enumerate(A):
        if not any(row):
            return ([[i, 1]], [])
    d, na, ne = (len(A[0]), len(A), len(E))
    matrix = np.hstack([np.array(A).T, np.array(E).T if E else np.empty((d, 0))])
    matrix = np.vstack([matrix, np.array([1] * na + [0] * ne)])
    result = linprog(np.zeros(na + ne), A_eq=matrix, b_eq=[0] * d + [1], bounds=[(0, None)] * na + [(None, None)] * ne, method='highs')
    if not result.success:
        raise RuntimeError('No certificate discovered; this is not a geometric feasibility conclusion.')
    values = [Fraction(float(x)).limit_denominator(10 ** 7) if abs(x) > 1e-09 else Fraction(0) for x in result.x]
    denominator = lcm(*(x.denominator for x in values))
    integers = [int(x * denominator) for x in values]
    divisor = reduce(gcd, (abs(x) for x in integers if x))
    integers = [x // divisor for x in integers]
    positive = [[i, x] for i, x in enumerate(integers[:na]) if x]
    equality = [[i, x] for i, x in enumerate(integers[na:]) if x]
    verify_certificate(A, E, positive, equality)
    return (positive, equality)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('kind', choices=['triangle', 'diamond', 'residual'])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    name = {'triangle': 'transitive_radius_certificates.json', 'diamond': 'diamond_certificates.json', 'residual': 'seven_angle_certificates.json'}[args.kind]
    records = load(name)
    model = AngleModel(7 if args.kind == 'residual' else 3 if args.kind == 'triangle' else 4)
    for record in records:
        if args.kind == 'triangle':
            arrows, greater = transitive_model_input(record)
        elif args.kind == 'diamond':
            arrows, greater = (diamond_arrows(record), [])
        else:
            arrows, greater = seven_model_input(record)
        A, E = model.build(arrows, greater)
        record['positive'], record['equality'] = discover_certificate(A, E)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(records, separators=(',', ':')) + '\n')
    print(json.dumps({'exactly_verified_certificates': len(records), 'kind': args.kind, 'geometric_sufficiency_claimed': False}))
if __name__ == '__main__':
    main()
