# n=9 Vertex-circle T12 Strict-cycle Local Lemma Packet

Status: `REVIEW_PENDING_DIAGNOSTIC_ONLY`.

This note records one focused proof-mining packet for the single-family `T12`
strict-cycle motif. It does not claim a proof of `n=9`, does not claim a
counterexample, does not complete independent review of the exhaustive
checker, and does not update the official/global status.

## Packet scope

The checked artifact is
`data/certificates/n9_vertex_circle_t12_strict_cycle_lemma_packet.json`.
It is derived from:

- `data/certificates/n9_vertex_circle_strict_cycle_template_packet.json`
- `data/certificates/n9_vertex_circle_template_lemma_catalog.json`

The packet covers 2 assignment ids in one family:

```text
F16: 2 assignments
```

The family has a six-row core and replays to a directed strict cycle with 54
strict edges, three cycle edges, and no self-edge conflict. The local
obstruction is a three-step quotient cycle, not a reflexive self-edge.

## Family core

`F16`:

```text
[0, 1, 3, 6, 7]
[1, 2, 4, 7, 8]
[2, 0, 3, 5, 8]
[3, 0, 1, 4, 6]
[4, 1, 2, 5, 7]
[8, 0, 2, 5, 6]

strict: [0, 3] > [0, 8] from row 2
path:   [0, 8] -> [2, 8]

strict: [2, 8] > [2, 4] from row 1
path:   [2, 4] -> [1, 4] -> [1, 7]

strict: [1, 7] > [1, 3] from row 0
path:   [1, 3] -> [0, 3]
```

Thus the packet isolates the directed cycle

```text
[0, 3] > [0, 8] = [2, 8] > [2, 4] = [1, 4] = [1, 7] > [1, 3] = [0, 3].
```

## Local lemma

The following local obstruction is independent of the exhaustive `n=9`
brancher once the six displayed rows are assumed.

Assume a strictly convex polygon has labels appearing in cyclic order

```text
0,1,2,3,4,5,6,7,8
```

and contains the six selected rows

```text
S_0 = {1,3,6,7}
S_1 = {2,4,7,8}
S_2 = {0,3,5,8}
S_3 = {0,1,4,6}
S_4 = {1,2,5,7}
S_8 = {0,2,5,6}
```

Then these six rows cannot be realized.

First use row `2`. Its selected witnesses occur in cyclic order

```text
3,5,8,0.
```

In a strictly convex polygon, the rays from a vertex to the other vertices
occur in the polygon's cyclic order inside an angle smaller than `pi`. Since
the row-`2` witnesses lie on one circle centered at vertex `2`, chord length
on that circle is strictly increasing with the enclosed central angle in this
range. The chord `[0,3]` strictly contains `[0,8]` in the row-`2` witness
order, so

```text
d(0,3) > d(0,8).                         (1)
```

Row `8` identifies the inner chord in (1) with the next outer chord:

```text
d(0,8) = d(2,8)      from row 8.
```

Thus

```text
d(0,3) > d(2,8).                         (2)
```

Next use row `1`. Its selected witnesses occur in cyclic order

```text
2,4,7,8.
```

The chord `[2,8]` strictly contains `[2,4]` in this row-`1` witness order, so

```text
d(2,8) > d(2,4).                         (3)
```

Rows `4` and `1` identify this inner chord with the next outer chord:

```text
d(2,4) = d(1,4)      from row 4,
d(1,4) = d(1,7)      from row 1.
```

Therefore

```text
d(2,8) > d(1,7).                         (4)
```

Finally use row `0`. Its selected witnesses occur in cyclic order

```text
1,3,6,7.
```

The chord `[1,7]` strictly contains `[1,3]` in this row-`0` witness order, so

```text
d(1,7) > d(1,3).                         (5)
```

Row `3` identifies this inner chord with the first outer chord:

```text
d(1,3) = d(0,3)      from row 3.
```

Combining this equality with (5) gives

```text
d(1,7) > d(0,3).                         (6)
```

The strict inequalities (2), (4), and (6) produce the impossible cycle

```text
d(0,3) > d(2,8) > d(1,7) > d(0,3).
```

Equivalently, after quotienting ordinary pair distances by the selected
distance equalities, rows `2`, `1`, and `0` create a directed strict cycle of
length three.

The lemma is local: it rules out any selected-witness system containing these
six rows in the stated cyclic order. It does not prove the full `n=9` finite
case, because the exhaustive checker is still needed to show that every
frontier assignment contains one of the recorded local obstruction templates.

## Commands

Generate and check the packet:

```bash
python scripts/check_n9_vertex_circle_t12_strict_cycle_lemma_packet.py \
  --assert-expected \
  --write

python scripts/check_n9_vertex_circle_t12_strict_cycle_lemma_packet.py \
  --check \
  --assert-expected \
  --json
```

Run the targeted artifact tests:

```bash
python -m pytest tests/test_n9_vertex_circle_t12_strict_cycle_lemma_packet.py -q -m "artifact"
```

## Review standard

Before treating this as a reusable local lemma, a reviewer should restate the
incidence and cyclic-order hypotheses without relying on `T12` as a theorem
name, then prove directly for the `F16` core that the listed rows force the
three strict inequalities and the three nonempty connector chains. The packet
is a small replay aid for that review, not an independent proof of the `n=9`
case.
