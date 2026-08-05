# Fragile-cycle three-halo vertex-circle closure

Status: exact bounded abstract diagnostic and proof-mining aid. This note does
not claim a fragile-cycle forcing lemma, Euclidean realizability, a proof of
`n=10`, a general proof, or a counterexample.

## Question

The halo-lift frontier for the proper `23=27` seven-role quotient found that
two added halo roles are the first boundary admitting full selected-row
extensions. Its six `n=9` witnesses are all rejected by stored exact positive
circuits. The next finite question is whether three halo roles create an
abstract escape at `n=10`.

The retained quotient data are unchanged:

```text
centers: 1, 3, 4, 6
required witness pairs:
  1 -> {0,4}
  3 -> {4,5}
  4 -> {0,2}
  6 -> {2,5}
```

Exactly three canonically labelled halo roles are inserted into the seven
cyclic gaps. Nondecreasing three-element gap multisets give
`C(7+3-1,3) = 84` canonical placements.

## Exact search contract

For each placement, every retained center completes its required pair to a
self-excluding four-witness row. The four retained rows must satisfy:

- row intersection size at most two;
- proper chord crossing for every two-overlap;
- witness-pair multiplicity at most two;
- coverage of all ten labels; and
- an essential matching of retained rows to distinct covered labels.

Every essential cover is then extended exhaustively to one four-witness
selected row at every center, subject to the same intersection, crossing, and
witness-pair rules and selected indegree at most
`floor(2(10-1)/3) = 6`.

After every added extension row, the checker quotients the selected center-to-
witness distances and adds every strict nested-chord comparison. A branch is
rejected as soon as the strict quotient graph has a self-edge or a directed
cycle. Remaining centers are visited by deterministic
minimum-remaining-options order. No node or time cutoff is used.

The optimized status kernel is the repository's generic vertex-circle search
engine. The artifact also stores examples of both terminal obstruction types
and replays them through the separate quotient replay implementation.

## Result

| Quantity | Exact count |
| --- | ---: |
| Canonical three-halo placements | 84 |
| Raw retained-row combinations | 16,336,404 |
| Pair/crossing-compatible retained systems | 352,012 |
| Essential covers | 141,750 |
| Covers immediately giving a quotient self-edge | 5,544 |
| Covers immediately giving a strict cycle | 15,516 |
| Vertex-circle-clean covers entering extension search | 120,690 |
| Extension candidates tested | 420,682 |
| Full vertex-circle-clean selected-row systems | 0 |

The extension candidates split as follows:

| Candidate status after insertion | Exact count |
| --- | ---: |
| Still clean and recursively explored | 144,714 |
| Self-edge | 96,008 |
| Strict cycle | 179,960 |

All 120,690 initially clean covers exhaust their extension trees. The search
records 108,085 incidence dead ends after minimum-remaining-options selection,
and no complete clean assignment. The generated catalog includes all 84
placement summaries and a deterministic trace digest over every accepted
cover and tested extension candidate.

Therefore the fixed core has no escape with exactly three formal halo roles
under this selected-row and vertex-circle contract.

## Scope of the conclusion

This closes one finite abstract slice. It does not show that a genuine fragile
matching cycle forces the `23=27` core, that its four retained rows are selected
in a minimal counterexample, or that all genuine halo incidence reduces to
three formal roles. It says nothing about four or more halo roles. In
particular, it is not an `n=10` theorem: the search begins with one fixed
quotient core rather than enumerating all `n=10` selected-witness systems.

The proof-mining implication is narrower and useful:

```text
force the 23=27 core plus at most three controlled halo roles
    -> no full selected-row escape survives the vertex-circle quotient.
```

A Contract F lemma must still supply the geometric forcing step or a checked
alternative, and must engage the scalable and `Z/16` controls for the right
ordinary-distance reason.

## Replay

```bash
python scripts/check_fragile_cycle_three_halo_vertex_circle.py \
  --check --assert-expected --summary-json

python scripts/check_fragile_cycle_halo_lift_frontier.py \
  --check --assert-expected --summary-json
```

The generated artifact is
`data/certificates/fragile_cycle_three_halo_vertex_circle.json`; do not edit it
directly.
