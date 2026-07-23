"""Doubled-Danzer 18-gon C3 slice model for Erdos Problem #97.

This module implements the C3-equivariant doubling of the Danzer-type
nonagon proposed in the 2026-07-13 handoff and tested in the 2026-07-22
continuation run.  No counterexample is claimed; the continuation test is
negative at this base family (see docs/danzer18-doubling-failed-approach.md).

Base nonagon (k=3 witness structure, every vertex has 3 equidistant others):
9 vertices in 3 rotational orbits, orbit m has radius r_m and phase phi_m,
vertex (m, j) = r_m * (cos(phi_m + 2*pi*j/3), sin(phi_m + 2*pi*j/3)) with
j in {0, 1, 2} and flat label v = 3*m + j.  Gauge r_0 = 1, phi_0 = 0.  Each
vertex sees its two orbit mates at distance sqrt(3)*r_m, and one tuned
cross-orbit witness closes the k=3 structure:

    CROSS = {0: (2, 1), 1: (0, 0), 2: (1, 0)}

meaning the third witness of an orbit-m center is vertex (vm, j0 + tv) for
(vm, tv) = CROSS[m] relative to the center's own j0.  The base equations
d^2(center, cross) = 3 r_m^2 leave a 1-parameter family after the gauge.

Doubled 18-gon C3 slice: two copies s in {0, 1} of the nonagon; slice
coordinates (12 total) are (r, phi) pairs per (orbit, copy), with the pair
for (m, s) stored at indices 2*(2m+s) and 2*(2m+s)+1.  The collision point
has both copies at the base values.

Witness pool for center class (m, s), in fixed order:

    pool[0..1] = own-copy mates (m, s, 1), (m, s, 2)
    pool[2..3] = twin-copy mates (m, 1-s, 1), (m, 1-s, 2)
    pool[4..5] = cross-witness copies (vm, 0, tv), (vm, 1, tv)

An assignment picks one of the C(6,4) = 15 4-subsets per class, with
subsets enumerated in lexicographic order over pool indices and classes
ordered (m=0,s=0), (m=0,s=1), (m=1,s=0), (m=1,s=1), (m=2,s=0), (m=2,s=1).
Each class contributes 3 chained squared-distance differences, giving 18
equations on the 12 slice coordinates.
"""

from __future__ import annotations

import itertools
import math

OMEGA = 2.0 * math.pi / 3.0
CROSS = {0: (2, 1), 1: (0, 0), 2: (1, 0)}
SUBSETS = tuple(itertools.combinations(range(6), 4))
NCLASS = 6

# Base nonagon solved to 50 digits (Newton-polished at mpmath dps=60 from the
# externally supplied seed; scripts/check_danzer18_base_nonagon.py re-derives
# and verifies these).  Gauge r0 = 1, phi0 = 0.
BASE_R1 = "1.0232765362286151212279138415749844121975239899365"
BASE_R2 = "0.84430467659553225135054203657922644411506189825712"
BASE_PH1 = "2.1348899349009594429280251524108783933547943057754"
BASE_PH2 = "0.34318985719866858113539443829133834740024089795205"

# Base-family tangent (d r1, d r2, d phi1, d phi2) in the gauge
# d r0 = d phi0 = 0, unit-normalized (kernel of the base 3x4 Jacobian).
BASE_FLEX4 = (
    -0.1182145033127394155329449534018426269757,
    0.3127831033657804570079149148278107813878,
    -0.2066841471652627621752361656160141265071,
    -0.9194964517419095646176069084998367568315,
)

# The 19 externally supplied survivor assignments (class order as above).
EXTERNAL_SURVIVORS = (
    (1, 2, 1, 2, 1, 2), (1, 2, 2, 1, 2, 1), (1, 3, 11, 1, 5, 5),
    (1, 10, 0, 0, 9, 0), (2, 1, 1, 2, 2, 1), (2, 1, 2, 1, 1, 2),
    (3, 4, 3, 4, 3, 4), (3, 4, 4, 3, 4, 3), (4, 3, 3, 4, 4, 3),
    (4, 3, 4, 3, 3, 4), (4, 6, 0, 0, 3, 1), (5, 4, 0, 0, 12, 7),
    (5, 5, 6, 10, 6, 11), (5, 5, 10, 1, 6, 12), (6, 11, 5, 5, 1, 10),
    (10, 0, 5, 5, 0, 0), (10, 8, 5, 5, 2, 11), (11, 0, 0, 0, 10, 14),
    (13, 1, 4, 3, 0, 0),
)

