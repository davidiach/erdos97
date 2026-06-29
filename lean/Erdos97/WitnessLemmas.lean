import Erdos97.SelectedWitness

/-!
# Witness interface lemmas

Small dependency-free lemmas for unpacking the abstract selected-witness
interface.  These do not add any geometric theorem about Erdos Problem #97;
they only make the existing witness data easier to reuse in later bridge files.
-/

namespace Erdos97

universe u

-- The reverse-orientation `Witness4.b_ne_a` … `Witness4.d_ne_c` lemmas live in
-- `Erdos97.Basic` (imported transitively via `Erdos97.SelectedWitness`); they
-- are intentionally not re-declared here to avoid duplicate declarations.

section WitnessInSet

variable {Point : Type u} {A : Point -> Prop} {p : Point}
    {W : Witness4 Point}

/-- Build a `WitnessInSet` value from its eight elementary components. -/
theorem WitnessInSet.of_parts
    (ha : A W.a) (hb : A W.b) (hc : A W.c) (hd : A W.d)
    (hap : Not (W.a = p)) (hbp : Not (W.b = p))
    (hcp : Not (W.c = p)) (hdp : Not (W.d = p)) :
    WitnessInSet A p W := by
  exact
    And.intro ha
      (And.intro hb
        (And.intro hc
          (And.intro hd
            (And.intro hap
              (And.intro hbp
                (And.intro hcp hdp))))))

/-- The first witness point belongs to the ambient set. -/
theorem WitnessInSet.mem_a (h : WitnessInSet A p W) : A W.a :=
  h.left

/-- The second witness point belongs to the ambient set. -/
theorem WitnessInSet.mem_b (h : WitnessInSet A p W) : A W.b :=
  h.right.left

/-- The third witness point belongs to the ambient set. -/
theorem WitnessInSet.mem_c (h : WitnessInSet A p W) : A W.c :=
  h.right.right.left

/-- The fourth witness point belongs to the ambient set. -/
theorem WitnessInSet.mem_d (h : WitnessInSet A p W) : A W.d :=
  h.right.right.right.left

/-- The first witness is not the center. -/
theorem WitnessInSet.a_ne_center (h : WitnessInSet A p W) : Not (W.a = p) :=
  h.right.right.right.right.left

/-- The second witness is not the center. -/
theorem WitnessInSet.b_ne_center (h : WitnessInSet A p W) : Not (W.b = p) :=
  h.right.right.right.right.right.left

/-- The third witness is not the center. -/
theorem WitnessInSet.c_ne_center (h : WitnessInSet A p W) : Not (W.c = p) :=
  h.right.right.right.right.right.right.left

/-- The fourth witness is not the center. -/
theorem WitnessInSet.d_ne_center (h : WitnessInSet A p W) : Not (W.d = p) :=
  h.right.right.right.right.right.right.right

/-- The center is not the first witness. -/
theorem WitnessInSet.center_ne_a (h : WitnessInSet A p W) : Not (p = W.a) := by
  intro hp
  exact (WitnessInSet.a_ne_center h) hp.symm

/-- The center is not the second witness. -/
theorem WitnessInSet.center_ne_b (h : WitnessInSet A p W) : Not (p = W.b) := by
  intro hp
  exact (WitnessInSet.b_ne_center h) hp.symm

/-- The center is not the third witness. -/
theorem WitnessInSet.center_ne_c (h : WitnessInSet A p W) : Not (p = W.c) := by
  intro hp
  exact (WitnessInSet.c_ne_center h) hp.symm

/-- The center is not the fourth witness. -/
theorem WitnessInSet.center_ne_d (h : WitnessInSet A p W) : Not (p = W.d) := by
  intro hp
  exact (WitnessInSet.d_ne_center h) hp.symm

end WitnessInSet

section WitnessEquidistant

variable {Point : Type u} {SameDistanceFrom : Point -> Point -> Point -> Prop}
    {p : Point} {W : Witness4 Point}

/-- Build a `WitnessEquidistant` value from its three elementary components. -/
theorem WitnessEquidistant.of_parts
    (hab : SameDistanceFrom p W.a W.b)
    (hac : SameDistanceFrom p W.a W.c)
    (had : SameDistanceFrom p W.a W.d) :
    WitnessEquidistant SameDistanceFrom p W := by
  exact And.intro hab (And.intro hac had)

/-- The first and second witnesses are at the same distance from the center. -/
theorem WitnessEquidistant.ab
    (h : WitnessEquidistant SameDistanceFrom p W) :
    SameDistanceFrom p W.a W.b :=
  h.left

