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

/-- The second witness is distinct from the first. -/
theorem witness4_b_ne_a {Point : Type u} (W : Witness4 Point) :
    Not (W.b = W.a) := by
  intro h
  exact W.a_ne_b h.symm

/-- The third witness is distinct from the first. -/
theorem witness4_c_ne_a {Point : Type u} (W : Witness4 Point) :
    Not (W.c = W.a) := by
  intro h
  exact W.a_ne_c h.symm

/-- The fourth witness is distinct from the first. -/
theorem witness4_d_ne_a {Point : Type u} (W : Witness4 Point) :
    Not (W.d = W.a) := by
  intro h
  exact W.a_ne_d h.symm

/-- The third witness is distinct from the second. -/
theorem witness4_c_ne_b {Point : Type u} (W : Witness4 Point) :
    Not (W.c = W.b) := by
  intro h
  exact W.b_ne_c h.symm

/-- The fourth witness is distinct from the second. -/
theorem witness4_d_ne_b {Point : Type u} (W : Witness4 Point) :
    Not (W.d = W.b) := by
  intro h
  exact W.b_ne_d h.symm

/-- The fourth witness is distinct from the third. -/
theorem witness4_d_ne_c {Point : Type u} (W : Witness4 Point) :
    Not (W.d = W.c) := by
  intro h
  exact W.c_ne_d h.symm

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

/-- Build a `WitnessInSet` fact from its named membership and center-avoidance components. -/
theorem witnessInSet_mk {Point : Type u} {A : Point -> Prop} {p : Point}
    {W : Witness4 Point}
    (ha : A W.a) (hb : A W.b) (hc : A W.c) (hd : A W.d)
    (ha_ne_p : Not (W.a = p)) (hb_ne_p : Not (W.b = p))
    (hc_ne_p : Not (W.c = p)) (hd_ne_p : Not (W.d = p)) :
    WitnessInSet A p W := by
  refine And.intro ha ?_
  refine And.intro hb ?_
  refine And.intro hc ?_
  refine And.intro hd ?_
  refine And.intro ha_ne_p ?_
  refine And.intro hb_ne_p ?_
  exact And.intro hc_ne_p hd_ne_p

/-- The first witness lies in the ambient set. -/
theorem witnessInSet_a_mem {Point : Type u} {A : Point -> Prop} {p : Point}
    {W : Witness4 Point} (h : WitnessInSet A p W) : A W.a :=
  h.left

/-- The second witness lies in the ambient set. -/
theorem witnessInSet_b_mem {Point : Type u} {A : Point -> Prop} {p : Point}
    {W : Witness4 Point} (h : WitnessInSet A p W) : A W.b :=
  h.right.left

/-- The third witness lies in the ambient set. -/
theorem witnessInSet_c_mem {Point : Type u} {A : Point -> Prop} {p : Point}
    {W : Witness4 Point} (h : WitnessInSet A p W) : A W.c :=
  h.right.right.left

/-- The fourth witness lies in the ambient set. -/
theorem witnessInSet_d_mem {Point : Type u} {A : Point -> Prop} {p : Point}
    {W : Witness4 Point} (h : WitnessInSet A p W) : A W.d :=
  h.right.right.right.left

/-- The first witness is not the center. -/
theorem witnessInSet_a_ne_center {Point : Type u} {A : Point -> Prop}
    {p : Point} {W : Witness4 Point} (h : WitnessInSet A p W) :
    Not (W.a = p) :=
  h.right.right.right.right.left

/-- The second witness is not the center. -/
theorem witnessInSet_b_ne_center {Point : Type u} {A : Point -> Prop}
    {p : Point} {W : Witness4 Point} (h : WitnessInSet A p W) :
    Not (W.b = p) :=
  h.right.right.right.right.right.left

/-- The third witness is not the center. -/
theorem witnessInSet_c_ne_center {Point : Type u} {A : Point -> Prop}
    {p : Point} {W : Witness4 Point} (h : WitnessInSet A p W) :
    Not (W.c = p) :=
  h.right.right.right.right.right.right.left

/-- The fourth witness is not the center. -/
theorem witnessInSet_d_ne_center {Point : Type u} {A : Point -> Prop}
    {p : Point} {W : Witness4 Point} (h : WitnessInSet A p W) :
    Not (W.d = p) :=
  h.right.right.right.right.right.right.right

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

/-- Build a `WitnessEquidistant` fact from its three named equal-distance components. -/
theorem witnessEquidistant_mk {Point : Type u}
    {SameDistanceFrom : Point -> Point -> Point -> Prop} {p : Point}
    {W : Witness4 Point}
    (hab : SameDistanceFrom p W.a W.b) (hac : SameDistanceFrom p W.a W.c)
    (had : SameDistanceFrom p W.a W.d) :
    WitnessEquidistant SameDistanceFrom p W := by
  exact And.intro hab (And.intro hac had)

/-- The first and second witnesses have the selected equal-distance relation. -/
theorem witnessEquidistant_ab {Point : Type u}
    {SameDistanceFrom : Point -> Point -> Point -> Prop} {p : Point}
    {W : Witness4 Point} (h : WitnessEquidistant SameDistanceFrom p W) :
    SameDistanceFrom p W.a W.b :=
  h.left

/-- The first and third witnesses have the selected equal-distance relation. -/
theorem witnessEquidistant_ac {Point : Type u}
    {SameDistanceFrom : Point -> Point -> Point -> Prop} {p : Point}
    {W : Witness4 Point} (h : WitnessEquidistant SameDistanceFrom p W) :
    SameDistanceFrom p W.a W.c :=
  h.right.left

/-- The first and fourth witnesses have the selected equal-distance relation. -/
theorem witnessEquidistant_ad {Point : Type u}
    {SameDistanceFrom : Point -> Point -> Point -> Prop} {p : Point}
    {W : Witness4 Point} (h : WitnessEquidistant SameDistanceFrom p W) :
    SameDistanceFrom p W.a W.d :=
  h.right.right

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

/-- Unpack the abstract property at one center. -/
theorem hasFourEquidistantProperty_exists_witness {Point : Type u}
    {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (h : HasFourEquidistantProperty A SameDistanceFrom) {p : Point}
    (hp : A p) :
    Exists fun W : Witness4 Point =>
      And (WitnessInSet A p W) (WitnessEquidistant SameDistanceFrom p W) :=
  h p hp

end Erdos97
