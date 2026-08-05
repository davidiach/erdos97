# Fragile-cycle three-halo deep frontier

Status: exact bounded local-certificate compression. This note does not claim
a geometric forcing lemma, Euclidean realizability, a proof of `n=10`, a
general proof, or a counterexample.

## Purpose

The complete fixed three-halo scan closes 141,750 essential retained covers,
but that aggregate count hides the structure of its final search layers. This
packet asks a narrower proof-mining question:

```text
How many vertex-circle-clean partial systems reach eight selected rows,
and why can none receive the final two rows?
```

The checker instruments the original exhaustive traversal without changing
its branch order. Its recomputed source trace is required to equal
`06132f8cf83fa5015596a1d384c5cdff5aa90d857cd66a5c264392a1bdae2c56`,
the trace pinned by the complete three-halo artifact.

## Exact depth profile

The first status obtained after each selected-row insertion is:

| Selected rows | Clean | Self-edge | Strict cycle |
| ---: | ---: | ---: | ---: |
| 4 | 120,690 | 5,544 | 15,516 |
| 5 | 116,374 | 28,179 | 87,592 |
| 6 | 27,054 | 53,837 | 80,165 |
| 7 | 1,273 | 13,584 | 11,992 |
| 8 | 13 | 406 | 211 |
| 9 | 0 | 2 | 0 |

Only thirteen clean eight-row states survive. They occur in seven of the 84
canonical halo placements:

```text
(0,0,0), (0,1,5), (0,3,5), (0,5,6),
(1,1,6), (1,2,5), (2,2,5)
```

All thirteen states are distinct even after arbitrary rotation or reflection
of the ten natural cyclic labels.

## Compact terminal lemma

Within the fixed source-search contract, every clean eight-row frontier state
satisfies exactly one of the following alternatives.

1. **Crossing-dead alternative.** Eleven states have an unassigned center with
   no admissible four-witness row. Across their eleven deterministic dead-center
   certificates, all `11 * C(9,4) = 1,386` candidate rows already fail the
   row-intersection or proper two-overlap crossing rule. Selected-indegree and
   witness-pair capacities reject none of those candidates.
2. **Forced-row alternative.** The other two states have a unique row at the
   minimum-remaining-options center. Adding it gives a quotient self-edge for
   the complete nine-row partial assignment. Exhausting its row subsets shows
   that the minimum obstruction width is exactly three. The packet stores all
   six minimum cores: two replay as self-edges and four as strict cycles.

Thus the last two layers do not require a large opaque search tree. They reduce
to eleven crossing-dead ledgers and six independently replayable three-row
vertex-circle cores.

The statement is reusable as a regression lemma for this exact quotient and
three-halo contract. It is not a universal lemma about all fragile cycles:
the thirteen deep states themselves are a finite catalog, not one forced
geometric template.

## Certificate structure

For every clean eight-row state, the generated artifact stores:

- the halo gaps and cyclic order;
- selected rows in natural and original quotient labels;
- both remaining centers and their exact admissible-option counts;
- an independent quotient replay confirming that the eight rows are clean;
- either a 126-option rejection ledger at a dead center, or the unique forced
  ninth row and its independent obstruction replay.

For the two forced-row states it additionally stores every minimum-width core,
including the exact self-edge conflict or directed cycle returned by the
independent quotient replay.

## Scope

This packet compresses the final layers of one already bounded enumeration.
It does not force the `23=27` core, its retained rows, or any halo placement
from minimal-counterexample geometry. It does not cover four or more halo
roles. The next genuine Contract F step remains a geometric reason that lands
inside this core/halo packet or forces a separately checked alternative.

## Natural-order metric follow-up

The exact follow-up in
`docs/fragile-cycle-three-halo-kalmanson-endgame.md` shows that every one of
the thirteen states already contains a natural-order Kalmanson obstruction on
exactly three selected rows. Eleven use one strict self-edge; two use exact
two-inequality inverse pairs. That packet replaces the incidence/ninth-row
terminal split by a uniform convex-metric endgame, while remaining conditional
on this fixed source catalog.

## Replay

```bash
python scripts/check_fragile_cycle_three_halo_deep_frontier.py \
  --check --assert-expected --summary-json

python scripts/check_fragile_cycle_three_halo_kalmanson_endgame.py \
  --check --assert-expected --summary-json

python scripts/check_fragile_cycle_three_halo_vertex_circle.py \
  --check --assert-expected --summary-json
```

The generated artifact is
`data/certificates/fragile_cycle_three_halo_deep_frontier.json`; do not edit it
directly.
