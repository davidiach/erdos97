# Barany--Roldan-Pensado boundary vertexization probe

Status: `NUMERICAL_GEOMETRIC_DIAGNOSTIC`.

This note records a first contrarian probe of the convex-body boundary
construction lane. It does not prove Erdos Problem #97, does not give a
counterexample, and does not model the full Barany--Roldan-Pensado 15-gon.

## Question

Barany--Roldan-Pensado construct convex bodies whose boundary has high
centered-circle intersection multiplicity. The obstruction for Erdos #97 is
that those extra circle intersections may lie in edge interiors rather than at
vertices.

The first finite-vertex question is deliberately smaller:

```text
For the recorded 3-fold seed points, do centered circles already convert
boundary richness into vertex richness?
```

## Modeled seed

The checker uses the four quoted source points

```text
A1 = (1000, 0)
A2 = (906, 114)
A3 = (645, 359)
A4 = (-498, 871)
```

and their rotations by `2*pi/3` and `4*pi/3`, giving the 12 modeled vertices

```text
A1,A2,A3,A4,B1,B2,B3,B4,C1,C2,C3,C4.
```

The seed order is strictly convex in the float64 check. The source paper then
uses Lemma 3.1 to prove the existence of a point `A5` in a neighborhood of the
broken line `A4B1B2B3`, but it does not give coordinates for `A5`. The checker
therefore keeps the explicit 12-point seed separate from any synthetic `A5`
stress test.

## Checker

Run:

```bash
python3 scripts/check_brp_boundary_probe.py --assert-expected
```

The checked artifact is
`data/certificates/brp_boundary_vertexization_probe.json`, managed by
`metadata/generated_artifacts.yaml`. Replay the artifact check with:

```bash
python3 scripts/check_brp_boundary_probe.py --check --assert-expected --json
```

The checker:

- represents vertex-to-vertex squared distances exactly in `Q(sqrt(3))` for
  the 120-degree rotated seed;
- enumerates every distinct circle centered at a seed vertex and passing
  through another seed vertex;
- intersects each such circle numerically with the 12 seed boundary edges;
- separates hits at modeled vertices from hits in edge interiors;
- runs a small signed synthetic `A5` edge-pocket scan with
  `A5(t,h)=A4+t*(B1-A4)+h*unit_left_normal(A4B1)`, rotating the result to
  `B5` and `C5`. This is only a stress test, not the source paper's `A5`.

## Current result

The stable checked summary is:

```text
seed vertices: 12
distinct centered vertex radii: 120
max seed-vertex hits on one centered circle: 2
max seed-boundary hits on one centered circle: 5
circles with at least four boundary hits: 45
circles with at least four seed vertices: 0
synthetic A5 edge-pocket candidates: 36
strictly convex synthetic A5 candidates: 0
synthetic candidates with at least four vertices on a centered circle: 0
```

Thus the modeled 12-point seed shows the expected continuous/discrete gap:
many centered circles hit the polygonal boundary four or five times, but none
hits four modeled seed vertices.

The synthetic `A5` pocket scan is also a useful failed route: the sampled
signed normal-offset stand-ins do not remain strictly convex. This only
rejects those 36 sampled edge-pocket candidates; it does not rule out other
naive edge-pocket placements or the source construction's existential `A5`.
It is still not evidence against the full contrarian lane: the source
construction's Lemma 3.1 choice is existential, and the relevant
edge-parameter closure remains unmodeled.

## Next steps

Useful follow-up work should avoid more visual inspection and instead make the
edge-interior hits algebraic:

1. Replace the synthetic pocket scan with the actual Lemma 3.1 constraints for
   `A=A3`, `B=A4`, `C=B1`, and a suitable `D` from the adjacent seed chain.
2. Solve or parameterize admissible `A5` choices with strict convexity
   constraints.
3. Promote each interior circle-edge hit to a candidate vertex parameter.
4. Iterate the closure condition: promoted vertices become centers that must
   themselves acquire four vertex hits.
5. Replace float64 edge intersections with exact algebraic or interval
   certificates.
6. If every closure attempt explodes into new edge interiors, extract the
   failure as a boundary-to-vertex obstruction lemma.

## Guardrails

Do not cite this probe as:

- a proof of Erdos Problem #97;
- a counterexample or counterexample candidate;
- a finite extraction from the Barany--Roldan-Pensado body;
- a check of the final 15-gon;
- evidence about the actual existential `A5` from Lemma 3.1;
- an exact certificate for boundary intersections.
