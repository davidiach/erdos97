# n=9 Vertex-circle T09/F03 Self-edge Local Lemma

Status: `REVIEW_PENDING_DIAGNOSTIC_ONLY`.

This note records one focused proof-mining extraction for the `T09/F03`
self-edge motif. It does not claim a proof of `n=9`, does not claim a
counterexample, does not complete independent review of the exhaustive
checker, and does not update the official/global status.

## Packet scope

The checked focused artifact is
`data/certificates/n9_vertex_circle_t09_self_edge_lemma_packet.json`. It is
derived from:

- `data/certificates/n9_vertex_circle_self_edge_template_packet.json`
- `data/certificates/n9_vertex_circle_template_lemma_catalog.json`

The template covers 18 assignment ids:

```text
A003, A010, A017, A030, A033, A044, A049, A073, A107,
A108, A123, A130, A135, A142, A144, A160, A161, A169
```

All assignments belong to family `F03`. The canonical local core is the
six-row certificate:

```text
[0, 1, 2, 3, 8]
[1, 0, 3, 5, 7]
[2, 1, 3, 4, 6]
[3, 2, 4, 5, 8]
[4, 0, 3, 6, 8]
[8, 0, 1, 4, 7]
```

Here `[c, a, b, d, e]` means that `a,b,d,e` are the selected witnesses for
center `c`, hence the four distances from `c` to those witnesses are equal.

## Local lemma

The following local obstruction is independent of the exhaustive `n=9`
brancher once the displayed rows are given.

Assume a strictly convex polygon has labels appearing in cyclic order

```text
0,1,2,3,4,5,6,7,8
```

and contains the six selected rows

```text
S_0 = {1,2,3,8}
S_1 = {0,3,5,7}
S_2 = {1,3,4,6}
S_3 = {2,4,5,8}
S_4 = {0,3,6,8}
S_8 = {0,1,4,7}.
```

Then these six rows cannot be realized.

Indeed, the selected-distance equalities give

```text
d(1,3) = d(0,1)      from row 1,
d(0,1) = d(0,8)      from row 0,
d(0,8) = d(4,8)      from row 8,
d(4,8) = d(3,4)      from row 4,
d(3,4) = d(2,3)      from row 3,
d(2,3) = d(1,2)      from row 2.
```

Thus

```text
d(1,3) = d(1,2).
```

On the other hand, the selected witnesses of row `0` lie on one circle
centered at vertex `0`, and their radial order is

```text
1,2,3,8.
```

In a strictly convex polygon, the rays from a vertex to the other vertices
occur in polygon cyclic order inside an angle smaller than `pi`. On a fixed
circle, chord length is strictly increasing with the enclosed central angle in
this range. The chord `[1,3]` strictly contains the chord `[1,2]` in the
row-`0` witness order, so

```text
d(1,3) > d(1,2).
```

This contradicts the equality above. Equivalently, after quotienting ordinary
pair distances by the selected-distance equalities, row `0` creates a
reflexive strict edge for the quotient class of `[1,3]` and `[1,2]`.

The lemma is local: it rules out any selected-witness system containing these
six rows in the stated cyclic order. It does not prove the full `n=9` finite
case, because the exhaustive checker is still needed to show that every
frontier assignment contains one of the recorded local obstruction templates.

## Packet data

For row `0`, the witness order `[1, 2, 3, 8]` gives the strict
vertex-circle inequality

```text
[1, 3] > [1, 2]
```

The selected-distance equality path is:

```text
[1, 3] -- row 1 --> [0, 1]
[0, 1] -- row 0 --> [0, 8]
[0, 8] -- row 8 --> [4, 8]
[4, 8] -- row 4 --> [3, 4]
[3, 4] -- row 3 --> [2, 3]
[2, 3] -- row 2 --> [1, 2]
```

Thus the packet isolates a six-row local self-edge shape: a strict edge from
a selected-distance quotient class back to itself.

## Commands

Generate and check the packet:

```bash
python scripts/check_n9_vertex_circle_t09_self_edge_lemma_packet.py \
  --assert-expected \
  --write

python scripts/check_n9_vertex_circle_t09_self_edge_lemma_packet.py \
  --check \
  --assert-expected \
  --json
```

Run the targeted artifact tests:

```bash
python -m pytest tests/test_n9_vertex_circle_t09_self_edge_lemma_packet.py -q
```

## Review standard

Before treating this as a reusable local lemma, a reviewer should restate the
incidence and cyclic-order hypotheses without relying on `T09` as a theorem
name, then prove directly that the six rows force the displayed equality path
and that row `0` gives the displayed strict inequality. The packet is a small
replay aid for that review, not an independent proof of the `n=9` case.
