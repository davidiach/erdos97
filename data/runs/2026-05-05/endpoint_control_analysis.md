# Endpoint Control Auxiliary Claim — Analysis

## 1. Setup recap

Take the standard Lemma 12 setup from canonical-synthesis §5.1.
Let `m := min_i M(i) >= 4`, fix `(i*, r*)` with `|S_{i*}(r*)| = m`, and put
`A = {a_1, …, a_m}` in joint angular/boundary order around `v_{i*}`.
Endpoints of `A`: `j^- = a_1` (= angular start) and `j^+ = a_m`. The polygon
boundary, traversed once, gives the cyclic sequence

```
v_{i*}, L_1, …, L_s, j^-, a_2, …, a_{m-1}, j^+, R_1, …, R_t, v_{i*}
```

so `V \ (A ∪ {i*}) = L ⊔ R` with `|L|+|R| = n-m-1`. Already proved (using
L1, L3, L7): `A` is contained in an open semicircle around `v_{i*}`, the
chord `‖a_1 - a_t‖` is strictly increasing in `t`, and consequently at every
radius `ρ`, `|S_{j^-}(ρ) ∩ (A ∪ {i*})| ≤ 2` (and symmetrically at `j^+`).

The claim under attack: **for at least one of `j ∈ {j^-, j^+}` and every
`ρ > 0`, `|S_j(ρ) \ (A ∪ {i*})| ≤ m-3`.**

## 2. What's at stake — m=4 collapses everything

If the claim is true at `m=4`, then at one endpoint `j` we'd have
`|S_j(ρ) \ (A ∪ {i*})| ≤ 1` for all `ρ`, plus the proved
`|S_j(ρ) ∩ (A ∪ {i*})| ≤ 2`, so `M(j) ≤ 3`. That contradicts
`m = min M(i) ≥ 4`. Hence `m ≤ 3`, i.e. some vertex has `M ≤ 3` —
exactly Erdős #97. So Endpoint Control at `m=4` ⇒ the entire problem.

This sharp leverage is the reason the claim is "hard": it must somehow
encode geometric content that does *not* trivially follow from L1–L8.
It cannot be a one-page combinatorial argument.

## 3. Negation form

Assume the claim fails at both endpoints. Then there exist radii `ρ_-, ρ_+`
and outside vertices

```
u_1, u_2 ∈ L ∪ R    with ‖j^- - u_k‖ = ρ_-  for k=1,2,
w_1, w_2 ∈ L ∪ R    with ‖j^+ - w_k‖ = ρ_+  for k=1,2.
```

(The `m-3` count above for general `m` is just the count needed beyond the
2 inside slots; for `m=4` it is 1.) For convenience in m=4 take exactly two
outside witnesses at each endpoint.

## 4. m=4: where the obstruction lives

### 4.1 Convex-position pinning

Each unordered outside pair `{u_1, u_2}` is equidistant from `j^-`. By L4,
the perpendicular bisector of `{u_1, u_2}` contains at most 2 polygon
vertices. One of them is `j^-`. So this bisector contains at most one other
polygon vertex.

By L6 with `(i, j) = (j^-, ?)`: any vertex `j'` with both `u_1, u_2 ∈ S_{j^-} ∩ S_{j'}`
must satisfy `j^- j' ⊥ u_1 u_2`. So the second vertex on the bisector (if
any) gives a perpendicular‐pairing constraint.

### 4.2 Cyclic positioning of `u_1, u_2`

This is the real combinatorial input. The boundary order forces `u_1, u_2`
to be either both in `L`, both in `R`, or one in each.

**Case (a) both in L.** Then on the boundary traversed `v_{i*} → j^-`, the
vertices `u_1, u_2` lie strictly between `v_{i*}` and `j^-`. Around `j^-`,
by L3 the angular order matches the boundary order. So along the cone
at `j^-`, going from the `v_{i*}` side outward, we first meet `L_1, …, L_s`
in that boundary order, then the rest of the polygon. So `u_1, u_2` are
two non-adjacent positions on one angular arc at `j^-`.

