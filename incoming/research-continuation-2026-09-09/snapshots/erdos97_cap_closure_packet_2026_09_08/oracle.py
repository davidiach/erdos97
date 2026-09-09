"""Separate exact checker: ray exit times, polynomial evaluation, radical intervals.

Imports no primary arithmetic, geometry, graph code, or generated program.
The base field is represented by coefficients in 1,X with X^2=721. The final
extension uses Y^2=S0+S1*X; its negative field norm certifies irreducibility.
All nonzero signs are separated by rational enclosures, not float tolerances.
"""
from fractions import Fraction as F
from functools import lru_cache, total_ordering
from itertools import combinations, product
from math import isqrt
from pathlib import Path
import hashlib
import json
import zipfile
import sys

if sys.flags.optimize:
    raise RuntimeError('Run exact checks without Python -O or -OO')

ROOT = Path(__file__).resolve().parent
MAX_BITS = 0
D = F(721)


@lru_cache(None)
def sqrt_bounds(value, bits):
    assert value >= 0
    k = isqrt((value.numerator << (2*bits)) // value.denominator)
    lower = F(k, 1 << bits)
    return lower, lower if lower*lower == value else F(k+1, 1 << bits)


def ring(S0=F(0), S1=F(0)):
    S0, S1 = F(S0), F(S1)
    base_only = S0 == S1 == 0
    if not base_only:
        assert S0*S0 - D*S1*S1 < 0, 'extension irreducibility not established'

    @total_ordering
    class R:
        __slots__ = ('coeff',)
        def __init__(self, a=0, b=0, c=0, d=0):
            if isinstance(a, R):
                assert b == c == d == 0
                self.coeff = a.coeff
                return
            if any(isinstance(v, float) for v in (a, b, c, d)):
                raise TypeError('floating coefficients are not exact')
            if base_only and (c != 0 or d != 0):
                raise ValueError('nonzero extension coefficient in base field')
            self.coeff = tuple(map(F, (a, b, c, d)))
        def __add__(self, other):
            other = R(other)
            return R(*(x+y for x, y in zip(self.coeff, other.coeff)))
        __radd__ = __add__
        def __neg__(self):
            return R(*(-v for v in self.coeff))
        def __sub__(self, other):
            return self + -R(other)
        def __rsub__(self, other):
            return R(other) + -self
        def __mul__(self, other):
            other = R(other)
            out = [F(0)]*4
            for i, a in enumerate(self.coeff):
                for j, b in enumerate(other.coeff):
                    factor = a*b*(D if (i & j & 1) else 1)
                    index = i ^ j
                    if i & j & 2:
                        out[index] += factor*S0
                        out[index ^ 1] += factor*S1*(D if index & 1 else 1)
                    else:
                        out[index] += factor
            return R(*out)
        __rmul__ = __mul__
        def __truediv__(self, other):
            a, b, c, d = R(other).coeff
            if c or d:
                raise ValueError('oracle divides only by base-field elements')
            denominator = a*a-D*b*b
            if denominator == 0:
                raise ZeroDivisionError
            return self*R(a/denominator, -b/denominator)
        def __rtruediv__(self, other):
            return R(other)/self
        def __eq__(self, other):
            try:
                return self.coeff == R(other).coeff
            except (TypeError, ValueError):
                return NotImplemented
        def __hash__(self):
            return hash(self.coeff)
        def sign(self):
            global MAX_BITS
            if not any(self.coeff):
                return 0
            for bits in (32, 64, 128, 256, 512, 1024, 2048):
                X = sqrt_bounds(D, bits)
                if base_only:
                    Y = (F(0), F(0))
                else:
                    lower = S0+S1*(X[0] if S1 >= 0 else X[1])
                    upper = S0+S1*(X[1] if S1 >= 0 else X[0])
                    if lower < 0:
                        continue
                    Y = (sqrt_bounds(lower, bits)[0], sqrt_bounds(upper, bits)[1])
                bases = ((F(1), F(1)), X, Y, (X[0]*Y[0], X[1]*Y[1]))
                low = high = F(0)
                for c, (l, h) in zip(self.coeff, bases):
                    low += c*(l if c >= 0 else h)
                    high += c*(h if c >= 0 else l)
                if low > 0 or high < 0:
                    MAX_BITS = max(MAX_BITS, bits)
                    return 1 if low > 0 else -1
            raise AssertionError('sign not isolated; no conclusion is drawn')
        def __lt__(self, other):
            return (self-R(other)).sign() < 0
        @classmethod
        def q(cls, value):
            assert isinstance(value, list) and len(value) == 2 and all(isinstance(s, str) for s in value)
            return cls(F(value[0]), F(value[1]))
        @classmethod
        def e(cls, value):
            assert isinstance(value, list) and len(value) == 2
            assert all(isinstance(v, list) and len(v) == 2 and all(isinstance(s, str) for s in v) for v in value)
            return cls(F(value[0][0]), F(value[0][1]), F(value[1][0]), F(value[1][1]))
        def qjson(self):
            assert self.coeff[2:] == (0, 0)
            return [str(c) for c in self.coeff[:2]]
    return R


def plus(a, b):
    return a[0]+b[0], a[1]+b[1]
def minus(a, b):
    return a[0]-b[0], a[1]-b[1]
def times(a, t):
    return a[0]*t, a[1]*t
def area(a, b):
    return a[0]*b[1]-a[1]*b[0]
def orientation(a, b, c):
    return area(minus(b, a), minus(c, a))
def square(a):
    return a[0]*a[0]+3*a[1]*a[1]
def distance(a, b):
    return square(minus(a, b))
def rotate(a):
    return (-a[0]-3*a[1])/2, (a[0]-a[1])/2


def seed(R):
    def z(t):
        den = 1+3*t*t
        return -R(F(1, 2))+3*t/den, (1-3*t*t)/(2*den)
    a = z(R(F(1, 10)))
    b = z(R(F(83, 200), -F(3, 200)))
    points = []
    for q in ((R(1), R(0)), a, (b[0], -b[1])):
        points.extend((q, rotate(q), rotate(rotate(q))))
    return points


def strict(points, order):
    assert sorted(order) == list(range(len(points))) and len(set(points)) == len(points)
    count = 0
    for k, a in enumerate(order):
        b = order[(k+1) % len(points)]
        for j in range(len(points)):
            if j not in (a, b):
                assert orientation(points[a], points[b], points[j]).sign() > 0
                count += 1
    return count


def maxima(points):
    answer = []
    for i, p in enumerate(points):
        counts = {}
        for j, q in enumerate(points):
            if i != j:
                d = distance(p, q)
                assert d.sign() > 0
                counts[d] = counts.get(d, 0)+1
        answer.append(max(counts.values()))
    return answer


def ceiling(R, P, expected):
    with zipfile.ZipFile(ROOT/'inputs/previous_packet.zip') as archive:
        raw = archive.read('erdos97_codesign_packet_2026_09_08/data/base9_circumcenters.json')
    cert = json.loads(raw)
    assert [tuple(R.q(x) for x in p) for p in cert['points']] == P
    assert [tuple(r['triple']) for r in cert['triples']] == list(combinations(range(9), 3))
    centers = [tuple(R.q(x) for x in r['point']) for r in cert['centers']]
    assert len(set(centers)) == len(centers)
    used = set()
    for row in cert['triples']:
        a, b, c = row['triple']
        k = row['center']
        assert 0 <= k < len(centers)
        used.add(k)
        z = centers[k]
        assert orientation(P[a], P[b], P[c]).sign() != 0
        assert distance(z, P[a]) == distance(z, P[b]) == distance(z, P[c])
        assert distance(z, P[a]).sign() > 0
    assert used == set(range(len(centers)))
    counts = {'old': 0, 'strict_containment': 0, 'closed_containment': 0}
    for z, row in zip(centers, cert['centers']):
        assert ('coincides_with' in row) != ('obstruction' in row)
        if 'coincides_with' in row:
            assert z == P[row['coincides_with']]
            counts['old'] += 1
        else:
            assert z not in P
            X = P+[z]
            ob = row['obstruction']
            a, b, c = ob['triangle']
            v = ob['target']
            assert len({a, b, c, v}) == 4 and all(0 <= k < 10 for k in (a,b,c,v))
            assert orientation(X[a], X[b], X[c]).sign() > 0
            signs = [orientation(X[a], X[b], X[v]).sign(),
                     orientation(X[b], X[c], X[v]).sign(),
                     orientation(X[c], X[a], X[v]).sign()]
            assert signs == ob['signs'] and min(signs) >= 0
            counts['strict_containment' if min(signs) > 0 else 'closed_containment'] += 1
    actual = {'triples': 84, 'centers': len(centers), **counts,
              'certificate_sha256': hashlib.sha256(raw).hexdigest()}
    assert actual == expected


def ray_slots(R, P, order):
    """Independent construction: sort first/second supporting-line exit times."""
    result = []
    for a, b in combinations(range(len(P)), 2):
        m = times(plus(P[a], P[b]), R(F(1, 2)))
        u = minus(P[b], P[a])
        v = (-3*u[1], u[0])
        for sign in (-1, 1):
            w = times(v, R(sign))
            exits = []
            for k in range(len(P)):
                p, q = P[order[k]], P[order[(k+1) % len(P)]]
                alpha = orientation(p, q, m)
                beta = area(minus(q, p), w)
                assert alpha.sign() >= 0
                assert alpha.sign() != 0 or beta.sign() != 0
                if beta.sign() < 0:
                    exits.append((-alpha/beta, k))
            exits.sort(key=lambda item: item[0])
            if len(exits) < 2:
                raise AssertionError('unbounded ray is not supported by this oracle')
            t1, cell = exits[0]
            t2 = exits[1][0]
            if t1 == t2:
                continue
            assert 0 <= t1 < t2
            lower, upper = (t1, t2) if sign == 1 else (-t2, -t1)
            result.append({'pair': [a, b], 'cell': cell,
                           'midpoint': [q.qjson() for q in m], 'direction': [q.qjson() for q in v],
                           'lower': lower.qjson(), 'upper': upper.qjson()})
    return sorted(result, key=lambda s: (s['pair'], s['cell']))


def decode_slot(R, item):
    return (item['pair'], tuple(R.q(x) for x in item['midpoint']),
            tuple(R.q(x) for x in item['direction']), R.q(item['lower']), R.q(item['upper']))


def graph(R, P, records):
    slots = [decode_slot(R, record) for record in records]
    edges = []
    counts = {'negative': 0, 'positive': 0, 'possible': 0}
    digest = hashlib.sha256()
    for i, (pair, m, v, left, right) in enumerate(slots):
        for j, (_, n, w, lower, upper) in enumerate(slots):
            if i == j:
                continue
            values = []
            for parameter in (left, right):
                x = plus(m, times(v, parameter))
                def f(t):
                    return distance(x, plus(n, times(w, t)))-distance(x, P[pair[0]])
                f0, fp, fm = f(R(0)), f(R(1)), f(R(-1))
                A, B = (fp+fm-2*f0)/2, (fp-fm)/2
                assert A.sign() > 0
                t = -B/(2*A)
                values.extend((f(lower), f(upper)))
                if lower < t < upper:
                    values.append(f(t))
            low, high = min(values), max(values)
            digest.update((json.dumps([i, j, low.qjson(), high.qjson()], separators=(',', ':'))+'\n').encode())
            if low.sign() <= 0 <= high.sign():
                edges.append([i,j])
                counts['possible'] += 1
            else:
                counts['negative' if high.sign() < 0 else 'positive'] += 1
    return edges, counts, digest.hexdigest()


def reverse_core(n, edges):
    active = set(range(n))
    while True:
        removed = False
        for i in sorted(active, reverse=True):
            if sum(a == i and b in active for a,b in edges) < 2:
                active.remove(i)
                removed = True
        if not removed:
            return sorted(active)


def check_core(report, R, P, records):
    detail = report['core_classification']
    active = report['remaining_core']
    assert active == [6,14,22]
    slots = [decode_slot(R, records[k]) for k in active]
    assert [s[0] for s in slots] == [[0,6],[1,7],[2,8]]
    corner_records = []
    for parameters in product(*[(s[3],s[4]) for s in slots]):
        points = [plus(s[1],times(s[2],t)) for s,t in zip(slots,parameters)]
        o = orientation(*points)
        y = points[0][1]-points[1][1]
        assert o.sign() > 0 and y.sign() > 0
        corner_records.append({'orientation':o.qjson(), 'y_difference':y.qjson()})
    assert corner_records == detail['corner_signs']
    _, m, v, lower, upper = slots[0]
    def ownside(t):
        z = plus(m,times(v,t))
        return 1-2*square(z)-2*z[0]
    C = ownside(R(0))
    A = (ownside(R(1))+ownside(R(-1))-2*C)/2
    B = (ownside(R(1))-ownside(R(-1)))/2
    assert [c.qjson() for c in (A,B,C)] == detail['quadratic']
    S = B*B-4*A*C
    assert S.sign() > 0 and S.qjson() == detail['discriminant']
    s0,s1 = S.coeff[:2]
    N = s0*s0-D*s1*s1
    assert N < 0 and str(N) == detail['discriminant_field_norm']
    R4 = ring(s0,s1)
    A4,B4,C4 = [R4.q(c) for c in detail['quadratic']]
    rec = records[active[0]]
    m4 = tuple(R4.q(x) for x in rec['midpoint'])
    v4 = tuple(R4.q(x) for x in rec['direction'])
    admissible = []
    assert [r['branch'] for r in detail['roots']] == [-1,1]
    for row in detail['roots']:
        t = (-B4+R4(0,0,row['branch']))/(2*A4)
        assert t == R4.e(row['parameter']) and A4*t*t+B4*t+C4 == 0
        inside = R4.q(rec['lower']) < t < R4.q(rec['upper'])
        assert inside == row['in_open_slot']
        z = plus(m4,times(v4,t))
        assert z == tuple(R4.e(x) for x in row['representative'])
        if inside:
            admissible.append(z)
    assert len(admissible) == 1
    z = admissible[0]
    points = seed(R4)+[z,rotate(z),rotate(rotate(z))]
    assert points == [tuple(R4.e(x) for x in p) for p in detail['points']]
    assert strict(points,detail['hull_order']) == detail['supporting_signs'] == 120
    assert maxima(points) == detail['maxima'] == [2]*3+[3]*3+[4]*6
    for row in detail['new_witness_rows']:
        i = row['source']
        assert i in (9,10,11)
        radius = 3*square(points[i])
        assert radius == R4.e(row['radius_squared'])
        witnesses = [j for j in range(12) if j != i and distance(points[i],points[j]) == radius]
        assert witnesses == row['witnesses'] and len(witnesses) == 4
        assert sum(j < 9 for j in witnesses) == 2
    numerator = z[0]+F(1,2)
    denominator = 3*(z[1]+F(1,2))
    t1 = R4(F(83,200),-F(3,200))
    assert numerator.sign() > 0 and denominator.sign() > 0 and numerator < t1*denominator
    assert numerator*numerator-(1-2*t1+3*t1*t1)*numerator*denominator+t1*t1*denominator*denominator == 0
    assert detail['next_recurrence_step_identified'] is True


def positive(R, record):
    A, B, C = (R(0),R(0)), (R(1),R(0)), (R(F(1,2)),R(F(1,2)))
    O = (R(F(1,2)),R(F(1,6)))
    X = [A,B,C]
    for t in (F(1,40),F(1,20)):
        a = (R((1-3*t*t)/(1+3*t*t)),R(-2*t/(1+3*t*t)))
        v = minus(a,O)
        X.extend((a,plus(O,rotate(v)),plus(O,rotate(rotate(v)))))
    P = X[3:]
    assert P == [tuple(R.q(z) for z in p) for p in record['old_points']]
    assert X[:3] == [tuple(R.q(z) for z in p) for p in record['rich_cap_points']]
    strict(P,record['old_order'])
    slots = ray_slots(R,P,record['old_order'])
    edges,counts,digest = graph(R,P,slots)
    core = reverse_core(len(slots),edges)
    assert len(slots) == record['slot_count'] and len(edges) == record['edge_count']
    assert counts == record['range_sign_counts'] and digest == record['range_digest']
    assert len(core) == record['core_size']
    for q,k in zip(X[:3],record['selected_slots']):
        pair,m,v,left,right = decode_slot(R,slots[k])
        assert pair == [j for j,p in enumerate(P) if distance(q,p) == 1]
        coordinate = 0 if v[0] != 0 else 1
        t = (q[coordinate]-m[coordinate])/v[coordinate]
        assert left < t < right and plus(m,times(v,t)) == q and k in core
    assert all([a,b] in edges for a in record['selected_slots'] for b in record['selected_slots'] if a != b)
    assert strict(X,[8,5,0,6,3,1,7,4,2]) == record['full_supporting_signs'] == 63
    assert maxima(X) == record['maxima'] == [4]*3+[2]*6


def check_discrete(report, records, edges, counts, digest):
    assert records == report['slots'] and len(records) == 42
    assert edges == report['possible_edges'] and len(edges) == 123
    assert counts == report['range_sign_counts'] and digest == report['range_digest']
    core = reverse_core(len(records), edges)
    assert core == report['remaining_core'] == [6,14,22]
    active = set(range(len(records)))
    for layer in report['peeling_layers']:
        expected = sorted(i for i in active if sum(a == i and b in active for a,b in edges) < 2)
        assert layer == expected and layer
        active.difference_update(layer)
    assert sorted(active) == core


def audit(report):
    global MAX_BITS
    MAX_BITS = 0
    R = ring()
    P = seed(R)
    order = [4,2,6,5,0,7,3,1,8]
    assert report['base_sha'] == '047d05149382e48b602b292df4b8fc9e2da560bb'
    assert strict(P,order) == report['seed_supporting_signs'] == 63
    ceiling(R,P,report['old_ceiling_replay'])
    records = ray_slots(R,P,order)
    edges,counts,digest = graph(R,P,records)
    check_discrete(report, records, edges, counts, digest)
    check_core(report,R,P,records)
    positive(R,report['positive_control'])
    return {'status':'passed','old_triples':84,'slots':42,'directed_interval_pairs':1722,
            'possible_edges':123,'remaining_core':[6,14,22],
            'largest_enclosure_precision_bits':MAX_BITS,
            'arithmetic':'flattened radical algebra and rational enclosures',
            'slot_method':'first and second ray exit times',
            'graph_method':'endpoint interpolation and reverse sequential peeling',
            'external_mathematical_review':False,'formalized_in_Lean':False}


if __name__ == '__main__':
    import sys
    report = json.loads((ROOT/'data/verification.json').read_text())
    result = json.dumps(audit(report),indent=2,sort_keys=True)+'\n'
    if '--write' in sys.argv:
        (ROOT/'data/oracle_report.json').write_text(result)
    else:
        assert (ROOT/'data/oracle_report.json').read_text() == result
    print(result)
