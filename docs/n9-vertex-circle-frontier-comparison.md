# n=9 Vertex-circle Frontier Comparison

Status: `REVIEW_PENDING_DIAGNOSTIC`.

This note compares the `n=9` local-core motifs with two larger fixed-pattern
frontier checks: the P18 pattern killed by the vertex-circle filter and the
recorded `C19_skew` order that passes it. It does not claim a general proof of
Erdos Problem #97 and does not claim a counterexample. The official/global
status remains falsifiable/open.

## Exact Core Embeddings

Using a strict cyclic-order-preserving row match, no checked `n=9` local core
embeds exactly into either recorded larger pattern:

```text
P18_parity_balanced: 0 exact n=9 local-core embeddings
C19_skew:            0 exact n=9 local-core embeddings
```

Here "exact" means that every selected row in the local core maps to a selected
row with exactly the same four selected witnesses. This is intentionally strict;
it prevents treating the n=9 cores as a general theorem by wishful analogy.

## P18 And C19

The P18 order recorded in `docs/vertex-circle-order-filter.md` is still killed
by a local strict-cycle core:

```text
P18 local core size: 6 selected rows
P18 vertex support: 14 vertices
P18 strict-cycle span signature: [[2,1], [3,1]]
matching n=9 strict-cycle span bucket count: 8
```

So P18 does not literally contain one of the n=9 local cores, but it does share
one of the same coarse strict-cycle span shapes.

The recorded `C19_skew` order still passes the vertex-circle filter, although
the fixed abstract pattern is now killed by the separate all-order Z3 Kalmanson
certificate. This remains the guardrail for the proof route: the current
quotient-graph vertex-circle obstruction is not enough by itself.

## Reproduction

Generate and check the comparison artifact:

```bash
python scripts/compare_n9_vertex_circle_frontier.py \
  --assert-expected \
  --write
```

Run the targeted artifact test:

```bash
python -m pytest tests/test_n9_vertex_circle_frontier_comparison.py -q
```
