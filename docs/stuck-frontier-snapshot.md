# Stuck-Frontier Snapshot

Status: exact fixed-selection diagnostics plus bounded search windows. No
general proof and no counterexample are claimed.

This note records the first pass of the fixed-selection stuck-set miner on the
currently live sparse frontier:

- `C19_skew`
- `C13_sidon_1_2_4_10`
- `C25_sidon_2_5_9_14`
- `C29_sidon_1_3_7_15`

The results are for the fixed selected rows in the natural label order. They do
not settle abstract cyclic-order realizability, and they do not certify any
Euclidean geometry.

## Commands

The compact table below is reproducible from:

```bash
python scripts/find_minimal_stuck_sets.py \
  --pattern C19_skew \
  --min-set-size 4 \
  --max-set-size 12 \
  --max-examples 2 \
  --json

python scripts/find_minimal_stuck_sets.py \
  --pattern C13_sidon_1_2_4_10 \
  --min-set-size 4 \
  --max-set-size 12 \
  --max-examples 2 \
  --json

python scripts/find_minimal_stuck_sets.py \
  --pattern C25_sidon_2_5_9_14 \
  --min-set-size 4 \
  --max-set-size 4 \
  --max-examples 1 \
  --fragile-cover-max-size 7 \
  --json

python scripts/find_minimal_stuck_sets.py \
  --pattern C29_sidon_1_3_7_15 \
  --min-set-size 4 \
  --max-set-size 4 \
  --max-examples 1 \
  --fragile-cover-max-size 8 \
  --json
```

The `C25` and `C29` fragile-cover searches stop at the first nontrivial window:
size `7` for `n=25`, and size `8` for `n=29`. These windows are incomplete
cover searches; `NONE<=k` means no incidence cover was found through size `k`,
not that no cover exists.

## Snapshot

| Pattern | n | max row overlap | `phi` edges | forward ear order | minimal fixed-row stuck size | stuck sets at min size | greedy terminal size | radius propagation | fragile-cover window |
|---|---:|---:|---:|---|---:|---:|---:|---|---|
| `C19_skew` | 19 | 1 | 0 | no | 4 | 3800 | 9 | `PASS_ACYCLIC_CHOICE` | min cover size 7, complete |
| `C13_sidon_1_2_4_10` | 13 | 1 | 0 | no | 4 | 663 | 7 | `PASS_ACYCLIC_CHOICE` | min cover size 4, complete |
| `C25_sidon_2_5_9_14` | 25 | 1 | 0 | no | 4 | 12550 | 9 | `PASS_ACYCLIC_CHOICE` | `NONE<=7`, incomplete |
| `C29_sidon_1_3_7_15` | 29 | 1 | 0 | no | 4 | 23635 | 7 | `PASS_ACYCLIC_CHOICE` | `NONE<=8`, incomplete |

## Reading

The frontier patterns are already adversarial to a naive fixed-row bridge:
none admits a forward ear order from a three-vertex seed, and all have many
size-4 stuck subsets. This is not by itself geometric evidence; it says these
selected rows are poor candidates for a simple peeling proof unless geometry
forces a different witness choice.

The current radius-propagation filter does not kill any of the four patterns.
In these sparse-overlap cases there are many consecutive witness pairs whose
selected-pair source list is empty, so the disjunctive strict-radius graph can
choose acyclic local gaps. The sharper witness-pair source diagnostic in
`docs/sparse-frontier-diagnostic.md` records that, in natural order, every
frontier row has an uncovered consecutive pair and the radius-propagation
filter admits an all-empty radius choice.

The fragile-cover snapshot is also not decisive. `C13` and `C19` have complete
incidence-level covers of sizes `4` and `7`, respectively. `C25` and `C29` have
no cover through the first nontrivial windows checked, but those are bounded
negative results only.

The useful conclusion is narrower: the live sparse/Sidon patterns remain a
good target for a new sparse-overlap exact filter. The current two-overlap,
minimum-radius, and radius-propagation filters do not see them.
