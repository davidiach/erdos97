# n=9 Vertex-circle T06/F11 Self-edge Local Lemma

Status: `REVIEW_PENDING_DIAGNOSTIC_ONLY`.

This note records one focused proof-mining extraction for the `T06/F11`
self-edge motif. It does not claim a proof of `n=9`, does not claim a
counterexample, does not complete independent review of the exhaustive
checker, and does not update the official/global status.

## Packet scope

The checked focused artifact is
`data/certificates/n9_vertex_circle_t06_self_edge_lemma_packet.json`. It is
derived from:

- `data/certificates/n9_vertex_circle_self_edge_template_packet.json`
- `data/certificates/n9_vertex_circle_template_lemma_catalog.json`

The template covers 18 assignment ids:

```text
A016, A018, A026, A027, A041, A046, A069, A094, A097,
A112, A127, A139, A146, A158, A165, A168, A172, A179
```

All assignments belong to family `F11`. The canonical local core is the
five-row certificate:

```text
[1, 0, 3, 5, 8]
[5, 0, 3, 4, 7]
[6, 2, 5, 7, 8]
[7, 0, 1, 5, 6]
[8, 2, 3, 6, 7]
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
S_1 = {0,3,5,8}
S_5 = {0,3,4,7}
S_6 = {2,5,7,8}
S_7 = {0,1,5,6}
S_8 = {2,3,6,7}.
```

Then these five rows cannot be realized.

Indeed, the selected-distance equalities give

```text
d(3,8) = d(6,8)      from row 8,
d(6,8) = d(6,7)      from row 6,
d(6,7) = d(5,7)      from row 7,
d(5,7) = d(3,5)      from row 5.
```

Thus

```text
d(3,8) = d(3,5).
```

On the other hand, the selected witnesses of row `1` lie on one circle
centered at vertex `1`, and their radial order is

```text
3,5,8,0.
```

In a strictly convex polygon, the rays from a vertex to the other vertices
occur in polygon cyclic order inside an angle smaller than `pi`. On a fixed
circle, chord length is strictly increasing with the enclosed central angle in
this range. The chord `[3,8]` strictly contains the chord `[3,5]` in the
row-`1` witness order, so

```text
d(3,8) > d(3,5).
```

This contradicts the equality above. Equivalently, after quotienting ordinary
pair distances by the selected-distance equalities, row `1` creates a
reflexive strict edge for the quotient class of `[3,8]` and `[3,5]`.

The lemma is local: it rules out any selected-witness system containing these
five rows in the stated cyclic order. It does not prove the full `n=9` finite
case, because the exhaustive checker is still needed to show that every
frontier assignment contains one of the recorded local obstruction templates.

## Packet data

For row `1`, the witness order `[3, 5, 8, 0]` gives the strict
vertex-circle inequality

```text
[3, 8] > [3, 5]
```

The selected-distance equality path is:

```text
[3, 8] -- row 8 --> [6, 8]
[6, 8] -- row 6 --> [6, 7]
[6, 7] -- row 7 --> [5, 7]
[5, 7] -- row 5 --> [3, 5]
```

Thus the packet isolates a five-row local self-edge shape: a strict edge from
a selected-distance quotient class back to itself.

## Commands

Generate and check the packet:

```bash
python scripts/check_n9_vertex_circle_t06_self_edge_lemma_packet.py \
  --assert-expected \
  --write

python scripts/check_n9_vertex_circle_t06_self_edge_lemma_packet.py \
  --check \
  --assert-expected \
  --json
```

Run the targeted artifact tests:

```bash
python -m pytest tests/test_n9_vertex_circle_t06_self_edge_lemma_packet.py -q
```

## Review standard

Before treating this as a reusable local lemma, a reviewer should restate the
incidence and cyclic-order hypotheses without relying on `T06` as a theorem
name, then prove directly that the five rows force the displayed equality path
and that row `1` gives the displayed strict inequality. The packet is a small
replay aid for that review, not an independent proof of the `n=9` case.
