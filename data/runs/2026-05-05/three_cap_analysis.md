# Three-Cap Bridge Lemma — Analysis (Erdős #97, §5.4)

## Executive summary

The Three-Cap Bridge Lemma cannot be derived from the **cap lemma** as stated in
`canonical-synthesis.md` §5.4 because that statement of the cap lemma is *false*
without an inscribed-polygon hypothesis. A concrete counterexample (the §7.4
hexagon, already in the repository) shows that even the diameter case's claim
`E(p) ≤ 2` is far from automatic. I give a counterexample to the literal
"distinct distances" form of the cap lemma, identify the correct (Moser) form,
isolate the actual gap in §5.4, and analyze the three-cap setup carefully.

## 1. Exact statement of the cap lemma

`canonical-synthesis.md` §5.4 cites the cap lemma as:

> *distances from a chord endpoint to convex-position points inside the cap are
> all distinct.*

**This statement is false in general.** Take

  a = (0,0), b = (3,0), x = (1,1), y = (-1,1).

The 4-gon `(a, b, x, y)` is strictly convex (every internal cross-product is
positive), the chord `ab` cuts off an upper cap whose interior contains both
`x` and `y`, and `||a - x|| = ||a - y|| = √2`. So two convex-position interior
cap points are equidistant from chord endpoint `a`. The cited cap lemma fails.

What Moser actually proved (Moser, 1952; cf. Brass–Moser–Pach,
*Research Problems in Discrete Geometry*, problem 5.5; cf. Dumitrescu's survey
on unit distances) requires the polygon to be **inscribed in a circle**:

> **Cap lemma (correct form).** Let `P` be a convex polygon inscribed in a
> circle `C`. For any chord `pq` cutting `C` into two arcs, walking along
> either arc from `p` to `q` strictly increases the distance to `p`; in
> particular distances from `p` to the cap points are pairwise distinct.

The proof is one line: a vertex `x` on the arc has `||p - x|| = 2R sin(θ/2)`
where `θ` is the central angle between `p` and `x`, monotonic in `θ`.

A weaker incidence form (Moser-style, the version actually used in convex
unit-distance bounds) is:

> **Cap incidence bound.** For a convex polygon `V` and a chord `pq` of length
> 1, on either cap of `pq` at most 2 vertices are at distance 1 from `p`.

This is the version that drives the `O(n)` unit-distance bound for convex
polygons; it does **not** give "distinct distances," only "≤ 2 hits at any one
distance."

## 2. What the cap lemma actually implies in §5.4

Applying the inscribed-arc form to the diameter case, **only if** the polygon
`V` is inscribed in its SEC (a strong assumption — only `n = 2` of `V`'s
vertices need touch SEC), one obtains `E(p) ≤ 2` per cap × 2 caps ⇒
`E(p) ≤ 2`.

If only `p` and `q` lie on SEC and the rest of `V` is strictly inside, the
inscribed cap lemma does **not** apply, and the diameter-case argument has a
gap. Nonetheless, computational experiments (placing 4 candidate witnesses on
a circle around `p` inside the closed pq-disc) consistently fail to produce a
strictly convex configuration: for any 3 witnesses on a sub-180° arc around
`p`, the middle witness is dominated and falls inside the convex hull of the
two extremes plus `p` and `q`. The hexagon §7.4 actually achieves `E(A) = 4`
*precisely because the SEC is not the diameter case but the three-cap case*,
which side-steps the SEC-disc-domination obstruction.

So the literature-style cap incidence bound (`≤ 2` cap hits at any unit
distance) is consistent with `E(p) ≤ 2` in the diameter case, but the proof
sketched in §5.4 is incomplete.

## 3. The §7.4 hexagon disproves the §5.4 reduction in the three-cap case

The §7.4 hexagon

  A = (0,0), D = (0.7286615964, 0.2295545885),
  P_k = (cos k°, sin k°) for k ∈ {20, 40, 60, 80}

with cyclic order `A, D, P_20, P_40, P_60, P_80` is strictly convex and has

- SEC center (0.371114, 0.442276), radius `1/√3`,
- SEC supported by the **non-obtuse triangle** `(A, P_20, P_80)` (in fact
  equilateral with side 1, so all three angles `60°`),
- `E(A) = 4` with witnesses `{P_20, P_40, P_60, P_80}`, all at distance 1.

Cap decomposition (cyclic order):

- `K_{A, P_20}` interior: `{D}`,
- `K_{P_20, P_80}` interior: `{P_40, P_60}`,
- `K_{P_80, A}` interior: `∅`.

