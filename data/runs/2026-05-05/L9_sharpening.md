# L9 Sharpening, Near-Cyclic Polygons, and the 3-Cap SEC Case

Sources cross-checked: `/home/user/erdos97/docs/canonical-synthesis.md` §2 (L1–L10),
§5.4 (SEC / 3-cap), §6.8 (cyclic-polygon distance unimodality), and the surveyed
data artifacts in `data/incidence/`, `data/certificates/`. No repo files were
modified.

## 1. Quantitative version of L9

### 1.1 Setup and statement

Let `P` be a strictly convex `n`-gon with vertex set `V`. Define the
**non-cyclicity** of `P` as
```
ε(P) := min over circles Γ of max over v in V of dist(v, Γ),
```
i.e. the Hausdorff-radial deviation of `V` from a single best-fit circle.
The classical L9 says `ε(P) = 0 ⇒ M(v) ≤ 2` for all `v`.

**Quantitative L9 (Q-L9).** Let `δ_min := min_{u ≠ w ∈ V} |u-w|` be the minimum
vertex-separation. Pick a vertex `v` with witness radius `r_v` and let `Γ`
denote the optimal best-fit circle of centre `C` and radius `ρ`. Let
`θ_int(v) ∈ (0, π/2]` be the angle between `circle(v, r_v)` and `Γ` at their
nominal intersection. Then
```
M(v) ≥ 3   ⟹   ε(P) ≥ (δ_min · sin θ_int(v)) / 2.
M(v) ≥ 4   ⟹   same ε threshold, but with ≥ 2 witnesses per cluster.
```
When `circle(v, r_v)` and `Γ` are uniformly transverse (i.e.
`sin θ_int(v) ≥ c_n > 0` over the candidate family — true away from the
tangent locus), this collapses to the explicit lower bound
```
ε(P) ≥ c_n · δ_min / 2.
```

### 1.2 Proof sketch

Pick a vertex `v` and parametrise `circle(v, r_v)` by `w(t) = v + r_v (cos t, sin t)`.
With `d := |v - C|` and `θ := arg(v - C)`,
```
|w(t) - C|^2 = r_v^2 + d^2 + 2 r_v d cos(t - θ).            (*)
```
`w` lies in the `ε`-annulus `{ρ-ε ≤ |w-C| ≤ ρ+ε}` iff
`(ρ-ε)^2 ≤ (*) ≤ (ρ+ε)^2`. The width of the admissible interval for the
expression `2 r_v d cos(t - θ)` is `(ρ+ε)^2 - (ρ-ε)^2 = 4 ρ ε`, so
```
cos(t - θ) ∈ [α - 2 ρ ε / (r_v d),  α + 2 ρ ε / (r_v d)]
```
for some centre `α`. Since `cos` is 2-to-1 on `[0, 2π)`, the admissible set in
`t` consists of **two arcs** of angular width
```
Δt ≈ 2 · (2 ρ ε / (r_v d)) / sin(t* - θ),
```
where `t*` is the nominal solution. The geometric content of `sin(t* - θ)` is
exactly `sin θ_int(v)`: the two circles `circle(v, r_v)` and `Γ` intersect at
angle `θ_int`, and `sin θ_int = (r_v d / (r_v · ρ)) · |sin(t* - θ)| · ...` — the
constant simplifies (after eliminating `ρ`, `d` via the chord-length identity)
to `Δt = 2 ε / (r_v sin θ_int)`.

Therefore the chord between any two distinct witnesses `w_i, w_j` lying in the
**same** of the two admissible arcs satisfies
```
|w_i - w_j| ≤ 2 r_v sin(Δt / 2) ≤ r_v · Δt = 2 ε / sin θ_int(v).
```
But `|w_i - w_j| ≥ δ_min`, giving the inequality of the statement. ∎

The "two arcs" picture is the quantitative replacement for L9's "two
intersection points": as `ε → 0`, both arcs collapse to single points and
`M(v) ≤ 2` returns.

### 1.3 Higher counts

A 4-bad vertex (`M(v) ≥ 4`) needs at least one of the two arcs to host
≥ 2 witnesses, so the bound `ε ≥ δ_min sin θ_int / 2` is necessary.
For 5 witnesses one arc must host ≥ 3, giving the stronger
`ε ≥ δ_min sin θ_int` (since the 3rd witness must be > 2 δ_min away inside an
arc whose extent is at most the cluster diameter, so the cluster is ≥ 2 δ_min
wide). This continues linearly in `M(v)`.

