# n=9 Vertex-circle T02 Self-edge Local Lemma Packet

Status: `REVIEW_PENDING_DIAGNOSTIC_ONLY`.

This note records one focused proof-mining packet for the multi-family `T02`
self-edge motif. It does not claim a proof of `n=9`, does not claim a
counterexample, does not complete independent review of the exhaustive
checker, and does not update the official/global status.

## Packet scope

The checked artifact is
`data/certificates/n9_vertex_circle_t02_self_edge_lemma_packet.json`.
It is derived from:

- `data/certificates/n9_vertex_circle_self_edge_template_packet.json`
- `data/certificates/n9_vertex_circle_template_lemma_catalog.json`

The packet covers 40 assignment ids across four families:

```text
F01: 18 assignments
F04: 18 assignments
F08:  2 assignments
F14:  2 assignments
```

Each family has a three-row core and replays to a single self-edge conflict
with 27 strict edges and no strict cycle.

## Family cores

`F01`:

```text
[0, 1, 2, 3, 8]
[1, 0, 2, 4, 7]
[8, 0, 1, 4, 5]
strict: [1, 8] > [1, 2] from row 0
path:   [1, 8] -> [0, 8] -> [0, 1] -> [1, 2]
```

`F04`:

```text
[0, 1, 2, 4, 6]
[1, 0, 2, 3, 5]
[2, 1, 3, 4, 8]
strict: [0, 2] > [2, 3] from row 1
path:   [0, 2] -> [0, 1] -> [1, 2] -> [2, 3]
```

`F08`:

```text
[0, 1, 2, 4, 8]
[1, 0, 2, 3, 5]
[8, 0, 1, 3, 7]
strict: [1, 8] > [1, 2] from row 0
path:   [1, 8] -> [0, 8] -> [0, 1] -> [1, 2]
```

`F14`:

```text
[0, 1, 2, 6, 8]
[1, 0, 2, 3, 7]
[8, 0, 1, 5, 7]
strict: [1, 8] > [1, 2] from row 0
path:   [1, 8] -> [0, 8] -> [0, 1] -> [1, 2]
```

Thus the packet isolates a reusable-looking local self-edge shape: each family
forces a strict edge from a selected-distance quotient class back to itself.

## Commands

Generate and check the packet:

```bash
python scripts/check_n9_vertex_circle_t02_self_edge_lemma_packet.py \
  --assert-expected \
  --write

python scripts/check_n9_vertex_circle_t02_self_edge_lemma_packet.py \
  --check \
  --assert-expected \
  --json
```

Run the targeted artifact tests:

```bash
python -m pytest tests/test_n9_vertex_circle_t02_self_edge_lemma_packet.py -q -m "artifact"
```

## Review standard

Before treating this as a reusable local lemma, a reviewer should restate the
incidence and cyclic-order hypotheses without relying on `T02` as a theorem
name, then prove directly for each of the four family cores that the listed
rows force the displayed equality path and strict inequality. The packet is a
small replay aid for that review, not an independent proof of the `n=9` case.
