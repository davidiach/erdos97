# n=9 Vertex-circle Template Lemma-candidate Catalog

Status: `REVIEW_PENDING_DIAGNOSTIC_ONLY`.

This note records a derived catalog for proof search. It does not claim a
proof of `n=9`, does not claim a counterexample, does not complete independent
review of the exhaustive checker, and does not update the official/global
status.

## What is cataloged

The checked artifact
`data/certificates/n9_vertex_circle_template_lemma_catalog.json` combines the
two template packets:

- `data/certificates/n9_vertex_circle_self_edge_template_packet.json`
- `data/certificates/n9_vertex_circle_strict_cycle_template_packet.json`

The catalog has one record per replay-derived local-core template:

```text
templates:              12
self-edge templates:     9
strict-cycle templates:  3
families covered:       16
assignments covered:   184
```

Each self-edge catalog record summarizes the local-core shape that produces a
reflexive strict edge after selected-distance quotienting. Each strict-cycle
record summarizes the local-core shape that produces a directed strict cycle
after selected-distance quotienting. Template ids are deterministic artifact
labels for reviewer navigation and lemma mining; they are not theorem names.

## Commands

Generate and check the catalog:

```bash
python scripts/check_n9_vertex_circle_template_lemma_catalog.py \
  --assert-expected \
  --write

python scripts/check_n9_vertex_circle_template_lemma_catalog.py \
  --check \
  --assert-expected \
  --json
```

Run the targeted artifact tests:

```bash
python -m pytest tests/test_n9_vertex_circle_template_lemma_catalog.py -q -m "artifact"
```

## Review standard

Before any lemma is promoted from this catalog, a reviewer should restate its
incidence/order hypotheses without using template labels as theorem names,
then prove the quotient self-edge or strict-cycle conclusion directly from
those hypotheses. The catalog is intended to make that proof-mining pass
smaller; it is not itself an independent proof.
