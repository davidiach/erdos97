# n=9 Vertex-circle T11 Strict-cycle Local Lemma Packet

Status: `REVIEW_PENDING_DIAGNOSTIC_ONLY`.

This note records one focused proof-mining packet for the single-family `T11`
strict-cycle motif. It does not claim a proof of `n=9`, does not claim a
counterexample, does not complete independent review of the exhaustive
checker, and does not update the official/global status.

## Packet scope

The checked artifact is
`data/certificates/n9_vertex_circle_t11_strict_cycle_lemma_packet.json`.
It is derived from:

- `data/certificates/n9_vertex_circle_strict_cycle_template_packet.json`
- `data/certificates/n9_vertex_circle_template_lemma_catalog.json`

The packet covers 6 assignment ids in one family:

```text
F07: 6 assignments
```

The family has a four-row core and replays to a directed strict cycle with 36
strict edges, three cycle edges, and no self-edge conflict. The local
obstruction is a three-step quotient cycle, not a reflexive self-edge.

## Family core

`F07`:

```text
[0, 1, 2, 4, 8]
[1, 0, 2, 3, 5]
[5, 0, 3, 4, 7]
[6, 1, 5, 7, 8]

strict: [0, 2] > [0, 3] from row 1
empty connector: [0, 3] = [0, 3]

strict: [0, 3] > [0, 5] from row 1
path:   [0, 5] -> [5, 7]

strict: [5, 7] > [1, 5] from row 6
path:   [1, 5] -> [0, 1] -> [0, 2]
```

Thus the packet isolates the directed cycle

```text
[0, 2] > [0, 3] = [0, 3] > [0, 5] = [5, 7] > [1, 5] = [0, 1] = [0, 2].
```

## Local lemma

The following local obstruction is independent of the exhaustive `n=9`
brancher once the four displayed rows are assumed.

Assume a strictly convex polygon has labels appearing in cyclic order

```text
0,1,2,3,4,5,6,7,8
```

and contains the four selected rows

```text
S_0 = {1,2,4,8}
S_1 = {0,2,3,5}
S_5 = {0,3,4,7}
S_6 = {1,5,7,8}
```

Then these four rows cannot be realized.

First use row `1`. Its selected witnesses occur in cyclic order

```text
2,3,5,0.
```

In a strictly convex polygon, the rays from a vertex to the other vertices
occur in the polygon's cyclic order inside an angle smaller than `pi`. Since
the row-`1` witnesses lie on one circle centered at vertex `1`, chord length
on that circle is strictly increasing with the enclosed central angle in this
range. The chord `[0,2]` strictly contains `[0,3]`, and `[0,3]` strictly
contains `[0,5]`, in the row-`1` witness order. Hence

```text
d(0,2) > d(0,3) > d(0,5).                (1)
```

Row `5` identifies the last chord in (1) with the next outer chord:

```text
d(0,5) = d(5,7)      from row 5.
```

Thus

```text
d(0,2) > d(0,3) > d(5,7).                (2)
```

Next use row `6`. Its selected witnesses occur in cyclic order

```text
7,8,1,5.
```

The chord `[5,7]` strictly contains `[1,5]` in this row-`6` witness order, so

```text
d(5,7) > d(1,5).                         (3)
```

Rows `1` and `0` identify this inner chord with the first outer chord:

```text
d(1,5) = d(0,1)      from row 1,
d(0,1) = d(0,2)      from row 0.
```

Therefore

```text
d(5,7) > d(0,2).                         (4)
```

Combining (2) and (4) gives the impossible strict cycle

```text
d(0,2) > d(0,3) > d(5,7) > d(0,2).
```

Equivalently, after quotienting ordinary pair distances by the selected
distance equalities, rows `1`, `5`, and `6` create a directed strict cycle of
length three.

The lemma is local: it rules out any selected-witness system containing these
four rows in the stated cyclic order. It does not prove the full `n=9` finite
case, because the exhaustive checker is still needed to show that every
frontier assignment contains one of the recorded local obstruction templates.

## Commands

Generate and check the packet:

```bash
python scripts/check_n9_vertex_circle_t11_strict_cycle_lemma_packet.py \
  --assert-expected \
  --write

python scripts/check_n9_vertex_circle_t11_strict_cycle_lemma_packet.py \
  --check \
  --assert-expected \
  --json
```

Run the targeted artifact tests:

```bash
python -m pytest tests/test_n9_vertex_circle_t11_strict_cycle_lemma_packet.py -q -m "artifact"
```

## Review standard

Before treating this as a reusable local lemma, a reviewer should restate the
incidence and cyclic-order hypotheses without relying on `T11` as a theorem
name, then prove directly for the `F07` core that the listed rows force the
three strict inequalities, the two nonempty connector chains, and the one
empty identity connector. The packet is a small replay aid for that review, not
an independent proof of the `n=9` case.
