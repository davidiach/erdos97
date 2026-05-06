"""Strategy L9: take 7-vertex hull of Danzer (drop interior v4 and one more),
then add 3 additional vertices to make a 10-vertex polygon with E=4.
This gives 10 points = 20 dof, 10×1 = 10 4-window constraints, plus 10 strict
convexity constraints. Possibly feasible.

Strategy L10: enforce 3-fold rotational symmetry on a 12-point set
(4 concentric triangles). 4 radii + 3 angles = 7 dof, with 4 4-window constraints
+ convexity. Also enforce the 4-window constraint locally.
"""
import math
import numpy as np
from scipy.optimize import minimize, NonlinearConstraint

S3 = math.sqrt(3.0)


def pair_dists(P):
    diff = P[:, None] - P[None, :]
    return np.sqrt((diff ** 2).sum(-1))


def diagnostics(P, tol=1e-7):
    n = P.shape[0]
    D = pair_dists(P)
    sizes = []
    for v in range(n):
        ds = sorted([D[v, u] for u in range(n) if u != v])
        groups = []
        cur = [ds[0]]
        for x in ds[1:]:
            if abs(x - cur[-1]) <= tol:
                cur.append(x)
            else:
                groups.append(cur); cur = [x]
        groups.append(cur)
        sizes.append(max(len(g) for g in groups))
    c = P.mean(0)
    angles = np.arctan2(P[:, 1] - c[1], P[:, 0] - c[0])
    order = np.argsort(angles)
    Q = P[order]
    cross_min = float("inf")
    for i in range(n):
        a, b, d = Q[i], Q[(i + 1) % n], Q[(i + 2) % n]
        v1 = b - a; v2 = d - b
        cr = v1[0] * v2[1] - v1[1] * v2[0]
        cross_min = min(cross_min, cr)
    rms_4 = 0.0
    max_4 = 0.0
    for v in range(n):
        ds = np.sort(np.array([D[v, u] for u in range(n) if u != v]))
        if len(ds) >= 4:
            wins = ds[3:] - ds[:-3]
            best = float(wins.min())
        else:
            best = float('inf')
        rms_4 += best ** 2; max_4 = max(max_4, best)
    rms_4 = math.sqrt(rms_4/n)
    return {
        "n": int(n), "E": sizes, "min_E": min(sizes), "max_E": max(sizes),
        "convex": cross_min > 0, "convex_margin": float(cross_min),
        "rms_4_window": rms_4, "max_4_window": max_4,
        "min_pair_dist": float(np.sort(D[~np.eye(n, dtype=bool)])[0]),
    }


def loss_4window_convex(P, init_order, conv_min=0.05, sep_min=0.2,
                        conv_w=10.0, sep_w=100.0):
    n = P.shape[0]
    Q = P[init_order]
    cnv_pen = 0.0
    for i in range(n):
        a, b, d = Q[i], Q[(i + 1) % n], Q[(i + 2) % n]
        v1 = b - a; v2 = d - b
        cr = v1[0] * v2[1] - v1[1] * v2[0]
        if cr < conv_min:
            cnv_pen += (conv_min - cr) ** 2
    diff = P[:, None] - P[None, :]
    D2 = (diff ** 2).sum(-1) + np.eye(n) * 1e6
    D = np.sqrt(D2)
    min_d = D.min()
    sep_pen = max(0.0, sep_min - min_d) ** 2
    s = 0.0
    for v in range(n):
        ds = np.sort(np.array([D[v, u] for u in range(n) if u != v]))
        if len(ds) >= 4:
            wins = ds[3:] - ds[:-3]
            s += wins.min() ** 2
    return float(s + conv_w * cnv_pen + sep_w * sep_pen)


