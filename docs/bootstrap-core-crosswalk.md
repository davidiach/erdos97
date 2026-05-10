# Bootstrap-Core Crosswalk

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note applies the rich-triple closure and private-halo capacity ledger from
`docs/bootstrap-core-bridge.md` to current fixed selected-row frontier motifs.
The checked artifact is:

```bash
python scripts/check_bootstrap_core_crosswalk.py --check --assert-expected
```

The generator writes:

```bash
python scripts/check_bootstrap_core_crosswalk.py --write --assert-expected
```

to `data/certificates/bootstrap_core_crosswalk.json`.

## Scope

The records use singleton rich classes: each selected row is treated as the
only rich class at its center. This makes the crosswalk a fixed-selection
diagnostic. Passing the bootstrap-core ledger is not a Euclidean realization
certificate, and positive capacity margin is not evidence for a counterexample.

The crosswalk covers:

- natural-order sparse fixed-row motifs `C13_sidon_1_2_4_10`, `C19_skew`,
  `C25_sidon_2_5_9_14`, and `C29_sidon_1_3_7_15`;
- the registered non-natural survivor orders for `C13_sidon_1_2_4_10` and
  `C19_skew`, retained as fixed-pattern provenance even though both abstract
  patterns are now killed across all cyclic orders by Kalmanson/Farkas
  certificates;
- the two non-ear-orderable `n=9` vertex-circle frontier assignments from the
  review-pending bridge-lemma frontier packet.

The existing base-apex D=3 incidence-capacity packet is included only as a
reference row. It records profile/capacity ledgers rather than full selected
rows or full rich classes, so it is not bootstrap-core audited here.

## Results

Every audited fixed-row order case has bootstrap rank greater than 3, so none
enters the ear-orderable bridge in this singleton-rich interpretation. The
weighted private-halo capacity ledger kills none of them.

| Case | n | minimum rank | first core | private pairs | cyclic capacity | margin | outside run lengths |
|---|---:|---:|---|---:|---:|---:|---|
| `C13_sidon_1_2_4_10:natural` | 13 | 4 | `[0,1,2,3]` | 6 | 36 | 30 | `[9]` |
| `C13_sidon_1_2_4_10:sample_full_filter_survivor` | 13 | 4 | `[0,1,2,3]` | 6 | 56 | 50 | `[6,2,1]` |
| `C19_skew:natural` | 19 | 5 | `[0,1,2,6,8]` | 19 | 134 | 115 | `[3,1,10]` |
| `C19_skew:vertex_circle_survivor` | 19 | 5 | `[0,1,2,6,8]` | 19 | 156 | 137 | `[5,5,4]` |
| `C25_sidon_2_5_9_14:natural` | 25 | 6 | `[0,1,3,4,7,8]` | 30 | 221 | 191 | `[1,2,16]` |
| `C29_sidon_1_3_7_15:natural` | 29 | 5 | `[0,2,8,17,23]` | 21 | 494 | 473 | `[1,5,8,5,5]` |
| `n9_vertex_circle_assignment_81:natural` | 9 | 4 | `[0,1,2,4]` | 6 | 14 | 8 | `[1,4]` |
| `n9_vertex_circle_assignment_151:natural` | 9 | 4 | `[0,1,2,4]` | 8 | 14 | 6 | `[1,4]` |

The small `n=9` assignments are the tightest current rows for this ledger:
their capacity margins are `8` and `6`. The sparse circulant cases have much
larger margins, so this private-pair ledger alone is too weak to explain their
known exact Kalmanson/Farkas obstructions.

A follow-up overlay joins these two tight `n=9` rows to the review-pending
vertex-circle strict-cycle certificate chain; see
`docs/bootstrap-vertex-circle-overlay.md`. Both rows land on the `T12/F16`
strict-cycle template by selected-row signature, but the strict-cycle local
row cores are not contained in the bootstrap core.

## Reading

The useful negative conclusion is narrow:

```text
singleton-rich fixed-row stuck motifs
  -> bootstrap rank > 3
  -> private-halo capacity still has slack
```

Thus the next bridge strengthening should not be "try the same capacity ledger
harder" on sparse singleton rows. It should add an exact ingredient that
reduces capacity or creates additional private-pair demand: for example,
metric/order restrictions on where private halos can sit, compatibility with
full rich-class alternatives, or a coupling to the vertex-circle/Kalmanson
quotient inequalities that already kill the retired sparse leads.

The base-apex D=3 reference remains a separate bookkeeping frontier: it has 88
representative packet rows, realizability state `UNKNOWN`, and incidence state
`UNKNOWN`. It needs full selected-row or full rich-class data before the
bootstrap-core checker can audit it directly.
