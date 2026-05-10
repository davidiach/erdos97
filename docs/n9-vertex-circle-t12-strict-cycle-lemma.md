# n=9 Vertex-circle T12 Strict-cycle Local Lemma Candidate

Status: `REVIEW_PENDING_LOCAL_LEMMA_CANDIDATE`.

This note extracts one proof-facing local obstruction from the review-pending
`n=9` vertex-circle diagnostics. It does not claim a proof of `n=9`, does not
claim a counterexample, does not complete independent review of the exhaustive
checker, and does not update the official/global status of Erdos Problem #97.

The labels `T12` and `F16` are retained only as packet/catalog navigation. They
are not theorem hypotheses.

## Exact Local Hypotheses

Let `p_0,...,p_8` be distinct vertices of a strictly convex nonagon in cyclic
order

```text
0,1,2,3,4,5,6,7,8.
```

Assume the following six selected witness rows are present:

```text
center 0: {1,3,6,7}
center 1: {2,4,7,8}
center 2: {0,3,5,8}
center 3: {0,1,4,6}
center 4: {1,2,5,7}
center 8: {0,2,5,6}
```

The selected-row hypothesis means that each listed center is equidistant from
the four listed witnesses. In pair-distance notation, the rows used below give
the selected-distance connector chains

```text
row 8: [0,8] = [2,8]

row 4: [2,4] = [1,4]
row 1: [1,4] = [1,7]

row 3: [1,3] = [0,3]
```

or equivalently

```text
[0,8] = [2,8],
[2,4] = [1,4] = [1,7],
[1,3] = [0,3].
```

The checked packet recording this local shape is
`data/certificates/n9_vertex_circle_t12_strict_cycle_lemma_packet.json`. It is
derived from the strict-cycle template packet and the template lemma catalog,
but the local argument below uses only the six displayed selected rows plus
the displayed cyclic order.

## Vertex-circle Strict Inequalities

At vertex `2`, the selected witnesses occur in boundary/angular order

```text
[3,5,8,0].
```

Since the nonagon is strictly convex, boundary order agrees with angular order
inside the vertex cone at `2`. The witnesses in row `2` lie on one circle
centered at `p_2`, and chord length on that circle is strictly increasing with
central angle below `pi`.

The chord `[0,3]` spans witness positions `0` to `3`, while `[0,8]` spans the
proper subinterval `2` to `3`. Therefore

```text
[0,3] > [0,8].                         (1)
```

Using the selected-distance connector from row `8`,

```text
[0,8] = [2,8],
```

inequality (1) becomes

```text
[0,3] > [2,8].                         (2)
```

At vertex `1`, the selected witnesses occur in boundary/angular order

```text
[2,4,7,8].
```

The chord `[2,8]` spans witness positions `0` to `3`, while `[2,4]` spans the
proper subinterval `0` to `1`. The same vertex-circle monotonicity gives

```text
[2,8] > [2,4].                         (3)
```

Using the selected-distance connector from rows `4` and `1`,

```text
[2,4] = [1,4] = [1,7],
```

inequality (3) becomes

```text
[2,8] > [1,7].                         (4)
```

At vertex `0`, the selected witnesses occur in boundary/angular order

```text
[1,3,6,7].
```

The chord `[1,7]` spans witness positions `0` to `3`, while `[1,3]` spans the
proper subinterval `0` to `1`. Hence

```text
[1,7] > [1,3].                         (5)
```

Using the selected-distance connector from row `3`,

```text
[1,3] = [0,3],
```

inequality (5) becomes

```text
[1,7] > [0,3].                         (6)
```

## Contradiction

The quotient inequalities (2), (4), and (6) form the directed strict cycle

```text
[0,3] > [2,8] > [1,7] > [0,3].
```

Equivalently, after quotienting ordinary pair distances by the selected-row
equalities, the strict quotient graph has a directed three-edge cycle. No
Euclidean strictly convex realization satisfying the stated local hypotheses
can exist.

## Packet Replay

The compact checker treats the JSON packet and its source packets as input
data. It checks that the source packets are valid, verifies each selected-row
equality connector, verifies that each strict inequality is supported by the
stated row and cyclic witness interval, replays the vertex-circle quotient
graph from the six local rows, and reports validation errors if the packet no
longer supports the stated local lemma candidate.

```bash
python scripts/check_n9_vertex_circle_t12_strict_cycle_lemma_packet.py \
  --check \
  --assert-expected \
  --json
```

Targeted artifact test:

```bash
python -m pytest tests/test_n9_vertex_circle_t12_strict_cycle_lemma_packet.py -q -m "artifact"
```

## What This Does Not Prove

This local lemma candidate rules out only configurations satisfying the exact
cyclic order and six selected rows displayed above. It does not enumerate all
`n=9` selected-witness systems, does not promote the review-pending exhaustive
`n=9` checker, does not rule out other vertex-circle templates, does not prove
Erdos Problem #97, and does not produce or certify a counterexample.
