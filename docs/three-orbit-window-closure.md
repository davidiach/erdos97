# Three-orbit (t=3) finite-m closure screen

Trust labels: `LEMMA` draft (review pending) for the normalization, atom
catalogue, and paired-cosine reduction; `NUMERICAL_EVIDENCE` with exact
escalation bookkeeping for the per-`m` screen verdicts. This note is a
restricted-family screen only. It is not an all-`m` lemma, it is not a proof
of Erdos Problem #97, it is not an `n`-range exclusion outside the stated
family, and it is not a counterexample or counterexample claim. The named
quarter-cell sub-cases for `m = 0 mod 4` are explicitly open.

Follow-up to `docs/half-step-matching-reduction.md` (open next target 2:
"resultant-based elimination for the generic branch over the discrete index
choices") and `docs/two-orbit-circulant-obstruction.md` (whose machine-audit
pattern this screen reuses). The numerical negative control for the same
family is the dynamic-witness sweep
(`docs/dynamic-witness-free-pattern-search.md`).

## Setting and normalization

Fix `m >= 3`, `h = pi/m`. The configuration family is three concentric
regular `m`-gon orbits

```text
A_k = exp(2ikh),  B_k = y exp(i(beta + 2kh)),  C_k = z exp(i(gamma + 2kh)),
```

`k = 0..m-1`, with `y, z > 0`. Rotation fixes `phi_A = 0`, scaling fixes
`r_A = 1`, orbit-index shifts put `beta, gamma` in `[0, 2h)`, and swapping
the labels `B, C` (with the radii) puts `beta < gamma`. Offsets `0` are
excluded: an aligned orbit pair places the smaller-radius point strictly
inside the hull (the center `O` is interior because it is the center of the
regular `m`-gon `{A_k}` with `m >= 3`), violating strict convexity; the
normalization `0 < beta < gamma < 2h` therefore loses no 4-bad
configurations. Inside this open box at most one of
`beta, gamma, gamma - beta` can equal the half-step `h` (two equalities at
once force `beta = gamma`, `gamma = 2h`, or `beta = 0`). The search splits
into four exhaustive branches:

- `G`: no offset equals `h`;
- `AB`: `beta = h`;
- `AC`: `gamma = h`;
- `BC`: `gamma - beta = h`.

Because `O` is interior and the `3m` angles are distinct, the points are in
strictly convex position iff the angular-order polygon
`..., C_{-1}, A_0, B_0, C_0, A_1, ...` has positive turns; by `C_m`
equivariance the three per-period turn determinants at `A_0`, `B_0`, `C_0`
suffice. Chord comparisons give the necessary radius window
`cos h < y, z < 1/cos h` (lower bound: a `B`- or `C`-vertex must lie
strictly outside the chord `A_0 A_1`; upper bound: `A_1` must lie strictly
outside the chord between the consecutive `B`- or `C`-orbit points
straddling it), the same window as the two-orbit note.

## Atom catalogue

For a center vertex, the other `3m - 1` vertices split into equidistance
atoms (sets forced to one circle):

- own pairs `{X_a, X_{m-a}}`, `1 <= a <= ceil(m/2) - 1`, at `4 r^2 sin^2(ah)`
  (strictly increasing in `a`);
- the own antipode (even `m`) at `4 r^2`;
- cross singles: with a generic offset, all `m` cross distances to one orbit
  are pairwise distinct (two equal cross distances force that offset into
  `{0, h}` mod `2h`, the quantization step of
  `docs/half-step-matching-reduction.md`, Lemma 3);
- on the unique half-step pair: cross pairs at `1 + r^2 - 2 r cos(oh)` for
  odd `o <= m - 1`, plus the cross pole (odd `m`) at `(1 + r)^2`-type
  distances.

A vertex is 4-covered iff some union of atoms of total size `>= 4` shares
one distance; it suffices to exclude the inclusion-minimal such unions.
Combos killed outright by exact arithmetic are not enumerated: two distinct
own pairs (strict monotonicity), own pair + own antipode (`a = m/2`
collision), two same-orbit generic singles (quantization), two cross pairs
(distinct `cos(oh)`), cross pair + cross pole (`cos(oh) = -1` needs
`o = m`), and combos short of four vertices. The remaining minimal combos
are, per branch:

