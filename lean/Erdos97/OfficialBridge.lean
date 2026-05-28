import Erdos97.SelectedWitness

/-!
# Official-Shape Bridge

This module isolates the first adapter needed to connect the upstream
Formal Conjectures statement to the local selected-witness interface.

The upstream statement uses a finite filter/cardinality assertion:
for each center, at least four points lie at one positive distance. This
dependency-free pilot does not import `Finset`, `dist`, or `ConvexIndep`.
Instead, it records the extracted four-point radius fiber that such a
cardinality assertion should provide, and proves that this extracted data
implies the local `HasFourEquidistantProperty`.

It is not a proof of Erdos Problem #97.
-/

namespace Erdos97

universe u

/--
Four points extracted from an official-style equal-radius fiber around `p`.

`SameDistanceFrom p q r` should later be instantiated by equal distance from
`p`, for example `dist p q = dist p r` in the upstream mathlib setting.
-/
structure FourPointFiberWitness {Point : Type u} (A : Point -> Prop)
    (SameDistanceFrom : Point -> Point -> Point -> Prop) (p : Point) where
  a : Point
  b : Point
  c : Point
  d : Point
  a_mem : A a
  b_mem : A b
  c_mem : A c
  d_mem : A d
  a_ne_p : Not (a = p)
  b_ne_p : Not (b = p)
  c_ne_p : Not (c = p)
  d_ne_p : Not (d = p)
  a_ne_b : Not (a = b)
  a_ne_c : Not (a = c)
  a_ne_d : Not (a = d)
  b_ne_c : Not (b = c)
  b_ne_d : Not (b = d)
  c_ne_d : Not (c = d)
  a_same_b : SameDistanceFrom p a b
  a_same_c : SameDistanceFrom p a c
  a_same_d : SameDistanceFrom p a d

def FourPointFiberWitness.toWitness4 {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop} {p : Point}
    (F : FourPointFiberWitness A SameDistanceFrom p) : Witness4 Point :=
  { a := F.a
    b := F.b
    c := F.c
    d := F.d
    a_ne_b := F.a_ne_b
    a_ne_c := F.a_ne_c
    a_ne_d := F.a_ne_d
    b_ne_c := F.b_ne_c
    b_ne_d := F.b_ne_d
    c_ne_d := F.c_ne_d }

theorem FourPointFiberWitness.witnessInSet {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop} {p : Point}
    (F : FourPointFiberWitness A SameDistanceFrom p) :
    WitnessInSet A p F.toWitness4 :=
  And.intro F.a_mem
    (And.intro F.b_mem
      (And.intro F.c_mem
        (And.intro F.d_mem
          (And.intro F.a_ne_p
            (And.intro F.b_ne_p (And.intro F.c_ne_p F.d_ne_p))))))

theorem FourPointFiberWitness.witnessEquidistant {Point : Type u}
    {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop} {p : Point}
    (F : FourPointFiberWitness A SameDistanceFrom p) :
    WitnessEquidistant SameDistanceFrom p F.toWitness4 :=
  And.intro F.a_same_b (And.intro F.a_same_c F.a_same_d)

theorem FourPointFiberWitness.toLocalWitness {Point : Type u}
    {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop} {p : Point}
    (F : FourPointFiberWitness A SameDistanceFrom p) :
    Exists fun W : Witness4 Point =>
      And (WitnessInSet A p W) (WitnessEquidistant SameDistanceFrom p W) :=
  Exists.intro F.toWitness4
    (And.intro F.witnessInSet F.witnessEquidistant)

/--
Official-shaped row data for every point in `A`.

The remaining upstream bridge obligation is to derive this predicate from the
Formal Conjectures `HasNEquidistantProperty 4` definition by unpacking the
finite filter/cardinality proof.
-/
def HasFourPointFiberWitnesses {Point : Type u} (A : Point -> Prop)
    (SameDistanceFrom : Point -> Point -> Point -> Prop) : Prop :=
  forall p : Point,
    A p -> Exists fun F : FourPointFiberWitness A SameDistanceFrom p => True

/--
An official-shaped four-point fiber for every center gives the local
selected-witness property.
-/
theorem has_four_point_fiber_witnesses_implies_has_four_equidistant_property
    {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (h : HasFourPointFiberWitnesses A SameDistanceFrom) :
    HasFourEquidistantProperty A SameDistanceFrom :=
  fun p hp =>
    match h p hp with
    | Exists.intro F _ => F.toLocalWitness

end Erdos97
