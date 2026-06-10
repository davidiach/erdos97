# Mixed-radius bipartite FR-lift homotopies

Status: `FAILED_APPROACH` / `NUMERICAL_EVIDENCE`.

This note records selected 2026-06-09 homotopy probes around the repository
`B20_4x5_FR_lift` incidence template. The runs are Fishburn--Reeds-inspired
only: no exact historical Fishburn--Reeds coordinate certificate was present in
the session input, and the template is already archived as killed as a fixed
selected pattern. These artifacts therefore record failed numerical route
provenance, not a proof, counterexample, or counterexample candidate.

The imported scripts are:

```text
scripts/search_mixed_radius_bipartite_homotopy.py
scripts/search_mixed_radius_bipartite_arc_homotopy.py
scripts/homotopy_mixed_radius_bipartite_arc.py
```

The imported artifacts are under:

```text
data/runs/mixed_radius_bipartite_fr_lift_2026-06-09/
```

## Family

Labels are written `i = 5*a + b` on the `4 x 5` torus. The bipartite classes
are determined by parity of `a`, and the FR-lift row pattern uses opposite-class
witnesses

```text
S_(a,b) = {(a+1,b), (a+3,b), (a+1,b+2), (a+3,b-2)} mod (4,5).
```

The scripts test three related parameterizations.

The support-arc chart uses fixed support-line normals and one independent
support offset per vertex. It is numerically stabilizing, but convexity is not
assumed from the chart; every accepted point is checked by edge-vs-all-vertices
strict convexity margin, minimum edge length, and minimum pair distance.

The polar-arc chart fixes boundary order `0,1,...,19`, giving consecutive
blocks `A0,B0,A1,B1`, with positive angular gaps and independent radial
parameters for every vertex.

The two-arc frozen-distance chart relabels the two bipartite classes into
opposing 10-vertex arcs, starts at a convex seed with selected squared
distances frozen, and tracks toward an independent per-center mixed-radius
four-witness endpoint.

## Outcomes

The stabilizing support-arc run is the most informative. Its best path accepts
only to `t = 0.05` and then rides the convexity/edge floor:

```text
artifact:             mixed_radius_bipartite_fr_homotopy_seed20260609.json
drop:                 0
termination:          convexity_floor_riding
max spread:           3.4572000614654375e-3
eq RMS:               1.1267190361809176e-3
convexity margin:     1.7791413471530331e-8
minimum edge length:  2.3994629152953263e-4
minimum pair distance:2.3994629152953263e-4
```

The polar-arc chart does not find a convex three-row seed in the quick run:

```text
artifact:             mixed_radius_bipartite_polar_arc_fr_homotopy_seed20260609.json
drop:                 0
last accepted t:      0.0
termination:          convexity_floor_riding
max spread:           3.0792504422983957
eq RMS:               0.7722542278017873
convexity margin:     -2.5795643703454586e-4
minimum edge length:  6.526136877227974e-2
```

The two-arc frozen-distance run keeps homotopy residual small only for tiny
positive `t`, then fails the primary convexity gate. Endpoint polishing reduces
spread by collapsing vertices:

```text
artifact:             mixed_radius_bipartite_arc_homotopy_summary_seed20260609.json
best final spread:    6.723949176912214e-5
best final eq RMS:    1.6997497193710797e-5
convexity margin:     -1.7087300231030095e-5
minimum edge length:  0.0
minimum pair distance:0.0
standalone verifier:  not triggered
```

The companion row-dependent fourth-witness aggregate records the same
qualitative failure at `t=0`: the three-witness base constraints solve only on
the non-strict/collision boundary for seeds `9702`, `9703`, and `9705`.

## Interpretation

Across these packets, distance residuals improve by moving toward the boundary
of the strict-convexity cone. The binding constraints are convexity and
edge/pair separation, not floating-point equality residual. This matches the
repository's broader pattern for numerical near-misses: the equations can look
approachable only while a hull edge or larger cluster collapses.

No imported run meets the repo exactification threshold from
`docs/exactification-plan.md`:

```text
max selected-distance spread < 1e-10
convexity margin            > 1e-3
minimum edge length         > 1e-3
minimum pair distance       > 1e-3
independent verifier passes
```

No exact verifier was invoked and no `COUNTEREXAMPLE_CANDIDATE` is recorded.
The useful next step would be an obstruction lemma for this restricted
mixed-radius bipartite FR-lift family, or a rerun from independently verified
exact Fishburn--Reeds coordinates if such coordinates are later added.
