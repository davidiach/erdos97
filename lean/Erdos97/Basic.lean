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

/-- The witness fields `b` and `a` are distinct in the reverse order. -/
lemma Witness4.b_ne_a {Point : Type u} (W : Witness4 Point) :
    Not (W.b = W.a) := by
  intro h
  exact W.a_ne_b h.symm

/-- The witness fields `c` and `a` are distinct in the reverse order. -/
lemma Witness4.c_ne_a {Point : Type u} (W : Witness4 Point) :
    Not (W.c = W.a) := by
  intro h
  exact W.a_ne_c h.symm

/-- The witness fields `d` and `a` are distinct in the reverse order. -/
lemma Witness4.d_ne_a {Point : Type u} (W : Witness4 Point) :
    Not (W.d = W.a) := by
  intro h
  exact W.a_ne_d h.symm

/-- The witness fields `c` and `b` are distinct in the reverse order. -/
lemma Witness4.c_ne_b {Point : Type u} (W : Witness4 Point) :
    Not (W.c = W.b) := by
  intro h
  exact W.b_ne_c h.symm

/-- The witness fields `d` and `b` are distinct in the reverse order. -/
lemma Witness4.d_ne_b {Point : Type u} (W : Witness4 Point) :
    Not (W.d = W.b) := by
  intro h
  exact W.b_ne_d h.symm

/-- The witness fields `d` and `c` are distinct in the reverse order. -/
lemma Witness4.d_ne_c {Point : Type u} (W : Witness4 Point) :
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

/-- Build a `WitnessInSet` fact from its membership and center-exclusion parts. -/
lemma witnessInSet_mk {Point : Type u} {A : Point -> Prop} {p : Point}
    {W : Witness4 Point} (ha : A W.a) (hb : A W.b) (hc : A W.c)
    (hd : A W.d) (ha_ne_p : Not (W.a = p))
    (hb_ne_p : Not (W.b = p)) (hc_ne_p : Not (W.c = p))
    (hd_ne_p : Not (W.d = p)) : WitnessInSet A p W := by
  exact
    And.intro ha
      (And.intro hb
        (And.intro hc
          (And.intro hd
            (And.intro ha_ne_p
              (And.intro hb_ne_p (And.intro hc_ne_p hd_ne_p))))))

/-- The `a` witness lies in the ambient point set. -/
lemma witnessInSet_a_mem {Point : Type u} {A : Point -> Prop} {p : Point}
    {W : Witness4 Point} (h : WitnessInSet A p W) : A W.a := by
  exact h.left

/-- The `b` witness lies in the ambient point set. -/
lemma witnessInSet_b_mem {Point : Type u} {A : Point -> Prop} {p : Point}
    {W : Witness4 Point} (h : WitnessInSet A p W) : A W.b := by
  exact h.right.left

/-- The `c` witness lies in the ambient point set. -/
lemma witnessInSet_c_mem {Point : Type u} {A : Point -> Prop} {p : Point}
    {W : Witness4 Point} (h : WitnessInSet A p W) : A W.c := by
  exact h.right.right.left

/-- The `d` witness lies in the ambient point set. -/
lemma witnessInSet_d_mem {Point : Type u} {A : Point -> Prop} {p : Point}
    {W : Witness4 Point} (h : WitnessInSet A p W) : A W.d := by
  exact h.right.right.right.left

/-- The `a` witness is not the center. -/
lemma witnessInSet_a_ne_center {Point : Type u} {A : Point -> Prop}
    {p : Point} {W : Witness4 Point} (h : WitnessInSet A p W) :
    Not (W.a = p) := by
  exact h.right.right.right.right.left

/-- The `b` witness is not the center. -/
lemma witnessInSet_b_ne_center {Point : Type u} {A : Point -> Prop}
    {p : Point} {W : Witness4 Point} (h : WitnessInSet A p W) :
    Not (W.b = p) := by
  exact h.right.right.right.right.right.left

/-- The `c` witness is not the center. -/
lemma witnessInSet_c_ne_center {Point : Type u} {A : Point -> Prop}
    {p : Point} {W : Witness4 Point} (h : WitnessInSet A p W) :
    Not (W.c = p) := by
  exact h.right.right.right.right.right.right.left

