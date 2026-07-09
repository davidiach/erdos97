# n <= 8 Geometric Proof Audit — 2026-07-09

Status: `REPO_LOCAL_PROOF_AUDIT_ACCEPTED`.

Scope: line-by-line repository review of `docs/n8-geometric-proof.md`. This is
not independent external/publication review and does not address `n >= 9` or
the global status of Erdős Problem #97.

## Verdict

Two independent derivations accepted the proof after two implicit geometric
facts were made explicit in the theorem note:

1. An apex cannot lie on its base line, because that line meets its
   perpendicular bisector only at the base midpoint, which is not an extreme
   point.
2. A diagonal of a strictly convex polygon separates the vertices on its two
   open boundary chains into opposite open half-planes.

No substantive gap or hidden countercase was found.

## Checked chain

- The number of apex-marked isosceles triples is
  `T(A) = sum_p sum_k binom(m_{p,k},2)` over distance-class sizes at each
  vertex.
- Badness gives `T(A) >= 6n`.
- Strict convexity gives base capacities one for sides and two for diagonals,
  hence `T(A) <= n(n-2)`.
- At `n=8`, equality forces every vertex contribution and every base capacity
  to saturate; the only allowed distance partition is `(4,1,1,1)`.
- Saturation for every length-2 diagonal forces all eight side lengths equal.
- In an equilateral convex polygon the skip-one chord at exterior turn `tau`
  has length `2s cos(tau/2)`.
- Saturation for every length-3 diagonal forces at least one turn in each
  adjacent pair to equal `2*pi/3`.
- Those marked turns form a vertex cover of `C_8`, so at least four are
  required; their sum is at least `8*pi/3 > 2*pi`, a contradiction.

## Claim boundary

Accepted repo-local theorem: if every vertex of a strictly convex polygon has
four other vertices at one common distance, then the polygon has at least nine
vertices. The selected-witness computation remains independent corroboration.
The official problem remains falsifiable/open.
