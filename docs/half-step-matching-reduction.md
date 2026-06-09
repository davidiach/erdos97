# Half-step matching reduction for multi-orbit cyclic configurations

Trust labels: `LEMMA` draft (review pending) for the matching lemma and the
row-shape corollary; reduction bookkeeping for the equation catalogues. This
note is a structural reduction for restricted symmetric families only. It is
not a proof of Erdos Problem #97, it is not an `n`-range exclusion, and it
is not a counterexample or counterexample search.

## Setting

Fix `m >= 3`, `h = pi/m`, and a strictly convex polygon whose vertex set is
a union of `t >= 2` noncentral `C_m` orbits

```text
X^{(i)}_k = r_i * exp(I*(phi_i + 2kh)),   k = 0..m-1,   i = 1..t,
```

with all `tm` points distinct. Define the pairwise offsets
`delta_ij = phi_j - phi_i mod 2h`. The two-orbit case is settled by
`docs/two-orbit-circulant-obstruction.md` and
`docs/symmetric-two-orbit-reduction.md`; this note organizes what survives
for `t >= 3`.

Throughout, "row" means a witness 4-set on one circle centered at a vertex,
and "4-bad" means every vertex has such a row, as in `STATE.md`.

## Lemma 1 (no aligned pair)

No pairwise offset satisfies `delta_ij = 0`.

Proof. If `delta_ij = 0`, each ray carrying a vertex of orbit `i` carries a
vertex of orbit `j`. The rotation center `O` is interior to the hull (it is
the center of the regular `m`-gon formed by either orbit, `m >= 3`). If
`r_i = r_j` the two orbits coincide, contradicting distinctness; otherwise
the smaller-radius point lies strictly between `O` and the larger-radius
point on the same ray, hence strictly inside the hull, contradicting strict
convexity. QED (review pending).

## Lemma 2 (half-step partners are matched)

Call `{i, j}` a half-step pair if `delta_ij = h`. Then no orbit belongs to
two half-step pairs. Consequently the half-step pairs form a partial
matching on the `t` orbits.

Proof. If `delta_ij = h` and `delta_ik = h`, then
`delta_jk = delta_ik - delta_ij = 0 mod 2h`, which Lemma 1 forbids. QED
(review pending).

So for `t = 3`, at least two of the three pairwise offsets are *generic*,
meaning not in `{0, h} mod 2h`; for general `t`, at least
`binom(t,2) - floor(t/2)` of the offsets are generic.

## Lemma 3 (cross-pair quantization)

If some row centered at a vertex `c` of orbit `i` contains two witnesses of
orbit `j != i`, then `delta_ij in {0, h} mod 2h`; by Lemma 1 it is `h`, so
`{i, j}` is a half-step pair.

Proof. Two same-orbit witnesses `p, q` equidistant from `c` put `c` on the
perpendicular bisector of `pq`; since `|p| = |q|`, that bisector passes
through `O`, so `p, q` are symmetric about the line `Oc`. The mean of their
angles is therefore the angle of `c` modulo `pi`:
`phi_j + (k+l)h = phi_i mod pi`, hence `delta_ij in h*Z mod pi`, which is
`{0, h} mod 2h` after orbit re-indexing. QED (review pending).

## Corollary (row shapes for t = 3)

Let the orbits be `A, B, C`. By Lemmas 1-3 at most one pair, say `{A, B}`,
is half-step, and rows decompose per center orbit as follows (an "own pair"
is the automatic symmetric same-orbit pair `{+a, -a}`; a "single" is one
witness from another orbit; the antipode is the lone same-orbit option at
distance `2r` when `m` is even):

- `C`-rows (both `C`-offsets generic): one own pair plus one `A`-single
  plus one `B`-single, or (even `m`) own antipode variants. Every such row
  carries two independent distance equations.
- `A`-rows and `B`-rows: an own pair plus a cross pair from the half-step
  partner (one equation), or an own pair plus two singles (two equations),
  or a partner cross pair plus own pair/antipode variants.
- If no pair is half-step, every row of every orbit is own pair plus two
  singles, carrying two equations.

Counting continuous unknowns (after fixing scale, rotation, and orbit `A`'s
phase): in the half-step branch `beta = h` is pinned, leaving the three
unknowns `y, z, gamma` against at least `1 + 1 + 2 = 4` equations; in the
no-half-step branch all four of `y, z, beta, gamma` stay free against
`2 + 2 + 2 = 6` equations. Every branch is therefore strictly
overdetermined before any discrete choices; this counting is bookkeeping,
not an obstruction.

## Explicit generic-branch system (t = 3, no half-step pair)

With `r_A = 1`, `phi_A = 0`, unknowns `y = r_B`, `z = r_C`,
`beta = phi_B`, `gamma = phi_C`, and discrete choices
`a_1, a_2, a_3` (own-pair offsets) and `k_1, j_1, k_2, j_2, k_3, j_3`
(single indices):

```text
A-row:  y^2 + 1 - 2y cos(beta + 2 k_1 h)          = 4 sin^2(a_1 h)
        z^2 + 1 - 2z cos(gamma + 2 j_1 h)         = 4 sin^2(a_1 h)
B-row:  1 + y^2 - 2y cos(2 k_2 h - beta)          = 4 y^2 sin^2(a_2 h)
        z^2 + y^2 - 2zy cos(gamma - beta + 2 j_2 h) = 4 y^2 sin^2(a_2 h)
C-row:  1 + z^2 - 2z cos(2 k_3 h - gamma)         = 4 z^2 sin^2(a_3 h)
        y^2 + z^2 - 2yz cos(beta - gamma + 2 j_3 h) = 4 z^2 sin^2(a_3 h)
```

plus strict convexity of the interleaved `3m`-gon and the genericity side
conditions. Six equations in four unknowns for each discrete choice. The
half-step-pair branch replaces two of these rows by single gear equations of
the form settled in the two-orbit notes.

## Status and next steps

- The dynamic-witness deep sweep
  (`data/runs/dynamic_witness_sweep_2026-06-09b/summary.json`) provides the
  numerical negative control for exactly these systems at `t = 3..10`:
  no strictly convex solution basin was found, and all small spreads are
  floor-riding degenerations.
- Open next targets recorded for the loop: (1) a window analysis for the
  half-step-pair branch, reusing the two-orbit gear machinery with the
  third orbit's two single-equations adjoined; (2) resultant-based
  elimination for the generic branch over the discrete index choices, with
  the same exact audit pattern as
  `scripts/check_two_orbit_dynamic_window_lemma.py`.
- None of this covers partial orbits, mirror-only symmetry, or asymmetric
  configurations, and none of it changes any repository status.
