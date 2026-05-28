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

namespace WitnessInSet

/-- Build a `WitnessInSet` proof from its eight component facts. -/
theorem of_components {Point : Type u} {A : Point -> Prop} {p : Point}
    {W : Witness4 Point}
    (ha : A W.a) (hb : A W.b) (hc : A W.c) (hd : A W.d)
    (ha_ne : Not (W.a = p)) (hb_ne : Not (W.b = p))
    (hc_ne : Not (W.c = p)) (hd_ne : Not (W.d = p)) :
    WitnessInSet A p W := by
  exact
    And.intro ha
      (And.intro hb
        (And.intro hc
          (And.intro hd
            (And.intro ha_ne
              (And.intro hb_ne (And.intro hc_ne hd_ne))))))

/-- The first selected witness belongs to the ambient set. -/
theorem a_mem {Point : Type u} {A : Point -> Prop} {p : Point}
    {W : Witness4 Point} (h : WitnessInSet A p W) : A W.a :=
  h.left

/-- The second selected witness belongs to the ambient set. -/
theorem b_mem {Point : Type u} {A : Point -> Prop} {p : Point}
    {W : Witness4 Point} (h : WitnessInSet A p W) : A W.b :=
  h.right.left

/-- The third selected witness belongs to the ambient set. -/
theorem c_mem {Point : Type u} {A : Point -> Prop} {p : Point}
    {W : Witness4 Point} (h : WitnessInSet A p W) : A W.c :=
  h.right.right.left

/-- The fourth selected witness belongs to the ambient set. -/
theorem d_mem {Point : Type u} {A : Point -> Prop} {p : Point}
    {W : Witness4 Point} (h : WitnessInSet A p W) : A W.d :=
  h.right.right.right.left

/-- The first selected witness is not the center. -/
theorem a_ne_center {Point : Type u} {A : Point -> Prop} {p : Point}
    {W : Witness4 Point} (h : WitnessInSet A p W) : Not (W.a = p) :=
  h.right.right.right.right.left

/-- The second selected witness is not the center. -/
theorem b_ne_center {Point : Type u} {A : Point -> Prop} {p : Point}
    {W : Witness4 Point} (h : WitnessInSet A p W) : Not (W.b = p) :=
  h.right.right.right.right.right.left

/-- The third selected witness is not the center. -/
theorem c_ne_center {Point : Type u} {A : Point -> Prop} {p : Point}
    {W : Witness4 Point} (h : WitnessInSet A p W) : Not (W.c = p) :=
  h.right.right.right.right.right.right.left

/-- The fourth selected witness is not the center. -/
theorem d_ne_center {Point : Type u} {A : Point -> Prop} {p : Point}
    {W : Witness4 Point} (h : WitnessInSet A p W) : Not (W.d = p) :=
  h.right.right.right.right.right.right.right

end WitnessInSet

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

namespace WitnessEquidistant

/-- Build a `WitnessEquidistant` proof from its three component facts. -/
theorem of_components {Point : Type u}
    {SameDistanceFrom : Point -> Point -> Point -> Prop} {p : Point}
    {W : Witness4 Point}
    (hab : SameDistanceFrom p W.a W.b)
    (hac : SameDistanceFrom p W.a W.c)
    (had : SameDistanceFrom p W.a W.d) :
    WitnessEquidistant SameDistanceFrom p W := by
  exact And.intro hab (And.intro hac had)

/-- The first and second selected witnesses are equidistant from the center. -/
theorem ab {Point : Type u}
    {SameDistanceFrom : Point -> Point -> Point -> Prop} {p : Point}
    {W : Witness4 Point} (h : WitnessEquidistant SameDistanceFrom p W) :
    SameDistanceFrom p W.a W.b :=
  h.left

/-- The first and third selected witnesses are equidistant from the center. -/
theorem ac {Point : Type u}
    {SameDistanceFrom : Point -> Point -> Point -> Prop} {p : Point}
    {W : Witness4 Point} (h : WitnessEquidistant SameDistanceFrom p W) :
    SameDistanceFrom p W.a W.c :=
  h.right.left

/-- The first and fourth selected witnesses are equidistant from the center. -/
theorem ad {Point : Type u}
    {SameDistanceFrom : Point -> Point -> Point -> Prop} {p : Point}
    {W : Witness4 Point} (h : WitnessEquidistant SameDistanceFrom p W) :
    SameDistanceFrom p W.a W.d :=
  h.right.right

end WitnessEquidistant

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
