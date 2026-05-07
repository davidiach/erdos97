# n=9 Vertex-circle T11 Strict-cycle Local Lemma Packet

Status: `REVIEW_PENDING_DIAGNOSTIC_ONLY`.

This note records one focused proof-mining packet for the single-family `T11`
strict-cycle motif. It does not claim a proof of `n=9`, does not claim a
counterexample, does not complete independent review of the exhaustive
checker, and does not update the official/global status.

## Packet scope

The checked artifact is
`data/certificates/n9_vertex_circle_t11_strict_cycle_lemma_packet.json`.
It is derived from:

- `data/certificates/n9_vertex_circle_strict_cycle_template_packet.json`
- `data/certificates/n9_vertex_circle_template_lemma_catalog.json`

The packet covers 6 assignment ids in one family:

```text
F07: 6 assignments
```

The family has a four-row core and replays to a directed strict cycle with 36
strict edges, three cycle edges, and no self-edge conflict. The local
obstruction is a three-step quotient cycle, not a reflexive self-edge.

## Family core

`F07`:

```text
[0, 1, 2, 4, 8]
[1, 0, 2, 3, 5]
[5, 0, 3, 4, 7]
[6, 1, 5, 7, 8]

strict: [0, 2] > [0, 3] from row 1
empty connector: [0, 3] = [0, 3]

strict: [0, 3] > [0, 5] from row 1
path:   [0, 5] -> [5, 7]

strict: [5, 7] > [1, 5] from row 6
path:   [1, 5] -> [0, 1] -> [0, 2]
```

Thus the packet isolates the directed cycle

```text
[0, 2] > [0, 3] = [0, 3] > [0, 5] = [5, 7] > [1, 5] = [0, 1] = [0, 2].
```

## Commands

Generate and check the packet:

```bash
python scripts/check_n9_vertex_circle_t11_strict_cycle_lemma_packet.py \
  --assert-expected \
  --write

python scripts/check_n9_vertex_circle_t11_strict_cycle_lemma_packet.py \
  --check \
  --assert-expected \
  --json
```

Run the targeted artifact tests:

```bash
python -m pytest tests/test_n9_vertex_circle_t11_strict_cycle_lemma_packet.py -q -m "artifact"
```

## Review standard

Before treating this as a reusable local lemma, a reviewer should restate the
incidence and cyclic-order hypotheses without relying on `T11` as a theorem
name, then prove directly for the `F07` core that the listed rows force the
three strict inequalities, the two nonempty connector chains, and the one
empty identity connector. The packet is a small replay aid for that review, not
an independent proof of the `n=9` case.
