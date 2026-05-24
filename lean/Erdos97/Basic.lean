/-!
# Erdos97 Lean Pilot

This module is a small abstract interface for proof-sketch work. It does not
formalize the official geometric statement of Erdos Problem #97 and it does not
claim a proof or a counterexample.

The purpose is to isolate the selected-witness extraction shape before binding
it to `Finset R^2`, `ConvexIndep`, cyclic orders, or squared-distance
certificate formats.
-/

namespace Erdos97

universe u

/-- Four distinct points chosen as witnesses for a center. -/
structure Witness4 (Point : Type u) where
  a : Point
  b : Point
  c : Point
  d : Point
  a_ne_b : Not (a = b)
  a_ne_c : Not (a = c)
  a_ne_d : Not (a = d)
  b_ne_c : Not (b = c)
  b_ne_d : Not (b = d)
  c_ne_d : Not (c = d)

/--
The chosen witnesses are members of `A` and are not the center.

This stays point-set based on purpose. Cyclic labels and finite incidence rows
should be added by later bridge modules, not baked into the first extraction
lemma.
-/
def WitnessInSet {Point : Type u} (A : Point -> Prop) (p : Point)
    (W : Witness4 Point) : Prop :=
  And (A W.a)
    (And (A W.b)
      (And (A W.c)
        (And (A W.d)
          (And (Not (W.a = p))
            (And (Not (W.b = p))
              (And (Not (W.c = p)) (Not (W.d = p))))))))

/--
`SameDistanceFrom p q r` should later be instantiated as
`dist p q = dist p r`, or as an equivalent squared-distance relation with the
needed nonnegativity bridge.
-/
def WitnessEquidistant {Point : Type u}
    (SameDistanceFrom : Point -> Point -> Point -> Prop) (p : Point)
    (W : Witness4 Point) : Prop :=
  And (SameDistanceFrom p W.a W.b)
    (And (SameDistanceFrom p W.a W.c) (SameDistanceFrom p W.a W.d))

/--
An abstract point-set version of "every point has four other equidistant
points". This is not the Formal Conjectures definition; it is the local
selected-witness interface that the official definition should imply.
-/
def HasFourEquidistantProperty {Point : Type u} (A : Point -> Prop)
    (SameDistanceFrom : Point -> Point -> Point -> Prop) : Prop :=
  forall p : Point,
    A p ->
      Exists fun W : Witness4 Point =>
        And (WitnessInSet A p W) (WitnessEquidistant SameDistanceFrom p W)

end Erdos97