/-- The first and third witnesses are at the same distance from the center. -/
theorem WitnessEquidistant.ac
    (h : WitnessEquidistant SameDistanceFrom p W) :
    SameDistanceFrom p W.a W.c :=
  h.right.left

/-- The first and fourth witnesses are at the same distance from the center. -/
theorem WitnessEquidistant.ad
    (h : WitnessEquidistant SameDistanceFrom p W) :
    SameDistanceFrom p W.a W.d :=
  h.right.right

end WitnessEquidistant

section HasFourEquidistantProperty

variable {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}

/-- The abstract four-equidistant property supplies a witness row in the set. -/
theorem HasFourEquidistantProperty.exists_witness_in_set
    (h : HasFourEquidistantProperty A SameDistanceFrom)
    (p : Point) (hp : A p) :
    Exists fun W : Witness4 Point => WitnessInSet A p W := by
  match h p hp with
  | Exists.intro W hW =>
      exact Exists.intro W hW.left

/-- The abstract four-equidistant property supplies an equidistant witness row. -/
theorem HasFourEquidistantProperty.exists_witness_equidistant
    (h : HasFourEquidistantProperty A SameDistanceFrom)
    (p : Point) (hp : A p) :
    Exists fun W : Witness4 Point => WitnessEquidistant SameDistanceFrom p W := by
  match h p hp with
  | Exists.intro W hW =>
      exact Exists.intro W hW.right

end HasFourEquidistantProperty

section SelectedWitnessSystem

variable {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}

/-- The selected first witness belongs to the ambient set. -/
theorem SelectedWitnessSystem.witness_mem_a
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    A ((S.witness p hp).a) :=
  WitnessInSet.mem_a (S.witness_in_set p hp)

/-- The selected second witness belongs to the ambient set. -/
theorem SelectedWitnessSystem.witness_mem_b
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    A ((S.witness p hp).b) :=
  WitnessInSet.mem_b (S.witness_in_set p hp)

/-- The selected third witness belongs to the ambient set. -/
theorem SelectedWitnessSystem.witness_mem_c
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    A ((S.witness p hp).c) :=
  WitnessInSet.mem_c (S.witness_in_set p hp)

/-- The selected fourth witness belongs to the ambient set. -/
theorem SelectedWitnessSystem.witness_mem_d
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    A ((S.witness p hp).d) :=
  WitnessInSet.mem_d (S.witness_in_set p hp)

/-- The selected first witness is not its center. -/
theorem SelectedWitnessSystem.witness_a_ne_center
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    Not (((S.witness p hp).a) = p) :=
  WitnessInSet.a_ne_center (S.witness_in_set p hp)

/-- The selected second witness is not its center. -/
theorem SelectedWitnessSystem.witness_b_ne_center
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    Not (((S.witness p hp).b) = p) :=
  WitnessInSet.b_ne_center (S.witness_in_set p hp)

/-- The selected third witness is not its center. -/
theorem SelectedWitnessSystem.witness_c_ne_center
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    Not (((S.witness p hp).c) = p) :=
  WitnessInSet.c_ne_center (S.witness_in_set p hp)

/-- The selected fourth witness is not its center. -/
theorem SelectedWitnessSystem.witness_d_ne_center
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    Not (((S.witness p hp).d) = p) :=
  WitnessInSet.d_ne_center (S.witness_in_set p hp)

/-- The selected center is not its first witness. -/
theorem SelectedWitnessSystem.center_ne_witness_a
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    Not (p = ((S.witness p hp).a)) :=
  WitnessInSet.center_ne_a (S.witness_in_set p hp)

/-- The selected center is not its second witness. -/
theorem SelectedWitnessSystem.center_ne_witness_b
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    Not (p = ((S.witness p hp).b)) :=
  WitnessInSet.center_ne_b (S.witness_in_set p hp)

/-- The selected center is not its third witness. -/
theorem SelectedWitnessSystem.center_ne_witness_c
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    Not (p = ((S.witness p hp).c)) :=
  WitnessInSet.center_ne_c (S.witness_in_set p hp)

/-- The selected center is not its fourth witness. -/
theorem SelectedWitnessSystem.center_ne_witness_d
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    Not (p = ((S.witness p hp).d)) :=
  WitnessInSet.center_ne_d (S.witness_in_set p hp)

/-- The selected first and second witnesses are equidistant from the center. -/
theorem SelectedWitnessSystem.witness_equidistant_ab
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    SameDistanceFrom p ((S.witness p hp).a) ((S.witness p hp).b) :=
  WitnessEquidistant.ab (S.witness_equidistant p hp)