# The four rank-6 assignments recorded by the external census.
EXPECTED_RANK6 = (
    (0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 5, 5),
    (0, 0, 5, 5, 0, 0), (5, 5, 0, 0, 0, 0),
)

EXPECTED_CENSUS_COUNTS = {9: 11206584, 8: 182540, 7: 1497, 6: 4}


def idx_r(m: int, s: int) -> int:
    return 2 * (2 * m + s)


def idx_phi(m: int, s: int) -> int:
    return 2 * (2 * m + s) + 1


def base_floats() -> dict:
    return {
        "r": [1.0, float(BASE_R1), float(BASE_R2)],
        "phi": [0.0, float(BASE_PH1), float(BASE_PH2)],
    }


def pool_vertices(m: int, s: int) -> list[tuple[int, int, int]]:
    """The 6 pool vertices (m', s', j') for center class (m, s)."""
    vm, tv = CROSS[m]
    return [
        (m, s, 1), (m, s, 2),
        (m, 1 - s, 1), (m, 1 - s, 2),
        (vm, 0, tv), (vm, 1, tv),
    ]


def collision_x(base: dict | None = None) -> list[float]:
    """12-coordinate slice vector at the collision point."""
    if base is None:
        base = base_floats()
    x = [0.0] * 12
    for m in range(3):
        for s in range(2):
            x[idx_r(m, s)] = base["r"][m]
            x[idx_phi(m, s)] = base["phi"][m]
    return x


def vertex_xy(x, m: int, s: int, j: int, cos=math.cos, sin=math.sin):
    r = x[idx_r(m, s)]
    ph = x[idx_phi(m, s)] + OMEGA * j
    return (r * cos(ph), r * sin(ph))


def d2_and_grad(x, v1, v2, cos=math.cos, sin=math.sin, omega=OMEGA):
    """Squared distance between slice vertices and its 12-gradient.

    Works for float inputs (default trig) and for mpmath inputs when the
    mpmath cos/sin (and an mpmath omega = 2*pi/3) are passed explicitly.
    """
    m1, s1, j1 = v1
    m2, s2, j2 = v2
    ir1, ip1 = idx_r(m1, s1), idx_phi(m1, s1)
    ir2, ip2 = idx_r(m2, s2), idx_phi(m2, s2)
    r1, p1 = x[ir1], x[ip1]
    r2, p2 = x[ir2], x[ip2]
    delta = (p2 + omega * j2) - (p1 + omega * j1)
    c, sn = cos(delta), sin(delta)
    val = r1 * r1 + r2 * r2 - 2 * r1 * r2 * c
    g = [0 * val] * 12
    g[ir1] = g[ir1] + 2 * r1 - 2 * r2 * c
    g[ir2] = g[ir2] + 2 * r2 - 2 * r1 * c
    g[ip1] = g[ip1] - 2 * r1 * r2 * sn
    g[ip2] = g[ip2] + 2 * r1 * r2 * sn
    return val, g


def class_pool_values(x, m: int, s: int, cos=math.cos, sin=math.sin,
                      omega=OMEGA):
    center = (m, s, 0)
    vals, grads = [], []
    for w in pool_vertices(m, s):
        v, g = d2_and_grad(x, center, w, cos=cos, sin=sin, omega=omega)
        vals.append(v)
        grads.append(g)
    return vals, grads


def assignment_residuals(x, assign, cos=math.cos, sin=math.sin,
                         omega=OMEGA):
    """The 18 chained squared-distance differences for an assignment."""
    out = []
    for c in range(NCLASS):
        m, s = divmod(c, 2)
        vals, _ = class_pool_values(x, m, s, cos=cos, sin=sin, omega=omega)
        sub = SUBSETS[assign[c]]
        for t in range(3):
            out.append(vals[sub[t]] - vals[sub[t + 1]])
    return out


