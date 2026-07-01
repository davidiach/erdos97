# Small Counterexamples To Erdos Problem 97: n <= 8 Release Note

Self-contained reviewer release note. Source-of-truth status remains README.md, STATE.md, RESULTS.md, docs/claims.md, and metadata/erdos97.yaml.

## Abstract

Erdos Problem #97 asks whether every convex polygon has a vertex with
no other four vertices equidistant from it. This release note packages
the repository's small-case result: in the selected-witness formulation
there is no strictly convex counterexample with n <= 8, in the
repo-local machine-checked finite-case sense. The official problem
remains falsifiable/open, and independent review is still requested
before paper-style or public theorem-style use.

## Status And Scope

Official/global status: falsifiable/open, rechecked at
https://www.erdosproblems.com/97 on 2026-07-02; the page
reports last edited 2025-10-27. This packet does not
prove Erdos Problem #97, does not claim a counterexample, and does not
promote any n=9 or n=10 artifact. It isolates the n <= 8 selected-witness
finite-case evidence for external review.

## Problem And Selected Witnesses

A bad polygon would have vertices p_0,...,p_{n-1} such that for every
center i there are four other vertices at one common distance from
p_i. Choosing one such 4-set S_i at every center gives the
selected-witness formulation. Ruling out all selected-witness systems
for a fixed n rules out bad polygons with that n, because any bad
polygon supplies at least one selected row at each center.

## Lemma Library L1-L10

L1. Selected-witness extraction: every bad polygon supplies one
selected 4-row S_i at each center.

L2. Two-circle cap: for distinct centers a,b, |S_a cap S_b| <= 2,
since two distinct circles share at most two points.

L3. Witness-pair capacity: a fixed unordered witness pair can occur in
at most two selected rows, because all such centers lie on the
perpendicular bisector of that pair.

L4. Crossing-bisector rule: if two rows share exactly two witnesses,
the center chord is the perpendicular bisector of the common-witness
chord, and the two chords cross at the midpoint.

L5. Sharpened count: L2-L4 rule out selected-witness counterexamples
for n <= 7; the retained n=7 Fano enumeration independently audits the
equality case.

L6. n=8 indegree regularity: the witness-pair capacity forces every
witness label to have selected indegree exactly 4.

L7. n=8 incidence enumeration: with row 0 fixed to {1,2,3,4} by
relabeling, exact enumeration leaves 15 canonical survivor classes.

L8. Forced geometry equations: two-overlap rows generate exact
perpendicular-bisector equations; selected rows generate exact
equal-distance equations.

L9. Survivor obstruction: class 12 has no compatible cyclic order; ten
classes are killed by rational y_2 span certificates; classes 3, 4, 5,
and 14 are killed by the named duplicate, collinearity, Groebner, and
strict-interior certificates.

L10. Independent cross-checks: a SymPy-free rational recheck covers 11
classes, and an order-free z3 nonlinear-real-arithmetic replay finds
all 15 classes UNSAT for strictly convex octagon realization.

## Finite-Case Theorem Under Review

Claim under review. In the selected-witness formulation, no strictly
convex counterexample exists for n <= 8.

Proof sketch. L5 excludes n <= 7. For n=8, L6 reduces the incidence
layer to regular 4-in/4-out selected-witness systems. L7 exhausts the
resulting necessary incidence systems and reduces them to 15 canonical
classes. L8 translates every survivor into exact algebraic and
cyclic-order constraints. L9 kills all 15 classes with exact checks.
L10 gives two independent defensive replays. Therefore the repository
has a machine-checked finite-case artifact for n <= 8, subject to the
stated review boundary.

## Reproduction Commands

```bash
python scripts/independent_check_n8_artifacts.py --check --json
python scripts/enumerate_n8_incidence.py --summary
python scripts/analyze_n8_exact_survivors.py --check --json
python scripts/independent_n8_obstruction_recheck.py --check --json
python scripts/check_n8_class14_certificate.py --check --json
python scripts/check_n8_residual_certificates.py --check --json
python scripts/check_n8_survivors_smt.py --assert-clear --check-artifact data/certificates/n8_survivors_smt.json
```

## Expected Stable Invariants

The incidence enumeration reports 117072 balanced cap matrices with
row 0 fixed, 4560 forced-perpendicular survivors with row 0 fixed, and
15 canonical survivor classes. The exact survivor checker rejects all
15 classes. The SymPy-free recheck kills classes
0,1,2,6,7,8,9,10,11,12,13 and explicitly leaves 3,4,5,14 to the
focused Groebner-dependent audit path. The z3 SMT cross-check reports
all 15 survivor classes UNSAT for strictly convex realization.

## Reviewer Boundary

The reviewer should check the geometric lemmas, the row-0 relabeling
symmetry break, the exact incidence filters, and the exact certificate
replays for classes 3, 4, 5, and especially 14. A successful review may
support paper-style use of the n <= 8 finite-case result. It would not
update the official/global status and would not settle any case n >= 9.
