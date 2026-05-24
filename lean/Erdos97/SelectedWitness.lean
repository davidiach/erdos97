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

end

end Erdos97
