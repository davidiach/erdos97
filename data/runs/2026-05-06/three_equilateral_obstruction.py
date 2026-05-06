"""Test geometric realizability of n=9 polygons with 3 forced equilateral triangles.

Setup: Strictly convex 9-gon with vertex labels 0..8 in cyclic order.
Constraint: vertices {0,3,6}, {1,4,7}, {2,5,8} each form an equilateral triangle.

Question: Can we have 3 such equilateral triangles in a strictly convex 9-gon?
If not, the n=9 non-ear circulants are killed by THIS geometric obstruction
(potentially independent of vertex-circle).
"""

import numpy as np


def check_geometric_realizability_9_with_3_equilateral_triangles():
    """Numerical search: minimize convexity-violating + equilateral-violating residual."""
    rng = np.random.default_rng(seed=42)
    best_res = None
    best_pts = None
    for trial in range(100):
        # Random initial: regular 9-gon perturbed
        theta = np.linspace(0, 2 * np.pi, 9, endpoint=False) + rng.normal(0, 0.05, 9)
        pts = np.stack([np.cos(theta), np.sin(theta)], axis=1)

        # equilateral constraint: for each triangle T = {i, i+3, i+6}, the 3 sides equal.
        def residual(p):
            res = 0
            for i in range(3):
                a, b, c = i, (i + 3), (i + 6)
                d_ab = np.linalg.norm(p[a] - p[b])
                d_bc = np.linalg.norm(p[b] - p[c])
                d_ca = np.linalg.norm(p[c] - p[a])
                res += (d_ab - d_bc) ** 2 + (d_bc - d_ca) ** 2
            return res

        # gradient descent
        p = pts.copy()
        lr = 0.05
        for it in range(2000):
            r = residual(p)
            grad = np.zeros_like(p)
            eps = 1e-6
            for i in range(9):
                for j in range(2):
                    p_perturb = p.copy()
                    p_perturb[i, j] += eps
                    grad[i, j] = (residual(p_perturb) - r) / eps
            p = p - lr * grad
            if r < 1e-12:
                break

        # check strict convexity: all cross products in cyclic order have same sign
        signs = []
        for i in range(9):
            a, b, c = p[i], p[(i + 1) % 9], p[(i + 2) % 9]
            cross = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
            signs.append(cross)
        is_convex = (all(s > 1e-6 for s in signs) or all(s < -1e-6 for s in signs))

        r = residual(p)
        if best_res is None or r < best_res:
            best_res = r
            best_pts = p

        if is_convex and r < 1e-8:
            print(f"  trial {trial}: residual={r:.2e}, convex! 3 equilateral triangles compatible")
            for i in range(3):
                a, b, c = i, i + 3, i + 6
                d_ab = np.linalg.norm(p[a] - p[b])
                d_bc = np.linalg.norm(p[b] - p[c])
                d_ca = np.linalg.norm(p[c] - p[a])
                print(f"   T_{i}={{{a},{b},{c}}}: sides {d_ab:.4f}, {d_bc:.4f}, {d_ca:.4f}")
            return True, p

    return False, best_pts


def main():
    print("=" * 70)
    print("Are 3 forced equilateral triangles compatible with strict convexity?")
    print("=" * 70)
    realizable, p = check_geometric_realizability_9_with_3_equilateral_triangles()
    print(f"Realizable: {realizable}")
    if not realizable:
        print(f"Best residual: ?")

    # Theoretical: 3 equilateral triangles {0,3,6}, {1,4,7}, {2,5,8} in a strictly
    # convex 9-gon. Each triangle has 3-fold rotational symmetry.
    # A strictly convex 9-gon has 9 vertices. The 3 triangles partition them.
    # Equilateral triangle {0,3,6} forces 3-fold rotational symmetry of these 3 points.
    # Similarly for the other two. But the 3 triangles can have DIFFERENT centers and sizes.
    print()
    print("Direct geometric construction: take a regular triangle T and rotate twice.")
    print("Place T_0 = {0,3,6} as equilateral triangle of size r_0 around origin.")
    print("Place T_1 = {1,4,7} as equilateral triangle of size r_1 around origin (possibly rotated).")
    print("Place T_2 = {2,5,8} as equilateral triangle of size r_2 around origin (possibly rotated).")
    print("In cyclic order: 0, 1, 2, 3, 4, 5, 6, 7, 8 -- so we need 0, 3, 6 at positions 0, 3, 6 in the cyclic.")
    print()
    print("Specifically: if we place T_i such that its vertex at position 3*j+i is at angle (2 pi (3j+i)/9 + theta_i)")
    print("and radius r_i, then we need:")
    print("  - All 9 vertices in cyclic order around origin (or similar).")
    print("  - Each T_i is rotated by some angle theta_i and scaled by r_i.")
    print()
    print("Generic such configuration: 3 concentric (or non-concentric) equilateral triangles.")
    print("The 9-gon vertices alternate among the 3 triangles in cyclic order (mod 3).")
    print("This IS realizable (Star of David type pattern).")
    print()
    print("So the 3-equilateral-triangle constraint alone does NOT obstruct realization.")
    print("The vertex-circle obstruction is what kills idx=81/151, but it has a deeper structure.")


if __name__ == "__main__":
    main()
