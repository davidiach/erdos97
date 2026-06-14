# A7 — Inversion / Mobius reformulation (beyond the shallow inversive pilot)

Trust label: `EXPLORATION_EXACT_DIAGNOSTIC` / `SHARP_NO_GO`.

Scope guardrail: this note does NOT prove Erdos Problem #97, does NOT claim a
counterexample, and does NOT certify Euclidean realizability of any point-line
system. All geometric equalities below are computed in exact rational arithmetic
(`fractions.Fraction`); none are floating-point near-equalities. The official /
global status of #97 remains open. The deliverable is a **sharp reasoned no-go**
for the inversion/Mobius route, together with the exact structural facts that
explain *why* it does not compress the problem, plus a small reusable exact
filter ingredient (the Inversion-Foot Lemma) that did not produce a new frontier
obstruction.

Reproduction:

```bash
python scripts/exploration/a7_inversion_mobius.py
ruff check scripts/exploration/a7_inversion_mobius.py
```

Input (treated as data, not truth):
`data/certificates/n9_vertex_circle_frontier_motif_classification.json`
(the 184 regenerated n=9 pre-vertex-circle frontier assignments).

---

## 0. Setup and the exact object

For center `v` the #97 event is: four OTHER vertices lie on a circle
`C(v, r_v)` **centered at `v`**, i.e. `|v - w_j|^2` are all equal over
`w_j in S_v`. A circle centered at `v` does NOT pass through `v`. Therefore the
naive "invert at `v` to linearize `v`'s own witness circle" is FALSE — already
recorded in `docs/research-directions-2026-05-19.md` §9 and respected here.

The only correct linearization is inversion at a **witness** `b`: every circle
`C_i` whose selected set contains `b` passes through `b`, so inverting at `b`
maps `C_i` to a LINE through the three image points `inv(S_i \ {b})`. The
shallow pilot (`docs/inversive-incidence-pilot.md`) kept only this incidence
consequence and found no line-compression on the 184 frontier. This note goes
deeper: it (a) derives the full exact image (Inversion-Foot Lemma), (b) tests
whether that extra data is a new frontier filter, and (c) pins down the exact
geometric reasons inversion cannot compress the problem.

---

## 1. Single-inversion incompatibility (exact, finite)

A single inversion centered at a point `q` linearizes `C_i` iff `q in C_i`, i.e.
`q` is a witness of center `i`. For ONE inversion to linearize ALL `n` centered
circles simultaneously, `q` would have to lie on all `n` distinct centered
circles at once. Two distinct circles meet in `<= 2` points and three circles in
general position share none, so this is impossible for `n >= 3` unless the
circles are coaxial — which centered-at-distinct-vertices circles are not.

Frontier confirmation (Section 1 of the script): across all 184 assignments
every vertex is a witness of **exactly 4** centers (indegree 4). So the best a
single vertex-centered inversion can do is linearize `4 < 9` of the rows. There
is no global single-inversion linearization. This is the precise finite reason
"inversion as global linearization" fails.

`max_indegree_over_all_assignments = 4`, `needed = 9`,
`global_single_inversion_possible = false`.

---

## 2. Inversion-Foot Lemma (the exact data the pilot dropped) — EXACT

Invert circle `C(O, r)` through `b` at `b` with any power `k != 0`. Let
`inv(O)` be the image of the center. Then (verified exactly, Sections 2 & 2b):

- the three image witnesses are collinear on a line `L` (circle-through-center
  maps to a line);
- **`L` is the perpendicular bisector of the segment `[b, inv(O)]`**:
  `foot_L(b) = midpoint(b, inv(O))`, and `inv(O)` is the mirror image of `b`
  across `L`;
- `L perp (b -> inv(O))`, and `inv(O)` lies OFF `L`.

So the whole image line is **determined by the single point `inv(O)`** (the
image of the center). The pilot kept "3 points collinear" but discarded the fact
that the line is a perpendicular bisector anchored at the image-of-center. This
is the genuinely new exact ingredient.

Verified flags: `three_images_collinear=true`,
`foot_equals_midpoint_b_invO=true`,
`invO_is_reflection_of_b_across_L=true`, `L_is_perp_bisector_of_b_invO=true`.

---

## 3. Why the extra data is NOT a new filter — EXACT equivalence

The pilot already shows forced lines at a pivot never merge: two distinct
circles cannot share two points besides `b`, so the image-point sets never share
a pair (`two_circles_share_two_pts_besides_b = 0`, `line_merges_found = 0`).

The deeper test (Section 4): at witness `b` the 4 centers through `b` give 4
perp-bisector lines `L_j`. There are **8820** incidences across the frontier
where a center `O_j` (through `b`) is also a witness of another center `O_m`
(through `b`); every one of the 1656 pivots has such incidences. Each forces
`inv(O_j)` onto `L_m = perp-bisector([b, inv(O_m)])`, i.e.

```text
|inv(O_j) - b| = |inv(O_j) - inv(O_m)|.
```