def attempt_l9_seven_plus_three(seed=0):
    """Take 7-hull of Danzer, perturb + add 3 inner vertices,
    optimize 4-window constraint while preserving strict convexity."""
    pts = [
        (-S3, -1.0), (S3, -1.0), (0.0, 2.0),
        (-8991.0/10927.0 * S3, -26503.0/10927.0),
        (-17747.0/10927.0 * S3,   -235.0/10927.0),
        (-8756.0/10927.0 * S3,  26738.0/10927.0),
        (-10753.0/18529.0 * S3, -44665.0/18529.0),
        ( 27709.0/18529.0 * S3,   6203.0/18529.0),
        (-16956.0/18529.0 * S3,  38462.0/18529.0),
    ]
    P_full = np.array(pts)
    # Convex hull
    from scipy.spatial import ConvexHull
    hull = ConvexHull(P_full)
    hull_pts = P_full[hull.vertices]
    # Sort by angle
    c = hull_pts.mean(0)
    ang = np.arctan2(hull_pts[:, 1] - c[1], hull_pts[:, 0] - c[0])
    hull_pts = hull_pts[np.argsort(ang)]
    n_hull = hull_pts.shape[0]  # 7

    rng = np.random.default_rng(seed)
    # Add 3 new vertices on the hull boundary (between existing ones, slightly outside)
    # then make a 10-gon and optimize.
    n = 10
    best = None
    for trial in range(30):
        # Pick 3 random insertion edges and add interpolated points pushed out
        new = []
        # Insert at edges 0->1, 2->3, 5->6 (arbitrary)
        edges = sorted(rng.choice(n_hull, size=3, replace=False))
        new_pts = []
        idx = 0
        for i in range(n_hull):
            new_pts.append(hull_pts[i])
            if idx < 3 and i == edges[idx]:
                # interpolate
                t = 0.5 + 0.05 * rng.standard_normal()
                next_i = (i + 1) % n_hull
                mid = (1 - t) * hull_pts[i] + t * hull_pts[next_i]
                # push outward from centroid
                outward = (mid - c)
                outward = outward / np.linalg.norm(outward)
                mid = mid + outward * 0.1 * rng.standard_normal()
                new_pts.append(mid)
                idx += 1
        P0 = np.array(new_pts)
        # Now n = 10 (actually n_hull + #edges)
        if P0.shape[0] != 10:
            continue
        init_order = np.arange(10)
        x0 = P0.flatten() + 0.02 * rng.standard_normal(20)
        sol = minimize(
            lambda f: loss_4window_convex(f.reshape(10, 2), init_order,
                                          conv_min=0.02, sep_min=0.1),
            x0, method="L-BFGS-B",
            options={"ftol": 1e-18, "gtol": 1e-12, "maxiter": 3000},
        )
        if best is None or sol.fun < best["loss"]:
            best = {"loss": float(sol.fun), "P": sol.x.reshape(10, 2).copy(),
                    "trial": trial}
    P = best["P"]
    diag = diagnostics(P, tol=1e-6)
    diag["loss"] = best["loss"]
    return {"name": "L9_seven_plus_three", "trust": "NUMERICAL_NEAR_MISS",
            "diagnostics": diag, "points": P.tolist()}


def attempt_l10_3fold_symmetric(seed=0, n_orbits=4):
    """Construct n_orbits concentric triangles with 3-fold symmetry,
    radius r_i and rotation phi_i (phi_0=0). 12 points total = 4 orbits.
    Each vertex has 2 equidistant 'sisters' from same orbit (E>=2).
    Need 2 more witnesses per vertex => 4 conditions per orbit.
    With 7 dof (4 radii - 1 scale + 3 phases), 4 vertex types × constraints.
    """
    rng = np.random.default_rng(seed)
    n = n_orbits * 3

    def build(params):
        # params = [r1, r2, ..., r_{n_orbits}, phi_1, ..., phi_{n_orbits-1}]
        # phi_0 = 0 always.
        radii = params[:n_orbits]
        phis = np.concatenate([[0.0], params[n_orbits:n_orbits + (n_orbits - 1)]])
        pts = []
        for k in range(n_orbits):
            for j in range(3):
                ang = phis[k] + 2 * math.pi * j / 3
                pts.append([radii[k] * math.cos(ang), radii[k] * math.sin(ang)])
        return np.array(pts)

    init_order_indices = []  # angle ordering depends on params

    def loss(params):
        # Force radii positive
        radii = params[:n_orbits]
        if any(r <= 0.05 for r in radii):
            return 1e10
        P = build(params)
        # Compute init order by angle from centroid
        c = P.mean(0)
        ang = np.arctan2(P[:, 1] - c[1], P[:, 0] - c[0])
        order = np.argsort(ang)
        return loss_4window_convex(P, order, conv_min=0.02, sep_min=0.05)

    n_params = n_orbits + (n_orbits - 1)
    best = None
    for trial in range(30):
        # initialize: increasing radii, evenly spaced phases
        r0 = np.array([1 + 0.5 * k for k in range(n_orbits)]) + 0.1 * rng.standard_normal(n_orbits)
        p0 = np.array([math.pi / 6 * (k + 1) for k in range(n_orbits - 1)]) + 0.05 * rng.standard_normal(n_orbits - 1)
        x0 = np.concatenate([r0, p0])
        sol = minimize(loss, x0, method="Nelder-Mead",
                       options={"xatol": 1e-12, "fatol": 1e-16, "maxiter": 5000})
        if best is None or sol.fun < best["loss"]:
            best = {"loss": float(sol.fun), "params": sol.x.copy(), "trial": trial}
    P = build(best["params"])
    diag = diagnostics(P, tol=1e-6)
    diag["loss"] = best["loss"]
    diag["params"] = best["params"].tolist()
    return {"name": f"L10_3fold_symmetric_n{n}", "trust": "NUMERICAL_NEAR_MISS",
            "diagnostics": diag, "points": P.tolist()}


