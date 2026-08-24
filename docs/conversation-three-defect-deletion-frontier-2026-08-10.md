# Corrected three-defect deletion frontier from the conversation

Status: `PAPER_PROOF_CANDIDATE / REVIEW_PENDING / OPEN_BRIDGE`

Date: 2026-08-10.

This note continues the conversation research ledger merged in PR #921. It
records one assignment-independent theorem that survived the later proof
search, identifies an overreach from an **unmerged** post-#921 conversation
round, and gives a narrower successor target. No claim in merged PR #921 is
being retracted.

It does **not** claim a proof or counterexample to Erdős Problem 97. It does not
change `STATE.md`, `RESULTS.md`, `docs/claims.md`, or any machine-readable claim
metadata.

## 1. Correction to the maximal-blocker-assignment route

A later, unmerged conversation round chose, for every source `q`, one
unique-four blocker `beta(q)` and maximized the sum of squared blocker-fiber
sizes. The resulting exchange inequality is useful for the **chosen**
assignment:

```text
q belongs to the exact row at c,
beta(q) = d != c
  => load(d) >= load(c) + 1.
```

That inequality can rule out certain mutual cross-memberships between two
chosen blocker fibers.

The overreach was the subsequent inference that deleting `q` can fail only at
`beta(q)`. A point can belong to several complete exact-four rows. In
particular, it can belong to a row centered at a unique-four center that receives
no source under the chosen assignment. Deleting `q` destroys every unique-four
row containing `q`, not merely the selected one.

Therefore the following implication is **withdrawn from that unmerged
continuation**:

```text
chosen blocker beta(q)
  => beta(q) is the only center made non-4-rich by deleting q.
```

Any downstream universal claim requiring that implication, including the
unqualified canonical-candidate/equilateral fork, is not promoted here.

The corrected route must count **all** unique-four rows containing a source.

## 2. Setup

Let `A` be a finite strictly convex carrier satisfying the four-equidistant
property at every vertex, and assume `A` is vertex-minimal among such carriers.

Write `K4(X,p)` for the assertion that `p` has at least four points of `X` at
one positive distance.

Call a center `c in A` fully deletion-robust when

```text
K4(A \ {q}, c)
```

holds for every `q in A`.

Let

```text
U = { c in A : c is not fully deletion-robust }.
```

Minimality gives the standard unique-four structure.

### Unique-four center lemma

For every `c in U`, there is a unique positive radius whose complete distance
class `K_c` has at least four points, and in fact

```text
|K_c| = 4.
```

Moreover, for every `q in A`,

```text
not K4(A \ {q}, c)  <=>  q in K_c.
```

#### Proof

Choose `q` whose deletion destroys four-richness at `c`.

Every rich radius class at `c` must contain `q`; otherwise it would remain
after deleting `q`. Distinct radius classes are disjoint, so there is at most
one rich radius. Its class cannot have at least five members, because deleting
one point would leave four. Hence the complete class has exactly four members.

Deleting a member of this class leaves only three points at the unique rich
radius and therefore destroys `K4`. Deleting a point outside the class leaves
the four-point class intact. This proves the equivalence.

### Unique-four cover lemma

Every `q in A` lies in `K_c` for at least one `c in U`.

#### Proof

Otherwise deleting `q` would preserve `K4` at every surviving center, producing
a smaller strictly convex carrier with the same property and contradicting
minimality.

## 3. The assignment-independent incidence count

For `q in A`, define

```text
d(q) = |{ c in U : q in K_c }|.
```

Count incidences `(c,q)` with `c in U` and `q in K_c` in two ways:

```text
sum_{q in A} d(q)
  = sum_{c in U} |K_c|
  = 4 |U|.
```

If `A` contains at least one fully deletion-robust center, then

```text
|U| <= |A| - 1,
```

and therefore

```text
sum_{q in A} d(q) <= 4|A| - 4 < 4|A|.
```

Hence some `q` satisfies `d(q) <= 3`. The cover lemma gives `d(q) >= 1`.