By L7, the chord-length-vs-angular-gap function `2 r sin(θ/2)` is strictly
monotone on `(0, π)` for fixed `r`. But here `u_1, u_2` are NOT necessarily
on a common circle around `j^-` — wait, they *are* by assumption, both at
distance `ρ_-`. So at `j^-` we have a witness 2-set `{u_1, u_2}` ON a
single circle. The angular gap between them equals the angular gap of the
boundary segment between them (matching by L3).

Now apply the same "endpoint chord-length monotonicity" trick used in the
proof of `|S_{j^-} ∩ (A ∪ {i*})| ≤ 2`: among any 3 cocircular points on a
circle around `j^-`, when angular order = boundary order, the chord
lengths from the *angular endpoint* are strictly increasing. So if
`u_1, u_2` are both in `L`, no third vertex of `L` is on `S_{j^-}(ρ_-)`.
That's a *single radius* statement; it doesn't immediately rule out the
two-witness case.

**Case (b) one in L, one in R.** Then `u_1 ∈ L` and `u_2 ∈ R`. Their
perpendicular bisector at `j^-` separates the polygon. Combined with the
inside slot constraints, this is the hardest case.

**Case (c) both in R.** Then `u_1, u_2 ∈ R`. On the boundary, going
`j^+ → R_1 → … → R_t → v_{i*}`, both lie on the *far* chain from `j^-`.

### 4.3 Symmetric situation at `j^+`

Same trichotomy applies to `{w_1, w_2}`. So we have a 3 × 3 case-split.

### 4.4 The route I think works (sketch — not a complete proof)

Among the `3 × 3 = 9` cases, the cleanest sub-case is **(a) at `j^-` and
(c) at `j^+`** — both pairs lie on the *near* chain of the corresponding
endpoint. In that case both `u_1, u_2 ∈ L` and `w_1, w_2 ∈ R`.

Then perpendicular bisector of `{u_1, u_2}` passes through `j^-`, and by
L1 cone containment at `u_1, u_2`, the line `u_1 u_2` lies "below" (toward
`v_{i*}`-side) of the polygon edge `j^- a_2`. Similarly for `{w_1, w_2}`
near `j^+`.

The structural fact one wants is: in this case the outer convex hull
forces a *cap* containing both `{u_1, u_2}` and `{w_1, w_2}`, but the cap
geometry around `j^-` and `j^+` is constrained by L1+L7 (cap lemma /
chord monotonicity). One can then push the argument toward a contradiction
with the diameter / chord-of-`A` `‖j^- - j^+‖` being the longest chord
among `A`-pairs.

I was not able to close this sub-case in the time budget. The remaining
cases (mixed L/R) appear strictly easier because they pin extra
perpendicularity constraints (L6 across `j^-` and `j^+`).

## 5. Asymmetric ("at least one") rather than symmetric

The synthesis (§5.1, Q1) flags the *asymmetry* as suggestive. Geometrically:
the angular semicircle of `A` around `v_{i*}` is closed on one side and
open on the other only up to the mid-bisector of `j^- v_{i*} j^+`. There
is no canonical reason `j^-` and `j^+` should behave identically; chord
lengths from `j^-` to `A` are strictly increasing, chord lengths from
`j^+` to `A` are strictly *decreasing*, and the perpendicular bisector
of `j^- j^+` may or may not pass through `v_{i*}`.

The "at least one" form is therefore consistent with: maybe at the
`v_-`-side, `L` is short and `R` is long, so the budget violation can only
happen at `j^+` (which sees long `R`). In that case the claim holds at
`j^-`. The symmetric-failure case is ruled out by a global combinatorial
constraint — likely a counting / pigeonhole on the *inside* witnesses
of the polygon.

## 6. Specific attack vector that I tried and failed to close

Consider the perpendicular bisectors `B_- := \perp\text{-bisector}(u_1, u_2)`
and `B_+ := \perp\text{-bisector}(w_1, w_2)`. Both are lines, each
containing at most 2 polygon vertices. `B_-` contains `j^-` and at most
one other polygon vertex `x_-`; `B_+` contains `j^+` and at most one other
polygon vertex `x_+`.