/-- The selected first and third witnesses are equidistant from the center. -/
theorem SelectedWitnessSystem.witness_equidistant_ac
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    SameDistanceFrom p ((S.witness p hp).a) ((S.witness p hp).c) :=
  WitnessEquidistant.ac (S.witness_equidistant p hp)

/-- The selected first and fourth witnesses are equidistant from the center. -/
theorem SelectedWitnessSystem.witness_equidistant_ad
    (S : SelectedWitnessSystem A SameDistanceFrom) (p : Point) (hp : A p) :
    SameDistanceFrom p ((S.witness p hp).a) ((S.witness p hp).d) :=
  WitnessEquidistant.ad (S.witness_equidistant p hp)

end SelectedWitnessSystem

section SharedWitnessRows

variable {Point : Type u} {SameDistanceFrom : Point -> Point -> Point -> Prop}

/--
If two rows share their `a`, `b`, and `c` witnesses and three points determine
at most one center, then the two centers are equal.
-/
theorem witness_abc_eqs_force_center_eq
    (center_unique :
      forall (p q x y z : Point),
        Not (x = y) ->
        Not (x = z) ->
        Not (y = z) ->
        SameDistanceFrom p x y ->
        SameDistanceFrom p x z ->
        SameDistanceFrom q x y ->
        SameDistanceFrom q x z ->
        p = q)
    {p q : Point} {Wp Wq : Witness4 Point}
    (hp : WitnessEquidistant SameDistanceFrom p Wp)
    (hq : WitnessEquidistant SameDistanceFrom q Wq)
    (ha : Wp.a = Wq.a) (hb : Wp.b = Wq.b) (hc : Wp.c = Wq.c) :
    p = q := by
  exact
    center_unique p q Wp.a Wp.b Wp.c
      Wp.a_ne_b Wp.a_ne_c Wp.b_ne_c
      (WitnessEquidistant.ab hp)
      (WitnessEquidistant.ac hp)
      (by
        simpa [ha, hb] using WitnessEquidistant.ab hq)
      (by
        simpa [ha, hc] using WitnessEquidistant.ac hq)

/--
If two distinct centers had rows sharing `a`, `b`, and `c`, this contradicts a
three-point center-uniqueness principle.
-/
theorem witness_abc_eqs_absurd_of_center_ne
    (center_unique :
      forall (p q x y z : Point),
        Not (x = y) ->
        Not (x = z) ->
        Not (y = z) ->
        SameDistanceFrom p x y ->
        SameDistanceFrom p x z ->
        SameDistanceFrom q x y ->
        SameDistanceFrom q x z ->
        p = q)
    {p q : Point} {Wp Wq : Witness4 Point}
    (hpq : Not (p = q))
    (hp : WitnessEquidistant SameDistanceFrom p Wp)
    (hq : WitnessEquidistant SameDistanceFrom q Wq)
    (ha : Wp.a = Wq.a) (hb : Wp.b = Wq.b) (hc : Wp.c = Wq.c) :
    False := by
  exact hpq (witness_abc_eqs_force_center_eq center_unique hp hq ha hb hc)

/-- Same as `witness_abc_eqs_force_center_eq`, using witnesses `a`, `b`, `d`. -/
theorem witness_abd_eqs_force_center_eq
    (center_unique :
      forall (p q x y z : Point),
        Not (x = y) ->
        Not (x = z) ->
        Not (y = z) ->
        SameDistanceFrom p x y ->
        SameDistanceFrom p x z ->
        SameDistanceFrom q x y ->
        SameDistanceFrom q x z ->
        p = q)
    {p q : Point} {Wp Wq : Witness4 Point}
    (hp : WitnessEquidistant SameDistanceFrom p Wp)
    (hq : WitnessEquidistant SameDistanceFrom q Wq)
    (ha : Wp.a = Wq.a) (hb : Wp.b = Wq.b) (hd : Wp.d = Wq.d) :
    p = q := by
  exact
    center_unique p q Wp.a Wp.b Wp.d
      Wp.a_ne_b Wp.a_ne_d Wp.b_ne_d
      (WitnessEquidistant.ab hp)
      (WitnessEquidistant.ad hp)
      (by
        simpa [ha, hb] using WitnessEquidistant.ab hq)
      (by
        simpa [ha, hd] using WitnessEquidistant.ad hq)

