# n=9 Vertex-circle T01 Self-edge Local Lemma Packet

Status: `REVIEW_PENDING_DIAGNOSTIC_ONLY`.

This note records one focused proof-mining packet for the `T01/F09`
self-edge motif. It does not claim a proof of `n=9`, does not claim a
counterexample, does not complete independent review of the exhaustive
checker, and does not update the official/global status.

## Packet scope

The checked artifact is
`data/certificates/n9_vertex_circle_t01_self_edge_lemma_packet.json`.
It is derived from:

- `data/certificates/n9_vertex_circle_self_edge_template_packet.json`
- `data/certificates/n9_vertex_circle_template_lemma_catalog.json`

The packet covers the six T01 assignment ids:

```text
A014, A024, A031, A140, A166, A175
```

The local core is the family `F09` three-row certificate:

```text
[0, 1, 2, 4, 8]
[1, 0, 3, 5, 8]
[2, 0, 1, 4, 6]
```

For row `0`, the witness order `[1, 2, 4, 8]` gives the strict
vertex-circle inequality

```text
[1, 8] > [1, 2]
```

The selected-distance equality path is:

```text
[1, 8] -- row 1 --> [0, 1]
[0, 1] -- row 0 --> [0, 2]
[0, 2] -- row 2 --> [1, 2]
```

Thus the packet isolates a local self-edge shape: a strict edge from a
selected-distance quotient class back to itself.

## Commands

Generate and check the packet:

```bash
python scripts/check_n9_vertex_circle_t01_self_edge_lemma_packet.py \
  --assert-expected \
  --write

python scripts/check_n9_vertex_circle_t01_self_edge_lemma_packet.py \
  --check \
  --assert-expected \
  --json
```

Run the targeted artifact tests:

```bash
python -m pytest tests/test_n9_vertex_circle_t01_self_edge_lemma_packet.py -q -m "artifact"
```

## Review standard

Before treating this as a reusable local lemma, a reviewer should restate the
incidence and cyclic-order hypotheses without relying on `T01` as a theorem
name, then prove directly that the three rows force the displayed equality
path and that row `0` gives the displayed strict inequality. The packet is a
small replay aid for that review, not an independent proof of the `n=9` case.