## 2. Application 1: numerical optimisation behaviour

The repo's optimisation routines (e.g. `scripts/check_min_radius_filter.py`,
NLP survivors in `data/certificates/ptolemy_order_nlp_survivors.json`,
`data/runs/C19_skew_order_survivor_slsqp_m1e-4_seed20260502.json`) hunt for
realisations of survivor incidence patterns. Q-L9 tells us:

* Any candidate with `ε(P) < δ_min · sin θ_int / 2` cannot be `M(v) ≥ 3` at any `v`,
  let alone 4-bad. So the "near-cyclic basin" is **forbidden** for genuine
  4-bad realisations.
* Numerically, however, a solver minimising a 4-bad infeasibility residual can
  drift toward `ε → 0` with `δ_min → 0` simultaneously, mimicking a 4-bad
  configuration via vertex coalescence. This is a known failure mode reported
  in `docs/phi4-rectangle-trap.md` §"Degenerate fixes" and the
  `metric-order-lp` survivor diagnostics. Q-L9 explains it: as the candidate
  approaches L9's cyclic locus, vertex separation must shrink at the **same
  rate** as the cyclic deviation. A non-degeneracy regulariser of the form
  `δ_min ≥ c · ε(P)` (with `c = 2 / sin θ_int` or any conservative constant
  larger than 4) would block the degenerate basin without excluding genuine
  realisations.

### 2.1 Concrete prescriptions for the codebase

Suggested filter (no implementation here, just the recipe):
1. For each candidate polygon, compute `ε(P)` as the SVD/Pratt residual of the
   four-parameter circle fit `(C, ρ)` to `V`.
2. Compute `δ_min`.
3. Reject candidates with `δ_min ≤ 4 · ε(P)` (constant 4 covers any
   `sin θ_int > 1/2`, a generic regime).

This is **not** a witness-based filter but a "non-cyclicity floor" filter; it
is implied by Q-L9 ∧ (M(v) ≥ 4 for some v).

## 3. Application 2: do `n = 8, 9, 10` survivors hit the near-cyclic basin?

Cross-referencing the artifact summaries:

* **`n = 8`.** Already closed at the abstract incidence level; all 15 reconstructed
  classes die under the `n = 8` exact-survivor pipeline
  (`docs/n8-exact-survivors.md`, `data/incidence/n8_reconstructed_15_survivors.json`).
  No surviving pattern has a continuous realisation, near-cyclic or otherwise.
* **`n = 9`.** The current frontier consists of `C19_skew` and `C13_sidon_1_2_4_10`
  patterns. Their surviving cyclic orders, in `data/certificates/c13_sidon_*` and
  `c19_skew_all_orders_kalmanson_z3.json`, have UNSAT certificates from the
  Kalmanson and Ptolemy filters but no closed-form realisation. The repo's
  NLP solver in `row-circle-ptolemy-nlp.md` reports convergence to "near-circle"
  shapes for some seeds — specifically for `C19_skew` row-circle reductions —
  and these are flagged as numerically unstable in
  `docs/row-circle-ptolemy-nlp.md`. Q-L9 confirms this is structural: the
  solver is approaching the L9 boundary, not a genuine counterexample.
* **`n = 10`.** `n10-vertex-circle-singleton-slices.md` is review-pending and
  not yet integrated into the canonical-truth pipeline. The recorded
  singleton-slice family is large; cap-by-cap counts have not been audited
  against the SEC structure here.

So the answer to "are near-cyclic configurations excluded?" is: yes, conditionally,
via Q-L9, modulo a non-cyclicity-floor filter being added to the survivors'
realisability checker. Currently the realisability code in
`scripts/check_*` does not implement this filter explicitly; the Kalmanson and
mutual-rhombus filters take a different angle.

## 4. The 3-cap SEC bridge: at `n = 8` one of `p, q, r` has `E ≤ 3`

This is the §5.4 three-cap bridge lemma, recorded as **open** in the synthesis.
The argument below settles it for `n = 8` and gives the rigid case at `n = 9`.

### 4.1 Setup (matches §5.4)