- generic center (both cross offsets generic): own pair + one single to
  each other orbit (two equations);
- half-step-pair center: own pair + cross pair (one equation); own pair +
  cross pole + free-orbit single (odd `m`, two equations); own antipode +
  cross pair + free-orbit single (even `m`, two equations).

A randomized audit (`self_audit` in the checker) verifies on every run that
random configurations in each branch produce only the catalogued atoms.

## Paired-cosine reduction

Writing each cross equation as `cos(offset + known multiple of h) = u(radii)`
makes every equation linear in `(cos, sin)` of one unknown offset. Two
equations hitting the same offset with angle gap `Delta = 2sh` eliminate it:

```text
cos(t2) = u2,  cos(t2 + Delta) = u1
  ==>  (u2 cos Delta - u1)^2 = (1 - u2^2) sin^2 Delta,
```

a univariate polynomial pinning condition on the radius, after which the
offset is recovered in closed form and the remaining equations become
discrete scans. Branch by branch:

- `G`: the two `beta` equations pin `y` (cells `(a1, a2, s_ab)`); the two
  `gamma` equations pin `z` (cells `(a1, a3, s_ac)`, same shared `a1`); the
  two `gamma - beta` equations are scans over `j2, j3`.
- `AB`/`AC`: the two pinned-pair centers pin the pinned radius by
  univariate row polynomials (the `{P_a, X_o}` rows are exactly the
  two-orbit gear equation `E_A` and its `B`-side mirror); the free center's
  two equations are linear in the free offset and pin the free radius by a
  quartic; pole/antipode rows leave one leftover single scan.
- `BC`: the `B`-`C` cross equations are homogeneous in `(y, z)`, so each
  pinned-pair row pins the ratio `z/y` to an algebraic constant; ratio
  consistency is an exact condition, and the `A`-row pins `y` by the same
  quartic mechanism.

## Degenerate quarter cells (open)

The branch-`G` pinning polynomial vanishes identically iff `sin(2sh) = 0`,
`cos(2sh) = -1`, and `t_{a1} = t_{a2} = 2`, i.e. exactly when

```text
m = 0 mod 4,   a1 = a2 = m/4,   s = m/2.
```

In these cells the two paired equations coincide and leave a one-parameter
family instead of isolated radii (`E3` follows from `E1` because the index
sum shifts the angle by exactly `pi`; the analogous `d`-scan coincidence
`j2 + j3 = m/2 mod m` then reduces the full six-equation system to three
independent equations in four unknowns). The point screen cannot sweep
these solution curves, so for `m = 0 mod 4` the quarter cells are skipped,
counted, and reported as named open sub-cases (`open_quarter_cells` in the
artifact). Closing them needs a one-dimensional sweep with margin tracking
(or an exact curve argument) and is the recorded next target. For
`m != 0 mod 4` no degenerate cell exists (the identity conditions force
`4 | m`), and the branch enumeration is complete.

**Update (2026-06-13): the `m = 4` quarter cell is now closed exactly.** For
three concentric squares (`n = 12`) the branch-G 4-bad conditions reduce to
three explicit algebraic conditions on the radii and offsets, and an SMT (z3)
certificate shows they are infeasible inside the strict-convexity radius
window over all 64 discrete sign/witness combinations (convexity inequalities
are not even needed). See `docs/three-square-m4-exact-closure.md` and
`scripts/check_three_square_m4_closure.py`. The `m = 8, 12, 16` quarter cells
remain open; that reduction is the template.

## Machine screen

