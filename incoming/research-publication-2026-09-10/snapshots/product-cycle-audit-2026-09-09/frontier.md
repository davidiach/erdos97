# Frontier after this continuation

**No unrestricted proof or counterexample. No nine-orbit exclusion.**
Repository base: 9b8b8f807ae8b21f10780a7d11f6c5cec65f26e7, merged #943.
Accepted finite-case status is unchanged.

## New exact boundary

All 160 distinct historically stored nine-orbit angle failures now have exact
integer certificates, checked independently of their optimizer. A stronger
bounded search produced additional systems. Among 333 distinct stored systems
in total, 330 have base-angle certificates and three require the new overlapping
diamond phase obstruction. All 333 are now rejected exactly in their specified
order. The search did not exhaust the nine-orbit universe.

The three latter systems have independently checked POSITIVE RATIONAL vectors
for the previous base-angle model and for a full ordinary-distance Kalmanson/
triangle/radius cone. These are separate relaxations, not Euclidean realizations.
Two commuting diamonds force a multiplicative identity incompatible with their
sector order. Thus these three are not live coordinate candidates anymore.

The supplier-arc lemma gives a further all-size necessary radial relation under
two C3 own-side arrows. Its three-arrow corollary has an additional exact angle
certificate. No extraction from arbitrary all-rich polygons is supplied.

## Construction escapes and controls

The six-cycle projective monodromy escape is real, now with a specified quartic
root and exact eighteen-point example. It is nonconvex: only six points are on
the hull, and all eighteen have maximum multiplicity three. It is not all-rich.
Neither this nor the sampled product failure proves that every longer cycle or
changed product graph fails.

An exact C3 convex 21-point control has a maximum-norm rich root orbit whose
entire own-side witness neighborhood is rich at no larger rich radii. There are
nine rich points and twelve good points. Even the C3 maximum-root one-step
shortcut is false without global richness.

A convex 12-point product diamond confirms that a diamond by itself is allowed.
A separate convex 12-point supplier-arc control calibrates the strict radial
and forbidden-arrow conclusions.

The 7x7 and 9x9 unrestricted-witness lattice models returned infeasible in
HiGHS. Those are solver diagnostics only; no certificate of those finite
exclusions is supplied. They impose neither C3 symmetry nor a fixed witness
table, but integer-grid membership remains a restrictive finite pool.

## Smallest missing implications

Proof: show that an arbitrary all-rich strictly convex configuration must
supply a proved local obstruction. Even within own-side C3, no theorem forces
aligned diamonds. A 60-state exact abstract two-out, nonreciprocal graph has
no directed diamond, so those incidence axioms alone cannot force one. That
graph is not supplied with convex order or Euclidean geometry.

Construction: find a witness system that survives the new circle-completion
phase equations and realizes with positive separation and ALL global support
margins. A small coordinate residual accompanied by coincident orbit phases
is degeneration, not progress toward an exact counterexample.

## Phase rule integrated after publication

An exact C++ one/two-diamond phase-gap filter is now active in
`search/nine_with_phase.cpp`. On all 333 stored systems its decisions agree with
an independent Python implementation: 200 are phase-rejected (five single and
195 double diamonds), with separately replayable integer certificates.
A bounded 2,000,000-node run generated 15 terminal systems, all already exactly
rejected in the stored corpus. It is not an exhaustive nine-orbit run. A larger
run timed out without a final counter report and supports no exclusion claim.

## Next executable experiment (not already run)

Augment `search/c3_model.py` with every equality from
`verify/diamond_phase.py:diamonds`, using q_i+q_l-q_j-q_k-2*sigma*pi=0.
This would integrate the full phase-equation span into the angle model, beyond
the one/two-relation phase filter already running inside the C++ search. Do not restart the three stored systems as live nonlinear candidates.
No all-n completeness claim follows from that proposed experiment.
