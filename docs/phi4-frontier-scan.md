# Phi4 Frontier Scan

Status: `FIXED_ORDER_EXACT_FILTER_DIAGNOSTIC`.

This note records the first reusable sweep of the phi 4-cycle rectangle-trap
filter over registered fixed patterns and fixed cyclic orders. It does not
claim a general proof, an `n=9` completeness result, or a counterexample.

## Scope

The scan covers:

- the registered positive `n=9` rectangle-trap pattern from
  `data/certificates/n9_phi4_rectangle_trap.json`;
- every built-in candidate pattern in natural cyclic order;
- the registered sparse non-natural orders in
  `data/certificates/sparse_order_survivors.json`.

For each case, the scanner records the number of `phi` edges, directed
`phi` 4-cycles, and exact rectangle-trap certificates.

## Current Result

The generated artifact is
`data/certificates/phi4_frontier_scan.json`.

It contains 17 fixed-order cases. The only positive hit is the registered
`n=9` fixed selected-witness pattern:

```text
N9_phi4_rectangle_trap_selected_witness_pattern:natural_order
```

with directed cycle

```text
{0,6} -> {2,8} -> {1,5} -> {4,7} -> {0,6}.
```

All built-in natural-order catalog patterns and the two registered sparse
non-natural orders have zero rectangle-trap certificates in this sweep. This is
useful negative filter information only. A miss by this filter is not evidence
of geometric realizability.

The sparse registered orders remain invisible to this filter because they have
no `phi` edges:

```text
C13_sidon_1_2_4_10:sample_full_filter_survivor
C19_skew:vertex_circle_survivor
```

That confirms the same sparse/Sidon blind spot recorded by the metric-order and
Ptolemy diagnostics.

## Reproduction

```bash
python scripts/check_phi4_frontier_scan.py --assert-expected
python scripts/check_phi4_frontier_scan.py --assert-expected --write
python -m pytest tests/test_phi4_frontier.py -q
```

The `--write` command regenerates
`data/certificates/phi4_frontier_scan.json`.