def attempt_l11_3fold_n12_constrained(seed=0):
    """Like L10 but only 4 orbits = 12 points; force the 4-window equality
    using sympy / equality constraints."""
    rng = np.random.default_rng(seed)
    n_orbits = 4
    n = 12

    def build(params):
        radii = params[:n_orbits]
        phis = np.concatenate([[0.0], params[n_orbits:n_orbits + (n_orbits - 1)]])
        pts = []
        for k in range(n_orbits):
            for j in range(3):
                ang = phis[k] + 2 * math.pi * j / 3
                pts.append([radii[k] * math.cos(ang), radii[k] * math.sin(ang)])
        return np.array(pts)

    def vertex_4window(P, v):
        D = np.linalg.norm(P - P[v], axis=1)
        ds = np.sort(D[D > 1e-9])
        if len(ds) < 4:
            return float('inf')
        return float((ds[3:] - ds[:-3]).min())

    def loss(params):
        radii = params[:n_orbits]
        if any(r <= 0.05 for r in radii):
            return 1e10
        # spacing penalty: radii should differ
        for i in range(n_orbits - 1):
            for j in range(i + 1, n_orbits):
                if abs(radii[i] - radii[j]) < 0.05:
                    return 1e10
        P = build(params)
        # By 3-fold sym, only 4 representative vertices (one per orbit)
        s = 0.0
        for orbit in range(n_orbits):
            v = orbit * 3
            s += vertex_4window(P, v) ** 2
        # Convexity penalty
        c = P.mean(0)
        ang = np.arctan2(P[:, 1] - c[1], P[:, 0] - c[0])
        order = np.argsort(ang)
        Q = P[order]
        cnv_pen = 0.0
        for i in range(n):
            a, b, d = Q[i], Q[(i + 1) % n], Q[(i + 2) % n]
            v1 = b - a; v2 = d - b
            cr = v1[0] * v2[1] - v1[1] * v2[0]
            if cr < 0.01:
                cnv_pen += (0.01 - cr) ** 2 * 100.0
        # Min separation
        diff = P[:, None] - P[None, :]
        D2 = (diff ** 2).sum(-1) + np.eye(n) * 1e6
        min_d = math.sqrt(D2.min())
        sep_pen = max(0.0, 0.05 - min_d) ** 2 * 1000
        return s + cnv_pen + sep_pen

    best = None
    for trial in range(50):
        r0 = np.array([1 + 0.4 * k for k in range(n_orbits)]) + 0.15 * rng.standard_normal(n_orbits)
        p0 = np.array([math.pi / 6 * (k + 1) for k in range(n_orbits - 1)]) + 0.1 * rng.standard_normal(n_orbits - 1)
        x0 = np.concatenate([r0, p0])
        sol = minimize(loss, x0, method="Nelder-Mead",
                       options={"xatol": 1e-12, "fatol": 1e-18, "maxiter": 8000})
        if best is None or sol.fun < best["loss"]:
            best = {"loss": float(sol.fun), "params": sol.x.copy(), "trial": trial}
    P = build(best["params"])
    diag = diagnostics(P, tol=1e-6)
    diag["loss"] = best["loss"]
    diag["params"] = best["params"].tolist()
    return {"name": "L11_3fold_n12_constrained",
            "trust": "NUMERICAL_NEAR_MISS",
            "diagnostics": diag, "points": P.tolist()}