def assignment_jacobian_rows(x, assign, cos=math.cos, sin=math.sin,
                             omega=OMEGA):
    """18x12 Jacobian rows (list of lists) of assignment_residuals at x."""
    rows = []
    for c in range(NCLASS):
        m, s = divmod(c, 2)
        _, grads = class_pool_values(x, m, s, cos=cos, sin=sin, omega=omega)
        sub = SUBSETS[assign[c]]
        for t in range(3):
            ga, gb = grads[sub[t]], grads[sub[t + 1]]
            rows.append([ga[k] - gb[k] for k in range(12)])
    return rows


def pair_separations(x) -> list[float]:
    """Geometric distance between the two copies of each orbit (at j=0)."""
    out = []
    for m in range(3):
        a = vertex_xy(x, m, 0, 0)
        b = vertex_xy(x, m, 1, 0)
        out.append(math.hypot(a[0] - b[0], a[1] - b[1]))
    return out


# ---------------------------------------------------------------------------
# numpy layer (kept import-light so the pure-math helpers above stay usable
# without numpy)
# ---------------------------------------------------------------------------

def numpy_blocks(x):
    """All 90 collision Jacobian blocks as an array of shape (6, 15, 3, 12)."""
    import numpy as np

    blocks = np.zeros((6, 15, 3, 12))
    for c in range(NCLASS):
        m, s = divmod(c, 2)
        _, grads = class_pool_values(x, m, s)
        garr = np.array(grads)
        for k, sub in enumerate(SUBSETS):
            for t in range(3):
                blocks[c, k, t] = garr[sub[t]] - garr[sub[t + 1]]
    return blocks


def trivial_directions(base: dict | None = None, flex4=BASE_FLEX4):
    """Orthonormal basis (12x3) of the trivial collision kernel: rotation,
    scaling, and the diagonal base-family flex."""
    import numpy as np

    if base is None:
        base = base_floats()
    rot = np.zeros(12)
    sca = np.zeros(12)
    flex = np.zeros(12)
    dr = [0.0, flex4[0], flex4[1]]
    dph = [0.0, flex4[2], flex4[3]]
    for m in range(3):
        for s in range(2):
            rot[idx_phi(m, s)] = 1.0
            sca[idx_r(m, s)] = base["r"][m]
            flex[idx_r(m, s)] = dr[m]
            flex[idx_phi(m, s)] = dph[m]
    q, _ = np.linalg.qr(np.stack([rot, sca, flex], axis=1))
    return q


def split_direction_matrix():
    """Matrix (6x12) whose rows are the normalized anti-diagonal split
    directions u_r^m, u_phi^m for orbits m = 0, 1, 2 (rows 2m, 2m+1)."""
    import numpy as np

    p = np.zeros((6, 12))
    inv = 1.0 / math.sqrt(2.0)
    for m in range(3):
        p[2 * m, idx_r(m, 0)] = inv
        p[2 * m, idx_r(m, 1)] = -inv
        p[2 * m + 1, idx_phi(m, 0)] = inv
        p[2 * m + 1, idx_phi(m, 1)] = -inv
    return p


def projected_blocks(x=None, base=None):
    """Blocks (6, 15, 3, 9) with the trivial 3-space projected out, plus the
    complement basis B (12x9) used for the projection."""
    import numpy as np

    if base is None:
        base = base_floats()
    if x is None:
        x = collision_x(base)
    blocks = numpy_blocks(x)
    t = trivial_directions(base)
    u, _, _ = np.linalg.svd(t, full_matrices=True)
    b = u[:, 3:]
    return np.einsum("ckij,jl->ckil", blocks, b), b


def assignment_rank_and_kernel(assign, pblocks, b, tol=1e-8):
    """(rank, kernel) of the projected 18x9 collision Jacobian.  The kernel
    rows are returned in the full 12-coordinate space (orthogonal to the
    trivial 3-space by construction)."""
    import numpy as np

    j = np.concatenate([pblocks[c, assign[c]] for c in range(6)], axis=0)
    _, sv, vt = np.linalg.svd(j)
    rank = int((sv > tol * sv[0]).sum())
    return rank, vt[rank:, :] @ b.T