/-- The `d` witness is not the center. -/
lemma witnessInSet_d_ne_center {Point : Type u} {A : Point -> Prop}
    {p : Point} {W : Witness4 Point} (h : WitnessInSet A p W) :
    Not (W.d = p) := by
  exact h.right.right.right.right.right.right.right

/-- The center is not the `a` witness. -/
lemma witnessInSet_center_ne_a {Point : Type u} {A : Point -> Prop}
    {p : Point} {W : Witness4 Point} (h : WitnessInSet A p W) :
    Not (p = W.a) := by
  intro hp
  exact (witnessInSet_a_ne_center h) hp.symm

/-- The center is not the `b` witness. -/
lemma witnessInSet_center_ne_b {Point : Type u} {A : Point -> Prop}
    {p : Point} {W : Witness4 Point} (h : WitnessInSet A p W) :
    Not (p = W.b) := by
  intro hp
  exact (witnessInSet_b_ne_center h) hp.symm

/-- The center is not the `c` witness. -/
lemma witnessInSet_center_ne_c {Point : Type u} {A : Point -> Prop}
    {p : Point} {W : Witness4 Point} (h : WitnessInSet A p W) :
    Not (p = W.c) := by
  intro hp
  exact (witnessInSet_c_ne_center h) hp.symm

/-- The center is not the `d` witness. -/
lemma witnessInSet_center_ne_d {Point : Type u} {A : Point -> Prop}
    {p : Point} {W : Witness4 Point} (h : WitnessInSet A p W) :
    Not (p = W.d) := by
  intro hp
  exact (witnessInSet_d_ne_center h) hp.symm

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

/-- Build a witness-equidistance fact from its three equality-of-distance parts. -/
lemma witnessEquidistant_mk {Point : Type u}
    {SameDistanceFrom : Point -> Point -> Point -> Prop} {p : Point}
    {W : Witness4 Point} (hab : SameDistanceFrom p W.a W.b)
    (hac : SameDistanceFrom p W.a W.c) (had : SameDistanceFrom p W.a W.d) :
    WitnessEquidistant SameDistanceFrom p W := by
  exact And.intro hab (And.intro hac had)

/-- The `a` and `b` witnesses are at the same distance from the center. -/
lemma witnessEquidistant_ab {Point : Type u}
    {SameDistanceFrom : Point -> Point -> Point -> Prop} {p : Point}
    {W : Witness4 Point} (h : WitnessEquidistant SameDistanceFrom p W) :
    SameDistanceFrom p W.a W.b := by
  exact h.left

/-- The `a` and `c` witnesses are at the same distance from the center. -/
lemma witnessEquidistant_ac {Point : Type u}
    {SameDistanceFrom : Point -> Point -> Point -> Prop} {p : Point}
    {W : Witness4 Point} (h : WitnessEquidistant SameDistanceFrom p W) :
    SameDistanceFrom p W.a W.c := by
  exact h.right.left

/-- The `a` and `d` witnesses are at the same distance from the center. -/
lemma witnessEquidistant_ad {Point : Type u}
    {SameDistanceFrom : Point -> Point -> Point -> Prop} {p : Point}
    {W : Witness4 Point} (h : WitnessEquidistant SameDistanceFrom p W) :
    SameDistanceFrom p W.a W.d := by
  exact h.right.right

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

/-- Extract just the set-membership side of a local four-equidistant witness. -/
lemma hasFourEquidistantProperty_exists_witnessInSet {Point : Type u}
    {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (h : HasFourEquidistantProperty A SameDistanceFrom) (p : Point)
    (hp : A p) : Exists fun W : Witness4 Point => WitnessInSet A p W := by
  cases (h p hp) with
  | intro W hW =>
      exact Exists.intro W hW.left

/-- Extract just the equidistance side of a local four-equidistant witness. -/
lemma hasFourEquidistantProperty_exists_witnessEquidistant {Point : Type u}
    {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}
    (h : HasFourEquidistantProperty A SameDistanceFrom) (p : Point)
    (hp : A p) :
    Exists fun W : Witness4 Point => WitnessEquidistant SameDistanceFrom p W := by
  cases (h p hp) with
  | intro W hW =>
      exact Exists.intro W hW.right

end Erdos97
