# Exact SMT closure of the m=4 three-square quarter cell (n=12)

Trust labels: `LEMMA` draft (review pending) for the reduction;
`EXACT_OBSTRUCTION` (SMT certificate) for the infeasibility decision. This is
a restricted-family result: three concentric regular 4-gons, branch G. It is
not an all-`m` result, not a proof of Erdos Problem #97, and not a
counterexample.

Closes the smallest open sub-case left by the three-orbit finite-`m` closure
screen (`docs/three-orbit-window-closure.md`): the degenerate `m = 0 mod 4`
quarter cells. The screen reports those cells as skipped/open; this note
closes `m = 4` (three concentric squares, `n = 12`) exactly.

## Setting

Three concentric regular 4-gons (squares), `h = pi/4`:

```text
A_k = exp(2ikh),  B_k = y exp(i(beta + 2kh)),  C_k = z exp(i(gamma + 2kh)),
```

`k = 0..3`, radii `y, z > 0`, offsets normalized to `0 < beta < gamma < pi/2`
(rotation fixes `A`, scaling fixes `r_A = 1`, index shifts and the `B<->C`
relabel put both offsets in the first quadrant with `beta < gamma`). Because
`own_pair_avals(4) = {1}`, every square's only own equidistance pair from a
vertex is the 90-degree diagonal pair `{X_{1}, X_{3}}`, at squared distance
`2 r^2`. So `m = 4` is entirely inside the quarter regime that the screen
skips, which is why it needs a dedicated argument.

## Reduction to three algebraic conditions

A vertex at radius `r`, angle `theta` is at squared distance 2 from
`A_0 = (1,0)` iff `cos(theta) = P(r) := (r^2 - 1)/(2r)`. The four B-vertices
sit at angles `beta + k*pi/2`, whose cosines are exactly
`{+-cos beta, +-sin beta}`. In branch G (no half-step offset) two same-orbit
witnesses cannot be equidistant from a foreign center, so a 4-bad center uses
its own 90-pair (automatically at the right distance) plus one witness from
each other orbit at that distance. Hence, writing `Q(y,z) := (z^2-y^2)/(2yz)`:

```text
(i)   P(y)   in {+-cos beta,  +-sin beta}            [A_0 has a B-witness]
(ii)  P(z)   in {+-cos gamma, +-sin gamma}           [A_0 has a C-witness]
(iii) Q(y,z) in {+-cos(gamma-beta), +-sin(gamma-beta)}   [B_0 has a C-witness]
```

is equivalent to branch-G 4-badness of the three-square configuration. The
other witness conditions (`B_0` and `C_0` seeing an `A`-vertex, `C_0` seeing a
`B`-vertex) are implied: each witness-angle set `{cos(theta + k*pi/2)}` equals
`{+-cos theta, +-sin theta}`, is closed under negation, and the target
distances are exact negatives of the ones above. This equivalence is exact for
`m = 4` and independent of the witness index ("`s`") that the screen uses to
pin radii — which is precisely why the screen's pinning degenerates here while
the underlying conditions remain finite and explicit.

**Log-radius form.** With `p = P(y) = sinh(ln y)`, `q = P(z) = sinh(ln z)`, the
quantity `Q = sinh(ln z - ln y)` obeys the sinh subtraction identity

```text
Q = q*sqrt(1+p^2) - p*sqrt(1+q^2),
```

so `sign(Q) = sign(z - y) = sign(q - p)`. This monotonicity lever already
forces many sign combinations to contradict (e.g. `P(y)=cos beta`,
`P(z)=cos gamma`, `Q=cos(gamma-beta)`: since `gamma > beta` gives
`cos gamma < cos beta`, hence `z < y`, while `Q = cos(gamma-beta) > 0` demands
`z > y`).

## Strict-convexity window

With the common center interior and the `12` angles distinct, strict convexity
of the interleaved 12-gon is equivalent to positivity of the three per-period
turn determinants and forces the radius window `cos h < y, z < 1/cos h`, i.e.

```text
1/2 < y^2 < 2,   1/2 < z^2 < 2,   0 < beta < gamma < pi/2.
```

In particular `|P(y)|, |P(z)| < 1/(2*sqrt 2) ~ 0.354`. Since
`cos^2 + sin^2 = 1`, at most one of `cos theta, sin theta` is below `0.354`, so
(i)/(ii) already force `beta, gamma` out of the middle band `[20.7, 69.3]`
degrees.

## SMT decision

`scripts/check_three_square_m4_closure.py` rationalizes the system via the
tangent half-angle (`t = tan(beta/2)`, `u = tan(gamma/2)` in `(0,1)`,
`t < u`), turning (i)-(iii), the window, and the angle order into a polynomial
system in `(y, z, t, u)`, and asks z3 whether it is satisfiable, over all
`64` discrete sign/witness combinations.

Recorded result: **all 64 combinations are UNSAT**, and the convexity
inequalities are not even added — the radius window alone makes the 4-bad
conditions infeasible. Since dropping convexity only enlarges the feasible
region, the strictly convex case is a fortiori empty. Therefore **no strictly
convex three-square (`n = 12`) configuration is branch-G 4-bad.**

The checker carries two internal guards:

- *Faithfulness*: for each witness index the radius solving the distance
  equation yields `P(r)` equal to the witness-angle cosine, which lies in the
  modelled set — confirming (i)-(iii) encode the geometry exactly.
- *Non-vacuity*: the conditions are satisfiable in the degenerate boundary
  limit `gamma -> pi/2`, `z -> 1` (the `C` square collapses onto the `A`
  square), so the window-UNSAT is a genuine obstruction rather than a vacuous
  over-constraint — solutions appear exactly at the excluded,
  non-strictly-convex boundary.

## Scope and non-claims

- Closes the `m = 4` branch-G quarter cell (the smallest open three-orbit
  sub-case), and in fact all of branch G for `m = 4`, exactly.
- The half-step branches AB/AC/BC for `m = 4` are covered at screen grade by
  the main three-orbit artifact; this note does not re-derive them exactly.
- The `m = 8, 12, 16` quarter cells remain open; the reduction here (own
  90-pair plus cross singles, the `P`/`Q` conditions, the sinh identity, and
  the window bound) is the template, but for `m > 4` the C-row own pair can
  differ from `m/4` and the witness-angle sets are larger.
- SMT (z3) UNSAT is an accepted exact-obstruction certificate in this repo
  (alongside the existing Kalmanson z3 certificates); it is reproducible by
  re-running the checker but is not independently human-auditable without z3.
  The reduction, the window necessity, and the sinh identity above are the
  human-checkable scaffolding.
- The official/global status of Erdos Problem #97 is unchanged
  (falsifiable/open); no source-of-truth dashboard claim is modified.

## Reproduce

```bash
python scripts/check_three_square_m4_closure.py --assert-clear \
  --write-artifact data/certificates/three_square_m4_closure.json
```
