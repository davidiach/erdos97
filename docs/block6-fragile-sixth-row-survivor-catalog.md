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

## Low-support Eighth-row Audit

Extending the same low-support branch one row deeper gives a mixed result. The
branch still does not close globally: `2240` of the `2252` clean seven-row
states have at least one clean eighth-row continuation. But `12` clean
seven-row states are terminal at the eighth-row level: every legal eighth row
after them forces a vertex-circle self-edge or strict cycle.

```text
legal eighth rows from low-support clean seven states: 97982
vertex-circle-clean:                           31636
self-edge obstruction:                          30272
strict-cycle obstruction:                       36074
clean seven-row states with clean eighth row:    2240 / 2252
terminal clean seven-row states:                   12
unique clean eight-row states:                  15740
```

The terminal states are distributed across the seven-center triples as follows:

```text
seven centers  clean seven  terminal at eighth row
1,4,5          160          0
1,10,11        71           0
2,4,5          283          2
2,10,11        362          1
4,5,7          71           0
4,5,8          362          1
4,5,10         95           0
4,5,11         155          3
4,10,11        95           0
5,10,11        155          3
7,10,11        160          0
8,10,11        283          2
```

One explicit clean eight-row state is:

```text
1  -> {0,2,7,11}
8  -> {0,5,7,9}
10 -> {0,1,6,9}
11 -> {2,5,6,10}
```

One explicit terminal clean seven-row state is:

```text
2  -> {0,1,6,11}
10 -> {0,4,6,9}
11 -> {3,5,6,7}
```

For that terminal state, there are `9` legal eighth rows: `7` force a
self-edge and `2` force a strict cycle. Thus the eighth-row audit supplies
small terminal pockets but still does not produce a full low-support closure
theorem.

## Terminal Seven-row Classification

The `12` terminal clean seven-row states form exactly `6` orbits under the
block-swap symmetry `i -> i+6 mod 12`; every orbit has size `2`.

For each terminal state, split each added row into the two witnesses in the
same block as its center and the two witnesses in the opposite block. The
terminal row-content profiles are exactly:

```text
profile                                      terminal states  block-swap orbits
same union 5, intersections 0,0,1;
  opposite union 6, intersections 0,0,0      8                4
same union 4, intersections 0,1,1;
  opposite union 5, intersections 0,0,1      4                2
```

The terminal eighth-row obstruction splits are:

```text
legal eighth rows  self-edge  strict-cycle  terminal states
9                  7          2             4
19                 10         9             2
9                  4          5             2
9                  5          4             2
11                 2          9             2
```

One representative from each block-swap orbit is:

```text
2  -> {0,1,6,11}; 10 -> {0,4,6,9}; 11 -> {3,5,6,7}  | legal 9, self 7, cycle 2
2  -> {1,5,6,7};  4  -> {0,3,6,10}; 5  -> {0,1,8,11} | legal 19, self 10, cycle 9
2  -> {1,5,6,7};  4  -> {0,3,6,10}; 5  -> {0,1,9,11} | legal 9, self 4, cycle 5
4  -> {0,3,6,10}; 5  -> {0,1,9,11}; 11 -> {0,5,6,7}  | legal 9, self 7, cycle 2
4  -> {0,3,8,11}; 5  -> {0,1,6,9};  11 -> {3,5,6,7}  | legal 9, self 5, cycle 4
4  -> {0,3,9,11}; 5  -> {0,1,6,10}; 11 -> {3,5,6,7}  | legal 11, self 2, cycle 9
```

Applying the block-swap map to these six representatives gives the other six
terminal states. This classification is useful as a proof-mining target: a
terminality lemma must use more than the seven-center triple, but may only need
the two row-content profiles above plus one short list of boundary variants.

## Profile-only Terminality Audit

The two terminal row-content profiles are not sufficient by themselves. Among
the `2252` clean seven-row states, `192` do not split every added row into
two same-block and two opposite-block witnesses; all `192` are extendable at
the eighth-row level.

The remaining `2060` two-and-two clean seven-row states have exactly `6`
row-content profiles. The two profiles that contain terminal states also
contain many extendable states:

```text
profile summary                              clean states  terminal  extendable
same u4, i011;  opposite u5, i001          320           4         316
same u5, i001;  opposite u6, i000          1230          8         1222
```

Here `u` is the union size of the three same-block or opposite-block pairs,
and `i` is the sorted pairwise-intersection multiset. Thus any terminality
lemma for these pockets needs finer boundary data than this coarse
same/opposite-block profile.

A clean extendable state with the first terminal profile is:

```text
1 -> {3,5,6,7}
4 -> {0,3,6,9}
5 -> {0,4,8,11}
```

A clean extendable state with the second terminal profile is:

```text
1  -> {0,2,7,11}
10 -> {0,1,6,9}
11 -> {2,5,6,10}
```

One clean extendable state outside the two-and-two profile domain is:

```text
2 -> {0,1,3,7}
4 -> {0,3,6,9}
5 -> {0,4,8,11}
```

