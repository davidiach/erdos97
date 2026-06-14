# Three-orbit quarter cells: the A-row reduction and the boundary-band lemma

Trust labels: `LEMMA` (exact, self-checked) for the A-row reduction and the
boundary-band confinement; `NUMERICAL_EVIDENCE` (float grid, tangency-limited)
for the non-convexity of the witness locus at `m = 8, 12, 16`. The `m = 4` cell
is the only quarter cell closed **exactly** so far, by SMT
(`docs/three-square-m4-exact-closure.md`). This is a restricted-family analysis
of the three-orbit (t=3) `C_m` family. It is not an all-`m` lemma, not a proof
of Erdos Problem #97, and not a counterexample.

This note reduces, and partially settles, the degenerate `m = 0 mod 4` quarter
cells that the three-orbit finite-`m` closure screen
(`docs/three-orbit-window-closure.md`) skips. The key simplification: the
obstruction lives entirely in the **A-row**, so it is uniform in the C-row
own-pair choice `a3`, and a single condition covers every quarter cell. The
`m = 4` cell is then closed exactly; for `m = 8, 12, 16` the witness locus is
shown numerically to be tangent to (and on the non-convex side of) the
convexity boundary, which is strong evidence of closure but, because the
margin vanishes, **not** a certificate -- those cells remain open pending the
exact turn-sign lemma stated at the end.

## The A-row reduction

"Quarter cell" means the branch-G cell (no half-step offset) in which the
A-row and B-row select their own pair at offset `a1 = a2 = m/4` -- the
residual the generic three-orbit screen skips because its pinning degenerates
there. Every other branch-G cell (a different own pair `a != m/4`, or a
half-step branch) is already closed by the generic screen
(`docs/three-orbit-window-closure.md`); this note handles only the skipped
`a1 = a2 = m/4` residual, so the reduction below is for that cell.

In a quarter cell the A-row (and B-row) own pair is the 90-degree pair
`{A_{m/4}, A_{-m/4}}` (`4 sin^2((m/4) h) = 2`), at squared distance 2 from
`A_0`. So in this cell `A_0` is 4-bad only if it additionally has a B-vertex
and a C-vertex at squared distance 2. With
`P(r) = (r^2-1)/(2r)` and `h = pi/m`, a vertex of radius `r` at angle `theta`
is at squared distance 2 from `A_0 = (1,0)` iff `cos(theta) = P(r)`. The four
(resp. `m`) B-vertices sit at angles `beta + 2k h`, so:

```text
(i)  P(y) in { cos(beta  + 2k h) : k }     [A_0 has a B-witness at dist^2 2]
(ii) P(z) in { cos(gamma + 2k h) : k }     [A_0 has a C-witness at dist^2 2]
```

Conditions (i)-(ii) involve only the A-row and B-row, which are the 90-pair in
**every** quarter cell regardless of `a3`. Hence **if no strictly convex
window configuration satisfies (i)&(ii), then `A_0` is never 4-bad, so no
quarter-cell configuration is 4-bad** -- the C-row and the value of `a3` never
enter.

## Exact boundary-band lemma

`LEMMA` (elementary; verified as a self-test in the checker). For
`m = 0 mod 4`, the angle `pi/2` is an integer multiple of the orbit step `2h`
(`pi/2 = (m/4)*2h`), so `pi/2 ≡ 0 (mod 2h)`. In the strict-convexity radius
window `cos h < y < sec h` one has `|P(y)| < omega_m := P(sec h)`, so any
vertex at squared distance 2 from `A_0` lies within
`delta_m := arcsin(omega_m)` of `±pi/2`; reduced mod `2h` (where `±pi/2 ≡ 0`),
its offset is forced into the **boundary bands**

```text
beta, gamma  in  (0, delta_m) ∪ (2h - delta_m, 2h).
```

