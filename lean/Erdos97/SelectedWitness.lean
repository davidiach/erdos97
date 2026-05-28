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

/-- A selected witness system recovers the abstract four-equidistant property. -/
theorem selectedWitnessSystem_gives_property {Point : Type u}
    {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) :
    HasFourEquidistantProperty A SameDistanceFrom := by
  intro p hp
  exact Exists.intro (S.witness p hp)
    (And.intro (S.witness_in_set p hp) (S.witness_equidistant p hp))

/-- The selected first witness lies in the ambient set. -/
theorem selectedWitnessSystem_a_mem {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) {p : Point} (hp : A p) :
    A (S.witness p hp).a :=
  witnessInSet_a_mem (S.witness_in_set p hp)

/-- The selected second witness lies in the ambient set. -/
theorem selectedWitnessSystem_b_mem {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) {p : Point} (hp : A p) :
    A (S.witness p hp).b :=
  witnessInSet_b_mem (S.witness_in_set p hp)

/-- The selected third witness lies in the ambient set. -/
theorem selectedWitnessSystem_c_mem {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) {p : Point} (hp : A p) :
    A (S.witness p hp).c :=
  witnessInSet_c_mem (S.witness_in_set p hp)

/-- The selected fourth witness lies in the ambient set. -/
theorem selectedWitnessSystem_d_mem {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) {p : Point} (hp : A p) :
    A (S.witness p hp).d :=
  witnessInSet_d_mem (S.witness_in_set p hp)

/-- The selected first witness is not the center. -/
theorem selectedWitnessSystem_a_ne_center {Point : Type u}
    {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) {p : Point} (hp : A p) :
    Not ((S.witness p hp).a = p) :=
  witnessInSet_a_ne_center (S.witness_in_set p hp)

/-- The selected second witness is not the center. -/
theorem selectedWitnessSystem_b_ne_center {Point : Type u}
    {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) {p : Point} (hp : A p) :
    Not ((S.witness p hp).b = p) :=
  witnessInSet_b_ne_center (S.witness_in_set p hp)

/-- The selected third witness is not the center. -/
theorem selectedWitnessSystem_c_ne_center {Point : Type u}
    {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) {p : Point} (hp : A p) :
    Not ((S.witness p hp).c = p) :=
  witnessInSet_c_ne_center (S.witness_in_set p hp)

/-- The selected fourth witness is not the center. -/
theorem selectedWitnessSystem_d_ne_center {Point : Type u}
    {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) {p : Point} (hp : A p) :
    Not ((S.witness p hp).d = p) :=
  witnessInSet_d_ne_center (S.witness_in_set p hp)

/-- The selected first and second witnesses satisfy the distance relation. -/
theorem selectedWitnessSystem_ab_equidistant {Point : Type u}
    {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) {p : Point} (hp : A p) :
    SameDistanceFrom p (S.witness p hp).a (S.witness p hp).b :=
  witnessEquidistant_ab (S.witness_equidistant p hp)

/-- The selected first and third witnesses satisfy the distance relation. -/
theorem selectedWitnessSystem_ac_equidistant {Point : Type u}
    {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) {p : Point} (hp : A p) :
    SameDistanceFrom p (S.witness p hp).a (S.witness p hp).c :=
  witnessEquidistant_ac (S.witness_equidistant p hp)

/-- The selected first and fourth witnesses satisfy the distance relation. -/
theorem selectedWitnessSystem_ad_equidistant {Point : Type u}
    {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (S : SelectedWitnessSystem A SameDistanceFrom) {p : Point} (hp : A p) :
    SameDistanceFrom p (S.witness p hp).a (S.witness p hp).d :=
  witnessEquidistant_ad (S.witness_equidistant p hp)

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

/-- The abstract property is equivalent to the existence of a selected witness system. -/
theorem has_property_iff_exists_selected_witness_system {Point : Type u}
    {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop} :
    HasFourEquidistantProperty A SameDistanceFrom ↔
      Exists fun _S : SelectedWitnessSystem A SameDistanceFrom => True := by
  constructor
  · intro h
    exact Exists.intro (selectedWitnessSystemOfProperty h) True.intro
  · intro h
    cases h with
    | intro S _ =>
        exact selectedWitnessSystem_gives_property S

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
  exact (has_property_iff_exists_selected_witness_system.mp h)

end

end Erdos97
