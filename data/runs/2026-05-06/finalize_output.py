"""Consolidate all lift attempt results into one JSON for the report."""
import json
import math
import numpy as np
from scipy.spatial import ConvexHull

S3 = math.sqrt(3.0)


def make_3fold(radii, phis):
    pts = []
    for r, phi in zip(radii, phis):
        for k in range(3):
            a = phi + 2*math.pi*k/3
            pts.append((r*math.cos(a), r*math.sin(a)))
    return np.array(pts)


def E_values(P, tol=1e-7):
    n = P.shape[0]
    D = np.linalg.norm(P[:, None] - P[None, :], axis=-1)
    sizes = []
    for v in range(n):
        ds = sorted([D[v, j] for j in range(n) if j != v])
        groups = [[ds[0]]]
        for x in ds[1:]:
            if abs(x - groups[-1][-1]) <= tol:
                groups[-1].append(x)
            else:
                groups.append([x])
        sizes.append(max(len(g) for g in groups))
    return sizes


def diagnostics(P, tol=1e-7):
    n = int(P.shape[0])
    D = np.linalg.norm(P[:, None] - P[None, :], axis=-1)
    Es = E_values(P, tol=tol)
    c = P.mean(0)
    angles = np.arctan2(P[:, 1] - c[1], P[:, 0] - c[0])
    order = np.argsort(angles)
    Q = P[order]
    crosses = []
    for i in range(n):
        a, b, d = Q[i], Q[(i + 1) % n], Q[(i + 2) % n]
        v1 = b - a; v2 = d - b
        crosses.append(float(v1[0] * v2[1] - v1[1] * v2[0]))
    cnv_min = min(crosses)
    rms_4 = 0.0
    for v in range(n):
        ds = np.sort(np.array([D[v, j] for j in range(n) if j != v]))
        if len(ds) >= 4:
            wins = ds[3:] - ds[:-3]
            rms_4 += wins.min() ** 2
    rms_4 = math.sqrt(rms_4 / n)
    # Hull check: if hull has fewer than n vertices, polygon is not convex
    hull = ConvexHull(P)
    on_hull = len(hull.vertices)
    return {
        "n": n,
        "E_values_per_vertex": Es,
        "min_E": int(min(Es)),
        "max_E": int(max(Es)),
        "convex_strict": bool(cnv_min > 1e-9 and on_hull == n),
        "convex_margin": float(cnv_min),
        "n_on_convex_hull": int(on_hull),
        "rms_4_window": float(rms_4),
        "cyclic_order": [int(x) for x in order],
    }


# Main consolidated output
out = {
    "task": "Erdos #97 lift attempts: Danzer 9-point + Fishburn-Reeds 20-point",
    "date": "2026-05-06",
    "summary": {
        "any_lift_strict_convex_4_bad": False,
        "principal_finding": (
            "We found a one-parameter algebraic family of 3-fold symmetric "
            "9-point sets with E(v)=4 at every vertex (rA=1, rB=rC+1, "
            "phiA=0, phiB=-pi/3, phiC=2pi/3, rC>0). However these point sets "
            "are NOT convex 9-gons: only 6 of 9 points lie on the convex hull "
            "(the inner-radius orbit is interior). So this is NOT a counter"
            "example to Erdos #97."
        ),
        "trust_label": "EXACT_ALGEBRAIC_NEAR_MISS",
    },
    "attempts": [],
}

# Load existing v1 results
v1 = json.load(open("/home/user/erdos97/data/runs/2026-05-06/danzer_fr_lift_attempts.json"))
out["attempts"].extend(v1["attempts"])

# L9: 3-fold algebraic family (RIGOROUS)
print("Adding L_alg algebraic family results...")
for rC in [0.3, 0.5, 0.7325480206474753, 0.8, 1.5]:
    P = make_3fold([1.0, rC + 1.0, rC], [0.0, -math.pi/3, 2*math.pi/3])
    diag = diagnostics(P, tol=1e-9)
    diag["rC"] = float(rC)
    diag["rB"] = float(rC + 1)
    out["attempts"].append({
        "name": f"L_alg_3fold_n9_rC={rC:.4f}",
        "trust": "EXACT_ALGEBRAIC",
        "construction": "3-fold sym, rA=1, rB=rC+1, phi=(0, -pi/3, 2pi/3)",
        "diagnostics": diag,
        "points": P.tolist(),
    })
    print(f"  rC={rC}: n={diag['n']}, E={diag['E_values_per_vertex']}, min_E={diag['min_E']}, "
          f"convex_strict={diag['convex_strict']}, hull_size={diag['n_on_convex_hull']}")

# Best fast 3-fold search result
fast = json.load(open("/tmp/3fold_search_best.json"))
P = np.array(fast["points"])
diag = diagnostics(P, tol=1e-5)
out["attempts"].append({
    "name": "L_fast_3fold_n9_search",
    "trust": "NUMERICAL_NEAR_MISS",
    "construction": "3-fold sym n=9 with strict convexity penalty",
    "diagnostics": diag,
    "points": P.tolist(),
    "params": fast["params"],
})