## Terminal Eighth-center Split Audit

A finer terminal-pocket audit splits the legal eighth-row candidates by their
eighth center before applying the vertex-circle status test. Across the `12`
terminal clean seven-row states there are `132` legal eighth rows, all
obstructed:

```text
eighth center  self-edge  strict-cycle
1              7          20
2              14         8
4              12         3
5              2          0
7              7          20
8              14         8
10             12         3
11             2          0
```

Thus no terminal pocket has a hidden clean eighth continuation after center
splitting. The center-level obstruction profiles across the `12` terminal
states are:

```text
self-only centers  strict-only centers  mixed centers  terminal states
3                  1                    0              4
1                  0                    4              2
1                  1                    2              2
1                  3                    1              2
0                  3                    1              2
```

The first block-swap orbit representative has the split:

```text
2  -> {0,1,6,11}; 10 -> {0,4,6,9}; 11 -> {3,5,6,7}

eighth center  self-edge  strict-cycle
1              2          0
4              2          0
7              0          2
8              3          0
```

The remaining orbit representatives are recorded by the checker output under
`low_support_terminal_eighth_center_audit`. The split is equivariant under the
block-swap map `i -> i+6 mod 12`.

## Triple-plus-profile Terminality Audit

Adding the seven-center triple to the row-content profile is still not enough
to force terminality. Among the `2060` two-and-two clean seven-row states,
there are `26` combined `(seven-center triple, row-content profile)` classes.
The `12` terminal states occupy `6` of those classes, and every one of those
`6` classes also contains extendable states:

```text
seven centers  terminal  extendable
2,4,5          2         118
2,10,11        1         293
4,5,8          1         293
4,5,11         3         152
5,10,11        3         152
8,10,11        2         118
```

Thus terminality is not determined by the seven-center triple together with
the same/opposite-block row-content profile. The checker records one terminal
and one extendable example in each terminal-containing combined class under
`low_support_triple_profile_terminality_audit`.

## Terminal-to-extendable Edit-distance Audit

Within each terminal-containing triple/profile class, terminality is fragile:
every terminal state is one witness replacement away from an extendable state
in the same class.

The row replacement distance between two clean seven-row states with the same
centers is

```text
sum over added centers c of |row_T(c) triangle row_E(c)| / 2.
```

The exact minimum replacement distribution for the `12` terminal states is:

```text
minimum replacements  terminal states
1                     12
```

For the nearest extendable states chosen by the checker, the changed-row count
is also concentrated:

```text
changed rows in nearest example  terminal states
1                                12
```

The number of nearest extendable states varies:

```text
nearest extendable states  terminal states
1                          2
3                          2
5                          2
6                          4
7                          2
```

Across all nearest terminal-to-extendable transitions, there are `56`
one-replacement transitions. The changed center distribution is block-swap
equivariant:

```text
changed center orbit  nearest transitions
2,8                   14
4,10                  8
5,11                  34
```

The replacement preserves whether the changed witness lies in the center's
same six-label block or in the opposite six-label block. The side split is:

```text
replacement side  nearest transitions
same block        14
opposite block    42
```

The nearest extendable states have only a small number of clean eighth-center
choices:

```text
clean eighth centers after nearest transition  nearest transitions
1                                              28
2                                              24
3                                              4
```

Across those `56` transitions, the opened clean eighth-center choices give
`88` transition-center incidences. Their block-swap orbit distribution is:

```text
opened eighth center orbit  incidences
1,7                         8
2,8                         46
4,10                        30
5,11                        4
```

Relative to the terminal state's legal eighth rows, the opened centers had
these prior status types:

```text
prior status  incidences
self only     30
mixed         30
strict only   22
not legal     6
```

Here `self only` means all legal eighth rows at that center failed by quotient
self-edge, `strict only` means all failed by strict cycle, and `mixed` means
both failure types appeared. The `not legal` cases were not legal eighth
centers at all before the one-row replacement. Only `4` transitions open the
added witness label and only `4` open the removed witness label; the other
`48` transitions open neither replacement label. Thus the one-row escape is
usually indirect rather than a replacement simply opening its own label.

The `6` not-legal openings all occur at centers in the block-swap orbit
`2,8`. They are not caused by the pair-cap or indegree-cap filters. Before
the one-row replacement, the opened center has zero pair/crossing-admissible
rows; after the replacement it has either `7` or `8` pair/crossing-admissible
rows, all of which also pass the pair-cap and indegree-cap filters:

```text
pair/crossing profile                       not-legal openings
before=0, after=7, after fully valid=7      2
before=0, after=8, after fully valid=8      4
```

Against the changed row, the `46` after-valid candidate rows had the following
before/after crossing relations:

```text
relation before replacement  candidate rows
noncrossing two-overlap       44
three-or-more overlap          2

relation after replacement   candidate rows
zero-or-one overlap           36
crossing two-overlap          10
```

