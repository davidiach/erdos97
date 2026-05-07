# n=9 Vertex-circle T12 Strict-cycle Local Lemma Packet

Status: `REVIEW_PENDING_DIAGNOSTIC_ONLY`.

This note records one focused proof-mining packet for the single-family `T12`
strict-cycle motif. It does not claim a proof of `n=9`, does not claim a
counterexample, does not complete independent review of the exhaustive
checker, and does not update the official/global status.

## Packet scope

The checked artifact is
`data/certificates/n9_vertex_circle_t12_strict_cycle_lemma_packet.json`.
It is derived from:

- `data/certificates/n9_vertex_circle_strict_cycle_template_packet.json`
- `data/certificates/n9_vertex_circle_template_lemma_catalog.json`

The packet covers 2 assignment ids in one family:

```text
F16: 2 assignments
```

The family has a six-row core and replays to a directed strict cycle with 54
strict edges, three cycle edges, and no self-edge conflict. The local
obstruction is a three-step quotient cycle, not a reflexive self-edge.

## Family core

`F16`:

```text
[0, 1, 3, 6, 7]
[1, 2, 4, 7, 8]
[2, 0, 3, 5, 8]
[3, 0, 1, 4, 6]
[4, 1, 2, 5, 7]
[8, 0, 2, 5, 6]

strict: [0, 3] > [0, 8] from row 2
path:   [0, 8] -> [2, 8]

strict: [2, 8] > [2, 4] from row 1
path:   [2, 4] -> [1, 4] -> [1, 7]

strict: [1, 7] > [1, 3] from row 0
path:   [1, 3] -> [0, 3]
```

Thus the packet isolates the directed cycle

```text
[0, 3] > [0, 8] = [2, 8] > [2, 4] = [1, 4] = [1, 7] > [1, 3] = [0, 3].
```

## Commands

Generate and check the packet:

```bash
python scripts/check_n9_vertex_circle_t12_strict_cycle_lemma_packet.py \
  --assert-expected \
  --write

python scripts/check_n9_vertex_circle_t12_strict_cycle_lemma_packet.py \
  --check \
  --assert-expected \
  --json
```

Run the targeted artifact tests:

```bash
python -m pytest tests/test_n9_vertex_circle_t12_strict_cycle_lemma_packet.py -q -m "artifact"
```

## Review standard

Before treating this as a reusable local lemma, a reviewer should restate the
incidence and cyclic-order hypotheses without relying on `T12` as a theorem
name, then prove directly for the `F16` core that the listed rows force the
three strict inequalities and the three nonempty connector chains. The packet
is a small replay aid for that review, not an independent proof of the `n=9`
case.
