# A short human-readable proof: no bad convex octagon

Status: proof-note draft; independent review requested. This is the
human-readable companion to the machine-checked artifacts in
`docs/n8-incidence-enumeration.md` and `docs/n8-exact-survivors.md`. It does
not, by itself, settle Erdős Problem #97 (the case `n >= 9` remains open).

A *bad* convex polygon is a strictly convex polygon in which every vertex has
at least four other vertices on a common circle centered at it. Throughout we
use the strong (cocircular) witness definition: for each vertex `v_i`, fix a
witness set `W_i` of four other vertices on a common circle of radius `r_i`
around `v_i`.

The proof uses only L1–L10 from §2 of `docs/canonical-synthesis.md`. The two
lemmas we actually need are:

- **L2** (no three vertices collinear in a strictly convex polygon).
- **L4** (perpendicular-bisector vertex bound: at most two polygon vertices lie
  on the perpendicular bisector of any segment, since strict convexity meets a
  line in at most two points).

Everything else is elementary plane geometry.

The argument is the base-apex / isosceles-triangle count due to the
proof-note draft `docs/n8-geometric-proof.md`, retightened and explicitly
keyed to L1–L10. A second route via forced perpendicularity is sketched at
the end with an honest pointer to where the human argument hands off to a
finite, computer-checked case analysis.

## 1. Base-apex lemma (L4 in coordinates)

**Lemma 1 (base-apex).** Let `A` be the vertex set of a strictly convex
polygon, and let `a, b in A` be distinct. On each open half-plane bounded by
the line `ab`, at most one vertex `p in A \ {a, b}` satisfies `|pa| = |pb|`.

*Proof.* Any such apex lies on the perpendicular bisector `B` of `ab`, and
`B` is a line. Suppose two apices `p, q` lie on the same side of `ab`.
Normalize so `a = (-1, 0)`, `b = (1, 0)`; then `B` is the y-axis. Write
`p = (0, s)`, `q = (0, t)` with `0 < s < t`. Then
```
p = (s/t) · q + ((1 - s/t)/2) · a + ((1 - s/t)/2) · b
```
is a convex combination of `q, a, b` with all coefficients positive. So `p` is
not an extreme point of `conv(A)`, contradicting strict convexity (`p` is a
hull vertex). ∎

**Corollary (apex capacities).**
- If `ab` is a polygon side, all other vertices lie on one side, so `ab`
  supports at most one apex.
- If `ab` is a diagonal, at most one apex on each side: at most two total.

This is exactly L4 made local: a perpendicular bisector meets the strictly
convex polygon in at most two points (one in each half-plane bounded by `ab`).

## 2. The isosceles-triangle count

Let
```
T(A) := #{ (p, {a, b}) : p, a, b in A,  p ∉ {a, b},  a ≠ b,  |pa| = |pb| }.
```
Here `p` is the *apex* and `{a, b}` is the *base*.

**Lower bound (badness).** At each vertex `p`, some distance class has at
least four other vertices. Those four determine `C(4, 2) = 6` unordered base
pairs. So
```
T(A) >= 6n.
```

**Upper bound (Lemma 1).** Sum apex capacities over all base pairs:
```
T(A) <= 1·n + 2·(C(n, 2) - n) = n(n - 2).
```

**Combining the bounds.** A bad convex `n`-gon must satisfy `6n <= n(n-2)`,
i.e. `n >= 8`. So no bad convex polygon exists for `n <= 7`.

(This count is independent of, and shorter than, the selected-witness
incidence count for `n <= 7` recorded in §3 of `docs/canonical-synthesis.md`.)

## 3. The equality case at n = 8

For `n = 8`, both bounds equal 48, so equality holds throughout.

**Equality at each apex** forces, at every vertex `p`, exactly six
equal-distance unordered base pairs. If the seven nonzero distance-class
sizes from `p` are `m_1 + m_2 + ... + m_r = 7`, then
```
sum_k C(m_k, 2) = 6.
```
By badness some `m_k >= 4`. The unique partition of 7 with some part `>= 4`
and sum-of-binomials equal to 6 is `(4, 1, 1, 1)`: a class of size 5 already
gives `C(5,2) = 10 > 6`, and any second part `>= 2` adds `>= 1` past the `6`
contributed by a single 4-class.

