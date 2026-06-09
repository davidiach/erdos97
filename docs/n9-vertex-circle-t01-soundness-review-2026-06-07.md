# n=9 Vertex-circle T01 Soundness Review - 2026-06-07

Status: `INTERNAL_REVIEW_NOTE`.

Claim scope: focused internal soundness review of the T01/F09 local
self-edge implication in
`docs/n9-vertex-circle-t01-self-edge-lemma.md`. This note does not prove
`n=9`, does not claim a counterexample, does not review the exhaustive
brancher, does not review all T01-T12 packets, and does not update the
official/global status of Erdos Problem #97.

## Outcome

Outcome: `accepted_packet_soundness_T01`.

The T01/F09 local implication is sound under exactly the displayed hypotheses:
natural cyclic order on labels `0,...,8` and the three selected rows

```text
0 -> {1,2,4,8}
1 -> {0,3,5,8}
2 -> {0,1,4,6}
```

This is an internal review of one local obstruction packet. It is not an
external independent review and it does not promote the aggregate A10
local-lemma layer beyond the existing review-pending status.

## Local Check

The selected rows force the equality chain of ordinary pair distances:

```text
row 1: [1,8] = [0,1]
row 0: [0,1] = [0,2]
row 2: [0,2] = [1,2]
```

Therefore

```text
[1,8] = [0,1] = [0,2] = [1,2].
```

At vertex `0`, strict convexity places the other vertices in the open vertex
cone in boundary order. The selected witnesses of row `0` occur in the
angular order

```text
[1,2,4,8].
```

Those four witnesses lie on the circle centered at `p_0`. The chord `[1,8]`
spans the proper containing interval `[0,3]`, while chord `[1,2]` spans the
proper subinterval `[0,1]`. The vertex cone angle is less than `pi`, so chord
length on the row circle is strictly increasing with the central angle in
this range. Hence row `0` gives the strict inequality

```text
[1,8] > [1,2].
```

This contradicts the selected-distance quotient equality
`[1,8] = [1,2]`. Equivalently, the strict quotient graph has a reflexive
strict edge.

## Packet/Data Agreement

The stored packet and mini-replay agree with the proof above:

- template/family: `T01/F09`;
- assignment ids: `A014`, `A024`, `A031`, `A140`, `A166`, `A175`;
- assignment count: `6`;
- equality chain: `[1,8] = [0,1] = [0,2] = [1,2]`;
- strict edge: outer pair `[1,8]`, inner pair `[1,2]`, row `0`,
  witness order `[1,2,4,8]`;
- replay status: `self_edge`.

The packet also records a second row-0 self-edge conflict involving inner pair
`[2,4]`; this review relies only on the primary `[1,8] > [1,2]` conflict.

## Commands Run

```bash
python scripts/check_n9_vertex_circle_t01_self_edge_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_t01_self_edge_minireplay.py --check --assert-expected --json
python -m pytest tests/test_n9_vertex_circle_t01_self_edge_lemma_packet.py tests/test_n9_t01_self_edge_minireplay.py -q -m "artifact"
```

All commands passed.

## Review Boundary

This review supports only the following narrow statement:

```text
Any strictly convex configuration satisfying the T01/F09 local cyclic-order
and selected-row hypotheses is impossible by a selected-distance quotient
self-edge.
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

Follow-up soundness reviews are now recorded for T02, T03, T04, T05, T06, T07,
and for the strict-cycle packets T10, T11, and T12. The remaining focused
local-lemma packet soundness review targets are the self-edge packets T08-T09.
