# n=9 Vertex-circle T11 Soundness Review - 2026-06-08

Status: `INTERNAL_REVIEW_NOTE`.

Claim scope: focused internal soundness review of the T11/F07 local
strict-cycle implication in
`docs/n9-vertex-circle-t11-strict-cycle-lemma.md`. This note does not prove
`n=9`, does not claim a counterexample, does not review the exhaustive
brancher, does not review all T01-T12 packets, and does not update the
official/global status of Erdos Problem #97.

## Outcome

Outcome: `accepted_packet_soundness_T11`.

The T11/F07 local implication is sound under exactly the displayed
hypotheses: natural cyclic order on labels `0,...,8` and the four selected
rows

```text
0 -> {1,2,4,8}
1 -> {0,2,3,5}
5 -> {0,3,4,7}
6 -> {1,5,7,8}
```

This is an internal review of one local obstruction packet. It is not an
external independent review and it does not promote the aggregate A10
local-lemma layer beyond the existing review-pending status.

## Local Check

At vertex `1`, the selected witnesses occur in angular order

```text
[2,3,5,0].
```

The witnesses lie on the circle centered at `p_1`. The chord `[0,2]` spans
positions `0` to `3`, while `[0,3]` spans the proper subinterval `1` to `3`.
Strict convexity puts this inside an angle below `pi`, so row `1` gives

```text
[0,2] > [0,3].                         (1)
```

The first connector is the identity chain

```text
[0,3] = [0,3].
```

The same row-`1` witness order also has chord `[0,3]` spanning positions
`1` to `3`, while `[0,5]` spans the proper subinterval `2` to `3`. Therefore
row `1` gives

```text
[0,3] > [0,5].
```

Row `5` forces the selected-distance equality

```text
[0,5] = [5,7],
```

so the second strict edge becomes

```text
[0,3] > [5,7].                         (2)
```

At vertex `6`, the selected witnesses occur in angular order

```text
[7,8,1,5].
```

The chord `[5,7]` spans positions `0` to `3`, while `[1,5]` spans the proper
subinterval `2` to `3`. The same vertex-circle monotonicity gives

```text
[5,7] > [1,5].
```

Rows `1` and `0` force the selected-distance equality chain

```text
row 1: [1,5] = [0,1]
row 0: [0,1] = [0,2]
```

so

```text
[1,5] = [0,1] = [0,2].
```

Thus the third strict edge becomes

```text
[5,7] > [0,2].                         (3)
```

The inequalities (1), (2), and (3) form the directed strict cycle

```text
[0,2] > [0,3] > [5,7] > [0,2].
```

No strictly convex Euclidean configuration can satisfy a directed strict cycle
of ordinary distances after selected-distance quotienting.

## Packet/Data Agreement

The stored packet, strict-cycle source packet, template catalog, and
mini-replay agree with the proof above:

- template/family: `T11/F07`;
- assignment ids: `A008`, `A015`, `A032`, `A137`, `A141`, `A167`;
- assignment count: `6`;
- core centers: `0`, `1`, `5`, `6`;
- cycle length: `3`;
- equality chains: `[0,3] = [0,3]`, `[0,5] = [5,7]`, and
  `[1,5] = [0,1] = [0,2]`;
- strict edges: row `1` gives outer pair `[0,2]`, inner pair `[0,3]`; row
  `1` gives outer pair `[0,3]`, inner pair `[0,5]`; row `6` gives outer pair
  `[5,7]`, inner pair `[1,5]`;
- replay status: `strict_cycle`;
- strict edge count in the focused packet: `36`.

## Commands Run

```bash
python scripts/check_n9_vertex_circle_t11_strict_cycle_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_t11_strict_cycle_minireplay.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_strict_cycle_template_packet.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_template_lemma_catalog.py --check --assert-expected --json
python -m pytest tests/test_n9_vertex_circle_t11_strict_cycle_lemma_packet.py tests/test_n9_t11_strict_cycle_minireplay.py tests/test_n9_vertex_circle_strict_cycle_template_packet.py tests/test_n9_vertex_circle_template_lemma_catalog.py -q -m "artifact"
```

All commands passed.

## Review Boundary

This review supports only the following narrow statement:

```text
Any strictly convex configuration satisfying the T11/F07 local cyclic-order
and selected-row hypotheses is impossible by a selected-distance quotient
directed strict cycle.
```

It does not support any of the following stronger statements:

- all T01-T12 packets have been mathematically reviewed;
- the A10 local-lemma layer is fully reviewed;
- the 184-assignment frontier is complete;
- the vertex-circle strict-edge generator is fully reviewed;
- no bad nonagon exists as a promoted source-of-truth claim;
- Erdos Problem #97 is proved;
- a counterexample is produced or certified.

## Next Packet

The strict-cycle packet family now has one internal soundness note for each of
T10, T11, and T12. The remaining focused local-lemma packet soundness review
targets are the self-edge packets T08-T09, while aggregate A10 review, `n=9`,
and global status all remain review-pending.