def kernel_split_norms(kernel, psplit=None):
    """Per-orbit split-component norms of a kernel (rows = basis vectors)."""
    import numpy as np

    if psplit is None:
        psplit = split_direction_matrix()
    comp = kernel @ psplit.T
    return np.sqrt((comp ** 2).reshape(-1, 3, 2).sum(axis=(0, 2)))


def decode_assignment(index: int) -> tuple[int, ...]:
    """Inverse of the base-15 big-endian assignment index used in the census."""
    digits = []
    for c in range(6):
        digits.append((index // 15 ** (5 - c)) % 15)
    return tuple(digits)


# ---------------------------------------------------------------------------
# mpmath layer
# ---------------------------------------------------------------------------

def mp_base(dps: int = 60):
    """Newton-polish the base nonagon at the requested precision.

    Returns (x4, residuals) where x4 = [r1, r2, phi1, phi2] as mpf values and
    residuals are the three cross-witness equation values at x4.
    """
    from mpmath import mp, mpf, matrix, lu_solve

    mp.dps = dps
    x = [mpf(BASE_R1), mpf(BASE_R2), mpf(BASE_PH1), mpf(BASE_PH2)]
    for _ in range(6):
        f = mp_base_residuals(x)
        j = mp_base_jacobian(x)
        jt = j.T
        y = lu_solve(j * jt, matrix(f))
        dx = jt * y
        x = [x[k] - dx[k] for k in range(4)]
    return x, mp_base_residuals(x)


def mp_base_vertices(x4):
    from mpmath import cos, sin, pi

    om = 2 * pi / 3
    r = [x4[0] * 0 + 1, x4[0], x4[1]]
    ph = [x4[0] * 0, x4[2], x4[3]]
    pts = []
    for m in range(3):
        for j in range(3):
            a = ph[m] + om * j
            pts.append((r[m] * cos(a), r[m] * sin(a)))
    return pts


def mp_base_residuals(x4):
    from mpmath import cos, sin, pi

    om = 2 * pi / 3
    r = [x4[0] * 0 + 1, x4[0], x4[1]]
    ph = [x4[0] * 0, x4[2], x4[3]]
    out = []
    for m in range(3):
        vm, tv = CROSS[m]
        cx = r[m] * cos(ph[m])
        cy = r[m] * sin(ph[m])
        wx = r[vm] * cos(ph[vm] + om * tv)
        wy = r[vm] * sin(ph[vm] + om * tv)
        out.append((cx - wx) ** 2 + (cy - wy) ** 2 - 3 * r[m] ** 2)
    return out


def mp_base_jacobian(x4, h_exp: int | None = None):
    from mpmath import mp, mpf, matrix

    if h_exp is None:
        h_exp = -(mp.dps // 2)
    h = mpf(10) ** h_exp
    j = matrix(3, 4)
    for k in range(4):
        xp = list(x4)
        xm = list(x4)
        xp[k] += h
        xm[k] -= h
        fp = mp_base_residuals(xp)
        fm = mp_base_residuals(xm)
        for i in range(3):
            j[i, k] = (fp[i] - fm[i]) / (2 * h)
    return j


def mp_collision_x(x4):
    from mpmath import mpf

    r = [mpf(1), x4[0], x4[1]]
    ph = [mpf(0), x4[2], x4[3]]
    x = [mpf(0)] * 12
    for m in range(3):
        for s in range(2):
            x[idx_r(m, s)] = r[m]
            x[idx_phi(m, s)] = ph[m]
    return x


def mp_assignment_residuals(x, assign):
    from mpmath import cos, sin, pi

    return assignment_residuals(x, assign, cos=cos, sin=sin, omega=2 * pi / 3)


def mp_assignment_jacobian(x, assign):
    from mpmath import cos, sin, pi, matrix

    rows = assignment_jacobian_rows(x, assign, cos=cos, sin=sin,
                                    omega=2 * pi / 3)
    j = matrix(18, 12)
    for i in range(18):
        for k in range(12):
            j[i, k] = rows[i][k]
    return j
