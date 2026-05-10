# Block-6 Fragile-cover Sixth-row Survivor Catalog

Status: `REVIEW_PENDING_DIAGNOSTIC_ONLY`.

This note records one bounded follow-up to the block-6 fifth-row catalog. It
does not claim a proof of Erdos Problem #97, does not claim a counterexample,
and does not update the official/global status.

## Subquestion

The fifth-row catalog found `166` legal one-row extensions of the two-block
block-6 fragile rows that remain vertex-circle-clean. The next narrow question
is:

```text
After a clean legal fifth row, does every legal sixth row immediately force a
vertex-circle quotient self-edge or strict cycle?
```

## Result

Counterexample to the sixth-row-only closure subclaim:
**Block-6 Sixth-row Survivor Catalog**.

Every one of the `166` clean fifth-row states has at least one legal sixth row
that remains vertex-circle-clean. In total, the ordered sixth-row
continuations from clean fifth-row states split as:

```text
ordered legal sixth rows after clean fifth rows: 29844
vertex-circle-clean:                         12094
self-edge obstruction:                        8108
strict-cycle obstruction:                     9642
```

After forgetting the order in which the two nonfixed rows were added, there
are `6047` distinct clean six-row states. Under the block-swap symmetry
`i -> i+6 mod 12`, these form `3056` orbits: `2991` two-element orbits and
`65` fixed orbits.

## Center-pair Normal Forms

The clean six-row states are not concentrated in a small set of added-center
pairs. Every one of the `28` unordered pairs of nonfixed centers supports at
least one clean six-row state. Under block-swap, these `28` pairs form `16`
center-pair orbits, and every orbit has positive clean support.

```text
center pair  clean states
1,2          350
1,4          98
1,5          126
1,7          256
1,8          508
1,10         69
1,11         105
2,4          182
2,5          238
2,7          508
2,8          1074
2,10         176
2,11         325
4,5          28
4,7          69
4,8          176
4,10         36
4,11         71
5,7          105
5,8          325
5,10         71
5,11         129
7,8          350
7,10         98
7,11         126
8,10         182
8,11         238
10,11        28
```

Thus no proof can close the two-block family at six rows using only the
unordered pair of added centers. The obstruction depends on finer row content.

## Minimum-support Row-content Normal Forms

The two minimum center pairs, `4,5` and `10,11`, do have a compact exact
row-content description. For `4,5`, the `28` clean states are exactly:

```text
4 -> {0,3} union A
5 -> {0,t} union B, where t in {1,4}
```

where `A` and `B` are ordered disjoint pairs from

```text
{6,7}, {6,9}, {6,10}, {7,11}, {8,11}, {9,11}.
```

This six-pair pool has `14` ordered disjoint pair edges, and the binary choice
of `t` gives `14 * 2 = 28` clean states.

By block-swap, the `10,11` family is exactly:

```text
10 -> {6,9} union A
11 -> {6,t} union B, where t in {7,10}
```

where `A` and `B` are ordered disjoint pairs from

```text
{0,1}, {0,3}, {0,4}, {1,5}, {2,5}, {3,5}.
```

Again all `14` ordered disjoint pair edges occur, with the binary choice of
`t`, giving `28` clean states.

## Low-support Seventh-row Continuations

The low-support disjoint-pair normal form still does not close at the next
row. Across the `56` block-swap-related clean six-row states from the `4,5`
and `10,11` minimum-support families, every clean six-row state has at least
one legal seventh row that remains vertex-circle-clean.

```text
legal seventh rows from low-support six states: 5590
vertex-circle-clean:                         2252
self-edge obstruction:                        1560
strict-cycle obstruction:                     1778
clean six-row states with clean seventh row:  56 / 56
```

For center pair `4,5`, the seventh-row split is `1126` clean, `780`
self-edge, and `889` strict-cycle. The block-swap-related `10,11` family has
the same aggregate split.

One explicit clean seven-row state extending the `4,5` minimum-support family
is:

```text
4 -> {0,3,6,9}
5 -> {0,4,7,11}
1 -> {2,5,6,7}
```

One explicit clean seven-row state extending the `10,11` minimum-support
family is:

```text
10 -> {0,4,6,9}
11 -> {3,5,6,7}
1  -> {0,2,7,11}
```

Together with the four fixed block-6 fragile rows, each displayed state
satisfies the checker incidence/order filters and has vertex-circle status
`ok` at the seven-row level. These are abstract selected-row states inside the
bounded natural-order audit; they are not Euclidean realizability claims.

## Center Counts

```text
fifth center  clean fifth  legal sixth  ok    self_edge  strict_cycle
1             21           3973         1512  1185       1276
2             41           7178         2853  1916       2409
4             7            1211         660   281        270
5             14           2560         1022  672        866
7             21           3973         1512  1185       1276
8             41           7178         2853  1916       2409
10            7            1211         660   281        270
11            14           2560         1022  672        866
```

One explicit clean six-row state is:

```text
1 -> {0,2,6,7}
2 -> {0,1,3,8}
```

Together with the four fixed block-6 fragile rows, these two rows satisfy the
listed incidence/order filters and have vertex-circle status `ok` at the
six-row level. This is only a counterexample to the sixth-row-only closure
subclaim, not to Erdos Problem #97.

## Reproduction

Run:

```bash
python scripts/check_block6_fragile_sixth_row_survivors.py \
  --assert-expected \
  --json
```

The checker first reconstructs the `166` clean fifth rows, then enumerates
every legal sixth row after each of them. It also computes the block-swap
orbits for the clean fifth-row and clean six-row states. Finally, it audits
every legal seventh row after the `56` low-support clean six-row states in the
`4,5` and `10,11` minimum-support center-pair families.

## Effect

This rules out the next tempting local bridge reduction. The Cycle 640 closure
cannot be made into a fifth-row-only or sixth-row-only obstruction theorem.
The obstruction is still real, but it occurs deeper in the selected-row
extension tree. The center-pair normal-form audit also rules out a still
coarser six-row proof based only on which two nonfixed centers have been
selected. The minimum-support row-content audit gives a compact target for the
next step, but the seventh-row continuation audit shows that even this compact
target is not seventh-row-local.

The next useful step is to mine the `6047` clean six-row states for a smaller
row-content normal-form family, or to extend the `56` low-support branches one
more row to ask where the disjoint-pair survivor family first becomes forced
into a quotient obstruction.
