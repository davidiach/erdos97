# n=9 Vertex-circle T03 Self-edge Local Lemma Packet

Status: `REVIEW_PENDING_DIAGNOSTIC_ONLY`.

This note records one focused proof-mining packet for the multi-family `T03`
self-edge motif. It does not claim a proof of `n=9`, does not claim a
counterexample, does not complete independent review of the exhaustive
checker, and does not update the official/global status.

## Packet scope

The checked artifact is
`data/certificates/n9_vertex_circle_t03_self_edge_lemma_packet.json`.
It is derived from:

- `data/certificates/n9_vertex_circle_self_edge_template_packet.json`
- `data/certificates/n9_vertex_circle_template_lemma_catalog.json`

The packet covers 20 assignment ids across two families:

```text
F05: 18 assignments
F15:  2 assignments
```

Each family has a four-row core and replays to a single self-edge conflict
with 36 strict edges and no strict cycle. The selected-distance equality path
still has three steps, so reviewers should keep the four selected rows separate
from the three equality edges.

## Family cores

`F05`:

```text
[1, 2, 5, 7, 8]
[2, 1, 3, 4, 8]
[3, 0, 2, 4, 7]
[6, 1, 3, 5, 7]
strict: [3, 7] > [1, 7] from row 6
path:   [3, 7] -> [2, 3] -> [1, 2] -> [1, 7]
```

`F15`:

```text
[0, 1, 3, 4, 8]
[1, 0, 2, 4, 5]
[2, 1, 3, 5, 6]
[3, 2, 4, 6, 7]
strict: [1, 4] > [3, 4] from row 0
path:   [1, 4] -> [1, 2] -> [2, 3] -> [3, 4]
```

Thus the packet isolates a reusable-looking local self-edge shape: each family
forces a strict edge from a selected-distance quotient class back to itself.

## Commands

Generate and check the packet:

```bash
python scripts/check_n9_vertex_circle_t03_self_edge_lemma_packet.py \
  --assert-expected \
  --write

python scripts/check_n9_vertex_circle_t03_self_edge_lemma_packet.py \
  --check \
  --assert-expected \
  --json
```

Run the targeted artifact tests:

```bash
python -m pytest tests/test_n9_vertex_circle_t03_self_edge_lemma_packet.py -q -m "artifact"
```

## Review standard

Before treating this as a reusable local lemma, a reviewer should restate the
incidence and cyclic-order hypotheses without relying on `T03` as a theorem
name, then prove directly for each of the two family cores that the listed
rows force the displayed equality path and strict inequality. The packet is a
small replay aid for that review, not an independent proof of the `n=9` case.
