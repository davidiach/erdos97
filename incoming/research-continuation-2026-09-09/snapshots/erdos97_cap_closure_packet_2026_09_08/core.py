"""Exact finite reduction for two-old-supported rich caps over the fixed seed.

All geometry uses the inherited Q(sqrt(721)) implementation. Cartesian points
are stored as (x,y), meaning (x,sqrt(3)*y). No optimizer or float is used here.
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import combinations, product
from pathlib import Path
import hashlib
import json
import sys
import zipfile

if sys.flags.optimize:
    raise RuntimeError('Run exact checks without Python -O or -OO')

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'prior_math'))
from quadratic import Q, F, base9, cycle9, add, sub, mul, cross, turn, dot, norm, dist, hull  # noqa: E402
from extensions import E  # noqa: E402

BASE_SHA = '047d05149382e48b602b292df4b8fc9e2da560bb'
ORDER = [4, 2, 6, 5, 0, 7, 3, 1, 8]


def rq(value):
    if not isinstance(value, list) or len(value) != 2 or not all(isinstance(s, str) for s in value):
        raise ValueError('exact coefficients must be two rational strings')
    return Q(F(value[0]), F(value[1]))


def point_json(point):
    return [x.json() for x in point]


def strict_check(points, order):
    """Works also in the non-hashable inherited quadratic extension E."""
    n = len(points)
    if sorted(order) != list(range(n)):
        raise ValueError('boundary order is not a permutation')
    for a, b in combinations(points, 2):
        if not dist(a, b) > 0:
            raise ValueError('coincident points')
    count = 0
    for k, a in enumerate(order):
        b = order[(k + 1) % n]
        for j in range(n):
            if j not in (a, b):
                if not turn(points[a], points[b], points[j]) > 0:
                    raise ValueError('nonpositive supporting sign')
                count += 1
    return count


def maxima(points):
    result = []
    for i, p in enumerate(points):
        ds = sorted(dist(p, q) for j, q in enumerate(points) if i != j)
        best = run = 0
        previous = None
        for d in ds:
            if not d > 0:
                raise ValueError('nonpositive separation')
            run = run + 1 if previous is not None and d == previous else 1
            best = max(best, run)
            previous = d
        result.append(best)
    return result


def old_ceiling():
    """Replay the supplied 84-triple certificate rather than assuming its claim."""
    with zipfile.ZipFile(ROOT / 'inputs/previous_packet.zip') as archive:
        raw = archive.read('erdos97_codesign_packet_2026_09_08/data/base9_circumcenters.json')
    cert = json.loads(raw)
    P = base9()
    assert cert['base_sha'] == BASE_SHA
    assert [tuple(map(rq, p)) for p in cert['points']] == P
    assert [tuple(row['triple']) for row in cert['triples']] == list(combinations(range(9), 3))
    centers = [tuple(map(rq, row['point'])) for row in cert['centers']]
    assert len(set(centers)) == len(centers)
    used = set()
    for row in cert['triples']:
        a, b, c = row['triple']
        k = row['center']
        assert isinstance(k, int) and 0 <= k < len(centers)
        used.add(k)
        z = centers[k]
        assert turn(P[a], P[b], P[c]) != 0
        assert 0 < dist(z, P[a]) == dist(z, P[b]) == dist(z, P[c])
    assert used == set(range(len(centers)))
    counts = {'old': 0, 'strict_containment': 0, 'closed_containment': 0}
    for z, row in zip(centers, cert['centers']):
        assert ('coincides_with' in row) != ('obstruction' in row)
        if 'coincides_with' in row:
            k = row['coincides_with']
            assert isinstance(k, int) and 0 <= k < 9 and z == P[k]
            counts['old'] += 1
        else:
            assert z not in P
            points = P + [z]
            ob = row['obstruction']
            v = ob['target']
            a, b, c = ob['triangle']
            assert len({v, a, b, c}) == 4 and all(0 <= k < 10 for k in (v, a, b, c))
            assert turn(points[a], points[b], points[c]) > 0
            signs = [turn(points[a], points[b], points[v]).sign(),
                     turn(points[b], points[c], points[v]).sign(),
                     turn(points[c], points[a], points[v]).sign()]
            assert signs == ob['signs'] and min(signs) >= 0
            counts['strict_containment' if min(signs) > 0 else 'closed_containment'] += 1
    return {'triples': 84, 'centers': len(centers), **counts,
            'certificate_sha256': hashlib.sha256(raw).hexdigest()}


@dataclass(frozen=True)
class Slot:
    pair: tuple[int, int]
    cell: int
    midpoint: tuple
    direction: tuple
    lower: Q
    upper: Q

    def point(self, parameter):
        return add(self.midpoint, mul(self.direction, parameter))

    def json(self):
        return {'pair': list(self.pair), 'cell': self.cell,
                'midpoint': point_json(self.midpoint), 'direction': point_json(self.direction),
                'lower': self.lower.json(), 'upper': self.upper.json()}


def build_slots(P, order):
    """Clip every old-pair bisector against every possible insertion cell.

