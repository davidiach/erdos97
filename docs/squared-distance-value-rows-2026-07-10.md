# Squared-distance value rows: a k=4-essential arithmetic filter (2026-07-10)

Status: LEMMA-grade row statements with complete proofs below, produced and
adversarially audited inside an AI research session (Claude Code multi-agent
session, 2026-07-10); machine results are exact z3 real-arithmetic decisions
replayable by `scripts/check_block6_value_rows_closure.py`. Review pending in
the repo sense. This note does not prove Erdos Problem #97, does not claim a
counterexample, and does not change the official/global falsifiable/open
status.

## Idea

The vertex-circle order filter compares selected-distance quotient classes
by strict nested-chord inequalities - a purely order-theoretic view. The
rows below add *arithmetic* necessary conditions on the squared distances
themselves, all consequences of the semicircle criterion (the four witnesses
of a center span an angular width below pi). Variables: squared distances
`D_xy > 0`; per center `i` with witness row `S_i`, the row equalities
`D_{i,w} = R_i` for `w in S_i`. Throughout, `a < b < c < d` denote the four
witnesses of center `i` in angular order as seen from `i` (equivalently, in
the polygon's cyclic order restricted to `S_i`), and `sigma_i < pi` the
total angular width, with the three consecutive gaps summing to `sigma_i`.
Chord arithmetic: a gap `g` between two witnesses gives squared chord
`4 R_i sin^2(g/2)`.

## Row lemmas

**Row O (obtuse rows).** `D_ac > D_ab + D_bc`, `D_bd > D_bc + D_cd`,
`D_ad > D_ab + D_bd`, `D_ad > D_ac + D_cd`.

Proof. For witnesses `x < y < z` (angular order), `y` lies on the minor arc
`xz` of the circle of radius `r_i` about the center (minor because the full
span is below pi). The inscribed-angle relation gives
`angle(x, y, z) = pi - angle_at_center(x, z)/2 > pi/2`, so the triangle
`x y z` is obtuse at `y`, and the law of cosines gives
`D_xz = D_xy + D_yz - 2 sqrt(D_xy D_yz) cos(angle(x,y,z)) > D_xy + D_yz`.
Apply to `(a,b,c)`, `(b,c,d)`, `(a,b,d)`, `(a,c,d)`. QED.

Remark: Row O strictly refines the plain nested strict rows at each center
(chain the obtuse rows with positivity).

**Row D (diameter rows).** `D_xy < 4 R_i` for every pair `x, y` in `S_i`.

Proof. The gap is below pi, so the squared chord `4 R_i sin^2(gap/2)` is
below `4 R_i`. QED.

**Row S (short-chord pigeonhole; the k=4-essential row).**
`min(D_ab, D_bc, D_cd) < R_i`.

Proof. The three consecutive gaps sum to `sigma_i < pi`, so the smallest is
below `pi/3`, and its squared chord is below
`4 R_i sin^2(pi/6) = R_i`. QED.

k-dependence: with only three witnesses the two gaps sum below pi, giving
only `min < 4 R_i sin^2(pi/4) = 2 R_i`, and exact k=3 configurations with
`min >= R_i` exist. Row S is where the number 4 enters essentially.

**Row A (arc-packing rows).** For the five pairs of witness intervals with
disjoint interiors - `(ab,bc)`, `(ab,bd)`, `(ab,cd)`, `(ac,cd)`, `(bc,cd)` -
the smaller of the two squared chords is below `2 R_i`.

Proof. The two central angles sum to at most `sigma_i < pi`, so one is
below `pi/2`; its squared chord is below `4 R_i sin^2(pi/4) = 2 R_i`. QED.

**Row K (kite rows; cross-center).** If `S_i` and `S_j` (`i != j`) share
exactly the pair `{x, y}`, then
`R_i + R_j - D_xy/2 < D_ij <= 2 (R_i + R_j) - D_xy`.

Proof. Both centers lie on the perpendicular bisector of `xy`, at offsets
`e_i = sqrt(R_i - D_xy/4)` and `e_j = sqrt(R_j - D_xy/4)` from the midpoint,
both strictly positive (a zero offset would place a vertex at the midpoint
of two others, collinear), and on opposite sides by the two-overlap
crossing lemma. So `D_ij = (e_i + e_j)^2`, and
`e_i^2 + e_j^2 < (e_i + e_j)^2 <= 2 (e_i^2 + e_j^2)`. QED.

All five row families are theorems about arbitrary strictly convex
selected-witness configurations, uniform in `n`; adding them to any sound
row system preserves soundness, so an unsat verdict under added rows is a
valid kill of the fixed (assignment, order) pair.

## Machine results (exact, z3 over the reals; replayable)

Replay: `python scripts/check_block6_value_rows_closure.py --check
--assert-expected --json`; artifact
`data/certificates/block6_value_rows_closure.json`.

Test bed 1: the 16 vertex-circle-clean fixed-order selected-row systems of
the reversed-second-block shuffle packet
(`data/certificates/block6_reversed_block_shuffle_vertex_circle_escape.json`),
previously closed only by 16 exact Kalmanson quotient-cone certificates
totaling 394 strict rows. With baseline `N` = the repo's strict
nested-interval rows (control: all 16 satisfiable, as cleanliness
requires):

- `N + S` (one disjunctive short-chord row per center): all 16 UNSAT.
- `N + O + D` (pure linear rows): 15 of 16 UNSAT; the record of escape
  index 13 is the unique survivor.
- `N + D`, `N + A`, `N + O` alone: 0 of 16.

So the pi/3-pigeonhole short-chord row alone gives a second, independent,
Kalmanson-free exact closure of the entire block-6 reversed-shuffle escape
family.

Test bed 2 (negative control): the C29 Sidon circulant (offsets 1,3,7,15),
in both the natural order and the recorded fixed escape order that required
a 165-row Kalmanson/Farkas certificate: satisfiable under all value-row
layers. The value rows complement, and do not dominate, Kalmanson/Altman
certificates; on Sidon-sparse patterns (pairwise row intersections at most
1, so no kite rows) they currently add nothing.

## Scope and next steps

- Fixed (assignment, cyclic order) diagnostics only; no all-order claim.
- The rows are uniform in `n`, so they are candidate material for the
  bridge-facing "enlarge the strict row family with a geometric source"
  obligation recorded in
  `docs/bootstrap-t12-151-6-label4-next-lemma-obligations.md`; whether the
  short-chord row (or its quantitative refinements) changes the 151:6
  target-sparse or order-sensitivity picture has not been tested in this
  session.
- Natural sharpenings exist (quantitative obtuse rows with the
  `sin(theta_i/2)` term; wedge inequalities coupling shared-pair centers;
  turning rows) and are recorded in the session attack report; only the
  five row families above were machine-tested here.
