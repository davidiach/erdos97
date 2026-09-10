import Erdos9796Proof.P97.SmallCardinality

/-! Independently spell out the finite plane statement and inspect its axiom closure.
This probe records external reproducibility; it does not change erdos97 claim status. -/

namespace IndependentN9Audit

/-- The finite claim, stated directly in standard Euclidean vocabulary. -/
theorem no_four_equidistant_up_to_nine
    {A : Finset (EuclideanSpace ℝ (Fin 2))}
    (hne : A.Nonempty)
    (hconv : ∀ a ∈ (A : Set (EuclideanSpace ℝ (Fin 2))),
      a ∉ convexHull ℝ ((A : Set (EuclideanSpace ℝ (Fin 2))) \ {a}))
    (hcard : A.card ≤ 9) :
    ¬ (∀ p ∈ A, ∃ r : ℝ, r > 0 ∧
      (A.filter fun q => dist p q = r).card ≥ 4) :=
  Problem97.not_hasNEquidistantProperty_four_of_card_le_nine hne hconv hcard

#print axioms Problem97.counterexample_card_ge_nine
#print axioms Problem97.FiniteN9Closure
#print axioms Problem97.counterexample_card_ge_ten
#print axioms Problem97.not_hasNEquidistantProperty_four_of_card_le_nine
#print axioms IndependentN9Audit.no_four_equidistant_up_to_nine

end IndependentN9Audit
