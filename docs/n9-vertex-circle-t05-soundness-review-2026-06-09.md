# n=9 Vertex-circle T05 Soundness Review - 2026-06-09

Status: `INTERNAL_REVIEW_NOTE`.

Claim scope: focused internal soundness review of the T05/F10 local self-edge
implication in `docs/n9-vertex-circle-t05-self-edge-lemma.md`. This note does
not prove `n=9`, does not claim a counterexample, does not review the
exhaustive brancher, does not review all T01-T12 packets, and does not update
the official/global status of Erdos Problem #97.

## Outcome

Outcome: `accepted_packet_soundness_T05`.

The T05/F10 local implication is sound under exactly the displayed hypotheses:
natural cyclic order on labels `0,...,8` and the four-row core listed below.

```text
T05/F10:
0 -> {1,2,4,8}
2 -> {1,3,4,7}
7 -> {2,5,6,8}
8 -> {0,1,6,7}
```

This is an internal review of one local obstruction packet. It is not an
external independent review and it does not promote the aggregate A10
local-lemma layer beyond the existing review-pending status.

## Local Check

The packet has the selected-path self-edge proof shape: a selected-distance
equality path identifies one row-circle outer chord with a proper subinterval
chord, while vertex-circle monotonicity makes the outer chord strictly longer.

Rows `8`, `7`, and `2` force

```text
row 8: [1,8] = [7,8]
row 7: [7,8] = [2,7]
row 2: [2,7] = [1,2]
```

so

```text
[1,8] = [7,8] = [2,7] = [1,2].
```

At vertex `0`, the selected witnesses occur in angular order

```text
[1,2,4,8].
```

The chord `[1,8]` spans positions `0` to `3`, while `[1,2]` spans the proper
subinterval `0` to `1`. Strict convexity puts this inside an angle below `pi`,
so row `0` gives

```text
[1,8] > [1,2],
```

contradicting the equality chain.

Equivalently, the family creates a reflexive strict edge in the
selected-distance quotient graph. No strictly convex Euclidean configuration
can satisfy the displayed local core.

## Packet/Data Agreement

The stored packet, self-edge source packet, template catalog, and mini-replay
agree with the proof above:

- template/family: `T05/F10`;
- assignment ids: `A013`, `A029`, `A036`, `A038`, `A053`, `A057`, `A059`,
  `A062`, `A072`, `A088`, `A090`, `A100`, `A105`, `A120`, `A129`, `A133`,
  `A162`, `A170`;
- assignment counts: `F10: 18`, total `18`;
- core size: `4` selected rows;
- equality path length: `3` selected-distance equality steps, and path length
  `3` for all `18` focused packet assignments;
- strict edge: `F10` uses row `0` with outer pair `[1,8]` and inner pair
  `[1,2]`;
- replay status: the family packet replays to `self_edge`;
- strict edge count in the focused packet: `36`.

## Commands Run

```bash
python scripts/check_n9_vertex_circle_t05_self_edge_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_t05_self_edge_minireplay.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_self_edge_template_packet.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_template_lemma_catalog.py --check --assert-expected --json
python -m pytest tests/test_n9_vertex_circle_t05_self_edge_lemma_packet.py tests/test_n9_t05_self_edge_minireplay.py tests/test_n9_vertex_circle_self_edge_template_packet.py tests/test_n9_vertex_circle_template_lemma_catalog.py -q -m "artifact"
```

All commands passed.

## Review Boundary

This review supports only the following narrow statement:

```text
Any strictly convex configuration satisfying the T05/F10 local cyclic-order
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

Focused packet-soundness notes are now recorded for T01-T12. Aggregate A10
review, `n=9`, and global status all remain review-pending.
