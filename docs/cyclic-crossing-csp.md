# Cyclic crossing CSP for two-overlap patterns

Status: finite exact cyclic-order obstruction.

No general proof of Erdos Problem #97 is claimed. No counterexample is claimed.

## Input

The input is a selected-witness incidence pattern: one 4-set `S_i` for each
center label `i`.

## Constraints

For every row-pair `{i,j}` with

```text
|S_i cap S_j| = 2,
```

define

```text
phi({i,j}) = S_i cap S_j.
```

The crossing-bisection lemma requires the source chord `{i,j}` to cross the
target chord `phi({i,j})` in any proposed cyclic order.

## Exact Search

The checker in `scripts/check_cyclic_crossing_csp.py` performs a deterministic
insertion search. It fixes the first required crossing up to rotation and
reversal, then recursively inserts unplaced labels into circular gaps. A branch
is rejected only when all four endpoints of a crossing constraint have been
placed and the source and target chords do not cross.

The first constraint is chosen by deterministic tuple ordering of the `phi`
constraints. A crossing of two disjoint chords has exactly two circular endpoint
embeddings up to rotation and reversal, so the two seeded orders cover all
symmetry classes for any satisfying cyclic order.

The search uses exact finite combinatorics only. It does not use coordinates or
floating point.

Routine JSON output caps retained terminal conflict traces by default. Certificate
runs may pass `--full-conflicts` when a full deterministic trace is desired.

## P18_parity_balanced

`P18_parity_balanced` is killed in natural order by adjacent-row two-overlap via
the crossing-bisection lemma. It survives the arbitrary-order crossing-only
filter. One compatible cyclic order is:

```text
0,8,4,15,1,5,11,9,3,7,17,13,2,6,14,10,16,12
```

Thus crossing constraints alone do not kill the abstract incidence pattern.
The stronger crossing plus vertex-circle strict-cycle search now kills it as a
fixed selected-witness abstract incidence pattern; see
`docs/vertex-circle-order-filter.md` and
`data/certificates/p18_vertex_circle_order_unsat.json`.

## P24_parity_balanced

`P24_parity_balanced` is killed in natural order by adjacent-row two-overlap via
the crossing-bisection lemma. As an abstract incidence pattern, it has 36
two-overlap crossing constraints.

The deterministic crossing CSP proves that no cyclic order of the 24 labels
satisfies all 36 required crossings. The certificate is stored at
`data/certificates/p24_cyclic_crossing_unsat.json`.

This is an exact finite cyclic-order obstruction for the fixed selected pattern.
