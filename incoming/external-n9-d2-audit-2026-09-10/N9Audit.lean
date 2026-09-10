import Erdos9796Proof.P97.SmallCardinality

/-!
Independent, mathlib-vocabulary statements for the two general small-cardinality
claims. These are consumers of external proofs, not new proofs of unrestricted
Erdos #97. Radius choice is inside the quantifier over the center.
-/
namespace ExternalN9D2Audit

theorem general_nine
    (A : Finset (EuclideanSpace ℝ (Fin 2))) (hcard : A.card = 9)
    (hconv : ∀ a ∈ (A : Set (EuclideanSpace ℝ (Fin 2))),
      a ∉ convexHull ℝ ((A : Set (EuclideanSpace ℝ (Fin 2))) \ {a})) :
    ¬ (∀ p ∈ A, ∃ r : ℝ, r > 0 ∧
      (A.filter fun q => dist p q = r).card ≥ 4) :=
  Problem97.FiniteN9Closure A hcard hconv

theorem through_nine
    (A : Finset (EuclideanSpace ℝ (Fin 2))) (hne : A.Nonempty)
    (hcard : A.card ≤ 9)
    (hconv : ∀ a ∈ (A : Set (EuclideanSpace ℝ (Fin 2))),
      a ∉ convexHull ℝ ((A : Set (EuclideanSpace ℝ (Fin 2))) \ {a})) :
    ¬ (∀ p ∈ A, ∃ r : ℝ, r > 0 ∧
      (A.filter fun q => dist p q = r).card ≥ 4) :=
  Problem97.not_hasNEquidistantProperty_four_of_card_le_nine hne hconv hcard

end ExternalN9D2Audit

#print axioms ExternalN9D2Audit.general_nine
#print axioms ExternalN9D2Audit.through_nine
#print axioms Problem97.FiniteN9Closure
#print axioms Problem97.counterexample_card_ge_ten