Only bounded cells are implemented in this packet. Unbounded input raises an
error; it is never silently discarded. The theorem's general finite bound does
not require boundedness, while the two supplied inputs have bounded slots.
    """
    strict_check(P, order)
    result = []
    n = len(P)
    for a, b in combinations(range(n), 2):
        m = mul(add(P[a], P[b]), Q(F(1, 2)))
        u = sub(P[b], P[a])
        v = (-3 * u[1], u[0])
        assert norm(v) > 0 and dot(v, u) == 0
        for cell in range(n):
            lower = upper = None
            impossible = False
            for k in range(n):
                p, q = P[order[k]], P[order[(k + 1) % n]]
                alpha = turn(p, q, m)
                beta = cross(sub(q, p), v)
                if k == cell:
                    alpha, beta = -alpha, -beta
                if beta == 0:
                    # All inequalities are strict in an admissible extension.
                    if alpha <= 0:
                        impossible = True
                        break
                elif beta > 0:
                    bound = -alpha / beta
                    if lower is None or bound > lower:
                        lower = bound
                else:
                    bound = -alpha / beta
                    if upper is None or bound < upper:
                        upper = bound
            if impossible or (lower is not None and upper is not None and lower >= upper):
                continue
            if lower is None or upper is None:
                raise NotImplementedError('unbounded slot; no exclusion is asserted')
            # The midpoint is in the old hull. An admissible slot lies on one ray.
            assert lower >= 0 or upper <= 0
            result.append(Slot((a, b), cell, m, v, lower, upper))
    return result


def interval_range(P, source, target):
    """Exact extrema of squared-distance difference on a closed rectangle.

