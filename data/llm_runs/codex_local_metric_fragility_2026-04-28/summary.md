# n=8 metric-fragility probe, 2026-04-28

Status: research artifact only. This is a symbolic diagnostic on the n=8
survivor classes, not a general proof and not a counterexample.

## Main result

Metric fragility uniqueness was tested in the only n=8 place where it can be
made exact from the current artifacts: the 15 selected-row survivor classes.

The full selected equal-distance equations are already inconsistent for classes
0 through 13 under the standard normalization p0=(0,0), p1=(1,0). For those
classes, any fragility-uniqueness question is vacuous: there is no selected-row
metric realization even over the complex numbers.

Class 14 is the only class whose full selected equal-distance ideal is
consistent. In that class, no selected row is algebraically forced to have an
alternate equal-distance four-subset at the same center. So metric fragility
uniqueness does not kill class 14. The existing exact n=8 artifact kills class
14 by solving the PB+ED system and showing every branch has only four hull
vertices, hence no strict convex octagon.

## Added tooling

`scripts/analyze_n8_metric_fragility.py` computes:

- which n=8 survivor classes have inconsistent full selected ED equations;
- for consistent classes, which rows are forced non-fragile by alternate
  equal-distance four-subsets;
- whether rows not forced non-fragile can still cover all vertices.

Expected fingerprint:

```text
selected_ed_inconsistent_classes = 0,1,...,13
selected_ed_consistent_classes = 14
consistent_classes_with_eligible_fragile_cover = 14
```

## Interpretation

This closes the current n=8 fragile-cover branch: incidence cover is too weak,
and exact metric uniqueness does not add a new obstruction beyond the existing
selected ED and strict-convexity checks.

For larger n, the analogous condition is a real semialgebraic constraint:
fragile centers require selected equality plus disequalities excluding every
other rich four-subset. A future solver should encode those disequalities by
saturation or interval separation rather than as prose.
