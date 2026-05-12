# n=9 T10 Strict-cycle Mini-replay

Status: `REVIEW_PENDING_DIAGNOSTIC`.

This mini-replay is a deliberately small verifier for the focused T10/F12
strict-cycle local lemma packet. It does not enumerate `n=9` selected-witness
systems, does not review the full vertex-circle checker, does not prove `n=9`,
does not claim a counterexample, and does not update the global status of
Erdos Problem #97.

## Scope

The source packet is:

```bash
data/certificates/n9_vertex_circle_t10_strict_cycle_lemma_packet.json
```

The mini-replay reads that packet as input data and checks only:

- the four local selected rows for centers `0`, `3`, `6`, and `8`;
- the strict row-8 chord containment `[0,6] > [0,3]`;
- the connector path `[0,3] = [3,6] = [1,6]`;
- the strict row-3 chord containment `[1,6] > [0,1]`;
- the connector path `[0,1] = [0,6]`;
- that the two strict edges close a directed cycle after selected-distance
  quotienting.

This is intentionally independent of the larger quotient-replay helper and the
full exhaustive brancher. It is a second, smaller input-data replay of one
local strict-cycle lemma candidate.

## Artifact

```bash
data/certificates/n9_t10_strict_cycle_minireplay.json
```

Generate and check:

```bash
python scripts/check_n9_t10_strict_cycle_minireplay.py --write --assert-expected
python scripts/check_n9_t10_strict_cycle_minireplay.py --check --assert-expected --json
```

Targeted test:

```bash
python -m pytest tests/test_n9_t10_strict_cycle_minireplay.py -q
```

## Interpretation

The replay confirms that the packet data supports the local contradiction:

```text
[0,6] > [0,3] = [1,6]
[1,6] > [0,1] = [0,6]
```

Equivalently, the strict quotient graph contains the directed cycle

```text
[0,6] > [1,6] > [0,6].
```

This rules out only the exact local T10/F12 hypothesis packet. It is proof
mining scaffolding, not a finite-case completeness result.
