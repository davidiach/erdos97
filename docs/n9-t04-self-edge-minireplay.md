# n=9 T04/F13 Self-edge Mini-replay

Status: `REVIEW_PENDING_DIAGNOSTIC`.

This mini-replay is a deliberately small verifier for the focused T04/F13
self-edge local lemma packet. It does not enumerate `n=9` selected-witness
systems, does not review the full vertex-circle checker, does not prove `n=9`,
does not claim a counterexample, and does not update the global status of
Erdos Problem #97.

## Scope

The source packet is:

```bash
data/certificates/n9_vertex_circle_t04_self_edge_lemma_packet.json
```

The mini-replay reads that packet as input data and checks only:

- the stored T04 family packet `F13`;
- its four local selected rows;
- its selected-distance equality chain of length `3`;
- its listed vertex-circle witness order;
- that the listed outer chord properly contains the inner chord in that row
  order;
- that the strict outer and inner chord pairs are joined by the same
  selected-distance equality chain.

This is intentionally independent of the larger quotient-replay helper and the
full exhaustive brancher. It is a second, smaller input-data replay of one
focused local lemma candidate.

## Artifact

```bash
data/certificates/n9_t04_self_edge_minireplay.json
```

Generate and check:

```bash
python scripts/check_n9_t04_self_edge_minireplay.py --write --assert-expected
python scripts/check_n9_t04_self_edge_minireplay.py --check --assert-expected --json
```

Targeted test:

```bash
python -m pytest tests/test_n9_t04_self_edge_minireplay.py -q
```

## Interpretation

The replay confirms that the stored T04/F13 packet supports the local
contradiction shape:

```text
outer pair = inner pair
outer pair > inner pair
```

This covers only the exact T04/F13 family packet listed above. It is
proof-mining scaffolding, not a finite-case completeness result.