If `B_- ≠ B_+`, the two lines meet in at most a point (or are parallel).
By L6, `j^- x_- ⊥ u_1 u_2` and `j^+ x_+ ⊥ w_1 w_2`. The four directions
`(j^- x_-, j^+ x_+, u_1 u_2, w_1 w_2)` give a closed system of orthogonal
constraints, and the question is whether convex position is consistent
with all of them when `m=4`.

This was the attack vector I explored. It does *not* close in the
generality we need: there are too many free parameters, and L8 (semicircle)
constrains only `A` and `v_{i*}`, not `u_1, u_2, w_1, w_2`. To close, one
would need an additional invariant.

## 7. Refutation attempts

I tried to construct a candidate configuration with `m=4` failing at both
endpoints, drawing on the §7.4 hexagon and the §7.6 concave decagon as
seeds. The §7.4 hexagon (diameter endpoint with 4 equidistant witnesses)
has the rest of the polygon NOT 4-bad, so it doesn't violate the hypothesis
`m ≥ 4`. The §7.6 decagon has every vertex 4-equidistant but is *not*
strictly convex, so it isn't a counterexample to #97 either, though it
*is* a counterexample to a weakened (non-convex) version of the claim.

This suggests the claim is essentially equivalent to strict convexity
acting as a global obstruction; locally L1–L8 do not seem sufficient.

## 8. Tractable sub-question

A precise, testable, isolated sub-claim for the m=4 case:

> **Sub-claim (m=4 mixed-side).** If `j^-` has outside witnesses
> `u_1 ∈ L, u_2 ∈ R` at a common distance `ρ_-`, then the perpendicular
> bisector of `u_1 u_2` (which passes through `j^-`) crosses the chord
> `j^- j^+` of `A`. Combined with L8 (semicircle), this forces a
> contradiction with the cone at `v_{i*}`.

If true, sub-claim removes case (b) of §4.2. Cases (a) and (c) remain to
attack. The (a)/(c) symmetric pairing at both endpoints is what the
"at least one" weakening is buying us.

## 9. Status report

- The reduction `Endpoint Control (m=4) ⇒ #97` is clean and
  uncontroversial; this analysis confirms it.
- I cannot prove the auxiliary claim using L1–L10 alone in the time budget.
- I cannot construct a counterexample within strict convex position.
- The natural attack via perpendicular-bisector + L4 + L6 produces a closed
  system of 4 orthogonal direction constraints; this system plausibly
  forces a contradiction with strict convexity, but the closure proof has
  ≥ 5 free real parameters and I did not find a global invariant.
- The "at least one of `j^-, j^+`" formulation is suggestively asymmetric
  with the chord-length monotonicity from `j^-` (increasing) vs `j^+`
  (decreasing). A useful next step would be: pick `i*` and `r*` with an
  additional tie-breaker (e.g., minimize `t = |R|` over all minimum-`m`
  choices) to eliminate the case where the failure site shifts symmetrically
  between endpoints.
- Likely the cleanest closure path is to rephrase the claim as a *boundary-
  chain intersection bound* (§5.1 Q3) and then count witnesses lying on
  each chain via L5 (each pair of circles meets ≤ 2 polygon vertices).

## 10. Concrete next steps a follow-up agent should take

1. **m=4 mixed-side first:** prove sub-claim §8 above. This is the
   "easy" case, and if true it removes case (b) cleanly.
2. **m=4 same-side cases (a) and (c):** combine L4 perpendicular-bisector
   bound with the chord-monotonicity to push two witnesses onto a single
   line through `j^-`; then use convex position (L2) to get a contradiction.
3. **Tie-breaker on `(i*, r*)`:** add the secondary minimization
   `argmin |L| + |R|` (smallest "outside" set), and check whether this
   tie-break makes one endpoint's outside-witnesses count automatically
   bounded.
4. **General m:** the m=4 → #97 leverage is so strong that even a clean
   m=4 proof is sufficient; m=5, m=6 cases are mostly of theoretical
   interest given m=4 closure.

In short: the claim is plausible, the reduction works, but the open
geometric step requires a global invariant that I could not isolate
within the time budget. The most promising route is the perpendicular-
bisector / L4+L6 system combined with a chord-monotonicity refinement at
the endpoints, complemented by a tie-breaker on `(i*, r*)` to break the
endpoint symmetry.
