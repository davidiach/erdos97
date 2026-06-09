# n=9 Vertex-circle T12 Soundness Review - 2026-06-08

Status: `INTERNAL_REVIEW_NOTE`.

Claim scope: focused internal soundness review of the T12/F16 local
strict-cycle implication in
`docs/n9-vertex-circle-t12-strict-cycle-lemma.md`. This note does not prove
`n=9`, does not claim a counterexample, does not review the exhaustive
brancher, does not review all T01-T12 packets, and does not update the
official/global status of Erdos Problem #97.

## Outcome

Outcome: `accepted_packet_soundness_T12`.

The T12/F16 local implication is sound under exactly the displayed
hypotheses: natural cyclic order on labels `0,...,8` and the six selected
rows

```text
0 -> {1,3,6,7}
1 -> {2,4,7,8}
2 -> {0,3,5,8}
3 -> {0,1,4,6}
4 -> {1,2,5,7}
8 -> {0,2,5,6}
```

This is an internal review of one local obstruction packet. It is not an
external independent review and it does not promote the aggregate A10
local-lemma layer beyond the existing review-pending status.

This packet is bridge-facing because current bootstrap/T12 diagnostics land on
the T12/F16 template. The review here checks only the local contradiction once
the six displayed rows are genuinely available; it does not prove that any
minimal or rich-support counterexample must supply those rows.

## Local Check

Row `8` forces the selected-distance equality

```text
[0,8] = [2,8].
```

At vertex `2`, the selected witnesses occur in angular order

```text
[3,5,8,0].
```

The witnesses lie on the circle centered at `p_2`. The chord `[0,3]` spans
positions `0` to `3`, while `[0,8]` spans the proper subinterval `2` to `3`.
Strict convexity puts this inside an angle below `pi`, so row `2` gives

```text
[0,3] > [0,8].
```

Using row `8`, this becomes

```text
[0,3] > [2,8].                         (1)
```

Rows `4` and `1` force the selected-distance equality chain

```text
row 4: [2,4] = [1,4]
row 1: [1,4] = [1,7]
```

so

```text
[2,4] = [1,4] = [1,7].
```

At vertex `1`, the selected witnesses occur in angular order

```text
[2,4,7,8].
```

The chord `[2,8]` spans positions `0` to `3`, while `[2,4]` spans the proper
subinterval `0` to `1`. The same vertex-circle monotonicity gives

```text
[2,8] > [2,4].
```

Using the equality chain above, this gives

```text
[2,8] > [1,7].                         (2)
```

Row `3` forces the selected-distance equality

```text
[1,3] = [0,3].
```

At vertex `0`, the selected witnesses occur in angular order

```text
[1,3,6,7].
```

The chord `[1,7]` spans positions `0` to `3`, while `[1,3]` spans the proper
subinterval `0` to `1`. Therefore row `0` gives

```text
[1,7] > [1,3].
```

Using row `3`, this becomes

```text
[1,7] > [0,3].                         (3)
```

The inequalities (1), (2), and (3) form the directed strict cycle

```text
[0,3] > [2,8] > [1,7] > [0,3].
```

No strictly convex Euclidean configuration can satisfy a directed strict cycle
of ordinary distances after selected-distance quotienting.

## Packet/Data Agreement

The stored packet, strict-cycle source packet, template catalog, and
mini-replay agree with the proof above:

- template/family: `T12/F16`;
- assignment ids: `A082`, `A152`;
- assignment count: `2`;
- core centers: `0`, `1`, `2`, `3`, `4`, `8`;
- cycle length: `3`;
- equality chains: `[0,8] = [2,8]`, `[2,4] = [1,4] = [1,7]`, and
  `[1,3] = [0,3]`;
- strict edges: row `2` gives outer pair `[0,3]`, inner pair `[0,8]`; row
  `1` gives outer pair `[2,8]`, inner pair `[2,4]`; row `0` gives outer pair
  `[1,7]`, inner pair `[1,3]`;
- replay status: `strict_cycle`.

## Commands Run

```bash
python scripts/check_n9_vertex_circle_t12_strict_cycle_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_t12_strict_cycle_minireplay.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_strict_cycle_template_packet.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_template_lemma_catalog.py --check --assert-expected --json
python -m pytest tests/test_n9_vertex_circle_t12_strict_cycle_lemma_packet.py tests/test_n9_t12_strict_cycle_minireplay.py tests/test_n9_vertex_circle_strict_cycle_template_packet.py tests/test_n9_vertex_circle_template_lemma_catalog.py -q -m "artifact"
```

All commands passed.

## Review Boundary

This review supports only the following narrow statement:

```text
Any strictly convex configuration satisfying the T12/F16 local cyclic-order
and selected-row hypotheses is impossible by a selected-distance quotient
directed strict cycle.
```

It does not support any of the following stronger statements:

- all T01-T12 packets have been mathematically reviewed;
- the A10 local-lemma layer is fully reviewed;
- the 184-assignment frontier is complete;
- the vertex-circle strict-edge generator is fully reviewed;
- the bootstrap/T12 bridge row-forcing targets are proved;
- no bad nonagon exists as a promoted source-of-truth claim;
- Erdos Problem #97 is proved;
- a counterexample is produced or certified.

## Next Packet

The follow-up T11/F07 soundness review is now recorded, so the strict-cycle
packet family has one internal soundness note for each of T10, T11, and T12.
Focused packet-soundness notes are now recorded for T01-T12, while aggregate
A10 review, `n=9`, and global status all remain review-pending.
