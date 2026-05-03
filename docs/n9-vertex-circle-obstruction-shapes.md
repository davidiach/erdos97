# n=9 Vertex-circle Obstruction Shapes

Status: `REVIEW_PENDING_DIAGNOSTIC`.

This note mines the complete `n=9` selected-witness assignments that survive
the pair, crossing, indegree, and witness-pair count filters before the
vertex-circle filter is applied. It does not claim a general proof of Erdos
Problem #97 and does not claim a counterexample. The official/global status
remains falsifiable/open.

## Result

The diagnostic enumerates the same 184 pre-vertex-circle assignments recorded
by `docs/n9-vertex-circle-exhaustive.md` and classifies the first
vertex-circle obstruction in each assignment.

Checked counts:

```text
pre-vertex-circle full assignments: 184
self-edge contradictions: 158
strict directed cycles: 26
strict cycle lengths: 22 of length 2, 4 of length 3
self-edge equality path lengths: 92 length-3, 41 length-4, 14 length-5,
  6 length-6, 4 length-7, 1 length-8
```

The checked-in diagnostic artifact is
`data/certificates/n9_vertex_circle_obstruction_shapes.json`.

## Why this matters

The obstruction shapes are small enough to point at a plausible general proof
target. Quotient all ordinary pair distances by the selected-distance
equalities. Each selected row then contributes strict directed inequalities
between quotient classes whenever one witness-witness chord properly contains
another in the vertex-circle angular order.

A realized bad configuration would need this strict graph to be irreflexive and
acyclic. The `n=9` frontier instead always forces either:

- a self-edge, meaning a strict chord-containment inequality inside one
  selected-distance class; or
- a directed strict cycle, which is impossible for real distances.

This suggests the next lemma to hunt:

```text
For sufficiently constrained selected-witness incidence systems, the
distance-class quotient graph forced by vertex-circle interval containment has
a self-edge or directed cycle.
```

That lemma is not proved here. The existing `C19_skew` caveat in
`docs/vertex-circle-order-filter.md` shows that the current vertex-circle
quotient graph alone is not enough for a global solution. The likely proof path
is to combine this quotient-graph obstruction with stronger order information,
Altman/Kalmanson inequalities, or radius propagation.

## Reproduction

Generate and check the diagnostic artifact:

```bash
python scripts/analyze_n9_vertex_circle_obstruction_shapes.py \
  --assert-expected \
  --write
```

Run the targeted artifact test:

```bash
python -m pytest tests/test_n9_vertex_circle_obstruction_shapes.py -q
```

## Review questions

- Are the mined self-edge equality paths exposing a common incidence motif, or
  are they merely shortest paths in a dense selected-distance equality graph?
- Can the length-2 and length-3 strict cycles be described by a small set of
  cyclic-order templates?
- Which extra condition rules out the known `C19_skew` vertex-circle survivor:
  Altman diagonal sums, Kalmanson inequalities, radius propagation, or a
  sharper vertex-circle inequality?
