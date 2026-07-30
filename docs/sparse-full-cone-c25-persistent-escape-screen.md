# C25 persistent-escape full-cone screen

Status: exact full-cone obstructions for two fixed C25 cyclic orders. No
general proof, all-order C25 obstruction, geometric counterexample, or
official-status change is claimed.

## Target

The residual-seed augmentation in
`docs/sparse-full-cone-c25-residual-seed-augmentation.md` stopped after the
original transferred seeds covered all 32 new probe orders and residual
augmentation added no marginal coverage. It predeclared the two original
transfer-CEGAR orders `probe:0` and `probe:1` as the next targets because both:

- survive the vertex-circle and both Altman lightweight filters;
- escape the two-inequality Kalmanson inverse-pair filter; and
- remain outside all three transferred and eight compressed residual seed
  orbits.

The remaining question was whether either order escapes the full fixed-order
Kalmanson cone.

## Exact protocol

`scripts/exploration/screen_sparse_full_cone_c25_persistent_escapes.py`
reconstructs the complete provenance chain from the residual-seed augmentation
artifact. It replays all 11 exact seed orbits and their 275
quotient-preserving affine images, verifies that both targets match none of
them, and screens all 25,300 strict fixed-order Kalmanson rows for each target.

The numerical LP is only a witness finder. A conclusive record must contain
one side of Gordan's theorem of alternatives:

1. an exact positive integer combination of strict row vectors summing to
   zero; or
2. an exact integer potential having strictly positive dot product with every
   row.

The stored checker uses exact integer arithmetic for the zero sum or every
separator dot product. It also checks the positive-circuit rank audit and
pins every source artifact by SHA-256.

## Result

| Target | Distance classes | Strict rows | Classification | Certificate rows | Ordered quads |
| --- | ---: | ---: | --- | ---: | ---: |
| `probe:0` | 225 | 25,300 | exact positive zero sum | 201 | 201 |
| `probe:1` | 225 | 25,300 | exact positive zero sum | 196 | 196 |

Both zero-objective LP supports exactify directly. There are no separator and
no unresolved records.

Therefore neither target is a fixed-order full-cone escape. Each fixed
selected-witness quotient and cyclic order is exactly inconsistent with the
strict Kalmanson inequalities, despite escaping all 11 previously stored seed
orbits.

## Decision and next target

The exact alternative returns
`CONTINUE_C25_CLAUSE_ROUTE_WITH_EXACT_POSITIVE_CIRCUITS`. These two orders are
not coordinate-search targets.

The completed follow-up in
`docs/sparse-full-cone-c25-persistent-escape-compression.md` compresses the
circuits to exact widths 4 and 5. The width-4 affine orbit alone covers all 23
targets marginal over the 11 existing seeds in the current 144-order packet,
including both persistent orders; the width-5 orbit adds no marginal target.

The next bounded target is a 144-history-blocked C25 order CEGAR run using the
three transferred seed orbits plus only the new width-4 orbit. Keep the
width-5 orbit and all eight zero-marginal residual orbits inactive. This
remains a bounded clause-engineering diagnostic, not evidence of an all-order
obstruction.

Replay:

```bash
python scripts/exploration/screen_sparse_full_cone_c25_persistent_escapes.py \
  --check data/runs/sparse_full_cone_c25_persistent_escape_screen_2026-07-30/summary.json
```
