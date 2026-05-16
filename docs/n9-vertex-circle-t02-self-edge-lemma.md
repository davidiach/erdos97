# n=9 Vertex-circle T02 Self-edge Local Lemma Packet

Status: `REVIEW_PENDING_DIAGNOSTIC_ONLY`.

This note records one focused proof-mining packet for the multi-family `T02`
self-edge motif. It does not claim a proof of `n=9`, does not claim a
counterexample, does not complete independent review of the exhaustive
checker, and does not update the official/global status.

## Packet scope

The checked artifact is
`data/certificates/n9_vertex_circle_t02_self_edge_lemma_packet.json`.
It is derived from:

- `data/certificates/n9_vertex_circle_self_edge_template_packet.json`
- `data/certificates/n9_vertex_circle_template_lemma_catalog.json`

The packet covers 40 assignment ids across four families:

```text
F01: 18 assignments
F04: 18 assignments
F08:  2 assignments
F14:  2 assignments
```

Each family has a three-row core and replays to a single self-edge conflict
with 27 strict edges and no strict cycle.

Here `[c, a, b, d, e]` means that `a,b,d,e` are the selected witnesses for
center `c`, hence the four distances from `c` to those witnesses are equal.

## Local lemma

The following local obstruction is independent of the exhaustive `n=9`
brancher once one of the displayed row cores is given.

Assume a strictly convex polygon has labels appearing in cyclic order

```text
0,1,2,3,4,5,6,7,8
```

and contains one of the four selected-row cores listed below. Then that row
core cannot be realized.

The geometric input used in every case is the same. For a fixed center row,
the four selected witnesses lie on one circle centered at that row's vertex.
In a strictly convex polygon, the rays from a vertex to the other vertices
occur in polygon cyclic order inside an angle smaller than `pi`. Therefore,
on the row circle, chord length is strictly increasing with the enclosed
central angle in this range. If the row witness order is `a,b,c,d`, then the
chord `[a,d]` strictly contains `[a,b]`, so `d(a,d) > d(a,b)`.

All four packet families are instances of this reusable five-label form. Let
`C,A,B,D,E` be distinct vertices of a strictly convex polygon, with
`A,B,D,E` occurring in that order in the vertex cone at `C`; the first and
last of these vertices may lie on the two boundary rays of the cone. Assume:

```text
center C selects A,B,D,E
center E selects A,C
center A selects B,C
```

Then the selected-distance equalities give

```text
|AE| = |CE| = |CA| = |AB|.
```

The first equality comes from the row at `E`, the second from the row at `C`,
and the third from the row at `A`. But row `C` puts `A,B,D,E` on one circle
centered at `C`, so the outer chord `AE` has strictly larger angular span
than the inner chord `AB`. Hence

```text
|AE| > |AB|,
```

contradicting the equality chain.

For `F01`, the three selected rows are

```text
S_0 = {1,2,3,8}
S_1 = {0,2,4,7}
S_8 = {0,1,4,5}.
```

The selected-distance equalities give

```text
d(1,8) = d(0,8)      from row 8,
d(0,8) = d(0,1)      from row 0,
d(0,1) = d(1,2)      from row 1.
```

Thus `d(1,8) = d(1,2)`. But row `0` has witness order

```text
1,2,3,8,
```

so vertex-circle monotonicity gives `d(1,8) > d(1,2)`, a contradiction.

For `F04`, the three selected rows are

```text
S_0 = {1,2,4,6}
S_1 = {0,2,3,5}
S_2 = {1,3,4,8}.
```

The selected-distance equalities give

```text
d(0,2) = d(0,1)      from row 0,
d(0,1) = d(1,2)      from row 1,
d(1,2) = d(2,3)      from row 2.
```

Thus `d(0,2) = d(2,3)`. But row `1` has witness order

```text
2,3,5,0,
```

so vertex-circle monotonicity gives `d(0,2) > d(2,3)`, a contradiction.

For `F08`, the three selected rows are

```text
S_0 = {1,2,4,8}
S_1 = {0,2,3,5}
S_8 = {0,1,3,7}.
```

The selected-distance equalities give

```text
d(1,8) = d(0,8)      from row 8,
d(0,8) = d(0,1)      from row 0,
d(0,1) = d(1,2)      from row 1.
```

Thus `d(1,8) = d(1,2)`. But row `0` has witness order

```text
1,2,4,8,
```

so vertex-circle monotonicity gives `d(1,8) > d(1,2)`, a contradiction.

For `F14`, the three selected rows are

```text
S_0 = {1,2,6,8}
S_1 = {0,2,3,7}
S_8 = {0,1,5,7}.
```

The selected-distance equalities give

```text
d(1,8) = d(0,8)      from row 8,
d(0,8) = d(0,1)      from row 0,
d(0,1) = d(1,2)      from row 1.
```

Thus `d(1,8) = d(1,2)`. But row `0` has witness order

```text
1,2,6,8,
```

so vertex-circle monotonicity gives `d(1,8) > d(1,2)`, a contradiction.

Equivalently, in each family the selected-distance quotient identifies the
outer and inner chord lengths, while one row creates a strict edge from that
quotient class back to itself. This is a local obstruction only: it rules out
selected-witness systems containing one of these row cores in the stated
cyclic order. It does not prove the full `n=9` finite case, because the
exhaustive checker is still needed to show that every frontier assignment
contains one of the recorded local obstruction templates.

## Packet data

`F01`:

```text
[0, 1, 2, 3, 8]
[1, 0, 2, 4, 7]
[8, 0, 1, 4, 5]
strict: [1, 8] > [1, 2] from row 0
path:   [1, 8] -> [0, 8] -> [0, 1] -> [1, 2]
```

`F04`:

```text
[0, 1, 2, 4, 6]
[1, 0, 2, 3, 5]
[2, 1, 3, 4, 8]
strict: [0, 2] > [2, 3] from row 1
path:   [0, 2] -> [0, 1] -> [1, 2] -> [2, 3]
```

`F08`:

```text
[0, 1, 2, 4, 8]
[1, 0, 2, 3, 5]
[8, 0, 1, 3, 7]
strict: [1, 8] > [1, 2] from row 0
path:   [1, 8] -> [0, 8] -> [0, 1] -> [1, 2]
```

`F14`:

```text
[0, 1, 2, 6, 8]
[1, 0, 2, 3, 7]
[8, 0, 1, 5, 7]
strict: [1, 8] > [1, 2] from row 0
path:   [1, 8] -> [0, 8] -> [0, 1] -> [1, 2]
```

Thus the packet isolates a reusable-looking local self-edge shape: each family
forces a strict edge from a selected-distance quotient class back to itself.

## Commands

Generate and check the packet:

```bash
python scripts/check_n9_vertex_circle_t02_self_edge_lemma_packet.py \
  --assert-expected \
  --write

python scripts/check_n9_vertex_circle_t02_self_edge_lemma_packet.py \
  --check \
  --assert-expected \
  --json
```

Run the targeted artifact tests:

```bash
python -m pytest tests/test_n9_vertex_circle_t02_self_edge_lemma_packet.py -q -m "artifact"
```

The smaller mini-replay treats the checked packet as input data and replays
only the four local equality-chain/self-edge contradictions:

```bash
python scripts/check_n9_t02_self_edge_minireplay.py --check --assert-expected --json
```

## Review standard

Before treating this as a reusable local lemma, a reviewer should restate the
incidence and cyclic-order hypotheses without relying on `T02` as a theorem
name, then prove directly for each of the four family cores that the listed
rows force the displayed equality path and strict inequality. The packet is a
small replay aid for that review, not an independent proof of the `n=9` case.
