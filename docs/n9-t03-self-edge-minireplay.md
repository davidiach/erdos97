# n=9 T03 Self-edge Mini-replay

Status: `REVIEW_PENDING_DIAGNOSTIC`.

This mini-replay is a deliberately small verifier for the focused T03
multi-family self-edge local lemma packet. It does not enumerate `n=9`
selected-witness systems, does not review the full vertex-circle checker, does
not prove `n=9`, does not claim a counterexample, and does not update the
global status of Erdos Problem #97.

## Scope

The source packet is:

```bash
data/certificates/n9_vertex_circle_t03_self_edge_lemma_packet.json
```

The mini-replay reads that packet as input data and checks only:

- the two stored T03 family packets `F05` and `F15`;
- each family's four local selected rows;
- each selected-distance equality chain of length `3`;
- each listed vertex-circle witness order;
- that the listed outer chord properly contains the inner chord in that row
  order;
- that every strict outer and inner chord pair is joined by the same
  selected-distance equality chain.

This is intentionally independent of the larger quotient-replay helper and the
full exhaustive brancher. It is a second, smaller input-data replay of one
multi-family local lemma candidate.

## Artifact

```bash
data/certificates/n9_t03_self_edge_minireplay.json
```

Generate and check:

```bash
python scripts/check_n9_t03_self_edge_minireplay.py --write --assert-expected
python scripts/check_n9_t03_self_edge_minireplay.py --check --assert-expected --json
```

Targeted test:

```bash
python -m pytest tests/test_n9_t03_self_edge_minireplay.py -q
```

## Interpretation

The replay confirms that each stored T03 family packet supports the local
contradiction shape:

```text
outer pair = inner pair
outer pair > inner pair
```

This covers only the exact T03 family packets listed above. It is proof-mining
scaffolding, not a finite-case completeness result.
