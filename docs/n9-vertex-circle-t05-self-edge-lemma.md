# n=9 Vertex-circle T05/F10 Self-edge Local Lemma

Status: `REVIEW_PENDING_DIAGNOSTIC_ONLY`.

This note records one focused proof-mining extraction for the `T05/F10`
self-edge motif. It does not claim a proof of `n=9`, does not claim a
counterexample, does not complete independent review of the exhaustive
checker, and does not update the official/global status.

## Packet scope

The checked focused artifact is
`data/certificates/n9_vertex_circle_t05_self_edge_lemma_packet.json`. It is
derived from:

- `data/certificates/n9_vertex_circle_self_edge_template_packet.json`
- `data/certificates/n9_vertex_circle_template_lemma_catalog.json`

The template covers 18 assignment ids:

```text
A013, A029, A036, A038, A053, A057, A059, A062, A072,
A088, A090, A100, A105, A120, A129, A133, A162, A170
```

All assignments belong to family `F10`. The canonical local core is the
four-row certificate:

```text
[0, 1, 2, 4, 8]
[2, 1, 3, 4, 7]
[7, 2, 5, 6, 8]
[8, 0, 1, 6, 7]
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

and contains the four selected rows

```text
S_0 = {1,2,4,8}
S_2 = {1,3,4,7}
S_7 = {2,5,6,8}
S_8 = {0,1,6,7}.
```

Then these four rows cannot be realized.

Indeed, the selected-distance equalities give

```text
d(1,8) = d(7,8)      from row 8,
d(7,8) = d(2,7)      from row 7,
d(2,7) = d(1,2)      from row 2.
```

Thus

```text
d(1,8) = d(1,2).
```

On the other hand, the selected witnesses of row `0` lie on one circle
centered at vertex `0`, and their radial order is

```text
1,2,4,8.
```

In a strictly convex polygon, the rays from a vertex to the other vertices
occur in polygon cyclic order inside an angle smaller than `pi`. On a fixed
circle, chord length is strictly increasing with the enclosed central angle in
this range. The chord `[1,8]` strictly contains the chord `[1,2]` in the
row-`0` witness order, so

```text
d(1,8) > d(1,2).
```

This contradicts the equality above. Equivalently, after quotienting ordinary
pair distances by the selected-distance equalities, row `0` creates a
reflexive strict edge for the quotient class of `[1,8]` and `[1,2]`.

The lemma is local: it rules out any selected-witness system containing these
four rows in the stated cyclic order. It does not prove the full `n=9` finite
case, because the exhaustive checker is still needed to show that every
frontier assignment contains one of the recorded local obstruction templates.

## Packet data

For row `0`, the witness order `[1, 2, 4, 8]` gives the strict
vertex-circle inequality

```text
[1, 8] > [1, 2]
```

The selected-distance equality path is:

```text
[1, 8] -- row 8 --> [7, 8]
[7, 8] -- row 7 --> [2, 7]
[2, 7] -- row 2 --> [1, 2]
```

Thus the packet isolates a four-row local self-edge shape: a strict edge from
a selected-distance quotient class back to itself.

## Commands

Generate and check the packet:

```bash
python scripts/check_n9_vertex_circle_t05_self_edge_lemma_packet.py \
  --assert-expected \
  --write

python scripts/check_n9_vertex_circle_t05_self_edge_lemma_packet.py \
  --check \
  --assert-expected \
  --json

python scripts/check_n9_t05_self_edge_minireplay.py \
  --check \
  --assert-expected \
  --json
```

Run the targeted artifact tests:

```bash
python -m pytest tests/test_n9_vertex_circle_t05_self_edge_lemma_packet.py -q
python -m pytest tests/test_n9_t05_self_edge_minireplay.py -q
```

## Review standard

Before treating this as a reusable local lemma, a reviewer should restate the
incidence and cyclic-order hypotheses without relying on `T05` as a theorem
name, then prove directly that the four rows force the displayed equality path
and that row `0` gives the displayed strict inequality. The packet is a small
replay aid for that review, not an independent proof of the `n=9` case.
