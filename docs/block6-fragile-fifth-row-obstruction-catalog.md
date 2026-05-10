# Block-6 Fragile-cover Fifth-row Obstruction Catalog

Status: `REVIEW_PENDING_DIAGNOSTIC_ONLY`.

This note records one bounded proof-mining audit for the two-block block-6
fragile-cover family. It does not claim a proof of Erdos Problem #97, does
not claim a counterexample, and does not update the official/global status.

## Subquestion

Cycle 640 showed that the two-block block-6 fragile-cover family has no full
selected-witness extension surviving the vertex-circle quotient filter in the
natural cyclic order.

The narrow follow-up question is whether that closure can already be reduced
to a one-step local lemma:

```text
After fixing the four block-6 fragile rows, does every legal fifth selected
row immediately force a vertex-circle quotient self-edge or strict cycle?
```

## Definitions

Use the same two-block fixed rows as the extension audit:

```text
0 -> {1,2,3,4}
3 -> {0,2,4,5}
6 -> {7,8,9,10}
9 -> {6,8,10,11}
```

A legal fifth row is a four-set at one remaining center that satisfies, with
respect to the four fixed rows:

- self-exclusion and row size 4;
- pairwise selected-row intersection at most 2;
- radical-axis crossing for every two-overlap;
- witness-pair multiplicity at most 2;
- selected indegree at most `floor(2*(12-1)/(4-1)) = 7`.

Its vertex-circle status is computed from the selected-distance quotient and
proper-interval strict edges of just those five selected rows in the natural
cyclic order.

## Result

Counterexample to the one-step local-closure subclaim:
**Block-6 Fifth-row Survivor Catalog**.

There are exactly `342` legal fifth rows. Of these, `176` already force a
vertex-circle quotient obstruction, but `166` remain vertex-circle-clean at
the five-row level.

```text
total legal fifth rows: 342
vertex-circle-clean:   166
self-edge obstruction:  82
strict-cycle obstruction: 94
```

Thus the Cycle 640 closure cannot be rewritten as the statement that every
legal fifth row already closes. Later rows are genuinely needed for the
surviving fifth-row states.

## Center Counts

```text
center  legal  ok  self_edge  strict_cycle
1       38     21  7          10
2       64     41  13         10
4       38     7   14         17
5       31     14  7          10
7       38     21  7          10
8       64     41  13         10
10      38     7   14         17
11      31     14  7          10
```

One explicit legal fifth-row survivor is:

```text
5 -> {0,1,6,7}
```

With the four fixed rows above, this row satisfies the listed incidence/order
necessary conditions and has vertex-circle status `ok` at the five-row level.
It is only a counterexample to the one-step local-closure subclaim, not to
Erdos Problem #97.

## Reproduction

Run:

```bash
python scripts/check_block6_fragile_fifth_row_obstructions.py \
  --assert-expected \
  --json
```

The checker enumerates all legal fifth rows from the fixed two-block state and
asserts the center counts and totals above. To print every row classification,
add `--include-rows`.

## Effect

This audit sharpens the Cycle 640 bridge lead. It shows that a proof-facing
block-6 closure lemma cannot stop at the first connector row. However, it also
shows that more than half of the legal fifth rows already close by the same
quotient-obstruction mechanism, giving a small exact catalog for the next
normal-form step.

The next useful reduction is to classify the `166` clean fifth-row states by
symmetry and then ask whether every clean state closes after a sixth row, or
whether a small family of clean normal forms persists deeper into the search.
