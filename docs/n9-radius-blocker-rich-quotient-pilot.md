# n=9 radius-blocker rich-class quotient pilot

Status: `REVIEW_PENDING_DIAGNOSTIC` / finite packet diagnostic. No general
proof of Erdos Problem #97 is claimed. No counterexample is claimed.

This note records a follow-up to
`docs/n9-radius-blocker-rich-projection-pilot.md`. Instead of projecting each
synthetic size-five rich class to selected exact four-subsets, it replays the
vertex-circle quotient using the full rich classes:

- center-to-witness distances are unioned across all witnesses in each rich
  class;
- nested-chord strict inequalities are generated from every rich class in its
  cyclic witness order;
- the resulting strict graph is checked for self-edges and directed cycles.

This is full vertex-circle quotient replay for one finite rich-class family.
It is not a classification of richer `n=9` systems and it is not a bridge
proof.

## Checked Result

The checked artifact is:

```text
data/certificates/n9_radius_blocker_rich_quotient_pilot.json
```

Regenerate and verify it with:

```bash
python scripts/check_n9_radius_blocker_rich_quotient_pilot.py --check --assert-expected
```

For the nine stored size-five classes, the full rich-class quotient has `225`
strict vertex-circle edges. It is obstructed immediately by `193` self-edge
conflicts; the first recorded conflict is in row `0`.

## Boundary

This closes one limitation of the projection pilot: the replay no longer
forgets equality information inside the selected size-five classes. It still
checks only one synthetic rich-class family, so it does not prove the adaptive
radius-blocker bridge, `n=9`, or Erdos Problem #97.

The useful next target is to quantify this full rich-class quotient replay
over a generated family of radius-blocker rich-class packets rather than one
stored pilot family.
