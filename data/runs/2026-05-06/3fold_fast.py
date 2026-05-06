"""Fast 3-fold symmetric n=9 + n=12 search for E=4 + strict convexity."""
import math
import numpy as np
from scipy.optimize import minimize
from scipy.spatial import ConvexHull


def make_3fold(radii, phis):
    """Build a point set with k orbits of 3 (so 3k points)."""
    pts = []
    for r, phi in zip(radii, phis):
        for k in range(3):
            a = phi + 2*math.pi*k/3
            pts.append((r*math.cos(a), r*math.sin(a)))
    return np.array(pts)


def is_strict_convex(P):
    n = P.shape[0]
    c = P.mean(0)
    angles = np.arctan2(P[:,1]-c[1], P[:,0]-c[0])
    order = np.argsort(angles)
    Q = P[order]
    crosses = []
    for i in range(n):
        a, b, d = Q[i], Q[(i+1)%n], Q[(i+2)%n]
        v1 = b-a; v2 = d-b
        crosses.append(v1[0]*v2[1] - v1[1]*v2[0])
    return all(c > 1e-9 for c in crosses), min(crosses), order


def E_values(P, tol=1e-8):
    n = P.shape[0]
    D = np.linalg.norm(P[:,None]-P[None,:], axis=-1)
    sizes = []
    for v in range(n):
        ds = sorted([D[v,j] for j in range(n) if j != v])
        groups = [[ds[0]]]
        for x in ds[1:]:
            if abs(x - groups[-1][-1]) <= tol:
                groups[-1].append(x)
            else:
                groups.append([x])
        sizes.append(max(len(g) for g in groups))
    return sizes


def loss_n9(params):
    rB, rC, phiB, phiC = params
    if rB <= 0.05 or rC <= 0.05 or rB > 10 or rC > 10:
        return 1e10
    P = make_3fold([1.0, rB, rC], [0.0, phiB, phiC])
    n = 9
    D = np.linalg.norm(P[:,None]-P[None,:], axis=-1)
    s = 0.0
    for v in range(n):
        ds = np.sort(np.array([D[v,j] for j in range(n) if j != v]))
        wins = ds[3:] - ds[:-3]
        s += wins.min() ** 2
    # Convexity
    c = P.mean(0)
    angles = np.arctan2(P[:,1]-c[1], P[:,0]-c[0])
    order = np.argsort(angles)
    Q = P[order]
    cnv_pen = 0.0
    for i in range(n):
        a, b, d = Q[i], Q[(i+1)%n], Q[(i+2)%n]
        v1 = b-a; v2 = d-b
        cr = v1[0]*v2[1] - v1[1]*v2[0]
        if cr < 0.05:
            cnv_pen += (0.05 - cr)**2
    diff = P[:,None]-P[None,:]
    D2 = (diff**2).sum(-1) + np.eye(n)*1e6
    min_d = math.sqrt(D2.min())
    sep_pen = max(0, 0.1 - min_d)**2 * 100
    return s + 50.0*cnv_pen + sep_pen


rng = np.random.default_rng(7)
best = None
n_trials = 60
for trial in range(n_trials):
    rB0 = rng.uniform(0.5, 3.0)
    rC0 = rng.uniform(0.5, 3.0)
    phiB0 = rng.uniform(-math.pi, math.pi)
    phiC0 = rng.uniform(-math.pi, math.pi)
    x0 = np.array([rB0, rC0, phiB0, phiC0])
    sol = minimize(loss_n9, x0, method="Nelder-Mead",
                   options={"xatol": 1e-10, "fatol": 1e-14, "maxiter": 3000})
    if best is None or sol.fun < best["loss"]:
        best = {"loss": float(sol.fun), "params": sol.x.copy(), "trial": trial}

print(f"BEST n=9 3-fold: loss = {best['loss']:.6e}")
rB, rC, phiB, phiC = best["params"]
P = make_3fold([1.0, rB, rC], [0.0, phiB, phiC])
cv, cmin, order = is_strict_convex(P)
Es = E_values(P, tol=1e-5)
print(f"  rA=1, rB={rB:.4f}, rC={rC:.4f}, phiB={phiB:.4f}, phiC={phiC:.4f}")
print(f"  E values: {Es}")
print(f"  min_E = {min(Es)}")
print(f"  convex 9-gon: {cv}, min cross = {cmin:.6e}")
print(f"  cyclic order: {order.tolist()}")

# Try harder: use known algebraic family rB=rC+1, phiB=-pi/3, phiC=2pi/3.
# But also allow OTHER E=4 configurations (different distance equality classes).
# Already covered by NM search.

# Save best result
import json
with open("/tmp/3fold_search_best.json", "w") as f:
    json.dump({
        "best_loss": best["loss"],
        "params": {"rA": 1.0, "rB": rB, "rC": rC, "phiB": phiB, "phiC": phiC},
        "E_values": Es,
        "min_E": min(Es),
        "convex_strict": bool(cv),
        "convex_min_cross": float(cmin),
        "cyclic_order": [int(x) for x in order],
        "points": P.tolist(),
    }, f, indent=2)
print("Saved /tmp/3fold_search_best.json")
