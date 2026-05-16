# n=9 radius-blocker order reduction

Status: `REVIEW_PENDING_DIAGNOSTIC` / finite packet crosswalk. No general
proof of Erdos Problem #97 is claimed. No counterexample is claimed.

This note records the relabelling scope of
`docs/n9-radius-blocker-shape-sweep.md`. For the exact-four radius-blocker
packet, a supplied cyclic order and four-vertex blocker reduce to the natural
order by the label map

```text
order[i] -> i.
```

The blocker becomes the sorted set of positions occupied by its vertices in
that order. The exact-four row-option rule depends only on the center and
blocker membership, so this relabelling transports row options, two-overlap
crossing in the supplied order, witness-pair caps, indegree caps, and
selected-distance vertex-circle replay to the natural-order packet for the
transformed blocker.

## Checked Crosswalk

The checked artifact is:

```text
data/certificates/n9_radius_blocker_order_reduction_crosswalk.json
```

Regenerate and verify it with:

```bash
python scripts/check_n9_radius_blocker_order_reduction_crosswalk.py --check --assert-expected
```

The crosswalk checks that the shape-sweep representatives cover all `126`
labelled four-vertex blockers in natural order. Therefore, for this exact-four
packet only, arbitrary cyclic-order placements of a four-blocker are reduced to
the already checked natural-order shape sweep.

## Interpretation

This closes the cyclic-order placement gap for the full `n=9` exact-four
four-blocker packet, not for arbitrary `n=9` rich-class systems. It still does
not handle rich classes larger than four, and it does not prove that every
hypothetical counterexample reduces to this packet.