/-- Same as `witness_abc_eqs_absurd_of_center_ne`, using witnesses `a`, `b`, `d`. -/
theorem witness_abd_eqs_absurd_of_center_ne
    (center_unique :
      forall (p q x y z : Point),
        Not (x = y) ->
        Not (x = z) ->
        Not (y = z) ->
        SameDistanceFrom p x y ->
        SameDistanceFrom p x z ->
        SameDistanceFrom q x y ->
        SameDistanceFrom q x z ->
        p = q)
    {p q : Point} {Wp Wq : Witness4 Point}
    (hpq : Not (p = q))
    (hp : WitnessEquidistant SameDistanceFrom p Wp)
    (hq : WitnessEquidistant SameDistanceFrom q Wq)
    (ha : Wp.a = Wq.a) (hb : Wp.b = Wq.b) (hd : Wp.d = Wq.d) :
    False := by
  exact hpq (witness_abd_eqs_force_center_eq center_unique hp hq ha hb hd)

/-- Same as `witness_abc_eqs_force_center_eq`, using witnesses `a`, `c`, `d`. -/
theorem witness_acd_eqs_force_center_eq
    (center_unique :
      forall (p q x y z : Point),
        Not (x = y) ->
        Not (x = z) ->
        Not (y = z) ->
        SameDistanceFrom p x y ->
        SameDistanceFrom p x z ->
        SameDistanceFrom q x y ->
        SameDistanceFrom q x z ->
        p = q)
    {p q : Point} {Wp Wq : Witness4 Point}
    (hp : WitnessEquidistant SameDistanceFrom p Wp)
    (hq : WitnessEquidistant SameDistanceFrom q Wq)
    (ha : Wp.a = Wq.a) (hc : Wp.c = Wq.c) (hd : Wp.d = Wq.d) :
    p = q := by
  exact
    center_unique p q Wp.a Wp.c Wp.d
      Wp.a_ne_c Wp.a_ne_d Wp.c_ne_d
      (WitnessEquidistant.ac hp)
      (WitnessEquidistant.ad hp)
      (by
        simpa [ha, hc] using WitnessEquidistant.ac hq)
      (by
        simpa [ha, hd] using WitnessEquidistant.ad hq)

/-- Same as `witness_abc_eqs_absurd_of_center_ne`, using witnesses `a`, `c`, `d`. -/
theorem witness_acd_eqs_absurd_of_center_ne
    (center_unique :
      forall (p q x y z : Point),
        Not (x = y) ->
        Not (x = z) ->
        Not (y = z) ->
        SameDistanceFrom p x y ->
        SameDistanceFrom p x z ->
        SameDistanceFrom q x y ->
        SameDistanceFrom q x z ->
        p = q)
    {p q : Point} {Wp Wq : Witness4 Point}
    (hpq : Not (p = q))
    (hp : WitnessEquidistant SameDistanceFrom p Wp)
    (hq : WitnessEquidistant SameDistanceFrom q Wq)
    (ha : Wp.a = Wq.a) (hc : Wp.c = Wq.c) (hd : Wp.d = Wq.d) :
    False := by
  exact hpq (witness_acd_eqs_force_center_eq center_unique hp hq ha hc hd)

end SharedWitnessRows

section SelectedSharedWitnessRows

variable {Point : Type u} {A : Point -> Prop}
    {SameDistanceFrom : Point -> Point -> Point -> Prop}

/-- Selected-row version of `witness_abc_eqs_force_center_eq`. -/
theorem SelectedWitnessSystem.abc_eqs_force_center_eq
    (S : SelectedWitnessSystem A SameDistanceFrom)
    (center_unique :
      forall (p q x y z : Point),
        Not (x = y) ->
        Not (x = z) ->
        Not (y = z) ->
        SameDistanceFrom p x y ->
        SameDistanceFrom p x z ->
        SameDistanceFrom q x y ->
        SameDistanceFrom q x z ->
        p = q)
    {p q : Point} (hp : A p) (hq : A q)
    (ha : ((S.witness p hp).a) = ((S.witness q hq).a))
    (hb : ((S.witness p hp).b) = ((S.witness q hq).b))
    (hc : ((S.witness p hp).c) = ((S.witness q hq).c)) :
    p = q :=
  witness_abc_eqs_force_center_eq center_unique
    (S.witness_equidistant p hp) (S.witness_equidistant q hq) ha hb hc

/-- Selected-row contradiction form for shared `a`, `b`, and `c` witnesses. -/
theorem SelectedWitnessSystem.abc_eqs_absurd_of_center_ne
    (S : SelectedWitnessSystem A SameDistanceFrom)
    (center_unique :
      forall (p q x y z : Point),
        Not (x = y) ->
        Not (x = z) ->
        Not (y = z) ->
        SameDistanceFrom p x y ->
        SameDistanceFrom p x z ->
        SameDistanceFrom q x y ->
        SameDistanceFrom q x z ->
        p = q)
    {p q : Point} (hp : A p) (hq : A q)
    (hpq : Not (p = q))
    (ha : ((S.witness p hp).a) = ((S.witness q hq).a))
    (hb : ((S.witness p hp).b) = ((S.witness q hq).b))
    (hc : ((S.witness p hp).c) = ((S.witness q hq).c)) :
    False := by
  exact hpq (SelectedWitnessSystem.abc_eqs_force_center_eq S center_unique hp hq ha hb hc)

