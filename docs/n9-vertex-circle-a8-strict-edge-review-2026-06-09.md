# n=9 Vertex-circle A8 Strict-edge Review - 2026-06-09

Status: `INTERNAL_REVIEW_NOTE`.

Claim scope: internal review of the A8 vertex-circle strict-edge geometry rule
used by the review-pending `n=9` vertex-circle checker. This note reviews the
local nested-chord implication and its implementation as a proper-interval
strict-edge generator. It does not review row coverage, brancher coverage,
A6/A7 source-frontier enumeration, selected-distance quotient soundness, A10
local-lemma completeness, the exhaustive `n=9` brancher, `n=9`, a
counterexample, or the official/global status of Erdos Problem #97.

## Outcome

Outcome: `accepted_A8_strict_edge_geometry_internal`.

The internal review accepts the local statement that, for a selected row
whose witnesses lie on one circle centered at the row center, proper interval
containment in the cyclic witness order forces a strict ordinary-distance
inequality between the corresponding witness chords. It also accepts that the
repo-native checker and reusable quotient replay enumerate exactly that
proper-containment rule for the current `n=9` selected-row universe.

This is not an external review-decision record. The machine-readable
`vertex_circle_geometry` gate in `metadata/n9_review_gate_ledger.yaml` remains
open until an explicit written decision is validated through the review-decision
intake or an equivalent source-of-truth review process.

## Geometry Reviewed

For a strictly convex polygon, fix a vertex `c` and four selected witnesses
`w0,w1,w2,w3` that lie on a circle centered at `p_c`. The other vertices have
distinct angular coordinates around `p_c` in an interval of length less than
`pi`, ordered by the polygon cyclic order up to reversal.

For two selected witnesses with angular separation `theta`, their chord length
on the selected circle is:

```text
2R sin(theta / 2).
```

On `0 < theta < pi`, this is strictly increasing. Therefore if witness
interval `[r,s]` properly contains `[u,v]` in the selected-witness order, the
ordinary chord distance for `{w_r,w_s}` is strictly larger than the ordinary
chord distance for `{w_u,w_v}`.

The rule is invariant under reversing the witness order, so sorting witnesses
by cyclic position relative to `c` is enough to choose one of the two equivalent
orientations.

## Implementation Reviewed

The reviewed implementation contract is:

```text
outer_start <= inner_start
and inner_end <= outer_end
and (outer_start < inner_start or inner_end < outer_end)
```

The exhaustive checker builds `STRICT_EDGES` by sorting each row's witnesses
relative to the center and adding exactly the outer/inner pair distances that
satisfy this condition. The quotient replay helper uses the same condition
after sorting witnesses in the supplied cyclic order.

For four witnesses, the six witness intervals yield nine strict comparisons
per selected row:

```text
outer span 2, inner span 1: 4
outer span 3, inner span 1: 3
outer span 3, inner span 2: 2
```

No non-contained interval comparison is accepted by this review; such a
comparison is not forced by cyclic order alone.

## Commands Run

```bash
python scripts/check_n9_vertex_circle_strict_edge_geometry.py --check --assert-expected --summary-json
python scripts/check_n9_review_gate_ledger.py --check --summary-json
python scripts/check_n9_candidate_review_manifest.py --check --summary-json
python scripts/check_n9_review_decision_intake.py --check --summary-json
```

## Stable Invariants Observed

- Strict-edge geometry audit validation status: `passed`.
- Selected rows checked: `630`.
- Strict edges per selected row: `{9: 630}`.
- Total direct strict edges checked: `5670`.
- Strict-edge table mismatches: `0`.
- One-row quotient replay strict-edge count mismatches: `0`.
- Interval-span histogram:
  - `2->1: 2520`;
  - `3->1: 1890`;
  - `3->2: 1260`.
- Review-gate ledger validation status: `passed`.
- Candidate review manifest validation status: `passed`.
- Review-decision intake validation status: `passed`.

## Narrow Statement Supported

This pass supports the following narrow internal-review statement:

```text
For the current n=9 selected-row universe, the vertex-circle proper-interval
strict-edge rule is geometrically sound, and the exhaustive checker plus
quotient replay helper enumerate that local rule without strict-edge table or
one-row replay-count drift.
```

## Review Boundary

This pass does not support any of the following stronger statements:

- the A6/A7 source-frontier enumeration is reviewed;
- the selected-distance quotient implementation is reviewed;
- the A10 local-lemma packet chain is promoted as a source-of-truth gate;
- the full vertex-circle route is accepted;
- the turn-packing route is accepted;
- no bad nonagon exists as a promoted source-of-truth claim;
- Erdos Problem #97 is proved;
- any counterexample is produced or certified;
- the official/global status changes.

## Next Review Step

The next source-of-truth step is either an explicit `vertex_circle_geometry`
gate decision using the review-decision intake, or upstream review of the
A6/A7 source-frontier enumeration so the internally reviewed A8 and A10 layers
can be placed in the full vertex-circle route.
