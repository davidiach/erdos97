"""Sparse rational replay of the earlier attached angle certificates.

The source checker is preserved in snapshots/. This implementation reconstructs
its triangle/isosceles equations independently and avoids dense zero matrices.
It validates stored cases, not search execution or completeness of enumeration.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
import json
from pathlib import Path
import sys

F = Fraction
ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'snapshots/unrestricted-angle-bridge-2026-09-09/reports'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def rational(value):
    require(type(value) in (str, int), 'Exact rational text/integer required')
    return F(value)


def normalize_rows(n, rows):
    require(type(n) is int and 3 <= n <= 100, 'Invalid point count')
    require(isinstance(rows, dict), 'Rows must be a mapping')
    result = {}
    for raw, targets in rows.items():
        require(type(raw) in (int, str), 'Invalid center')
        apex = int(raw)
        require(str(apex) == str(raw) and 0 <= apex < n, 'Invalid center')
        require(apex not in result, 'Duplicate center')
        require(isinstance(targets, list) and len(targets) == 4, 'Four witnesses required')
        require(all(type(x) is int and 0 <= x < n and x != apex for x in targets), 'Invalid target')
        require(len(set(targets)) == 4, 'Repeated witness')
        result[apex] = sorted(targets)
    return dict(sorted(result.items()))


@lru_cache(maxsize=16)
def base_angles(n):
    result = []
    for a, b, c in combinations(range(n), 3):
        result.extend([
            ({(a, c): 1, (a, b): -1}, 0),
            ({(b, c): 1, (a, c): -1}, 0),
            ({(a, b): 1, (b, c): -1}, 1),
        ])
    return result


def equations(n, rows):
    out = []
    for apex, targets in normalize_rows(n, rows).items():
        for u, v in combinations(targets, 2):
            a, b, c = sorted((apex, u, v))
            if apex == a:
                out.append(({(a, b): 1, (a, c): 1, (b, c): -2}, -1))
            elif apex == b:
                out.append(({(a, b): 1, (b, c): 1, (a, c): -2}, 0))
            else:
                out.append(({(a, c): 1, (b, c): 1, (a, b): -2}, 1))
    out.append(({(0, 1): 1}, 0))
    return out


def weights(items, size, positive=False):
    require(isinstance(items, list), 'Weight list required')
    seen = set()
    result = []
    for item in items:
        require(isinstance(item, list) and len(item) == 2, 'Invalid weight term')
        index, raw = item
        require(type(index) is int and 0 <= index < size and index not in seen, 'Invalid/repeated index')
        seen.add(index)
        value = rational(raw)
        require(value != 0 and (not positive or value > 0), 'Invalid multiplier')
        result.append((index, value))
    return result


def check_contradiction(n, rows, certificate):
    eq = equations(n, rows)
    angles = base_angles(n)
    require(isinstance(certificate, dict), 'Certificate object required')
    terms = weights(certificate['equality_weights'], len(eq))
    coefficient = defaultdict(F)
    eq_constant = F(0)
    for index, value in terms:
        vector, rhs = eq[index]
        eq_constant += value * rhs
        for chord, coeff in vector.items():
            coefficient[chord] += value * coeff
    kind = certificate['kind']
    claimed = rational(certificate['constant'])
    if kind == 'inconsistent-equalities':
        require(not any(coefficient.values()) and eq_constant != 0 and eq_constant == claimed,
                'False inconsistent-equality certificate')
        return
    require(kind == 'strict-positive-angle-contradiction', 'Unknown certificate kind')
    positive = weights(certificate['angle_weights'], len(angles), True)
    require(positive, 'Strictness missing')
    value = -eq_constant
    for index, weight in positive:
        vector, constant = angles[index]
        value += weight * constant
        for chord, coeff in vector.items():
            coefficient[chord] += weight * coeff
    require(not any(coefficient.values()) and value <= 0 and value == claimed,
            'False positive-angle contradiction')


def check_feasible(n, rows, values):
    eq = equations(n, rows)
    chords = list(combinations(range(n), 2))
    require(isinstance(values, list) and len(values) == len(chords), 'Wrong phase-vector size')
    beta = dict(zip(chords, map(rational, values)))
    for vector, rhs in eq:
        require(sum(c * beta[p] for p, c in vector.items()) == rhs, 'Isosceles equation fails')
    minimum = min(sum(c * beta[p] for p, c in vector.items()) + constant
                  for vector, constant in base_angles(n))
    require(minimum > 0, 'Nonpositive triangle angle')
    return minimum


def check_case(case):
    result = case['result']
    kind = result['classification']
    if kind == 'EXACT_ANGLE_OBSTRUCTION':
        check_contradiction(case['n'], case['rows'], result['certificate'])
    elif kind == 'EXACT_ANGLE_RELAXATION_FEASIBLE':
        check_feasible(case['n'], case['rows'], result['chord_directions_over_pi'])
    else:
        raise ValueError('Unverified or unrecognized case classification')
    return kind


def run(source=SOURCE):
    catalogue = json.loads((source / 'two_star_angles.json').read_text(encoding='utf-8'))
    counts = Counter(check_case(case) for case in catalogue['cases'])
    require(len(catalogue['cases']) == 2266, 'Two-star case inventory changed')
    require(counts == {'EXACT_ANGLE_OBSTRUCTION': 912, 'EXACT_ANGLE_RELAXATION_FEASIBLE': 1354},
            'Unexpected two-star evidence census')
    records = []
    for name, expected in [('angle_minconflicts_n20_exact.json', 799),
                           ('angle_minconflicts_n30.json', 487)]:
        data = json.loads((source / name).read_text(encoding='utf-8'))
        require(len(data['events']) == expected == len(data['learned']), 'Stored run inventory changed')
        unique = set()
        for event, learned in zip(data['events'], data['learned']):
            for key in ('n', 'rows', 'result'):
                require(event[key] == learned[key], 'Event/learned record mismatch')
            require(check_case(event) == 'EXACT_ANGLE_OBSTRUCTION', 'Unresolved event')
            unique.add(json.dumps(event['rows'], sort_keys=True, separators=(',', ':')))
        records.append({'file': name, 'verified_certificate_records': expected,
                        'distinct_stored_row_systems': len(unique), 'search_rerun': False})
    return {'status': 'PASS_STORED_ATTACHMENT_ANGLE_EVIDENCE', 'two_star_cases': 2266,
            'two_star_counts': dict(counts), 'bounded_runs': records,
            'enumeration_completeness_checked': False, 'geometric_realizations_certified': 0,
            'unrestricted_solution': False, 'external_review': False}


if __name__ == '__main__':
    require(not sys.flags.optimize, 'Do not disable assertions')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = json.dumps(run(), indent=2) + '\n'
    if args.output:
        args.output.write_text(report, encoding='utf-8', newline='\n')
    print(report, end='')
