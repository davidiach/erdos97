# First escape from two-old support

The main theorem requires a rich radius using two old witnesses at every
new vertex. This diagnostic permits exactly one exceptional new vertex,
with at most one old witness at its rich radius and hence at least three
new witnesses. Every other new point is assigned a two-old-supported slot.

The exceptional point is placed in each of the nine old insertion cells
in turn. Closed triangles cover those cells exactly. A source slot can
possibly use the exceptional point only when its squared-distance-difference
range on the slot-by-triangle product contains zero. The script computes
those ranges with exact field arithmetic.

The free point itself is allowed to point to every regular slot; its common
radius is NOT imposed. Deleting regular nodes below outdegree two and the
free node below outdegree three therefore checks only a coarse relaxation.
It ignores additional circle-sharing and joint-convexity constraints and
does not require the old vertices to become rich.

All nine cases survive: six with 13 nodes including the free vertex, three
with 16. These are abstract graph survivors, not numerical or exact point
configurations. No impossibility result or feasible cap is inferred.

```sh
python exploratory/one_free_relaxation.py
```

This script imports the primary arithmetic. Its results are **not** checked
by the independent oracle and are not part of the unique-cap certificate.
