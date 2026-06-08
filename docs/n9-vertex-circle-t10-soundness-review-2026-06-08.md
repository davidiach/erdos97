# n=9 Vertex-circle T10 Soundness Review - 2026-06-08

Status: `INTERNAL_REVIEW_NOTE`.

Claim scope: focused internal soundness review of the T10/F12 local
strict-cycle implication in
`docs/n9-vertex-circle-t10-strict-cycle-lemma.md`. This note does not prove
`n=9`, does not claim a counterexample, does not review the exhaustive
brancher, does not review all T01-T12 packets, and does not update the
official/global status of Erdos Problem #97.

## Outcome

Outcome: `accepted_packet_soundness_T10`.

The T10/F12 local implication is sound under exactly the displayed
hypotheses: natural cyclic order on labels `0,...,8` and the four selected
rows

```text
0 -> {1,2,5,6}
3 -> {0,1,4,6}
6 -> {1,3,4,7}
8 -> {0,3,6,7}
```

This is an internal review of one local obstruction packet. It is not an
external independent review and it does not promote the aggregate A10
local-lemma layer beyond the existing review-pending status.

## Local Check

Rows `3` and `6` force the selected-distance equality chain

```text
row 3: [0,3] = [3,6]
row 6: [3,6] = [1,6]
```

so

```text
[0,3] = [3,6] = [1,6].
```

At vertex `8`, the selected witnesses occur in angular order

```text
[0,3,6,7].
```

The witnesses lie on the circle centered at `p_8`. The chord `[0,6]` spans
positions `0` to `2`, while `[0,3]` spans the proper subinterval `0` to `1`.
Strict convexity puts this inside an angle below `pi`, so row `8` gives

```text
[0,6] > [0,3].
```

Using the equality chain above, this gives

```text
[0,6] > [1,6].                         (1)
```

Row `0` forces the selected-distance equality

```text
[0,1] = [0,6].
```

At vertex `3`, the selected witnesses occur in angular order

```text
[4,6,0,1].
```

The chord `[1,6]` spans positions `1` to `3`, while `[0,1]` spans the proper
subinterval `2` to `3`. The same vertex-circle monotonicity gives

```text
[1,6] > [0,1].
```

Using row `0`, this becomes

```text
[1,6] > [0,6].                         (2)
```

The inequalities (1) and (2) form the directed strict cycle

```text
[0,6] > [1,6] > [0,6].
```

Using the packet's canonical selected-distance quotient representatives, this
is the two-class cycle

```text
[0,1] > [0,3] > [0,1].
```

No strictly convex Euclidean configuration can satisfy a directed strict cycle
of ordinary distances after selected-distance quotienting.

## Packet/Data Agreement

The stored packet, strict-cycle source packet, template catalog, mini-replay,
and paired-square diagnostic agree with the proof above:

- template/family: `T10/F12`;
- assignment ids: `A020`, `A040`, `A047`, `A071`, `A080`, `A081`, `A083`,
  `A093`, `A095`, `A111`, `A126`, `A147`, `A151`, `A153`, `A154`, `A157`,
  `A164`, `A180`;
- assignment count: `18`;
- core centers: `0`, `3`, `6`, `8`;
- cycle length: `2`;
- equality chains: `[0,3] = [3,6] = [1,6]` and `[0,1] = [0,6]`;
- strict edges: row `8` gives outer pair `[0,6]`, inner pair `[0,3]`; row
  `3` gives outer pair `[1,6]`, inner pair `[0,1]`;
- replay status: `strict_cycle`;
- paired-square companion audit: all `18` T10 assignments have a representative
  paired-square entry, with `54` total entries.

The paired-square audit is diagnostic corroboration only. The local soundness
acceptance above relies on the selected-row equalities, the two
vertex-circle strict inequalities, and the quotient-cycle closure.

## Commands Run

```bash
python scripts/check_n9_vertex_circle_t10_strict_cycle_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_t10_strict_cycle_minireplay.py --check --assert-expected --json
python scripts/check_n9_t10_paired_square_entry.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_strict_cycle_template_packet.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_template_lemma_catalog.py --check --assert-expected --json
python -m pytest tests/test_n9_vertex_circle_t10_strict_cycle_lemma_packet.py tests/test_n9_t10_strict_cycle_minireplay.py tests/test_n9_t10_paired_square_entry.py tests/test_n9_vertex_circle_strict_cycle_template_packet.py tests/test_n9_vertex_circle_template_lemma_catalog.py -q -m "artifact"
```

All commands passed.

## Review Boundary

This review supports only the following narrow statement:

```text
Any strictly convex configuration satisfying the T10/F12 local cyclic-order
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

The follow-up T11/F07 and T12/F16 soundness reviews are now recorded, so the
strict-cycle packet family has one internal soundness note for each of T10,
T11, and T12. The remaining focused local-lemma packet soundness review
targets are the self-edge packets T04-T09.