In the intended all-large tri-apex residual, each of the three distinct
physical MEC apices carries the established `ApexRichClassStructure`: either
one radius class has at least six points or two distinct radii each have at
least four. Either alternative makes the center fully deletion-robust, as
recorded by the pinned Lean theorem
[`fullyDeletionRobustAt_of_apexRichClassStructure`](https://github.com/mysticflounder/erdos-97-96-formalization/blob/3ee15db22b02f4923da535a7f7a19c4a75fb3030/lean/Erdos9796Proof/P97/ATail/ApexRichClassStructure.lean#L70-L83).
Thus the hypothesis is available there with room to spare.

## 4. Three-defect deletion theorem

> **Theorem.**
> In a vertex-minimal counterexample with at least one fully
> deletion-robust center, there exists `q in A` such that deleting `q` leaves
> between one and three non-4-rich centers. More exactly, if
>
> ```text
> F(q) = { c in U : q in K_c },
> ```
>
> then
>
> ```text
> 1 <= |F(q)| <= 3
> ```
>
> and
>
> ```text
> { c in A \ {q} : not K4(A \ {q}, c) } = F(q).
> ```

### Proof

Choose `q` with `1 <= d(q) <= 3` from the incidence count.

For `c in F(q)`, the unique-four center lemma says that deleting `q` destroys
`K4` at `c`.

For `c in U \ F(q)`, the exact class `K_c` avoids `q` and survives intact.

Every center outside `U` is fully deletion-robust and also survives.

The deleted point `q` is not a member of its own positive-radius class, so it is
not accidentally counted as a failed center. The displayed equality follows.

## 5. Immediate dangerous-triple consequences

Fix the source `q` from the theorem. For each `p in F(q)`, write

```text
K_p = {q} disjoint_union T_p.
```

Then:

```text
|T_p| = 3,
```

all members of `T_p` are at distance `|pq|` from `p`, and `T_p` is
noncollinear. A line meets a positive-radius circle in at most two points.

Thus `(q,p,T_p)` has exactly the theorem-facing shape called a U5 dangerous
triple in the separate Lean formalization.

For distinct `p,r in F(q)`, the circles centered at `p` and `r` both contain
`q`. Distinct circles have at most two common points, so

```text
|T_p intersect T_r| <= 1.
```

Consequently:

```text
|F(q)| = 1  =>  one three-point dangerous triple;
|F(q)| = 2  =>  the union of the two triples has at least 5 points;
|F(q)| = 3  =>  the union of the three triples has at least 6 points.
```

For the last line, add the triples in sequence: the second loses at most one
new point to the first, and the third loses at most two new points to the first
two.

Every center outside `F(q) union {q}` has some q-free four-point witness after
deleting `q`.

## 6. What the theorem does not supply

The three-defect theorem does not by itself finish the current U5 route.

Global q-free `K4` at a center only gives the existence of a four-point witness
somewhere in `A \ {q}`. The current bounded U5 terminal needs a stronger
payload, such as:

1. a selected candidate on the dangerous `p`-circle;
2. q-free selected classes confined to a named eight-point support;
3. the positive row memberships of a proved q-critical/exact/q-critical or
   equilateral-bridge incompatibility; or
4. a small ordered set of exact rows matching one of the established
   Kalmanson schemas.

Deletion survival alone does not choose a canonical surviving radius at a
robust center and does not confine the witness class to a bounded support.

The theorem also does not ensure that the selected `q` lies in the designated
surplus cap required by a particular on-spine U-lane ingress. It produces the
native dangerous-triple geometry, not the entire cap-specific residual packet.

## 7. Corrected remaining bridge

The next theorem should be stated from the assignment-independent packet.

> **Three-defect closure target.**
> Let `q` be a source whose deletion has defect set `F(q)` of cardinality at
> most three, and let `T_p` be the q-critical triple at each `p in F(q)`.
> Prove that at least one of the following occurs:
>
> 1. a q-free witness lies on one dangerous `p`-circle;
> 2. the q-free classes needed by a U5 audit are confined to a bounded support;
> 3. four exact rows materialize a proved Kalmanson schema;
> 4. deleting `q` together with a blocker-closed subset of `F(q)` leaves a
>    proper nonempty `K4` subcarrier.

Each output is already terminal or feeds an existing terminal. The missing work
is the disjunction itself.

A useful way to organize the proof is by the exact value of `|F(q)|`:

```text
1 defect: one q-critical circle plus q-free K4 everywhere else;
2 defects: two q-critical circles through q, with at most one shared triple point;
3 defects: three q-critical circles through q, with pairwise triple overlap <= 1.
```

This is a finite number of **critical centers**, but not yet a finite number of
ambient witness vertices.

## 8. Formalization crosswalk

This crosswalk is pinned to upstream formalization commit
[`3ee15db`](https://github.com/mysticflounder/erdos-97-96-formalization/commit/3ee15db22b02f4923da535a7f7a19c4a75fb3030),
the `main` revision at 2026-08-10 10:43 UTC immediately before this note was
committed. The unique-four interfaces are in
[`MinimalUniqueFourCover.lean`](https://github.com/mysticflounder/erdos-97-96-formalization/blob/3ee15db22b02f4923da535a7f7a19c4a75fb3030/lean/Erdos9796Proof/P97/ATail/MinimalUniqueFourCover.lean),
and the U5 interfaces are in
[`U5GlobalIncidenceBasic.lean`](https://github.com/mysticflounder/erdos-97-96-formalization/blob/3ee15db22b02f4923da535a7f7a19c4a75fb3030/lean/Erdos9796Proof/P97/U5GlobalIncidenceBasic.lean).
At that revision the separate Lean project contains interfaces close to the
required pieces:

```text
IsUniqueFourCenter / uniqueFourClass
notRobustCenters
U5DangerousTriple
U5QCriticalTripleClass
U5QDeletedK4Class
U5BoundedEightPointSupport
U5BoundedAuditSupport
```

The recommended first formal theorem is the pure double-counting statement:

```text
exists q in A,
  1 <= card {c in notRobustCenters D | q in uniqueFourClass c}
  and
  card {c in notRobustCenters D | q in uniqueFourClass c} <= 3.
```

Its dependencies should be limited to:

- the minimal unique-four cover;
- exact cardinality four of every nonrobust center's unique class;
- existence of one robust center;
- finite incidence double counting.

No cap order, Kalmanson inequality, solver certificate, or selected-blocker map
is needed for this theorem.

The second theorem should identify this incidence fiber with the exact set of
centers that fail after deleting `q`.

## 9. Status boundary

The rigorous candidate advancement recorded here is:

```text
minimal counterexample
  + at least one fully deletion-robust center
  => a deletion with exactly 1, 2, or 3 bad centers
  => at most three q-critical dangerous triples.
```

The still-open step is:

```text
at most three q-critical dangerous triples
  + q-free K4 at every other center
  => a bounded U5, Kalmanson, or smaller-subcarrier terminal.
```

No general proof is claimed.