**Equality at each base** is also saturated. Since each base-pair capacity
is an individual upper bound (one for sides, two for diagonals), equality of
the sum forces equality term-by-term:
1. Every polygon side is the base of *exactly one* isosceles triangle.
2. Every diagonal is the base of *exactly two* isosceles triangles, with
   apices on opposite sides of the diagonal.

## 4. All sides equal

Index vertices cyclically `v_0, ..., v_7`. Consider the length-2 diagonal
`v_i v_{i+2}` (subscripts mod 8). One of its two sides contains exactly one
polygon vertex, namely `v_{i+1}`. By saturation (item 2 of §3), this short
side carries an apex, which can only be `v_{i+1}`. So
```
|v_i v_{i+1}| = |v_{i+1} v_{i+2}|       for every i.
```
By transitivity around the cycle, all eight side lengths are equal. Call the
common value `s`.

## 5. Length-3 diagonals force a τ-cover

Let `τ_j ∈ (0, π)` be the exterior turn angle at `v_j`. Strict convexity gives
`τ_j > 0`, and Hopf's "umlaufsatz" / total turning gives
```
τ_0 + τ_1 + ... + τ_7 = 2π.       (∗)
```

For an equilateral convex polygon, the standard side-from-turn formula
(isoceles triangle with apex angle `π - τ_j` and legs of length `s`) gives
```
|v_{j-1} v_{j+1}| = 2s · sin( (π - τ_j) / 2 ) = 2s · cos(τ_j / 2).
```
Therefore
```
|v_{j-1} v_{j+1}| = s   ⇔   cos(τ_j / 2) = 1/2   ⇔   τ_j = 2π/3.
```

Now consider the length-3 diagonal `v_i v_{i+3}`. The "short side" of this
diagonal (the side containing the two arc-vertices) holds exactly
`{v_{i+1}, v_{i+2}}`. By saturation, the diagonal must carry an apex on its
short side; that apex is one of `v_{i+1}, v_{i+2}`.

- *Case A: apex `v_{i+1}`.* Then `|v_i v_{i+1}| = |v_{i+1} v_{i+3}|`, so
  `|v_{i+1} v_{i+3}| = s`, forcing `τ_{i+2} = 2π/3`.
- *Case B: apex `v_{i+2}`.* Then `|v_i v_{i+2}| = |v_{i+2} v_{i+3}|`, so
  `|v_i v_{i+2}| = s`, forcing `τ_{i+1} = 2π/3`.

In either case, **at least one of `τ_{i+1}, τ_{i+2}` equals `2π/3`**, for
every `i ∈ {0, ..., 7}`.

Let
```
M := { j ∈ Z/8 : τ_j = 2π/3 }.
```
The condition above says: for every cyclic edge `{i+1, i+2}` of the index
8-cycle, `M` meets it. Equivalently, `M` is a *vertex cover* of the 8-cycle.

## 6. The vertex-cover contradiction

The minimum vertex cover of an `n`-cycle has size `⌈n/2⌉`. For `n = 8`,
`|M| >= 4`.

But then
```
sum_j τ_j  >=  sum_{j ∈ M} τ_j  =  |M| · (2π/3)  >=  4 · (2π/3)  =  8π/3,
```
which is strictly greater than `2π`. This contradicts (∗).

Therefore no bad convex octagon exists. ∎

Combining with §2, no bad convex polygon exists for `n <= 8`. The case
`n >= 9` is not addressed by this argument.

## 7. Honest provenance

Steps 1–6 are entirely hand-verifiable; nothing is hidden behind
"by inspection" or computer check. The proof uses only:

- L2 (no three collinear vertices), invoked implicitly in Lemma 1 to ensure
  the perpendicular bisector contributes only the two algebraically constructed
  apices and no degenerate collinear configurations;
