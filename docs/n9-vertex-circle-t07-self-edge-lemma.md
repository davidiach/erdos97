# n=9 Vertex-circle T07/F06 Self-edge Local Lemma

Status: `REVIEW_PENDING_DIAGNOSTIC_ONLY`.

This note records one focused proof-mining extraction for the `T07/F06`
self-edge motif. It does not claim a proof of `n=9`, does not claim a
counterexample, does not complete independent review of the exhaustive
checker, and does not update the official/global status.

## Packet scope

The checked focused artifact is
`data/certificates/n9_vertex_circle_t07_self_edge_lemma_packet.json`. It is
derived from:

- `data/certificates/n9_vertex_circle_self_edge_template_packet.json`
- `data/certificates/n9_vertex_circle_template_lemma_catalog.json`

The template covers 18 assignment ids:

```text
A007, A028, A037, A039, A052, A055, A064, A066, A075,
A089, A091, A098, A102, A113, A125, A128, A171, A177
```

All assignments belong to family `F06`. The canonical local core is the
five-row certificate:

```text
[0, 1, 2, 4, 7]
[2, 0, 1, 4, 6]
[4, 1, 3, 5, 7]
[5, 3, 4, 6, 8]
[6, 0, 2, 5, 7]
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

and contains the five selected rows

```text
S_0 = {1,2,4,7}
S_2 = {0,1,4,6}
S_4 = {1,3,5,7}
S_5 = {3,4,6,8}
S_6 = {0,2,5,7}.
```

Then these five rows cannot be realized.

Indeed, the selected-distance equalities give

```text
d(1,4) = d(4,5)      from row 4,
d(4,5) = d(5,6)      from row 5,
d(5,6) = d(2,6)      from row 6,
d(2,6) = d(1,2)      from row 2.
```

Thus

```text
d(1,4) = d(1,2).
```

On the other hand, the selected witnesses of row `0` lie on one circle
centered at vertex `0`, and their radial order is

```text
1,2,4,7.
```

In a strictly convex polygon, the rays from a vertex to the other vertices
occur in polygon cyclic order inside an angle smaller than `pi`. On a fixed
circle, chord length is strictly increasing with the enclosed central angle in
this range. The chord `[1,4]` strictly contains the chord `[1,2]` in the
row-`0` witness order, so

```text
d(1,4) > d(1,2).
```

This contradicts the equality above. Equivalently, after quotienting ordinary
pair distances by the selected-distance equalities, row `0` creates a
reflexive strict edge for the quotient class of `[1,4]` and `[1,2]`.

The lemma is local: it rules out any selected-witness system containing these
five rows in the stated cyclic order. It does not prove the full `n=9` finite
case, because the exhaustive checker is still needed to show that every
frontier assignment contains one of the recorded local obstruction templates.

## Packet data

For row `0`, the witness order `[1, 2, 4, 7]` gives the strict
vertex-circle inequality

```text
[1, 4] > [1, 2]
```

The selected-distance equality path is:

```text
[1, 4] -- row 4 --> [4, 5]
[4, 5] -- row 5 --> [5, 6]
[5, 6] -- row 6 --> [2, 6]
[2, 6] -- row 2 --> [1, 2]
```

Thus the packet isolates a five-row local self-edge shape: a strict edge from
a selected-distance quotient class back to itself.

## Commands

Generate and check the packet:

```bash
python scripts/check_n9_vertex_circle_t07_self_edge_lemma_packet.py \
  --assert-expected \
  --write

python scripts/check_n9_vertex_circle_t07_self_edge_lemma_packet.py \
  --check \
  --assert-expected \
  --json

python scripts/check_n9_t07_self_edge_minireplay.py \
  --check \
  --assert-expected \
  --json
```

Run the targeted artifact tests:

```bash
python -m pytest tests/test_n9_vertex_circle_t07_self_edge_lemma_packet.py -q
python -m pytest tests/test_n9_t07_self_edge_minireplay.py -q
```

## Review standard

Before treating this as a reusable local lemma, a reviewer should restate the
incidence and cyclic-order hypotheses without relying on `T07` as a theorem
name, then prove directly that the five rows force the displayed equality
path and that row `0` gives the displayed strict inequality. The packet is a
small replay aid for that review, not an independent proof of the `n=9` case.
