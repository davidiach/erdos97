# n=9 Vertex-circle T03 Self-edge Local Lemma Packet

Status: `REVIEW_PENDING_DIAGNOSTIC_ONLY`.

This note records one focused proof-mining packet for the multi-family `T03`
self-edge motif. It does not claim a proof of `n=9`, does not claim a
counterexample, does not complete independent review of the exhaustive
checker, and does not update the official/global status.

## Packet scope

The checked artifact is
`data/certificates/n9_vertex_circle_t03_self_edge_lemma_packet.json`.
It is derived from:

- `data/certificates/n9_vertex_circle_self_edge_template_packet.json`
- `data/certificates/n9_vertex_circle_template_lemma_catalog.json`

The packet covers 20 assignment ids across two families:

```text
F05: 18 assignments
F15:  2 assignments
```

Each family has a four-row core and replays to a single self-edge conflict
with 36 strict edges and no strict cycle. The selected-distance equality path
still has three steps, so reviewers should keep the four selected rows separate
from the three equality edges.

Here `[c, a, b, d, e]` means that `a,b,d,e` are the selected witnesses for
center `c`, hence the four distances from `c` to those witnesses are equal.

## Local lemma

The following local obstruction is independent of the exhaustive `n=9`
brancher once one of the displayed row cores is given.

Assume a strictly convex polygon has labels appearing in cyclic order

```text
0,1,2,3,4,5,6,7,8
```

and contains one of the two selected-row cores listed below. Then that row
core cannot be realized.

The geometric input used in both cases is the same. For a fixed center row,
the four selected witnesses lie on one circle centered at that row's vertex.
In a strictly convex polygon, the rays from a vertex to the other vertices
occur in polygon cyclic order inside an angle smaller than `pi`. Therefore,
on the row circle, chord length is strictly increasing with the enclosed
central angle in this range. If a chord strictly contains another chord in the
row witness order, then the containing chord has strictly larger ordinary
length.

For `F05`, the four selected rows are

```text
S_1 = {2,5,7,8}
S_2 = {1,3,4,8}
S_3 = {0,2,4,7}
S_6 = {1,3,5,7}.
```

The selected-distance equalities give

```text
d(3,7) = d(2,3)      from row 3,
d(2,3) = d(1,2)      from row 2,
d(1,2) = d(1,7)      from row 1.
```

Thus `d(3,7) = d(1,7)`. But row `6` has witness order

```text
7,1,3,5,
```

so the chord `[3,7]` strictly contains `[1,7]` in that row's witness order.
Vertex-circle monotonicity gives `d(3,7) > d(1,7)`, a contradiction.

For `F15`, the four selected rows are

```text
S_0 = {1,3,4,8}
S_1 = {0,2,4,5}
S_2 = {1,3,5,6}
S_3 = {2,4,6,7}.
```

The selected-distance equalities give

```text
d(1,4) = d(1,2)      from row 1,
d(1,2) = d(2,3)      from row 2,
d(2,3) = d(3,4)      from row 3.
```

Thus `d(1,4) = d(3,4)`. But row `0` has witness order

```text
1,3,4,8,
```

so the chord `[1,4]` strictly contains `[3,4]` in that row's witness order.
Vertex-circle monotonicity gives `d(1,4) > d(3,4)`, a contradiction.

Equivalently, in each family the selected-distance quotient identifies the
outer and inner chord lengths, while one row creates a strict edge from that
quotient class back to itself. This is a local obstruction only: it rules out
selected-witness systems containing one of these row cores in the stated
cyclic order. It does not prove the full `n=9` finite case, because the
exhaustive checker is still needed to show that every frontier assignment
contains one of the recorded local obstruction templates.

## Packet data

`F05`:

```text
[1, 2, 5, 7, 8]
[2, 1, 3, 4, 8]
[3, 0, 2, 4, 7]
[6, 1, 3, 5, 7]
strict: [3, 7] > [1, 7] from row 6
path:   [3, 7] -> [2, 3] -> [1, 2] -> [1, 7]
```

`F15`:

```text
[0, 1, 3, 4, 8]
[1, 0, 2, 4, 5]
[2, 1, 3, 5, 6]
[3, 2, 4, 6, 7]
strict: [1, 4] > [3, 4] from row 0
path:   [1, 4] -> [1, 2] -> [2, 3] -> [3, 4]
```

Thus the packet isolates a reusable-looking local self-edge shape: each family
forces a strict edge from a selected-distance quotient class back to itself.

## Commands

Generate and check the packet:

```bash
python scripts/check_n9_vertex_circle_t03_self_edge_lemma_packet.py \
  --assert-expected \
  --write

python scripts/check_n9_vertex_circle_t03_self_edge_lemma_packet.py \
  --check \
  --assert-expected \
  --json
```

Run the targeted artifact tests:

```bash
python -m pytest tests/test_n9_vertex_circle_t03_self_edge_lemma_packet.py -q -m "artifact"
```

The smaller mini-replay treats the checked packet as input data and replays
only the two local equality-chain/self-edge contradictions:

```bash
python scripts/check_n9_t03_self_edge_minireplay.py --check --assert-expected --json
```

## Review standard

Before treating this as a reusable local lemma, a reviewer should restate the
incidence and cyclic-order hypotheses without relying on `T03` as a theorem
name, then prove directly for each of the two family cores that the listed
rows force the displayed equality path and strict inequality. The packet is a
small replay aid for that review, not an independent proof of the `n=9` case.