Geometrically: to put a cross-orbit vertex at `A_0`'s witness distance, the
cross orbit must nearly align with the A-orbit (offset near `0` or `2h`). That
near-alignment is exactly what strict convexity forbids.

## The tangency, and why this is screen-grade for m >= 8

Within the boundary bands and the window, the witness locus turns out to be
**tangent** to the convexity boundary: over a dense grid of `(i)&(ii)`
configurations with `0 < beta < gamma < 2h`, the maximum of the minimum
per-period turn determinant is strictly negative but its supremum is `0`,
attained only in the degenerate orbit-coincidence limit (which strict
convexity excludes). The sampled maximum is **not** monotone in the grid, but
it can be driven arbitrarily close to `0` by sampling nearer the tangency
(e.g. a grid of `320` reaches `~-1e-10` for `m = 16`). So every sampled
configuration is strictly non-convex, but with no uniform margin -- the margin
is grid-dependent with supremum `0`.

This tangency is why:

- the `m = 4` cell needed an **exact** SMT decision
  (`docs/three-square-m4-exact-closure.md`) rather than a margin screen; and
- the float grid at `m = 8, 12, 16` is **evidence, not a certificate**: it
  shows the locus sits on the non-convex side of the boundary, but the
  vanishing, grid-dependent margin means it cannot rule out an exactly-convex
  point on the locus. Those cells remain open; `m = 4` is the only quarter
  cell closed exactly.

## Recorded route limits

So future iterations do not re-attempt them:

- **The exact-SMT encoding used for `m = 4` did not close `m >= 8`.** z3
  nonlinear real arithmetic returns `unknown` on the witness-membership
  disjunctions for `m >= 8`, and times out on the cubic turn determinants in
  the explicit-combo encoding (both with and without the `(iii)` tie). The
  `m = 4` success relied on the small (4-value) witness sets and the window
  making convexity unnecessary; neither holds for `m >= 8`. A different
  encoding (CAD/resultants on the band-confined region, per below) may still
  succeed -- only this particular SMT encoding is recorded as a dead end.
- **A blind margin screen cannot close the cells**, because the locus is
  tangent to the convexity boundary (margin `-> 0`).

## The open lemma (recommended next step)

The clean exact, `m`-uniform statement that would close all quarter cells:

```text
On the (i)&(ii) witness locus inside the window, the minimum per-period turn
determinant is <= 0, with equality only at the degenerate orbit-coincidence
limit.
```

The boundary-band lemma confines the locus to a small explicit region; the
remaining task is to show one turn determinant is sign-definite there (a
factored form vanishing exactly on the degenerate locus would do it). The SMT
route is recorded as a dead end for this; an analytic turn-sign argument or an
exact CAD/resultant computation on the confined region is the recommended path.

Follow-up preflight: `docs/quarter-cell-signed-band-preflight.md` splits the
boundary-band locus into three band orders and `12` radius-sign cells. In each
cell it records a fixed turn determinant whose first nonzero boundary term is
negative for `m >= 8`, with deterministic grid stress of the same fixed turns.
That narrows the exact target but does not prove the full sign-definiteness
statement, so the `m = 8, 12, 16` cells remain open.

## Reproduce

```bash
python scripts/check_quarter_cell_closure.py --assert-clear \
  --write-artifact data/certificates/quarter_cell_closure.json
```

## Scope and non-claims

- The A-row reduction and the boundary-band confinement are exact and
  `m`-uniform proved lemmas (machine-checked self-test).
- `m = 4` is the only quarter cell closed **exactly** (by SMT, separate note).
  For `m = 8, 12, 16` the witness locus is shown numerically to be tangent to
  and on the non-convex side of the convexity boundary -- evidence of closure,
  not a certificate; those cells remain **open**.
- Says nothing about `m` not divisible by 4 (no quarter cell there -- the
  three-orbit screen already closes those), about more than three orbits, or
  about the general problem; the official/global status of Erdos Problem #97 is
  unchanged (falsifiable/open).
