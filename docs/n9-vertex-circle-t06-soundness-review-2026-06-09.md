# n=9 Vertex-circle T06 Soundness Review - 2026-06-09

Status: `INTERNAL_REVIEW_NOTE`.

Claim scope: focused internal soundness review of the T06/F11 local self-edge
implication in `docs/n9-vertex-circle-t06-self-edge-lemma.md`. This note does
not prove `n=9`, does not claim a counterexample, does not review the
exhaustive brancher, does not review all T01-T12 packets, and does not update
the official/global status of Erdos Problem #97.

## Outcome

Outcome: `accepted_packet_soundness_T06`.

The T06/F11 local implication is sound under exactly the displayed hypotheses:
natural cyclic order on labels `0,...,8` and the five-row core listed below.

```text
T06/F11:
1 -> {0,3,5,8}
5 -> {0,3,4,7}
6 -> {2,5,7,8}
7 -> {0,1,5,6}
8 -> {2,3,6,7}
```

This is an internal review of one local obstruction packet. It is not an
external independent review and it does not promote the aggregate A10
local-lemma layer beyond the existing review-pending status.

## Local Check

The packet has the selected-path self-edge proof shape: a selected-distance
equality path identifies one row-circle outer chord with a proper subinterval
chord, while vertex-circle monotonicity makes the outer chord strictly longer.

Rows `8`, `6`, `7`, and `5` force

```text
row 8: [3,8] = [6,8]
row 6: [6,8] = [6,7]
row 7: [6,7] = [5,7]
row 5: [5,7] = [3,5]
```

so

```text
[3,8] = [6,8] = [6,7] = [5,7] = [3,5].
```

At vertex `1`, the selected witnesses occur in angular order

```text
[3,5,8,0].
```

The chord `[3,8]` spans positions `0` to `2`, while `[3,5]` spans the proper
subinterval `0` to `1`. Strict convexity puts this inside an angle below `pi`,
so row `1` gives

```text
[3,8] > [3,5],
```

contradicting the equality chain.

Equivalently, the family creates a reflexive strict edge in the
selected-distance quotient graph. No strictly convex Euclidean configuration
can satisfy the displayed local core.

## Packet/Data Agreement

The stored packet, self-edge source packet, template catalog, and mini-replay
agree with the proof above:

- template/family: `T06/F11`;
- assignment ids: `A016`, `A018`, `A026`, `A027`, `A041`, `A046`, `A069`,
  `A094`, `A097`, `A112`, `A127`, `A139`, `A146`, `A158`, `A165`, `A168`,
  `A172`, `A179`;
- assignment counts: `F11: 18`, total `18`;
- core size: `5` selected rows;
- equality path length: `4` selected-distance equality steps, and path length
  `4` for all `18` focused packet assignments;
- strict edge: `F11` uses row `1` with outer pair `[3,8]` and inner pair
  `[3,5]`;
- replay status: the family packet replays to `self_edge`;
- strict edge count in the focused packet: `45`.

## Commands Run

```bash
python scripts/check_n9_vertex_circle_t06_self_edge_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_t06_self_edge_minireplay.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_self_edge_template_packet.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_template_lemma_catalog.py --check --assert-expected --json
python -m pytest tests/test_n9_vertex_circle_t06_self_edge_lemma_packet.py tests/test_n9_t06_self_edge_minireplay.py tests/test_n9_vertex_circle_self_edge_template_packet.py tests/test_n9_vertex_circle_template_lemma_catalog.py -q -m "artifact"
```

All commands passed.

## Review Boundary

This review supports only the following narrow statement:

```text
Any strictly convex configuration satisfying the T06/F11 local cyclic-order
and selected-row core is impossible by a selected-distance quotient self-edge.
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

The remaining focused self-edge soundness review target is T09. After T08, the
reviewed packet-soundness set is T01, T02, T03, T04, T05, T06, T07, T08, and
T10-T12, while aggregate A10 review, `n=9`, and global status all remain
review-pending.