/-- Selected-row version of `witness_abd_eqs_force_center_eq`. -/
theorem SelectedWitnessSystem.abd_eqs_force_center_eq
    (S : SelectedWitnessSystem A SameDistanceFrom)
    (center_unique :
      forall (p q x y z : Point),
        Not (x = y) ->
        Not (x = z) ->
        Not (y = z) ->
        SameDistanceFrom p x y ->
        SameDistanceFrom p x z ->
        SameDistanceFrom q x y ->
        SameDistanceFrom q x z ->
        p = q)
    {p q : Point} (hp : A p) (hq : A q)
    (ha : ((S.witness p hp).a) = ((S.witness q hq).a))
    (hb : ((S.witness p hp).b) = ((S.witness q hq).b))
    (hd : ((S.witness p hp).d) = ((S.witness q hq).d)) :
    p = q :=
  witness_abd_eqs_force_center_eq center_unique
    (S.witness_equidistant p hp) (S.witness_equidistant q hq) ha hb hd

/-- Selected-row contradiction form for shared `a`, `b`, and `d` witnesses. -/
theorem SelectedWitnessSystem.abd_eqs_absurd_of_center_ne
    (S : SelectedWitnessSystem A SameDistanceFrom)
    (center_unique :
      forall (p q x y z : Point),
        Not (x = y) ->
        Not (x = z) ->
        Not (y = z) ->
        SameDistanceFrom p x y ->
        SameDistanceFrom p x z ->
        SameDistanceFrom q x y ->
        SameDistanceFrom q x z ->
        p = q)
    {p q : Point} (hp : A p) (hq : A q)
    (hpq : Not (p = q))
    (ha : ((S.witness p hp).a) = ((S.witness q hq).a))
    (hb : ((S.witness p hp).b) = ((S.witness q hq).b))
    (hd : ((S.witness p hp).d) = ((S.witness q hq).d)) :
    False := by
  exact hpq (SelectedWitnessSystem.abd_eqs_force_center_eq S center_unique hp hq ha hb hd)

/-- Selected-row version of `witness_acd_eqs_force_center_eq`. -/
theorem SelectedWitnessSystem.acd_eqs_force_center_eq
    (S : SelectedWitnessSystem A SameDistanceFrom)
    (center_unique :
      forall (p q x y z : Point),
        Not (x = y) ->
        Not (x = z) ->
        Not (y = z) ->
        SameDistanceFrom p x y ->
        SameDistanceFrom p x z ->
        SameDistanceFrom q x y ->
        SameDistanceFrom q x z ->
        p = q)
    {p q : Point} (hp : A p) (hq : A q)
    (ha : ((S.witness p hp).a) = ((S.witness q hq).a))
    (hc : ((S.witness p hp).c) = ((S.witness q hq).c))
    (hd : ((S.witness p hp).d) = ((S.witness q hq).d)) :
    p = q :=
  witness_acd_eqs_force_center_eq center_unique
    (S.witness_equidistant p hp) (S.witness_equidistant q hq) ha hc hd

/-- Selected-row contradiction form for shared `a`, `c`, and `d` witnesses. -/
theorem SelectedWitnessSystem.acd_eqs_absurd_of_center_ne
    (S : SelectedWitnessSystem A SameDistanceFrom)
    (center_unique :
      forall (p q x y z : Point),
        Not (x = y) ->
        Not (x = z) ->
        Not (y = z) ->
        SameDistanceFrom p x y ->
        SameDistanceFrom p x z ->
        SameDistanceFrom q x y ->
        SameDistanceFrom q x z ->
        p = q)
    {p q : Point} (hp : A p) (hq : A q)
    (hpq : Not (p = q))
    (ha : ((S.witness p hp).a) = ((S.witness q hq).a))
    (hc : ((S.witness p hp).c) = ((S.witness q hq).c))
    (hd : ((S.witness p hp).d) = ((S.witness q hq).d)) :
    False := by
  exact hpq (SelectedWitnessSystem.acd_eqs_force_center_eq S center_unique hp hq ha hc hd)

end SelectedSharedWitnessRows

end Erdos97
