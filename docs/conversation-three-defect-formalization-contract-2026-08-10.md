# Formalization contract for the three-defect deletion theorem

Status: `FORMALIZATION_TARGET / REVIEW_PENDING / NO_STATUS_PROMOTION`

Date: 2026-08-10.

This document turns the corrected conversation result into a small,
independently checkable theorem contract. It is intentionally separated from
the larger cap, U5, and Kalmanson machinery.

The schematic Lean vocabulary below is pinned to upstream formalization commit
[`3ee15db`](https://github.com/mysticflounder/erdos-97-96-formalization/commit/3ee15db22b02f4923da535a7f7a19c4a75fb3030),
the `main` revision at 2026-08-10 10:43 UTC immediately before this document
was committed. Later implementations should either use that revision or
explicitly recheck the names and theorem surfaces against a newer source.

## 1. Pure finite-cover core

The geometric content needed for the first theorem is only the existence of a
proper family of four-element blocks that covers the carrier.

Let:

```text
V = finite nonempty set of vertices,
C = finite set of critical centers,
K(c) subset V for c in C,
|K(c)| = 4 for every c,
union_{c in C} K(c) = V,
|C| < |V|.
```

Define the block degree

```text
d(v) = |{c in C : v in K(c)}|.
```

Then:

> **Low-degree four-cover lemma.**
> There exists `v in V` with
>
> ```text
> 1 <= d(v) <= 3.
> ```

### Proof

Coverage gives `d(v) >= 1` for every `v`.

Double counting gives

```text
sum_{v in V} d(v) = sum_{c in C} |K(c)| = 4|C| < 4|V|.
```

If every degree were at least four, the left side would be at least `4|V|`, a
contradiction.

This lemma should be formalized first, with no Euclidean imports.

## 2. Suggested abstract Lean surface

One possible theorem shape is:

```lean
theorem exists_mem_degree_between_one_and_three
    {V C : Type*}
    [Fintype V] [Fintype C]
    [DecidableEq V] [DecidableEq C]
    (K : C → Finset V)
    (hcard : ∀ c, (K c).card = 4)
    (hcover : ∀ v, ∃ c, v ∈ K c)
    (hproper : Fintype.card C < Fintype.card V) :
    ∃ v : V,
      1 ≤ ((Finset.univ : Finset C).filter fun c => v ∈ K c).card ∧
      ((Finset.univ : Finset C).filter fun c => v ∈ K c).card ≤ 3
```

The proof should use a finite incidence set or a sum-swap identity rather than
any solver-backed arithmetic.

A convenient incidence set is:

```lean
I = (Finset.univ.product Finset.univ).filter fun pair => pair.1 ∈ K pair.2
```

Count `I` by centers and by vertices.

## 3. Geometric adapter

For a vertex-minimal four-rich convex carrier `D.A`, instantiate:

```text
V = carrier vertices,
C = notRobustCenters D,
K(c) = the complete unique-four class at c.
```

The adapter needs four established facts.

### A. Exact four

For every `c in notRobustCenters D`, the unique rich class at `c` has
cardinality exactly four.

### B. Cover

Every carrier vertex belongs to the unique-four class of at least one
nonrobust center.

### C. Proper center set

At least one carrier center is fully deletion-robust. In the intended
all-large tri-apex application, each of the three physical MEC apices carries
`ApexRichClassStructure`: either one radius class has at least six points or
two distinct radii each have at least four. The pinned theorem
[`fullyDeletionRobustAt_of_apexRichClassStructure`](https://github.com/mysticflounder/erdos-97-96-formalization/blob/3ee15db22b02f4923da535a7f7a19c4a75fb3030/lean/Erdos9796Proof/P97/ATail/ApexRichClassStructure.lean#L70-L83)
makes either alternative fully deletion-robust. Hence

```text
(notRobustCenters D).card <= D.A.card - 3.
```

Only strict inequality is needed by the abstract lemma.

### D. Failure equivalence

For `c` nonrobust and `q` a carrier vertex:

```text
not K4(D.A.erase q, c)
  <=>
q belongs to the complete unique-four class at c.
```

The forward direction follows because every rich class must meet the deleted
point. The reverse direction follows from uniqueness and exact cardinality
four.

## 4. Suggested geometric declarations

The first declaration should expose only the incidence fiber:

```lean
noncomputable def deletionDefectFiber
    (D : CounterexampleData) (q : ℝ²) : Finset ℝ² :=
  (notRobustCenters D).filter fun c =>
    q ∈ uniqueFourClass D.A c
```

The exact argument list of `uniqueFourClass` should follow the pinned source,
or a later source revision whose interface has been explicitly rechecked,
rather than this schematic notation.

Then prove:

```lean
theorem exists_deletionDefectFiber_card_between_one_and_three
    (D : CounterexampleData)
    (hmin : D.Minimal)
    (hrobust : ∃ a ∈ D.A, FullyDeletionRobustAt D a) :
    ∃ q ∈ D.A,
      1 ≤ (deletionDefectFiber D q).card ∧
      (deletionDefectFiber D q).card ≤ 3
```

The second declaration should identify the fiber semantically:

```lean
theorem deletionDefectFiber_eq_failedCenters
    (D : CounterexampleData)
    (hmin : D.Minimal)
    {q : ℝ²} (hq : q ∈ D.A) :
    deletionDefectFiber D q =
      (D.A.erase q).filter fun c =>
        ¬ HasNEquidistantPointsAt 4 (D.A.erase q) c
```

Depending on the live definition of robustness, it may be cleaner to filter
all of `D.A`; `q` itself should not enter the failure set because deleting the
center does not remove any positive-radius witness.

The combined theorem is:

```lean
theorem exists_threeDefectDeletion
    (D : CounterexampleData)
    (hmin : D.Minimal)
    (hrobust : ∃ a ∈ D.A, FullyDeletionRobustAt D a) :
    ∃ q ∈ D.A,
      1 ≤ ((D.A.erase q).filter fun c =>
        ¬ HasNEquidistantPointsAt 4 (D.A.erase q) c).card ∧
      ((D.A.erase q).filter fun c =>
        ¬ HasNEquidistantPointsAt 4 (D.A.erase q) c).card ≤ 3
```

## 5. Dangerous-triple adapter

For each `p` in the defect fiber, the ambient complete class through `q` is a
critical four-shell. Erasing `q` gives a three-point class.

The adapter should prove:

```lean
theorem exists_u5DangerousTriple_of_mem_deletionDefectFiber
    (D : CounterexampleData)
    (hmin : D.Minimal)
    {q p : ℝ²}
    (hq : q ∈ D.A)
    (hp : p ∈ deletionDefectFiber D q) :
    ∃ T : Finset ℝ²,
      U5DangerousTriple D q p T
```

The support can be defined canonically as the unique-four class at `p` erased
at `q`.

For distinct defect centers, prove the overlap bound:

```lean
theorem dangerousTriples_inter_card_le_one
    ...
    (hp_ne_hr : p ≠ r) :
    (T_p ∩ T_r).card ≤ 1
```

This is the ordinary two-circle intersection bound after accounting for their
already shared point `q`.

Optional useful corollaries are:

```text
2 defect centers => union of triples has cardinality at least 5;
3 defect centers => union of triples has cardinality at least 6.
```

## 6. Explicit non-goals

This formalization must not claim any of the following:

- the selected source lies in a designated Moser cap;
- only one center fails after deletion;
- a robust center's surviving class is its previously selected class;
- all needed U5 classes lie in eight points;
- the three-defect packet already contradicts convexity;
- a proof of Erdős 97 has been completed.

The theorem is assignment-independent. It should not depend on a maximized
blocker selector, blocker-fiber loads, or a chosen critical-shell map except as
an adapter for an already canonical unique-four class.

## 7. Validation plan

Before connecting the theorem to the live spine:

1. Prove the pure finite-cover lemma in an isolated file.
2. Print its axioms and require only the ordinary Lean core axioms used by the
   surrounding noncomputational geometry.
3. Instantiate it with a small synthetic four-cover where the minimum degree is
   exactly three, to guard against accidentally proving a stronger false bound.
4. Add a negative control with `|C| = |V|` and every degree exactly four; this
   should demonstrate why the existence of a robust center, hence `|C| < |V|`,
   is load-bearing.
5. Prove the failure-fiber equality separately from the counting theorem.
6. Only then construct the U5 dangerous triples.

## 8. Successor theorem contract

The next genuinely geometric statement is not part of the first PR-sized
formalization task.

> **Three-defect bounded-closure target.**
> From one to three q-critical dangerous triples and q-free K4 at every other
> center, produce at least one of:
>
> - a U5 same-circle export;
> - bounded support for the U5 finite audit;
> - a proved positive-incidence U5 or Kalmanson pattern;
> - a proper blocker-closed K4 subcarrier.

The three-defect theorem narrows the number of exceptional centers. It does not
bound the ambient witnesses used by surviving classes. That support-confinement
step remains the open bridge.
