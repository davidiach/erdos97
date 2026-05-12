# n=9 T01 Self-edge Mini-replay

Status: `REVIEW_PENDING_DIAGNOSTIC`.

This mini-replay is a deliberately small verifier for the focused T01/F09
self-edge local lemma packet. It does not enumerate `n=9` selected-witness
systems, does not review the full vertex-circle checker, does not prove `n=9`,
does not claim a counterexample, and does not update the global status of
Erdos Problem #97.

## Scope

The source packet is:

```bash
data/certificates/n9_vertex_circle_t01_self_edge_lemma_packet.json
```

The mini-replay reads that packet as input data and checks only:

- the three local selected rows for centers `0`, `1`, and `2`;
- the selected-distance equality chain
  `[1,8] = [0,1] = [0,2] = [1,2]`;
- the row-0 witness order `[1,2,4,8]`;
- that chord `[1,8]` strictly contains chord `[1,2]` in that row order;
- that the strict outer and inner chord pairs are the endpoints of the same
  selected-distance equality chain.

This is intentionally independent of the larger quotient-replay helper and the
full exhaustive brancher. It is a second, smaller input-data replay of one
local lemma candidate.

## Artifact

```bash
data/certificates/n9_t01_self_edge_minireplay.json
```

Generate and check:

```bash
python scripts/check_n9_t01_self_edge_minireplay.py --write --assert-expected
python scripts/check_n9_t01_self_edge_minireplay.py --check --assert-expected --json
```

Targeted test:

```bash
python -m pytest tests/test_n9_t01_self_edge_minireplay.py -q
```

## Interpretation

The replay confirms that the packet data supports the local contradiction:

```text
[1,8] = [1,2]
[1,8] > [1,2]
```

This rules out only the exact local T01/F09 hypothesis packet. It is proof
mining scaffolding, not a finite-case completeness result.
