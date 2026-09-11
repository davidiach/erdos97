"""Integer phase certificates from gain-aligned four-arrow diamonds.
Geometric justification is written in README.md.
No optimizer, coordinate residual, or assumed product parametrization is used.
"""
from collections import defaultdict
from itertools import combinations

def require(ok, message):
    if not ok:
        raise ValueError(message)

def arrow_gain(rows, i, j):
    require(type(i) is int and type(j) is int and (0 <= i < len(rows)) and (0 <= j < len(rows)), 'bad orbit label')
    pairs = list(zip(rows[i][::2], rows[i][1::2]))
    hits = [g for t, g in pairs if t == j]
    require(len(hits) == 1, 'missing or duplicate diamond arrow')
    require(type(hits[0]) is int and 0 <= hits[0] < 3, 'bad rotation gain')
    return hits[0]

def relation(rows, i, j, k, tip):
    require(len({i, j, k, tip}) == 4, 'diamond needs four distinct orbits')
    a, b, c, d = (arrow_gain(rows, i, j), arrow_gain(rows, i, k), arrow_gain(rows, j, tip), arrow_gain(rows, k, tip))
    require((a + c - b - d) % 3 == 0, 'unmatched total gains')
    g = (b - c) % 3
    sigma = (0, 1, -1)[g]
    v = defaultdict(int)
    for x, s in [(i, 1), (tip, 1), (j, -1), (k, -1)]:
        v[x] += s
    v['L'] -= sigma
    return {x: s for x, s in v.items() if s}

def diamonds(rows):
    out = []
    for i, row in enumerate(rows):
        for j, k in combinations(row[::2], 2):
            for tip in set(rows[j][::2]) & set(rows[k][::2]):
                if len({i, j, k, tip}) < 4:
                    continue
                try:
                    v = relation(rows, i, j, k, tip)
                except ValueError:
                    continue
                out.append({'labels': [i, j, k, tip], 'coefficients': [[str(x), s] for x, s in v.items()]})
    return out

def check(rows, certificate):
    require(set(certificate) == {'strict', 'equal'}, 'bad phase certificate keys')
    require(certificate['strict'], 'no strict contribution')
    total = defaultdict(int)
    for label, w in certificate['strict']:
        require(type(w) is int and w > 0, 'strict multiplier must be positive integer')
        require(len(label) == 3, 'bad phase order label')
        kind, i, j = label
        require(type(i) is int and type(j) is int and (0 <= i < j < len(rows)), 'unforced sector order')
        if kind == 'phase_gap':
            v = {j: 1, i: -1}
        elif kind == 'sector_span':
            v = {'L': 1, i: 1, j: -1}
        else:
            raise ValueError('unknown strict phase premise')
        for x, s in v.items():
            total[x] += s * w
    for label, w in certificate['equal']:
        require(type(w) is int and w != 0, 'equality multiplier must be nonzero integer')
        require(len(label) == 5 and label[0] == 'diamond', 'bad diamond premise')
        v = relation(rows, *label[1:])
        for x, s in v.items():
            total[x] += s * w
    require(not any(total.values()), 'phase certificate does not cancel')
    return True
TWO_DIAMOND_CERTIFICATE = {'strict': [[['phase_gap', 1, 3], 1], [['sector_span', 0, 8], 1]], 'equal': [[['diamond', 0, 1, 2, 6], -1], [['diamond', 2, 6, 8, 3], -1]]}

def verify_packet(data):
    require(data.get('schema') == 1, 'unsupported schema')
    require(len(data['cases']) == 3, 'expected three fixed systems')
    seen = set()
    for case in data['cases']:
        rows = case['rows']
        require(len(rows) == 9, 'expected nine ordered orbits')
        for i, row in enumerate(rows):
            require(isinstance(row, list) and len(row) == 4, 'two target/gain pairs required')
            require(len(set(row[::2])) == 2, 'duplicate supplier')
            for j, g in zip(row[::2], row[1::2]):
                require(type(j) is int and 0 <= j < 9 and (j != i), 'invalid target')
                require(type(g) is int and 0 <= g < 3, 'invalid gain')
        key = tuple((tuple(x) for x in rows))
        require(key not in seen, 'duplicate case')
        seen.add(key)
        check(rows, data['certificate'])
    return {'status': 'PASS_EXACT_DIAMOND_PHASE_CERTIFICATES', 'fixed_systems': 3, 'diamonds_per_certificate': 2, 'strict_terms_per_certificate': 2, 'all_nine_orbit_systems_exhausted': False, 'unrestricted_solution': False, 'external_mathematical_review': False}
if __name__ == '__main__':
    import argparse
    import json
    import sys
    from pathlib import Path
    require(not sys.flags.optimize, 'assertions must remain enabled')
    p = argparse.ArgumentParser()
    p.add_argument('--input', type=Path, default=Path(__file__).with_name('cases.json'))
    args = p.parse_args()
    print(json.dumps(verify_packet(json.loads(args.input.read_text())), indent=2))
