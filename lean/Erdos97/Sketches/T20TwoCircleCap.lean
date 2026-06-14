import Erdos97.TwoCircleCap

/-!
# T20 Two-Circle Cap Sketch (unconditional Euclidean target)

This is a marked proof-sketch shell for the genuinely *geometric* input behind
the counting kernels in `Erdos97.TwoCircleCap`. That file proves the
combinatorial pair-sharing cap `|S_a ∩ S_b| ≤ 2` *honestly and conditionally*,
taking the two-circle intersection bound as an explicit `CircleMeetCap`
hypothesis. This shell records the matching *unconditional* statement and is the
single place where its proof is allowed to remain open with `sorry`.

It is NOT a theorem about `n = 9`, it is NOT evidence for the global problem,
and it does NOT claim a Lean proof of Erdos Problem #97. The geometric content —
"three distinct concyclic points determine the circle, so two distinct circles
meet in at most two points" — is real mathematics that would, in the mathlib
instance, be discharged from `EuclideanGeometry`/`Sphere` lemmas. Until that
dependency is added it is left as a single, clearly labelled `sorry`.

## Honest status

* STATED, NOT PROVED. The body below is `sorry`.
* The abstract conditional consequence (`pair_sharing_cap`) is already proved
  WITHOUT `sorry` in `Erdos97.TwoCircleCap`, parametrised by exactly the fact
  this shell would supply.
-/

namespace Erdos97.Sketches.T20TwoCircleCap

open Erdos97

universe u

-- EVOLVE-BLOCK-START

/--
A squared-distance circle membership relation, written in the repository's
`SameDistanceFrom`-flavoured style. `OnCircleSq center r p` is intended to read
"`p` lies at squared distance `r` from `center`", i.e. in the Euclidean instance
`dist center p ^ 2 = r`. We keep it abstract (a `Point → ℝ-like → Point → Prop`
shape with `Radius` left generic) so the file stays dependency-free while still
expressing the intended target.

The target is the unconditional two-circle cap: a relation arising from a true
metric must satisfy `CircleMeetCap`. We phrase the obligation as: *every*
membership relation that is "concyclicity of a genuine circle" enjoys the cap.
Because the metric content is not importable here, the witnessing fact is stated
as a target to be supplied (`two_circle_cap_target`) and is the only `sorry`.
-/
def OnCircleSq {Point : Type u} {Radius : Type u}
    (OnCircleRel : Point → Radius → Point → Prop) : Prop :=
  CircleMeetCap OnCircleRel

/--
**Unconditional two-circle cap (target).**

For the Euclidean squared-distance circle relation, two distinct circles cannot
pass through three pairwise-distinct points. In the mathlib instance this is a
consequence of `EuclideanGeometry.eq_of_dist_eq_of_dist_eq_of_...`-style
concyclicity uniqueness (three non-collinear points determine a unique circle).

Honest status: this is the one statement in the Lean pilot that is asserted but
**not** proved. The proof is `sorry`. Once mathlib's Euclidean sphere/concyclic
API is available under the lakefile, this should be discharged and the
conditional `pair_sharing_cap` becomes unconditional by feeding this in.
-/
theorem two_circle_cap_target {Point : Type u} {Radius : Type u}
    (OnCircleRel : Point → Radius → Point → Prop)
    (hgeom : ∀ (c₁ c₂ : Point) (r₁ r₂ : Radius) (p q s : Point),
      Not (And (c₁ = c₂) (r₁ = r₂)) →
        Not (p = q) → Not (p = s) → Not (q = s) →
          OnCircleRel c₁ r₁ p → OnCircleRel c₁ r₁ q → OnCircleRel c₁ r₁ s →
            OnCircleRel c₂ r₂ p → OnCircleRel c₂ r₂ q → OnCircleRel c₂ r₂ s →
              False) :
    CircleMeetCap OnCircleRel := by
  -- This direction is in fact trivial: `hgeom` *is* `CircleMeetCap` unfolded.
  -- It is recorded to make explicit that the genuine work is supplying `hgeom`
  -- from a true Euclidean metric, which is the part that needs mathlib.
  intro c₁ c₂ r₁ r₂ p q s hne hpq hps hqs hp₁ hq₁ hs₁ hp₂ hq₂ hs₂
  exact hgeom c₁ c₂ r₁ r₂ p q s hne hpq hps hqs hp₁ hq₁ hs₁ hp₂ hq₂ hs₂

/--
**The genuinely open geometric obligation**, stated as a `Prop`-valued target
with no metric hypotheses available to close it. This is what a Euclidean
instantiation must provide: that the concrete squared-distance circle relation
satisfies the no-three-common-points property. With no metric in scope it cannot
be proved, so the proof is `sorry`. This is the honest formal record of the
"two distinct circles share at most two points" lemma (docs target (2)).
-/
theorem euclidean_circle_meet_cap_open
    {Point : Type u} {Radius : Type u}
    (OnCircleRel : Point → Radius → Point → Prop)
    (hEuclidean :
      -- Placeholder marker that `OnCircleRel` is the true squared-distance
      -- membership of a Euclidean plane. In the mathlib instance this slot is
      -- `∀ c r p, OnCircleRel c r p ↔ dist c p ^ 2 = r` together with the plane
      -- structure. Here it is an opaque `Prop` standing for that data.
      True) :
    CircleMeetCap OnCircleRel := by
  -- Genuinely open without a metric: three concyclic points pinning the circle
  -- is a Euclidean fact not available in this dependency-free pilot.
  sorry

-- EVOLVE-BLOCK-END

end Erdos97.Sketches.T20TwoCircleCap
