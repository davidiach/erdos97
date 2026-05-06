"""Numerical verification of the 3-fold symmetric n=9 with rB=rC+1, phiB=-pi/3, phiC=2pi/3, rA=1."""
import math
import numpy as np


def make_pts(rC):
    rA = 1.0
    rB = rC + 1.0
    phiA, phiB, phiC = 0.0, -math.pi/3, 2*math.pi/3
    pts = []
    for k in range(3):
        a = phiA + 2*math.pi*k/3
        pts.append((rA*math.cos(a), rA*math.sin(a)))
    for k in range(3):
        a = phiB + 2*math.pi*k/3
        pts.append((rB*math.cos(a), rB*math.sin(a)))
    for k in range(3):
        a = phiC + 2*math.pi*k/3
        pts.append((rC*math.cos(a), rC*math.sin(a)))
    return np.array(pts)


for rC_test in [0.1, 0.3, 0.5, 0.8, 1.0, 1.5, 2.0]:
    P = make_pts(rC_test)
    D = np.linalg.norm(P[:,None]-P[None,:], axis=-1)
    print(f"\n=== rC={rC_test}, rB={rC_test+1} ===")
    Es = []
    for v in range(9):
        ds = sorted([(D[v,j], j) for j in range(9) if j != v])
        groups = []; cur_d, cur = ds[0][0], [ds[0][1]]
        for d, j in ds[1:]:
            if abs(d - cur_d) < 1e-9:
                cur.append(j)
            else:
                groups.append((cur_d, cur)); cur_d, cur = d, [j]
        groups.append((cur_d, cur))
        sizes = [len(g[1]) for g in groups]
        max_E = max(sizes)
        Es.append(max_E)
        # Find which group
        max_idx = sizes.index(max_E)
        print(f"  v{v}: sizes={sizes}, max E = {max_E}, witnesses at d={groups[max_idx][0]:.4f}: {sorted(groups[max_idx][1])}")
    print(f"  Min E across vertices: {min(Es)}, Max E: {max(Es)}")
    # Convexity: compute cyclic order
    c = P.mean(0)
    angles = np.arctan2(P[:,1]-c[1], P[:,0]-c[0])
    order = np.argsort(angles)
    Q = P[order]
    crosses = []
    for i in range(9):
        a, b, d = Q[i], Q[(i+1)%9], Q[(i+2)%9]
        v1 = b-a; v2 = d-b
        crosses.append(v1[0]*v2[1] - v1[1]*v2[0])
    print(f"  Cyclic order: {order.tolist()}")
    print(f"  Cross products: {[round(x,4) for x in crosses]}")
    print(f"  CONVEX STRICT: {all(c > 0 for c in crosses)}, min cross: {min(crosses):.6f}")
    if all(c > 0 for c in crosses) and min(Es) >= 4:
        print(f"  *** FOUND k=4 STRICT CONVEX 9-POINT! ***")
