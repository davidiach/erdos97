# Proof record: the turn-inequality lemma (2026-07-10)

Status: complete written proof produced and adversarially audited inside an
AI research session (Claude Code multi-agent session, 2026-07-10); recorded
as review input for the lemma note `docs/turn-inequality-lemma.md`, whose
own status line remains "independent review requested" until the maintainer
decides. This note does not promote the `n=9` turn-inequality frontier
artifact, does not change any source-of-truth status, and does not prove
Erdos Problem #97 or claim a counterexample.

Relation to existing artifacts: `docs/turn-inequality-lemma.md` states the
lemma and lists it as the main bottleneck for the review-pending
`n9_turn_inequality_frontier` artifact
(`data/certificates/n9_turn_inequality_frontier.json`,
`scripts/check_n9_turn_inequality_frontier.py`). The proof below resolves
the geometric bottleneck; the upstream frontier enumeration (the
pair/crossing/count filters and brancher coverage producing the 184
assignments) is a separate review scope and is not addressed here.

## Statement

**Lemma (turn inequality).** Let `p_0, ..., p_{n-1}` (`n >= 3`) be a
strictly convex polygon in counterclockwise cyclic order (convex position,
no three vertices collinear), with exterior turn `tau_j in (0, pi)` at
vertex `p_j`. Fix a center `i` and offsets `1 <= a < b <= n-1` (indices mod
`n`) with

```text
|p_{i+a} - p_i| = |p_{i+b} - p_i|.
```

Then both

```text
(F)  tau_{i+1} + tau_{i+2} + ... + tau_{i+b-1} > pi/2
(R)  tau_{i+a+1} + tau_{i+a+2} + ... + tau_{i+n-1} > pi/2.
```

The support of (F) is `{i+1, ..., i+b-1}` (includes `i+a`, excludes `i` and
`i+b`); the support of (R) is `{i+a+1, ..., i+n-1}` (includes `i+b`,
excludes `i` and `i+a`). These are exactly the supports emitted by
`turn_inequality_terms_for_pattern` and audited by
`scripts/check_turn_inequality_indexing.py`.

## Proof

Work with the cross product `u x v = u_1 v_2 - u_2 v_1` and dot product
`u . v`. Use as working definition of strict convexity in CCW order: for
every `j` and every `k` not in `{j, j+1}`,
`(p_{j+1} - p_j) x (p_k - p_j) > 0` (every other vertex strictly to the
left of every directed edge). Write `e_j = p_{j+1} - p_j != 0`.

Step 1 (left turns). `e_{j-1} x e_j > 0` for every `j`: apply the working
definition to edge `(p_{j-1}, p_j)` and vertex `p_{j+1}`, and use
`p_{j+1} - p_{j-1} = e_{j-1} + e_j`.

Step 2 (exterior turn as rotation). Since
`(e_{j-1} . e_j)^2 + (e_{j-1} x e_j)^2 = |e_{j-1}|^2 |e_j|^2` and
`e_{j-1} x e_j > 0`, there is a unique `tau_j in (0, pi)` with
`cos tau_j = (e_{j-1} . e_j) / (|e_{j-1}| |e_j|)` and
`sin tau_j = (e_{j-1} x e_j) / (|e_{j-1}| |e_j|)`; the unit vector of `e_j`
is the unit vector of `e_{j-1}` rotated CCW by `tau_j`.

Step 3 (direction lift along an arc). Fix `i` and set `f_j = e_{(i+j) mod n}`
for `0 <= j <= n-1`. Choose `psi_0` with
`f_0 / |f_0| = (cos psi_0, sin psi_0)` and define
`psi_j = psi_0 + sum_{h=1}^{j} tau_{(i+h) mod n}`. By induction with Step 2,
`f_j / |f_j| = (cos psi_j, sin psi_j)` for all `j`. Hence for
`0 <= j < k <= n-1`:

```text
f_j . f_k = |f_j| |f_k| cos(psi_k - psi_j),
psi_k - psi_j = tau_{i+j+1} + ... + tau_{i+k} > 0,
```

with no branch care needed (cosine is `2 pi`-periodic, applied to the lifted
difference).

Step 4 (cone bound). If `J < K` and
`S = tau_{i+J+1} + ... + tau_{i+K} <= pi/2`, then for all
`J <= j < k <= K` the lifted difference `psi_k - psi_j` is a sub-sum of `S`
with positive terms, so it lies in `(0, pi/2]`, and `f_j . f_k >= 0`.

Step 5 (chords). `p_{(i+m) mod n} - p_i = f_0 + f_1 + ... + f_{m-1}` for
`0 <= m <= n` (telescoping; `p_{(i+n) mod n} = p_i`).

Proof of (F). Let `u = p_{i+a} - p_i = sum_{j=0}^{a-1} f_j` and
`v = p_{i+b} - p_{i+a} = sum_{k=a}^{b-1} f_k` (no wraparound since
`0 < a < b <= n-1`). The hypothesis gives `|u + v| = |u|`, and expanding
`|u+v|^2` yields