Crucially, this inverted metric equation is **logically equivalent** to the
original Euclidean radius equation `|O_m - O_j| = |O_m - b| = r_{O_m}` (verified
exactly on a concrete rational configuration in the script's analysis). Because
inversion at `b` is a bijection of the plane minus `b`, "concyclic through `b`"
and "image collinear" are equivalent statements of the SAME fact. Inversion
**re-expresses** the constraint system; it neither adds nor removes information.

Degrees-of-freedom accounting (script tail): inversion at one witness `b` loses
`b` (to infinity) and keeps 8 image points (16 unknowns). Only the 4 circles
through `b` linearize; the other 5 centered-circle conditions remain quadratic
(a circle not through the inversion center maps to a circle, still with a hidden
center). Convexity is destroyed (Section 4 below). No reduction in the number of
unknowns or in the essential equation degree. **No compression.**

---

## 4. The decisive reason: convexity has no clean image — EXACT certificate

Any #97 impossibility proof MUST use strict convexity (the P24 metric-linear
non-convex control, `docs/failed-ideas.md` §16, satisfies every selected
equal-distance row yet is non-convex). Inversion does not preserve convexity:

Section 5 gives an EXACT rational certificate. The strictly convex octagon

```text
(0,0),(100,0),(101,1),(101,50),(100,51),(0,51),(-1,50),(-1,1)
```

(all 8 turn-determinants positive) inverted at vertex `(0,0)` (which goes to
infinity and is dropped) has remaining 7 image points whose turn-determinant
signs are

```text
[-1, -1, 1, 1, 0, 1, 0],
```

i.e. mixed signs with collinear triples — **not strictly convex**. Geometric
reason: inversion sends the polygon's straight EDGES to circular ARCS, so the
image bounded by straight chords need not be convex. Convexity, the one
ingredient any proof must use, therefore has no trackable image under inversion.

Complementary obstruction (Section 6, cross-ratio): the only genuinely
Mobius-invariant handle on four points is the cross-ratio, which is real iff the
four points are concyclic-or-collinear. But the #97 condition is strictly
stronger than concyclicity: it requires the circle to be **centered at the
vertex `v`**. The cross-ratio is **blind to the center** — two quadruples on
circles with different centers can share the same cross-ratio (verified: two
unit-circle quadruples centered at `0` and at `5` both have cross-ratio `2`).
The center re-enters only as a non-invariant affine/metric datum that Mobius
maps scramble. So no cross-ratio (Mobius-invariant) constraint can encode the
"centered at `v`" requirement — exactly the part of the problem that matters.

---

## 5. Verdict

The inversion/Mobius route does NOT compress Erdos #97, and the reasons are now
exact and specific:

1. No single inversion linearizes all centers (indegree 4 < 9; circles not
   coaxial). Per-center inversions are mutually incompatible (each needs a
   different center, and inversion at `p_i` does not even linearize `p_i`'s own
   circle).
2. Inversion at a witness `b` linearizes only the 4 circles through `b`; the
   resulting linear equations are Mobius-equivalent restatements of the original
   radius equations (Section 3) — no information gain, hence the pilot's "no
   compression" is structural, not incidental.
3. The two features a proof must exploit are exactly the two features inversion
   destroys or cannot see: **strict convexity** (turns to non-convex arcs;
   exact certificate, Section 4) and **the center of each witness circle**
   (cross-ratio is center-blind, Section 6).

The one positive byproduct — the **Inversion-Foot Lemma** (image line = perp
bisector of `[b, inv(center)]`) — is exact and reusable, but on the 184 frontier
it adds no obstruction beyond the existing vertex-circle/Kalmanson machinery
because its content is metric-equivalent to the original radius equations.

---

## 6. What was NOT established

- No proof or disproof of #97; no counterexample; no realizability certificate.
- The Inversion-Foot Lemma was not pushed into a global incidence bound; whether
  the perp-bisector net of all `n` witness-inversions has a non-obvious
  *projective* invariant (beyond the metric-equivalent content shown here) was
  not ruled in or out — but Section 6's center-blindness argument makes a
  purely Mobius-invariant obstruction implausible.
- No use of `z3`/Groebner realizability on the inverted systems; the argument
  is that such work would be solving the SAME system in different coordinates.
- The convexity-breaking certificate is an existence proof that inversion can
  destroy convexity; it does not characterize WHICH inversions preserve it (an
  inversion centered far outside a nearly-round polygon can preserve convexity,
  as the script's round-pentagon cases show — but no inversion can be chosen
  uniformly across the `n` per-center conditions, by Section 1).

---

## Artifacts

- Code: `scripts/exploration/a7_inversion_mobius.py` (exact, ruff-clean).
- Input: `data/certificates/n9_vertex_circle_frontier_motif_classification.json`.
- Prior shallow pilot (superseded by this deeper analysis):
  `docs/inversive-incidence-pilot.md`,
  `data/certificates/n9_inversive_incidence_pilot.json`.
