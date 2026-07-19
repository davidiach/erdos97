# Independent recheck of the n=9 Kalmanson closure

Status: `INDEPENDENT_IMPLEMENTATION_RECHECK_REVIEW_PENDING`.

This note records an implementation-independent audit of the self-contained
`n=9` Kalmanson frontier replay. It does not complete the repository's written
external-review gate, does not update the repo-local strongest result, does not
prove Erdos Problem #97 for arbitrary `n`, and does not claim a counterexample.

## Claim under review

The finite claim is:

```text
No strictly convex nonagon has four other vertices at one common distance from
each of its vertices.
```

A hypothetical nonagon can be labelled in its actual cyclic order `0,...,8`.
At each center, choose four equidistant witnesses. The resulting nine selected
rows must satisfy three elementary necessary conditions:

1. Two rows share at most two witnesses, because two distinct centered circles
   meet in at most two points.
2. If rows at centers `i,j` share witnesses `x,y`, then `ij` is the
   perpendicular bisector of `xy`, while `xy` is the perpendicular bisector
   of `ij`. The two chords cross at their common midpoint.
3. A witness pair occurs in at most two rows, because every corresponding
   center lies on one perpendicular-bisector line and a strictly convex vertex
   set has no three collinear vertices.

The independent search also applies the selected-indegree bound `d <= 5`.
This is necessary for every hypothetical bad nonagon. The separate fresh
Kalmanson replay omits that filter and nevertheless produces the same frontier.

## Independent implementation

`scripts/independent_n9_vertex_circle_recheck.py` is structurally different
from `scripts/check_n9_kalmanson_selfedge_frontier_replay.py`:

- it assigns centers in the fixed order `0,1,...,8`, rather than dynamic
  minimum-remaining-options order;
- it represents rows and distance pairs by `frozenset`, rather than tuples and
  indexed distance variables;
- it maintains the selected-indegree cap as an additional necessary filter;
- it computes equality components with a hashable-item union-find; and
- it reads no stored Kalmanson frontier or self-edge certificate.

The optional comparison with the stored vertex-circle frontier happens only
after generation and does not influence either enumeration or Kalmanson
classification.

## Strict Kalmanson obstruction

For cyclically ordered vertices `a < b < c < d`, ordinary Euclidean distances
in a strictly convex quadrilateral satisfy

```text
D_ab + D_cd < D_ac + D_bd
D_ad + D_bc < D_ac + D_bd.
```

Let the diagonals `ac` and `bd` meet at `q`. Strict triangle inequalities in
the four small triangles at `q`, followed by
`D_ac = D_aq + D_qc` and `D_bd = D_bq + D_qd`, give the two displayed
inequalities.

A selected row at center `i` forces its four spoke distances to be equal. The
rechecker constructs the transitive components of exactly those equalities.
If the two distance variables on the left and right of a strict Kalmanson
inequality have the same component multiset, the inequality becomes `L < L`.
That selected-row assignment is impossible.

## Reproduced invariants

The fixed-order recheck reports:

```text
labelled frontier assignments: 184
sorted assignment SHA-256:
  dc28b32d93e721838a592d1f010f92720869191594dbcc40df2a00f96f213d55
K1 self-edges: 150
K2 self-edges: 34
assignments without a Kalmanson self-edge: 0
```

The assignment digest matches the separately maintained compact brancher. The
`150 + 34` split also matches the self-contained Kalmanson frontier replay,
whose certificate digest is
`3e6e208cd4212f9275eba2f0be9e32558da9b77544304d33d09abc953feeee9d`.

Run the end-to-end report without the optional random vertex-circle stress
samples:

```bash
python scripts/independent_n9_vertex_circle_recheck.py --samples 0 --json
```

Run the deterministic artifact test:

```bash
pytest -q tests/test_independent_n9_kalmanson_recheck.py
```

## Review boundary

This independent implementation found no enumeration, quotient, or strict
Kalmanson gap. Before any repo-local `n=9` status proposal, a written external
review must still identify the commit reviewed, independently accept the three
necessary incidence lemmas and the strict ordinary-distance inequalities, run
the checked command surface, and record the accepted gate partition. Any
status proposal must remain separate and must preserve the global open status
for arbitrary `n`.