```text
u . v = -|v|^2 / 2 < 0
```

(strict: `v != 0` because the witnesses are distinct vertices). If the
forward sum satisfied `tau_{i+1} + ... + tau_{i+b-1} <= pi/2`, Step 4 with
`J = 0, K = b-1` would give `f_j . f_k >= 0` for all `0 <= j < k <= b-1`,
and bilinearity would force

```text
u . v = sum_{j=0}^{a-1} sum_{k=a}^{b-1} f_j . f_k >= 0
```

(each term has `j < a <= k`, both indices in `[0, b-1]`), a contradiction.
Hence (F).

Proof of (R). Let `u' = p_{i+b} - p_{i+a} = sum_{j=a}^{b-1} f_j` and
`v' = p_i - p_{i+b} = sum_{k=b}^{n-1} f_k`. Then `u' + v' = p_i - p_{i+a}`
and the hypothesis gives `|u' + v'| = |v'|`, so `u' . v' = -|u'|^2 / 2 < 0`.
If `tau_{i+a+1} + ... + tau_{i+n-1} <= pi/2`, Step 4 with `J = a, K = n-1`
gives `f_j . f_k >= 0` for all `a <= j < k <= n-1`, forcing
`u' . v' >= 0` - contradiction. Hence (R). QED.

## Corollaries and remarks

- Monotone form (no equidistance hypothesis): for every center `i` and
  `1 <= m <= n-1`, if `tau_{i+1} + ... + tau_{i+m-1} <= pi/2` then
  `|p_i - p_{i+m}| > |p_i - p_{i+m-1}|` (same cone bound applied to
  `|w + f_{m-1}|^2 - |w|^2` with `w = p_{i+m-1} - p_i`). Chaining this
  reproves the lemma and is the samplable engine form.
- Weak normalized layer: with `t_j = 2 tau_j / pi`, strict convexity gives
  `t_j > 0` and `sum t_j = 4` (total exterior turn `2 pi`), and the lemma
  gives the strict forms of the stored inequalities; the stored weak forms
  `>= 1` are relaxations, so the stored certificates refuting the weak
  system a fortiori refute the geometric system.
- Sharpness: in the isosceles configuration `a = 1, b = 2` with apex angle
  at `p_i` tending to `0`, the forward support is the single turn
  `tau_{i+1} = pi/2 + apex/2 -> pi/2` from above. So `pi/2` cannot be
  improved and the weak `>= 1` layer is the tightest uniform closed
  relaxation. (The `a = 1, b = 2` case is the classical fact that base
  angles of an isosceles triangle are acute; the lemma is its convex-arc
  generalization.)
- Boundary case "sum exactly `pi/2`" is excluded, not just unreachable: the
  cone bound yields the weak `u . v >= 0` while equidistance yields the
  strict `u . v < 0`.
- k=3 sanity check: the lemma is universally true for every strictly convex
  polygon (including Danzer's 9-gon with three equidistant witnesses per
  vertex); only the infeasibility of the assembled n=9 four-witness weak
  systems is specific to `k = 4`. No contradiction with known k=3
  constructions.

## Verification performed in this session (2026-07-10)

- Exact-arithmetic sampling (fractions end to end; the only analytic step,
  deciding "consecutive turn sum > pi/2", done by an exact sign-pattern
  region test cross-validated on 20,000 windows against 50-digit numerics
  with zero disagreements): 273,698 direct instances of the lemma on 6,000
  strictly convex rational polygons (`n = 5..12`, three seeds, generators:
  rational circle points, parabola points, integer-grid hulls, lens
  profiles; 136,849 exactly-equidistant pairs, both (F) and (R) per pair),
  zero violations; 219,982 instances of the monotone engine form, zero
  violations; 15 known-answer boundary tests including exact `pi/2` windows,
  all passing.
- Repo replays on the unmodified tree:
  `python scripts/check_turn_inequality_indexing.py --check --assert-expected`
  passed (70 subsets, 630 rows, 7,560 terms, 0 mismatches);
  `python scripts/check_n9_turn_inequality_frontier.py --check --assert-expected`
  passed (184 assignments, 108 inequalities each, z3 unsat 184/184,
  stored-certificate replay agreeing with the artifact digests).
- Independent certificate re-verification (not importing the repo emitter):
  all 108 supports per assignment re-derived from the lemma statement and
  matched the stored order exactly; all 184 stored integer dual certificates
  re-checked in pure integer arithmetic (each uses `4L + 1` weak
  inequalities with every variable used at most `L` times, `L in {1, 2}`,
  giving `4L + 1 <= 4L` on summation - a contradiction); 0 mismatches,
  0 invalid certificates.

## Scope

With this lemma proved, the stored integer dual certificates validly
exclude all 184 frontier assignments for strictly convex nonagons - i.e.
the turn route's geometric hinge holds - conditional on the separate,
still-review-pending upstream question of frontier completeness
(pair/crossing/count filter soundness and brancher coverage). Nothing here
proves `n=9` on its own, promotes any artifact, changes the official/global
falsifiable/open status, or proves Erdos Problem #97.
