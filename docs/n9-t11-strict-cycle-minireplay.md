# n=9 T11 Strict-cycle Mini-replay

Status: `REVIEW_PENDING_DIAGNOSTIC`.

This mini-replay is a deliberately small verifier for the focused T11/F07
strict-cycle local lemma packet. It does not enumerate `n=9` selected-witness
systems, does not review the full vertex-circle checker, does not prove `n=9`,
does not claim a counterexample, and does not update the global status of
Erdos Problem #97.

## Scope

The source packet is:

```bash
data/certificates/n9_vertex_circle_t11_strict_cycle_lemma_packet.json
```

The mini-replay reads that packet as input data and checks only:

- the four local selected rows for centers `0`, `1`, `5`, and `6`;
- the strict row-1 chord containment `[0,2] > [0,3]`;
- the identity connector path `[0,3] = [0,3]`;
- the strict row-1 chord containment `[0,3] > [0,5]`;
- the connector path `[0,5] = [5,7]`;
- the strict row-6 chord containment `[5,7] > [1,5]`;
- the connector path `[1,5] = [0,1] = [0,2]`;
- that the three strict edges close a directed cycle after selected-distance
  quotienting.

This is intentionally independent of the larger quotient-replay helper and the
full exhaustive brancher. It is a second, smaller input-data replay of one
local strict-cycle lemma candidate.

## Artifact

```bash
data/certificates/n9_t11_strict_cycle_minireplay.json
```

Generate and check:

```bash
python scripts/check_n9_t11_strict_cycle_minireplay.py --write --assert-expected
python scripts/check_n9_t11_strict_cycle_minireplay.py --check --assert-expected --json
```

Targeted test:

```bash
python -m pytest tests/test_n9_t11_strict_cycle_minireplay.py -q
```

## Interpretation

The replay confirms that the packet data supports the local contradiction:

```text
[0,2] > [0,3] = [0,3]
[0,3] > [0,5] = [5,7]
[5,7] > [1,5] = [0,2]
```

Equivalently, the strict quotient graph contains the directed cycle

```text
[0,2] > [0,3] > [5,7] > [0,2].
```

This rules out only the exact local T11/F07 hypothesis packet. It is proof
mining scaffolding, not a finite-case completeness result.
