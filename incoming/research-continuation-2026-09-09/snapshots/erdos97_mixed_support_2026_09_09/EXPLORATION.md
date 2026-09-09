# Exploratory record and limits

The initial scouts counted real roots of distance quartics in floating point
for minimum- and maximum-|x| candidate centers. They were used to identify the
complementary height regimes and to select exact controls, never as exclusion
certificates. The raw threshold scan includes a spurious high count at H=1/2,
c=0: it counted a repeated polynomial root repeatedly. The exact Sturm tests
now explicitly cover that case and count one geometric witness. This illustrates
why the floating scans are not mathematical evidence.

Other scouting triples in `build_lens_controls.py` fail the lens-membership
condition. They are not retained as positive geometric controls. The two
successful controls are separately specified and exactly checked in
`data/controls.json`. Their lower witness coordinates are isolated algebraic
roots, not decimal approximations.

The all-height mixed-lens proof came from differentiating the two distance
polynomials and evaluating the upper-left distance at its stationary points.
The shallow bound was sharpened from three to two after observing that the
upper distance can have only a maximum on the relevant interval, so its two
intersections cannot coexist with a distinct lower intersection.

The separate two-free probe covers closed insertion triangles and old-pair
slots from the inherited packet. It includes every unordered cell pair
(including equal cells) and all ten old-support choices for each free vertex.
The total is 45*10*10=4,500 cases; same-cell label duplicates are intentionally
retained. Among the outcomes, 1,824 necessary graphs peel away at least one
required free vertex; 2,676 survive. This is not an exactification or a
nonexistence result for all two-free caps. Zero-old free rows have no single-
radius compatibility filter in this probe. New-point mutual convexity, old-
vertex richness, and simultaneous realization of all edges are omitted.

No new numerical coordinate optimizer was run after obtaining the lens proof.
No unrestricted counterexample was found. No claim is made that the two-free
probe is stronger than every possible earlier relaxation or that its surviving
graphs merit expensive numerical realization without further exact checks.
