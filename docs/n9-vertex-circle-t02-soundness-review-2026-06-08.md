# n=9 Vertex-circle T02 Soundness Review - 2026-06-08

Status: `INTERNAL_REVIEW_NOTE`.

Claim scope: focused internal soundness review of the T02/F01,F04,F08,F14
local self-edge implications in
`docs/n9-vertex-circle-t02-self-edge-lemma.md`. This note does not prove
`n=9`, does not claim a counterexample, does not review the exhaustive
brancher, does not review all T01-T12 packets, and does not update the
official/global status of Erdos Problem #97.

## Outcome

Outcome: `accepted_packet_soundness_T02`.

The T02 local implications are sound under exactly the displayed hypotheses:
natural cyclic order on labels `0,...,8` and one of the four three-row cores
listed below.

```text
T02/F01:
0 -> {1,2,3,8}
1 -> {0,2,4,7}
8 -> {0,1,4,5}

T02/F04:
0 -> {1,2,4,6}
1 -> {0,2,3,5}
2 -> {1,3,4,8}

T02/F08:
0 -> {1,2,4,8}
1 -> {0,2,3,5}
8 -> {0,1,3,7}

T02/F14:
0 -> {1,2,6,8}
1 -> {0,2,3,7}
8 -> {0,1,5,7}
```

This is an internal review of one multi-family local obstruction packet. It is
not an external independent review and it does not promote the aggregate A10
local-lemma layer beyond the existing review-pending status.

## Local Check

The four families share the same proof shape: a selected-distance equality
path identifies one row-circle outer chord with a proper subinterval chord,
while vertex-circle monotonicity makes the outer chord strictly longer.

For `F01`, rows `8`, `0`, and `1` force

```text
row 8: [1,8] = [0,8]
row 0: [0,8] = [0,1]
row 1: [0,1] = [1,2]
```

so

```text
[1,8] = [0,8] = [0,1] = [1,2].
```

At vertex `0`, the selected witnesses occur in angular order

```text
[1,2,3,8].
```

The chord `[1,8]` spans positions `0` to `3`, while `[1,2]` spans the proper
subinterval `0` to `1`. Strict convexity puts this inside an angle below `pi`,
so row `0` gives

```text
[1,8] > [1,2],
```

contradicting the equality chain.

For `F04`, rows `0`, `1`, and `2` force

```text
row 0: [0,2] = [0,1]
row 1: [0,1] = [1,2]
row 2: [1,2] = [2,3]
```

so

```text
[0,2] = [0,1] = [1,2] = [2,3].
```

At vertex `1`, the selected witnesses occur in angular order

```text
[2,3,5,0].
```

The chord `[0,2]` spans positions `0` to `3`, while `[2,3]` spans the proper
subinterval `0` to `1`. Therefore row `1` gives

```text
[0,2] > [2,3],
```

contradicting the equality chain.

For `F08`, the equality path is the same as `F01`:

```text
[1,8] = [0,8] = [0,1] = [1,2].
```

At vertex `0`, the selected witnesses occur in angular order

```text
[1,2,4,8].
```

Thus row `0` gives the strict inequality

```text
[1,8] > [1,2],
```

again contradicting the equality chain.

For `F14`, the equality path is again

```text
[1,8] = [0,8] = [0,1] = [1,2].
```

At vertex `0`, the selected witnesses occur in angular order

```text
[1,2,6,8].
```

Thus row `0` gives the strict inequality

```text
[1,8] > [1,2],
```

again contradicting the equality chain.

Equivalently, each family creates a reflexive strict edge in the
selected-distance quotient graph. No strictly convex Euclidean configuration
can satisfy any one of the four displayed local cores.

## Packet/Data Agreement

The stored packet, self-edge source packet, template catalog, and mini-replay
agree with the proof above:

- template/families: `T02/F01`, `T02/F04`, `T02/F08`, and `T02/F14`;
- assignment ids: `A001`, `A004`, `A006`, `A009`, `A011`, `A019`, `A022`,
  `A025`, `A034`, `A035`, `A045`, `A051`, `A056`, `A058`, `A060`, `A061`,
  `A063`, `A065`, `A070`, `A076`, `A078`, `A087`, `A092`, `A099`, `A101`,
  `A103`, `A114`, `A115`, `A118`, `A119`, `A121`, `A136`, `A138`, `A145`,
  `A163`, `A173`, `A176`, `A178`, `A182`, `A184`;
- assignment counts: `F01: 18`, `F04: 18`, `F08: 2`, `F14: 2`, total `40`;
- core size: `3` selected rows in each family;
- equality path length: `3` selected-distance equality steps in each family;
- strict edges: `F01`, `F08`, and `F14` use row `0` with outer pair
  `[1,8]` and inner pair `[1,2]`; `F04` uses row `1` with outer pair `[0,2]`
  and inner pair `[2,3]`;
- replay statuses: all four family packets replay to `self_edge`;
- strict edge count in the focused packet: `27`.

## Commands Run

```bash
python scripts/check_n9_vertex_circle_t02_self_edge_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_t02_self_edge_minireplay.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_self_edge_template_packet.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_template_lemma_catalog.py --check --assert-expected --json
python -m pytest tests/test_n9_vertex_circle_t02_self_edge_lemma_packet.py tests/test_n9_t02_self_edge_minireplay.py tests/test_n9_vertex_circle_self_edge_template_packet.py tests/test_n9_vertex_circle_template_lemma_catalog.py -q -m "artifact"
```

All commands passed.

## Review Boundary

This review supports only the following narrow statement:

```text
Any strictly convex configuration satisfying one of the T02 local cyclic-order
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
