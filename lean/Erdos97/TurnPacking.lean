/-!
# Turn-Packing Contract

This module is the formalization-facing shell for the review-pending
turn-inequality route. It does not prove the Euclidean turn lemma. Instead, it
pins the indexing and arithmetic contract consumed by the Python checker:

* equal-radius offset pairs should force two weak interval inequalities;
* the machine replay stores sorted sums of exterior-turn variables; and
* a dual certificate is contradictory when its lower bound is larger than its
  total coefficient budget.

The intended geometry bridge is documented in `docs/turn-inequality-lemma.md`.
-/

namespace Erdos97

/-- The two interval orientations extracted from one equal-radius offset pair. -/
inductive TurnOrientation where
  | forward
  | reverse
deriving Repr, BEq

namespace TurnOrientation

/-- Stable reviewer-facing names used by the Python JSON payloads. -/
def name : TurnOrientation -> String
  | forward => "forward"
  | reverse => "reverse"

theorem name_forward : TurnOrientation.forward.name = "forward" := by
  rfl

theorem name_reverse : TurnOrientation.reverse.name = "reverse" := by
  rfl

theorem forward_ne_reverse : Not (TurnOrientation.forward = TurnOrientation.reverse) := by
  intro h
  cases h

end TurnOrientation

/-- Cyclic index convention for a turn variable `h` steps after center `i`. -/
def cyclicTurnIndex (n i h : Nat) : Nat :=
  (i + h) % n

/--
The forward support for offsets `a < b`: turns at `i+1, ..., i+b-1`.

The left witness turn `i+a` is included when `a > 0`; the right endpoint
`i+b` is excluded. The support is cyclic-order, not sorted storage order.
-/
def forwardTurnSupport (n i b : Nat) : List Nat :=
  (List.range (b - 1)).map (fun k => cyclicTurnIndex n i (k + 1))

/--
The reverse support for offsets `a < b`: turns at `i+a+1, ..., i+n-1`.

The left endpoint `i+a` is excluded; the right witness turn `i+b` is included
when `b < n`. The support is cyclic-order, not sorted storage order.
-/
def reverseTurnSupport (n i a : Nat) : List Nat :=
  (List.range (n - a - 1)).map (fun k => cyclicTurnIndex n i (a + 1 + k))

theorem forwardTurnSupport_length (n i b : Nat) :
    (forwardTurnSupport n i b).length = b - 1 := by
  simp [forwardTurnSupport]

theorem reverseTurnSupport_length (n i a : Nat) :
    (reverseTurnSupport n i a).length = n - a - 1 := by
  simp [reverseTurnSupport]

/-- Offset-pair hypotheses for the proof-facing turn lemma. -/
def ValidTurnOffsetPair (n a b : Nat) : Prop :=
  And (1 <= a) (And (a < b) (b < n))

/-- One weak machine-facing interval inequality. -/
structure WeakTurnInterval where
  n : Nat
  center : Nat
  leftOffset : Nat
  rightOffset : Nat
  orientation : TurnOrientation
  cyclicSupport : List Nat
  bound : Nat
deriving Repr

/-- Build the expected weak interval record for one orientation. -/
def expectedWeakTurnInterval
    (n center leftOffset rightOffset : Nat)
    (orientation : TurnOrientation) : WeakTurnInterval :=
  match orientation with
  | TurnOrientation.forward =>
      { n := n
        center := center
        leftOffset := leftOffset
        rightOffset := rightOffset
        orientation := TurnOrientation.forward
        cyclicSupport := forwardTurnSupport n center rightOffset
        bound := 1 }
  | TurnOrientation.reverse =>
      { n := n
        center := center
        leftOffset := leftOffset
        rightOffset := rightOffset
        orientation := TurnOrientation.reverse
        cyclicSupport := reverseTurnSupport n center leftOffset
        bound := 1 }

theorem expectedWeakTurnInterval_bound
    (n center leftOffset rightOffset : Nat) (orientation : TurnOrientation) :
    (expectedWeakTurnInterval n center leftOffset rightOffset orientation).bound = 1 := by
  cases orientation <;> rfl

theorem expectedWeakTurnInterval_forward_support
    (n center leftOffset rightOffset : Nat) :
    (expectedWeakTurnInterval n center leftOffset rightOffset
      TurnOrientation.forward).cyclicSupport =
        forwardTurnSupport n center rightOffset := by
  rfl

theorem expectedWeakTurnInterval_reverse_support
    (n center leftOffset rightOffset : Nat) :
    (expectedWeakTurnInterval n center leftOffset rightOffset
      TurnOrientation.reverse).cyclicSupport =
        reverseTurnSupport n center leftOffset := by
  rfl

/--
Proof-facing assumption shape for the geometric turn lemma.

`EqualRadiusPair center a b` is supplied by selected-distance equality.
`ForcesWeakInterval interval` means the geometric lemma justifies the stored
weak inequality. The module deliberately leaves both predicates abstract.
-/
def TurnLemmaForcesWeakIntervals
    (EqualRadiusPair : Nat -> Nat -> Nat -> Prop)
    (ForcesWeakInterval : WeakTurnInterval -> Prop) : Prop :=
  forall n center a b : Nat,
    ValidTurnOffsetPair n a b ->
      EqualRadiusPair center a b ->
        And
          (ForcesWeakInterval
            (expectedWeakTurnInterval n center a b TurnOrientation.forward))
          (ForcesWeakInterval
            (expectedWeakTurnInterval n center a b TurnOrientation.reverse))

/-- A compact arithmetic certificate shape for a weak turn-packing replay. -/
structure TurnPackingDualCertificate where
  lambda : Nat
  turnTotalBudget : Nat
  selectedIntervalCount : Nat
deriving Repr

namespace TurnPackingDualCertificate

/--
The maximum possible left side when each turn variable appears at most
`lambda` times and the normalized total turn is `turnTotalBudget`.
-/
def coefficientBudget (cert : TurnPackingDualCertificate) : Nat :=
  cert.turnTotalBudget * cert.lambda

/--
Semantic arithmetic realization of the certificate summary. The selected weak
intervals force `selectedIntervalCount <= lhs`, while coefficient counting
gives `lhs <= coefficientBudget`.
-/
def RealizedBy (cert : TurnPackingDualCertificate) (lhs : Nat) : Prop :=
  And (cert.selectedIntervalCount <= lhs) (lhs <= cert.coefficientBudget)

/-- The stored summary is contradictory when its lower bound exceeds the cap. -/
def HasGap (cert : TurnPackingDualCertificate) : Prop :=
  cert.coefficientBudget < cert.selectedIntervalCount

/-- A turn-packing certificate with a strict gap has no arithmetic realization. -/
theorem no_realization (cert : TurnPackingDualCertificate) (lhs : Nat)
    (hrealized : cert.RealizedBy lhs) (hgap : cert.HasGap) : False := by
  have hle : cert.selectedIntervalCount <= cert.coefficientBudget :=
    Nat.le_trans hrealized.left hrealized.right
  exact (Nat.not_lt_of_ge hle) hgap

/-- The normalized n=9 turn replay uses total turn budget `4`. -/
def normalizedN9 (lambda selectedIntervalCount : Nat) :
    TurnPackingDualCertificate :=
  { lambda := lambda
    turnTotalBudget := 4
    selectedIntervalCount := selectedIntervalCount }

theorem normalizedN9_coefficientBudget
    (lambda selectedIntervalCount : Nat) :
    (normalizedN9 lambda selectedIntervalCount).coefficientBudget = 4 * lambda := by
  rfl

end TurnPackingDualCertificate

end Erdos97