`A`'s 4 witnesses are: `P_20` (SEC vertex, cap-endpoint), `P_40` (in
`K_{P_20, P_80}`), `P_60` (in `K_{P_20, P_80}`), `P_80` (SEC vertex,
cap-endpoint).

This is a real, fully-checked instance of the three-cap setup with a bad
vertex `p = A`. The **Three-Cap Bridge Lemma** asks for two of `A`'s
witnesses to lie in a single cap with a diagonal joining them. In §7.4 this
is satisfied with `{P_40, P_60} ⊂ K_{P_20, P_80}` and chord `P_40 P_60`
inside that cap. So §7.4 is *consistent with* the Three-Cap Bridge Lemma but
proves nothing about it.

## 4. Where the framework's "≥ 2 in K_{qr}" count comes from, and why it is fragile

§5.4 reasons:

> Cap lemma controls distances from `p` to `K_{pq}` and `K_{rp}` (each ≤ 1
> contribution to any equal-distance set at `p`), but not `K_{qr}`. So if `p`
> is bad, ≥ 2 of its 4 witnesses lie in `K_{qr}`.

There are *three* distinct issues:

1. **The cap lemma is being used in its strong "distinct distances" form,
   which is FALSE for non-inscribed convex polygons.** Even when `p, q` are
   SEC support vertices, the polygon need not be inscribed in SEC; we have
   shown an explicit convex counterexample to the strong form.

2. **Endpoints vs interior.** SEC support vertices `q, r` are themselves
   potential witnesses of `p`. In the §7.4 hexagon, *both* `P_20` and `P_80`
   are at the witness distance 1 from `A`. This means 2 of `A`'s 4 witnesses
   are SEC support vertices, leaving only 2 for the cap interiors. The
   framework's counting "1 in `K_{pq}` + 1 in `K_{rp}` + ≥ 2 in `K_{qr}`"
   actually allocates witness count among open caps only and ignores the
   contribution from `q, r` themselves. Including this:
   `E(p) ≤ #{interior K_{pq}} + #{interior K_{qr}} + #{interior K_{rp}}
              + 1_{q is witness} + 1_{r is witness}`.

3. **The bound `≤ 1 per cap K_{pq}, K_{rp}`** is even weaker than claimed:
   even with the correct cap lemma (inscribed form), the polygon would have
   to be inscribed in SEC. With only 3 SEC support vertices, the cap-interior
   points are not on SEC, so the inscribed cap lemma does not apply
   directly.

   What survives: For chord `pq` of polygon `V`, the cap `K_{pq}` is a convex
   region. Cap-interior vertices on `K_{pq}` form a strictly convex chain
   from `p` to `q`. **No** general theorem says distances from `p` to this
   chain are pairwise distinct.

## 5. Can the Three-Cap Bridge Lemma be proved? Identifying the precise gap

**Pigeonhole argument (best one can do).** Suppose `p` has witnesses
`w_1, w_2, w_3, w_4` at common distance `r`. Distribute among the closed
caps; by `q, r` being cap endpoints, this distributes among
`K_{pq}, K_{qr}, K_{rp}` (closed). If two witnesses share a closed cap,
either:

- both interior to a single open cap ⇒ Three-Cap Bridge Lemma holds
  (probably with diagonal);
- one interior, one is an endpoint ⇒ "diagonal inside cap" requires the
  interior witness not to lie on the chord defining the cap;
- both endpoints ⇒ they are some `{q, r}`-pair, and the chord `qr` is the
  cap-defining chord, not a diagonal inside.

The last case is the obstruction: `{q, r}` *both* witnesses of `p`, paired
across the cap `K_{qr}` they define. The "chord `qr`" isn't a diagonal inside
`K_{qr}`; it is `K_{qr}`'s boundary. Whether this counts depends on the
intended formulation of the Three-Cap Bridge Lemma.

**Maximum spread with no cap repetition.** The "worst case" we must rule out
for the strict bridge lemma:

- 1 witness interior to `K_{pq}`,
- 1 witness interior to `K_{rp}`,
- 0 witnesses interior to `K_{qr}`,
- both `q` and `r` are witnesses (= cap-endpoint witnesses).

Total = 4, achievable in principle. **In §7.4** this is *not* the
configuration: there it's 0 interior to `K_{pq}`, 0 interior to `K_{rp}`,
2 interior to `K_{qr}`, both `q = P_20` and `r = P_80` witnesses (so 4 total
with 2 in `K_{qr}` interior plus 2 SEC vertices). So §7.4 does not exhibit
the worst case.

