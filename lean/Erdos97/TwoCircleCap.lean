import Erdos97.SelectedWitness

/-!
# Two-Circle Cap and Pair-Sharing Cap (dependency-free conditional form)

This module states the two foundational counting kernels behind the
selected-witness obstruction, in a deliberately *dependency-free, conditional*
form so that it remains compile-intended under the current mathlib-free
`lakefile.lean`.

The two near-term targets from `docs/formalization.md` addressed here are:

* **Two-circle intersection cap.** If two distinct circles share at least three
  points, contradiction. Geometrically, three distinct concyclic points
  determine the circle, so two genuinely different circles meet in at most two
  points.
* **Pair-sharing cap.** For distinct centers `a, b`, the set of common
  equidistant witnesses has size at most `2`, i.e. `|S_a ∩ S_b| ≤ 2`.

Honesty note (NO Lean proof of #97 is claimed). The genuinely *geometric* input
— that a center together with a common squared distance pins a Euclidean circle
and that two distinct circles meet in `≤ 2` points — is **not** proved here. It
is taken as an explicit hypothesis (`CircleMeetCap` below). Everything proved in
this file is the *combinatorial* consequence of that hypothesis, which is closed
honestly with `exact`/elementary tactics and **no `sorry` and no `axiom`**. The
unconditional Euclidean statement lives, faithfully and `sorry`-marked, in
`lean/Erdos97/Sketches/T20TwoCircleCap.lean`.

The matching abstract geometric input is recorded with the repository's
existing `SameDistanceFrom : Point -> Point -> Point -> Prop` convention, read as
"the second and third points are equidistant from the first".
-/

namespace Erdos97

universe u

section TwoCircleCap

variable {Point : Type u}

/--
The intended reading of `OnCircleRel center r p` is "point `p` lies on the
circle of (squared) radius class `r` about `center`". `r : Radius` is left
abstract: in the Euclidean instance it is the common squared distance, so
`OnCircleRel c r p ↔ dist c p ^ 2 = r`. We keep `OnCircleRel` itself abstract
rather than defining a wrapper, to stay dependency-free.

The abstract two-circle cap hypothesis.

`CircleMeetCap OnCircleRel` says: if a point `p` lies on two circles
`(c₁, r₁)` and `(c₂, r₂)` that are *distinct as circles* (their center/radius
data differ), and likewise for two further points `q, s` all on both circles,
and `p, q, s` are pairwise distinct, then we have a contradiction. In words: two
distinct circles cannot share three distinct points.

This is exactly the geometric fact `docs/formalization.md` lists as target (2),
isolated as a hypothesis so the counting below is honest without mathlib.
-/
def CircleMeetCap {Radius : Type u} (OnCircleRel : Point -> Radius -> Point -> Prop) : Prop :=
  forall (c₁ c₂ : Point) (r₁ r₂ : Radius) (p q s : Point),
    Not (And (c₁ = c₂) (r₁ = r₂)) ->
      Not (p = q) -> Not (p = s) -> Not (q = s) ->
        OnCircleRel c₁ r₁ p -> OnCircleRel c₁ r₁ q -> OnCircleRel c₁ r₁ s ->
          OnCircleRel c₂ r₂ p -> OnCircleRel c₂ r₂ q -> OnCircleRel c₂ r₂ s ->
            False

/--
**Two distinct circles share at most two points** (contrapositive packaging of
`CircleMeetCap`).

Given the cap hypothesis and three pairwise-distinct points all on both of two
circles whose data differ, derive `False`. This is the form most directly
consumed by the pair-sharing argument: any putative third common point forces a
contradiction.
-/
theorem two_distinct_circles_no_three_common
    {Radius : Type u} {OnCircleRel : Point -> Radius -> Point -> Prop}
    (hcap : CircleMeetCap OnCircleRel)
    {c₁ c₂ : Point} {r₁ r₂ : Radius} {p q s : Point}
    (hne : Not (And (c₁ = c₂) (r₁ = r₂)))
    (hpq : Not (p = q)) (hps : Not (p = s)) (hqs : Not (q = s))
    (hp₁ : OnCircleRel c₁ r₁ p) (hq₁ : OnCircleRel c₁ r₁ q)
    (hs₁ : OnCircleRel c₁ r₁ s)
    (hp₂ : OnCircleRel c₂ r₂ p) (hq₂ : OnCircleRel c₂ r₂ q)
    (hs₂ : OnCircleRel c₂ r₂ s) : False :=
  hcap c₁ c₂ r₁ r₂ p q s hne hpq hps hqs hp₁ hq₁ hs₁ hp₂ hq₂ hs₂

end TwoCircleCap

section PairSharingCap

/-!
## Pair-sharing cap `|S_a ∩ S_b| ≤ 2`

We model the witnesses common to two centers as a `List` (dependency-free; the
mathlib instance would use `Finset`). `AtMostTwoDistinct xs` is the honest
"`≤ 2` distinct elements" predicate: there are no three pairwise-distinct
members. The pair-sharing cap then says that the common-witness list of two
distinct centers has at most two distinct elements.
-/

variable {Point : Type u}

/-- `p` is a common witness of centers `a, b` for the abstract circle relation. -/
def CommonWitness {Radius : Type u} (OnCircleRel : Point -> Radius -> Point -> Prop)
    (a b : Point) (rₐ r_b : Radius) (p : Point) : Prop :=
  And (OnCircleRel a rₐ p) (OnCircleRel b r_b p)

/-- A list has at most two distinct elements: no three pairwise-distinct members. -/
def AtMostTwoDistinct (xs : List Point) : Prop :=
  forall p q s : Point,
    p ∈ xs -> q ∈ xs -> s ∈ xs ->
      Not (p = q) -> Not (p = s) -> Not (q = s) -> False

/--
**Pair-sharing cap.**

Let `a, b` be two centers whose `(center, radius)` data differ, let
`OnCircleRel` satisfy the two-circle cap, and let `common` be any list of
points that are all common witnesses of `a` and `b`. Then `common` has at most
two distinct elements. This is the local `|S_a ∩ S_b| ≤ 2` statement (target (3)
of `docs/formalization.md`), proved honestly from the cap hypothesis.
-/
theorem pair_sharing_cap
    {Radius : Type u} {OnCircleRel : Point -> Radius -> Point -> Prop}
    (hcap : CircleMeetCap OnCircleRel)
    {a b : Point} {rₐ r_b : Radius}
    (hne : Not (And (a = b) (rₐ = r_b)))
    {common : List Point}
    (hcommon : forall p : Point, p ∈ common ->
      CommonWitness OnCircleRel a b rₐ r_b p) :
    AtMostTwoDistinct common := by
  intro p q s hp hq hs hpq hps hqs
  have hp' := hcommon p hp
  have hq' := hcommon q hq
  have hs' := hcommon s hs
  exact
    two_distinct_circles_no_three_common hcap hne hpq hps hqs
      hp'.left hq'.left hs'.left hp'.right hq'.right hs'.right

/--
Direct contradiction form: three pairwise-distinct common witnesses of two
distinct circles are impossible. (Unfolds `pair_sharing_cap` at three explicit
members; convenient for incidence counting that produces a third overlap.)
-/
theorem no_three_common_witnesses
    {Radius : Type u} {OnCircleRel : Point -> Radius -> Point -> Prop}
    (hcap : CircleMeetCap OnCircleRel)
    {a b : Point} {rₐ r_b : Radius}
    (hne : Not (And (a = b) (rₐ = r_b)))
    {p q s : Point}
    (hpq : Not (p = q)) (hps : Not (p = s)) (hqs : Not (q = s))
    (hp : CommonWitness OnCircleRel a b rₐ r_b p)
    (hq : CommonWitness OnCircleRel a b rₐ r_b q)
    (hs : CommonWitness OnCircleRel a b rₐ r_b s) : False :=
  two_distinct_circles_no_three_common hcap hne hpq hps hqs
    hp.left hq.left hs.left hp.right hq.right hs.right

end PairSharingCap

end Erdos97
