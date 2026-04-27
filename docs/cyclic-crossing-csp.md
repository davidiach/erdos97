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

The search uses exact finite combinatorics only. It does not use coordinates or
floating point.

## P18_parity_balanced

`P18_parity_balanced` is killed in natural order by adjacent-row two-overlap via
the crossing-bisection lemma. It survives the current arbitrary-order crossing
filters. One compatible cyclic order is:

```text
0,8,4,15,1,5,11,9,3,7,17,13,2,6,14,10,16,12
```

Thus the abstract-incidence status remains unresolved
algebraically/geometrically; `P18_parity_balanced` is not globally archived as
killed.

## P24_parity_balanced

`P24_parity_balanced` is killed in natural order by adjacent-row two-overlap via
the crossing-bisection lemma. As an abstract incidence pattern, it has 36
two-overlap crossing constraints.

The deterministic crossing CSP proves that no cyclic order of the 24 labels
satisfies all 36 required crossings. The certificate is stored at
`data/certificates/p24_cyclic_crossing_unsat.json`.

This is an exact finite cyclic-order obstruction for the fixed selected pattern.
