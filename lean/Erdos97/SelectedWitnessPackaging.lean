import Erdos97.SelectedWitness

/-!
# Selected Witness Packaging Lemmas

This file keeps small packaging equivalences for the abstract selected-witness
interface. It is deliberately lemma-only: no search artifacts, status claims, or
new geometric assumptions are introduced here.
-/

namespace Erdos97

universe u

noncomputable section

/-- A property proof gives nonempty selected-witness-system packaging. -/
lemma selectedWitnessSystem_nonempty_of_property {Point : Type u}
    {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (h : HasFourEquidistantProperty A SameDistanceFrom) :
    Nonempty (SelectedWitnessSystem A SameDistanceFrom) := by
  exact Nonempty.intro (selectedWitnessSystemOfProperty h)

/-- Nonempty selected-witness-system packaging gives back the abstract property. -/
lemma property_of_selectedWitnessSystem_nonempty {Point : Type u}
    {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (h : Nonempty (SelectedWitnessSystem A SameDistanceFrom)) :
    HasFourEquidistantProperty A SameDistanceFrom := by
  cases h with
  | intro S => exact SelectedWitnessSystem.property S

/-- Nonempty selected-witness-system packaging is equivalent to the abstract property. -/
lemma selectedWitnessSystem_nonempty_iff_property {Point : Type u}
    {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop} :
    Nonempty (SelectedWitnessSystem A SameDistanceFrom) ↔
      HasFourEquidistantProperty A SameDistanceFrom := by
  constructor
  · intro h
    exact property_of_selectedWitnessSystem_nonempty h
  · intro h
    exact selectedWitnessSystem_nonempty_of_property h

end

end Erdos97
