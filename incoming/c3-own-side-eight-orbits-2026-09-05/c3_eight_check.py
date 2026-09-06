#!/usr/bin/env python3
"""Standard-library geometric/provenance and integer-certificate verification.
No LP, floating arithmetic, or imported search implementation is used here.
Stored frontier checks do not replace complete enumeration.
"""
from __future__ import annotations
from collections import defaultdict
from itertools import combinations
import argparse
import hashlib
import json
from math import gcd
from pathlib import Path
ROOT = Path(__file__).resolve().parent
PI = (-1, -1)

def require(value, message):
    if not value:
        raise ValueError(message)

def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def validate_rows(rows, full=True):
    """Validate the selected supplier/gain data before using it as a geometric premise."""
    require(isinstance(rows, list) and len(rows) >= 3, 'orbit rows required')
    m = len(rows)
    for i, row in enumerate(rows):
        require(isinstance(row, list) and (len(row) == 4 if full else len(row) % 2 == 0), 'target/gain pairs required')
        targets = row[::2]
        require(len(set(targets)) == len(targets), 'duplicate supplier')
        for j, g in zip(targets, row[1::2]):
            require(type(j) is int and 0 <= j < m and (j != i), 'invalid target')
            require(type(g) is int and 0 <= g < 3, 'invalid gain')
            require(i not in rows[j][::2], 'reciprocal arrows')
    return m

