# n=9 radius-blocker rich-class quotient sweep

Status: `REVIEW_PENDING_DIAGNOSTIC` / finite packet diagnostic. No general
proof of Erdos Problem #97 is claimed. No counterexample is claimed.

This note widens `docs/n9-radius-blocker-rich-quotient-pilot.md` from one
synthetic size-five rich-class family to a generated packet family. The input is
the stored natural-order `n=9` radius-blocker shape sweep. For each of the `10`
four-blocker shapes, the sweep takes the stored self-edge obstruction example
and the stored strict-cycle obstruction example, then enlarges every exact
four-row to one synthetic size-five rich class.

The enlargement rule preserves the actual radius-blocker condition: if a row
center is inside the blocker, the enlarged rich class must still contain fewer
than three blocker vertices. For centers outside the blocker, blocker
intersection is recorded but is not constrained by the radius-blocker
definition.

## Checked Result

The checked artifact is:

```text
data/certificates/n9_radius_blocker_rich_quotient_sweep.json
```

Verify it with:

```bash
python scripts/check_n9_radius_blocker_rich_quotient_sweep.py --check --assert-expected --json
```

The sweep checks `20` generated packets, with `180` total size-five rich
classes. Each packet has `225` full rich-class strict vertex-circle edges.
All `20` packets are obstructed by quotient self-edges, for `3,533` total
self-edge conflicts. The first self-edge row is row `0` in every packet.

## Boundary

This is full rich-class quotient replay for generated examples, not an
enumeration of arbitrary rich-class catalogues. It does not prove that all
radius-blockers are impossible, does not prove `n=9`, does not prove the
adaptive radius-blocker bridge, and does not prove Erdos Problem #97.

The follow-up `docs/n9-radius-blocker-rich-extension-neighborhood.md` checks a
bounded Hamming-distance neighborhood of size-five extension choices around
these generated packets. The next wider target is still the full extension
product for a carefully chosen packet or a genuine minimal/rich-class bridge
hypothesis.