# Add v2 results from script output (we don't have JSON due to bool serialization bug)
# Manually transcribe diagnostics from terminal output
v2_attempts = [
    {
        "name": "L9_seven_plus_three",
        "trust": "NUMERICAL_NEAR_MISS",
        "construction": "Convex hull (7 vertices) of Lean Danzer + 3 inserted edge midpoints, optimized",
        "diagnostics": {"n": 10, "min_E": 1, "convex_strict": True, "convex_margin": 0.0106,
                        "rms_4_window": 0.03370, "loss": 0.01308, "min_pair_dist": 0.0993,
                        "E_values_per_vertex": [2, 1, 1, 2, 2, 1, 2, 2, 1, 1]},
    },
    {
        "name": "L10_3fold_symmetric_n12",
        "trust": "NUMERICAL_NEAR_MISS",
        "construction": "4 concentric 3-fold orbits = 12 points, optimized",
        "diagnostics": {"n": 12, "min_E": 2, "convex_strict": True, "convex_margin": 0.0184,
                        "rms_4_window": 0.01292, "loss": 0.00208, "min_pair_dist": 0.1379,
                        "E_values_per_vertex": [2]*12},
    },
    {
        "name": "L11_3fold_n12_constrained",
        "trust": "NUMERICAL_NEAR_MISS",
        "construction": "n=12 with 3-fold sym, optimized for E=4 at orbit reps",
        "diagnostics": {"n": 12, "min_E": 2, "convex_strict": True, "convex_margin": 0.0276,
                        "rms_4_window": 0.02042, "loss": 0.00167, "min_pair_dist": 0.1401,
                        "E_values_per_vertex": [3, 3, 3, 2, 2, 2, 3, 3, 3, 2, 2, 2]},
    },
    {
        "name": "L12_3fold_n9_force_e4_convex",
        "trust": "NUMERICAL_NEAR_MISS",
        "construction": "n=9 with 3-fold sym + strict convex penalty",
        "diagnostics": {"n": 9, "min_E": 2, "convex_strict": True, "convex_margin": 0.00986,
                        "rms_4_window": 0.01428, "loss": 0.000618, "min_pair_dist": 0.2982,
                        "E_values_per_vertex": [3, 3, 3, 2, 2, 2, 2, 2, 2]},
    },
]
out["attempts"].extend(v2_attempts)

# Update summary
results_summary = []
best_min_E_with_convex = 0
best_rms_with_convex = float('inf')
best_attempt_name = None
for a in out["attempts"]:
    diag = a["diagnostics"]
    if diag.get("convex_strict") is True:
        if diag.get("min_E", 0) >= 4:
            out["summary"]["any_lift_strict_convex_4_bad"] = True
        if diag.get("min_E", 0) > best_min_E_with_convex:
            best_min_E_with_convex = diag.get("min_E", 0)
            best_attempt_name = a["name"]
        if diag.get("rms_4_window", float('inf')) < best_rms_with_convex:
            best_rms_with_convex = diag.get("rms_4_window")

out["summary"]["best_min_E_with_strict_convexity"] = best_min_E_with_convex
out["summary"]["best_rms_4window_among_strict_convex"] = best_rms_with_convex

# Per-n min E
per_n = {}
for a in out["attempts"]:
    diag = a["diagnostics"]
    n = diag.get("n")
    if n is None:
        continue
    is_cv = diag.get("convex_strict") is True
    cur = per_n.get(n, {"min_E_convex": -1, "best_rms_convex": float('inf')})
    if is_cv:
        if diag.get("min_E", 0) > cur["min_E_convex"]:
            cur["min_E_convex"] = diag.get("min_E", 0)
            cur["best_min_E_attempt"] = a["name"]
        if diag.get("rms_4_window", float('inf')) < cur["best_rms_convex"]:
            cur["best_rms_convex"] = diag.get("rms_4_window")
            cur["best_rms_attempt"] = a["name"]
    per_n[n] = cur
out["summary"]["per_n_best_strict_convex"] = {str(k): v for k, v in sorted(per_n.items())}

# Save
out_path = "/home/user/erdos97/data/runs/2026-05-06/danzer_fr_lift_attempts.json"
with open(out_path, "w") as f:
    json.dump(out, f, indent=2)

print(f"\nSaved consolidated results to {out_path}")
print(f"\nNumber of attempts: {len(out['attempts'])}")
print(f"Any strict-convex 4-bad: {out['summary']['any_lift_strict_convex_4_bad']}")
print(f"Best min E with strict convexity: {out['summary']['best_min_E_with_strict_convexity']}")
print()
print("Per-n best strict-convex results:")
for n, info in sorted(per_n.items()):
    print(f"  n={n}: min_E_convex={info['min_E_convex']}, "
          f"best_rms_convex={info.get('best_rms_convex','N/A'):.6e}")
