import Erdos97.Basic

/-!
# Selected Witness Extraction

This file contains the first bridge-shaped lemma for the Lean pilot. It is
abstract and point-set based: later work must connect the official
`HasNEquidistantProperty 4` statement to `HasFourEquidistantProperty`.
-/

namespace Erdos97

universe u

/-- A selected witness row for every point of `A`. -/
structure SelectedWitnessSystem {Point : Type u} (A : Point -> Prop)
    (SameDistanceFrom : Point -> Point -> Point -> Prop) where
  witness : (p : Point) -> A p -> Witness4 Point
  witness_in_set :
    forall (p : Point) (hp : A p), WitnessInSet A p (witness p hp)
  witness_equidistant :
    forall (p : Point) (hp : A p),
      WitnessEquidistant SameDistanceFrom p (witness p hp)

namespace SelectedWitnessSystem

/-- A selected witness system implies the abstract point-set property. -/
theorem has_property {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) :
    HasFourEquidistantProperty A SameDistanceFrom := by
  intro p hp
  exact Exists.intro (S.witness p hp)
    (And.intro (S.witness_in_set p hp) (S.witness_equidistant p hp))

/-- The first selected witness for a row belongs to the ambient set. -/
theorem witness_a_mem {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    A (S.witness p hp).a :=
  WitnessInSet.a_mem (S.witness_in_set p hp)

/-- The second selected witness for a row belongs to the ambient set. -/
theorem witness_b_mem {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    A (S.witness p hp).b :=
  WitnessInSet.b_mem (S.witness_in_set p hp)

/-- The third selected witness for a row belongs to the ambient set. -/
theorem witness_c_mem {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    A (S.witness p hp).c :=
  WitnessInSet.c_mem (S.witness_in_set p hp)

/-- The fourth selected witness for a row belongs to the ambient set. -/
theorem witness_d_mem {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    A (S.witness p hp).d :=
  WitnessInSet.d_mem (S.witness_in_set p hp)

/-- The first selected witness for a row is not the row center. -/
theorem witness_a_ne_center {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    Not ((S.witness p hp).a = p) :=
  WitnessInSet.a_ne_center (S.witness_in_set p hp)

/-- The second selected witness for a row is not the row center. -/
theorem witness_b_ne_center {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    Not ((S.witness p hp).b = p) :=
  WitnessInSet.b_ne_center (S.witness_in_set p hp)

/-- The third selected witness for a row is not the row center. -/
theorem witness_c_ne_center {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    Not ((S.witness p hp).c = p) :=
  WitnessInSet.c_ne_center (S.witness_in_set p hp)

/-- The fourth selected witness for a row is not the row center. -/
theorem witness_d_ne_center {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    Not ((S.witness p hp).d = p) :=
  WitnessInSet.d_ne_center (S.witness_in_set p hp)

/-- The first and second selected witnesses in a row are equidistant from the center. -/
theorem witness_ab {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    SameDistanceFrom p (S.witness p hp).a (S.witness p hp).b :=
  WitnessEquidistant.ab (S.witness_equidistant p hp)

/-- The first and third selected witnesses in a row are equidistant from the center. -/
theorem witness_ac {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    SameDistanceFrom p (S.witness p hp).a (S.witness p hp).c :=
  WitnessEquidistant.ac (S.witness_equidistant p hp)

/-- The first and fourth selected witnesses in a row are equidistant from the center. -/
theorem witness_ad {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    SameDistanceFrom p (S.witness p hp).a (S.witness p hp).d :=
  WitnessEquidistant.ad (S.witness_equidistant p hp)

end SelectedWitnessSystem

noncomputable section

/-- Choice-based extraction of selected witnesses from the abstract property. -/
def selectedWitnessSystemOfProperty {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (h : HasFourEquidistantProperty A SameDistanceFrom) :
    SelectedWitnessSystem A SameDistanceFrom := by
  refine
    { witness := ?_
      witness_in_set := ?_
      witness_equidistant := ?_ }
  · intro p hp
    exact Classical.choose (h p hp)
  · intro p hp
    exact (Classical.choose_spec (h p hp)).left
  · intro p hp
    exact (Classical.choose_spec (h p hp)).right

/--
Bridge-shaped statement: the abstract four-equidistant property gives a
selected-witness system.

This is intentionally weaker than the eventual repository goal. The missing
work is to prove that the official Formal Conjectures predicate implies the
abstract local predicate above.
-/
theorem has_property_gives_selected_witness_system {Point : Type u}
    {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (h : HasFourEquidistantProperty A SameDistanceFrom) :
    Exists fun _S : SelectedWitnessSystem A SameDistanceFrom => True := by
  exact Exists.intro (selectedWitnessSystemOfProperty h) True.intro

/-- A selected-witness system is equivalent to the abstract property. -/
theorem has_property_iff_exists_selected_witness_system {Point : Type u}
    {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop} :
    HasFourEquidistantProperty A SameDistanceFrom <->
      Exists fun _S : SelectedWitnessSystem A SameDistanceFrom => True := by
  constructor
  · intro h
    exact has_property_gives_selected_witness_system h
  · intro h
    cases h with
    | intro S _ => exact SelectedWitnessSystem.has_property S

end

end Erdos97