`scripts/check_three_orbit_window_closure.py` enumerates all discrete cells
of all four branches, runs the deterministic solution path in float64
inside the padded necessary window, and emits every joint configuration
passing a `1e-7` residual/margin band as a candidate. Every candidate is
re-derived along the same path at 60-digit mpmath precision
(`mp.polyroots` with extra precision; closed-form recoveries): an equality
residual above `1e-20` refutes it, below `1e-45` counts as satisfied,
anything between triggers a 240-digit re-derivation and is otherwise
reported as unresolved (blocking `--assert-clear`). Margin handling is
strict-first: configurations with a decisively negative margin are refuted;
margins within `1e-30` of zero are re-derived at 240 digits and classified
as exact boundary hits (excluded by the open constraints) when they stay
within `1e-100`. Any survivor must additionally pass the direct 4-bad
minimum-spread confirmation before being reported -- loudly -- as feasible;
nothing is ever silently accepted.

Redundant audits built into the run and the test suite
(`tests/test_three_orbit_window_closure.py`):

- random-configuration atom-catalogue audit per branch and `m`;
- planted-solution tests: raw two- and four-equation systems solved by
  `fsolve` (no reduction) must be recovered by the pinning polynomials and
  solution lists, including multiplicity-2 roots;
- per-option geometry tests: every pinned-row polynomial root and every
  `BC` ratio option is checked against direct coordinate distances.

## Recorded result

```bash
python scripts/check_three_orbit_window_closure.py --min-m 3 --max-m 16 \
  --audit-samples 40 \
  --write-artifact data/certificates/three_orbit_window_closure_m3_16.json
```

The stored artifact records, for `m = 3..16`: every branch cell screened,
every screen candidate refuted at 60 digits or excluded as an exact
boundary hit, no unresolved cases, no feasible survivors, and the
`m = 4, 8, 12, 16` quarter cells as the only open sub-cases. In repo terms:
no strictly convex 4-bad three-orbit configuration exists at screen
precision for `m = 3..16` outside the named quarter cells, and for
`m = 3, 5, 6, 7, 9, 10, 11, 13, 14, 15` the branch coverage has no named
gap at all.

## Scope and non-claims

- The family is exactly three full concentric regular `m`-gon orbits with a
  common center; partial orbits, mixed orbit sizes, non-cyclic
  configurations, `t >= 4`, and the general problem are untouched.
- The screen verdict is float64-plus-escalation evidence, not an exact
  certificate: cells with no in-band candidate are excluded at float
  precision only. An exact replay (sympy arithmetic over the cyclotomic
  values, or interval arithmetic with directed rounding) is the natural
  hardening step and is not claimed here.
- The quarter cells for `m = 0 mod 4` are open sub-cases, recorded in the
  artifact; nothing is claimed about them.
- The official/global status of Erdos Problem #97 is unchanged
  (falsifiable/open); no repository source-of-truth claim is modified by
  this note.

## Adversarial review reconciliation (2026-06-12)

A fresh-context adversarial review independently re-derived the atom
catalogue, all equation forms and sign conventions (with raw fsolve-planted
systems and end-to-end coordinate checks), the quarter-cell
characterization, and the verdict ladder, and confirmed the recorded
artifact as stated. It flagged two latent infrastructure defects, both
verified unexercised in the recorded run and hardened immediately after:
BC candidate cells are now keyed by option content instead of positions in
a data-dependent list (options with ratio within `1e-9` of zero are
excluded deterministically in every backend; such ratios are window-killed
regardless, so no solution is lost), and a high-precision root-finding
failure now raises an escalation-inconclusive verdict (counted as
unresolved) instead of reading as an empty cell. The artifact was
regenerated with the hardened code.

## Next steps recorded for the loop

1. Close the quarter cells by a swept one-parameter analysis (the reduced
   system is three equations in four unknowns with explicit curves
   `beta(y)`, `gamma(z)` and a pinned hyperbola `z/y` in the doubly
   degenerate sub-cell).
2. Exact small-`m` replay of the same enumeration in sympy arithmetic to
   upgrade the screen tiers to `EXACT_OBSTRUCTION` for `m <= 8`.
3. Attempt the all-`m` case ladder for the `AB`/`AC` pinned-row
   polynomials, reusing the two-orbit cosine-difference identities; the
   pinned rows are the two-orbit gear equations, so the existing window
   lemma already kills the `{P_a, X_o}` + `{P_a, X_o}` row shapes for all
   `m`, and only the pole/antipode and free-row layers are new.
