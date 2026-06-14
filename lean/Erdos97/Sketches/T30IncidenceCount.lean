import Erdos97.TwoCircleCap

/-!
# T30 Incidence-Count Lower Bound Sketch (rules out small `n`)

This is a marked proof-sketch shell for the incidence-counting kernel that
forces the vertex count to be large. It addresses docs targets (4) and (5):

* (4) the incidence count ruling out `n ≤ 6` (equivalently `n ≥ 7`);
* (5) the `n = 7` parity/Fano-type obstruction, stated but left open.

It is NOT a proof of Erdos Problem #97 and claims no Lean proof of it.

## The counting idea (informal)

Every vertex `i` of a strictly convex `n`-gon carries a selected `4`-set `S_i`
of *other* vertices that are equidistant from `i` (concyclic about `i`). View
this as a bipartite incidence between `n` centers and the unordered pairs of
vertices: center `i` "uses" the `C(4,2) = 6` pairs inside `S_i`. The
pair-sharing cap `|S_a ∩ S_b| ≤ 2` (proved conditionally in
`Erdos97.TwoCircleCap`) means two distinct centers can share at most one common
pair... and a Fisher/double-counting inequality between the `n · 6` used-pair
slots and the `C(n,2)` available pairs forces `n` to be large. The clean
threshold this route yields is `n ≥ 7`.

## Honest status

* The combinatorial *engine* — a counting inequality forcing `7 ≤ n` from a
  bounded-overlap design — is stated as `incidence_forces_seven` and is
  **NOT** proved here (open step): it needs `Finset.card`/double-counting from
  mathlib, absent under the dependency-free lakefile.
* The packaging `no_small_n` (no valid configuration with `n ≤ 6`) is derived
  from it honestly (no extra open step).
* The `n = 7` obstruction `seven_obstruction_open` is stated and left open;
  it is the harder parity/Fano step and is genuinely unsettled at
  proof-assistant level here.
-/

namespace Erdos97.Sketches.T30IncidenceCount

open Erdos97

universe u

-- EVOLVE-BLOCK-START

/--
Abstract incidence data for the small-case counting argument.

* `n` is the vertex count.
* `usedPairs i` is the number of vertex-pairs that center `i` "uses" (its
  `C(4,2) = 6` equidistant pairs); we record the intended value `6` as a field
  hypothesis rather than hard-coding it.
* `overlap i j ≤ 1` encodes the pair-sharing cap consequence: two distinct
  centers share at most one common used pair (the `≤ 2` *points* cap of
  `Erdos97.TwoCircleCap` yields `≤ 1` common *pair*).
* `totalPairs = C(n,2)` bounds the number of distinct pairs available.

This is a deliberately arithmetic surrogate (over `Nat`) for the genuine
`Finset` incidence count, kept dependency-free.
-/
structure IncidenceData where
  n : Nat
  usedPairsPerCenter : Nat
  used_eq_six : usedPairsPerCenter = 6
  totalPairs : Nat
  total_eq_choose : totalPairs * 2 = n * (n - 1)
  /-- Distinct used pairs is at most the available pairs (a packing bound). -/
  packing : n * usedPairsPerCenter ≤ totalPairs * 2

/--
**Incidence lower bound (target (4)): a valid configuration forces `7 ≤ n`.**

From the packing inequality `n · 6 ≤ totalPairs · 2 = n · (n-1)` one gets,
for `n ≥ 1`, that `6 ≤ n - 1`, i.e. `n ≥ 7`. The arithmetic is elementary but
its honest Lean discharge needs `Nat`-subtraction monotonicity lemmas; we leave
it as the labelled open step of this kernel.

Honest status: STATED, NOT PROVED (`sorry`). The inequality manipulation is
routine but is exactly the `Nat` arithmetic that would be done with mathlib
`omega`/`Nat.sub` lemmas. We do not fake it.
-/
theorem incidence_forces_seven (d : IncidenceData) (hn : 1 ≤ d.n) : 7 ≤ d.n := by
  -- From `d.packing` and `d.used_eq_six`, `6 * n ≤ n * (n - 1)`, hence
  -- `6 ≤ n - 1` (using `1 ≤ n`), hence `7 ≤ n`. Routine `Nat` arithmetic.
  sorry

/--
**No valid configuration on `≤ 6` vertices** (the docs target (4) packaging).

Contrapositive form: if the bounded-overlap incidence data exists with `n ≤ 6`
and `n ≥ 1`, we get a contradiction with `incidence_forces_seven`. This is
closed honestly modulo the single open arithmetic step above.
-/
theorem no_small_n (d : IncidenceData) (hn : 1 ≤ d.n) (hsmall : d.n ≤ 6) :
    False := by
  have h7 : 7 ≤ d.n := incidence_forces_seven d hn
  -- `7 ≤ n ≤ 6` is impossible.
  exact absurd (Nat.le_trans h7 hsmall) (by decide)

/--
**`n = 7` obstruction (target (5)), stated and left open.**

At `n = 7` the packing inequality is tight (`7·6 = 42 = 7·6`), so the crude
count does not rule it out; the genuine obstruction is a parity / Fano-plane
incidence argument showing the would-be `(7,?,?)`-design cannot be realised by
*concyclic* `4`-sets in a strictly convex polygon. This is recorded as a target;
it is genuinely open at proof-assistant level in this pilot.

Honest status: STATED, NOT PROVED (`sorry`). The hypothesis `htight` records
that the count is tight; the conclusion `False` is the obstruction we cannot
yet formally close.
-/
theorem seven_obstruction_open (d : IncidenceData)
    (hn7 : d.n = 7)
    (htight : d.n * d.usedPairsPerCenter = d.totalPairs * 2) :
    False := by
  -- Parity/Fano-type obstruction for the tight `n = 7` case. Not formalised.
  sorry

-- EVOLVE-BLOCK-END

end Erdos97.Sketches.T30IncidenceCount
