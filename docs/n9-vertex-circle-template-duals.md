# n=9 Vertex-Circle Template Dual Certificates

Status: `REVIEW_PENDING_DIAGNOSTIC_ONLY`.

This note consolidates the sixteen stored `n=9` vertex-circle relation
skeletons into exact positive-circuit identities. It is a proof-mining and
review artifact. It does not force any skeleton in an arbitrary polygon, does
not prove `n=9`, does not prove Erdos Problem #97, and does not claim a
counterexample. The official/global status remains falsifiable/open.

## Result

For every one of the sixteen stored relation skeletons, the checker constructs
an exact identity

```text
sum(strict distance differences)
  + sum(signed selected-row equality differences)
  = 0.
```

Every strict term has coefficient `1`. Every equality multiplier is `+1` or
`-1`. Since each strict term is positive and every selected-row equality term
vanishes, the identity is an exact `0 > 0` contradiction.

Checked counts:

```text
relation skeletons:                    16
local templates:                       12
dihedral families:                     16
covered frontier assignments:         184

strict-term counts per certificate:
  1 term:                              13
  2 terms:                              1
  3 terms:                              2

equality-term counts per certificate:
  3 terms:                             11
  4 terms:                              3
  5 terms:                              1
  6 terms:                              1

maximum active ordinary pair distances: 7
active-variable quotient partitions:   2451
```

The checked artifact is
`data/certificates/n9_vertex_circle_template_duals.json`.

## The dual identity

Write `d_ab` for the ordinary distance between labels `a` and `b`. A stored
vertex-circle strict edge contributes

```text
d_outer - d_inner > 0.
```

A selected row centered at `c` identifies the four distances from `c` to its
witnesses. An oriented equality-path step therefore contributes

```text
d_left - d_right = 0.
```

For a self-edge skeleton, the equality path joins the outer pair to the inner
pair. Subtracting that path from the one strict inequality gives the zero
coefficient vector.

For a directed-cycle skeleton, each equality path joins the inner pair of one
strict edge to the outer pair of the next. Adding the strict edges and the
oriented connector paths telescopes around the cycle. The result is again the
zero coefficient vector.

This is the linear-dual form of the quotient self-edge or directed-cycle
argument. It records the contradiction in the original ordinary pair-distance
coordinates rather than only displaying the quotient graph.

## Quotient-stability lemma

The packet uses the following elementary lemma.

> If a finite system has an identity
> `sum_i a_i L_i + sum_j b_j E_j = 0`, where every `a_i > 0`, every
> `L_i > 0`, and every `E_j = 0`, then the system is infeasible. Adding more
> constraints or identifying additional variables preserves the certificate,
> provided the strict constraints remain valid.

The proof is immediate: the equality contribution is zero and the strict
contribution is positive, contradicting the displayed identity. Applying any
variable-identification map to the coefficient identity preserves zero
balance. If a strict edge collapses to one variable, it becomes the immediate
contradiction `0 > 0`.

Here “quotient” has a deliberately narrow meaning: additional identifications
among ordinary pair-distance variables. The result does not identify polygon
vertices, discard cyclic-order hypotheses, or establish new strict edges.

As a defensive computation, the checker enumerates all set partitions of the
active pair-distance variables in every certificate. There are `2451` such
partitions in total, and every coarsened coefficient balance remains zero. The
general algebraic argument above is the proof; the enumeration checks the
implementation and stored paths.

## Assignment-level replay

The frontier classification maps each of the `184` labelled assignments to
one canonical dihedral family. The checker inverts each dihedral label map,
transforms the corresponding family certificate back to the assignment, and
checks that:

- every transformed strict term is supported by a row in the stored compact
  assignment core;
- every transformed equality step is supplied by a stored selected row;
- the transformed ordinary-distance coefficient vector is exactly zero; and
- the family/template coverage is disjoint and totals `184` assignments.

The deterministic digest of the complete transformed-certificate replay is:

```text
c60ce8833bd4b2fa7ad32e2e034091966369a77553614fffc2226dc4a0edf3eb
```

This is a crosswalk over review-pending source artifacts. It does not
independently prove frontier coverage or the geometric vertex-circle lemma.

## What this changes

The local obstruction layer is now expressed in the form needed by a
duality-first or potential-search program:

```text
local hypotheses -> exact positive circuit -> quotient-stable contradiction.
```

In particular, a richer equality class cannot repair one of the sixteen
stored local obstructions. The unresolved bridge is not certificate stability;
it is proving that minimal-counterexample geometry supplies one of the local
hypothesis systems, or supplies a different global accumulating potential.

The scalable strict-cycle negative control remains decisive. It shows that the
current abstract bridge axioms do not force a universally bounded
vertex-circle certificate or a Kalmanson circuit using at most three
inequalities. This packet does not evade that control: it consolidates the
finite `n=9` terminal certificates but does not force them in the scalable
family.

## Reproduction

Generate and check the artifact:

```bash
python scripts/check_n9_vertex_circle_template_duals.py \
  --assert-expected \
  --write

python scripts/check_n9_vertex_circle_template_duals.py \
  --check \
  --assert-expected \
  --json
```

Run the focused tests:

```bash
python -m pytest tests/test_n9_vertex_circle_template_duals.py -q
```

## Source artifacts

- `data/certificates/relation_skeleton_catalog.json`
- `data/certificates/n9_vertex_circle_frontier_motif_classification.json`
- `docs/relation-skeleton-catalog.md`
- `docs/scalable-strict-cycle-bridge-control.md`
