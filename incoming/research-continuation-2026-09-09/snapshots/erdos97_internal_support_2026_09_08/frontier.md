# Frontier after the internally supported cap and moving-seed continuation

Status: restricted written proofs and exact certificates; independent
mathematical review pending. Erdős97 is not resolved by this packet.

## Fixed old seed

The old seed is the same exact nine-point P from the two delivered packets.
The previous zero-internally-supported case has one possible cap: the next
recurrence triangle, which leaves the old six good vertices good.

The new theorem excludes exactly one internally supported cap vertex. Here
such a vertex means one whose **every** rich radius uses at most one point
of P, and therefore at least three other points of the added set Q. All
other cap vertices are allowed to choose any rich radius with two old
witnesses. Old vertices need not be rich in the exclusion theorem.

Together these force at least two internally supported cap vertices in any
all-rich strict convex extension of this P. Their three or more new witnesses
need not themselves be internally supported. No obstruction to two such
vertices is proved, and no unrestricted extraction from an arbitrary polygon
is established.

This genuinely strengthens the previous one-free diagnostic: that diagnostic
left all nine insertion cells alive because it omitted the free vertex's
common-radius constraint and compulsory shared-circle conflicts. The new
proof includes those constraints over exact continuous domains and excludes
all 90 cell/old-support cases. It is not a cap-size-limited grid scan.

The rational 14-point control demonstrates that exactly one internally
supported vertex *can* occur over a different old seed. This calibrates the
fixed-seed hypothesis rather than closing the unrestricted construction route.

## Moving-coordinate branch

A general pair-capacity argument rules out promoting a three-witness
construction by replacing every vertex with two consecutive copies and
using only copies of the three old witnesses. This is symmetry-free and
allows moving coordinates, but retains the consecutive-copy and witness-pool
hypotheses. Changing witnesses or changing that cluster structure escapes it.

Three copies saturate, rather than violate, the pair budget: every four-point
row must use the 2+1+1 distribution. This remains only a necessary condition.
The bounded experiment selected nonsymmetric 27-point patterns in that class.
All 15 retained distinct patterns now have exact strict-quadrilateral
obstructions in their stated order. The initial four numerical optimizations
are retrospectively obstructed benchmarks, not live candidates.

The fresh stronger-preflight scan rejected its twelve patterns before
coordinate optimization. It has no certificate of exhausting the whole
tripled family. There is no accepted all-rich realization from this branch.

## What would change the unrestricted frontier

A fixed-seed construction must solve a cap with at least two genuinely
internally supported vertices simultaneously, including the old exceptions'
richness and every supporting half-plane sign. A moving-seed construction
must rederive its geometric constraints rather than reuse this P's fixed
slot or circumcenter certificates. The unrestricted proof route still lacks
a reduction from arbitrary all-rich polygons to these structures.

No repository status, main branch, or accepted finite bound was changed.
No PR was opened. No external review, Lean formalization, or published
novelty is claimed.
