# n=9 Vertex-circle T10 Strict-cycle Local Lemma Packet

Status: `REVIEW_PENDING_DIAGNOSTIC_ONLY`.

This note records one focused proof-mining packet for the single-family `T10`
strict-cycle motif. It does not claim a proof of `n=9`, does not claim a
counterexample, does not complete independent review of the exhaustive
checker, and does not update the official/global status.

## Packet scope

The checked artifact is
`data/certificates/n9_vertex_circle_t10_strict_cycle_lemma_packet.json`.
It is derived from:

- `data/certificates/n9_vertex_circle_strict_cycle_template_packet.json`
- `data/certificates/n9_vertex_circle_template_lemma_catalog.json`

The packet covers 18 assignment ids in one family:

```text
F12: 18 assignments
```

The family has a four-row core and replays to a directed strict cycle with 36
strict edges, two cycle edges, and no self-edge conflict. The local obstruction
is a two-step quotient cycle, not a reflexive self-edge.

## Family core

`F12`:

```text
[0, 1, 2, 5, 6]
[3, 0, 1, 4, 6]
[6, 1, 3, 4, 7]
[8, 0, 3, 6, 7]

strict: [0, 6] > [0, 3] from row 8
path:   [0, 3] -> [3, 6] -> [1, 6]

strict: [1, 6] > [0, 1] from row 3
path:   [0, 1] -> [0, 6]
```

Thus the packet isolates the directed cycle

```text
[0, 6] > [0, 3] = [3, 6] = [1, 6] > [0, 1] = [0, 6].
```

## Commands

Generate and check the packet:

```bash
python scripts/check_n9_vertex_circle_t10_strict_cycle_lemma_packet.py \
  --assert-expected \
  --write

python scripts/check_n9_vertex_circle_t10_strict_cycle_lemma_packet.py \
  --check \
  --assert-expected \
  --json
```

Run the targeted artifact tests:

```bash
python -m pytest tests/test_n9_vertex_circle_t10_strict_cycle_lemma_packet.py -q -m "artifact"
```

## Review standard

Before treating this as a reusable local lemma, a reviewer should restate the
incidence and cyclic-order hypotheses without relying on `T10` as a theorem
name, then prove directly for the `F12` core that the listed rows force the two
strict inequalities and the two connector chains. The packet is a small replay
aid for that review, not an independent proof of the `n=9` case.