def attempt_l12_3fold_n9_force_e4(seed=0):
    """3-fold sym 9-point, force E=4. With 3 orbits and 5 dof (3 radii - 1 scale + 2 phases),
    must satisfy 1 representative vertex condition (E=4) -> 1 equation in 5 dof.
    Should have a solution! Let's find it."""
    rng = np.random.default_rng(seed)
    n_orbits = 3
    n = 9

    def build(params):
        radii = params[:n_orbits]
        phis = np.concatenate([[0.0], params[n_orbits:]])
        pts = []
        for k in range(n_orbits):
            for j in range(3):
                ang = phis[k] + 2 * math.pi * j / 3
                pts.append([radii[k] * math.cos(ang), radii[k] * math.sin(ang)])
        return np.array(pts)

    def vertex_4window(P, v):
        D = np.linalg.norm(P - P[v], axis=1)
        ds = np.sort(D[D > 1e-9])
        if len(ds) < 4:
            return float('inf')
        return float((ds[3:] - ds[:-3]).min())

    def loss(params):
        radii = params[:n_orbits]
        if any(r <= 0.05 for r in radii):
            return 1e10
        for i in range(n_orbits - 1):
            for j in range(i + 1, n_orbits):
                if abs(radii[i] - radii[j]) < 0.05:
                    return 1e10
        P = build(params)
        s = 0.0
        for orbit in range(n_orbits):
            v = orbit * 3
            s += vertex_4window(P, v) ** 2
        # Convexity penalty
        c = P.mean(0)
        ang = np.arctan2(P[:, 1] - c[1], P[:, 0] - c[0])
        order = np.argsort(ang)
        Q = P[order]
        cnv_pen = 0.0
        for i in range(n):
            a, b, d = Q[i], Q[(i + 1) % n], Q[(i + 2) % n]
            v1 = b - a; v2 = d - b
            cr = v1[0] * v2[1] - v1[1] * v2[0]
            if cr < 0.01:
                cnv_pen += (0.01 - cr) ** 2 * 100.0
        diff = P[:, None] - P[None, :]
        D2 = (diff ** 2).sum(-1) + np.eye(n) * 1e6
        min_d = math.sqrt(D2.min())
        sep_pen = max(0.0, 0.05 - min_d) ** 2 * 1000
        return s + cnv_pen + sep_pen

    best = None
    for trial in range(80):
        r0 = np.array([1.0, 1.6, 2.4]) + 0.3 * rng.standard_normal(3)
        p0 = np.array([math.pi / 6, math.pi / 3]) + 0.2 * rng.standard_normal(2)
        x0 = np.concatenate([np.abs(r0), p0])
        sol = minimize(loss, x0, method="Nelder-Mead",
                       options={"xatol": 1e-14, "fatol": 1e-18, "maxiter": 8000})
        if best is None or sol.fun < best["loss"]:
            best = {"loss": float(sol.fun), "params": sol.x.copy(), "trial": trial}
    P = build(best["params"])
    diag = diagnostics(P, tol=1e-6)
    diag["loss"] = best["loss"]
    diag["params"] = best["params"].tolist()
    return {"name": "L12_3fold_n9_force_e4",
            "trust": "NUMERICAL_NEAR_MISS",
            "diagnostics": diag, "points": P.tolist()}


# Run extra attempts
import json
results = []
for fn in [attempt_l9_seven_plus_three,
           attempt_l10_3fold_symmetric,
           attempt_l11_3fold_n12_constrained,
           attempt_l12_3fold_n9_force_e4]:
    print(f"Running {fn.__name__}...")
    r = fn(seed=42)
    diag = r["diagnostics"]
    print(f"  n={diag['n']}, E={diag['E']}, min_E={diag['min_E']}")
    print(f"  convex={diag['convex']}, margin={diag['convex_margin']}")
    print(f"  rms_4={diag['rms_4_window']}, loss={diag.get('loss')}")
    print(f"  min_pair_dist={diag['min_pair_dist']}")
    results.append(r)

# Save
with open("/tmp/danzer_lift_v2_results.json", "w") as f:
    json.dump({"date": "2026-05-06", "attempts": results}, f, indent=2)
print("\nSaved to /tmp/danzer_lift_v2_results.json")
