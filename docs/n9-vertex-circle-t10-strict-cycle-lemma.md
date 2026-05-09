# n=9 Vertex-circle T10 Strict-cycle Local Lemma Packet

Status: `REVIEW_PENDING_DIAGNOSTIC_ONLY`.

This note records one focused proof-mining packet for the single-family `T10`
strict-cycle motif. It does not claim a proof of `n=9`, does not claim a
counterexample, does not complete independent review of the exhaustive
checker, and does not update the official/global status.

## Packet scope

The checked artifact is
`data/certificates/n9_vertex_circle_t10_strict_cycle_lemma_packet.json`.
It is derived from:

- `data/certificates/n9_vertex_circle_strict_cycle_template_packet.json`
- `data/certificates/n9_vertex_circle_template_lemma_catalog.json`

The packet covers 18 assignment ids in one family:

```text
F12: 18 assignments
```

The family has a four-row core and replays to a directed strict cycle with 36
strict edges, two cycle edges, and no self-edge conflict. The local obstruction
is a two-step quotient cycle, not a reflexive self-edge.

## Family core

`F12`:

```text
[0, 1, 2, 5, 6]
[3, 0, 1, 4, 6]
[6, 1, 3, 4, 7]
[8, 0, 3, 6, 7]

strict: [0, 6] > [0, 3] from row 8
path:   [0, 3] -> [3, 6] -> [1, 6]

strict: [1, 6] > [0, 1] from row 3
path:   [0, 1] -> [0, 6]
```

Thus the packet isolates the directed cycle

```text
[0, 6] > [0, 3] = [3, 6] = [1, 6] > [0, 1] = [0, 6].
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
S_0 = {1,2,5,6}
S_3 = {0,1,4,6}
S_6 = {1,3,4,7}
S_8 = {0,3,6,7}
```

Then these four rows cannot be realized.

Indeed, row `8` has witness order

```text
0,3,6,7.
```

In a strictly convex polygon, the rays from a vertex to the other vertices
occur in the polygon's cyclic order inside an angle smaller than `pi`. Since
the row-`8` witnesses lie on one circle centered at vertex `8`, chord length
on that circle is strictly increasing with the enclosed central angle in this
range. The chord `[0,6]` strictly contains `[0,3]` in the row-`8` witness
order, so

```text
d(0,6) > d(0,3).                         (1)
```

The selected-distance equalities from rows `3` and `6` give

```text
d(0,3) = d(3,6)      from row 3,
d(3,6) = d(1,6)      from row 6.
```

Thus (1) implies

```text
d(0,6) > d(1,6).                         (2)
```

Next, row `3` has witness order

```text
4,6,0,1.
```

The chord `[1,6]` strictly contains `[0,1]` in this row-`3` witness order, so

```text
d(1,6) > d(0,1).                         (3)
```

Row `0` identifies the inner chord from (3) with the first outer chord:

```text
d(0,1) = d(0,6)      from row 0.
```

Combining this equality with (3) gives

```text
d(1,6) > d(0,6).                         (4)
```

The inequalities (2) and (4) form the impossible strict cycle

```text
d(0,6) > d(1,6) > d(0,6).
```

Equivalently, after quotienting ordinary pair distances by the selected
distance equalities, rows `8` and `3` create a directed strict cycle of length
two.

The lemma is local: it rules out any selected-witness system containing these
four rows in the stated cyclic order. It does not prove the full `n=9` finite
case, because the exhaustive checker is still needed to show that every
frontier assignment contains one of the recorded local obstruction templates.

## Commands

Generate and check the packet:

```bash
python scripts/check_n9_vertex_circle_t10_strict_cycle_lemma_packet.py \
  --assert-expected \
  --write

python scripts/check_n9_vertex_circle_t10_strict_cycle_lemma_packet.py \
  --check \
  --assert-expected \
  --json
```

Run the targeted artifact tests:

```bash
python -m pytest tests/test_n9_vertex_circle_t10_strict_cycle_lemma_packet.py -q -m "artifact"
```

## Review standard

Before treating this as a reusable local lemma, a reviewer should restate the
incidence and cyclic-order hypotheses without relying on `T10` as a theorem
name, then prove directly for the `F12` core that the listed rows force the two
strict inequalities and the two connector chains. The packet is a small replay
aid for that review, not an independent proof of the `n=9` case.
