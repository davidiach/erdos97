"""Check whether the 9 points are even all on the convex hull."""
import math
import numpy as np
from scipy.spatial import ConvexHull


def make_pts(rC, phiA=0.0, phiB=-math.pi/3, phiC=2*math.pi/3):
    rA = 1.0
    rB = rC + 1.0
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


# Check hull membership for various rC.
# B is the largest circle (rB = rC+1). A at radius 1, C at radius rC.
# So if rC < 1: B > A > C. C is innermost.
# rC > 1: B > C > A. A is innermost.

for rC in [0.1, 0.3, 0.5, 0.8, 1.5, 2.0, 5.0]:
    P = make_pts(rC)
    print(f"\n=== rC={rC} (rB={rC+1}) ===")
    hull = ConvexHull(P)
    on_hull = sorted(hull.vertices.tolist())
    print(f"Hull vertices: {on_hull}, count: {len(on_hull)}")
    # Print all 9 with positions
    for i, p in enumerate(P):
        marker = "*" if i in on_hull else " "
        print(f"  {marker} v{i}: ({p[0]:.4f}, {p[1]:.4f})")