- L4 (perpendicular-bisector vertex bound), which is exactly Lemma 1;
- the standard equilateral-polygon side-from-turn identity
  `|v_{j-1} v_{j+1}| = 2s cos(τ_j / 2)` (immediate from the isoceles
  triangle `v_{j-1} v_j v_{j+1}`);
- total exterior turning `sum τ_j = 2π` for a strictly convex polygon.

No other lemma from L1–L10 is used.

## 8. Relationship to the φ-permutation route

The repository also contains a forced-perpendicularity / radical-axis route
(`docs/n8-incidence-enumeration.md`, `docs/n8-exact-survivors.md`). Its outline:

- **Step 1** (incidence completeness, fully human-verifiable). The incidence
  count saturates: every selected-witness indegree equals 4, adjacent rows
  share exactly one witness, nonadjacent rows share exactly two. (See L4 +
  Jensen, applied as in §3.3 of `docs/canonical-synthesis.md`.)

- **Step 2** (forced perpendicularity, fully human-verifiable). Each
  nonadjacent unordered pair of centers `{i, j}` defines a target chord
  `φ({i, j}) := W_i ∩ W_j` (size 2 by Step 1). By L6 (kite corollary),
  `v_i v_j ⊥ φ({i, j})`. There are `C(8, 2) - 8 = 20` source chords (the
  diagonals of the octagon) and 28 target chord candidates.

- **Step 3** (case analysis, currently *not* human-readable). The valid
  φ-data must respect cyclic order, must avoid odd perpendicularity cycles
  (since `chord ⊥ chord ⊥ ... ⊥ chord` around an odd cycle is impossible),
  and must respect a same-color-parallel constraint that, combined with L2,
  excludes parallel chords sharing an endpoint. After these necessary
  filters, the incidence enumerator finds exactly 15 canonical classes
  (`docs/n8-incidence-enumeration.md`). One class is killed by cyclic-order
  noncrossing; ten by rational linear span; one each by duplicate vertices,
  by collinearity (forbidden by L2), by an exact Gröbner contradiction; and
  one final class by a Gröbner basis whose four real branches each fail
  strict convexity. See `docs/n8-exact-survivors.md` for class-by-class
  certificates and `data/certificates/2026-05-05/n8_groebner_results.json`
  for the independent Gröbner reproduction.

The φ-permutation approach has a clean Step 1 + Step 2 (these are essentially
finite combinatorial consequences of L4, L5, L6), but its Step 3 has *not*
yet collapsed to a small symmetry-quotient case analysis: the 15 incidence
classes are already canonical up to dihedral relabeling. The rational
linear-span kills cluster ten of them but leave four that genuinely depend
on degree-bounded Gröbner / equal-distance algebra rather than pure
linear-span arguments.

So Steps 1–6 of this note (the base-apex / isosceles-count argument) is
currently the only fully hand-verifiable proof of "no bad convex octagon"
in the repository. The φ-permutation route is documented as a structurally
useful machine-checked alternative, not as an independent human proof.

## 9. Length and self-containment

The mathematical content (§1–§6) fits in roughly three printed pages and
is self-contained modulo L2 and L4 of `docs/canonical-synthesis.md`. Steps
hand-verifiable in this note:

| Step | Hand-verifiable? | Computer-checked supporting artifact |
| ---- | ---------------- | ------------------------------------ |
| §1 base-apex lemma | yes | — |
| §2 isosceles count | yes | — |
| §3 partition (4,1,1,1) | yes | — |
| §4 all sides equal | yes | — |
| §5 τ-cover | yes | — |
| §6 vertex-cover contradiction | yes | — |
| §8 φ-permutation, Steps 1–2 | yes | — |
| §8 φ-permutation, Step 3 | **no** (case analysis) | `data/incidence/n8_reconstructed_15_survivors.json`, `data/certificates/2026-05-05/n8_groebner_results.json` |

This note should be promoted beyond `proof-note draft` only after independent
mathematical review of §1–§6.
