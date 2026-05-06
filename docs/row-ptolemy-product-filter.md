# Row-Ptolemy Product Filter

Status: `EXACT_OBSTRUCTION` for fixed selected-witness patterns with a supplied
or certified row witness order. The generated n=9 sweep is exploratory
bookkeeping only; it is not a proof of `n=9`, not a counterexample, not a
geometric realizability test, and not a global status update.

## Lemma

Let one selected row have center `i` and four distinct witnesses
`w0,w1,w2,w3` in cyclic order around `i`. Because the witnesses lie on the
circle centered at `i`, Ptolemy's theorem gives

```text
d02*d13 = d01*d23 + d03*d12,
```

where `dab` denotes the Euclidean distance `|w_a w_b|`.

If the selected-distance quotient forces

```text
d02 = d23
d13 = d01
```

then substituting into Ptolemy cancels the left product with the first product
on the right, leaving `d03*d12 = 0`. That is impossible for distinct vertices
in a strictly convex polygon. Thus the fixed selected-witness pattern is
obstructed under the supplied row order.

The row order is part of the hypothesis. The selected-distance quotient alone
does not determine which witness pairs are sides and diagonals in Ptolemy, so
this is not an orderless abstract-incidence obstruction unless all compatible
orders have been checked separately.

## n=9 Sweep

The artifact
`data/certificates/n9_row_ptolemy_product_cancellations.json` applies the
filter to the 184 complete `n=9` selected-witness assignments that survive the
pair/crossing/count filters before the vertex-circle filter.

It records:

- `26` hit assignments out of `184`;
- `216` row-local certificates after checking all cyclic rotations of the row
  Ptolemy cancellation;
- `3` deterministic dihedral family labels: `F02`, `F09`, and `F13`;
- all hits are vertex-circle `self_edge` cases in the current n=9 frontier.

This gives an independent Ptolemy-equality certificate for those fixed-order
assignments, but it does not dominate or replace the vertex-circle checker and
does not prove the full `n=9` finite case.

## Reproduction

```bash
python scripts/analyze_n9_row_ptolemy_product_cancellations.py \
  --assert-expected \
  --out data/certificates/n9_row_ptolemy_product_cancellations.json

python scripts/check_n9_row_ptolemy_product_cancellations.py --check --json
```