So the previously not-legal openings are pure crossing-gate switches: the
replacement either destroys a forbidden noncrossing two-overlap or changes it
into an allowed crossing two-overlap.

The switch is even more rigid. Every one of the `46` before-replacement
forbidden overlaps contains the removed witness endpoint. Among the `44`
noncrossing two-overlaps, the old target chord is always contained in a
non-short side of the source chord `(changed center, opened center)`: `30`
lie in the long open arc and `14` lie in one of the two equal arcs of the
diameter source `2,8`. None lie in a short open arc.

```text
source -> old target chord  candidate rows
2,10 -> 3,5                5
2,10 -> 3,6                2
2,5  -> 0,11               2
2,5  -> 1,11               6
2,8  -> 0,11               2
2,8  -> 1,11               5
2,8  -> 5,6                2
2,8  -> 5,7                5
4,8  -> 0,9                2
4,8  -> 9,11               5
8,11 -> 5,6                2
8,11 -> 5,7                6
```

For those `44` noncrossing two-overlaps, omitting the added endpoint gives
`36` zero/one-overlap rows after replacement, while containing the added
endpoint gives `8` crossing two-overlap rows. The remaining `2`
three-or-more overlaps also contain the removed endpoint and collapse to
crossing two-overlaps after replacement.

The `8` noncrossing-to-crossing switches are exactly removed-to-added
substitutions: the candidate row already contains the added endpoint, and the
surviving old target endpoint and added endpoint lie in opposite source arcs.

```text
source: old target -> new target  candidate rows
2,10: 3,5 -> 1,5                 3
2,10: 3,6 -> 1,6                 1
4,8: 0,9 -> 0,7                  1
4,8: 9,11 -> 7,11                3
```

The other `36` noncrossing two-overlaps are deletions: the candidate row omits
the added endpoint, so removing the active endpoint leaves at most one common
witness with the changed row. The `2` three-or-more cases are a second
crossing-creation mechanism: deleting the removed endpoint leaves the crossing
target `1,7` across source `2,8`.

This opposite-arc conclusion is forced by the pair/cross gate, not by raw row
availability alone. In general, suppose a one-witness replacement changes row
`R` to `R' = R - {r} + {a}`, an opened candidate row `Q` has old overlap
`R cap Q = {r,s}`, and `Q` contains the added endpoint `a`. Then
`R' cap Q = {a,s}`. If `a` and `s` lie in the same source arc of the chord
joining the changed center to the opened center, the new target chord
`{a,s}` is noncrossing. Since after-valid rows have already passed the
pair/cross gate against `R'`, this same-arc substitution is impossible in the
after-valid layer. The exact audit records the boundary:

```text
substitution layer and arc relation                         candidate rows
all options, same source arc -> noncrossing two-overlap      60
all options, opposite source arcs -> crossing two-overlap    36
after pair/cross, opposite source arcs -> crossing two-overlap 8
after valid, opposite source arcs -> crossing two-overlap      8
```

For example, the terminal state

```text
2  -> {0,1,6,11}
10 -> {0,4,6,9}
11 -> {3,5,6,7}
```

has a nearest extendable state obtained by replacing witness `11` with `10`
in the row centered at `2`:

```text
2  -> {0,1,6,10}
10 -> {0,4,6,9}
11 -> {3,5,6,7}
```

Thus no terminality lemma can be stable under even one witness replacement
inside the same combined triple/profile class. The next useful invariant must
see the exact boundary-pair placement and changed-center orbit that
distinguishes those adjacent states.

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
`4,5` and `10,11` minimum-support center-pair families, and every legal
eighth row after the resulting `2252` clean seven-row states, including the
center-level split for the `12` terminal seven-row pockets and the
triple-plus-profile terminality and terminal-to-extendable edit-distance
audits.

## Effect

This rules out the next tempting local bridge reduction. The Cycle 640 closure
cannot be made into a fifth-row-only or sixth-row-only obstruction theorem.
The obstruction is still real, but it occurs deeper in the selected-row
extension tree. The center-pair normal-form audit also rules out a still
coarser six-row proof based only on which two nonfixed centers have been
selected. The minimum-support row-content audit gives a compact target for the
next step, but the seventh-row continuation audit shows that even this compact
target is not seventh-row-local. The eighth-row audit finds the first terminal
pockets inside the low-support branch, but most clean seven-row states still
continue.

The next useful step is to mine the `6047` clean six-row states for a smaller
row-content normal-form family, or to classify the `12` terminal seven-row
states by a boundary-pair invariant that distinguishes them from the `2240`
seven-row states that still extend cleanly. The eighth-center split rules out
the coarsest possible terminal explanation: terminality is not concentrated at
one eighth center or one obstruction type. The triple-plus-profile audit also
shows that terminality is not determined by adding the seven-center triple to
the row-content profile. The edit-distance audit sharpens this failure:
terminality can disappear after changing a single witness in one row while
staying inside the same combined class. The nearest-transition classification
also shows that the escapes are not explained by one exceptional changed
center: all three nonfixed block-swap center orbits occur.
