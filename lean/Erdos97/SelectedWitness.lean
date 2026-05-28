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

/-- Reconstitute the abstract four-equidistant property from selected witnesses. -/
lemma SelectedWitnessSystem.property {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) :
    HasFourEquidistantProperty A SameDistanceFrom := by
  intro p hp
  exact Exists.intro (S.witness p hp)
    (And.intro (S.witness_in_set p hp) (S.witness_equidistant p hp))

/-- The selected `a` witness lies in the ambient point set. -/
lemma SelectedWitnessSystem.a_mem {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    A (S.witness p hp).a := by
  exact witnessInSet_a_mem (S.witness_in_set p hp)

/-- The selected `b` witness lies in the ambient point set. -/
lemma SelectedWitnessSystem.b_mem {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    A (S.witness p hp).b := by
  exact witnessInSet_b_mem (S.witness_in_set p hp)

/-- The selected `c` witness lies in the ambient point set. -/
lemma SelectedWitnessSystem.c_mem {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    A (S.witness p hp).c := by
  exact witnessInSet_c_mem (S.witness_in_set p hp)

/-- The selected `d` witness lies in the ambient point set. -/
lemma SelectedWitnessSystem.d_mem {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    A (S.witness p hp).d := by
  exact witnessInSet_d_mem (S.witness_in_set p hp)

/-- The selected `a` witness is not its center. -/
lemma SelectedWitnessSystem.a_ne_center {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    Not ((S.witness p hp).a = p) := by
  exact witnessInSet_a_ne_center (S.witness_in_set p hp)

/-- The selected `b` witness is not its center. -/
lemma SelectedWitnessSystem.b_ne_center {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    Not ((S.witness p hp).b = p) := by
  exact witnessInSet_b_ne_center (S.witness_in_set p hp)

/-- The selected `c` witness is not its center. -/
lemma SelectedWitnessSystem.c_ne_center {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    Not ((S.witness p hp).c = p) := by
  exact witnessInSet_c_ne_center (S.witness_in_set p hp)

/-- The selected `d` witness is not its center. -/
lemma SelectedWitnessSystem.d_ne_center {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    Not ((S.witness p hp).d = p) := by
  exact witnessInSet_d_ne_center (S.witness_in_set p hp)

/-- The center is not the selected `a` witness. -/
lemma SelectedWitnessSystem.center_ne_a {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    Not (p = (S.witness p hp).a) := by
  exact witnessInSet_center_ne_a (S.witness_in_set p hp)

/-- The center is not the selected `b` witness. -/
lemma SelectedWitnessSystem.center_ne_b {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    Not (p = (S.witness p hp).b) := by
  exact witnessInSet_center_ne_b (S.witness_in_set p hp)

/-- The center is not the selected `c` witness. -/
lemma SelectedWitnessSystem.center_ne_c {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    Not (p = (S.witness p hp).c) := by
  exact witnessInSet_center_ne_c (S.witness_in_set p hp)

/-- The center is not the selected `d` witness. -/
lemma SelectedWitnessSystem.center_ne_d {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    Not (p = (S.witness p hp).d) := by
  exact witnessInSet_center_ne_d (S.witness_in_set p hp)

/-- The selected `a` and `b` witnesses have the same radius from the center. -/
lemma SelectedWitnessSystem.ab_equidistant {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    SameDistanceFrom p (S.witness p hp).a (S.witness p hp).b := by
  exact witnessEquidistant_ab (S.witness_equidistant p hp)

/-- The selected `a` and `c` witnesses have the same radius from the center. -/
lemma SelectedWitnessSystem.ac_equidistant {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    SameDistanceFrom p (S.witness p hp).a (S.witness p hp).c := by
  exact witnessEquidistant_ac (S.witness_equidistant p hp)

/-- The selected `a` and `d` witnesses have the same radius from the center. -/
lemma SelectedWitnessSystem.ad_equidistant {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    SameDistanceFrom p (S.witness p hp).a (S.witness p hp).d := by
  exact witnessEquidistant_ad (S.witness_equidistant p hp)

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

/-- The choice-extracted selected-witness system reconstitutes the input property. -/
lemma selectedWitnessSystemOfProperty_property {Point : Type u}
    {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (h : HasFourEquidistantProperty A SameDistanceFrom) :
    HasFourEquidistantProperty A SameDistanceFrom := by
  exact SelectedWitnessSystem.property (selectedWitnessSystemOfProperty h)

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

/-- Selected-witness-system packaging is equivalent to the abstract property. -/
lemma selectedWitnessSystem_exists_iff_property {Point : Type u}
    {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop} :
    (Exists fun _S : SelectedWitnessSystem A SameDistanceFrom => True) ↔
      HasFourEquidistantProperty A SameDistanceFrom := by
  constructor
  · intro h
    cases h with
    | intro S _ => exact SelectedWitnessSystem.property S
  · intro h
    exact Exists.intro (selectedWitnessSystemOfProperty h) True.intro

end

end Erdos97