F(s,t)=|x(s)-y(t)|^2-|x(s)-p_a|^2 is affine in s and convex
quadratic in t. Thus source endpoints and target endpoints/stationary points
exhaust its extrema. Closed rectangles deliberately overapproximate slots.
    """
    A = norm(target.direction)
    assert A > 0
    values = []
    for s in (source.lower, source.upper):
        x = source.point(s)
        B = 2 * dot(target.direction, sub(target.midpoint, x))
        C = dist(x, target.midpoint) - dist(x, P[source.pair[0]])
        stationary = -B / (2 * A)
        parameters = [target.lower, target.upper]
        if target.lower < stationary < target.upper:
            parameters.append(stationary)
        values.extend(A * t * t + B * t + C for t in parameters)
    return min(values), max(values)


def graph_data(P, slots):
    edges = []
    counts = {'negative': 0, 'positive': 0, 'possible': 0}
    digest = hashlib.sha256()
    for i, source in enumerate(slots):
        for j, target in enumerate(slots):
            if i == j:
                continue
            lo, hi = interval_range(P, source, target)
            digest.update((json.dumps([i, j, lo.json(), hi.json()], separators=(',', ':')) + '\n').encode())
            if lo <= 0 <= hi:
                edges.append((i, j))
                counts['possible'] += 1
            else:
                counts['negative' if hi < 0 else 'positive'] += 1
    return edges, counts, digest.hexdigest()


def peel(vertices, edges, minimum=2):
    active = set(vertices)
    layers = []
    while True:
        removed = sorted(i for i in active if sum(a == i and b in active for a, b in edges) < minimum)
        if not removed:
            return sorted(active), layers
        layers.append(removed)
        active.difference_update(removed)


def rotate(point):
    return ((-point[0] - 3 * point[1]) * F(1, 2),
            (point[0] - point[1]) * F(1, 2))


def classify_core(P, slots, active):
    assert active == [6, 14, 22]
    core = [slots[i] for i in active]
    assert [s.pair for s in core] == [(0, 6), (1, 7), (2, 8)]
    assert [s.cell for s in core] == [6, 0, 3]
    # The entire three-slot box has the indicated orientation and y-order.
    corners = []
    for s, t, u in product(*[(q.lower, q.upper) for q in core]):
        a, b, c = [q.point(v) for q, v in zip(core, (s, t, u))]
        determinant = turn(a, b, c)
        assert determinant > 0 and a[1] > b[1]
        corners.append({'orientation': determinant.json(), 'y_difference': (a[1] - b[1]).json()})
    # Source 0 must be concentric, by the written equilateral/anchor argument.
    # Its own-side equation is 1 - 2|z|^2 - 2 z_x = 0 on its bisector slot.
    source = core[0]
    m, v = source.midpoint, source.direction
    A = -2 * norm(v)
    B = -4 * dot(m, v) - 2 * v[0]
    C = 1 - 2 * norm(m) - 2 * m[0]
    discriminant = B * B - 4 * A * C
    assert A < 0 and discriminant > 0
    field_norm = discriminant.a**2 - F(721) * discriminant.b**2
    assert field_norm < 0  # In particular, the final radical is not in Q(sqrt721).
    results = []
    selected_points = None
    for branch in (-1, 1):
        t = E(-B / (2 * A), Q(branch) / (2 * A), discriminant)
        assert t * t * A + t * B + C == 0
        in_slot = t > source.lower and t < source.upper
        z = (E(m[0], 0, discriminant) + t * v[0],
             E(m[1], 0, discriminant) + t * v[1])
        old = [(E(x, 0, discriminant), E(y, 0, discriminant)) for x, y in P]
        new = [z, rotate(z), rotate(rotate(z))]
        assert dist(z, old[0]) == dist(z, old[6]) == 3 * norm(z)
        results.append({'branch': branch, 'parameter': t.json(), 'in_open_slot': in_slot,
                        'representative': point_json(z)})
        if in_slot:
            assert selected_points is None
            selected_points = old + new
    assert [r['in_open_slot'] for r in results] == [False, True]
    order = [4, 10, 2, 6, 5, 11, 0, 7, 3, 9, 1, 8]
    signs = strict_check(selected_points, order)
    census = maxima(selected_points)
    assert census == [2]*3 + [3]*3 + [4]*6
    witness_rows = []
    for i in range(9, 12):
        r2 = 3 * norm(selected_points[i])
        row = [j for j in range(12) if j != i and dist(selected_points[i], selected_points[j]) == r2]
        assert len(row) == 4 and sum(j < 9 for j in row) == 2
        witness_rows.append({'source': i, 'witnesses': row, 'radius_squared': r2.json()})
    # Exact identification with the next original recurrence step.
    z = selected_points[9]
    # Rational circle parameter t = (1/2 - z_y)/(z_x + 1/2), avoiding E division.
    # Instead certify the quadratic of the next parameter using the equivalent
    # rationalization t=(z_x+1/2)/(3*(z_y+1/2)) by cross multiplication.
    numerator = z[0] + F(1, 2)
    denominator = 3 * (z[1] + F(1, 2))
    t1 = Q(F(83, 200), -F(3, 200))
    recurrence_B = 1 - 2*t1 + 3*t1*t1
    assert numerator > 0 and denominator > 0
    assert numerator < denominator * t1
    assert numerator*numerator - numerator*denominator*recurrence_B + denominator*denominator*(t1*t1) == 0
    return {'corner_signs': corners, 'quadratic': [A.json(), B.json(), C.json()],
            'discriminant': discriminant.json(), 'discriminant_field_norm': str(field_norm),
            'roots': results, 'points': [point_json(p) for p in selected_points],
            'hull_order': order, 'supporting_signs': signs, 'maxima': census,
            'new_witness_rows': witness_rows, 'next_recurrence_step_identified': True}


def positive_control():
    """The former middle-cycle control is a genuinely admissible rich 3-cap."""
    X = cycle9()
    P = X[3:]
    old_order = hull(P)
    slots = build_slots(P, old_order)
    edges, counts, digest = graph_data(P, slots)
    active, layers = peel(range(len(slots)), edges)
    selected = []
    for i, q in enumerate(X[:3]):
        old_witnesses = tuple(j for j, p in enumerate(P) if dist(q, p) == 1)
        assert len(old_witnesses) == 2
        matches = []
        for k, slot in enumerate(slots):
            if slot.pair != old_witnesses:
                continue
            coordinate = 0 if slot.direction[0] != 0 else 1
            t = (q[coordinate] - slot.midpoint[coordinate]) / slot.direction[coordinate]
            if slot.point(t) == q and slot.lower < t < slot.upper:
                matches.append(k)
        assert len(matches) == 1
        selected.extend(matches)
    assert len(set(selected)) == 3 and set(selected) <= set(active)
    assert all((i, j) in edges for i in selected for j in selected if i != j)
    return {'old_points': [point_json(p) for p in P], 'old_order': old_order,
            'rich_cap_points': [point_json(p) for p in X[:3]],
            'slot_count': len(slots), 'edge_count': len(edges), 'core_size': len(active),
            'selected_slots': selected, 'range_sign_counts': counts, 'range_digest': digest,
            'full_supporting_signs': strict_check(X, [8, 5, 0, 6, 3, 1, 7, 4, 2]),
            'maxima': maxima(X)}


def run():
    P = base9()
    seed_signs = strict_check(P, ORDER)
    ceiling = old_ceiling()
    slots = build_slots(P, ORDER)
    edges, counts, digest = graph_data(P, slots)
    active, layers = peel(range(len(slots)), edges)
    assert len(slots) == 42 and len(edges) == 123
    assert [len(layer) for layer in layers] == [21, 15, 3]
    return {'status': 'restricted all-cap-size classification; review pending; not a solution of Erdos97',
            'base_sha': BASE_SHA, 'seed_supporting_signs': seed_signs, 'old_ceiling_replay': ceiling,
            'slots': [s.json() for s in slots], 'possible_edges': [list(e) for e in edges],
            'range_sign_counts': counts, 'range_digest': digest,
            'peeling_layers': layers, 'remaining_core': active,
            'core_classification': classify_core(P, slots, active),
            'positive_control': positive_control()}


def canonical(report):
    return json.dumps(report, indent=2, sort_keys=True) + '\n'
