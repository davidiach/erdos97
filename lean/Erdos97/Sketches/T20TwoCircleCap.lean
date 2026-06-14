import Erdos97.TwoCircleCap

/-!
# T20 Two-Circle Cap Sketch (unconditional Euclidean target)

This is a marked proof-sketch shell for the genuinely *geometric* input behind
the counting kernels in `Erdos97.TwoCircleCap`. That file proves the
combinatorial pair-sharing cap `|S_a ∩ S_b| ≤ 2` *honestly and conditionally*,
taking the two-circle intersection bound as an explicit `CircleMeetCap`
hypothesis. This shell records the matching *unconditional* statement and is the
single place where its proof is allowed to remain open.

It is NOT a theorem about `n = 9`, it is NOT evidence for the global problem,
and it does NOT claim a Lean proof of Erdos Problem #97. The geometric content —
"three distinct concyclic points determine the circle, so two distinct circles
meet in at most two points" — is real mathematics that would, in the mathlib
instance, be discharged from `EuclideanGeometry`/`Sphere` lemmas. Until that
dependency is added it is left as a single, clearly labelled open step inside
the evolve block below.

## Honest status

* STATED, NOT PROVED. The unconditional body below is an open step.
* The abstract conditional consequence (`pair_sharing_cap`) is already proved
  WITHOUT an open step in `Erdos97.TwoCircleCap`, parametrised by exactly the
  fact this shell would supply.
-/

namespace Erdos97.Sketches.T20TwoCircleCap

open Erdos97

universe u

-- EVOLVE-BLOCK-START

/--
A squared-distance circle membership relation, written in the repository's
`SameDistanceFrom`-flavoured style. `OnCircleSq center r p` is intended to read
"`p` lies at squared distance `r` from `center`", i.e. in the Euclidean instance
`dist center p ^ 2 = r`. We keep it abstract (a `Point → Radius → Point → Prop`
shape with `Radius` left generic) so the file stays dependency-free while still
expressing the intended target.

The target is the unconditional two-circle cap: a relation arising from a true
metric must satisfy `CircleMeetCap`. We phrase the obligation as: *every*
membership relation that is "concyclicity of a genuine circle" enjoys the cap.
Because the metric content is not importable here, the witnessing fact is stated
as a target to be supplied (`two_circle_cap_target`) and the unconditional
Euclidean version is the only open step.
-/
def OnCircleSq {Point : Type u} {Radius : Type u}
    (OnCircleRel : Point → Radius → Point → Prop) : Prop :=
  CircleMeetCap OnCircleRel

/--
**Two-circle cap, packaging direction (proved).**

If the concrete relation already has the no-three-common-points property as a
hypothesis, it satisfies `CircleMeetCap`. This direction is definitional: it
makes explicit that the genuine work is *supplying* `hgeom` from a true
Euclidean metric, which is the part that needs mathlib. Closed WITHOUT an open
step.
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
  intro c₁ c₂ r₁ r₂ p q s hne hpq hps hqs hp₁ hq₁ hs₁ hp₂ hq₂ hs₂
  exact hgeom c₁ c₂ r₁ r₂ p q s hne hpq hps hqs hp₁ hq₁ hs₁ hp₂ hq₂ hs₂

/--
**The genuinely open geometric obligation**, stated as a target with no metric
hypotheses available to close it. This is what a Euclidean instantiation must
provide: that the concrete squared-distance circle relation satisfies the
no-three-common-points property. With no metric in scope it cannot be proved, so
the body is left open. This is the honest formal record of the "two distinct
circles share at most two points" lemma (docs target (2)).

The `hEuclidean : True` slot is a placeholder marker that `OnCircleRel` is the
true squared-distance membership of a Euclidean plane. In the mathlib instance
this slot would be `∀ c r p, OnCircleRel c r p ↔ dist c p ^ 2 = r` together with
the plane structure; here it is an opaque `Prop`.
-/
theorem euclidean_circle_meet_cap_open
    {Point : Type u} {Radius : Type u}
    (OnCircleRel : Point → Radius → Point → Prop)
    (hEuclidean : True) :
    CircleMeetCap OnCircleRel := by
  -- Genuinely open without a metric: three concyclic points pinning the circle
  -- is a Euclidean fact not available in this dependency-free pilot.
  sorry

-- EVOLVE-BLOCK-END

end Erdos97.Sketches.T20TwoCircleCap