class Geometry:

    def __init__(self, rows, full=True):
        """Reconstruct physical chord equalities by BFS and directions by explicit C3 rotations."""
        self.m = validate_rows(rows, full)
        self.n = 3 * self.m
        self.rows = rows
        m, n = (self.m, self.n)
        self.pairs = list(combinations(range(n), 2))
        self.selected = []
        self.right = []
        for p in range(n):
            i, k = (p % m, p // m)
            self.selected.append({i + (k + 1) % 3 * m, i + (k + 2) % 3 * m})
            self.right.append(set())
            for j, g in zip(rows[i][::2], rows[i][1::2]):
                self.selected[p].add(j + (k + g) % 3 * m)
                self.right[p].add(tuple(sorted((j + (k + g + 1) % 3 * m, j + (k + g + 2) % 3 * m))))
        graph = defaultdict(set)
        for a, b in self.pairs:
            nxt = tuple(sorted(((a + m) % n, (b + m) % n)))
            graph[a, b].add(nxt)
            graph[nxt].add((a, b))
        for p, targets in enumerate(self.selected):
            spokes = [tuple(sorted((p, t))) for t in sorted(targets)]
            for a, b in zip(spokes, spokes[1:]):
                graph[a].add(b)
                graph[b].add(a)
        self.length = {}
        for pair in self.pairs:
            if pair in self.length:
                continue
            stack = [pair]
            self.length[pair] = pair
            while stack:
                for q in graph[stack.pop()]:
                    if q not in self.length:
                        self.length[q] = pair
                        stack.append(q)
        self.owner = {self.length[i, i + m]: i for i in range(m)}
        require(len(self.owner) == m, 'own-side length collision')
        self.less = set()
        for i, row in enumerate(rows):
            for j, g in zip(row[::2], row[1::2]):
                offset = (g * m + j - i) % n
                self.less.add((j, i) if m < offset < 2 * m else (i, j))
        self.direction = {}
        for a, b in self.pairs:
            orbit = [tuple(sorted(((a + k * m) % n, (b + k * m) % n))) for k in range(3)]
            rep = min(orbit)
            num = a + b - sum(rep)
            require(num % m == 0, 'nonintegral rotation offset')
            self.direction[a, b] = (rep, num // m)
        self.variables = sorted({rep for rep, _ in self.direction.values()}) + [PI]

    def angle(self, tri, at):
        """Return three times a triangle angle in unreduced chord-direction coordinates."""
        a, b, c = tri
        if at == 0:
            return {(a, c): 1, (a, b): -1}
        if at == 1:
            return {(a, b): 1, (b, c): -1, PI: 3}
        return {(b, c): 1, (a, c): -1}

    def combine(self, a, b, wa=1, wb=-1):
        result = defaultdict(int)
        for key, val in a.items():
            result[key] += wa * val
        for key, val in b.items():
            result[key] += wb * val
        return {k: v for k, v in result.items() if v}

    def reduce(self, raw, equality):
        """Substitute rotation offsets and normalize with the appropriate equality sign convention."""
        ans = defaultdict(int)
        for key, v in raw.items():
            if key == PI:
                ans[PI] += v
            else:
                rep, offset = self.direction[key]
                ans[rep] += v
                ans[PI] += v * offset
        ans = {k: v for k, v in ans.items() if v}
        g = 0
        for v in ans.values():
            g = gcd(g, v)
        if not g:
            return {}
        if equality:
            first = next((ans[key] for key in self.variables if key in ans))
            if first < 0:
                g = -g
        return {key: value // g for key, value in ans.items()}

    def row(self, label, equality):
        """Rebuild and validate one geometric certificate premise, without the generator model."""
        require(isinstance(label, list) and label, 'invalid geometric row label')
        kind = label[0]
        if kind == 'pi_positive':
            require(not equality and len(label) == 1, 'pi row kind')
            raw = {PI: 1}
        elif kind == 'right_angle':
            require(equality and len(label) == 4, 'right-angle row kind')
            _, p, j, g = label
            require(all((type(v) is int for v in (p, j, g))) and 0 <= p < self.m, 'right-angle source')
            require(any((t == j and h == g for t, h in zip(self.rows[p][::2], self.rows[p][1::2]))), 'unforced right angle')
            u = (g + 1) % 3 * self.m + j
            v = (g + 2) % 3 * self.m + j
            tri = tuple(sorted((p, u, v)))
            raw = self.combine(self.angle(tri, tri.index(p)), {PI: 3}, 2, -1)
        else:
            require(kind in {'angle_positive', 'equal_sides', 'angle_order'}, 'unknown row kind')
            require(len(label) == (5 if kind == 'angle_positive' else 6), 'triangle label length')
            tri = tuple(label[1:4])
            require(all((type(v) is int for v in tri)) and 0 <= tri[0] < tri[1] < tri[2] < self.n, 'triangle order')
            a, b, c = tri
            opposite = [self.length[b, c], self.length[a, c], self.length[a, b]]
            at = label[4]
            require(type(at) is int and 0 <= at < 3, 'triangle corner')
            if kind == 'angle_positive':
                require(not equality, 'positive angle called equality')
                raw = self.angle(tri, at)
            else:
                other = label[5]
                require(type(other) is int and 0 <= other < 3 and (at != other), 'opposite corner')
                if kind == 'equal_sides':
                    require(equality and opposite[at] == opposite[other], 'unforced isosceles equality')
                    raw = self.combine(self.angle(tri, at), self.angle(tri, other))
                else:
                    require(not equality, 'side order called equality')
                    x, y = (self.owner.get(opposite[at]), self.owner.get(opposite[other]))
                    require((x, y) in self.less, 'unforced strict side order')
                    raw = self.combine(self.angle(tri, other), self.angle(tri, at))
        return self.reduce(raw, equality)

    def verify_angle_certificate(self, certificate):
        """Check a nonempty positive sum of strict premises plus equalities is identically zero."""
        require(isinstance(certificate, dict) and set(certificate) == {'strict', 'equal'}, 'certificate keys')
        require(certificate['strict'], 'no strict multiplier')
        total = defaultdict(int)
        for name in ('strict', 'equal'):
            require(isinstance(certificate[name], list), 'terms must be a list')
            for term in certificate[name]:
                require(isinstance(term, list) and len(term) == 2, 'invalid term')
                label, weight = term
                require(type(weight) is int and (weight > 0 if name == 'strict' else weight != 0), 'invalid multiplier')
                v = self.row(label, name == 'equal')
                require(v, 'zero certificate premise')
                for key, value in v.items():
                    total[key] += weight * value
        require(not any(total.values()), 'integer certificate does not sum to zero')
        return True

    def verify_containment(self, certificate):
        """Verify an isosceles base angle contains a forced right angle in boundary order."""
        require(isinstance(certificate, list) and len(certificate) == 5, 'five labels required')
        require(all((type(x) is int and 0 <= x < self.n for x in certificate)), 'containment label bounds')
        center, p, b, u, v = certificate
        require(p != b and p in self.selected[center] and (b in self.selected[center]), 'missing equal legs')
        require(tuple(sorted((u, v))) in self.right[p], 'missing right angle at base')
        lo, hi = sorted(((center - p) % self.n, (b - p) % self.n))
        x, y = sorted(((u - p) % self.n, (v - p) % self.n))
        require(0 < lo <= x < y <= hi < self.n, 'right angle is not inside base angle')
        return True

def verify_packet(path=ROOT / 'certificates.json'):
    """Check every stored frontier certificate; this does not establish exhaustive coverage."""
    data = json.loads(Path(path).read_text())
    require(data.get('schema') == 1, 'schema mismatch')
    cases = data['cases']
    require(len(cases) == 632, 'wrong frontier size')
    require(len({digest(case['rows']) for case in cases}) == 632, 'duplicate case')
    contained = 0
    terms = 0
    for i, case in enumerate(cases):
        require(case['index'] == i, 'case index mismatch')
        require(len(case['rows']) == 8, 'not an eight-orbit case')
        geo = Geometry(case['rows'])
        geo.verify_angle_certificate(case['angle_certificate'])
        terms += sum((len(v) for v in case['angle_certificate'].values()))
        if case['containment'] is not None:
            geo.verify_containment(case['containment'])
            contained += 1
    require(contained == 369, 'containment census changed')
    return {'scope': 'stored frontier and exact certificate validation, not exhaustive regeneration', 'cases': 632, 'integer_angle_certificates': 632, 'angle_terms': terms, 'obtuse_base_certificates': contained, 'frontier_sha256': digest([x['rows'] for x in cases]), 'certificates_sha256': digest(cases)}

def audit_run_records():
    """Check full shard coverage, source binding, and integer totals of saved completed runs."""
    data = json.loads((ROOT / 'runs.json').read_text())
    require(data.get('schema') == 1, 'run-record schema')
    for name in ('search.cpp', 'oracle.cpp'):
        require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == data['source_sha256'][name], 'source hash no longer matches recorded runs')
    records = data['records']
    keys = []
    summary = {}
    for record in records:
        kind = record['implementation']
        r = record['report']
        require(kind in ('primary', 'oracle'), 'unknown implementation')
        key = (kind, r['orbits'], r['slice'])
        keys.append(key)
        require(r['exhausted'] is True and r['termination_reason'] == 'exhausted', 'incomplete recorded run')
        require(all((type(r[k]) is int and r[k] >= 0 for k in ('nodes', 'radius_prunes', 'shortcut_prunes', 'metric_prunes', 'pair_dead', 'survivors'))), 'noninteger recorded counters')
        if kind == 'primary':
            require(r['metric_enabled'] is True and r['shortcut_enabled'] is True, 'disabled recorded filter')
    expected = {(kind, m, -1) for kind in ('primary', 'oracle') for m in (5, 6, 7)}
    expected |= {(kind, 8, i) for kind in ('primary', 'oracle') for i in range(21)}
    require(len(keys) == len(set(keys)) and set(keys) == expected, 'recorded slice coverage mismatch')
    for kind in ('primary', 'oracle'):
        small = [r['report'] for r in records if r['implementation'] == kind and r['report']['orbits'] < 8]
        require(all((r['survivors'] == 0 for r in small)), 'unexpected small-case survivor')
        big = [r['report'] for r in records if r['implementation'] == kind and r['report']['orbits'] == 8]
        summary[kind] = {'slices': len(big), 'nodes': sum((r['nodes'] for r in big)), 'survivors': sum((r['survivors'] for r in big))}
        require(summary[kind] == {'slices': 21, 'nodes': 11415572, 'survivors': 632}, 'recorded aggregate mismatch')
    return {'scope': 'stored-run consistency, not fresh search', 'implementations': summary}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    result = verify_packet()
    if args.check:
        report = json.loads((ROOT / 'report.json').read_text())
        require(result == report['certificate_audit'], 'certificate report mismatch')
        result = {'certificate_audit': result, 'run_record_audit': audit_run_records()}
    print(json.dumps(result, indent=2, sort_keys=True))
if __name__ == '__main__':
    main()