**A diagonal inside `K_{qr}` already exists in §7.4.** `P_40` and `P_60` are
in `K_{P_20, P_80}` interior, both at distance 1 from `A`, joined by chord
`P_40 P_60` (a diagonal inside `K_{P_20, P_80}`). So the strong Three-Cap
Bridge Lemma *holds* in this hexagon.

**Can the worst case (no two witnesses share an interior cap) be ruled
out?** This is the precise gap. It would require showing:

> *Lemma (claim, unproved):* If `p, q, r` form a non-obtuse triangle
> determining SEC of strictly convex polygon `V`, and `p` has 4 vertices
> equidistant from `p` in `V \ {p}`, then at least one pair of these 4 lies
> simultaneously in some open cap `K_{pq}, K_{qr}, K_{rp}` (not in cap
> closures only via shared endpoint).

The simplest known constraints are:

- (a) `q` and `r` can both be witnesses **only if `|pq| = |pr|`**, i.e.,
  triangle `pqr` is isoceles at `p` (so the SEC is supported by an isoceles
  triangle with apex `p`).
- (b) The interior cap `K_{pq}` contains at most 1 witness, **only if** the
  cap-interior distances from `p` to `K_{pq}` interior are pairwise distinct
  (which is the cap-lemma fact, valid only if these cap-interior points are
  on SEC, i.e., on the same circular arc inscribed). For the three-cap case,
  cap-interior points are interior to SEC (not on it), so the cap lemma
  does not give this; one needs a separate argument.

So the bridge lemma is contingent on: **either** the cap-lemma extends to
non-inscribed cap interiors, **or** the isoceles-pqr restriction itself
forces a witness collision. Neither has been proved in the repository.

## 6. The "exactly 2 in `K_{qr}`, 1 each in `K_{pq}, K_{rp}`" configuration

Per the user's question: can this exist? **Yes**, modulo the gap. The
configuration is:

- `K_{pq}` interior: 1 witness `x_1` of `p`,
- `K_{rp}` interior: 1 witness `x_2` of `p`,
- `K_{qr}` interior: 2 witnesses `x_3, x_4` of `p`,
- `q, r` not witnesses.

Total = 4. In this configuration the bridge-lemma conclusion **does hold**,
because `{x_3, x_4}` lie in the same open cap `K_{qr}` and `x_3 x_4` is a
diagonal inside `K_{qr}`. So this configuration is *not* a counterexample
to the bridge lemma; it satisfies it.

The truly worrying configurations are:
- (A) "1 in `K_{pq}` interior + 1 in `K_{rp}` interior + `q` witness + `r`
  witness": **no** two witnesses share an open cap. The pair `{q, r}` lies
  on chord `qr` which is the cap-bounding chord, not a diagonal inside
  `K_{qr}`.
- (B) "1 each in three open caps + 1 of `{q, r}` witness": one open cap has
  1 witness; we need a pair, and the pair `{cap-witness, cap-endpoint}` may
  fail the "diagonal inside cap" test.

Configurations (A), (B) need to be ruled out by *additional* convex-position
or cap-geometry constraints, none of which the cap lemma alone provides.

## 7. Verdict

- The cap lemma as stated in §5.4 is the inscribed-polygon version; the
  framework applies it without the inscribing hypothesis, and there is an
  explicit 4-gon counterexample to the literal statement.
- The diameter case proof of `E(p) ≤ 2` is therefore not rigorous as
  written, but extensive experimentation suggests `E(p) ≤ 2` in the diameter
  case still holds; a correct proof would proceed via SEC-disc dominance
  (the `pq`-diameter forces witnesses on a circle around `p` inside the disc
  to lose convex position once 3 of them lie in the same half-plane).
- The §7.4 hexagon shows the three-cap case admits `E(p) = 4`, so the
  three-cap case is genuinely open.
- The strong "Three-Cap Bridge Lemma" (no cap repetition possible) cannot
  be derived from the cap lemma alone — even the correct cap-lemma form does
  not rule out the SEC-vertex-as-witness configurations (A), (B) above.
- The §7.4 hexagon happens to satisfy the bridge lemma (witnesses
  `P_40, P_60` are in `K_{P_20, P_80}` with `P_40 P_60` a diagonal), but
  this is a *fortunate* configuration and does not force the lemma.

**No closure of the three-cap case is achieved here.** The precise gap is:
proving that interior-cap distances from `p` are pairwise distinct in
the three-cap (non-inscribed) setup, **or** proving that the "SEC vertices
as witnesses" configurations (A) and (B) cannot simultaneously occur with 4
witnesses for `p`.
