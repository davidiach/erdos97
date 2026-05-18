# n=9 mixed rich-support frontier crosswalk

Status: `REVIEW_PENDING_DIAGNOSTIC` / support-to-frontier crosswalk. No
general proof of Erdos Problem #97 is claimed. No counterexample is claimed.

This note joins two checked artifacts:

- `data/certificates/n9_mixed_rich_support_reduction.json`;
- `data/certificates/n9_vertex_circle_frontier_motif_classification.json`.

The mixed rich-support reduction enumerates every four- or five-witness
support at every center of the natural-order nonagon and leaves `184` complete
assignments, all exact-four. The crosswalk reruns that mixed support search,
collects those terminal exact-four row systems, and compares them as labelled
row sets with the stored pre-vertex-circle frontier.

## Checked Result

The checked artifact is:

```text
data/certificates/n9_mixed_rich_frontier_crosswalk.json
```

Verify it with:

```bash
python scripts/check_n9_mixed_rich_frontier_crosswalk.py --check --assert-expected --json
```

The crosswalk records:

```text
mixed terminal assignments:     184
stored frontier assignments:    184
set equality:                   true
sequence equality:              false
sequence mismatch positions:    106, 107, 108, 109, 134, 135
matched frontier status counts: 158 self_edge, 26 strict_cycle
sorted row-set SHA-256:         dc28b32d93e721838a592d1f010f92720869191594dbcc40df2a00f96f213d55
```

The sequence mismatch is harmless provenance: the mixed-support brancher and
the stored frontier classifier order six assignments differently, but the
labelled row set is identical.

## Consequence

Repo-locally, the mixed rich-support reduction now lands exactly on the stored
`184` exact-four pre-vertex-circle frontier, not merely on another collection
with the same cardinality. This removes one bookkeeping gap between the
four/five support catalogue and the existing exact-four vertex-circle review
pipeline.

## Boundary

This crosswalk does not independently prove the exact-four vertex-circle
exhaustive checker. It does not prove filter soundness, strict-edge geometry,
selected-distance quotient soundness, `n=9`, the adaptive radius-blocker
bridge, or Erdos Problem #97. It is not a counterexample.