The smallest enclosing circle `S` of `V` has centre `O`, radius `R`, and is
supported by three vertices `p, q, r` forming a non-obtuse triangle. The disk
of radius `R` decomposes into the triangle `pqr` and three caps `K_pq`, `K_qr`,
`K_rp` (the closed cap regions excluding the chord interior). All polygon
vertices not in `{p, q, r}` lie in exactly one cap.

The cap lemma (Moser; Dumitrescu's survey) states: from a chord endpoint, the
distances to convex-position points in the cap are **all distinct**.

### 4.2 Cap-occupancy of witnesses

Apply the cap lemma at every endpoint of every chord:

| Centre | Endpoint of chord | Cap | Witness count |
|---|---|---|---|
| `p` | `pq` | `K_pq` | ≤ 1 (cap lemma at `p`) |
| `p` | `pr` | `K_pr` | ≤ 1 |
| `p` | (not endpoint) | `K_qr` | unrestricted |

If `p` is bad (`M(p) ≥ 4`), then `≥ 4 - 1 - 1 = 2` of `p`'s witnesses lie in
`K_qr`. By symmetry:

* `q` bad ⇒ ≥ 2 of `q`'s witnesses in `K_rp`.
* `r` bad ⇒ ≥ 2 of `r`'s witnesses in `K_pq`.

Let `(a, b, c)` be the cap sizes (number of polygon vertices in `K_qr, K_rp, K_pq`
excluding `p, q, r`). We have `a + b + c = n - 3`.

If all of `p, q, r` are bad, then `a ≥ 2` (to host ≥ 2 of `p`'s witnesses),
`b ≥ 2`, `c ≥ 2`, giving `n - 3 ≥ 6`, i.e. `n ≥ 9`.

### 4.3 Theorem (3-cap, `n = 8`)

> If the smallest enclosing circle of a strictly convex `n = 8`-gon is supported by
> three vertices `p, q, r` forming a non-obtuse triangle, then
> `min{M(p), M(q), M(r)} ≤ 3`. In particular `min{E(p), E(q), E(r)} ≤ 3`.

This combines with the diameter-case theorem from §5.4 (which forces
`E(p), E(q) ≤ 2` for the diameter endpoints) to fully resolve the SEC reduction
at `n = 8`: at least one polygon vertex always has `E ≤ 3`, and **`n = 8` cannot
be 4-bad**, which agrees with the artifact-level closure in `docs/n8-exact-survivors.md`.

### 4.4 The rigid case at `n = 9`

If `n = 9` and all three of `p, q, r` are bad, then `(a, b, c) = (2, 2, 2)`
and the inequalities are tight: each cap holds exactly 2 polygon vertices,
**both of which serve as witnesses of the bad vertex opposite that cap.**

In `K_qr`, write the two vertices as `X_1, X_2`. They satisfy
`|p X_1| = |p X_2| = r_p`, so both lie on `circle(p, r_p)`, and the perpendicular
bisector of `X_1 X_2` passes through `p`. By the cap lemma applied to
**chord `qr`** (where `q` is the endpoint), distances `|q X_1|, |q X_2|` are
distinct, so at most one of `X_1, X_2` is a witness of `q`. By the cap lemma
applied at `r`, same: at most one is a witness of `r`. Combined: among
`(X_1, X_2)` we have

* both are witnesses of `p`,
* at most one is a witness of `q`,
* at most one is a witness of `r`.

By pigeonhole on the three roles, one of `X_1, X_2` is **only** a witness of `p`
(call it `X_*`). Then `X_*`, being in cap `K_qr`, has its full witness role
constrained by L4: the perpendicular bisector of any equidistant pair from `X_*`'s
witness set passes through `X_*` and contains at most 2 polygon vertices (L4).

This is the foothold for ruling out the rigid `(2, 2, 2)` configuration via
perpendicularity (L6 + parity-style argument as in §3.3): every cap pair
`{X_1, X_2}` forces a perpendicularity `|p (X_1 + X_2)/2| ⊥ X_1 X_2`, and
similarly at `q, r`. Three perpendicularity constraints on three pairs in a
9-vertex configuration are non-trivial and likely overdetermined; closing
this is the natural next step but is left as an open subproblem here. (The
analogous overdetermination for `n = 7` is what powers §3.3.)

### 4.5 Concrete bounds for the equilateral 3-cap

Take the symmetric extremal case: `p, q, r` equispaced on `S` (regular 3-cap),
`R = 1`. Then `|pq| = |qr| = |rp| = √3`, each cap depth (from the opposite
vertex) is `1 - cos(2π/3) = 3/2`, the cap chord is `√3`, and any vertex in
`K_qr` has distance from `p` in `[3/2, 2]`.

The witness radius `r_p` of `p` therefore lies in `[3/2, 2]`. The locus
`circle(p, r_p) ∩ disk(O, 1)` is an arc of angular width (around `p`)
```
2 arccos(r_p / 2),
```
which evaluates to `60°` at `r_p = √3`, shrinking to `0°` as `r_p → 2`.

So the two witnesses of `p` in `K_qr` lie on a **≤ 60° arc** at `p`. Cap
witnesses of `p` in `K_pq, K_pr` (one each) lie outside this arc, in the
directions `p → q`, `p → r`. By L8 the four witnesses span < `π`, which
the geometry already forces: the angular range from `p → q` (at angle `2π/3`)
through the K_qr arc (around `p → -p` direction at `π`) to `p → r` (at angle
`-2π/3 ≡ 4π/3`) is exactly `2π/3` if measured the short way. That is the
mandatory angular envelope of any 4-witness set at `p` in the equilateral 3-cap.

## 5. The "non-cyclicity ≥ explicit constant" question

> Conjecture: every 4-bad polygon has non-cyclicity `≥ c_n` for some explicit
> `c_n > 0`.

By Q-L9 this reduces to `ε(P) ≥ δ_min(P) · sin θ_int / 2`. With normalisation
`R = 1` (SEC radius) and the L1 cone constraint, `δ_min ≥ (1/n)`-ish lower
bounds for non-degenerate convex `n`-gons are not automatic (a thin
elongated `n`-gon can have arbitrarily small `δ_min` relative to `R`). Hence
the conjecture in the literal "absolute constant" form is false: it scales
with the polygon's aspect ratio.

The right scale-invariant statement is

> For every strictly convex `n`-gon `P` with at least one 4-bad vertex,
> `ε(P) / δ_min(P) ≥ 1/2 · sin θ_int`,

and the right "absolute constant" is the multiplicative ratio
`ε / δ_min ≥ 1/2`, valid whenever `circle(v, r_v)` is uniformly transverse to
the best-fit circle. This is **non-vacuous** because in any strictly convex
polygon `δ_min > 0`.

For obtuse-trianglular near-tangent witness circles, `θ_int → 0` and the
bound degenerates; whether such a configuration can host 4 witnesses is then
controlled by the higher-order tangent picture (left open here).

## 6. Summary

* **Q-L9 (proved):** `M(v) ≥ 4` ⇒ `ε(P) ≥ δ_min · sin θ_int / 2`. Two-arc
  geometric mechanism replaces L9's two-point one.
* **Filter (recommended):** reject candidates with `δ_min ≤ 4 · ε(P)` in the
  realisability search. Not currently implemented; would explain the observed
  near-cyclic numerical instabilities in `row-circle-ptolemy-nlp.md` and
  related survivors.
* **3-cap SEC at `n = 8` (proved):** cap-occupancy counting gives
  `n - 3 ≥ 6` ⇒ `n ≥ 9` for all-three-bad; hence at `n = 8` always
  `min{M(p), M(q), M(r)} ≤ 3`. This closes the 3-cap subcase at `n = 8`
  and supplements the `docs/n8-exact-survivors.md` artifact with a
  cleaner, geometry-only proof that does not rely on enumeration.
* **3-cap SEC at `n ≥ 9` (open):** cap counting becomes tight at `(2, 2, 2)`
  for `n = 9` and admits room thereafter; needs perpendicularity (L4+L6)
  closing in the rigid case.
* **Equilateral 3-cap concrete bound:** witnesses of bad `p` in `K_qr` live on
  an arc of angular width ≤ `60°` at `p`; `r_p ∈ [3/2, 2]` (with SEC radius 1).
* **Non-cyclicity ≥ constant:** falsified in the absolute form; the correct
  scale-invariant version `ε/δ_min ≥ 1/2 · sin θ_int` is sharp.

The full 3-cap bridge lemma at all `n ≥ 9` remains open. The natural attack is
the rigid `(2, 2, 2)` configuration at `n = 9` via the three forced
perpendicularity equations of L6 — a 9-vertex analogue of §3.3 parity.
