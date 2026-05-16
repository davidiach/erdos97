# n=9 Vertex-circle T01 Self-edge Local Lemma Candidate

Status: `REVIEW_PENDING_LOCAL_LEMMA_CANDIDATE`.

This note extracts one proof-facing local obstruction from the
review-pending `n=9` vertex-circle diagnostics. It does not claim a proof of
`n=9`, does not claim a counterexample, does not complete independent review
of the exhaustive checker, and does not update the official/global status of
Erdos Problem #97.

The labels `T01` and `F09` are retained only as packet/catalog navigation. They
are not theorem hypotheses.

## Reusable Five-label Form

The local obstruction does not intrinsically use all nine labels. It has the
following reusable shape.

Let `C,A,B,D,E` be five distinct vertices of a strictly convex polygon, with
`A,B,D,E` occurring in that order in the vertex cone at `C`; the first and
last of these vertices may lie on the two boundary rays of the cone. Assume:

```text
center C selects A,B,D,E
center A selects C,E
center B selects A,C
```

Here "center X selects Y,Z" means that the selected witness row at `X`
contains both `Y` and `Z`, so `|XY|=|XZ|`. The first row says that
`A,B,D,E` lie on one circle centered at `C`.

Then the selected-distance equalities give

```text
|AE| = |AC| = |CB| = |AB|.
```

But on the circle centered at `C`, the chord `AE` strictly contains the chord
`AB` in angular span, because the witnesses occur as `A,B,D,E` inside an
angle smaller than `pi`. Thus

```text
|AE| > |AB|,
```

contradicting the equality chain. Therefore no strictly convex realization can
satisfy this five-label local pattern.

The n=9 packet below is the specialization

```text
C=0, A=1, B=2, D=4, E=8.
```

## Exact Local Hypotheses

Let `p_0,...,p_8` be distinct vertices of a strictly convex nonagon in cyclic
order

```text
0,1,2,3,4,5,6,7,8.
```

Assume the following three selected witness rows are present:

```text
center 0: {1,2,4,8}
center 1: {0,3,5,8}
center 2: {0,1,4,6}
```

The selected-row hypothesis means that each listed center is equidistant from
the four listed witnesses. In pair-distance notation, the rows give these
selected-distance equalities among ordinary pair distances:

```text
row 1: [1,8] = [0,1]
row 0: [0,1] = [0,2]
row 2: [0,2] = [1,2]
```

Equivalently, the three rows force the selected-distance quotient chain

```text
[1,8] = [0,1] = [0,2] = [1,2].
```

The checked packet recording this local shape is
`data/certificates/n9_vertex_circle_t01_self_edge_lemma_packet.json`. It is
derived from the self-edge template packet and the template lemma catalog, but
the local argument above uses only the three displayed selected rows plus the
displayed cyclic order.

## Vertex-circle Strict Inequality

At vertex `0`, the selected witnesses occur in boundary/angular order

```text
[1,2,4,8].
```

Since the nonagon is strictly convex, all other vertices lie in the open
vertex cone at `0` except the adjacent boundary vertices on the cone rays.
Thus this boundary order agrees with angular order about `p_0`.

The four witnesses in row `0` lie on one circle centered at `p_0`. On one
circle, chord length is strictly increasing with the central angle while the
angle is below `pi`; the vertex cone at a strictly convex vertex has angle
less than `pi`. The chord `[1,8]` spans the full interval from witness position
`0` to `3`, while `[1,2]` spans the proper subinterval from position `0` to
`1`. Therefore row `0` gives the strict vertex-circle inequality

```text
[1,8] > [1,2].
```

## Contradiction

The selected-distance rows identify `[1,8]` and `[1,2]` in the quotient, while
the vertex-circle monotonicity step gives a strict inequality between the same
two quotient classes:

```text
[1,8] = [1,2]
[1,8] > [1,2].
```

Equivalently, the strict quotient graph has a reflexive strict edge. No
Euclidean strictly convex realization satisfying the stated local hypotheses
can exist.

## Packet Replay

The compact checker treats the JSON packet and its source packets as input
data. It checks that the source packets are valid, verifies the three equality
steps from selected rows, replays the vertex-circle quotient graph from the
three local rows, and reports validation errors if the packet no longer
supports the stated local lemma candidate.

```bash
python scripts/check_n9_vertex_circle_t01_self_edge_lemma_packet.py \
  --check \
  --assert-expected \
  --json
```

Targeted artifact test:

```bash
python -m pytest tests/test_n9_vertex_circle_t01_self_edge_lemma_packet.py -q -m "artifact"
```

## What This Does Not Prove

This local lemma candidate rules out only configurations satisfying the exact
cyclic order and three selected rows displayed above. It does not enumerate all
`n=9` selected-witness systems, does not promote the review-pending exhaustive
`n=9` checker, does not rule out other vertex-circle templates, does not prove
Erdos Problem #97, and does not produce or certify a counterexample.
