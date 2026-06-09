# n=9 Vertex-circle T03 Soundness Review - 2026-06-08

Status: `INTERNAL_REVIEW_NOTE`.

Claim scope: focused internal soundness review of the T03/F05,F15 local
self-edge implications in
`docs/n9-vertex-circle-t03-self-edge-lemma.md`. This note does not prove
`n=9`, does not claim a counterexample, does not review the exhaustive
brancher, does not review all T01-T12 packets, and does not update the
official/global status of Erdos Problem #97.

## Outcome

Outcome: `accepted_packet_soundness_T03`.

The T03 local implications are sound under exactly the displayed hypotheses:
natural cyclic order on labels `0,...,8` and one of the two four-row cores
listed below.

```text
T03/F05:
1 -> {2,5,7,8}
2 -> {1,3,4,8}
3 -> {0,2,4,7}
6 -> {1,3,5,7}

T03/F15:
0 -> {1,3,4,8}
1 -> {0,2,4,5}
2 -> {1,3,5,6}
3 -> {2,4,6,7}
```

This is an internal review of one multi-family local obstruction packet. It is
not an external independent review and it does not promote the aggregate A10
local-lemma layer beyond the existing review-pending status.

## Local Check

The two families share the same proof shape: a selected-distance equality path
identifies one row-circle outer chord with a proper subinterval chord, while
vertex-circle monotonicity makes the outer chord strictly longer.

For `F05`, rows `3`, `2`, and `1` force

```text
row 3: [3,7] = [2,3]
row 2: [2,3] = [1,2]
row 1: [1,2] = [1,7]
```

so

```text
[3,7] = [2,3] = [1,2] = [1,7].
```

At vertex `6`, the selected witnesses occur in angular order

```text
[7,1,3,5].
```

The chord `[3,7]` spans positions `0` to `2`, while `[1,7]` spans the proper
subinterval `0` to `1`. Strict convexity puts this inside an angle below `pi`,
so row `6` gives

```text
[3,7] > [1,7],
```

contradicting the equality chain.

For `F15`, rows `1`, `2`, and `3` force

```text
row 1: [1,4] = [1,2]
row 2: [1,2] = [2,3]
row 3: [2,3] = [3,4]
```

so

```text
[1,4] = [1,2] = [2,3] = [3,4].
```

At vertex `0`, the selected witnesses occur in angular order

```text
[1,3,4,8].
```

The chord `[1,4]` spans positions `0` to `2`, while `[3,4]` spans the proper
subinterval `1` to `2`. Therefore row `0` gives

```text
[1,4] > [3,4],
```

contradicting the equality chain.

Equivalently, each family creates a reflexive strict edge in the
selected-distance quotient graph. No strictly convex Euclidean configuration
can satisfy either displayed local core.

## Packet/Data Agreement

The stored packet, self-edge source packet, template catalog, and mini-replay
agree with the proof above:

- template/families: `T03/F05` and `T03/F15`;
- assignment ids: `A005`, `A021`, `A042`, `A048`, `A054`, `A068`, `A074`,
  `A077`, `A079`, `A104`, `A110`, `A116`, `A117`, `A124`, `A131`, `A148`,
  `A155`, `A156`, `A181`, `A183`;
- assignment counts: `F05: 18`, `F15: 2`, total `20`;
- core size: `4` selected rows in each family;
- equality path length: `3` selected-distance equality steps in each family,
  and path length `3` for all `20` focused packet assignments;
- strict edges: `F05` uses row `6` with outer pair `[3,7]` and inner pair
  `[1,7]`; `F15` uses row `0` with outer pair `[1,4]` and inner pair
  `[3,4]`;
- replay statuses: both family packets replay to `self_edge`;
- strict edge count in the focused packet: `36`.

## Commands Run

```bash
python scripts/check_n9_vertex_circle_t03_self_edge_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_t03_self_edge_minireplay.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_self_edge_template_packet.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_template_lemma_catalog.py --check --assert-expected --json
python -m pytest tests/test_n9_vertex_circle_t03_self_edge_lemma_packet.py tests/test_n9_t03_self_edge_minireplay.py tests/test_n9_vertex_circle_self_edge_template_packet.py tests/test_n9_vertex_circle_template_lemma_catalog.py -q -m "artifact"
```

All commands passed.

## Review Boundary

This review supports only the following narrow statement:

```text
Any strictly convex configuration satisfying one of the T03 local cyclic-order
and selected-row cores is impossible by a selected-distance quotient self-edge.
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

Focused packet-soundness notes are now recorded for T01-T12. Aggregate A10
review, `n=9`, and global status all remain review-pending.
